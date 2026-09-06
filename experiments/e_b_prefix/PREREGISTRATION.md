# Family B pre-registration

Written **before** any code in this directory was executed. Commit hash of this
file's first commit is the timestamp of record.

## B1 — exhaustive prefix-code enumeration

Statistic: `n_books_parsed` — the number of the 70 Hellgate books that a given
structure parses to the end with **zero** dangling remainder (the parse is
forced and unique, so this is well defined).

Search space (enumerated by structure, codeword length capped at 3):
`S1` = set of single-digit codewords; every digit not in `S1` is a length-1
prefix; for each such prefix `p`, `T_p subset {0..9}` is the set of digits `d`
for which `pd` is again a *prefix* (expanded to ten length-3 codewords) rather
than a codeword. `|S1|` and `sum |T_p|` are the only free structural quantities.

Pre-registered expectation: a structure whose codewords have mean length `L`
lands on a book's final boundary with probability roughly `1/L ~ 0.6`; 70
independent books therefore give `~0.6^70 = 1e-16` per structure by chance.
**I predict that zero structures parse all 70 books**, and that the interesting
statistic is therefore `max n_books_parsed` over the search, scored against
surrogates.

## B2 — the `07` gap

Three candidate explanations, tested not assumed:
(i) `0` is a prefix and `07...` is an unassigned codeword;
(ii) `0` is a delimiter/escape;
(iii) `07` is a forbidden *plaintext* bigram.
Prediction: (i) is the only one that the enumeration can distinguish, and
(i) is testable directly — the near-forbidden `3 -> {2,3,9}` gaps must then be
explained by the *same* mechanism, i.e. `3` must also be a prefix. If a
structure needs `0` a prefix but `3` a codeword the explanation is incoherent.
Crib constraint used: `1` = "Tibia" => `1 in S1`. No NPC string is used.

## B3 — the 1.577 prediction (central gate)

Independent evidence (2011 Facebook pairs, r/l = 0.634 +/- 0.019) predicts
**1.577 digits per plaintext unit**.

Pre-registered pass criteria, fixed now:
* (a) surviving family-B codebooks have corpus-weighted mean codeword length in
  **[1.50, 1.70]** with **8-10** single-digit codewords;
* (b) BPE (V in 50..1000) and MDL/Viterbi dictionary segmentation on the
  deduplicated core (22 books / 3901 digits) and on the contigs induce a mean
  token length in **[1.50, 1.70]**.
A result outside those windows is a **failed** prediction and will be reported
as such. A mean token length that varies monotonically with the vocabulary
budget V (so that 1.577 can be hit by tuning V) counts as **no evidence**
either way, and I commit in advance to reporting the whole V-curve rather than
the V that happens to land on 1.577.

## B4 — nulls

Identical search over >=200 surrogates from each of `Shuffle`, `Markov2`,
`Markov3`, `BlockShuffle20`, `CopyPasteMutate`, plus digits of pi.
If the search finds equally good codebooks on pi and on CopyPasteMutate, the
conclusion recorded will be **"the method has no power"**.

Empirical two-sided p with the +1 correction; Benjamini-Hochberg q over all
codebooks tested. No raw best-of-many p will be reported.
