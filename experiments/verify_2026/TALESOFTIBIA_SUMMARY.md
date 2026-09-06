# The Tales of Tibia 469 series: what it actually argues

**Source:** https://article.talesoftibia.com/469/1 through `/5` (five parts; `/469/6` is a 404).
**Retrieved:** 2026-09-04, over an unblocked network. Full structured notes per part in
`data/external/provenance/talesoftibia_469_part{1..5}_2026-09-04.md`.

**Author:** "Simula" — reddit *s2w*, Discord *Cony Island*, Twitch/GitHub *s2ward*. **This is this
repository's own owner.** The article is not an outside rebuttal of the repo; it is the repo author's
own later position, which is why the README defers to it. He names this repository inside part 2:
"I made a github repository listing all findings so far and some of my own thoughts."

The prior session could not reach the domain and reconstructed §8 of
`experiments/provenance/TIBIA_MYSTERY_PATTERNS.md` from search snippets. That reconstruction was
**directionally right but wrong on the mechanism** — corrections in §6 below.

---

## 1. Central thesis, in three sentences

469 is not a cipher with a recoverable plaintext; it is a **deliberately authored decoy**, planted by
CipSoft's content team to absorb player attention so that the real hidden content — the Magic Web of
teleport gates, the ley lines, the coordinate books, and the buried history of the "ancients" — would
go unexamined for two decades. The article's proof text is a ruined in-game book on Isle of the Kings
whose surviving fragments read `... of madness ... decoy ... avert ... from the obvious ...`, which
the author completes as "Numbers of madness were made as a decoy, a ploy to avert from the obvious",
plus a 2000s TibiaBR interview in which Knightmare jokes that CipSoft "hired an actual beholder" to
write the texts and had **no way to verify it wrote what was dictated**. Everything the author claims
to have *recovered* is lore and geography — the Mad Mage as Durin/Kirok, the Dream Catcher as
Variphor, the Navigator as Lagatos — reached by cross-referencing NPC dialogue and books, never by
decoding a single digit.

### Was the prior session's "meta/lore in-joke about the 2010 beholder→bonelord rename" guess right?

**Half right — correct that it is meta/lore rather than cryptographic, wrong that the rename is the
punchline.** The trademark rename appears exactly once, as a subordinate clause in part 2, noting the
15th-anniversary nostalgic bonelord was named 3478 "instead of beholder as they used to be called
before they had to change it due to some copyright thing." It carries no argumentative weight. The
actual thesis is the decoy claim above. Correct that file's §8.

---

## 2. Section-by-section summary of the argument

| Part | Title | What it does | Evidence type |
|---|---|---|---|
| 1 | Introduction to Madness | Bonelord lore; Paradox Tower / A Prisoner / mathemagics; the **Mad Mage = Durin** thesis; the `...`/`****` redaction motif; the Thais rebellion chain | NPC dialogue, in-game books |
| 2 | A Taste of Madness | Demona's warlocks; the **Magic Web**; the honeminas/Donina/tridiag formulae; the Dianscher coordinates; the first map overlay | In-game books, map overlay |
| 3 | Descent into Madness | The **Drefia geometry formulae**; refined Dianscher reading; full web reconstruction; the **Kilmaresh reuse**; Ztiss and the enslaved many-eyed horrors | Map overlay, NPC dialogue |
| 4 | Widespread Madness | Shattered Isles catastrophe; Yalahar and **Variphor**; the Deepling language and the **SENX consonant-shift decode**; the Navigator = Lagatos | Philology, in-game books |
| 5 | Complete Madness | The Dream Catcher as Variphor; **the decoy reveal**; the Knightmare interview; open leads | Two quoted texts |

**Part 1** establishes bonelords as a fallen god-war race, then walks the Paradox Tower riddle chain to
A Prisoner in Mintwallin, who teaches "mathemagics" and whose 1+1 answer depends on a stated favourite
colour. It quotes the canonical wrinkled-bonelord lines about 469 and *Beware of the Bonelords*, then
builds its first speculative identification: the Mad Mage is Durin, the dwarves' celestial paladin
god, who faked his death. Load-bearing for later parts is a line from the famous
"You can not even imagine how old I am" book: **"It was me who assisted the great calculator to
assemble the bonelords language."** It also identifies a recurring redaction motif — books whose text
is `...`, `****`, or in Drefia's *Circular Canon of Eternal Darkness* pure punctuation — read as
"powerful people only". The Thais rebellion chain (Oswald's rumours → Sam/Uzgod/Ben → Gamel →
`berfasmur`) is offered as *method validation*: obscure cross-references really do resolve.

**Part 2** is where the article's real programme starts. From Demona's warlock books it extracts the
**Magic Web**: a gods-made network of teleport gates joined by "red lines". Zuania's book records a
teleport that overshot from the intended east gate of Thais to north of Carlin; the author visits both
endpoints and reports concealed content at each. He then reproduces the formula books — honeminas,
Donina I and II, tridiag, and the Dianscher coordinates `p3,q9,0o and p3,23,0t` — and makes the move
that connects them to 469 at all: **the lowercase-h argument**, that every author name in the set is
capitalised except *honeminas*, and that the text says "honeminas *itself* died", so honeminas was not
human but a bonelord. With Sopel and Elkolorado he overlays an in-game map on the coordinates and
lands on a swamp island with a three-stone circle and swamp trolls.

**Part 3** proposes "tridiag" means tridiagonal matrix, reports three geometry formulae found in
**Drefia** (see §4), refines the coordinate reading by mirroring a creased map corner, reconstructs the
whole web, and finds Milos's in-game **ley lines** dialogue as apparent confirmation. Its strongest
structural claim is that the *same* Demona map appears in Kilmaresh's Fafnar ruins and that the same
overlay method produces a meaningful X there too. It closes with the article's origin story, from
Ztiss: Zao "fought ze many-eyed horrorz and enzlaved zem... Zao had learnt enough of zeir magic to
crush zem" — i.e. 469 was taken from the bonelords, not invented by them.

**Part 4** is lore synthesis with one real methodological contribution. Its worked **SENX decode** —
deriving the consonant shifts T→H, X→K, W→M, V→B from near-identical word pairs across the older and
younger Deepling tongues — is genuine, checkable philology and the only cryptanalysis-shaped work in
the series. It is also where the author reports and then *discounts* a language experiment: he
collected every Tibian constructed language, transposed them, ran character frequency analysis, found
top-7 similarity that unrelated real languages did not show, and concluded frequency analysis was "not
as useful" given language evolution. He states the design intent plainly: the languages were "never
intended" to be completely translatable.

**Part 5** identifies Variphor with the Dream Catcher, then delivers the reveal. The decisive argument
against decryption is a **dating argument**: "What could books from 2001~ tell you? ... Could it tell
us the answer to Tibia in 2023?" — coupled with his own overlay finding that the 71 books reduce to
roughly one book's worth of content. He closes with a list of leads he explicitly did not test.

---

## 3. Where the article AGREES with this repo's PR

This matters more than the disagreements. The article is **not** a defence of decryption:

- It concludes there is no plaintext to recover. So does the PR.
- It reports the author's own ~50 hours of overlay work finding the corpus reduces to about one
  book's worth of distinct content — an independent, differently-derived version of the PR's
  copy-paste finding.
- It quotes the same Knightmare "obvious things distract attention" line the PR's provenance file
  already uses, and adds the stronger TibiaBR joke interview.
- It states that Tibia's constructed languages were "never intended" to be fully translatable.

---

## 4. Evidence, content and leads the PR did NOT consider

### 4.1 The Drefia geometry formulae — the strongest new lead

Part 3 reports three formulae found **in Drefia**, on a location the author's reconstructed web marks
as a gate, brought to his attention by another player, **Besd Tesd**. Rendered in the article as LaTeX:

1. `\frac{1}{2} ab` — area of a triangle from two sides and the included angle
2. `A_G \cdot h` — area of a parallelogram from base, height and included angle
3. `\vec{P} = (p_1, p_2)^T` — a two-component column vector

He uses them to license reading the Dianscher coordinates as three points forming a triangle, and
notes formula 2's dot product matches the honeminas construction. He computes that dot product as
**88**; the correct value is **83** (this repo's `experiments/provenance/HONEMINAS.md` already has it
right). He never returns to Drefia.

**What is concretely open, and what to do about it:**

| Open question | How to settle it |
|---|---|
| Do these three formulae exist as in-game Drefia content at all? | Tibia Fandom search for Drefia book titles; the article gives no title, room, or coordinates |
| Are they *books*, or map decorations / an author's transcription of images? | The LaTeX rendering is suspicious — in-game books are plain text. This may be the author's own formalisation of pictures |
| Is the Drefia location actually a "gate"? | Only asserted, on the author's own reconstructed web |
| Do they connect to 469 digits in any way? | **The article never claims they do.** They are used only to justify a coordinate reading |

This is the single unverified primary-source item in the series that a next session could resolve
cheaply. Note the honest assessment: even if the formulae exist, the article uses them for map
geometry, not for the digit corpus. Confirming them would validate the *Magic Web* thread and would
not by itself bear on whether 469 has a plaintext.

### 4.2 Other content the PR never touched

- **The Dianscher coordinates** `p3,q9,0o and p3,23,0t` and the whole map-overlay method. The PR's
  `HONEMINAS.md` catalogues the formula books but does not mention this book, which is by the same
  in-fiction author (Mathemicus) and is the actual payload the author cares about.
- **The Kilmaresh reuse.** The claim that the same Demona map appears in Kilmaresh's Fafnar ruins and
  that one overlay method works in two regions separated by ~14 years of development is the article's
  most falsifiable structural claim. Entirely absent from the PR.
- **The lowercase-h argument** — the *only* textual argument anywhere linking honeminas to bonelords.
  `HONEMINAS.md` asks "Is Honeminas even a bonelord?", answers no from wiki sources, and never
  encounters the argument the community actually uses. It should engage it directly. (The argument is
  weak — "itself" is used of a person elsewhere in Tibian book English, and the lowercase is equally
  explicable as a typo in a 2001 flavour-text book — but it deserves an explicit answer.)
- **The SENX consonant-shift decode** (part 4). A real, reproducible substitution derivation on a
  Tibian constructed language, showing CipSoft *does* ship decodable content — but, tellingly, **only
  with an in-game dictionary attached**. This is direct support for the PR's own thesis in
  `TIBIA_MYSTERY_PATTERNS.md` that Tibia ships decodable content only with the key.
- **The author's own frequency-analysis experiment** across all Tibian constructed languages, and his
  reasons for abandoning it.
- **The Opticording Sphere parchment reportedly bearing Jekhr characters representing binary** — an
  unverified but concrete claim of a numeric/constructed-language crossover artefact.
- **The 15th-anniversary nostalgic bonelord named 3478** and the **Knightmare NPC** using 3478 in a
  number sentence. The repo's README has the Knightmare NPC line; it does not have the anniversary
  monster name, which if true is a designer-side reuse of a corpus 4-gram.
- **The TibiaBR beholder-language joke interview.** The repo has the 2009 Chayenne interview; this is
  a second, earlier, more explicit designer joke, and it is the strongest single piece of external
  evidence in the article.

---

## 5. Does anything CONTRADICT the PR's "copy-paste artefact, no recoverable plaintext" conclusion?

**On the conclusion itself: no. On the mechanism: yes, and it matters.**

### 5.1 The real disagreement: accident versus design

The PR concludes the corpus is a **copy-paste artefact** — a mechanical, unintended consequence of how
the books were produced. The article concludes it is a **deliberate decoy** — authored, intentional,
with the redundancy as camouflage.

Both predict "no plaintext", so the PR's headline survives. But they are different claims about the
world and they diverge on what a next experiment should expect. If the corpus is an artefact, its
statistical structure should look like unconsidered duplication. If it is a designed decoy, one might
expect the duplication to have been *shaped* — and the PR's statistics, which test for language-like
signal, would not distinguish these. The PR should either adopt "designed decoy" as an equally-ranked
hypothesis or say explicitly why it prefers accident.

### 5.2 Claims that cut against "pure artefact" — and how they hold up

**(a) The 4-gram claim — verified as stated, then defused.** The article claims that in the Hellgate
books `4315` appears 14 times and `3478` appears 24 times, while the full five-digit honeminas vectors
appear 0 times. Checked directly against this repo's `books.json` (substring counts over the
concatenated digit stream):

| string | article's claim | measured |
|---|---|---|
| `4315` | 14 | **14** ✓ |
| `3478` | 24 | **24** ✓ |
| `43153` | (0 implied) | **0** ✓ |
| `34784` | (0 implied) | **0** ✓ |

The article is **exactly right**, and its claim is a *different and better-founded* claim than the
README's, which `HONEMINAS.md` correctly demolished as a transcription typo (`43151`/`34783`). The 14
occurrences `HONEMINAS.md` attributes to the typo `43151` are in fact the same 14 hits as the correct
`4315`, because `43151` contains `4315`. **`HONEMINAS.md` §4 should be amended:** its conclusion
("Neither number from the formula appears anywhere in the corpus") is true only for the 5-digit forms,
and the article's 4-digit version of the observation is factually correct.

**But the observation is not evidential.** Over the 11,263-digit corpus there are 1,097 distinct
4-grams with a mean of 10.3 occurrences and a maximum of 128. `4315` at 14 ranks **221st**; `3478` at
24 is beaten by **87** other 4-grams. Both sit unremarkably inside the bulk of the distribution. This
is a clean, quantitative answer that neither the article nor the previous README ever computed, and it
is worth adding to the repo.

**(b) The Kilmaresh reuse.** If the same map artefact really is reused across ~14 years of content, it
implies sustained authorial intent around this material — supporting "designed" over "accidental".
Unverified; falsifiable from the wiki.

**(c) The reduction-to-one-book finding.** The author independently reached the corpus's redundancy by
manual overlay. Read one way this corroborates the PR. Read another, an author who *deliberately*
padded one book into 71 would produce exactly this signature.

### 5.3 What does NOT contradict the PR, despite appearances

The article contains no successful decryption, no plaintext, no key, no digit-level structure claim
beyond the 4-gram counts above, and no dev statement confirming any of it. Its author is explicit that
it is biased and untested ("Sadly I cannot test anything"), and that his theory "might not be 100%
accurate". The prior session's worry that part 3's Drefia leads make the article "not purely
deflationary" is correct in letter but weak in force: those leads are about map geometry, and the
article's own conclusion is that the digits are a decoy.

---

## 6. Corrections owed to existing repo files

1. `experiments/provenance/TIBIA_MYSTERY_PATTERNS.md` §8 — replace the snippet-reconstructed thesis.
   The article is not primarily about the beholder→bonelord rename; that is one clause. The thesis is
   the Isle of the Kings "decoy" book plus the Knightmare interview. Remove the `[SE]`/`REPORTED`
   markers on the article claims; they are now first-hand. Keep the file's honest caveat that the
   article partly diverges from the PR — but restate the divergence as *design vs accident*, not
   *pointer vs noise*.
2. `experiments/provenance/HONEMINAS.md` §4 — amend as set out in §5.2(a). The 5-digit finding stands;
   the blanket statement does not.
3. `experiments/provenance/HONEMINAS.md` §5 — engage the lowercase-h argument explicitly, since it is
   the community's actual reason for calling honeminas a bonelord.
4. The repo has never recorded the *Coordinates for the area around Dianscher* book. It belongs
   alongside the other Demona formula books.

---

## 7. Every checkable factual claim, classified

Legend: **[G]** verifiable in-game · **[W]** verifiable from wiki/external record · **[U]**
unverifiable assertion (interpretation, speculation, or personal narrative).

### Quoted in-game text (all [W], and [G] where a location is given)

| # | Claim | Class |
|---|---|---|
| 1 | *Beware of the Bonelords* describes a blinking code that is also mathematics | [W] — already in repo README |
| 2 | A Wrinkled Bonelord's 469 / language / bonelord dialogue lines as quoted | [W][G] |
| 3 | A Wrinkled Bonelord says "I'm 486486 and NOT 'Blinky'" | [W][G] |
| 4 | The Hellgate library holds 71 books of numbers | [G] — repo's corpus has 70; **worth reconciling** |
| 5 | A Prisoner teaches mathemagics; 1+1 = 1/13/49/94 by favourite colour | [W][G] |
| 6 | Riddler answers: goshnar, demonbunny, Tha'kull, green, nothing | [W][G] |
| 7 | Kawill calls Durin "the celestial paladin"; Isimov says all firstborn but Durin lie in the Hall of the Ancients | [W][G] |
| 8 | Oswald is Durin's assistant and calls him a tyrant; Bozo links Durin to *Fun with Demons* | [W][G] |
| 9 | "Mad Mage valley" appears only in the hidden *Create Beer* recipe | [G] — the "only" is checkable and strong |
| 10 | The "You can not even imagine how old I am" book contains "assisted the great calculator to assemble the bonelords language" | [W] |
| 11 | Demona holds 19 blank formula books and 5 blank *History of the Ancients* books | [G] — exact counts, checkable |
| 12 | Demona holds ~10 maps of Tibia showing the web | [G] |
| 13 | Honeminas / Donina I & II / tridiag formula texts as transcribed | [W] — repo has independently |
| 14 | *Coordinates for the area around Dianscher*: `p3,q9,0o and p3,23,0t`, by Mathemicus | [W] — **not yet in repo** |
| 15 | Zuania's teleport book: intended east Thais, arrived near Carlin, saw red light and distant gates | [W] |
| 16 | Milos's ley lines dialogue | [W][G] |
| 17 | Ztiss: Zao fought and enslaved the many-eyed horrors and learnt their magic | [W][G] |
| 18 | Yalahar plaques on the "missing factor" and the naming of Variphor | [W][G] |
| 19 | Eruaran on the dream catcher as dispenser, shaper, magnet and musical instrument, with an unidentified flaw | [W][G] |
| 20 | Lagatos's Jekhr dictionaries and grammar rules as quoted | [W][G] |
| 21 | The Navigator responds to the keyword LAGATOS | [G] — **directly testable, decisive for that identification** |
| 22 | The Isle of the Kings ruined book fragments: `... of madness ... decoy ... avert ... from the obvious ...` | [W][G] — **the thesis rests on this; verify verbatim first** |
| 23 | *Behind The Veil Of Ignorance I* text as quoted | [W] |
| 24 | The Gate Keeper / Key Master / "Other Door" dialogue | [W][G] |
| 25 | Luis's Planegazer diary: "the right coordinates in your sphere" | [G] |
| 26 | Serpentine Tower research papers 56-09 A, 33-16 H, 02-56 A, 74-08 G, 44-33 C, 77-04 D | [W][G] |

### External-record claims

| # | Claim | Class |
|---|---|---|
| 27 | Knightmare's TibiaBR interview: orc language a basic early quest device; the beholder "hired", in the basement, unverifiable output, probably "tasteless jokes" | [W] — **highest-value verification; the thesis leans on it** |
| 28 | Knightmare: "only the obvious things seems to attract peoples attention..." | [W] — repo already has |
| 29 | Lionet 2022 on metalevel storytelling | [W] — repo has `tibiasecrets_article137_lionet` |
| 30 | The 15th-anniversary nostalgic bonelord was **named 3478** | [W] — **check; a designer reusing a corpus 4-gram would be notable** |
| 31 | Beholders were renamed bonelords over a trademark issue | [W] — repo has `DND_BEHEATER.md` equivalent in `DND_BEHOLDER.md` |
| 32 | An NPC "Knightmare" used 3478 in a numeric sentence | [W] — repo README has the string |
| 33 | `4315` occurs 14×, `3478` occurs 24× in the books; 5-digit forms 0× | [W] — **verified true, see §5.2(a)** |
| 34 | A further pair `74032 45331` in Zathroth's secret library fits the same plot | [W] — **measured: neither occurs in `books.json`** |
| 35 | `berfasmur` / "one eyed stranger" "was not found by players, but was leaked" | [U] — hearsay about the community, no source given |
| 36 | Sopel and Elkolorado collaborated on the coordinate overlay; a comment thread exists | [W] — linked in the article |

### Claims requiring in-game observation

| # | Claim | Class |
|---|---|---|
| 37 | Three geometry formulae exist in Drefia at a web-gate location | [G] — **the key open lead; see §4.1** |
| 38 | Levitate on specific tiles east of Thais reaches an otherwise sealed room | [G] |
| 39 | White stone tiles occur only in dream-related locations | [G] — an "only" claim, falsifiable |
| 40 | Cracked jade flooring on Robson's Isle matches Zathroth's Secret Library | [G] |
| 41 | Paradox Tower / Excalibug islet / Rookgaard cistern / Zathroth's library sit at equal cardinal distances from the Thais dream machine | [G] — **arithmetic on map coordinates; cheap and decisive** |
| 42 | Eight gates sit at equal distances around the Thais dream machine | [G] — same method |
| 43 | A line north from the Thais dream machine passes through Paradox Tower onto "the eye" | [G] |
| 44 | The same map artefact appears in both Demona and Kilmaresh's Fafnar ruins | [G] — **highest-value structural check** |
| 45 | An unannounced pirate raid occurs at the Kilmaresh X, sometimes with a gold chest | [G] |
| 46 | The opticompass lies beneath that X | [G] |
| 47 | An Opticording Sphere parchment bears Jekhr characters representing binary | [G] — **the only numeric/language crossover claim in the series** |
| 48 | Chip appears at the Fields of Glory roughly every 100 days | [G] |
| 49 | The Cranky Lizard Crone accepts a jade hat and mentions working "for zeze people" | [G] |
| 50 | Uzgod's English becomes fluent when Excalibug is mentioned | [G] |
| 51 | Amber's notebook lists Bozo, Sam, Oswald, Ferumbras, Partos, Kingsguards, Noodles, Frodo | [G] |
| 52 | Star amulets: two in Kazordoon treasury, one in Draconia, one by Omruc | [G] |
| 53 | A bonelord shield and star amulet are present in Draconia | [G] |

### Unverifiable assertions (the article's interpretive core)

| # | Claim | Class |
|---|---|---|
| 54 | The Mad Mage is Durin | [U] |
| 55 | The Mad Mage is Kirok the Mad | [U] — and in tension with 54 |
| 56 | Durin faked his death | [U] |
| 57 | honeminas was a bonelord (from lowercase + "itself") | [U] — textual but not decisive |
| 58 | The Navigator is Lagatos, and probably Faltugios | [U] — though claim 21 is a real test of it |
| 59 | Variphor is the Dream Catcher | [U] |
| 60 | The magic web existed to channel life-force to the Dream Catcher | [U] |
| 61 | All Tibian constructed languages descend from one language | [U] — author himself reports the negative result |
| 62 | Humans predate elves | [U] — inference from one book line |
| 63 | Deeplings are ancestral to the elves of Ankrahmun | [U] |
| 64 | **469 was authored as a decoy** | [U] — the thesis; supported by 22 and 27, neither of which states it |
| 65 | The blank/`****`/`...` books are one deliberate redaction motif | [U] |
| 66 | The coordinate system is real and generalises across regions | [U] pending 44 |
| 67 | Overlaying the 71 books reduces them to about one book | [W] — the repo can and should test this directly |

---

## 8. My own assessment (clearly separated from the author's argument)

Recorded separately as instructed; none of this is the article's position.

1. **The thesis is under-supported by its own two pieces of evidence.** The Isle of the Kings book is
   a *fragmentary* text whose blanks the author fills in himself; the completion "Numbers of madness
   were made as a decoy" is his sentence, not CipSoft's. It is at least as consistent with an
   in-fiction warning about madness-inducing knowledge — a very common Tibian book register — as with
   a fourth-wall statement about 469. And a joke interview is a joke: Knightmare's "we can't tell if
   the beholder wrote what we dictated" is a gag whose humour depends on the language being real
   in-fiction. Treating it as a confession is a category error.
2. **The dating argument is the strongest thing in the article, and the author under-plays it.** "What
   could a 2001 book tell you about 2023 Tibia?" is a genuinely good constraint, and it is
   independent of all the lore machinery.
3. **The method is unfalsifiable by construction.** The stated approach — know 99.99% of the lore so
   the 0.01% becomes obvious — has no stopping rule and no failure mode. Across five parts, no
   proposed reading is ever rejected on evidence; the one negative result the author does report
   (structural dissimilarity in the one-language test) is noted and then pressed forward from anyway.
4. **The article's own conclusion undercuts most of its content.** If 469 is a decoy, then parts 1–4 —
   which exist to explain 469 — are largely orthogonal to the thesis they build toward.
5. **The genuinely valuable parts are the ones that are not about 469**: the SENX consonant-shift
   derivation, the Navigator/Lagatos identification, and the map-overlay method. These are testable.
   The repo would gain more from checking claim 44 (the Kilmaresh map reuse) and claim 21 (the
   Navigator keyword) than from any further work on the digits.
6. **Net effect on the PR: strengthened, with one correction.** The article's own author independently
   reached "no plaintext" from a completely different direction. The PR's conclusion should stand; its
   *mechanism* should be softened from "artefact" to "artefact or deliberate decoy — both predict no
   recoverable plaintext, and our statistics do not separate them", and `HONEMINAS.md` §4 needs the
   4-gram amendment.
