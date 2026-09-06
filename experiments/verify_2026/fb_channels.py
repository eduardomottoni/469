"""Two questions the preprocessing plan raises, answered with numbers.

1. Does any single R/G/B channel separate the ink from the paper better than
   luminance?  Measured as the contrast between known ink pixels and the paper
   immediately around them, over the legible glyphs.
2. Does a tighter clay mask expose more of the digits at the figure's edge?
   The mask is dilated so its own soft boundary does not leak into readings;
   this measures what that dilation costs.
"""
from __future__ import annotations
import os, json, numpy as np
from PIL import Image, ImageFilter
import fb_enhance as E
import fb_ocr as O

OUT = E.OUT


def channel_contrast():
    src = E.unmirror()
    rgb = np.asarray(src)
    soft = np.load(os.path.join(OUT, "R_soft.npy"))
    # ink pixels, located in the deskewed frame then read back per channel is
    # awkward; instead work in the un-rotated frame using the same flattening.
    mask = E.figure_mask(rgb)
    layers = {"L": np.asarray(src.convert("L"), dtype=np.float64),
              "R": rgb[:, :, 0].astype(np.float64),
              "G": rgb[:, :, 1].astype(np.float64),
              "B": rgb[:, :, 2].astype(np.float64)}
    out = {}
    for name, g in layers.items():
        f = E.flatten_masked(g, mask)
        # ink = the 0.5% darkest ratio pixels off the figure; paper = the median
        v = f[~mask]
        ink = np.percentile(v, 0.5)
        paper = np.percentile(v, 60)
        noise = np.percentile(v, 40) - np.percentile(v, 20)
        out[name] = dict(ink=round(float(ink), 4), paper=round(float(paper), 4),
                         contrast=round(float(paper - ink), 4),
                         noise=round(float(noise), 4),
                         snr=round(float((paper - ink) / max(noise, 1e-6)), 2))
        print(f"  {name}: ink={ink:.4f} paper={paper:.4f} contrast={paper-ink:.4f} "
              f"noise={noise:.4f}  SNR={out[name]['snr']}")
    return out


def mask_cost():
    """How much of each occluded cell the mask dilation itself removes."""
    src = E.unmirror()
    rgb = np.asarray(src)
    mx = rgb.max(axis=2).astype(np.float64); mn = rgb.min(axis=2).astype(np.float64)
    raw = ((mx - mn) / np.maximum(mx, 1.0) > 0.18) | (mx < 110)
    tight = np.asarray(Image.fromarray((raw * 255).astype(np.uint8)
                                       ).filter(ImageFilter.MinFilter(3))) > 127
    ang = float(open(os.path.join(OUT, "angle.txt")).read())
    rt = np.asarray(Image.fromarray((tight * 255).astype(np.uint8)
                                    ).rotate(ang, resample=Image.NEAREST, expand=True,
                                             fillcolor=0), dtype=np.float64)
    np.save(os.path.join(OUT, "R_mask_tight.npy"), rt)
    cur = np.load(os.path.join(OUT, "R_mask.npy")) > 127
    tightr = rt > 127
    print(f"  dilated mask covers {100*cur.mean():.2f}% of frame, "
          f"tight mask {100*tightr.mean():.2f}%")
    rows = {"left": [22, 23, 28], "right": [6, 7, 12, 13, 14, 16]}
    res = {}
    for side, rs in rows.items():
        for r in rs:
            for slot in range(3):
                bx0, bx1, by0, by1 = O.cell_box(side, r, slot)
                b = (slice(int(by0), int(by1)), slice(int(bx0), int(bx1)))
                a = float((~cur[b]).mean()); t = float((~tightr[b]).mean())
                if t - a > 0.03:
                    res[f"{side} r{r} slot{slot}"] = (round(a, 2), round(t, 2))
                    print(f"  {side} r{r} slot{slot}: visible {a:.2f} -> {t:.2f} "
                          f"with the tight mask")
    return res


if __name__ == "__main__":
    soft = np.load(os.path.join(OUT, "R_soft.npy"))
    mask = np.load(os.path.join(OUT, "R_mask.npy")) > 127
    O.prep(soft, mask)
    print("1. per-channel ink/paper separation (mask-aware flattened ratio):")
    ch = channel_contrast()
    print("\n2. cost of the mask dilation on the occluded cells:")
    mc = mask_cost()
    json.dump(dict(channels=ch, mask_cost=mc),
              open(os.path.join(OUT, "channels.json"), "w"), indent=1)
