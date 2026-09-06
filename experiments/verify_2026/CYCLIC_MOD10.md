# The cyclic mod-10 letter hypothesis — REFUTED

Pre-registered and run 2026-09-06. Code: `cyclic_mod10.py`.

## The hypothesis

Each digit stands for **any letter whose alphabet index is congruent to it
mod 10** — the alphabet cycles, so `0` can be `A`, `K` or `U`.

| digit | letters | | digit | letters |
|---|---|---|---|---|
| 0 | A K U | | 5 | F P Z |
| 1 | B L V | | 6 | G Q |
| 2 | C M W | | 7 | H R |
| 3 | D N X | | 8 | I S |
| 4 | E O Y | | 9 | J T |

This is **not** what `SEED_ATTACK.md` refuted. The `a1z26_*` statistics there
test whether digit *groups* fall in the 1–26 range. This is a one-digit-to-
many-letters lattice, and it had never been tested.

Its useful property: **there is no key to search.** The map is fixed by the
hypothesis, so the only question is whether the best-scoring path through the
lattice is language. That makes it decidable by Viterbi rather than by search.

## Method

Character 5-gram model with stupid backoff, built from 250,000 letters of
English. Viterbi over the candidate lattice, beam 400. Statistic: best-path
mean log₂ P(char | context), in bits/char — higher is more language-like.

**Pre-registered criterion:** supported only if real 469 beats Markov-3
surrogates decoded identically, *and* the decoder demonstrably recovers
injected English at the same length.

## The decoder is powered

On 800 characters of **held-out** English, encoded with the scheme and decoded:

- **83.4% character recovery**, score **−2.548 bits/char**

```
truth  : MANCRUDERFOLDINGAOUSSSSCORPUSPROVENANCESTATEDPLAINLYGENERALWEBEGRESSIS
decoded: CANCHANORFOLDINGKOKSISSCORPUSPROVEDANCESTATEXPLAINLEGENERALMELEGRYISSI
```

Plainly recognisable. If 469 were mod-10 encoded text, this would find it.

## Result: nothing, at any offset

| target | n | real | Markov-3 null | z | p |
|---|---|---|---|---|---|
| contig 13 | 791 | −4.6623 | −4.6577 ± 0.0709 | **−0.07** | 0.42 |
| residue mc8 | 800 | −4.6395 | −4.6959 ± 0.0800 | **+0.70** | 0.23 |
| master head | 800 | −4.6058 | −4.6723 ± 0.0847 | **+0.78** | 0.29 |

Real English decodes at **−2.55**; 469 decodes at **−4.6**, indistinguishable
from a Markov chain of its own digits.

Sweeping all ten alphabet offsets (A=0, A=1, …) on contig 13:

- maximum z across all offsets: **+0.64**
- Benjamini–Hochberg over 10 offsets: **minimum q = 0.741**

## Why the output still looks tempting

The decode contains English-shaped fragments — `WRITED`, `PLUS`, `VITALITYOF`,
`TWISTFCL` — and this is exactly the trap. The language model is *required* to
emit plausible letter sequences whatever it is fed. **The surrogates produce
equally English-looking output at equal scores.** Fragment-spotting in the
decode is not evidence; the score against the matched null is.

(`TWISTFCL` appearing in both contig 13 and the residue is the corpus's
copy-paste redundancy showing through, not a repeated word.)

## Verdict

**REFUTED**, at power that recovers 83% of injected plaintext. The cyclic
mod-10 reading is not the code — for any of its ten alphabet alignments.
