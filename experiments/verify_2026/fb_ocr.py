"""Fragment identification by template matching against the page's own glyphs.

The sheet is set in one font at one size, so every digit that is legible
somewhere on the page is an exemplar for the same digit where it is occluded.

Templates are built from the DETECTED bounding boxes of unoccluded glyphs
(standard OCR normalisation).  A fragment has no usable bounding box -- the
clay cuts it -- so a fragment is matched by sliding each template over a
window centred on the predicted grid cell and scoring only the pixels the clay
does not cover.  The alignment freedom is deliberately small (+-8px, +-10%
scale) so the search cannot manufacture a fit.

`selftest` reports leave-one-out accuracy on the fully legible glyphs, both
with the true box (upper bound) and through the same sliding search a fragment
gets (the number that actually matters).
"""
from __future__ import annotations
import os, json, itertools, numpy as np
from PIL import Image
from scipy import ndimage as ndi
import fb_enhance as E
from fb_read import LEFT_Y, RIGHT_Y

OUT = E.OUT
TH, TW = 30, 22                     # template raster
GEOM = json.load(open(os.path.join(OUT, "geom.json")))
XWIN = {"left": (495, 705), "right": (1295, 1495)}


def row_y(side, row):
    return np.polyval(GEOM[side]["cy"], row - 1)


def row_edge(side, row):
    return np.polyval(GEOM[side]["ce"], row - 1)


def row_adv(side, row):
    return np.polyval(GEOM[side]["ca"], row - 1)
TRAIN = {
    "left": {1: "713", 2: "765", 3: "706", 4: "824", 5: "975", 6: "937",
             7: "726", 8: "729", 9: "652", 10: "653", 11: "565", 12: "746",
             13: "1021", 14: "759", 15: "718", 16: "737", 17: "648",
             18: "818", 19: "985", 20: "2154", 25: "1017", 26: "1280",
             27: "684"},
    "right": {1: "473", 2: "464", 3: "447", 4: "499", 18: "520", 19: "621",
              20: "1307", 21: "540", 22: "471", 23: "489", 24: "447",
              25: "658", 26: "625", 27: "448", 28: "453", 29: "860",
              30: "514", 31: "496"}}


def load():
    return (np.load(os.path.join(OUT, "R_soft.npy")),
            np.load(os.path.join(OUT, "R_mask.npy")) > 127)


_IMG = {}


def prep(soft, mask):
    """Build the full-frame PIL rasters once; every crop reuses them."""
    _IMG["ink"] = np.clip((205.0 - soft) / 150.0, 0, 1)
    _IMG["inkimg"] = Image.fromarray((_IMG["ink"] * 255).astype(np.uint8))
    _IMG["maskimg"] = Image.fromarray((mask * 255).astype(np.uint8))


def inkmap(soft):
    return _IMG["ink"]


def row_glyphs(side, row, soft, mask, thr=0.32):
    """Connected glyph boxes whose centre lies on the given row."""
    x0, x1 = XWIN[side]
    yc = row_y(side, row)
    lo, hi = int(yc - 34), int(yc + 34)
    sub = inkmap(soft)[lo:hi, x0:x1] > thr
    sub &= ~mask[lo:hi, x0:x1]
    lab, n = ndi.label(sub, structure=np.ones((3, 3)))
    out = []
    for j, sl in enumerate(ndi.find_objects(lab), 1):
        ys, xs = sl
        if ys.stop - ys.start < 12 or xs.stop - xs.start < 5:
            continue
        if int((lab[sl] == j).sum()) < 55:
            continue
        out.append((xs.start + x0, xs.stop + x0, ys.start + lo, ys.stop + lo))
    return sorted(out)


def raster(soft, box):
    x0, x1, y0, y1 = box
    im = _IMG["inkimg"].crop((x0, y0, x1, y1))
    return np.asarray(im.resize((TW, TH), Image.BILINEAR), dtype=np.float64) / 255.0


def build_templates(soft, mask, exclude=None):
    acc = {}
    for side, rows in TRAIN.items():
        for row, val in rows.items():
            if exclude == (side, row):
                continue
            gs = row_glyphs(side, row, soft, mask)
            if len(gs) != len(val):
                continue
            for box, ch in zip(gs, val):
                acc.setdefault(ch, []).append(raster(soft, box))
    return {d: np.mean(v, axis=0) for d, v in acc.items()}, {d: len(v) for d, v in acc.items()}


def ncc(a, b, w):
    """Weighted normalised cross-correlation over w (bool)."""
    if w.sum() < 60:
        return -1.0
    x = a[w]; y = b[w]
    x = x - x.mean(); y = y - y.mean()
    d = np.sqrt((x * x).sum() * (y * y).sum())
    return float((x * y).sum() / d) if d > 1e-9 else 0.0


def cell_box(side, row, slot):
    """The grid box for one digit cell -- independent of any surviving ink."""
    adv = row_adv(side, row)
    xc = row_edge(side, row) - (slot + 0.5) * adv
    gw, gh = GEOM[side]["gw"], GEOM[side]["gh"]
    yc = row_y(side, row)
    return xc - gw / 2, xc + gw / 2, yc - gh / 2, yc + gh / 2


def nominal_visible(side, row, slot, mask):
    """Fraction of the cell the clay does NOT cover, at the NOMINAL grid box.
    Reporting the best-case visibility over the sliding search would flatter
    every fragment, so visibility is always measured here and never inside the
    search loop."""
    bx0, bx1, by0, by1 = cell_box(side, row, slot)
    box = (int(bx0), int(by0), int(bx1), int(by1))
    pm = np.asarray(_IMG["maskimg"].crop(box).resize((TW, TH), Image.BILINEAR)) > 96
    return float((~pm).mean())


def match(side, row, slot, soft, mask, tmpl, dxy=8, scales=(0.92, 1.0, 1.08)):
    """Slide each template over a window around the predicted cell."""
    bx0, bx1, by0, by1 = cell_box(side, row, slot)
    ink = inkmap(soft)
    best = {}
    vis_best = nominal_visible(side, row, slot, mask)
    for sc in scales:
        w = (bx1 - bx0) * sc; h = (by1 - by0) * sc
        for dx in range(-dxy, dxy + 1, 4):
            for dy in range(-dxy, dxy + 1, 4):
                cx = (bx0 + bx1) / 2 + dx; cy = (by0 + by1) / 2 + dy
                box = (int(cx - w / 2), int(cx + w / 2), int(cy - h / 2), int(cy + h / 2))
                x0, x1, y0, y1 = box
                if x0 < 0 or y0 < 0 or y1 > soft.shape[0] or x1 > soft.shape[1]:
                    continue
                pi = np.asarray(_IMG["inkimg"].crop((x0, y0, x1, y1))
                                .resize((TW, TH), Image.BILINEAR), dtype=np.float64) / 255.0
                pm = np.asarray(_IMG["maskimg"].crop((x0, y0, x1, y1))
                                .resize((TW, TH), Image.BILINEAR)) > 96
                vis = ~pm
                for d, t in tmpl.items():
                    s = ncc(pi, t, vis)
                    if s > best.get(d, -2):
                        best[d] = s
    r = sorted(best.items(), key=lambda kv: -kv[1])
    return dict(visible=round(vis_best, 3),
                ranked=[(d, round(v, 3)) for d, v in r[:4]],
                margin=round(r[0][1] - r[1][1], 3) if len(r) > 1 else 0.0)


def selftest(soft, mask):
    ok = tot = 0; wrong = []
    for side, rows in TRAIN.items():
        for row, val in rows.items():
            gs = row_glyphs(side, row, soft, mask)
            if len(gs) != len(val):
                continue
            tmpl, _ = build_templates(soft, mask, exclude=(side, row))
            for slot, ch in enumerate(reversed(val)):
                r = match(side, row, slot, soft, mask, tmpl)
                tot += 1
                if r["ranked"][0][0] == ch:
                    ok += 1
                else:
                    wrong.append((side, row, slot, ch, r["ranked"][:2]))
    return ok, tot, wrong


if __name__ == "__main__":
    soft, mask = load()
    prep(soft, mask)
    tmpl, counts = build_templates(soft, mask)
    print("template exemplar counts:", counts)
    Image.fromarray(np.hstack([(tmpl[d] * 255).astype(np.uint8) for d in "0123456789"])
                    ).resize((TW * 10 * 6, TH * 6), Image.NEAREST).save(
                        os.path.join(OUT, "templates.png"))
    ok, tot, wrong = selftest(soft, mask)
    print(f"\nleave-one-out, sliding search (same as a fragment gets): "
          f"{ok}/{tot} = {100*ok/tot:.1f}%")
    for w in wrong:
        print("   miss:", w)
    np.save(os.path.join(OUT, "templates.npy"), np.array([tmpl[d] for d in "0123456789"]))
