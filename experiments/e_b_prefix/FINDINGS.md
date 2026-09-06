# Family B — prefix-code enumeration, and the 1.577 gate

Agent 2. Branch `claude/cypher-solving-agents-hqnbq7`.
Predictions fixed in `PREREGISTRATION.md` (commit `70c8416`) before any run.

Corpus: `books.json`, 70 books / 11,263 digits, via `c469.corpus.load_books()`.
Every statistic comes from `c469.stats`; every scored number is a
`c469.harness.Result` in `results/` with its null distributions attached.

---

## Headline

1. **No prefix code with codewords of length <= 3 parses all 70 books, except
   the degenerate one.** Over the enumerated space the only structure that
   parses 70/70 is `S1 = {0..9}` — the identity "code" that is just the digits
   themselves. The best non-degenerate structure reaches **68/70** and is
   near-degenerate too (mean codeword length 1.11, only one prefix digit).
   Inside the pre-registered 1.50–1.70 band the best is **60/70**, out of
   841,879 structures in band.

   Stronger, and covering incomplete codes too: **over all 9.5 M structures the
   largest mean codeword length attainable with a letter-sized effective
   alphabet (20-40 codewords actually used) is 1.4495** — it never reaches 1.50,
   let alone 1.577.

2. **The 1.577 prediction is refuted in the form the plan stated it, and the
   refutation is a counting theorem, not a search result.** A *complete* 10-ary
   prefix code with <= 2-digit codewords satisfies `10*m1 + m2 = 100`, so a
   letter-sized codebook of 28 codewords is forced to be exactly 8 singles +
   20 doubles — and on this corpus that code attains a mean codeword length of
   **at most 1.3015**. Reaching 1.577 requires a codebook of **>= 55** codewords.
   The two halves of the prediction ("mean length 1.577" and "~26–32 letters
   with ~8 on single digits") are mutually exclusive.

3. **The token-induction half of the prediction is unfalsifiable as posed.**
   Mean induced token length is a smooth monotone function of the vocabulary
   budget V, passing through 1.577 at V ~ 32 (BPE) and V ~ 40 (MDL) on all
   three datasets. The pre-registered honesty clause therefore applies. Scored
   properly — mean token length at a fixed V = 32, against 200 surrogates per
   family — all four pre-registered runs are **REJECTED** (worst-family p =
   0.56-0.67); `Markov3` reproduces the real value to three decimals.

4. **The `07` gap does not need a codebook.** It is significant only against
   unigram-matched nulls (`Shuffle`/`IID`/pi, p = 0.002 = the 1/(1+500) floor);
   against `Markov2`, `Markov3` and `CopyPasteMutate` it is entirely ordinary
   (p = 1.00, 1.00, 0.79).

---

## B1 — the enumeration

### The search space

A *structure* is `(S1, T)`: `S1` are the single-digit codewords; every digit
outside `S1` is a length-1 prefix; for each prefix `p`, `T_p` says which
continuations `pd` are themselves prefixes (expanded to ten length-3 codewords)
rather than codewords. Codeword length is capped at 3. Codebook size is
`|S1| + 10k + 9*sum|T_p|` with `k = 10 - |S1|`. Given `(S1, T)` the parse is
**forced and unique**, so each structure is one linear pass (numba kernel,
`enum_core.py`, ~59k structures/s/core).

`FULL_SPACE` enumerated (`b1_enumerate.py`):

| \|S1\| | cap on sum\|T_p\| | structures | max codebook |
|---|---|---|---|
| 10 | 0 | 1 | 10 |
| 9 | 10 (complete) | 10,240 | 109 |
| 8 | 6 | 2,720,700 | 82 |
| 7 | 4 | 3,831,720 | 73 |
| 6 | 3 | 2,247,210 | 73 |
| 5 | 2 | 321,552 | 73 |
| 4 | 2 | 384,510 | 82 |
| 3 | 1 | 8,520 | 82 |
| 2 | 1 | 3,645 | 91 |
| 1 | 1 | 910 | 100 |
| **total** | | **9,529,008** | |

`|S1| ∈ {9,10}` is enumerated *completely*. For smaller `|S1|` the cap makes
each branch exhaustive up to the stated codebook size. That is the honest
boundary of the claim. The `|S1| = 8` branch was capped at 6 rather than
exhausted (2^20 per S1) because the frontier below proves it can never reach
mean length 1.5 whatever `T` is.

A separate `REDUCED_SPACE` of **70,803** structures (1,023 S1 tasks) is the one
re-run identically on every surrogate in B4.

### Why the statistic is banded

Parse success is confounded with codeword length: a code whose codewords are
almost all one digit long lands on a book's final boundary almost every time.
So `max n_books_parsed` is reported **within mean-codeword-length bins**.
`V` below is the *effective* alphabet — the number of codewords the forced
parse actually uses. Unused codewords can be deleted for free (the code stays
prefix-free, merely incomplete), which is exactly hypothesis (i) for `07`.

### Results

`out/b1_full.json`, 9,529,008 structures in 467 s wall (4 workers).

* **max n_books_parsed overall = 70/70 — attained by exactly one structure,
  `S1 = {0..9}`**, the identity "code" (10 codewords, mean length 1.000). That
  is not a code; it is the digit string itself.
* the best **non-degenerate** structure parses **68/70**: `S1 = {0,1,2,3,4,5,7,8,9}`,
  `6` the only prefix, 19 codewords, mean codeword length **1.111**.
* inside the pre-registered band 1.50-1.70: **60/70**, from 841,879 structures
  in band. The best is `S1 = {0,1,2,3,4,9}`, prefixes `{5,6,7,8}`, three
  length-3 expansions (`14`, `51`, `52`), 64 codewords, 69 used, mean length
  1.525.
* **max n_books_parsed by mean-codeword-length bin** (`out/full.log` has all
  47 bins):

| mean length | structures | max parsed | best S1 | \|codebook\| | V used |
|---|---|---|---|---|---|
| 1.01 | 1 | **70** | 0123456789 | 10 | 10 |
| 1.11 | 1,602 | 68 | 012345789 | 19 | 19 |
| 1.15 | 40,210 | 67 | 012345789 | 37 | 30 |
| 1.25 | 538,443 | 65 | 01234579 | 28 | 40 |
| 1.35 | 734,314 | 62 | 0123479 | 37 | 37 |
| 1.45 | 389,032 | 61 | 0123479 | 64 | 57 |
| 1.53 | 127,710 | 60 | 012349 | 64 | 69 |
| 1.57 | 87,547 | 57 | 01349 | 73 | 71 |
| 1.65 | 48,316 | 56 | 0134 | 82 | 75 |
| 1.75 | 4,590 | 49 | 0347 | 82 | 78 |
| 1.85 | 552 | 43 | 04 | 91 | 85 |
| 1.93 | 241 | 46 | 9 | 100 | 92 |

The trend is monotone and mechanical: the longer the code, the fewer books end
on a codeword boundary. Nothing stands out against it.

### The sharpest form of the incompatibility

Tracking the *effective* alphabet V (codewords the forced parse actually uses;
unused ones can be deleted for free, which is exactly what an incomplete
prefix code is) over all 9.5 M structures:

> **The largest mean codeword length attainable with a letter-sized effective
> alphabet (V in [20,40]) is 1.4495.**

Not 1.50, let alone 1.577. This covers incomplete codes as well as complete
ones, so it is stronger than the Kraft counting argument in B3(a) below, and it
is the single number that kills the prediction as stated.


---

## B3(a) — the alphabet-size / mean-length frontier

`b3_frontier.py`, exact, over every `S1` with `sum|T_p| <= 1..4`:

| codebook size | largest attainable mean codeword length | S1 | books parsed |
|---|---|---|---|
| 10 | 1.0000 | 0123456789 | 70/70 |
| 19 | 1.1510 | 023456789 | 61/70 |
| **28** | **1.3015** | 02356789 | 55/70 |
| 37 | 1.4324 | 0236789 | 46/70 |
| 46 | 1.5401 | 023689 | 41/70 |
| **55** | **1.6430** | 02369 | 37/70 |
| 64 | 1.7214 | 2369 | 32/70 |
| 73 | 1.8058 | 379 | 37/70 |
| 82 | 1.8803 | 37 | 34/70 |
| 91 | 1.9389 | 3 | 36/70 |

* letter-sized codebooks (24–34 codewords): max mean length **1.3015**
* smallest codebook that can reach 1.577: **55**

The 5.15 bits/unit that 1.577 digits buys is real — it is just not a 26–32
letter alphabet under a prefix code. It is a ~55–73 symbol alphabet, i.e. a
**homophonic** code with ~2–2.5 symbols per letter, or not a letter code.

Supporting arithmetic (corpus unigrams `1`=.166 `5`=.129 `4`=.113 `6`=.101
`8`=.099 `9`=.089 `7`=.085 `2`=.084 `0`=.076 `3`=.058): eight single-digit
codewords cover ~87% of the digit mass, forcing mean length ~1.13, not 1.577.
Getting to 1.577 needs the single-digit codewords to cover only ~42% of the
mass — four or five digits, not eight. The plan's "~8 high-frequency letters
get single-digit codewords" is arithmetically inconsistent with 1.577.

---

## B2 — what explains `07`?

Measured facts (`out/b2_structure.json`):

* exactly one missing bigram, `07`; expected count under independence **72.3**
* next-rarest: `33` (1 obs / 37.4 exp), `32` (2 / 54.3), `39` (4 / 57.7),
  `66` (12 / 113.7), `02` (13 / 71.3), `69` (13 / 100.6), `37` (14 / 55.1)
* book-final digits: `0`x9 `1`x12 `2`x6 `3`x4 `4`x8 `5`x9 `6`x2 `7`x6 `8`x7 `9`x7

### (i) `0` is a prefix and `07...` is an unassigned codeword — *disfavoured*

`b2_zero_role.py` splits the whole reduced-space enumeration by whether `0` is
a codeword or a prefix, within the same length band:

| | n structures | max books parsed | mean books parsed |
|---|---|---|---|
| `0` a codeword, all lengths | 39,509 | **70/70** | 52.32 |
| `0` a prefix, all lengths | 31,294 | 64/70 | 44.52 |
| `0` a codeword, band 1.50–1.70 | 10,748 | **58/70** | 44.77 |
| `0` a prefix, band 1.50–1.70 | 14,274 | 54/70 | 42.38 |

Making `0` a prefix costs parse coverage rather than buying it. The same split
for `3` (whose `{2,3,9}` continuations are the other near-forbidden bigrams)
gives 58 (codeword) vs 53 (prefix) in band; for `1` — the one digit the cribs
constrain, since "It's 1, not Tibia" makes `1` a codeword — 58 vs 53. And in
the reduced-space best-per-bin set, `0` and `3` are *never simultaneously*
prefixes in the best structure of any bin (0 of 37). So the mechanism (i)
needs for `07` is not the mechanism the data picks for `32/33/39`. The effect
sizes are small (58 vs 54 books), so this is a *lean*, not a refutation — but
it leans against (i).

### (ii) `0` is a delimiter / escape — *coherent but unsupported*

Splitting on `0`: 753 "words", mean length **13.82 +- 11.57** digits, max 62,
and **172** empty gaps (`00` runs). Word-initial digit distribution
`4`:.227 `1`:.177 `3`:.175 `8`:.110 `9`:.104 `5`:.097 `6`:.076 `2`:.027
`7`:**.008** `0`:.000. The six `7`-initial "words" are exactly the six books
that *begin* with `7`, so under this reading no word ever begins with `7` —
internally consistent, but that is a restatement of the `07` gap, not
independent support.

Against nulls (500 per family), none of it survives:

| statistic | real | Shuffle | Markov2 | Markov3 | BlockShuffle20 | CopyPasteMutate | pi | IID |
|---|---|---|---|---|---|---|---|---|
| n missing bigrams | 1 | 0 (p=.002) | 1.56 (p=1.00) | 1.47 (p=1.00) | 0.00 (p=.004) | 1.18 (p=.79) | 0 (p=.002) | 0 (p=.002) |
| word-initial-7 rate | .0080 | .0924 (p=.002) | .0078 (p=.55) | .0082 (p=.48) | .0133 (p=.088) | .0093 (p=.38) | .112 (p=.002) | .0918 (p=.002) |
| mean word length | 13.82 | 12.25 (p=.002) | 13.83 (p=.51) | 13.84 (p=.52) | 13.68 (p=.020) | 13.87 (p=.52) | 9.72 (p=.002) | 12.24 (p=.002) |

All three verdicts: **REJECTED** (BH q-values in `results/e_b_prefix.b2.*.json`;
the worst-family q is 0.61–1.00 in every case). A 13.8-digit mean "word" is
9–11 letters at 1.3–1.6 digits/letter — far too long for a word — and a
delimiter that doubles 172 times is not behaving like a delimiter.

### (iii) `07` is a forbidden *plaintext* bigram — *refuted on frequencies*

If `0` and `7` are single letters they sit at 7.6% and 8.5% of the stream. The
nearest German letters are `i` (7.55%), `s` (7.27%), `r` (7.00%), `n` (9.78%);
the nearest English ones `n` (7.23%), `o` (7.64%), `s` (6.51%), `r` (6.28%).
These are among the ten commonest letters in both languages and **no pair of
them has a forbidden bigram** in German or English. (iii) would require a
language in which two top-ten letters never co-occur in that order.

**Conclusion for B2:** the `07` gap is not evidence for a codebook. It is
significant only relative to models that ignore the corpus's own bigram
structure. Every null that preserves that structure — including the copy-paste
null the plan calls the leading hypothesis — reproduces a single missing bigram
as a matter of course. The p ~ e^-72 figure in the plan assumes independence,
which the corpus's own bigram chi-square (5277 / 81 df) already refutes.

---

## B3(b) — token induction

`b3_tokens.py`: BPE, and a SentencePiece-style unigram-LM/MDL dictionary
(Viterbi shortest-description parse + EM + pruning), on `books70`, the
deduplicated core (22 books / 3,901 digits) and the contigs.

Mean induced token length vs vocabulary budget V (`out/b3_curves.json`):

| V | BPE books70 | BPE core22 | BPE contigs | MDL books70 | MDL core22 | MDL contigs |
|---|---|---|---|---|---|---|
| 16 | 1.196 | 1.202 | 1.197 | 1.181 | 1.185 | 1.189 |
| 24 | 1.402 | 1.410 | 1.407 | 1.326 | 1.335 | 1.367 |
| 28 | 1.499 | 1.509 | 1.506 | 1.393 | 1.407 | 1.423 |
| **32** | **1.583** | **1.596** | **1.588** | 1.443 | 1.457 | 1.473 |
| 36 | 1.668 | 1.680 | 1.672 | 1.490 | 1.523 | 1.518 |
| **40** | 1.748 | 1.753 | 1.756 | **1.532** | **1.575** | **1.567** |
| 50 | 1.929 | 1.926 | 1.938 | 1.658 | 1.742 | 1.694 |
| 100 | 2.579 | 2.568 | 2.586 | 2.675 | 2.515 | 2.604 |
| 200 | 3.821 | 3.649 | 3.753 | 4.173 | 3.666 | 4.107 |
| 500 | 5.629 | 4.734 | 5.375 | 5.083 | 5.359 | 5.536 |

The curve is monotone in V on every dataset by both methods, crossing 1.577 at
V ~ 32 (BPE) and V ~ 40 (MDL). That is exactly the situation the
pre-registration named as **no evidence either way**. So the prediction is
reported as *unfalsifiable as posed*; the only informative version is the
null-scored one at a fixed V, below.

MDL held-out description length at the letter-alphabet end is 2.6–2.7
bits/digit (V=32–40) against H1 = 3.265 — a real but modest compression, and
one the surrogates must be allowed to match before it means anything.

Zipf slopes at V ~ 32 are 0.69–0.74 (BPE) and 1.44–1.60 (MDL); natural language
is ~1.0. Heaps' beta at V = 200 is 0.30–0.45.

### The null-scored version

The only informative form of the prediction is the mean token length at a
**fixed, pre-set** vocabulary size. V = 32 is the letter-alphabet size at which
the prediction is actually being made. 200 surrogates per family, `Pool(8)`.

| run | real | in [1.50,1.70]? | Shuffle | Markov2 | Markov3 | BlockShuffle20 | CopyPasteMutate | Digits_pi | verdict |
|---|---|---|---|---|---|---|---|---|---|
| core22 / BPE | 1.5962 | **yes** | 1.351+-.006 (p=.005) | 1.580+-.018 (.18) | 1.601+-.023 (.57) | 1.548+-.006 (.005) | 1.586+-.023 (.32) | 1.309+-.004 (.005) | REJECTED |
| core22 / MDL | 1.4567 | no | 1.304+-.017 (.005) | 1.426+-.030 (.16) | 1.451+-.037 (.41) | 1.464+-.022 (.67) | 1.360+-.042 (.015) | 1.266+-.009 (.005) | REJECTED |
| contigs / BPE | 1.5876 | **yes** | 1.340+-.005 (.005) | 1.577+-.014 (.20) | 1.591+-.018 (.61) | 1.556+-.002 (.005) | 1.516+-.086 (.24) | 1.296+-.000 (.005) | REJECTED |
| contigs / MDL | 1.4732 | no | 1.313+-.013 (.005) | 1.434+-.030 (.10) | 1.436+-.031 (.11) | 1.476+-.020 (.56) | 1.311+-.046 (.005) | 1.269+-.007 (.005) | REJECTED |

Every run's **worst-family p is 0.56-0.67** and the verdict is REJECTED.
`Markov3` reproduces the real value almost exactly (1.601 vs 1.596 on the core;
1.591 vs 1.588 on the contigs); so does `CopyPasteMutate` for BPE.

The only families the real corpus beats are `Shuffle`, `BlockShuffle20` and pi
(all p = 0.005, the 1/(1+200) floor) — i.e. the real corpus's tokens are longer
than they would be if its bigram structure were destroyed. That is a restatement
of "the corpus has strong bigram dependence", which the plan's established facts
already record as chi-square = 5277.

**Verdict on B3.** The token-induction half of the 1.577 prediction is
confirmed only in the sense that a mean length of ~1.58 is what a V = 32
tokenizer produces on *any* sequence with the corpus's bigram statistics,
message or not. Two of the four pre-registered runs land outside the target
window anyway (MDL: 1.457 and 1.473). The prediction is not supported.


---

## B4 — null calibration

`b4_nulls.py`, 200 surrogates from each of `Shuffle`, `Markov2`, `Markov3`,
`BlockShuffle20`, `CopyPasteMutate` and the digits of pi — 1,200 identical
searches, 674 s.

The calibration space is smaller than B1's, because it has to run 1,200 times:
`NULL_SPACE = {|S1|=9: sum|T|<=3, |S1|=8,7: <=1, all smaller |S1|: 0}` =
**7,273 structures**, covering the whole mean-length range 1.00–1.94 including
the band. The real corpus is re-scored on exactly this space, which is why its
`band_parsed` is 56 here and 60 in the full B1 search.

| statistic | real | Shuffle | Markov2 | Markov3 | BlockShuffle20 | CopyPasteMutate | Digits_pi | verdict |
|---|---|---|---|---|---|---|---|---|
| max_parsed | 70 | 70.0+-0.0 (p=1.00) | 70.0+-0.0 (1.00) | 70.0+-0.0 (1.00) | 70.0+-0.0 (1.00) | 70.0+-0.0 (1.00) | 70.0+-0.0 (1.00) | REJECTED |
| band_parsed | 56 | 54.8+-1.9 (0.34) | 55.1+-2.0 (0.40) | 54.9+-1.9 (0.35) | 54.9+-2.2 (0.36) | 55.2+-1.9 (0.45) | 55.2+-2.0 (0.40) | REJECTED |
| vwin_parsed | 68 | 67.9+-1.1 (0.63) | 67.9+-0.9 (0.64) | 67.7+-1.0 (0.56) | 67.8+-0.9 (0.61) | 67.9+-1.0 (0.65) | 67.3+-0.8 (0.47) | REJECTED |
| best_chi2_de | 30.93 | 30.92+-0.02 (1.00) | 28.95+-4.66 (0.69) | 28.34+-4.85 (0.70) | 29.01+-3.80 (1.00) | 28.21+-6.20 (0.68) | 91.59+-4.98 (0.005) | REJECTED |
| best_chi2_en | 2.617 | 2.617+-0 (1.00) | 3.20+-1.26 (0.35) | 3.11+-1.17 (0.41) | 2.617+-0 (1.00) | 4.55+-2.10 (0.20) | 80.02+-1.69 (0.005) | REJECTED |

Benjamini-Hochberg over all 30 (statistic, family) tests: the smallest q is
**0.075** (the two pi comparisons); every other q is **1.000**.

**The honest conclusion, stated as the task required: the family-B search has
essentially no power.**

* Every surrogate family — including `CopyPasteMutate`, the generative form of
  "there is no message" — finds a structure that parses 70/70 books, exactly as
  the real corpus does, because the identity structure is always available.
* In the 1.50–1.70 band the real corpus's best (56 books) is **+0.4 to +0.6
  sigma** above the surrogate means. It is inside the surrogate range for every
  family (surrogate maxima reach 60–62, i.e. *better* than the real corpus).
* The letter-frequency chi-square is worse still: on `Shuffle` and
  `BlockShuffle20` the null distribution has **standard deviation ~0** and sits
  exactly on the real value. That is a diagnostic, not a coincidence — those
  surrogates preserve the digit unigrams exactly, and the statistic's optimum is
  determined by the unigrams alone. The chi-square arm of family B is reading
  the digit histogram and nothing else.
* Only the digits of pi separate (z = -12 for German, -46 for English), and in
  the direction that says "pi's digits are too uniform to look like letters".
  That is the *one* thing this method can detect, and it is not a message.

So no family-B "hit" could have been believed even if one had appeared. The
value of the family is the exhaustive negative and the frontier, both of which
are deterministic facts about the corpus and need no null.


---

## What this closes, and what it does not

**Closed.** Within the enumerated space (9.5 M structures, codewords <= 3
digits), there is no non-degenerate complete prefix code that parses all 70
Hellgate books; and there is none at all — enumerated or not — that combines
mean codeword length 1.577 with a letter-sized alphabet, because that is a
counting result over every complete <=2-digit 10-ary prefix code.

**Not closed.** Incomplete prefix codes with many unused codewords, codewords
longer than 3 digits, codes with a context-dependent (non-prefix) parse, and
codes whose alphabet is genuinely homophonic at ~55–73 symbols. The last is the
live remainder of family B: it is the object family C should be handed, and the
frontier table says exactly how big its alphabet has to be.

## Files

* `PREREGISTRATION.md` — predictions, fixed before any run
* `enum_core.py` — numba kernels (forced parse, effective alphabet, enumeration)
* `b1_enumerate.py` — B1 driver (`full` / `reduced` spaces)
* `b2_structure.py`, `b2_zero_role.py` — B2
* `b3_frontier.py`, `b3_tokens.py` — B3
* `b4_nulls.py` — B4
* `out/` — raw outputs and logs; `results/e_b_prefix.*.json` — scored Results
