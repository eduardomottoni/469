# Game content and structure as the key

Agent session, branch `claude/open-pr-next-steps-5a04cf`, 2026-09-04.
Code in this directory; scored results in `results/G*.json` and
`experiments/verify_2026/out/`; new source data and its provenance in
`data/external/` and `data/external/provenance/SOURCES_2026-09-04_gamecontent.md`.

The open PR refuted five *statistical* hypothesis families and concluded the
corpus is a copy-paste artefact. Its own framing was that every Tibian text
ever decoded had a published in-game key. This is the search for that key, and
for the structural (non-statistical) readings the PR skipped.

**Verdict in one line: there is no key, and the absence is now a measured
result rather than a failure to find one.** The two-dialect split survives a
proper null at p ≈ 5e-6. Every form of the 5-eye premise is REJECTED. The 2020
poll correction is confirmed by decoding answer B from the in-game Deepling key.

### Files

| script | what it does | output |
|---|---|---|
| `g0_extract.py` | census of every digit run in 1,148 NPC trees, 2,135 books, 8 `.lua` scripts | `out/g0_all_hits.json` |
| `g1_dialect.py` | leave-one-out `p_hit(L)` and the two-dialect containment test | `out/g1_dialect.json` |
| `g1b_composition.py` | digit composition of the NPC set vs a window-matched null | `out/g1b_composition.json` |
| `g2_fiveeye.py` | H1/H2/H3 five-eye tests + the 2..12 control scan | `out/g2_summary.json`, `results/G2_*.json` |
| `g3_poll.py` | decodes poll answers A and B from shipped game text | `out/g3_poll.json` |
| `g4_corpus_provenance.py` | `books.json` vs the independent in-game scrape | stdout |
| `g5_zero_role.py` | the librarian's `0` taboo as delimiter / edge marker | `out/g5_zero_role.json`, `results/G5_*.json` |
| `g6_mod8_followup.py` | hardening the one cell that fired in G2's control scan | `out/g6_mod8.json`, `results/G6_*.json` |

---

## 0. New primary data brought into the repo

The earlier provenance session could reach only GitHub. This session could too
— but that turned out to be enough, because the whole of Tibia's shipped book
and NPC text is on GitHub.

| file | rows | what it is |
|---|---|---|
| `data/external/book_database.json` | 2,135 books | every in-game book, with text, author and library tag |
| `data/external/npc_transcripts.json` | 1,148 NPCs | every NPC keyword tree, `prompt -> answer` |
| `data/external/npc_metadata.json` | — | NPC locations |

Source `s2ward/tibia`; see the provenance file for URLs, sizes and caveats.
This is the first time the 469 question has been posed against the *entire*
shipped corpus rather than against a hand-picked set of wiki pages.

### 0.1 `books.json` is verified against an independent transcription

`g4_corpus_provenance.py`:

```
books.json:                        70 books, 11,263 digits
book_database Hellgate Library:    71 books, 11,408 digits
exact-match books: 70   only in books.json: 0   only in book_database: 0
duplicate texts inside book_database: 1  -> ['8550649967', '85506499670'] (145 digits)
```

Every one of the 70 books matches digit-for-digit. The 71st shelf entry is a
genuine in-game duplicate: two physical books carrying the same 145-digit text.
The corpus this repo has been analysing for years is **not** a transcription
artefact. (Caveat: `s2ward/tibia` shares an author with this repo, so this is an
independent *pass*, not an independent *party*.)

---

## 1. The cribs: the two-dialect split is real, and it is not a length artefact

`c469/cribs.py` records that the 469 strings with a claimed English meaning
occur zero times in the library, while every string that does occur is an
untranslated quotation. The obvious objection is length — short strings occur
by chance, long ones do not. **The objection runs backwards.**

`g1_dialect.py` measures `p_hit(L)`, the leave-one-out probability that a
length-`L` window of *genuine 469 book text* also occurs in some other book.
This corpus is famously repeat-heavy, so `p_hit` is high:

| L | windows | hits | p_hit |
|---|---|---|---|
| 5 | 10,983 | 10,515 | 0.9574 |
| 6 | 10,913 | 10,311 | 0.9448 |
| 9 | 10,703 | 9,799 | 0.9155 |
| 13 | 10,423 | 9,205 | 0.8831 |
| 15 | 10,283 | 8,947 | 0.8701 |
| 20 | 9,933 | 8,343 | 0.8399 |
| 36 | 8,813 | 6,646 | 0.7541 |

Against that background:

| string | L | p_hit | observed occurrences | source |
|---|---|---|---|---|
| `653768764` | 9 | 0.9155 | **0** | Evil Eye / Elder Bonelord — *translated* |
| `659978` | 6 | 0.9448 | **0** | Elder Bonelord — *translated* |
| `54764` | 5 | 0.9574 | **0** | Elder Bonelord — *translated* |
| `486486` | 6 | 0.9448 | **0** | librarian's own name — *translated* |
| `485611800364197` | 15 | 0.8701 | 1 | librarian voice — untranslated |
| `78572611857643646724` | 20 | 0.8399 | 6 | librarian voice — untranslated |
| `114514519485611451908304576512282177` | 36 | 0.7541 | 11 | Chayenne 2009 — untranslated |
| `6612527570584` | 13 | 0.8831 | 9 | Chayenne 2009 — untranslated |

* P(all four translated strings absent, given they behave like 469 book text)
  = **1.1e-5**
* P(all four quotation strings present) = 0.49
* P(the exact observed 4-absent / 4-present split) = **5.3e-6**

Mean length of the *absent* set is 6.5 digits; of the *present* set, 21.0. The
short strings are the ones that are missing. Length cannot explain this; it
makes it worse.

**The split holds.** The right reading is not "two encodings" but the simpler
one: the four translated strings were written *for their scene* and were never
drawn from, or added to, the library corpus, whereas the two "quotations"
(librarian voice lines, Chayenne's interview reply) are literally copied out of
existing book text. Chayenne was quoting the shelves back at the interviewer.

### 1.1 Composition: weak, and too small to matter

`g1b_composition.py` scores the 26 translated digits' composition against the
book unigram, with a matched null that draws four windows of exactly lengths
(9, 6, 5, 6) from the books:

```
observed n=26  chi2=19.727   digits never used: ['0', '1', '2']
null=window   p(chi2 >= obs) = 0.0163   p(>= 3 unused digits) = 0.0269
null=iid      p(chi2 >= obs) = 0.0199   p(>= 3 unused digits) = 0.0253
```

WEAK by the repo's own threshold (`p < 0.01` = SUPPORTED). And it is 26 digits:
the 1-sigma error on any digit frequency at n = 26 is +-0.059 against a 0.1
mean. **The NPC "dialect" cannot be attacked as a corpus at all** — it is
26 digits, 433x smaller than the books. Nothing about its internal structure is
estimable. Anyone proposing to solve the NPC lines separately should stop here.

The one detail worth recording is that no `0` appears in any of the four
translated strings, which is exactly what the librarian's `0` keyword says
should happen (§4).

---

## 2. Every 469 string in shipped game content

`g0_extract.py` scans all 1,148 NPC transcripts, all 2,135 books and the eight
OT-server `.lua` scripts for digit runs. The complete census of 469-like strings
(everything else at >= 5 digits is a gold price or an account balance):

| string | speaker | trigger | in books? |
|---|---|---|---|
| `485611800364197` | A Wrinkled Bonelord | ambient voice | yes (1x) |
| `78572611857643646724` | A Wrinkled Bonelord | ambient voice | yes (6x) |
| `486486` | A Wrinkled Bonelord | `name` | no |
| `1` | A Wrinkled Bonelord | `tibia` | (trivial) |
| `653768764` | Elder Bonelord, The Evil Eye | ambient voice | no |
| `659978 54764` | Elder Bonelord | ambient voice | no |
| Avar Tar's 20-group "poem" | Avar Tar | **`bonelord language`** | no |
| `74032 45331` | book, Secret Library (2018) | — | no |

That is the entire set. Nothing else in Tibia is written in 469.

### 2.1 The Elder Bonelord "translations" are an artefact of wiki layout

This is the most consequential single finding of the sweep, and it downgrades
two `confidence="high"` cribs.

`data/external/npc/elder_bonelord.lua` (`opentibiabr/canary`, `mattyx14/otxserver`):

```lua
monster.voices = {
    { text = "Inferior creatures, bow before my power!", yell = false },
    { text = "Let me take a look at you!", yell = false },
    { text = "659978 54764!", yell = false },
    { text = "653768764!", yell = false },
}
```

These are **four independent entries in one random-selection table**. There is
no pairing in the data. The reading "653768764 means *Inferior creatures, bow
before my power!*" comes from the two lines appearing adjacent in a wiki
"Sounds" list, not from anything in the game.

Two further checks kill the pairing outright:

* the plain **Bonelord** monster (`bonelord.lua`) says *"Let me take a look at
  you."* in English, with **no 469 at all** — alongside "You've got the look!",
  "Eye for eye!", "I've got to look!", "Here's looking at you!". It is an
  ordinary eyeball-pun flavour line reused for the Elder, not a gloss.
* **The Evil Eye** (`the_evil_eye.lua`) has only two voices — *"Inferior
  creatures, bow before my power!"* and *"653768764!"* — so if adjacency were
  translation, `653768764` would have to mean the Evil Eye's line *and* the
  Elder's, while `659978 54764` would have no partner at all.

The same four-entry table, byte-identical and with the same
`interval = 5000, chance = 10`, appears independently in `opentibiabr/canary`,
`mattyx14/otxserver`, `zimbadev/crystalserver` (two datapacks) and others —
checked live via GitHub code search. *Caveat:* these are open-source
**reimplementations** of CipSoft content, not CipSoft's source. But what they
transcribe is the observed in-game behaviour, and that behaviour — a random
ambient-voice table sampled every 5 s at 10% chance — is exactly what rules the
pairing out. Lines drawn independently at random cannot be a gloss of one
another.

**Recommendation for `c469/cribs.py`:** the `claimed_plaintext` on
`653768764` and `659978 54764` should be demoted from `confidence="high"` to
`confidence="low"` with a note that the pairing is a wiki-layout inference, not
game data. The librarian's `486486` (bound to the `name` keyword in a
`prompt -> answer` tree) and `1` (bound to `tibia`) keep their high confidence —
those really are keyword-bound glosses.

Net effect on §1: the *split* does not depend on the translations being real.
It is a containment result about which strings appear in the library. But the
supply of genuine known-plaintext for 469 shrinks from four strings to **two
short ones** (`486486` = a name, `1` = Tibia), i.e. seven digits.

### 2.2 The librarian's full keyword tree contains no key

Full transcript at
`s2ward/tibia:data/npcs/text/Ab'Dendriel/Hellgate/A_Wrinkled_Bonelord.txt`
(quoted in full in the extraction output). It is richer than the OT-server
version and than this repo's README — it adds `librarian`, `our`, `city`,
`wars`, `blinky`, `job` — and every added branch is lore, not cipher. The
relevant additions:

> *librarian*: "So much knowledge was lost in the great wars ... Most of our
> data storages are lost and so are the means to read or recreate some of them
> ... We had to use the primitive storage form of books to recreate some of the
> lost knowledge."

That is a designer telling you, in-world, that the means to read them is gone.

A **second** Hellgate bonelord NPC, **Dreadeye**, was not in this repo at all
and has a `language` keyword:

> *language*: "Only true bonelords can understand our language. Even I in my...
> changed state have a hard time understanding even the simple parts of our
> writings and some parts of it are completely alien to me now. You, human,
> will never understand our language as you will never understand our ways."

And **The First Dragon** (a boss NPC, `memoirs`):

> "If it becomes popular, I might consider an orcish translation or even one in
> bonelord language. ... By the way, it's a funny story how I learnt the
> bonelord language. However, I saved it for a possible part two of my memoirs."

Across 1,148 NPCs and 2,135 books, those are **all** the references to the
bonelord language, and every one of them is a refusal. That is a deliberate
authorial posture, sustained for 25 years.

---

## 3. The control case: what a Tibian cipher with a key actually looks like

Tibia *does* ship a solved constructed language, and its design is the decisive
comparison. `g3_poll.py` reads it straight out of `book_database.json`.

**Fiehonja Library** (Deepling, added 2011) contains, on the same shelves:

* 6 ciphertext books (`Deepling_Book_1` .. `_6`) in a glyph script;
* `Jekhr_Basics` — **the alphabet**, 26 glyph->Latin rows, parsed
  programmatically by `g3_poll.py` with no hand-transcription;
* `Jekhr_Pronouns`, `Jekhr_Basic_Vocabulary_I/II`,
  `Jekhr_Advanced_Vocabulary_I/II`, `Jekhr_Numbers` — **116 glossary entries**,
  plus a note on how compounds are formed;
* `Deepling_Book_1_Translated` .. `_6_Translated` — **the worked solutions**,
  four-stage (Original -> Alphanumeric -> Pronounced -> Substitution ->
  Interpretation).

CipSoft ships the ciphertext, the key, the dictionary **and the answer key**,
all in one library. There is a second, older instance of the same pattern in
Rookgaard: `Ork_Porak` gives an orcish inventory tally ("5 5 5 5 2 charcha /
5 burka / ...") with an explicit `Translation:` section on the same page — a
*numeric* code, published with its solution, in a starter zone.

**Hellgate Library contains 71 books and all 71 are 469.** Not one line of
prose. No alphabet, no glossary, no worked example, no "Translated" companion.
The one Tibian design pattern for a decodable constructed language is
conspicuously, completely absent from the one place it would have to be.

### 3.1 The 2020 poll correction is confirmed

The PR corrected an earlier claim that the poll's three answers were one
sentence in three encodings. `g3_poll.py` verifies this from shipped data only:

```
A (ASCII binary) -> "These aren't the words you're looking for."
B (Jekhr, decoded with the in-game alphabet from Jekhr_Basics)
  -> ROQOHN OLJENT JEH DAKN KWEH DH JHLOSK
     roqohn = nonbeliever/not obeying     jeh = the/that/this
     oljent = defy/defies                 dakn = narrow
     kweh   = path                        dh  = to
     jhlosk = jhli (sea/water) + osk (down) = "undersea"
  -> "Nonbelievers defy the narrow path to undersea!"
C (469) -> 663 902073 7223 67538 467 80097   [no key exists anywhere]
```

A and B are **different sentences**. The three answers are three different
jokes. **Answer C is not known-plaintext and must never be scored as such.**
The PR's correction is confirmed, and now it is confirmed by decoding B with
the game's own published key rather than by citing a wiki.

The poll is also the tell. All three answers are the same joke about opacity:
A says *these aren't the words you're looking for*, B is a taunt at
nonbelievers, C is 469. C is the punchline precisely because it has no key.

---

## 4. Structural hypotheses, scored

All scored through `c469/harness.py` against `surrogate.DEFAULT_FAMILIES`
(`Shuffle`, `Markov2`, `Markov3`, `BlockShuffle20`, `CopyPasteMutate`,
`CopyPasteMutateFitted`), 400 nulls each, pre-registered in the module
docstrings before any null was drawn. Verdict thresholds are the harness's:
worst-family `p < 0.01` SUPPORTED, `< 0.05` WEAK, else REJECTED.

### 4.1 The 5-eye premise (`g2_fiveeye.py`)

Three mechanised readings of "a bonelord blinks with five eyes", each
pre-registered in the module docstring:

| id | hypothesis | statistic | real | verdict |
|---|---|---|---|---|
| H1 | a 469 "word" is one digit per eye, so digit statistics depend on position mod 5 | `positional_chi2(books, 5)`, greater | 25.42 (df 36) | **REJECTED**, worst p = 0.923 |
| H2a | ten digits = five eye-values x a binary flag; the `d // 5` stream is the carrier | `cond_entropy(hi, 4)`, less | 0.99350 | **REJECTED**, worst p = 0.823 |
| H2b | ...the `d % 5` stream is the carrier | `cond_entropy(lo, 4)`, less | 1.62238 | **REJECTED**, worst p = 1.000 |
| H3 | words are five digits, so book lengths cluster on multiples of 5 | books with `len % 5 == 0` | 13 / 70 | **VACUOUS** — see below |

**H1 is not merely non-significant, it is anti-significant.** The observed
mod-5 chi-square is *below* every null family's mean (z = -1.0 to -1.3): the
corpus is slightly more uniform mod 5 than a shuffle of itself. Whatever 469
is, it does not have a five-digit frame.

**H2** is the base-5 decomposition. Both derived streams are unremarkable once
the corpus's own digit-level structure is accounted for. The `lo` stream shows
the classic trap in full: h4 = 1.622 against `Shuffle` at 2.264 +- 0.002, which
is **-294 sigma** — and against `Markov3` (1.598 +- 0.011) and
`CopyPasteMutateFitted` (1.521 +- 0.034) the real corpus is *less* structured
than the null. A base-5 split extracts no structure that the digit sequence did
not already have.

**H3 is vacuous and is recorded as such rather than as a rejection.** Every
family in `DEFAULT_FAMILIES` preserves book lengths exactly, so real == null ==
13 for all six. The observed mod-5 histogram of book lengths is
`{0: 13, 1: 19, 2: 13, 3: 12, 4: 13}` — 13/70 is 18.6%, i.e. chance. To score
H3 properly one would need a null that resamples book lengths, which no
existing family does; the raw histogram is flat enough that it is not worth
building one.

#### The control scan, and the one cell that fired

Modulus 5 was scanned alongside 2..12 precisely so that "5 is special" could
not be claimed retrospectively. Modulus 5 came out at p = 0.923, q = 0.99.
But **modulus 8 fired at the p floor against all six families** (+3.6 to
+4.7 sigma). `g6_mod8_followup.py` tested it harder rather than reporting it:

* **F1 — it does not survive dedup.** On `corpus.dedup_core()` (22 books,
  3,901 digits, the material left after greedily dropping books that are mostly
  repeats), mod 8 gives chi2 = 60.14 against df = 63 and null means of 63-66:
  **z = -0.25 to -0.48, worst p = 0.68**. Mod 16 likewise, z = -0.66 to -0.89.
  The effect is entirely carried by the corpus's near-duplicate books.
* **F2 — 8 is not special.** Extending the scan to 13..24 makes modulus 16
  SUPPORTED too (p = 0.0075) and 14 WEAK (p = 0.0299), while 13, 15, 17-24 are
  all null. The pattern is "some even moduli", i.e. repeated blocks landing at
  correlated offsets across near-duplicate books — not a frame.
* **Benjamini-Hochberg over the full 23-modulus scan**: the smallest q is
  **0.0575** (modulus 8) and the next is 0.0862 (modulus 16). **Nothing clears
  q < 0.05.** The one SUPPORTED cell does not survive its own multiplicity
  correction, let alone the dedup control.
* **F3 — the excess is a redundancy signature.** It sits almost entirely in
  residues 1 and 3, driven by digit `0` (-11.4 at residue 1, +11.3 at
  residue 3), `6` (-12.6 at residue 3), `5` (+9.4), `8` (+7.1); residues 4-7
  are flat. A leave-one-book-out jackknife moves the statistic only between
  105.5 and 123.1, so it is diffuse across the corpus rather than one book.

This is the PR's documented false-positive pattern (+1.2 sigma Zipf slope,
+6.26 sigma homophonic) recurring for a third time, and dying the same way.

### 4.2 The librarian's 0 taboo (`g5_zero_role.py`)

The librarian has a dedicated keyword for the digit `0` — *"Go and wash your
eyes for using this obscene number!"* — and no translated 469 string contains a
`0`, yet the books are 7.6% zeros. The natural structural reading is that `0`
is punctuation.

| hypothesis | statistic | real | verdict |
|---|---|---|---|
| H4 `0` delimits tokens | entropy of 0-to-0 gap lengths (direction: less) | 4.6299 bits | **REJECTED**, worst p = 0.678 |
| H5 `0` marks book edges | books whose first or last digit is `0` | 14 / 70 | **REJECTED**, worst p = 0.172 |

H4 is a textbook reproduction of the false-positive pattern the PR documents:

```
Shuffle                4.90617 +- 0.02416   z = -11.43   p = 0.0025
BlockShuffle20         4.77348 +- 0.02044   z =  -7.02   p = 0.0025
Markov2                4.76025 +- 0.04785   z =  -2.72   p = 0.0100
Markov3                4.74771 +- 0.05162   z =  -2.28   p = 0.0075
CopyPasteMutate        4.69423 +- 0.09474   z =  -0.68   p = 0.2469
CopyPasteMutateFitted  4.56909 +- 0.11793   z =  +0.52   p = 0.6783
```

-11.4 sigma against a unigram-matched null; *entirely ordinary* against the
copy-paste generator, which slightly overshoots it. The regularity in the zero
spacing is the corpus's redundancy, nothing more.

### 4.3 Book titles, ordering and shelf position

No carrier is available, and this is a data fact rather than a negative result:

* The books have **no in-game titles**. `book_database.json` names them by
  their first ten digits — that is the scraper's key, not a title.
* `previous-book` / `next-book` are `_NOPREV` / `_NONEXT` for all 71: there is
  no reading order.
* All 71 map to the **single** coordinate `32787,31686,13`. No public source
  records per-book shelf position, so "shelf order as a carrier" is not
  currently testable by anyone. Recovering it would need an in-client survey of
  the Hellgate library floor, which is the one piece of fieldwork that could
  add genuinely new signal.

### 4.4 Do the digits index a published Tibian word list?

There is exactly one number->word mapping ever published in Tibia
(`Ork_Porak`), and it is orcish tally-counting: `5 = burka` (sword),
`2 = batuk` (bow), digits are *quantities*, only 1/2/3/5 appear, and the
translation ships alongside. It has no bearing on 469, which uses all ten
digits including the one its own speaker declares obscene.

The Mad Mage's Paradox Tower mirror-room books, long proposed as the 469 key,
are in the database in full:

```
Ljkhbl_Nilse   (author: The Mad Mage)     Dtjfhg_Jhfvzk   (author: The Mad Mage)
ljkhbl nilse jfpce ojvco ld               dtjfhg
slcld ylddiv dnolsd dd sd                 jhfvzk
sdcp cppcs cccpc cpsc                     bbliiug
awdp cpcw cfw ce                          bkjjjjjjj
cpvc ev vcemmev vrvf                      xhvuo
cp fd vmfpm xcv                           fffff
                                          zkkbk h
                                          lbhiovz
                                          klhi igbb
```

Their neighbours on the same shelf are `Tfel_Thgirtfel` ("Tfel thgirtfel" =
"left rightleft" mirrored), `Mirror_Mirror_on_the_Wall`, `Doing_It_the_Mad_Way`,
`The_Book_of_Foolish_Jokes`, `Book_of_Funny_Letters_I`. The library is
characterised in-game as the raving of a madman, and `Book_of_Funny_Letters`
names the joke. There is nothing here to index into, and no in-game text ever
connects these books to 469.

---

## 5. What would still be worth doing

1. **Fix the cribs.** Demote the Elder Bonelord / Evil Eye `claimed_plaintext`
   entries to low confidence with the `voices`-table note (§2.1). Add Dreadeye.
   The known-plaintext budget for 469 is **7 digits**, not 26.
2. **Shelf positions.** The only untested structural carrier left is the
   physical arrangement of the 71 books in the Hellgate library, and no public
   dataset has it (§4.3). This needs a client, not a computer.
3. **Do not** attack the NPC strings as a separate corpus. 26 digits, of which
   19 now have no reliable gloss (§1.1, §2.1).

## 6. Answers to the three questions asked

* **Does the two-dialect split hold up?** Yes, at p ≈ 5.3e-6 against a
  leave-one-out null built from the corpus's own repeat structure, and length
  runs *against* the split rather than explaining it. But its meaning is
  narrower than "two encodings": the in-book strings are demonstrably
  quotations of existing book text, and half the out-of-book strings turn out
  not to have trustworthy translations at all (§2.1).
* **Does the 5-eye / base-5 hypothesis survive a null?** No, in every form.
  A period-5 frame is *anti*-significant (below every null's mean, p = 0.92);
  neither half of a base-5 decomposition carries structure the digit sequence
  did not already have; five-digit words are unsupported. The control scan's
  one hit was modulus **8**, not 5, and it dies both on the dedup-core corpus
  (z = -0.3) and under its own multiplicity correction (BH q = 0.058) — the
  repo's false-positive pattern, third occurrence. See §4.1.
* **Is there an in-game key candidate?** No. Tibia has a documented pattern for
  publishing one — alphabet book, glossary books, worked-solution books, all in
  the same library (§3) — and the Hellgate Library contains 71 books of which
  71 are 469 and none is prose. Every one of the three in-game references to
  the bonelord language, across 1,148 NPCs and 2,135 books, is an explicit
  refusal to supply a key.
