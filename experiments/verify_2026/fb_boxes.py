"""Row grid + per-row glyph boxes + digit-slot assignment on the deskewed
hi-res page.

Row pitch is NOT constant: residual perspective makes it grow from ~64px at
the top of the sheet to ~74px at the bottom, so each column's row grid is a
QUADRATIC fit in row index, seeded from the rows that are cleanly detected and
then extended to cover the occluded ones.

Both columns are right-aligned.  Slot 0 is the units digit, 1 the tens, 2 the
hundreds, 3 the thousands.  The alignment edge is also fitted linearly in row
index (the left column's edge drifts left going down, the right column's
drifts right).
"""
from __future__ import annotations
import os, json, numpy as np
from scipy import ndimage as ndi
import fb_enhance as E

OUT = E.OUT
XWIN = {"left": (515, 700), "right": (1310, 1480)}
NROW = {"left": 28, "right": 31}
README_L = ["713","765","706","824","975","937","726","729","652","653","565",
            "746","1021","759","718","737","648","818","985","2154","841",
            "71X","75X","689","1017","1280","684","694"]
README_R = ["473","464","447","499","595","X30","XY1","X47","400","407","X75",
            "X58","?X59","X75","X38","469","428","520","621","1307","540",
            "471","489","447","658","625","448","453","860","514","496"]
# (row index, measured y) anchors read off the cleanly detected bands.
# Three anchors per column pin the quadratic; everything else is derived.
ANCHOR = {"left":  {0: 273.8, 13: 1138.7, 27: 2138.5},
          "right": {2: 388.7, 19: 1411.1, 30: 2072.6}}


def glyphs(side, thr=150, minarea=55):
    soft = np.load(os.path.join(OUT, "R_soft.npy"))
    mask = np.load(os.path.join(OUT, "R_mask.npy")) > 127
    x0, x1 = XWIN[side]
    band = (soft[:, x0:x1] < thr) & (~mask[:, x0:x1])
    lab, n = ndi.label(band, structure=np.ones((3, 3)))
    out = []
    for i, sl in enumerate(ndi.find_objects(lab), 1):
        ys, xs = sl
        if ys.stop - ys.start < 12 or xs.stop - xs.start < 6:
            continue
        a = int((lab[sl] == i).sum())
        if a < minarea:
            continue
        out.append(dict(x0=int(xs.start) + x0, x1=int(xs.stop) + x0,
                        y0=int(ys.start), y1=int(ys.stop), area=a,
                        cx=(xs.start + xs.stop) / 2 + x0, cy=(ys.start + ys.stop) / 2))
    return out


def fit_grid(side, gl):
    ii = np.array(sorted(ANCHOR[side]))
    yy = np.array([ANCHOR[side][i] for i in ii])
    c = np.polyfit(ii, yy, 2)
    for _ in range(15):
        ys = np.polyval(c, np.arange(NROW[side]))
        pitch = np.gradient(ys)
        buckets = {}
        for g in gl:
            d = np.abs(ys - g["cy"])
            i = int(np.argmin(d))
            if d[i] < pitch[i] * 0.42:
                buckets.setdefault(i, []).append(g)
        good = {i: v for i, v in buckets.items() if len(v) >= 2}
        if len(good) < 6:
            break
        gi = np.array(sorted(good))
        gy = np.array([np.mean([g["cy"] for g in good[i]]) for i in gi])
        c = np.polyfit(gi, gy, 2)
    return c, buckets, np.polyval(c, np.arange(NROW[side]))


def analyse(side, readme):
    gl = glyphs(side)
    c, buckets, ys = fit_grid(side, gl)
    ii = [i for i in buckets if len(buckets[i]) >= 2]
    ea, eb = np.polyfit(ii, [max(g["x1"] for g in buckets[i]) for i in ii], 1)
    adv = [q["x0"] - p["x0"]
           for i in buckets
           for p, q in zip(sorted(buckets[i], key=lambda g: g["x0"]),
                           sorted(buckets[i], key=lambda g: g["x0"])[1:])
           if 20 <= q["x0"] - p["x0"] <= 60]
    advance = float(np.median(adv))
    pitch = np.gradient(ys)
    print(f"\n===== {side}: {NROW[side]} rows  pitch {pitch[0]:.1f}->{pitch[-1]:.1f}px  "
          f"edge={ea:+.3f}*i+{eb:.1f}  advance={advance:.1f}px  "
          f"({len(gl)} glyphs, {len(ii)} multi-glyph rows)")
    rows = []
    for i in range(NROW[side]):
        r = sorted(buckets.get(i, []), key=lambda g: g["x0"])
        e = ea * i + eb
        occ = {}
        for g in r:
            k = max(0, int(round((e - g["cx"] - advance / 2) / advance)))
            occ.setdefault(k, []).append(g)
        hi = max(occ) if occ else -1
        pat = "".join("#" if k in occ else "." for k in range(hi, -1, -1))
        rows.append(dict(row=i + 1, y=round(float(ys[i]), 1), nglyph=len(r),
                         slots=sorted(occ, reverse=True), pattern=pat,
                         readme=readme[i] if i < len(readme) else None,
                         boxes=[[g["x0"], g["x1"], g["y0"], g["y1"], g["area"]] for g in r]))
        xr = f"x=[{r[0]['x0']:4d},{r[-1]['x1']:4d}]" if r else " " * 15
        print(f"  r{i+1:02d} y={ys[i]:7.1f} n={len(r)} slots={str(sorted(occ, reverse=True)):12} "
              f"pat={pat:5} {xr}  areas={[g['area'] for g in r]}  README={readme[i] if i < len(readme) else '-'}")
    return dict(pitch_px=[round(float(p), 2) for p in pitch], y=[round(float(v), 1) for v in ys],
                edge_a=ea, edge_b=eb, advance=advance, rows=rows)


def main():
    out = {s: analyse(s, r) for s, r in (("left", README_L), ("right", README_R))}
    json.dump(out, open(os.path.join(OUT, "boxes.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
