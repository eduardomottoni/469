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

See [`a2_nulls.json`](a2_nulls.json) and `results/A2_*.json`.
