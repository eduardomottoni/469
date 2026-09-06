"""Shear the page so each number column becomes vertical, then emit magnified
strips in several renderings so the same glyph can be cross-checked.

Renderings
  soft  : background-divided ratio, linearly stretched, unsharp-masked.
          Keeps grey levels -> best for judging stroke shape.
  hard  : the CLAHE render.  Maximum sensitivity, but binarises and invents
          texture in the vignette -> only ever used to CONFIRM a soft reading.
  masked: soft, with the clay figure painted flat white so the eye is not
          drawn to it and partial glyphs at the clay edge stand out.
"""
from __future__ import annotations
import os, numpy as np
from PIL import Image
import fb_enhance as E

OUT = E.OUT
SHEAR = 0.320
Y0 = 500
WINDOW = {"left": (95, 215), "right": (490, 660)}


def shear(a: np.ndarray) -> np.ndarray:
    h, w = a.shape
    out = np.full_like(a, 255)
    for y in range(h):
        d = int(round(SHEAR * (y - Y0)))
        if d >= 0:
            out[y, :w - d] = a[y, d:]
        else:
            out[y, -d:] = a[y, :w + d]
    return out


def soft(lo=0.905, hi=1.005) -> np.ndarray:
    src = Image.open(os.path.join(OUT, "00_unmirrored.png")).convert("RGB")
    g = np.asarray(src.convert("L"), dtype=np.float64)
    flat = E.flatten(g, 12.0)
    v = np.clip((flat - lo) / (hi - lo), 0, 1) * 255.0
    return E.unsharp(v, 1.2, 1.6)


def main():
    rgb = np.asarray(Image.open(os.path.join(OUT, "00_unmirrored.png")).convert("RGB"))
    mask = E.figure_mask(rgb)
    renders = {
        "soft": soft(),
        "hard": np.asarray(Image.open(os.path.join(OUT, "02_ink_s12.png")), dtype=np.float64),
    }
    m = soft().copy(); m[mask] = 255.0
    renders["masked"] = m
    for rname, arr in renders.items():
        s = shear(arr)
        for side, (x0, x1) in WINDOW.items():
            im = Image.fromarray(np.clip(s[:, x0:x1], 0, 255).astype(np.uint8))
            im = im.resize((im.width * 5, im.height * 5), Image.LANCZOS)
            im.save(os.path.join(OUT, f"S_{side}_{rname}.png"))
            step = 900
            for i in range(0, im.height, step):
                im.crop((0, i, im.width, min(im.height, i + step + 80))).save(
                    os.path.join(OUT, f"S_{side}_{rname}_{i // step}.png"))
    print("done", {k: v.shape for k, v in renders.items()})


if __name__ == "__main__":
    main()
