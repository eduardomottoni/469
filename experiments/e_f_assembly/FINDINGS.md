# Phase 1 — assembly

*Agent 1. Code: `assembler.py` (overlaps + path cover), `run_assembly.py`
(driver), `null_assembly.py` (null control). Outputs: `data/master_v1.txt`,
`data/master_provenance.json`, `pareto.json`.*

## What was replaced

`try_combine_books/try_combine_books.py` computed all pairwise overlaps with an
O(n^2 * L) Python loop and then decomposed a networkx overlap DAG greedily. Its
published best is *49 books merged into one 6624-digit contig plus a 63-digit
leftover*. The new pipeline keeps its `Book`/`Library` data model and replaces
everything else:

| step | before | now |
|---|---|---|
| pairwise max overlap | nested slice comparison | KMP prefix function, all 71x70 pairs in **0.11 s** |
| containment | `get_unique()`, O(n^2) substring | same result, recorded as provenance (parent + offset) |
| rotation | done by hand for one book pair | suffix automaton of `b+b`, every rotation of every book, cut point recorded |
| inexact overlap | none (a separate script used Biopython `globalms`, the wrong model) | anchored (12-mer seeds) semi-global overlap alignment, <=1 mismatch **or** <=1 indel, free end gaps |
| path cover | greedy | exact ILP (pulp/CBC, assignment + **lazy subtour elimination**) cross-checked against beam search (width 5000, bitmask states) and 200 randomised greedy + or-opt restarts |

MTZ subtour elimination was tried first and CBC could not close the gap in
30 minutes on 51 nodes; lazy cycle cuts close the same models in 0.1 s.

## The corpus

71 books (70 Hellgate + 1 Kharos), 11,400 digits. **20 books are literal
substrings of another book** and are collapsed away (their placement is kept in
the provenance file). 51 distinct sequences, 8,626 digits, remain.

Chance overlaps are not a worry at the threshold used: among 51x50 = 2,550
ordered pairs, the expected number of length-`L` suffix/prefix coincidences is
about `2550 x 10^-L`, i.e. 0.03 at L=5. Every overlap the assembler uses is
therefore real. The distribution of the 67 overlaps of length >=5 is bimodal:
20 short ones (5-19) and **47 long ones (26-279)**.

## Pareto front

`k` = number of contigs; `len` = total digits over all contigs; `edits` = single
mismatch/indel repairs invoked; `rot` = rotations invoked. All rows are proved
optimal by the ILP unless marked heuristic.

| config | k=min | Pareto (k, len, edits, rot) |
|---|---|---|
| exact, min overlap 5 | 22 | (22, 6270, 0, 0) (23, 6096) (**24, 6072**) (25, 6077) (26, 6082) |
| <=1 edit, min overlap 5 | 22 | (22, 6254, 1, 0) (23, 6080) (**24, 6056, 1, 0**) (25, 6061) (26, 6066) |
| <=1 edit, min overlap 20 | 28 | (28, 6094, 1, 0) (29, 6116) (30, 6142) (31, 6169) (32, 6203) |
| + rotations, min overlap 5 | 16 | (16, 5970, 0, 11) (17, 5754) (18, 5646) (19, 5624) (**20, 5621, 0, 8**) |
| exact, min overlap 1 (prior work's setting) | 9 | (9, 6043, 0, 0), heuristic |

The front is not monotone in `k` because the ILP is asked for *exactly* `n-k`
arcs: forcing two extra joins can displace better ones under the degree
constraints. The minimum-length point, not the minimum-contig point, is the one
to use.

## master_v1

`data/master_v1.txt` — **6,056 digits in 24 contigs**, one single-digit edit,
no rotations (min overlap 5, <=1 edit, the ILP optimum). Contig boundaries and
every book's `(start, length, edits, rot)` are in
`data/master_provenance.json`, together with a per-position coverage array and
the list of single-coverage positions. Contained books inherit their host's
placement and are listed with `contained_in`.

**Verified, not eyeballed:** `run_assembly.verify()` asserts that all 71 books
are recoverable from the master at their recorded offset within the declared
budget (<=1 edit). It passes with an empty exception list. The assertion is in
the driver, so the file cannot be written if it fails.

`data/master_permissive_v1.txt` (6,043 digits, 9 contigs) is the same assembly
with the prior work's `min_overlap=1`. It is **not** recommended: at that
threshold ~640 of the 782 non-zero overlaps are 1-4 digits long and are pure
coincidence, so the junctions are fiction. It is emitted only so the prior
result is comparable. Note that even so it saves just 13 digits over
`master_v1` — and both beat the prior published 6,624 digits for 49 of the
books, because the prior decomposition was greedy.

## Null control — does assembly mean anything?

The identical assembler (exact overlaps >=5, plus a rotation-mode pass) was run
on 100 surrogates from each of six families, `results/e_f_assembly.*.json`.
Empirical p with the +1 correction, so 0.0099 is the floor at N=100.

| statistic | real | Shuffle | Markov2 | Markov3 | BlockShuffle20 | CopyPasteMutate | **CopyPasteMutateFitted** |
|---|---|---|---|---|---|---|---|
| contigs (fewer = better) | **29** | 70.9 | 67.5 | 60.6 | 58.0 | 50.5 | **31.1 (p = 0.33)** |
| compression (1 - len/digits) | **0.444** | 0.000 | 0.002 | 0.006 | 0.009 | 0.085 | 0.260 (p = 0.0099) |
| longest overlap used | **279** | 0.4 | 6.6 | 11.7 | 14.3 | 116.7 | 166.9 (p = 0.0099) |
| rotations invoked | 6 | 0 | 0 | 0 | 0.01 | 11.4 | 14.5 (p = 1.00) |

**The honest reading, in the plan's own words: assembly proves nothing about
meaning.** Against the ABC-fitted copy-paste null (family E, fitted independently
on 9 statistics that include none of these), a surrogate corpus assembles into
31.1 contigs on average against the real corpus's 29 — p = 0.33, no effect. The
corpus assembles because it was pasted together, not because it says anything.
Assembly stays useful as **dedup**: it is how you avoid counting the same digits
five times, and that is all it is.

Two statistics do still separate the real corpus from the fitted null, and both
have mundane explanations rather than linguistic ones:

* **compression 0.444 vs 0.260** — driven by the 20 books that are *exact*
  substrings of other books, which the fitted model under-produces;
* **longest overlap 279 vs 167** — the single B64/B65 near-duplicate pair
  (`05-rearrange.txt`'s B42/B43), one hand edit, not a distribution.

**Rotations are worthless as evidence.** Allowing every book to be rotated adds
55 arcs (67 -> 122) and cuts the contig count from 22 to 16, which looks
impressive until you score it: fitted surrogates invoke *more* rotations than
the real corpus (14.5 vs 6, p = 1.00). Rotation is nearly unconstrained — with a
corpus this repetitive, almost any book can be spun to match almost any other.
`master_v1` therefore uses **no** rotations, and the rotation-mode assembly is
reported only as a documented negative.

The one genuine rotation-like relation in the corpus is not a rotation at all.
B64 = X + Y + Z and B65 = Y + X + Z with |X| = 52, |Y| = 141, |Z| = 79: a
**block transposition inside the prefix**, not a rotation of the whole book
(checked directly — no pair of books satisfies `a in b+b`). The prior author's
hand analysis of B42/B43 is exactly right; the plan's description of it as a
whole-book rotation is not.

## For the other agents

* `data/master_v1.txt` — **6,056 digits**, the deduplicated stream. Contig
  boundaries in `data/master_provenance.json` (`contig_start_offsets`); do not
  read across them.
* `data/master_provenance.json` — every book's placement, per-position coverage,
  and **3,858 of the 6,056 positions are single-coverage** (no second book
  confirms them). A pattern that lives only on single-coverage positions is a
  pattern in one book, not in the corpus.
* Run everything on the master **and** on the raw books, per the plan. Anything
  that appears only on the master is an artifact of my junction choices.
* `data/master_permissive_v1.txt` exists for comparison with prior work only.
