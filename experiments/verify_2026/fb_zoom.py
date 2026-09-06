"""Emit magnified per-row crops of the deskewed page for visual reading."""
from __future__ import annotations
import os, sys, numpy as np
from PIL import Image
import fb_enhance as E

OUT = E.OUT
BOX = {"left": (140, 370), "right": (545, 790)}


def strip(side, y0, y1, scale=7, layer="soft"):
    a = np.load(os.path.join(OUT, f"R_{layer}.npy"))
    x0, x1 = BOX[side]
    sub = np.clip(a[y0:y1, x0:x1], 0, 255).astype(np.uint8)
    im = Image.fromarray(sub)
    return im.resize((im.width * scale, im.height * scale), Image.LANCZOS)


if __name__ == "__main__":
    side, y0, y1 = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
    layer = sys.argv[4] if len(sys.argv) > 4 else "soft"
    sc = int(sys.argv[5]) if len(sys.argv) > 5 else 7
    p = os.path.join(OUT, f"Z_{side}_{y0}_{y1}_{layer}.png")
    strip(side, y0, y1, sc, layer).save(p)
    print(p)
