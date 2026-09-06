"""Find the page rotation by maximising row-profile sharpness, then deskew."""
from __future__ import annotations
import os, numpy as np
from PIL import Image
import fb_enhance as E

OUT = E.OUT


def rot(a, ang, fill=255):
    im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    return np.asarray(im.rotate(ang, resample=Image.BICUBIC, expand=True, fillcolor=fill),
                      dtype=np.float64)


def score(soft, mask, ang):
    r = rot(soft, ang); m = rot(mask.astype(float) * 255, ang, 0) > 127
    band = (r < 150) & (~m)
    # only the two number columns, avoiding the paper edges
    h, w = band.shape
    p = band[:, int(0.12 * w):int(0.78 * w)].sum(axis=1).astype(float)
    return float((p ** 2).sum() / max(p.sum(), 1) ** 2 * len(p))


def main():
    src = E.unmirror()
    soft = E.soft(src)
    mask = E.figure_mask(np.asarray(src))
    best, ba = -1, None
    for ang in np.arange(-20.0, -16.0, 0.25):
        s = score(soft, mask, ang)
        print(f"  angle {ang:+6.2f} sharpness {s:.4f}")
        if s > best:
            best, ba = s, ang
    for ang in np.arange(ba - 0.25, ba + 0.26, 0.05):
        s = score(soft, mask, ang)
        if s > best:
            best, ba = s, float(ang)
    print(f"best rotation {ba:+.2f} deg  (sharpness {best:.4f})")
    hard = E.hard(src)
    # `soft2` is the primary reading layer: same stretch as `soft` but with the
    # mask-aware background, which is what makes the digits that sit beside the
    # clay figure legible at all.  `soft_plain` is kept for comparison.
    layers = {"soft": rot(E.soft2(src), ba), "soft_plain": rot(soft, ba),
              "hard": rot(hard, ba), "mask": rot(mask.astype(float) * 255, ba, 0)}
    masked = soft.copy(); masked[mask] = 255.0
    layers["masked"] = rot(masked, ba)
    for k, v in layers.items():
        np.save(os.path.join(OUT, f"R_{k}.npy"), v)
        Image.fromarray(np.clip(v, 0, 255).astype(np.uint8)).save(os.path.join(OUT, f"R_{k}.png"))
    im = Image.open(os.path.join(OUT, "R_soft.png"))
    im.resize((im.width // 3, im.height // 3)).save(os.path.join(OUT, "R_overview.png"))
    print("rotated frame", layers["soft"].shape)
    open(os.path.join(OUT, "angle.txt"), "w").write(str(ba))


if __name__ == "__main__":
    main()
