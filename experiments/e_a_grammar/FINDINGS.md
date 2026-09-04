# Family A — variable-length code / token induction

**Verdict: the pre-registered 1.577-digits-per-unit prediction FAILS, and the
MDL-optimal dictionary is not a lexicon. Family A is dead as a route to
plaintext.** What it produces instead is a clean, quantitative restatement of
the corpus's copy-paste structure.

Pre-registration: [`PREREGISTRATION.md`](PREREGISTRATION.md), committed in
`53bce66` before any inducer was run.

## What was run

Five inducers over the digit stream, all in
[`inducers.py`](inducers.py), all scored with one common two-part MDL accounting
(`mdl_bits`) so the numbers compare:

| inducer | status |
|---|---|
| BPE, V ∈ {50, 100, 200, 400, 1000} | run |
| Re-Pair | run |
| LZ78 dictionary | run |
| **MDL-optimal dictionary segmentation** (Viterbi shortest-path parse, EM re-estimation, vocabulary pruning by measured MDL gain) | run — **the arbiter** |
| Sequitur | implemented and validated on short streams (≤200 digits); the rule-utility check is O(rules²) per match and it does not terminate within budget on 3.9k digits. Re-Pair is the offline greedy equivalent and answers the same question, so nothing is lost — but it is an honest gap, not a completed run. |

Streams: the deduplicated core (`dedup_core(load_books())`, 22 books, 3901
digits, LZ76 = 510) and the published contigs (`load_contigs()`, 6687 digits,
LZ76 = 563). Never the raw 70-book corpus alone. `data/master_v1.txt` did not
exist when this ran; the code picks it up automatically if it is regenerated.

## A1 — the pre-registered token-length test

Prediction: mean token length in **[1.5, 1.7]** (P1) with **8–10** single-digit
tokens (P2).

| stream | MDL-argmin V | mean token length | P1 | length-1 types | P2 |
|---|---|---|---|---|---|
| dedup core | 76 | **2.029** | **FAIL** | 10 | pass (see caveat) |
| contigs | 121 | **2.984** | **FAIL** | 10 | pass (see caveat) |

**P1 fails on both streams**, and not marginally: the contigs figure is 75%
above the top of the predicted band. The failure is in the direction that
matters — the induced tokens are *longer* than a 26–32 letter code would need,
not shorter.

**P2's "pass" is degenerate and must not be counted as support.** The MDL parser
forces all ten digits into the vocabulary because the stream has to be coverable
at all; a length-1 type count of 10 is therefore guaranteed by construction, not
discovered. The informative version of P2 is the *shape* of the induced
vocabulary, and that is where the real result is:

| stream | types by token length |
|---|---|
| dedup core | 1:**10**, 2:**0**, 3:**0**, 4:**0**, 5:1, 6:1, 7:0, 8:**64** |
| contigs | 1:**10**, 2:**0**, 3:2, 4:3, 5:2, 6:1, 7:1, 8:**102** |

The MDL-optimal dictionary is **bimodal**: the ten bare digits, plus a block of
tokens pinned at the maximum allowed length. There are **no length-2 tokens at
all** and essentially nothing between. A variable-length code over a ~26-symbol
alphabet at 1.577 digits/unit must put most of its *types* at length 2 and 3.
The corpus contains no such layer.

This is not an artifact of the length cap. Raising `maxlen` moves the upper mode
with it and keeps improving the MDL, which is the signature of verbatim
repetition, not of a lexicon:

| maxlen | 4 | 6 | 8 | 12 | 16 |
|---|---|---|---|---|---|
| MDL (bits) | 11430 | 10944 | 10718 | 10575 | **10423** |
| mean token length | 1.753 | 2.096 | 2.029 | 2.480 | 2.205 |
| types by length | 1:10, 2:1, 3:1, **4:43** | 1:10, 3:2, 5:1, **6:69** | 1:10, 5:1, 6:1, **8:64** | …, **12:70** | …, **16:46** |

The dictionary always wants the ten digits plus whatever the longest permitted
verbatim chunk is. The top-frequency long tokens are exactly the corpus's known
cross-book repeats (`45191991`, `80036468`, `89521991`, `12889521`, …).

The comparison inducers agree, with the caveat that their vocabulary size is a
free knob and so they cannot arbitrate:

| inducer (dedup core) | mean token length | V | MDL bits |
|---|---|---|---|
| bpe50 | 1.926 | 50 | 11698 |
| bpe100 | 2.578 | 98 | 11485 |
| bpe200 | 3.893 | 162 | **11372** (BPE's own MDL optimum) |
| bpe400 | 7.771 | 232 | 13318 |
| bpe1000 / Re-Pair | 8.060 | 237 | 13439 |
| LZ78 | 2.245 | 372 | 20455 |
| **MDL-optimal** | **2.029** | **76** | **10719** |

BPE's MDL optimum sits at V=200 with mean length 3.89 — again far above the
band, and again with no length-2 layer to speak of.

Raw data: [`a1_tokenlen.json`](a1_tokenlen.json), reproduced by
`python experiments/e_a_grammar/run_a1_tokenlen.py`.

## A2 — every statistic against surrogates run through the same inducer

The pre-registration forbids two things that are the usual way this analysis goes
wrong, and both are honoured here:

1. **Zipf slope and Heaps' beta are never compared to a textbook value.** BPE and
   MDL segmenters manufacture Zipf-like curves on noise, so the only meaningful
   comparison is to the distribution of the *same* statistic produced by running
   the *same* inducer on surrogates.
2. **The MDL comparison is only made against surrogates matched on LZ76 factor
   count.** The real corpus wins on compression against unmatched surrogates for
   reasons that have nothing to do with language, so an unmatched p is not
   evidence of anything.

`CopyPasteMutate` was tuned per stream to match the real LZ76 factor count. On
the deduplicated core the match is essentially exact (**509.7 vs 510, 0.07%
error**, at `seed_len=900, seed_order=2, p_delete=0.006, max_segments=10`); on
the contigs it is **554.7 vs 563 (1.5%)**. (The first attempt at the contigs
failed to match at all, 1079 vs 563. The cause was a tuner grid that held
`max_segments` fixed at 3: `CopyPasteMutate` pads any book longer than about
`max_segments × seed_len` with independent random digits, which drives LZ76 up.
Adding `max_segments` to the grid fixed it. Had it not, the pre-registration
required reporting the MDL comparison on that stream as uninformative rather
than quoting an unmatched p — worth recording, because the unmatched version
would have looked like a large, spurious win for the real corpus.)

### Deduplicated core (22 books, 3901 digits, real LZ76 = 510), N = 200 per family

| statistic | real | Shuffle | Markov2 | Markov3 | BlockShuffle20 | **CopyPasteMutate (LZ-matched)** | pi |
|---|---|---|---|---|---|---|---|
| MDL bits/digit | **2.748** | 3.312±0.008 (z=−74.1) | 3.164±0.032 (z=−13.2) | 2.989±0.038 (z=−6.3) | 2.990±0.024 (z=−10.2) | **2.687±0.055 (z=+1.1, p=0.89)** | 3.378±0.008 (z=−80.5) |
| mean token length | **2.029** | 1.019±0.004 (z=+226.8) | 1.190±0.047 (z=+17.7) | 1.414±0.062 (z=+9.9) | 1.517±0.072 (z=+7.1) | **2.199±0.157 (z=−1.1, p=0.13)** | 1.017±0.004 (z=+256.6) |
| frac. occurrences at length ≤2 | **0.852** | 0.997±0.003 (z=−50.4) | 0.949±0.014 (z=−6.7) | 0.935±0.011 (z=−7.4) | 0.906±0.015 (z=−3.6) | **0.823±0.024 (z=+1.2, p=0.11)** | 0.999±0.002 (z=−86.8) |
| length-2 types | **0** | 1.26±0.74 | 0.24±0.50 | 0.04±0.18 | 0.23±0.46 | **0.06±0.26 (z=−0.2)** | 1.40±0.67 |
| vocabulary size | **76** | 12.0±0.1 (z=+643) | 25.8±4.8 (z=+10.5) | 45.9±5.8 (z=+5.2) | 53.3±6.8 (z=+3.3) | **80.5±6.5 (z=−0.7, p=0.77)** | 12.0±0.2 (z=+348) |
| **Zipf slope s** | **1.304** | 0.960±0.101 (z=+3.4) | 1.876±0.120 (z=−4.8) | 1.812±0.094 (z=−5.4) | 1.664±0.085 (z=−4.2) | **1.227±0.065 (z=+1.2, p=0.11)** | 0.736±0.125 (z=+4.5) |
| **Heaps' beta** | **0.356** | 0.016±0.014 (z=+24.9) | 0.142±0.049 (z=+4.3) | 0.313±0.048 (z=+0.9) | 0.324±0.053 (z=+0.6) | **0.361±0.060 (z=−0.1, p=0.55)** | 0.015±0.016 (z=+21.5) |

Surrogate mean LZ76 factors: Shuffle 1357, Markov2 957, Markov3 729,
BlockShuffle20 746, **CopyPasteMutate 504**, pi 1390.

### Contigs (6687 digits, real LZ76 = 563), matched at 1.5%

| statistic | real | CopyPasteMutate (LZ-matched) | CopyPasteMutateFitted | Markov3 |
|---|---|---|---|---|
| MDL bits/digit | **2.353** | 2.481±0.421 (z=−0.3, p=0.62) | 2.718±0.044 (z=−8.3) | 2.844±0.030 (z=−16.2) |
| mean token length | **2.984** | 3.696±1.384 (z=−0.5, p=0.25) | 2.982±0.517 (z=+0.0, p=0.49) | 1.679±0.093 (z=+14.1) |
| length-2 types | **0** | 0.88±1.95 (z=−0.5) | 0.03±0.17 (z=−0.2) | 0.21±0.47 (z=−0.5) |
| vocabulary size | **121** | 137.8±60.3 (z=−0.3, p=0.82) | 176.7±30.1 (z=−1.9) | 83.6±12.4 (z=+3.0) |
| Zipf slope | **0.999** | 0.838±0.268 (z=+0.6, p=0.17) | 0.888±0.157 (z=+0.7, p=0.27) | 1.484±0.097 (z=−5.0) |
| Heaps' beta | **0.282** | 0.328±0.185 (z=−0.2, p=0.73) | 0.352±0.145 (z=−0.5, p=0.65) | 0.363±0.055 (z=−1.5) |

### master_v1 (agent 1's ILP assembly, 6056 digits, real LZ76 = 578), matched at 0.17%

| statistic | real | CopyPasteMutate (LZ-matched) | CopyPasteMutateFitted (LZ 583) | Markov3 |
|---|---|---|---|---|
| MDL bits/digit | **2.485** | 2.695±0.342 (z=−0.6, p=0.32) | 2.763±0.036 (**z=−7.8**) | 2.906±0.031 (z=−13.6) |
| mean token length | **2.655** | 3.794±1.977 (z=−0.6, p=0.32) | 2.428±0.342 (z=+0.7, p=0.83) | 1.563±0.072 (z=+15.2) |
| length-2 types | **0** | 0.81±1.68 (z=−0.5) | 0.04±0.18 (z=−0.2) | 0.12±0.33 (z=−0.4) |
| vocabulary size | **114** | 144.7±80.5 (z=−0.4, p=0.68) | 138.0±22.7 (z=−1.1, p=0.83) | 71.7±9.8 (z=+4.3) |
| Zipf slope | **1.079** | 1.005±0.641 (z=+0.1, p=0.32) | 1.046±0.145 (z=+0.2, p=0.31) | 1.585±0.092 (z=−5.5) |
| Heaps' beta | **0.705** | 0.418±0.273 (z=+1.1, p=0.17) | 0.276±0.140 (**z=+3.1**, p=0.030) | 0.356±0.052 (z=+6.8) |

### Reading the tables

**Against the LZ-matched copy-paste null, every Family A statistic is
indistinguishable from noise.** The largest |z| across all seven statistics is
**1.2**, and no p is below 0.11. Specifically:

- **No MDL gain.** The real corpus needs **2.748 bits/digit**; the matched
  surrogate needs **2.687**. The real corpus is very slightly *worse*
  (z = +1.1, p = 0.89). The kill criterion's second clause is met.
- **The Zipf slope is a red herring.** s = 1.304 is in the range one would
  happily call "language-like" against a textbook value of ~1.0 — and the
  copy-paste null produces 1.227 ± 0.065 with no message in it whatsoever
  (z = +1.2). This is precisely the failure mode the pre-registration was
  written to prevent, and it would have produced a false positive here.
- **Heaps' beta likewise.** 0.356 is just below the 0.4–0.6 "language" band, and
  the null reproduces it at 0.361 ± 0.060 (z = −0.1).
- Against the *weaker* nulls (Shuffle, Markov2/3, BlockShuffle20, pi) the real
  corpus looks wildly distinctive on every statistic — z from +3 to +643. That
  apparent significance is entirely an artifact of those nulls not reproducing
  the corpus's long-range copying, and quoting it would have been the error the
  plan warned about.
- The same picture holds on the contigs and on `master_v1`: against the
  LZ-matched null, no statistic on any stream reaches |z| = 1.2.

### The two things that are not clean, reported anyway

Two cells are bold in the tables above, and both deserve saying out loud rather
than being smoothed over.

**(a) Two LZ-matched nulls disagree on the assembled streams.** On the contigs
and on `master_v1`, the ABC-fitted `CopyPasteMutateFitted` (which happens to
land at LZ76 579 and 583 against real 563 and 578 — matched to within 1%) says
the real stream compresses *better* than the null by z ≈ −8, while the
grid-tuned `CopyPasteMutate` says nothing (z ≈ −0.3 to −0.6). The reason is
variance, and it is a genuine methodological weakness of the tuned generator:
matching the *mean* LZ76 factor count left it with an enormous spread
(MDL bits/digit sd 0.34–0.42 against the fitted generator's 0.04). A null that
noisy has almost no power, so its non-significance is weak evidence. The
low-variance fitted null is the more informative comparison, and on the two
assembled streams it does show the real stream to be more compressible than the
model.

That is worth flagging for Family E — but it is **not** support for a lexicon,
because the very same runs show the token-length profile flat against that null
(mean token length z = +0.0 and +0.7; length-2 types z = −0.2 on both). The
streams are slightly more repetitive than the fitted copy-paste process; they
are not more *lexical*.

**(b) `master_v1` has a high Heaps' beta (0.705).** Against the fitted null,
z = +3.1, p = 0.030. Against the LZ-matched tuned null, z = +1.1, p = 0.17.
Two cautions apply. First, `master_v1` is a *derived* object — an ILP assembly —
and the plan's own rule is that anything appearing only on the master is
suspect; a vocabulary-growth exponent is exactly the kind of statistic assembly
can manufacture by concatenating overlapping fragments. Second, multiplicity:

> **Benjamini–Hochberg over all 42 tests against LZ-matched nulls
> (7 statistics × 3 streams × 2 matched generators): the smallest q is 0.104,
> and the `master_v1` Heaps result sits at q = 0.418.**

Nothing in Family A survives correction. (Note that p = 0.005 is the floor at
N = 200, i.e. "no surrogate out of 200 beat it".)

## Verdict

The pre-registered kill criterion is:

> no length-1/2 concentration **and** no MDL gain over LZ-matched surrogates
> ⇒ Family A is dead.

Both clauses hold.

1. **No length-1/2 concentration.** The MDL-optimal vocabulary contains **zero**
   length-2 tokens on every stream and at every `maxlen`. It is ten bare digits
   plus long verbatim chunks. There is no lexicon layer.
2. **No MDL gain over LZ-matched surrogates.** z = +1.1, p = 0.89 — the real
   corpus compresses very slightly *worse* than a copy-paste process fitted to
   its own LZ76 factor count.

And the primary pre-registered prediction fails outright: the Facebook-pair ratio
predicts a mean codeword length of **1.577**; the measured MDL-optimal figures
are **2.029** (dedup core) and **2.984** (contigs). **Family A is dead.** It
provides no support for the variable-length-code hypothesis, and the 1.577
prediction should not be counted as corroborated by token induction.

What Family A *does* deliver is a positive statement, and it agrees with
Family E: the induced structure of 469 — its dictionary, its MDL curve, its
Zipf slope, its Heaps exponent — is fully accounted for by one string cut up and
pasted with mutation. Nothing in the token statistics needs a lexicon to explain
it.

## Reproducing

```
python experiments/e_a_grammar/run_a1_tokenlen.py      # the pre-registered test
python experiments/e_a_grammar/run_a2_nulls.py         # the surrogate tables
python experiments/e_a_grammar/summarize_a2.py         # regenerate the tables above
```

Raw: [`a1_tokenlen.json`](a1_tokenlen.json), [`a2_nulls.json`](a2_nulls.json),
scored `Result`s in `results/A2_*.json`.
