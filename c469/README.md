# c469 — a calibrated attack harness for 469

Twenty years of work on 469 has been pattern-spotting without a null model.
This package exists so that every claim about the corpus is scored against
surrogate data and reported with an empirical p-value.

    pip install numpy scipy networkx tqdm numba pulp scikit-learn
    python -m c469.selftest        # must PASS before any result is trusted

## Modules

- `corpus.py`  — loaders for `books.json`, the Kharos set, the prior author's
  contigs, `alignment_data.json`, and a parser for the hand-drawn
  `04-align.txt` / `05-rearrange.txt` canvases.
- `stats.py`   — the shared measurement vocabulary. **Every number reported by
  any experiment must come from here.** Statistics take a *list of books* so
  that n-grams never straddle a book boundary (that artifact is what hides the
  corpus's single forbidden bigram, `07`).
- `cribs.py`   — every known 469 string outside the books, with an `in_books`
  flag. See the dialect split below.
- `surrogate.py` — the null models, including `CopyPasteMutate`, the generative
  form of the "there is no plaintext" hypothesis.
- `harness.py` — `Experiment` (pre-registration), empirical p with the +1
  correction, Benjamini–Hochberg q, and the rule that a finding must clear
  *every* family in `DEFAULT_FAMILIES`.

## Two facts this package encodes

**The corpus is copy-paste, not a Markov process.** LZ76 factor counts:

| stream | factors |
|---|---|
| real corpus (11,263 digits) | **608** |
| order-5 Markov surrogate | ~1,080 |
| order-3 Markov surrogate | ~1,590 |
| shuffled digits | ~3,370 |

**The cribs split into two disjoint dialects.** Every 469 string with a claimed
English meaning (Evil Eye `653768764`, Elder Bonelord, poll answer C, the
librarian's own name `486486`) occurs **zero** times in the library books; every
string that does occur in the books is an untranslated quotation. `selftest`
asserts this. No crib is therefore ground truth for the library code.
