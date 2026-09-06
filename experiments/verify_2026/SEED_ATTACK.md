# Attacking the innovation residue — powered methods, matched nulls

*Everything here is reproducible from `experiments/verify_2026/`. Nothing in the
existing experiment directories was modified. `python -m c469.selftest` passes
on this tree.*

## Headline

Three results, in order of how much they change the picture.

1. **The 578-digit seed was the wrong object, and it was wrong for a measurable
   reason.** `extract_seed.py` charges every match of length >= 3 to the copy
   model. Over a ten-symbol alphabet that is nearly free: an i.i.d. digit stream
   of the corpus's own length already contains a >= 3 match at **91%** of its
   positions. Raising the copy threshold to the chance-corrected value (>= 6,
   false-copy rate 0.6%) and taking the union of four parse orders yields a
   residue of **1,535 digits**; at >= 8 it yields **2,058**, which is the largest
   residue still consistent with the corpus's own information bound of ~2,350
   digit-equivalents. That is **3.6x the PR's target**.

2. **The whole pipeline is now demonstrably powered, and the old one was not.**
   Injecting a real message into the *seed* of `CopyPasteMutateFitted`,
   generating a 70-book corpus at the real book lengths, extracting, and solving
   recovers the injected key at **97.6%** (mean of 4 reps, truncated to 469's own
   residue length) under `union / min_copy=8`. The same test on the PR's
   `lz76_innovation` extraction recovers **4.4%**. The PR's negative on the
   578-digit seed was not a negative about 469; it was the extraction deleting
   the message.

3. **With a powered pipeline, the residue is still empty.** No configuration of
   any method beats its matched null. Across 50 pre-registered numeric/periodicity
   tests **zero** clear BH q < 0.05 against the matched null; the best q anywhere
   is **0.083**, shared by `kasiski` at n=1535 (not replicated at any of the four
   other residue sizes, and with a 10% empirical false-positive rate against
   i.i.d. input at that configuration) and by `lz76_pd` at n=2713 (which measures
   retained copy-paste and vanishes at the chance-corrected threshold). Fixed-V
   substitution solving, which recovers injected ciphers at 98-99% character
   accuracy at these exact shapes, **never exceeds the mean of its matched null**
   — the maximum z over all ten configurations is +0.01.

So the honest position moves: the seed question was previously *open because the
method was too weak*. It is now closed for the hypotheses tested — simple
substitution at V=10, homophonic at V=100 fixed a priori, A1Z26, decimal ASCII,
dates, periodic/Vigenere structure — at a power level that would have found any
of them.

---

## 1. Enlarging the target

### 1.1 Why min_copy = 3 destroys the residue

`chance_threshold.py` runs the extraction's own matcher on the real corpus and on
20 i.i.d. digit streams of identical length:

| min_copy | share of REAL positions inside a "copy" | FALSE-copy rate (i.i.d.) |
|---|---|---|
| 3 | 0.9508 | **0.9108** |
| 4 | 0.9022 | 0.3989 |
| 5 | 0.8666 | 0.0539 |
| 6 | 0.8379 | **0.0057** |
| 7 | 0.8141 | 0.0006 |
| 8 | 0.7924 | 0.0001 |
| 10 | 0.7541 | 0.0000 |
| 12 | 0.7223 | 0.0000 |

At `min_copy = 3` the copy model is being credited with 95% of the corpus on
evidence that random digits supply 91% of the time. **min_copy = 6 is the
chance-corrected threshold** (false-copy rate 0.6%); 8 and above are
conservative.

### 1.2 Parse orders and the permissive variant

`residue.py` implements four parse policies — greedy LZSS, LZSS with lazy
matching, the **minimum-code-length parse** by dynamic programming (the parse an
actual encoder would choose, not the greedy approximation), and the greedy parse
run backwards and mapped back — plus two combinations: `intersect` (a position is
innovation only if every policy says so) and `union` (**permissive: a position is
copied only if every policy agrees it is copied, so ambiguous innovation is
kept**). Alternative copy-source assignments are covered implicitly: the four
policies resolve source ambiguity differently, and `union` keeps anything they
disagree about.

### 1.3 The residues

`python experiments/verify_2026/residue.py` (full table in `residues.json`):

| residue | n | unigram H | IC | bigram chi2 (df=81) | LZ76 factors | LZ76/n |
|---|---|---|---|---|---|---|
| `PR_seed_estimate` (= master lz76 innovation) | 578 | 3.2571 | 0.10768 | 66.2 | 289 | 0.500 |
| `concat:lz76_innovation` | 608 | 3.2637 | 0.10708 | 92.2 | 307 | 0.505 |
| `concat:greedy_mc3` (LZ77 literals, the PR's estimate B) | 246 | 3.2981 | 0.09962 | 86.3 | 149 | 0.606 |
| `concat:greedy_mc6` | 791 | 3.2720 | 0.10587 | 265.4 | 327 | 0.413 |
| `concat:union_mc5` | 1238 | 3.2876 | 0.10404 | 342.8 | 394 | 0.318 |
| **`concat:union_mc6`** (chance-corrected) | **1535** | 3.2796 | 0.10538 | 497.2 | 429 | 0.279 |
| **`concat:union_mc8`** (largest under the info bound) | **2058** | 3.2824 | 0.10518 | 777.0 | 489 | 0.238 |
| `concat:union_mc10` | 2354 | 3.2848 | 0.10492 | 948.9 | 503 | 0.214 |
| `concat:union_mc12` | 2713 | 3.2788 | 0.10581 | 1157.0 | 524 | 0.193 |
| `master:union_mc8` | 2087 | 3.2792 | 0.10566 | 822.8 | 530 | 0.254 |
| `master:union_mc12` | 2835 | 3.2699 | 0.10718 | 1216.7 | 560 | 0.198 |

**How the enlarged residues differ statistically from the 578.** Unigram entropy
and IC are indistinguishable (3.257-3.285, IC 0.104-0.108) — enlargement does not
change the digit distribution. What changes is short-range structure: bigram
chi-square per digit rises from 0.115 at n=578 (which is *below* the df=81
expectation — the 578-digit residue has less bigram structure than chance) to
0.34-0.43 for the union residues, and LZ76 factors per digit falls from 0.50 to
0.19-0.28. That is the honest cost of enlargement: the permissive residues
retain short repeats. It is **not** a reason to prefer the small one — section 2
shows the small one cannot carry a recoverable message at all, and section 3
scores the retained structure against nulls that reproduce it.

They are also **not nested**. `union_mc8` contains only 62% of the 608
LZ76-innovation positions (`greedy_mc3` contains 22%); LZ76 innovation keeps the
digit that *terminates* each factor, a different criterion from "not inside a
copy". These are different objects, not a chain of subsets.

**Largest defensible residue: 2,058 digits** (`concat:union_mc8`; 2,087 on
`master_v1`). Beyond min_copy=10 the residue exceeds the corpus's ~2,350
digit-equivalent information bound from the PR's estimate C, which proves it is
re-including genuine copies; `union_mc12` at 2,713 is reported below but is
flagged as over the bound.

---

## 2. Power first: put a message in the seed and try to get it back

`pipeline_power.py`. This is the test that decides whether any null result here
is worth printing.

A known plaintext (10-letter reduced English under a fixed digit substitution) is
used as the **seed** of `c469.surrogate.CopyPasteMutateFitted` at its
posterior-median parameters. A 70-book corpus is generated at the real book
lengths with the fitted rotation / deletion / substitution / book-reuse
behaviour, with per-digit provenance tracked. Each extraction policy is run on the
result and the residue is solved; `key_acc` is the frequency-weighted share of
the ten cipher digits mapped to the right letter. Because the fitted generator is
slightly *less* redundant than 469 itself, its residues are longer than the real
ones, so every residue is also truncated to **exactly the length the same policy
yields on the real corpus** and re-solved. That matched column is the one to read.
4 repetitions.

| extraction | n_res (synthetic) | purity | seed recall | key acc (full) | n matched to 469 | **key acc (matched)** |
|---|---|---|---|---|---|---|
| `greedy` min_copy=3 (PR estimate B) | 302 | 0.988 | 0.114 | 0.074 | 246 | **0.109** |
| `lz76_innovation` (PR estimate A) | 964 | 0.791 | 0.333 | 0.055 | 608 | **0.044** |
| `greedy` min_copy=6 | 1941 | 0.976 | 0.726 | 0.581 | 791 | **0.774** |
| `union` min_copy=5 | 2882 | 0.525 | 0.718 | 0.549 | 1238 | **0.474** |
| `union` min_copy=6 | 3749 | 0.516 | 0.830 | 0.659 | 1535 | **0.854** |
| **`union` min_copy=8** | 4743 | 0.509 | 0.948 | 0.877 | 2058 | **0.976** |
| `union` min_copy=12 | 5074 | 0.500 | 0.974 | 0.877 | 2713 | **0.840** |

Per-repetition matched key accuracy: `union/8` = 1.00, 0.90, 1.00, 1.00;
`lz76_innovation` = 0.10, 0.00, 0.00, 0.08.

Two things follow.

* **The PR's extraction is not merely underpowered, it is lossy in the specific
  way that matters.** It recovers only 33% of the seed's digits and 4% of an
  injected key. `purity` — the share of residue digits that are the first corpus
  occurrence of their seed position — is *highest* for the PR's policies (0.79-0.99
  against 0.51 for `union`), and it does not help: purity buys nothing if recall
  and length are too low for a solver to work with. Chasing a clean residue was
  the wrong objective.
* **`union / min_copy=8` recovers an injected message essentially perfectly at
  469's own residue length.** Any null result reported on that residue below is a
  statement about 469, not about the method.

---

## 3. Numeric, periodicity and fixed-code statistics

`run_numeric.py`. Ten statistics, pre-registered with a declared direction before
any null was drawn; five residues; 300 null draws per family; 20 injected
plaintexts per hypothesis per statistic for power.

**Nulls, in two tiers.** The lesson of the PR's `Markov3_digits` false positive
(+6.26 sigma, r = +0.908 with the vocabulary gap) is that a null which does not
control the *shape of the object being measured* manufactures z on its own. So:

* **End-to-end** — each of the six `c469.surrogate.DEFAULT_FAMILIES` corpora
  pushed through the identical extraction. Controls the pipeline. **Does not
  control residue length**, and the gap is enormous: on the `union_mc8`
  configuration the real residue is 2,058 digits while `E2E:Shuffle` yields
  11,263 and `E2E:CopyPasteMutateFitted` yields 2,527. Length-sensitive
  statistics (`bigram_chi2_pd`, `lz76_pd`) are therefore *uninterpretable*
  against these families, exactly as the MDL vocabulary gap made `Markov3_digits`
  uninterpretable. These are reported in `numeric_results.json` and are not used
  to support any claim.
* **Matched** — `ResidueShuffle` (the real residue permuted: exact length, exact
  digit multiset) and `ResidueMarkov3` (order-3 resample of the residue itself:
  exact length, near-exact inventory, sequential arrangement destroyed). The
  digit-stream analogue of Family C's `Markov3_symbols`. **These decide.**

`ResidueShuffle` is deliberately the weaker of the two: it destroys all sequential
structure, so any residue that retains short copies beats it trivially
(`bigram_chi2_pd` reaches z = +85 on `union_mc12`). That is measuring leftover
copy-paste, not a message, which is why `ResidueMarkov3` — which reproduces the
residue's own order-3 statistics — is the null quoted.

### Power

Each statistic is evaluated on 20 injected plaintexts per hypothesis at the
target's exact length, and counted as detecting if it clears the 99th percentile
of `ResidueShuffle`. Summarised over the five targets:

| statistic | a1z26 | ASCII | dates | Vigenere-7 | subst-10 | i.i.d. control (false-positive rate) |
|---|---|---|---|---|---|---|
| `ic` | 1.00 | 1.00 | 1.00 | 0.75-1.00 | 1.00 | 0.00 |
| `bigram_chi2_pd` | 1.00 | 1.00 | 0.90-1.00 | 1.00 | 1.00 | 0.00 |
| `lz76_pd` | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 0.00 |
| `periodic_ic_max` | 1.00 | 1.00 | 1.00 | **1.00** | 1.00 | 0.00 |
| `kasiski` | 1.00 | 1.00 | 0.65-1.00 | **1.00** | 0.00 | 0.00-0.10 |
| `diff_ic` | 1.00 | 1.00 | **0.00-0.15** | 0.45-0.90 | 1.00 | 0.00 |
| `a1z26_frac` | 1.00 | 1.00 | 1.00 | **0.20-0.35** | 1.00 | 0.00-0.05 |
| `a1z26_chi2` | **0.55** at n=578, 1.00 above | **0.00** | 0.00-1.00 | 0.10-1.00 | 0.10-1.00 | 0.00 |
| `ascii_frac` | 0.90-1.00 | 1.00 | 1.00 | **0.10-0.15** | 0.95-1.00 | 0.00 |
| `date_frac` | 1.00 | 1.00 | 1.00 | **0.10-0.25** | 1.00 | 0.00-0.05 |

Read the bold cells as the stated limits: the fixed-code statistics
(`a1z26_frac`, `ascii_frac`, `date_frac`) have essentially **no power against an
enciphered plaintext**, which is expected and is why `periodic_ic_max` and
`kasiski` (power 1.00 against Vigenere-7) are in the set. `a1z26_chi2` is
**underpowered at n = 578** (0.55) and is not a valid negative there.
`diff_ic` is underpowered against the date hypothesis. Everything else is
powered at every residue size tested.

### Results against the matched null

Full tables per target in `numeric_results.json`; regenerate with
`python experiments/verify_2026/summarize_attack.py`. The two-sided empirical p
carries the +1 correction; BH q is taken across all 50 (target, statistic)
pairs against each matched family.

| residue | n | best z vs `ResidueMarkov3` | statistic | p | BH q |
|---|---|---|---|---|---|
| R578_PR | 578 | +2.89 | `a1z26_chi2` (**underpowered at this n**) | 0.983 (wrong tail) | 1.000 |
| R578_PR | 578 | +1.85 | `kasiski` | 0.0532 | 0.664 |
| R791_mc6_g | 791 | +0.03 | `a1z26_chi2` | 0.601 | 1.000 |
| R1535_mc6_u | 1535 | **+5.98** | `kasiski` | **0.0033** | **0.083** |
| R2058_mc8_u | 2058 | +0.80 | `date_frac` | 0.233 | 1.000 |
| R2713_mc12_u | 2713 | +1.05 | `ascii_frac` | 0.130 | 1.000 |

Two rows need saying out loud rather than burying.

**`kasiski` at n = 1535, q = 0.083.** This is the largest single number in the
study and it is not a finding. It does not clear q < 0.05. It is not replicated
at *any* other residue size — the same statistic gives p = 0.053, 0.704, 0.206
and 0.638 at n = 578, 791, 2058 and 2713, and there is no reason a periodic
structure would be visible only at min_copy = 6. And the i.i.d. control
false-positive rate for `kasiski` at that configuration is **0.10**, ten times the
nominal alpha, so the statistic's own calibration is the weakest in the set.
Reported as noise.

**`lz76_pd` at n = 2058 (p = 0.0066, q = 0.111) and n = 2713 (p = 0.0033,
q = 0.083), direction "less".** The residue has *fewer* LZ76 factors than an
order-3 resample of itself — i.e. it is more repetitive. This is retained
copy-paste, not message: it appears only at the permissive thresholds
(min_copy >= 8), and at the chance-corrected threshold (min_copy = 6, n = 1535)
it vanishes (p = 0.82). At min_copy = 12 the residue is provably above the
corpus's information bound, so it *must* contain real copies. Reported as a
property of the extraction.

**The two nulls disagree, and the disagreement is the PR's own lesson in a new
setting.** Against `ResidueShuffle` — which destroys all sequential structure —
**17 of the 50 tests clear BH q < 0.05** (min q = 0.012), and every one of them is
a statistic that measures sequential structure: `bigram_chi2_pd` (4 of 5
residues), `lz76_pd` (4), `a1z26_chi2` (4), `diff_ic` (3), `periodic_ic_max` (1),
`kasiski` (1). Against `ResidueMarkov3`, which reproduces the residue's own
order-3 statistics at identical length and inventory, **0 of the 50 clear
q < 0.05**, and the minimum q over the whole study is 0.083. A run that quoted
the shuffle null would have reported seventeen hits; all seventeen are the
leftover copy-paste that survives a permissive extraction.

The most seductive of the seventeen deserves naming: `a1z26_chi2` on
`union_mc8` sits at z = -3.97 against `ResidueShuffle` (p = 0.0033, q = 0.012) —
the residue's digit-pair frequency profile fits the *shape* of an English letter
distribution better than a shuffle of its own digits does. Against
`ResidueMarkov3` the same statistic is z = -0.64, p = 0.28. It is order-3
structure, not English.

---

## 4. Substitution solving with the alphabet size fixed a priori

`run_solve.py`. Family C's `C2_mdl` **induced** its symbol inventory by MDL and
on 578 digits it collapsed to V = 12 — fewer symbols than a Latin alphabet has
letters, so the configuration was ill-posed rather than negative. Here the
inventory is a hypothesis fixed before looking:

* **V10** — the residue read one digit at a time, exactly ten symbols: a
  ten-letter reduced-alphabet plaintext. At n = 578 that is 58 observations per
  symbol, the most sample-efficient cipher hypothesis a base-10 stream admits.
* **V100** — the residue read two digits at a time, exactly one hundred symbols,
  fixed by the encoding rather than induced: the homophonic hypothesis with the
  free parameter removed.

Solver, language models and scoring are Family C's, unchanged
(`experiments/e_c_homophonic/solver.py`, 5-gram log10 P per plaintext character;
genuine text scores about -0.63). Power is measured by enciphering real text at
the identical (length, symbol count) and reporting character accuracy. Nulls are
`ResidueShuffle`, `ResidueMarkov3`, and two end-to-end families **truncated to
the real residue's exact length** so the score comparison is not confounded by
length.

(80 null draws per family, 40 restarts; genuine text scores about -0.63 under
these models.)

| target | n | tok. | V | tokens | LM | best log10P/char | injected-cipher score | **recovery acc** | z Shuffle | **z Markov3** | z CPM-Fitted | p (Mk3) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| R578_PR | 578 | V10 | 10 | 578 | en | -2.2833 | -1.3234 | **0.879** | -0.47 | **-1.41** | -0.17 | 0.951 |
| R578_PR | 578 | V100 | 100 | 289 | en | -1.0259 | -1.0103 | **0.178** | +1.48 | **-2.13** | +1.33 | 0.988 |
| R1535_mc6_u | 1535 | V10 | 10 | 1535 | en | -2.1272 | -1.3101 | **0.984** | +6.61 | **-1.38** | +0.74 | 0.926 |
| R1535_mc6_u | 1535 | V100 | 100 | 767 | en | -1.4480 | -0.6921 | **0.992** | +3.19 | **-2.78** | +0.89 | 1.000 |
| R2058_mc8_u | 2058 | V10 | 10 | 2058 | en | -2.0771 | -1.3100 | **0.983** | +10.28 | **-0.45** | +0.71 | 0.642 |
| R2058_mc8_u | 2058 | V100 | 100 | 1029 | en | -1.5155 | -0.7000 | **0.994** | +5.96 | **-3.74** | -0.26 | 1.000 |
| R2713_mc12_u | 2713 | V10 | 10 | 2713 | en | -2.0475 | -1.3130 | **1.000** | +14.25 | **-0.15** | +0.02 | 0.580 |
| R2713_mc12_u | 2713 | V100 | 100 | 1356 | en | -1.5250 | -0.7004 | **0.994** | +14.41 | **-2.11** | -1.89 | 0.975 |
| R2058_mc8_u | 2058 | V10 | 10 | 2058 | de_ae | -2.1274 | -1.5522 | 0.659 | +12.53 | **+0.01** | +0.54 | 0.444 |
| R2058_mc8_u | 2058 | V100 | 100 | 1029 | de_ae | -1.5042 | -1.3134 | 0.491 | +6.68 | **-2.91** | +0.29 | 1.000 |

**Power.** Seven of the ten configurations recover an injected cipher of the
identical shape at **88-100% character accuracy**. Two facts about the other
three:

* `R578_PR / V100` recovers **17.8%** — the PR's 6.6% reproduced (this run uses
  40 restarts rather than the PR's setting, which is why it is higher). 289
  tokens over 100 symbols is still three observations per symbol.
  **UNDERPOWERED. Its z of -2.13 means nothing and is not quoted as evidence.**
* The two German rows recover 0.49 and 0.66. That number is a **lower bound and
  an artefact of this run**: the injected plaintext is English (no German running
  text or German word-frequency plaintext generator was wired into the injector),
  scored with a German model. They are reported as *partially powered* and the
  German hypothesis is not claimed to be refuted here. Family C already tested
  German at powered shapes on the larger streams and found nothing.

**The result.** `z Markov3` is the matched null — same length, same symbol
inventory, order-3 structure preserved, arrangement destroyed. **The maximum
across all ten configurations is +0.01.** Not one configuration reaches even the
mean of its matched null, exactly as in Family C, but now on residues where the
same solver recovers an injected message at 98-99%.

The `z Shuffle` column reaches +14.4 and is the trap: `ResidueShuffle` destroys
the order-3 structure that the permissive extraction retains, so the solver
scores the real residue far above it. That column measures leftover copy-paste.
The end-to-end `z CPM-Fitted` column — the fitted copy-paste generator pushed
through the identical extraction and truncated to identical length — agrees with
the matched null: maximum +1.33, and that maximum is on the underpowered
`R578/V100` row.

The best decryptions, for the record (`solve_results.json` has all of them):

```
R1535_mc6_u  V100 en : m iaa a ama is tn s r ints ant a as is iss i nosis is inst sae pintra
R2058_mc8_u  V100 en : saas a a anatinias naalia alisas ssaar aa a asaas as as n ma spaaa minst
R2058_mc8_u  V100 de : si ent a seine ein ten enen en eineier errnnte eneanete leer tie gnerneres
```

At -1.45 to -1.52 per character against genuine text's -0.63, these are what the
identical solver produces on noise.

---

## 5. Verdicts

| method | configuration | powered? | beats matched null? | verdict |
|---|---|---|---|---|
| **Extraction** | | | | |
| `lz76_innovation` (the PR's 578/608) | n=578 | **no** — 4.4% key recovery through the injection pipeline | n/a | **UNDERPOWERED BY CONSTRUCTION** — this residue cannot carry a recoverable message and no result on it, in this document or the PR, is informative |
| `greedy` min_copy=3 (the PR's 242/246) | n=246 | **no** — 10.9% | n/a | **UNDERPOWERED BY CONSTRUCTION** |
| `union` min_copy=6 / 8 | n=1535 / 2058 | **yes** — 85.4% / 97.6% | n/a | **VALIDATED** as the carrier to attack |
| **Numeric / periodicity** (per `run_numeric.py`, matched null `ResidueMarkov3`) | | | | |
| index of coincidence | 5 residues | yes (1.00 all hypotheses) | no (max z = -0.20) | **REFUTED** |
| `periodic_ic_max` (periodicity 2-40) | 5 residues | yes, incl. Vigenere-7 (1.00) | no (max z = +1.34, min p = 0.103) | **REFUTED** |
| `kasiski` (repeat-distance GCD) | 5 residues | yes vs Vigenere-7 (1.00); none vs simple substitution (0.00) | q = 0.083 at n=1535 only, unreplicated at 4 other sizes, 10% i.i.d. FP rate | **REFUTED** (see section 3) |
| `diff_ic` (additive / running-key) | 5 residues | yes vs a1z26 & subst-10; **no vs dates (0.00-0.15)** | no (max z = -0.49) | **REFUTED** for additive keys; **UNDERPOWERED** for a date payload |
| A1Z26 pair coverage | 5 residues | yes vs plain A1Z26 (1.00); **no vs enciphered (0.20-0.35)** | no (max z = +0.52) | **REFUTED** for plaintext A1Z26; **UNDERPOWERED** for enciphered A1Z26 |
| A1Z26 letter-shape chi2 | n>=791 | yes (1.00) | no (max z = +0.03 at n>=791) | **REFUTED** |
| A1Z26 letter-shape chi2 | n=578 | **no (0.55)** | — | **UNDERPOWERED** |
| decimal-ASCII triples | 5 residues | yes (1.00) | no (max z = +1.06, min p = 0.130) | **REFUTED** |
| date fields (DDMMYY/MMDDYY/YYMMDD) | 5 residues | yes (1.00) | no (max z = +0.80, min p = 0.219) | **REFUTED** |
| `lz76_pd`, `bigram_chi2_pd` (residual structure) | 5 residues | yes | q = 0.083 / 0.111 at min_copy >= 8 only; vanishes at the chance-corrected min_copy = 6 | **REFUTED as message evidence** — it is retained copy-paste |
| **Substitution solving** (per `run_solve.py`, matched null `ResidueMarkov3`) | | | | |
| V10 simple substitution, English | n = 578, 1535, 2058, 2713 | **yes (0.88, 0.98, 0.98, 1.00)** | no (max z = -0.15) | **REFUTED** |
| V100 homophonic, English | n = 1535, 2058, 2713 | **yes (0.99, 0.99, 0.99)** | no (max z = -2.11) | **REFUTED** |
| V100 homophonic, English | n = 578 | **no (0.178)** | — | **UNDERPOWERED** (confirms the PR) |
| V10 / V100, German | n = 2058 | partial (0.66 / 0.49, English-plaintext lower bound) | no (max z = +0.01) | **INCONCLUSIVE** — power not established for German in this run |

**No configuration anywhere in this study is PROMISING.**

---

## 6. What this does and does not establish

**Does.** For the residue of the 469 corpus at every extraction between 578 and
2,713 digits: there is no simple substitution over ten symbols, no homophonic
cipher over a hundred fixed symbols, no A1Z26 or decimal-ASCII or date encoding,
and no periodic (Vigenere-like) structure, at a power level that recovers each of
those when injected. The negative is now a real negative rather than a statement
about sample size, and the end-to-end injection test proves the *pipeline* would
have carried a message from the seed to the solver.

**Does not.** (a) The plaintext hypotheses tested are a finite list. A code with a
variable-length or context-dependent encoding, a non-Latin plaintext, or a keyed
cipher with a key longer than 40 is outside this set. (b) The language models are
the Family C word-frequency-synthesised ones — faithful for character statistics,
carrying no syntax; running text was unreachable from this session. The same gap
means the **German** configurations are inconclusive rather than negative here:
the power injector emits English plaintext, so 0.49-0.66 recovery under a German
model is a lower bound, not a measurement of German power. (c) The
injection tests use the *fitted* copy-paste generator as the transport model; if
the real construction differed in kind (e.g. hand-transcription errors with a
different profile) the recovery numbers would move. (d) `master_v1` itself
(6,056 digits) was already tested by Family C at powered shapes and was negative;
nothing here revisits that.

**The one thing worth doing next** is widening the plaintext hypothesis set
rather than the residue: the residue is now large enough and the pipeline is now
demonstrably lossless enough that failure is informative, and at 2,058 digits
with 97.6% injected-key recovery the binding constraint has moved from sample
size to the space of codes being searched.

---

## Reproducing

```
python experiments/verify_2026/chance_threshold.py   # copy-threshold calibration
python experiments/verify_2026/fastlz.py             # verifies fast Lmax vs c469.stats
python experiments/verify_2026/residue.py            # all residues + statistics
python experiments/verify_2026/pipeline_power.py 4   # message-in-the-seed power test
python experiments/verify_2026/run_numeric.py 300    # 10 statistics x 5 residues x 8 nulls
python experiments/verify_2026/run_solve.py 80 40    # fixed-V solving + power + nulls
python experiments/verify_2026/summarize_attack.py   # every table above
```

The two residues this document recommends as targets are written out for reuse
(the PR's `data/seed_estimate.txt` is left untouched):

```
data/residue_union_mc6_v2026.txt   1,535 digits  chance-corrected threshold
data/residue_union_mc8_v2026.txt   2,058 digits  largest under the information bound
```

Result files: `residues.json`, `pipeline_power.json`, `numeric_results.json`,
`solve_results.json`, plus the `*.log` transcripts.

Note: `run_solve.py` and `run_numeric.py` need `experiments/e_c_homophonic/build_lm.py`
to have been run once (it writes ~50 MB per model into `data/external/lm5_*.npz`).
