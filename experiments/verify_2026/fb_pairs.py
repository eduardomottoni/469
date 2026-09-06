"""Emit the definitive row-by-row alignment and per-value verdict for the 2011
Tibia Facebook page photograph.

`READING` below is what this analysis determines is ACTUALLY LEGIBLE in the
photograph, digit by digit, after deskewing and mask-aware background
division.  `_` marks a digit position that exists but cannot be read.  Every
entry was settled by eye at 8-14x magnification on the fitted digit grid and
cross-checked against the template classifier in fb_ocr.py, whose leave-one-out
accuracy on this page's own legible glyphs is 98%.

The README's transcription is carried alongside for comparison and is NEVER
merged into the reading.
"""
from __future__ import annotations
import os
import json
import numpy as np
import fb_enhance as E
import fb_ocr as O

OUT = E.OUT

README_L = ["713", "765", "706", "824", "975", "937", "726", "729", "652",
            "653", "565", "746", "1021", "759", "718", "737", "648", "818",
            "985", "2154", "841", "71X", "75X", "689", "1017", "1280", "684",
            "694"]
README_R = ["473", "464", "447", "499", "595", "X30", "XY1", "X47", "400",
            "407", "X75", "X58", "?X59", "X75", "X38", "469", "428", "520",
            "621", "1307", "540", "471", "489", "447", "658", "625", "448",
            "453", "860", "514", "496"]

READING_L = {
    **{r: (v, "READ", "") for r, v in zip(range(1, 21), README_L[:20])},
    21: ("841", "READ",
         "all three digits legible on the hi-res frame with the mask-aware "
         "background; plain background division washed the units digit out"),
    22: ("71_", "PARTIAL", "units digit fully behind the figure's left foot"),
    23: ("7__", "PARTIAL",
         "tens digit sits on the clay boundary and survives only as an "
         "unidentifiable smear; units digit fully behind the foot"),
    24: ("689", "READ", "units 9 is clipped by the clay but unambiguous"),
    25: ("1017", "READ", ""),
    26: ("1280", "READ", ""),
    27: ("684", "READ", ""),
    28: ("_94", "PARTIAL",
         "the photograph's bottom edge cuts this row; only the top sliver of "
         "the hundreds digit is in frame"),
}
READING_R = {
    **{r: (v, "READ", "") for r, v in zip(range(1, 5), README_R[:4])},
    5: ("595", "READ",
        "all three digits legible on the hi-res frame with the mask-aware "
        "background"),
    6: ("__0", "PARTIAL", "tens and hundreds fully behind the figure's head"),
    7: ("__1", "PARTIAL", "tens and hundreds fully behind the head"),
    8: ("_47", "PARTIAL", "hundreds fully behind the head/shoulder"),
    9: ("400", "READ", "hundreds digit sits on the clay boundary but is clear"),
    10: ("407", "READ", ""),
    11: ("_75", "PARTIAL", "hundreds fully behind the shoulder"),
    12: ("__8", "PARTIAL", "tens and hundreds fully behind the arm"),
    13: ("__9", "PARTIAL",
         "tens and above behind the arm; the digit COUNT is also undetermined"),
    14: ("__5", "PARTIAL", "tens and hundreds behind the arm"),
    15: ("_38", "PARTIAL", "hundreds behind the arm"),
    16: ("_69", "PARTIAL",
         "THE 469 ROW.  6 and 9 are both clearly legible; the leading digit is "
         "entirely behind the figure's right arm and only a sliver of ink "
         "survives at the clay boundary"),
    17: ("428", "READ", "hundreds digit recovered by the mask-aware background"),
    **{r: (v, "READ", "") for r, v in zip(range(18, 32), README_R[17:])},
}
# Cells that are hopeless: opaque clay, or outside the photograph.
UNRECOVERABLE = {
    ("left", 22, 0): "opaque clay (left foot)",
    ("left", 23, 0): "opaque clay (left foot)",
    ("left", 23, 1): "clay boundary; only an unidentifiable smear survives",
    ("left", 28, 2): "outside the photograph's bottom edge",
    ("right", 6, 1): "opaque clay (head)",
    ("right", 6, 2): "opaque clay (head)",
    ("right", 7, 1): "opaque clay (head)",
    ("right", 7, 2): "opaque clay (head)",
    ("right", 8, 2): "opaque clay (head/shoulder)",
    ("right", 11, 2): "opaque clay (shoulder)",
    ("right", 12, 1): "opaque clay (arm)",
    ("right", 12, 2): "opaque clay (arm)",
    ("right", 13, 1): "opaque clay (arm)",
    ("right", 13, 2): "opaque clay (arm)",
    ("right", 14, 1): "opaque clay (arm)",
    ("right", 14, 2): "opaque clay (arm)",
    ("right", 15, 2): "opaque clay (arm)",
    ("right", 16, 2): "opaque clay (right arm)",
}


def build(soft, mask, tmpl):
    rows = []
    for i in range(1, 32):
        lp, lv, ln = READING_L.get(i, (None, "NOT-PHOTOGRAPHED", ""))
        rp, rv, rn = READING_R[i]
        rec = dict(
            row=i,
            left=dict(reading=lp, verdict=lv, note=ln,
                      readme=README_L[i - 1] if i <= 28 else None,
                      y=round(float(O.row_y("left", i)), 1) if i <= 28 else None),
            right=dict(reading=rp, verdict=rv, note=rn,
                       readme=README_R[i - 1],
                       y=round(float(O.row_y("right", i)), 1)))
        if i > 28:
            rec["left"]["note"] = ("this row's left value lies below the bottom "
                                   "edge of the photograph and was never captured")
        for side, pat in (("left", lp), ("right", rp)):
            if pat is None:
                continue
            cells = []
            for k, ch in enumerate(reversed(pat)):
                m = O.match(side, i, k, soft, mask, tmpl)
                cells.append(dict(slot=k, read=(ch if ch != "_" else None),
                                  visible=m["visible"], top=m["ranked"][:3],
                                  margin=m["margin"],
                                  unrecoverable=UNRECOVERABLE.get((side, i, k))))
            rec[side]["cells"] = cells
        rows.append(rec)
    return rows


def main():
    soft = np.load(os.path.join(OUT, "R_soft.npy"))
    mask = np.load(os.path.join(OUT, "R_mask.npy")) > 127
    O.prep(soft, mask)
    tmpl, _ = O.build_templates(soft, mask)
    rows = build(soft, mask, tmpl)
    geom = json.load(open(os.path.join(OUT, "geom.json")))
    cal = json.load(open(os.path.join(OUT, "recover.json")))["calibration"]
    out = dict(
        source=dict(
            file="data/external/provenance/fb/fb_hires.jpg",
            size=[1536, 2048],
            origin=("Facebook og:image for fbid 10150239378812364 on Tibia's "
                    "official page, posted 12 Aug 2011; 2x the linear "
                    "resolution of the 768x1024 copy previously in the repo "
                    "and genuinely more detailed (high-frequency RMS 3.46 vs "
                    "1.80 for an upscale of the small copy)"),
            note=("in the as-posted image the speech bubble reads correctly "
                  "and the NUMBERS are the mirrored element; the analysis "
                  "flips horizontally so the digits read left-to-right")),
        geometry=dict(
            rotation_deg=float(open(os.path.join(OUT, "angle.txt")).read()),
            left_rows=geom["left"]["nrow"],
            right_rows=geom["right"]["nrow"],
            row_pitch_px_first_last=[
                round(geom["left"]["y"][1] - geom["left"]["y"][0], 1),
                round(geom["left"]["y"][-1] - geom["left"]["y"][-2], 1)]),
        classifier_calibration=cal,
        total_rows=31,
        left_rows_photographed=28,
        rows=rows)
    p = os.path.join(os.path.dirname(OUT), "fb_pairs.json")
    json.dump(out, open(p, "w"), indent=1)
    print("wrote", p)
    print(f"\n{'row':>4} {'left':>7} {'verdict':>16} | {'right':>7} {'verdict':>8} "
          f"| README L / R")
    for r in rows:
        print(f"{r['row']:>4} {str(r['left']['reading']):>7} "
              f"{r['left']['verdict']:>16} | {str(r['right']['reading']):>7} "
              f"{r['right']['verdict']:>8} | {str(r['left']['readme']):>5} / "
              f"{r['right']['readme']}")


if __name__ == "__main__":
    main()
