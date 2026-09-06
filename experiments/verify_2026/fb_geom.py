"""Fit the per-column digit geometry: row baseline y(i), right-alignment edge
x(i), and digit advance a(i).  All three vary smoothly down the page because
of the photograph's residual perspective, so each is a quadratic in row index
fitted to the rows where enough glyphs survive to measure it."""
from __future__ import annotations
import os, json, numpy as np
from scipy import ndimage as ndi
from PIL import Image
import fb_enhance as E

OUT = E.OUT
XWIN = {"left": (495, 705), "right": (1295, 1495)}
NROW = {"left": 28, "right": 31}
# Rows whose units digit is certainly clear of the clay.  Only these may be
# used to fit the right-alignment edge -- a row whose units digit is occluded
# has its rightmost surviving glyph one slot too far left and would drag the
# fitted edge inwards by a full digit width.
CLEAN = {"left": list(range(0, 20)) + [24, 25, 26, 27],
         "right": [0, 1, 2, 3] + list(range(16, 29))}
SEED_Y = {  # (row index 0-based, y) triples read off the clean glyph clusters
    "left": [(0, 275.0), (13, 1137.3), (27, 2145.0)],
    "right": [(0, 260.8), (16, 1347.5), (30, 2360.0)]}


def glyphs(soft, mask, side, thr=0.32):
    x0, x1 = XWIN[side]
    b = (np.clip((205.0 - soft) / 150.0, 0, 1) > thr) & (~mask)
    b[:, :x0] = False; b[:, x1:] = False
    lab, n = ndi.label(b, structure=np.ones((3, 3)))
    out = []
    for j, sl in enumerate(ndi.find_objects(lab), 1):
        ys, xs = sl
        if ys.stop - ys.start < 12 or xs.stop - xs.start < 5:
            continue
        if int((lab[sl] == j).sum()) < 55:
            continue
        out.append(dict(x0=xs.start, x1=xs.stop, y0=ys.start, y1=ys.stop,
                        cx=(xs.start + xs.stop) / 2, cy=(ys.start + ys.stop) / 2))
    return out


def fit(side, soft, mask):
    gl = glyphs(soft, mask, side)
    ii = np.array([p[0] for p in SEED_Y[side]], float)
    yy = np.array([p[1] for p in SEED_Y[side]], float)
    cy = np.polyfit(ii, yy, 2)
    buckets = {}
    for _ in range(20):
        ys = np.polyval(cy, np.arange(NROW[side]))
        pitch = np.gradient(ys)
        buckets = {}
        for g in gl:
            d = np.abs(ys - g["cy"]); i = int(np.argmin(d))
            if d[i] < pitch[i] * 0.40:
                buckets.setdefault(i, []).append(g)
        good = {i: v for i, v in buckets.items() if len(v) >= 2}
        gi = np.array(sorted(good), float)
        gy = np.array([np.mean([g["cy"] for g in good[i]]) for i in sorted(good)])
        cy = np.polyfit(gi, gy, 2)
    # edge: rightmost glyph edge, measured only on rows with an unoccluded
    # units digit
    ck = [i for i in sorted(good) if i in CLEAN[side]]
    ei = np.array(ck, float)
    ee = np.array([max(g["x1"] for g in good[i]) for i in ck], float)
    ce = np.polyfit(ei, ee, 2)
    # advance: median gap between adjacent glyph centres, per row, fitted linearly
    ai, aa = [], []
    for i in ck:
        r = sorted(good[i], key=lambda g: g["cx"])
        d = [q["cx"] - p["cx"] for p, q in zip(r, r[1:]) if 20 <= q["cx"] - p["cx"] <= 45]
        if d:
            ai.append(i); aa.append(np.median(d))
    ca = np.polyfit(np.array(ai, float), np.array(aa, float), 1)
    # glyph box size, for the template window
    hh = np.median([g["y1"] - g["y0"] for i in good for g in good[i]])
    ww = np.median([g["x1"] - g["x0"] for i in good for g in good[i]])
    res_e = float(np.abs(np.polyval(ce, ei) - ee).max())
    print(f"{side}: rows={NROW[side]}  y={cy}  edge residual max {res_e:.1f}px  "
          f"advance {np.polyval(ca,0):.1f}->{np.polyval(ca,NROW[side]-1):.1f}  "
          f"glyph {ww:.0f}x{hh:.0f}px  ({len(good)} measured rows)")
    return dict(cy=cy.tolist(), ce=ce.tolist(), ca=ca.tolist(),
                gw=float(ww), gh=float(hh), nrow=NROW[side],
                y=[float(v) for v in np.polyval(cy, np.arange(NROW[side]))],
                nglyph={int(i): len(v) for i, v in buckets.items()})


if __name__ == "__main__":
    soft = np.load(os.path.join(OUT, "R_soft.npy"))
    mask = np.load(os.path.join(OUT, "R_mask.npy")) > 127
    g = {s: fit(s, soft, mask) for s in ("left", "right")}
    json.dump(g, open(os.path.join(OUT, "geom.json"), "w"), indent=1)
    for s in g:
        print(f"\n{s} rows:")
        for i, y in enumerate(g[s]["y"]):
            print(f"  r{i+1:02d} y={y:7.1f} edge={np.polyval(g[s]['ce'],i):7.1f} "
                  f"adv={np.polyval(g[s]['ca'],i):5.1f} nglyph={g[s]['nglyph'].get(i,0)}")
