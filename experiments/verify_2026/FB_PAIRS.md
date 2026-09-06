# The 2011 Facebook number pairs, re-read from a 2× original

Handoff item 5 of `experiments/provenance/HANDOFF_UNBLOCKED_NETWORK.md`.

**Headline results**

1. **A higher-resolution original exists and is now in the repo.** The post's own
   `og:image` is **1536 × 2048**, four times the pixels of the 768 × 1024 copy the
   repo had. Saved as `data/external/provenance/fb/fb_hires.jpg`.
2. **The table has 31 rows, not 28.** The left column has 28 rows *because the
   photograph's bottom edge cuts it there*. The right column has 31. The three
   right-hand orphans (860, 514, 496) do have left partners — those partners are
   **below the bottom edge of the photograph** and were never captured. They are
   not behind the clay figure and they are not absent from the page.
3. **The README's 1:1 pairing is geometrically correct**, and is now confirmed
   rather than assumed.
4. **Zero digits were converted from unknown to known.** Everything legible in
   this photograph was already claimed by the README. What did change is the
   other direction: **seven cells the README/`cribs.py` treat as legible are not
   legible**, including the leading `4` of the `469` in row 16.

---

## 1. Source

The 768 × 1024 files in `data/external/provenance/fb/` are downsamples. The
original upload is still served by Facebook's crawler endpoint for the post
(`fbid 10150239378812364`, Tibia's official page, 12 Aug 2011, caption "Have a
nice weekend!"), at **1536 × 2048**, and it is a genuine 2× original rather than
an enlargement: high-frequency RMS is 3.46 against 1.80 for a Lanczos upscale of
the small copy, and the two agree to a mean absolute difference of 1.4/255 when
the big one is downsampled. 2048px on the long edge was Facebook's ceiling for
2011 uploads, so this is almost certainly the largest version that exists.

No Wayback capture of the post exists. TibiaWiki, tibiasecrets, talesoftibia and
the `s2ward/469` repo itself host nothing larger than 768 × 1024.

**Orientation note.** In the as-posted image the speech bubble reads correctly
and the *numbers* are the mirrored element (they are show-through from the far
side of the printed sheet). All work here flips the image horizontally so the
digits read left-to-right; the bubble then reads backwards, which is expected.

## 2. Method

Code in this directory, run in order:

| script | what it does |
| --- | --- |
| `fb_enhance.py` | un-mirror; background division; CLAHE; unsharp; clay mask |
| `fb_deskew.py` | finds the page rotation by maximising row-profile sharpness, rotates |
| `fb_geom.py` | fits each column's row grid, right-alignment edge and digit advance |
| `fb_ocr.py` | builds digit templates from the page's own legible glyphs; matches fragments |
| `fb_recover.py` | calibrates the classifier under occlusion; classifies every occluded cell |
| `fb_annot.py`, `fb_read.py` | magnified per-row crops with the digit grid drawn on, for reading by eye |
| `fb_channels.py` | per-channel separation test; cost of the mask dilation |
| `fb_pairs.py` | emits `fb_pairs.json` and the table in §4 |

`fb_out/*.npy` are regenerable caches and are gitignored; run `fb_deskew.py` to
rebuild them.

### What actually made the difference

**Mask-aware background division.** The photograph has a strong vignette whose
dynamic range is much wider than the ink's, so global contrast stretching cannot
work; dividing by a Gaussian-blurred copy of the image removes it. But the clay
figure is large and nearly black, and it drags the blurred background estimate
down in a **halo far wider than the blur radius**. Inside that halo the ratio
image is ≈ 1 everywhere and the digits vanish completely. Replacing the plain
blur with a normalised convolution — `blur(image·w)/blur(w)` with `w = 0` on the
clay — estimates the background from paper pixels only. This is what recovers
`595`, `400`, `407`, `428`, `841`, `689`, and the `6` of row 16's `_69`; all of
those looked blank or fragmentary under plain flattening. It is the single most
important step and is worth more than the resolution increase.

**Deskew by rotation, not shear.** The sheet is rotated **−18.2°** in the frame.
Two independent measurements agree (within-number baseline slope −0.333, column
direction +0.32 from vertical), and the angle is confirmed by maximising the
sharpness of the horizontal ink profile. After rotation both columns are
vertical and both sit on the *same* row grid, which is what settles the pairing.

**A fitted digit grid.** Row pitch is not constant — residual perspective grows
it from 64.6 px at the top to 74.1 px at the bottom — so each column's row
positions are a quadratic in row index. The right-alignment edge and the digit
advance are fitted the same way (edge fit residual ≤ 8 px, about a quarter of a
digit). This gives every digit *slot* a predicted box **independent of whether
any ink survives inside it**, which is the only way to say which digit position
a fragment belongs to. Fitting the edge required excluding rows whose units
digit is occluded — otherwise their rightmost surviving glyph drags the fitted
edge inwards by a full digit width.

### Things tried that did not help

- **Per-channel (R/G/B) separation.** Paper and ink are both neutral. Measured
  SNR of the flattened ratio: L 16.6, R 15.8, G 16.2, B 16.3 — no channel
  separates the digits better than luminance. The channels are useful only for
  building the clay mask, which is strongly saturated.
- **Global CLAHE / aggressive thresholding.** Maximum sensitivity, but it
  binarises and invents texture in the vignette. Kept only as a confirmation
  layer (`02_hard.png`), never as the basis of a reading.
- **A tighter clay mask.** Shrinking the mask dilation raises nominal visibility
  on the marginal cells by ~15 points (e.g. right r16 slot 2, 0.27 → 0.42), but
  the extra area is the clay's own dark penumbra, not paper. Inspected at 14×:
  no additional digit strokes appear. It would only feed dark non-ink pixels to
  the classifier.

### The classifier, and how far it should be trusted

The sheet is set in one font at one size, so every digit legible somewhere on
the page is an exemplar for the same digit where it is occluded. Templates are
built from the bounding boxes of 99 unoccluded glyphs on 41 rows; a fragment is
matched by sliding each template over a small window (±8 px, ±8 % scale) around
its predicted grid cell and scoring only the pixels the clay does not cover.

Leave-one-out accuracy, with synthetic occlusion applied from the same side the
clay eats each column:

| fraction of cell hidden | accuracy | accuracy when top-2 margin ≥ 0.10 |
| --- | --- | --- |
| 0 % | 98.0 % (n=99) | 100 % (n=87) |
| 15 % | 96.0 % | 100 % (n=78) |
| 30 % | 89.9 % | 98.4 % (n=64) |
| 45 % | 82.8 % | 98.0 % (n=49) |
| 60 % | 78.8 % | 90.2 % (n=41) |

Read that table as a warning, not a licence. Even on a *fully visible* digit the
classifier is wrong about 1 time in 50, and it was wrong on three fully visible
digits in this very run (it called the `0` of `1021` a `1`, the `8` of `648` a
`3`, and the `8` of `684` a `3`). **No verdict below rests on the classifier
alone.** Every reading was settled by eye at 8–14× on the annotated grid, with
the classifier used only as a second opinion. Where the two disagree, the report
says so.

## 3. Geometry, and the row count

After deskewing, the two columns lie on nearly the same row grid — the offset
between them runs from +16 px at row 1 to −4 px at row 28, against a pitch of
65–74 px. That is far under half a row everywhere, so **the 1:1 pairing is a
measured fact, not an assumption.**

Boundaries of the printed table:

- **Top.** Right row 1 (`473`) sits at source y = 7.5, i.e. right against the
  photograph's top edge, with its glyph tops slightly clipped; a hypothetical row
  0 would be at y = −55, outside the frame. But the left column's row 0 position
  *is* inside the frame and is **blank photographed paper** (`fb_out/Z_topleft.png`).
  Combined with the row-grid alignment, `713` ↔ `473` is row 1 of the table.
- **Bottom.** The right column ends at `496`, with the sheet's own bottom-right
  corner visible just below it (`fb_out/Z_botright.png`) — that is the end of the
  list. The left column's last captured row is 28 (`_94`), sitting at source
  y = 2044 of 2048. Mapping rows 29–31 of the left column back through the
  rotation puts them at source y = 2107, 2172, 2235 — **63, 128 and 191 px below
  the bottom of the photograph.** `fb_out/Z_botleft.png` shows the frame edge
  cutting diagonally right through row 28.

So: **31 rows total; 28 left values photographed; 3 left values lost to the
crop.** The README's "28 pairs" counts the left column, and its remark that the
monotone relation holds for "26/28" is computed on an incomplete table.

## 4. The alignment table

`READ` = every digit legible. `PARTIAL` = some digits legible, `_` marks a
position that exists but cannot be read. `NOT-PHOTOGRAPHED` = outside the frame.
The README column is the existing transcription, kept strictly separate.

| row | left read | verdict | right read | verdict | README L | README R | agree? |
| ---: | ---: | --- | ---: | --- | ---: | --- | --- |
| 1 | 713 | READ | 473 | READ | 713 | 473 | ✓ |
| 2 | 765 | READ | 464 | READ | 765 | 464 | ✓ |
| 3 | 706 | READ | 447 | READ | 706 | 447 | ✓ |
| 4 | 824 | READ | 499 | READ | 824 | 499 | ✓ |
| 5 | 975 | READ | **595** | READ | 975 | 595 | ✓ |
| 6 | 937 | READ | `__0` | PARTIAL | 937 | X30 | **README claims a `3` that is not visible** |
| 7 | 726 | READ | `__1` | PARTIAL | 726 | XY1 | ✓ |
| 8 | 729 | READ | `_47` | PARTIAL | 729 | X47 | ✓ |
| 9 | 652 | READ | **400** | READ | 652 | 400 | ✓ |
| 10 | 653 | READ | **407** | READ | 653 | 407 | ✓ |
| 11 | 565 | READ | `_75` | PARTIAL | 565 | X75 | ✓ |
| 12 | 746 | READ | `__8` | PARTIAL | 746 | X58 | **README claims a `5` that is not visible** |
| 13 | 1021 | READ | `__9` | PARTIAL | 1021 | ?X59 | **README claims a `5`; digit count also undetermined** |
| 14 | 759 | READ | `__5` | PARTIAL | 759 | X75 | **README claims a `7` that is not visible** |
| 15 | 718 | READ | `_38` | PARTIAL | 718 | X38 | ✓ |
| 16 | 737 | READ | **`_69`** | PARTIAL | 737 | **469** | **the leading `4` is NOT visible** |
| 17 | 648 | READ | **428** | READ | 648 | 428 | ✓ |
| 18 | 818 | READ | 520 | READ | 818 | 520 | ✓ |
| 19 | 985 | READ | 621 | READ | 985 | 621 | ✓ |
| 20 | 2154 | READ | 1307 | READ | 2154 | 1307 | ✓ |
| 21 | **841** | READ | 540 | READ | 841 | 540 | ✓ |
| 22 | `71_` | PARTIAL | 471 | READ | 71X | 471 | ✓ |
| 23 | `7__` | PARTIAL | 489 | READ | 75X | 489 | **README claims a `5` that is not visible** |
| 24 | **689** | READ | 447 | READ | 689 | 447 | ✓ |
| 25 | 1017 | READ | 658 | READ | 1017 | 658 | ✓ |
| 26 | 1280 | READ | 625 | READ | 1280 | 625 | ✓ |
| 27 | 684 | READ | 448 | READ | 684 | 448 | ✓ |
| 28 | `_94` | PARTIAL | 453 | READ | 694 | 453 | **the leading `6` is cut by the frame** |
| 29 | — | NOT-PHOTOGRAPHED | 860 | READ | — | 860 | below the crop |
| 30 | — | NOT-PHOTOGRAPHED | 514 | READ | — | 514 | below the crop |
| 31 | — | NOT-PHOTOGRAPHED | 496 | READ | — | 496 | below the crop |

Bold marks values that plain background division could not read and the
mask-aware version can.

**Every digit this analysis can read agrees with the README.** There is no cell
where the README states a digit and the pixels say a different one. All the
disagreements are of one kind: the README asserts digits that are not there to
be seen.

## 5. Per-value detail on the occluded cells

Format: what is legible / what the README says. These are kept separate on
purpose.

| cell | legible | confidence | README | why not more |
| --- | --- | --- | --- | --- |
| right r6 | `__0` | units `0` high (fully visible, margin 0.19) | `X30` | tens and hundreds are opaque clay (head). Nominal visibility of the tens cell is 0.27 and the classifier's top-2 margin is 0.00 — no information at all. |
| right r7 | `__1` | units `1` high (margin 0.22) | `XY1` | tens and hundreds opaque (head). |
| right r8 | `_47` | tens `4` good (57 % visible, margin 0.23), units `7` high | `X47` | hundreds opaque (head/shoulder), visibility 0.00. |
| right r11 | `_75` | tens `7` good (55 % visible, margin 0.18), units `5` high | `X75` | hundreds opaque (shoulder). |
| right r12 | `__8` | units `8` high (margin 0.27) | `X58` | tens cell is 13 % visible with margin 0.04. The `5` is a guess. |
| right r13 | `__9` | units `9` high (margin 0.34) | `?X59` | tens 25 % visible, margin 0.02. Digit count unknown — nothing survives left of the units digit to bound it. |
| right r14 | `__5` | units `5` high | `X75` | tens 32 % visible; classifier prefers `7` at margin 0.09, below the bar. Suggestive of `7`, **not** assertable. |
| right r15 | `_38` | tens `3` and units `8` both legible by eye | `X38` | hundreds opaque (arm). |
| **right r16** | **`_69`** | tens `6` good (fully visible, margin 0.20), units `9` high (margin 0.25) | `469` | **the hundreds digit is entirely behind the figure's right arm.** Nominal visibility 0.27, and what is inside that 27 % is the clay's penumbra, not ink. The `4` cannot be read from this photograph at any resolution. |
| left r22 | `71_` | `7` high, `1` good (margin 0.13) | `71X` | units digit behind the left foot, 33 % nominally visible, margin 0.04. |
| left r23 | `7__` | `7` high (margin 0.31) | `75X` | tens is a smear on the clay boundary — 33 % visible, and the classifier prefers `4` at margin 0.07, *disagreeing with the README's `5`*. Neither is assertable. Units fully behind the foot. |
| left r28 | `_94` | `9` and `4` legible though clipped | `694` | the photograph's bottom edge crosses this row; only the top sliver of the hundreds digit is in frame. |

### On row 16 and the `4` of `469`

This is the one that matters, so it is worth being blunt. `fb_out/A_right_13_16.png`
(bottom panel) shows row 16 at 10×: a complete `6` and a complete `9` in the tens
and units slots, and solid black clay across the whole hundreds slot with a few
pixels of ink at the very boundary. `469` is not a reading from this photograph.
It is an inference — a well-motivated one, since `_69` plus the cipher's name
leaves little else, but an inference. `cribs.py` currently lists `(737, 469)` in
`FB_PAIRS_CERTAIN`, which is exactly the kind of guess-promoted-to-datum that
`FB_PAIRS_OBSCURED` exists to prevent.

## 6. Proposed changes to `c469/cribs.py`

Not applied — proposing only.

1. **Move `(737, 469)` out of `FB_PAIRS_CERTAIN`.** The right value reads `_69`;
   the leading digit is opaque clay. If Family D is fitted on it, it is being
   fitted on an inference.
2. **Move `(694, 453)` out of `FB_PAIRS_CERTAIN`.** The left value reads `_94`;
   the leading digit is outside the photograph.
3. **Correct five `FB_PAIRS_OBSCURED` annotations that overstate what is
   legible**, so the pattern strings match the pixels:
   - `(937, None, "X30, …")` → the legible pattern is `__0`, not `X30`.
   - `(746, None, "X58, …")` → `__8`.
   - `(1021, None, "?X59, …")` → `__9`, digit count unknown.
   - `(759, None, "X75, …")` → `__5`.
   - `(None, 489, "75X")` → the left value's legible pattern is `7__`; the `5`
     is not visible and the classifier weakly prefers `4`.
   The four that are correct as written — `(729, "X47")`, `(565, "X75")`,
   `(718, "X38")`, `(None, 471, "71X")` — are independently confirmed here.
4. **Add the three lost rows** so the table's true length is recorded, e.g. a
   `FB_PAIRS_UNPHOTOGRAPHED = ((None, 860), (None, 514), (None, 496))` with a
   note that these left values exist on the page but fall below the crop. Any
   analysis that assumes 28 pairs is working with a truncated table.
5. **Note in the docstring that the table has 31 rows**, that the columns are
   row-aligned after a −18.2° deskew, and point at `fb_hires.jpg` as the
   canonical source.

## 7. Honest bottom line

The 2× original and the mask-aware background between them turned six
fragmentary cells into full readings (`595`, `400`, `407`, `428`, `841`, `689`)
and added a confidently-read digit to three more (`_47`, `_75`, `_69`). But
**every one of those digits was already in the README.** As held-out validation
data for Family D, the net gain is zero new values and a small amount of
independent confirmation.

The real finding is subtraction: seven cells that the repo currently treats as
observations are inferences, `469` among them, and the table is three rows
longer than anyone recorded. Fixing that makes the held-out set smaller and more
honest, which is the direction that protects the fit.

Nothing behind opaque clay is recoverable. There is no further preprocessing to
try on those cells — they contain no signal, at any resolution.
