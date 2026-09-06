"""Magnified per-row crops with the fitted digit-slot grid drawn on top, so a
surviving fragment can be seen in the slot the geometry assigns it to."""
from __future__ import annotations
import os, sys, numpy as np
from PIL import Image, ImageDraw
import fb_enhance as E
import fb_ocr as O

OUT = E.OUT


def row_img(side, row, scale=9, nslot=4, layer="soft"):
    a = np.load(os.path.join(OUT, f"R_{layer}.npy"))
    edge = O.row_edge(side, row); adv = O.row_adv(side, row)
    y = O.row_y(side, row); gh = O.GEOM[side]["gh"]
    x1 = edge + adv * 0.6
    x0 = edge - adv * (nslot + 0.6)
    y0, y1 = y - gh * 0.95, y + gh * 0.95
    box = (int(x0), int(y0), int(x1), int(y1))
    im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).crop(box).convert("RGB")
    im = im.resize((im.width * scale, im.height * scale), Image.LANCZOS)
    d = ImageDraw.Draw(im)
    for k in range(nslot + 1):
        px = (edge - k * adv - x0) * scale
        d.line([(px, 0), (px, im.height)], fill=(255, 0, 0), width=2)
    d.line([(0, (y - gh / 2 - y0) * scale), (im.width, (y - gh / 2 - y0) * scale)],
           fill=(0, 140, 255), width=2)
    d.line([(0, (y + gh / 2 - y0) * scale), (im.width, (y + gh / 2 - y0) * scale)],
           fill=(0, 140, 255), width=2)
    return im


def montage(side, rows, scale=9, nslot=4, layer="soft", name=None):
    ims = [row_img(side, r, scale, nslot, layer) for r in rows]
    w = max(i.width for i in ims); gap = 10
    out = Image.new("RGB", (w, sum(i.height + gap for i in ims)), (200, 200, 200))
    y = 0
    for im in ims:
        out.paste(im, (0, y)); y += im.height + gap
    p = os.path.join(OUT, name or f"A_{side}_{rows[0]}_{rows[-1]}.png")
    out.save(p); print(p, out.size)
    return p


if __name__ == "__main__":
    montage(sys.argv[1], [int(v) for v in sys.argv[2].split(",")],
            int(sys.argv[3]) if len(sys.argv) > 3 else 9,
            int(sys.argv[4]) if len(sys.argv) > 4 else 4,
            sys.argv[5] if len(sys.argv) > 5 else "soft")
