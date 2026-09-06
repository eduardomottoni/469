"""Row / column detection on the deskewed hi-res page."""
from __future__ import annotations
import os, json, numpy as np
from scipy import ndimage as ndi
import fb_enhance as E

OUT = E.OUT


def load():
    return (np.load(os.path.join(OUT, "R_soft.npy")),
            np.load(os.path.join(OUT, "R_mask.npy")) > 127)


def ink(thr=150):
    soft, mask = load()
    b = (soft < thr) & (~mask)
    h, w = b.shape
    # kill the paper border / outside-frame noise
    b[:int(0.03 * h)] = False; b[int(0.98 * h):] = False
    b[:, :int(0.06 * w)] = False; b[:, int(0.92 * w):] = False
    return b


def columns(b):
    p = b.sum(axis=0).astype(float)
    p = ndi.uniform_filter1d(p, 15)
    lab, n = ndi.label(p > p.max() * 0.12)
    out = []
    for i in range(1, n + 1):
        idx = np.where(lab == i)[0]
        if len(idx) > 60:
            out.append((int(idx[0]), int(idx[-1] + 1), float(p[idx].sum())))
    return out


def rows(b, x0, x1, thr=2, minlen=8):
    p = b[:, x0:x1].sum(axis=1).astype(float)
    lab, n = ndi.label(p >= thr)
    out = []
    for i in range(1, n + 1):
        idx = np.where(lab == i)[0]
        if len(idx) < minlen:
            continue
        w = p[idx]
        out.append((float((idx * w).sum() / w.sum()), int(idx[0]), int(idx[-1]), float(w.max())))
    return out


if __name__ == "__main__":
    b = ink()
    print("ink columns (x0,x1,mass):")
    cols = columns(b)
    for c in cols:
        print("  ", c)
    for name, (x0, x1) in {"left": (300, 740), "right": (1130, 1600)}.items():
        rs = rows(b, x0, x1)
        print(f"\n== {name} x[{x0},{x1}]  {len(rs)} ink bands")
        prev = None
        for y, a, z, pk in rs:
            gap = f"  d={y-prev:6.1f}" if prev else ""
            print(f"   y={y:8.1f} [{a},{z}] peak={pk:4.0f}{gap}")
            prev = y
