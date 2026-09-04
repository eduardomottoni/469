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

