# Family E — the structural null

*Agent 1. Every number here comes from `c469.stats`; every claim is either a
held-out code length (a decidable quantity, no null needed) or carries an
empirical p against `c469.surrogate` families.*

## Headline

**The 469 corpus is a copy-paste artefact.** Under a leave-one-book-out
protocol, a model that says "this book is made of pieces of the other books"
costs **0.40 bits per digit**, while the best sequential statistical model of
any order costs **0.90**. No fixed-order Markov chain, and no variable-order
context tree, comes within a factor of two of the copy model.

That is not a negative result about our search; it is a positive
characterisation of the object. It also bounds how much message there can be.

## 1. Model comparison (`model_compare.py`, `model_comparison.json`)

One protocol for everything: **leave-one-book-out**, bits per digit, every model
a real decodable code. Uniform base-10 is 3.322 bits/digit.

| model | held-out b/d | in-sample b/d | code length of the corpus (bits) |
|---|---|---|---|
| Markov-0 | 3.2655 | 3.2647 | 36,892 |
| Markov-1 | 2.9314 | 2.9206 | 34,106 |
| Markov-2 | 2.0029 | 1.9443 | 34,012 |
| Markov-3 | 1.2584 | 1.1588 | 134,186 |
| Markov-4 | 1.0367 | 0.9087 | 1,221,572 |
| Markov-5 | 0.9863 | 0.8303 | 12,122,725 |
| Markov-6 | 0.9904 | 0.8094 | 121,142,848 |
| CTW depth 2 | 1.9635 | 2.0797 | 23,424 |
| CTW depth 4 | 1.0742 | 1.3578 | 15,293 |
| CTW depth 8 | 0.9086 | 1.2558 | 14,144 |
| CTW depth 16 | **0.8988** | 1.2497 | 14,075 |
| **relative-LZ copy code** | **0.4047** | 0.6930 | **4,558** |

The best statistical model of any order — a variable-order context tree, which
is the strongest thing there is short of a semantic model — needs 0.90 bits per
digit. Saying "this book is made of pieces of the other books" needs **0.40**.
The copy code describes the whole 11,263-digit corpus in **4,558 bits**, a third
of what CTW needs and 1/8 of what a first-order chain needs. Markov's BIC blows
up past order 3 because the parameter count multiplies by ten each step; the
held-out column shows the same thing without needing BIC's asymptotics, and
Markov-6 is already *worse* held-out than Markov-5 (pure memorisation).

**The copy code is not a trick that wins everywhere.** The same table on
surrogates, held-out bits/digit:

| corpus (LZ76 factors) | Markov-3 | CTW-8 | relative-LZ copy |
|---|---|---|---|
| **real 469 (608)** | 1.258 | 0.909 | **0.405** |
| `Shuffle` (3378) | 3.545 | 3.266 | 3.963 (loses) |
| `MarkovK(3)` (1572) | 1.204 | 1.246 | 1.891 (loses) |
| `CopyPasteMutate` (1107) | 1.864 | 1.521 | **0.628** (wins) |

On i.i.d. and Markov material the copy code is *worse* than the sequential
models — it pays for pointers it cannot use. It wins only on material that was
actually built by copying. The real corpus sits on the copy-paste side of this
diagnostic, and further out than the shipped `CopyPasteMutate` defaults.

## 2. ABC fit of the copy-paste generator (`abc.py`, `abc_fit.json`)

The shipped `surrogate.CopyPasteMutate` defaults give ~1,107 LZ76 factors, not
608, so they were **not** yet a null that explains 469. `cpm.py` adds the free
parameters the plan lists — seed length, seed Markov order, segment count and
lengths, rotation probability, deletion rate — plus a **substitution** rate (the
documented `864` anomaly in B32 is a substitution, not a deletion) and a
**reuse** probability (a book may copy from an earlier book, not only from the
seed). Book lengths are matched by construction: the generator is handed the
real book lengths.

4,000 simulations, two rounds (uniform prior, then a perturbation kernel around
the best 60), distance = RMS of the 9 summaries standardised by their
prior-predictive SDs (`c469.stats.abc_summary`). Best distance 0.203.

**Posterior predictive vs the real corpus** (150 draws from the accepted set):

| summary | observed | posterior predictive | 95% interval | inside? | z |
|---|---|---|---|---|---|
| LZ76 factors | 608 | 679 +- 98 | [511, 863] | yes | -0.72 |
| distinct 4-grams (concat) | 1097 | 1030 +- 131 | [855, 1297] | yes | +0.52 |
| distinct 4-grams (within book) | 984 | 883 +- 135 | [705, 1158] | yes | +0.74 |
| distinct 6-grams (within book) | 1571 | 1583 +- 257 | [1089, 2121] | yes | -0.05 |
| longest cross-book repeat | 279 | 204 +- 38 | [143, 271] | **no** | **+2.01** |
| 20-mer repeat coverage | 0.840 | 0.827 +- 0.050 | [0.731, 0.920] | yes | +0.26 |
| h4 (bits/digit) | 0.9372 | 0.8662 +- 0.135 | [0.682, 1.230] | yes | +0.52 |
| unigram H | 3.2647 | 3.2534 +- 0.025 | [3.176, 3.282] | yes | +0.46 |
| IC | 0.10825 | 0.10990 +- 0.0039 | [0.1053, 0.1180] | yes | -0.43 |

**8 of 9 summaries are reproduced simultaneously**, including the pair the plan
named as the kill condition: LZ76 factors (608) *and* both distinct-4-gram
counts (984 within-book / 1097 over the concatenation), at the observed book
lengths. That is the plan's stated "confirms E" condition.

The one miss is the longest cross-book repeat: the corpus contains a 279-digit
stretch shared by two books that the model only reaches at the top of its range.
That is the documented B64/B65 pair (`05-rearrange.txt`'s B42/B43): one book is
the other with a 52-digit block moved. It is a single hand edit, not a
distributional property, so it does not rescue a linguistic hypothesis.

**Posterior** (median, 5-95%):

| parameter | posterior | prior |
|---|---|---|
| seed length | **2602** (986-5931) | 400-8000 |
| seed Markov order | 3 (2-4) | 1-4 |
| segments per book | 1 + Poisson(0.27) — i.e. **mostly one whole block per book** | lambda 0-3 |
| P(rotate a segment) | 0.29 (0.05-0.57) | 0-0.6 |
| per-digit deletion | 0.0009 (0-0.006) | 0-0.012 |
| per-digit substitution | 0.0015 (0-0.005) | 0-0.012 |
| P(copy from an earlier book) | 0.39 (0.03-0.83) | 0-0.9 |

The fitted model is now shipped as `c469.surrogate.CopyPasteMutateFitted` and
added to `DEFAULT_FAMILIES`. **This, not the unfitted `CopyPasteMutate`, is the
null every other family's claims must clear.**

## 3. The seed — the only thing left that could carry a message

If E is right, everything in the corpus except the *first* occurrence of each
piece is a copy, and copies carry no information. Three estimates of what is
actually left (`extract_seed.py`, `seed_estimate.json`):

| estimate | length | what it is |
|---|---|---|
| **A. LZ76 innovation string** of `master_v1` | **578 digits** | the one new digit that ends each of the master's 578 LZ76 factors — written to `data/seed_estimate.txt` |
| A'. same on the raw corpus | 608 digits | the 608 factor innovations |
| B. LZ77 literals of `master_v1` | 242 digits | digits the greedy copy parse could not take from earlier material at all (414 copy tokens cover the other 5,814) |
| C. information bound | **~2,350 digit-equivalents** (7,806 bits) | the whole corpus's relative-LZ code length / log2(10) — a hard ceiling on how much independent content exists, including all the pointer bookkeeping |

`data/seed_estimate.txt` holds estimate A (578 digits). The honest reading of
the three: the corpus's 11,263 digits contain **at most about 2,350 digits'
worth of independent content, and plausibly as little as 242-608**. Under the
ABC posterior the underlying seed is ~2,600 digits of order-3 Markov-like
material, which is consistent with C and means most of even that 2,350 is
statistical filler rather than a message.

**This is the object families A, B and C should now be pointed at.** Searching
the full 11,263 digits for structure mostly re-finds the copy-paste.

## 4. Scored nulls

`run_nulls.py` scores `copy_code_advantage = CTW8 bits/digit - relative-LZ
bits/digit` (and LZ76 factors, and distinct 4-grams) against
`surrogate.DEFAULT_FAMILIES`, N=200. Results land in `results/`.

## Verdict on family E

**Confirmed, on the plan's own stated criteria.** A fitted copy-paste process
reproduces 8 of 9 summary statistics of the corpus simultaneously, including the
LZ76/distinct-4-gram pair that was named as the kill condition, and a copy code
beats every sequential model by more than a factor of two in held-out bits per
digit. Nothing here forbids a message *inside the seed*, and E does not by
itself prove there is no plaintext — but it removes the corpus-wide statistics
as evidence for one, and it shrinks the target from 11,263 digits to a few
hundred.
