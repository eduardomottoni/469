"""Detect the digit glyphs of the FB page and group them into numbers.

The photographed page is slightly rotated, so a number's digits do not share
a horizontal centroid.  The chaining tolerance is therefore generous in y and
the reported baseline slope is measured, not assumed.
"""
from __future__ import annotations
import os, json, numpy as np
from PIL import Image
from scipy import ndimage as ndi
import fb_enhance as E

OUT = E.OUT
EDGE = 745          # right-hand vignette produces junk beyond this x


def glyphs(thresh: int = 118):
    ink = np.asarray(Image.open(os.path.join(OUT, "02_ink_s12.png")), dtype=np.float64)
    rgb = np.asarray(Image.open(os.path.join(OUT, "00_unmirrored.png")).convert("RGB"))
    mask = E.figure_mask(rgb)
    binimg = (ink < thresh) & (~mask)
    binimg[:, EDGE:] = False
    binimg[:, :8] = False
    lab, n = ndi.label(binimg, structure=np.ones((3, 3)))
    out = []
    for i, sl in enumerate(ndi.find_objects(lab), 1):
        ys, xs = sl
        h, w = ys.stop - ys.start, xs.stop - xs.start
        area = int((lab[sl] == i).sum())
        if not (11 <= h <= 26 and 4 <= w <= 22 and area >= 25):
            continue
        out.append(dict(x0=int(xs.start), x1=int(xs.stop), y0=int(ys.start), y1=int(ys.stop),
                        cx=(xs.start + xs.stop) / 2, cy=(ys.start + ys.stop) / 2,
                        h=h, w=w, area=area))
    return out, binimg, mask


def group(gl, dy=13, gap=10):
    gl = sorted(gl, key=lambda g: (g["cy"], g["cx"]))
    used = [False] * len(gl)
    groups = []
    for i, g in enumerate(gl):
        if used[i]:
            continue
        cur = [g]; used[i] = True
        changed = True
        while changed:
            changed = False
            for j, h in enumerate(gl):
                if used[j]:
                    continue
                for c in cur:
                    if abs(h["cy"] - c["cy"]) <= dy and max(h["x0"] - c["x1"], c["x0"] - h["x1"]) <= gap:
                        cur.append(h); used[j] = True; changed = True; break
                if changed:
                    break
        cur.sort(key=lambda a: a["cx"])
        groups.append(dict(n=len(cur), x0=min(c["x0"] for c in cur), x1=max(c["x1"] for c in cur),
                           y0=min(c["y0"] for c in cur), y1=max(c["y1"] for c in cur),
                           cy=float(np.mean([c["cy"] for c in cur])),
                           cx=float(np.mean([c["cx"] for c in cur])), parts=cur))
    groups.sort(key=lambda a: a["cy"])
    return groups


def baseline_slope(groups):
    """Median within-number dy/dx over multi-digit groups -> page rotation."""
    sl = []
    for g in groups:
        if g["n"] >= 3:
            xs = np.array([p["cx"] for p in g["parts"]])
            ys = np.array([p["cy"] for p in g["parts"]])
            if np.ptp(xs) > 15:
                sl.append(np.polyfit(xs, ys, 1)[0])
    return float(np.median(sl)), len(sl)


if __name__ == "__main__":
    gl, binimg, mask = glyphs()
    Image.fromarray((binimg * 255).astype(np.uint8)).save(os.path.join(OUT, "04_bin.png"))
    gs = group(gl)
    s, nn = baseline_slope(gs)
    print(f"glyphs={len(gl)} groups={len(gs)} baseline slope={s:+.4f} "
          f"({np.degrees(np.arctan(s)):+.2f} deg, from {nn} numbers)")
    for g in gs:
        side = "L" if g["x0"] < 360 else "R"
        print(f" {side} y={g['cy']:7.1f} x=[{g['x0']:4d},{g['x1']:4d}] ndig={g['n']}")
