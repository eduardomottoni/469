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
