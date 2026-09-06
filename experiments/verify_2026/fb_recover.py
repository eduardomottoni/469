"""Calibrate the digit classifier under partial occlusion, then apply it to
every actually-occluded cell on the page and emit a machine-readable verdict.

Calibration matters more than the classifier.  A confidently wrong digit here
would be worse than a missing one, so the reported confidence is not the
correlation score -- it is the measured leave-one-out accuracy of the same
classifier on the same page's glyphs when an equivalent fraction of the cell
is hidden from the same side.
"""
from __future__ import annotations
import os, json, numpy as np
from PIL import Image
import fb_enhance as E
import fb_ocr as O

OUT = E.OUT
# Which side of a cell the clay eats: the left column stands left of the
# figure so its UNITS digits go first; the right column stands right of the
# figure so its LEADING digits go first.
EAT = {"left": "right", "right": "left"}
README_L = ["713","765","706","824","975","937","726","729","652","653","565",
            "746","1021","759","718","737","648","818","985","2154","841",
            "71X","75X","689","1017","1280","684","694"]
README_R = ["473","464","447","499","595","X30","XY1","X47","400","407","X75",
            "X58","?X59","X75","X38","469","428","520","621","1307","540",
            "471","489","447","658","625","448","453","860","514","496"]


def synth_mask(shape, side, frac):
    """A synthetic occlusion covering `frac` of the cell from EAT[side]."""
    h, w = shape
    m = np.zeros((h, w), bool)
    k = int(round(w * frac))
    if k <= 0:
        return m
    if EAT[side] == "right":
        m[:, w - k:] = True
    else:
        m[:, :k] = True
    return m


def calibrate(soft, mask, tmpl, fracs=(0.0, 0.15, 0.3, 0.45, 0.6)):
    """Leave-one-out accuracy vs. how much of the cell is hidden."""
    rows = []
    for f in fracs:
        ok = tot = 0
        by_margin = []
        for side, trows in O.TRAIN.items():
            for row, val in trows.items():
                gs = O.row_glyphs(side, row, soft, mask)
                if len(gs) != len(val):
                    continue
                t2, _ = O.build_templates(soft, mask, exclude=(side, row))
                for slot, ch in enumerate(reversed(val)):
                    r = match_synth(side, row, slot, soft, mask, t2, f)
                    if not r["ranked"]:
                        continue
                    tot += 1
                    hit = r["ranked"][0][0] == ch
                    ok += hit
                    by_margin.append((r["margin"], hit))
        hi = [h for m, h in by_margin if m >= 0.10]
        rows.append(dict(hidden=f, n=tot, acc=round(ok / max(tot, 1), 3),
                         n_margin10=len(hi),
                         acc_margin10=round(sum(hi) / max(len(hi), 1), 3)))
        print(f"  hidden {f:4.0%}  n={tot:4d}  acc={ok/max(tot,1):6.1%}   "
              f"(margin>=0.10: n={len(hi):3d} acc={sum(hi)/max(len(hi),1):6.1%})")
    return rows


def match_synth(side, row, slot, soft, mask, tmpl, frac):
    """Same as O.match but with an extra synthetic occlusion applied."""
    bx0, bx1, by0, by1 = O.cell_box(side, row, slot)
    best, vis_best = {}, 0.0
    for sc in (0.92, 1.0, 1.08):
        w = (bx1 - bx0) * sc; h = (by1 - by0) * sc
        for dx in range(-8, 9, 4):
            for dy in range(-8, 9, 4):
                cx = (bx0 + bx1) / 2 + dx; cy = (by0 + by1) / 2 + dy
                box = (int(cx - w / 2), int(cy - h / 2), int(cx + w / 2), int(cy + h / 2))
                if box[0] < 0 or box[1] < 0 or box[3] > soft.shape[0] or box[2] > soft.shape[1]:
                    continue
                pi = np.asarray(O._IMG["inkimg"].crop(box).resize((O.TW, O.TH),
                                Image.BILINEAR), dtype=np.float64) / 255.0
                pm = np.asarray(O._IMG["maskimg"].crop(box).resize((O.TW, O.TH),
                                Image.BILINEAR)) > 96
                pm |= synth_mask(pm.shape, side, frac)
                vis = ~pm
                vis_best = max(vis_best, float(vis.mean()))
                for d, t in tmpl.items():
                    s = O.ncc(pi, t, vis)
                    if s > best.get(d, -2):
                        best[d] = s
    if not best:
        return dict(visible=0.0, ranked=[], margin=0.0)
    r = sorted(best.items(), key=lambda kv: -kv[1])
    return dict(visible=round(vis_best, 3),
                ranked=[(d, round(v, 3)) for d, v in r[:4]],
                margin=round(r[0][1] - r[1][1], 3))


def ndigits(side, row, soft, mask):
    """How many digit slots this row's number has, from the leftmost surviving
    ink in the row, or from the row's pattern where nothing survives."""
    gs = O.row_glyphs(side, row, soft, mask)
    if not gs:
        return None
    edge = O.row_edge(side, row); adv = O.row_adv(side, row)
    return int(np.ceil((edge - min(g[0] for g in gs)) / adv))


def main():
    soft, mask = O.load()
    O.prep(soft, mask)
    tmpl, counts = O.build_templates(soft, mask)
    print("template exemplars:", counts)
    print("\nclassifier calibration (leave-one-out, synthetic occlusion):")
    cal = calibrate(soft, mask, tmpl)

    print("\nper-cell verdicts on the occluded rows:")
    result = {}
    for side, readme in (("left", README_L), ("right", README_R)):
        nrow = O.GEOM[side]["nrow"]
        rows = []
        for row in range(1, nrow + 1):
            rm = readme[row - 1] if row - 1 < len(readme) else None
            nd = len(rm) if rm else 3
            cells = []
            for slot in range(nd - 1, -1, -1):
                r = O.match(side, row, slot, soft, mask, tmpl)
                cells.append(dict(slot=slot, visible=r["visible"],
                                  ranked=r["ranked"], margin=r["margin"]))
            rows.append(dict(row=row, y=round(float(O.row_y(side, row)), 1),
                             readme=rm, cells=cells))
        result[side] = rows
    json.dump(dict(calibration=cal, columns=result),
              open(os.path.join(OUT, "recover.json"), "w"), indent=1)
    for side in result:
        print(f"\n===== {side}")
        for r in result[side]:
            parts = []
            for c in r["cells"]:
                v, m = c["visible"], c["margin"]
                top = c["ranked"][0] if c["ranked"] else ("?", 0)
                parts.append(f"s{c['slot']}:{top[0]}({top[1]:.2f},m{m:+.2f},v{v:.2f})")
            print(f"  r{r['row']:02d} README={str(r['readme']):5} " + "  ".join(parts))


if __name__ == "__main__":
    main()
