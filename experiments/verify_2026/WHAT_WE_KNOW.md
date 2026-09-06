# 469 — what is actually established

Consolidated 2026-09-05. Covers results from the `c469` branch and the
verification round that followed it. Every entry is either **[R]** reinforced
(previously believed, now measured or independently confirmed) or **[N]** new.

This document lists only claims that are backed by a number. Where a claim was
scored against a null model, the null is named — because in this corpus the
choice of null is the difference between a discovery and an artefact (see §6).

---

## 0. The rule that governs everything below

**A statistic without a matched null is not evidence.** This corpus produces
apparently significant results on demand. Seven separate ~4σ findings have now
been generated and killed during this work, each by replacing a weak null
(shuffle, uniform, textbook constant) with one that matches the corpus's length
*and* its inventory *and* its local structure.

Any future result on 469 that does not report the null it was scored against
should be assumed to be one of these.

---

## 1. The corpus is verified — the foundation is sound  **[N]**

`books.json` is **byte-identical** to primary sources. 70 books, 11,263 digits,
zero mismatching positions.

| source | result |
|---|---|
| tibia.fandom.com, 71 book pages (MediaWiki API, raw wikitext) | 70/70 exact |
| independent in-game/server-file scrape | 70/70 exact |
| `data/external/elkolorado_bacca_books.txt` | 70/70 exact |
| `01-books.md` | 70/70 exact |

This is **not OCR**. Each book's digits sit in the `text =` field of the wiki's
`{{Infobox Book}}` template and arrive as machine-readable wikitext, so no
transcription step was introduced by the verification itself.

**The 70-vs-71 discrepancy is resolved.** Pages `8550649967 (Book)` and
`85506499670 (Book)` are shelved separately with different prev/next links but
carry character-for-character identical text (145 digits). `books.json` keeps
one copy. The difference is de-duplication, not a missing book. For n-gram work
70 is correct — duplicating a book inflates every frequency.

*Residual caveat:* this proves faithfulness to the wiki and to a server scrape,
not to CipSoft's original authoring. An error made once, at first transcription,
would be invisible to all four sources.

---

## 2. The central result: the corpus is 85% duplication  **[N]**

This is the single most mystery-narrowing fact available.

| stage | digits | |
|---|---|---|
| raw corpus (70 books) | **11,263** | |
| after cross-book assembly (`master_v1.txt`) | **6,056** | −46% |
| after removing internal repeats as well | **1,684** | **−85% of original** |

The assembled master was never irreducible: **125 blocks of ≥12 digits reappear
later inside it**, making it 72% self-redundant. Only 1,684 digits of the entire
Hellgate Library cannot be derived from material appearing earlier in the same
reconstruction.

**And 1,684 is still an overestimate.** A 176-digit run occurs at master
positions 1472 and 5798 — that is **contig 10 and contig 23 sharing 176 digits,
64% of contig 23's entire length**. They should have been merged and were not,
so the published "ILP-optimal, 24 contigs" assembly has at least one missed
join.

At the corpus's own coding rate (~1.3 digits/character), 1,684 digits is roughly
**1,300 characters — about one page of text.** That is the size of the object
twenty years of work has been circling.

---

## 3. Copy-paste is proven by direct measurement, not inferred  **[R]**

Previously argued from compression. Now shown directly, with nulls.

**Held-out cost per digit** (leave-one-book-out):

| model | bits/digit |
|---|---|
| uniform random digits | 3.32 |
| Markov-0 | 3.266 |
| best Markov (order 5) | 0.986 |
| context tree, depth 16 | 0.899 |
| **relative-LZ copy code** | **0.405** |

No sequential model of any order comes within a factor of two. The copy code
*loses* on shuffled or Markov material, so this is diagnostic rather than a
trick that always wins.

**Longest exact run shared between two different books:**

| | digits |
|---|---|
| IID digits | 8 |
| shuffled corpus | 8 |
| Markov-3 | 26 (max 30 over 20 runs) |
| **real corpus** | **279** |

At the corpus's own digit entropy a specific 279-digit run has chance
probability ≈ **10⁻²⁷⁴**. Randomness is excluded by a margin with no useful
name. **378 of 2,415 book pairs** (16%) share an exact run of ≥40 digits.

**Books chain end-to-start** — a sequence stops at one book's end and resumes at
another's beginning:

| | median join | max | books joining ≥40 digits |
|---|---|---|---|
| Markov-3 null | 2 | 9 | **0** |
| **real corpus** | **52** | **279** | **38 of 70** |

**Assembly shape:** 202 copy operations total; median 2 blocks per book; median
block length 36 digits; 98.3% of all digits covered by copied material;
**52 of 70 books contain no new digits at all**; only 171 digits across the
whole corpus are not copyable from elsewhere.

**Hand editing is visible.** Book 64 is `X+Y+Z`, book 65 is `Y+X+Z` with
|X| = 52 — a block transposition. It is the one statistic the fitted stochastic
generator could **not** reproduce (z = +2.0). A script does not do that once and
never again.

---

## 4. The seed: why 578 was the wrong object  **[N]**

The branch attacked `data/seed_estimate.txt` (578 digits). That file is built by
LZ76-parsing the master and taking **the last digit of each factor**. Its length
is *defined* to equal the factor count. It is a parsing artefact, and it is a
**scatter** — one digit harvested per block from across the document, with
adjacency destroyed.

Five mutually inconsistent estimates of the same quantity exist:

| estimate | digits |
|---|---|
| LZ77 literals (seed_B) | 242 |
| LZ76 innovation (seed_A) — *the file that was attacked* | 578 |
| second-pass internal dedup | 1,684 |
| information bound (relative-LZ bits ÷ log₂10) | ~2,350 |
| ABC posterior median | 2,602 (90% CI **986–5,931**) |
| ABC best-fit point | 7,407 |

The ABC best-fit lies **outside its own 90% credible interval**, and the
posterior [986, 5931] barely narrows the prior [400, 8000]. Seed length is
weakly identified by the data.

**The 578 file was underpowered by construction, now measured:**

| residue | digits | injected-key recovery |
|---|---|---|
| `lz76_innovation` (the attacked file) | 578 | **4.4%** |
| `greedy` min_copy=3 | 242 | 10.9% |
| **`union` min_copy=8** | **2,058** | **97.6%** |

**The extraction threshold was wrong.** `extract_seed.py` charges every ≥3-digit
match to the copy model, but an i.i.d. digit stream of this length already
contains a ≥3 match at **91% of positions** by chance (≥6: 0.6%). The
chance-corrected threshold is 6 (→1,535 digits); 8 gives 2,058, the largest
still consistent with the ~2,350 information bound.

Two independent routes — second-pass dedup (1,684) and chance-corrected
extraction (1,535–2,058) — converge on the same object.

---

## 5. The search is now powered, and it is negative  **[N]**

At 97.6% measured power on a 2,058-digit residue, against matched nulls
(`ResidueMarkov3`: exact length **and** inventory):

- 50 pre-registered numeric/periodicity tests: **zero** clear BH q < 0.05
  (min q = 0.083, unreplicated at four other sizes).
- 10 solver configurations: **maximum z = +0.01**. Not one reaches even the
  mean of its noise distribution.

**Refuted** (now powered, previously "underpowered"): V10 substitution, V100
homophonic at n ≥ 1535, A1Z26, decimal ASCII, dates, index of coincidence,
periodicity/Kasiski, additive-key.

**Still underpowered, not refuted:** V100 at n = 578 (but that residue is now
known to be the wrong object), German-language solving (the power injector
emits English, so the 0.49–0.66 recovery is a lower bound, not a measurement).

Additional negatives from this round:

- **Not Benford** (χ² = 569). Rules out a harvested list of real-world
  quantities — IDs, populations, prices, measurements.
- **Not dates.** Years 1990–2012 appear 3.5× a naive expectation, but random
  4-grams in this corpus already run 1.71× above it. Decisively: **1997
  (Tibia's launch) appears once, rank 927 of 1,097 four-grams; 2001 (the books'
  year) and 2011 appear zero times.** The "enriched" years are arbitrary —
  `1991` at rank 42 is just an ordinary frequent 4-gram, the maximum being 128.
- **Not human random typing.** The two documented signatures both fail. Repeat
  avoidance looks textbook against shuffle (11 triples vs 78 expected,
  z = −7.08) but vanishes at Markov-2 (null 10.9 ± 3.6, z = **+0.02**). Counting
  bias is asymmetric — step +1 is enriched (z = +6.39) while step −1 sits exactly
  at chance (z = −0.08), with no run structure either way; a human drifting into
  counting produces both directions. And `7` is *under*-represented where human
  RNG reliably over-picks it.
- **`1`-as-delimiter refuted.** Pre-registered: if `1` marks codeword starts it
  should be the best MDL delimiter. Ranking came out
  `5 < 4 < 8 < 3 < 6 < 9 < 2 < 7 < 0 < 1` — **`1` is the worst of ten**, both raw
  and frequency-normalised.
- **5-eye / base-5 refuted** in every form. Period-5 framing is
  *anti*-significant (χ² 25.4 vs null ~36, p = 0.92).

---

## 6. The false-positive machine — the most transferable finding  **[N]**

Seven ~4σ results have been produced and killed. The pattern is identical every
time: a null that fails to control something the statistic depends on.

| apparent finding | against weak null | against matched null |
|---|---|---|
| Zipf slope 1.304 "language-like" | vs textbook ~1.0 | z = **+1.2** vs LZ-matched |
| homophonic solve | **+6.26σ** vs `Markov3_digits` | **max −0.13** vs `Markov3_symbols` |
| modulus-8 structure | +3.6 to +4.7σ, six families at p floor | dies on dedup (z = −0.25); BH q = 0.058 |
| `43151` occurs 14× | expectation ~0.1 under uniform | rank 209 of 1,499 5-grams |
| digit-run suppression | z = **−7.08** vs shuffle | z = **+0.02** vs Markov-2 |
| handwriting-confusion enrichment | z = **+3.44**, p = 0.0007 | z = **+0.64** with post-hoc pairs removed |
| residue structure | **17 of 50** tests q < 0.05 vs shuffle | **0 of 50** vs `ResidueMarkov3` |

Two of these were generated during this verification round, one by selecting the
hypothesis after seeing the ranking. The corpus's copy-paste redundancy means
*any* statistic sensitive to repetition will clear a shuffle null.

**Practical rule:** on 469, the null must match length, symbol inventory, and
local (≥2) context. Shuffle and uniform nulls are useless here.

---

## 7. External constraints — the mystery narrows from outside too  **[N]**

Not mathematical, but they bound what the mathematics can be looking for.

**There is no in-game key, and this is now measured rather than assumed.**
Against Tibia's *entire* shipped text — 2,135 books and 1,148 NPC keyword trees:

- Fiehonja Library ships the Deepling (Jekhr) cipher books **plus** the
  alphabet, 116 glossary entries, **and** six worked-solution books, all on the
  same shelves. Rookgaard's `Ork_Porak` does the same for a numeric orc code.
- **Hellgate Library contains 71 books and all 71 are 469.** No prose, no
  glossary, no companion.
- Across all 1,148 NPCs and 2,135 books there are exactly **three** references
  to the bonelord language, and every one is an explicit refusal.
- No Tibian conlang has ever been solved cold. Every solved text had a shipped
  key or a real-world standard encoding.

**Developer statements, all verified from primary sources.** Knightmare (2010),
Chayenne (2009) and Lionet (2022) were each asked directly; all three answered
with a joke. None used the cheaper option of "we're not telling." Knightmare's
punchline is itself a non-recoverability claim — "we have no means to tell if
the beholder actually wrote down what we dictated him" — and in the same
interview he warns "Sometimes players see allusions where there weren't any
intended." Lionet's stated criterion for a learnable conlang (large vocabulary,
characters actively using it) excludes 469 by the designer's own definition.

**The two-dialect split is real: p ≈ 5.3 × 10⁻⁶.** Every 469 string with a
claimed English meaning occurs **zero** times in the library books; every string
that does occur there is an untranslated quotation. The corpus is repeat-heavy,
so the leave-one-out probability that a genuine length-L book window recurs is
0.75–0.96 — against which all four translated strings being absent gives
P = 1.1 × 10⁻⁵. The obvious length confound runs *against* the result: the absent
set is the shorter one (mean 6.5 vs 21.0 digits). **No crib is ground truth for
the library code.**

---

## 8. Corrections to standing repo claims  **[N]**

- **The Honeminas book does not belong in the 469 evidence base.** Honeminas is
  a **Warlock of Demona**, not a bonelord; the book's author is `Mathemicus`;
  its own glossary says it is about teleport gates. The formula uses a
  **parenthesis** — `(4,3,1,5,3).(3,4,7,8,4)` — which is a Mathematica *syntax
  error* (no comma operator inside grouping parentheses), alongside a declared-
  but-unused pattern variable and non-terminating self-recursion. Its true
  digits `43153` and `34784` occur **0 times** in the corpus; the README's
  typos `43151`/`34783` occur 14 and 5 times, which is where "honeminas formula
  looks crucial" came from.
- **Known-plaintext budget shrinks from 26 digits to 7.** The Elder Bonelord /
  Evil Eye "translations" come from a flat four-entry random `voices` table
  (`interval = 5000, chance = 10`), byte-identical across four independent OT
  projects — the lines are sampled independently and cannot gloss each other.
  Only `486486` and `1` remain keyword-bound.
- **The 2011 Facebook pairs table has 31 rows, not 28**, after a −18.2° deskew
  makes the column pairing measured rather than assumed. Seven cells that
  `cribs.py` treats as observations are **not legible in the photograph** —
  including the `(737, 469)` pair in `FB_PAIRS_CERTAIN`, where only `_69`
  survives and the leading `4` is behind the clay figure. Family D's 18 "certain"
  pairs are really 16. A 1536×2048 original exists (4× the previously used copy)
  and is now in the repo; 2048px was Facebook's 2011 ceiling.
- **Poll answer C is not known-plaintext.** Answers A and B decode via the
  in-game Jekhr alphabet to *different* sentences; they are three separate joke
  answers, not one sentence in three encodings.
- **The medieval-comic premise is disconfirmed**, not merely unfound.
  TibiaWiki's Allusions page has a dedicated Comic Books section and contains
  zero hits for Prince Valiant, Eisenherz, Thorgal, Mosaik, Warlord or
  Serpentine. "Tibia's other mysteries had real external referents, so 469 does
  too" is folklore.

---

## 9. What genuinely remains open

1. **~1,700 digits of irreducible content**, sequence intact, that no tested
   code family explains. The binding constraint has moved from sample size to
   **the space of codes searched**.
2. **The largest coherent object is contig 13 — 791 digits assembled from 19
   books.** Both halves of Chayenne's 2009 interview answer sit inside it, at
   positions 479 and 666, 151 digits apart. A designer asked to speak beholder
   reached into this one region. That localises the quotation; it does not
   decode it.
3. **Accident vs. design cannot be distinguished.** The branch asserts the
   corpus is an artefact; the repo owner's own later article argues a deliberate
   decoy. Both predict exactly what is observed. The statistics cannot separate
   them and should say so.
4. **80 single-digit variant sites** between otherwise-identical 40-digit
   windows, present in the shipped game data (not player transcription).
   Catalogued but unexplained. A pre-registered handwriting-confusion test on
   these is cheap and has not been run blind.
5. **63.7% of the master rests on a single witness** (median coverage depth 1).
   Most of the reconstruction has no corroboration, so errors there are
   undetectable.
6. **Nobody at CipSoft has ever said it means nothing, either.** The honest
   verdict is *never claimed meaningful by anyone who would know* — which is not
   the same as denied.

---

## 10. One-paragraph summary

469 is 11,263 digits that reduce to roughly **1,700** — about one page. The
reduction is not statistical inference but direct measurement: 202 copy
operations, 52 of 70 books containing nothing new, a 279-digit run shared
verbatim between two books where chance allows 8, and 38 books whose closing
digits are another book's opening digits where a matched null allows none. That
page of residue is now searched at 97.6% power against matched nulls, and every
standard code family — substitution, homophonic, A1Z26, ASCII, dates, Benford
sources, periodicity, human typing — is refuted rather than merely untested. No
in-game key exists where every comparable Tibian cipher shipped one, and three
developers asked directly across thirteen years each answered with a joke.
Nothing proves the page is empty. But the target is now small, verified, and
bounded, and the remaining uncertainty is about **which code was used**, not
about how much material there is to work with.
