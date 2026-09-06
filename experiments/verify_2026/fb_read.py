"""Emit high-magnification crops of individual rows for visual reading.

Crops are taken from the UNMASKED renders: the clay mask is dilated and would
erase any digit stroke that touches the clay edge, which is exactly the
evidence worth looking at.
"""
from __future__ import annotations
import os, sys, numpy as np
from PIL import Image
import fb_enhance as E

OUT = E.OUT
# row index (1-based) -> deskewed y, measured from the glyph clusters and the
# quadratic pitch model.  Both columns share the same pitch progression.
LEFT_Y = [275.0, 339.3, 405.5, 471.5, 535.8, 601.5, 667.9, 734.8, 799.5,
          866.5, 932.5, 1003.5, 1070.4, 1137.3, 1211.7, 1283.7, 1355.7,
          1426.9, 1498.8, 1568.9, 1638.8, 1712.5, 1785.0, 1859.0, 1930.4,
          2001.4, 2073.0, 2145.0]
RIGHT_Y = [260.8, 325.2, 391.8, 457.8, 524.2, 590.0, 656.0, 723.0, 791.8,
           858.2, 925.0, 995.0, 1065.5, 1136.0, 1208.0, 1281.5, 1347.5,
           1425.0, 1496.8, 1568.5, 1643.5, 1715.7, 1787.7, 1861.7, 1934.8,
           2009.7, 2080.0, 2150.0, 2220.0, 2290.0, 2360.0]
XW = {"left": (500, 700), "right": (1310, 1480)}


def crop(side, i, layer="soft", scale=6, pad=44):
    ys = LEFT_Y if side == "left" else RIGHT_Y
    y = int(round(ys[i - 1]))
    a = np.load(os.path.join(OUT, f"R_{layer}.npy"))
    x0, x1 = XW[side]
    sub = np.clip(a[max(0, y - pad):y + pad, x0:x1], 0, 255).astype(np.uint8)
    im = Image.fromarray(sub)
    return im.resize((im.width * scale, im.height * scale), Image.LANCZOS)


def montage(side, idxs, layer="soft", scale=6, name=None):
    ims = [crop(side, i, layer, scale) for i in idxs]
    w = max(i.width for i in ims)
    gap = 14
    out = Image.new("L", (w, sum(i.height for i in ims) + gap * len(ims)), 210)
    y = 0
    for im in ims:
        out.paste(im, (0, y)); y += im.height + gap
    p = os.path.join(OUT, name or f"M_{side}_{layer}_{idxs[0]}_{idxs[-1]}.png")
    out.save(p)
    print(p, out.size, "rows", idxs)
    return p


if __name__ == "__main__":
    side = sys.argv[1]
    idxs = [int(v) for v in sys.argv[2].split(",")]
    montage(side, idxs, sys.argv[3] if len(sys.argv) > 3 else "soft",
            int(sys.argv[4]) if len(sys.argv) > 4 else 6)
