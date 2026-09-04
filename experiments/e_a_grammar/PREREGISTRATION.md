# Family A — pre-registration

Written **before** any token induction was run. Timestamped by the git commit that
introduces this file; no result in this directory predates it.

## Hypothesis under test

Finding 3 of the plan: the 2011 Facebook number pairs give r/l = 0.634 +/- 0.019
(CV 3% over 18 pairs). Inverted, **1.577 digits per plaintext unit**. If 469 is a
variable-length code over a ~26-32 symbol plaintext alphabet, then an
information-theoretically sane codebook at that rate must give single-digit
codewords to roughly 8-10 high-frequency plaintext symbols, with the rest at
length 2 (and a tail at 3).

## Pre-registered prediction (Family A, primary)

An MDL-optimal induced token set over the 469 digit stream, run on the
deduplicated core and on the contigs, will have:

- **P1.** corpus-weighted mean token length in **[1.5, 1.7]**
- **P2.** **8-10** tokens of length 1 in the induced vocabulary
- **P3.** as a supporting descriptor, >=80% of token *occurrences* at length 1 or 2

## Pass / fail criterion, fixed in advance

- **PASS** requires P1 and P2 to hold simultaneously on at least one of
  {dedup core, contigs, master_v1} for the MDL-optimal inducer (BPE/Re-Pair/
  Sequitur/LZ78 are reported but are not the arbiter — they have a vocabulary-size
  knob that trivially moves mean length, so they cannot confirm or refute).
- **FAIL** otherwise. Specifically: mean length outside [1.5,1.7], or a
  length-1 count outside 8-10, is a failure of the prediction, and must be
  reported as such even if the number is "close".
- Because BPE's V is a free knob, we additionally report, for each V, whether the
  MDL objective *prefers* that V. Only the MDL-argmin vocabulary is scored
  against P1/P2.

## Secondary, also pre-registered

- **Zipf slope s** and **Heaps' beta** of the induced token stream are compared
  **only** to the distribution of the same statistic computed by running the
  identical inducer on surrogates. No comparison to textbook values ("language is
  ~1.0") is admissible: BPE manufactures Zipf-like curves on i.i.d. noise.
- **MDL gain** (bits to encode the stream, model + data) is compared only to
  surrogates **matched on LZ76 factor count** to the real stream (measured
  per-stream, not assumed). If we cannot tune CopyPasteMutate to match the LZ76
  factor count within +/-5%, we say so and report the comparison as uninformative
  rather than quoting an unmatched p.

## Kill criterion

No length-1/2 concentration **and** no MDL gain over LZ-matched surrogates
=> Family A is dead, reported plainly.

## Streams

- `dedup_core(load_books())` — 22 books, 3901 digits (primary)
- `load_contigs()` — 6687 digits
- `data/master_v1.txt` if agent 1 produces it
- Never the raw 70-book corpus alone: naive BPE there reaches 3832 tokens / 127
  vocab, which is copy-paste redundancy, not a lexicon.
