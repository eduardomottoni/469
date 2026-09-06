"""Preprocessing for the 2011 Tibia Facebook mirrored-page photo.

Source
------
`data/external/provenance/fb/fb_hires.jpg`, 1536x2048, the post's own og:image
(fbid 10150239378812364, Tibia's official page, 12 Aug 2011).  It carries ~2x
the high-frequency energy of an upscaled copy of the 768x1024 version that was
previously in the repo, so it is a real 2x original, not an enlargement.

Pipeline
--------
1. un-mirror (flip horizontally) so the DIGITS read left-to-right.  In the
   as-posted image the speech bubble reads correctly and the numbers are the
   mirrored element -- they are show-through from the far side of the sheet.
2. divide by a heavily blurred copy of itself.  The photograph has a strong
   vignette whose dynamic range is far wider than the ink's, so global
   contrast stretching cannot work; dividing by the local background removes
   the vignette and the paper shading and leaves only the ink.
3. per-tile CLAHE for maximum sensitivity ("hard"), or a plain linear stretch
   of the useful ratio band for shape-faithful reading ("soft").
4. unsharp mask.

Channels: paper and ink are both neutral, so R/G/B carry near-identical digit
information (verified -- see FB_PAIRS.md).  The channels are useful only for
building the clay-figure mask, which is strongly saturated.
"""
from __future__ import annotations

import os
import numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage as ndi

HERE = os.path.dirname(os.path.abspath(__file__))
FB = os.path.abspath(os.path.join(HERE, "..", "..", "data", "external", "provenance", "fb"))
OUT = os.path.join(HERE, "fb_out")
SRC = os.path.join(FB, "fb_hires.jpg")
SCALE = 2.0                      # hi-res is 2x the old 768x1024 working copy
BLUR = 24.0                      # background sigma, = 12 * SCALE
os.makedirs(OUT, exist_ok=True)


def unmirror() -> Image.Image:
    return Image.open(SRC).convert("RGB").transpose(Image.FLIP_LEFT_RIGHT)


def flatten(gray: np.ndarray, sigma: float = BLUR) -> np.ndarray:
    bg = np.asarray(Image.fromarray(gray.astype(np.uint8)).filter(
        ImageFilter.GaussianBlur(sigma)), dtype=np.float64)
    return gray.astype(np.float64) / np.maximum(bg, 1.0)


def clahe(img: np.ndarray, tiles: int = 14, clip: float = 2.5) -> np.ndarray:
    h, w = img.shape
    u8 = np.clip(img, 0, 255).astype(np.uint8)
    ty, tx = max(1, h // tiles), max(1, w // tiles)
    ny, nx = int(np.ceil(h / ty)), int(np.ceil(w / tx))
    luts = np.zeros((ny, nx, 256))
    limit = max(1.0, clip * (ty * tx) / 256.0)
    for i in range(ny):
        for j in range(nx):
            t = u8[i * ty:(i + 1) * ty, j * tx:(j + 1) * tx]
            hist = np.bincount(t.ravel(), minlength=256).astype(float)
            exc = np.maximum(hist - limit, 0).sum()
            hist = np.minimum(hist, limit) + exc / 256.0
            cdf = np.cumsum(hist)
            luts[i, j] = 255.0 * cdf / max(cdf[-1], 1e-9)
    fy = np.clip((np.arange(h) - ty / 2) / ty, 0, ny - 1)
    fx = np.clip((np.arange(w) - tx / 2) / tx, 0, nx - 1)
    i0 = np.floor(fy).astype(int); i1 = np.minimum(i0 + 1, ny - 1); wy = (fy - i0)[:, None]
    j0 = np.floor(fx).astype(int); j1 = np.minimum(j0 + 1, nx - 1); wx = (fx - j0)[None, :]
    v = u8
    return (luts[i0[:, None], j0[None, :], v] * (1 - wy) * (1 - wx)
            + luts[i0[:, None], j1[None, :], v] * (1 - wy) * wx
            + luts[i1[:, None], j0[None, :], v] * wy * (1 - wx)
            + luts[i1[:, None], j1[None, :], v] * wy * wx)


def figure_mask(rgb: np.ndarray) -> np.ndarray:
    """True where the coloured clay figure or the near-black speech bubble is."""
    mx = rgb.max(axis=2).astype(np.float64)
    mn = rgb.min(axis=2).astype(np.float64)
    sat = (mx - mn) / np.maximum(mx, 1.0)
    m = (sat > 0.18) | (mx < 110)
    im = Image.fromarray((m * 255).astype(np.uint8))
    im = im.filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.MinFilter(5))
    return np.asarray(im) > 127


def unsharp(a: np.ndarray, radius: float = 2.4, amount: float = 1.6) -> np.ndarray:
    im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    blur = np.asarray(im.filter(ImageFilter.GaussianBlur(radius)), dtype=np.float64)
    return np.clip(a + amount * (a - blur), 0, 255)


def soft(src: Image.Image, lo=0.905, hi=1.005) -> np.ndarray:
    """Shape-faithful render: grey levels preserved.  LOW = ink."""
    g = np.asarray(src.convert("L"), dtype=np.float64)
    return unsharp(np.clip((flatten(g) - lo) / (hi - lo), 0, 1) * 255.0)


def hard(src: Image.Image) -> np.ndarray:
    """Maximum-sensitivity render.  Binarises; use only to CONFIRM a soft read."""
    g = np.asarray(src.convert("L"), dtype=np.float64)
    v = np.clip((flatten(g) - 0.90) / 0.12, 0, 1) * 255.0
    return unsharp(clahe(v))


def main() -> None:
    src = unmirror()
    src.save(os.path.join(OUT, "00_unmirrored.png"))
    rgb = np.asarray(src)
    Image.fromarray((figure_mask(rgb) * 255).astype(np.uint8)).save(
        os.path.join(OUT, "01_figure_mask.png"))
    Image.fromarray(soft(src).astype(np.uint8)).save(os.path.join(OUT, "02_soft.png"))
    Image.fromarray(hard(src).astype(np.uint8)).save(os.path.join(OUT, "02_hard.png"))
    # per-channel check: does graphite/toner separate in any single channel?
    for ci, cn in enumerate("RGB"):
        ch = Image.fromarray(rgb[:, :, ci]).convert("RGB")
        Image.fromarray(soft(ch).astype(np.uint8)).save(os.path.join(OUT, f"03_soft_{cn}.png"))
    print("hi-res frame", rgb.shape, "figure mask %.1f%%" % (100 * figure_mask(rgb).mean()))


if __name__ == "__main__":
    main()


def flatten_masked(gray: np.ndarray, keepout: np.ndarray, sigma: float = BLUR) -> np.ndarray:
    """Background division that ignores the clay figure.

    A plain Gaussian background estimate is dragged down by the near-black clay,
    so in a halo around the figure the estimated background is far darker than
    the paper actually is and the ratio image washes the digits out entirely.
    That halo is much wider than the blur radius because the figure is large and
    very dark.  Normalised convolution -- blur(image*w) / blur(w) with w=0 on the
    clay -- estimates the background from paper pixels only, so digits that sit
    beside the figure survive.
    """
    w = (~keepout).astype(np.float64)
    g = gray.astype(np.float64) * w

    def blur(a):
        return ndi.gaussian_filter(a, sigma, mode="nearest")
    num = blur(g)
    den = blur(w)
    bg = np.where(den > 1e-3, num / np.maximum(den, 1e-3), 1.0)
    return gray.astype(np.float64) / np.maximum(bg, 1.0)


def soft2(src: Image.Image, lo=0.905, hi=1.005) -> np.ndarray:
    """`soft`, but with the mask-aware background.  This is the render used for
    every reading near the clay figure."""
    rgb = np.asarray(src)
    g = np.asarray(src.convert("L"), dtype=np.float64)
    return unsharp(np.clip((flatten_masked(g, figure_mask(rgb)) - lo) / (hi - lo), 0, 1) * 255.0)
