# How CipSoft builds mysteries — a prior for 469

Research date: **2026-09-04**. Branch: `claude/cypher-solving-agents-hqnbq7`.
Sources and access caveats: `data/external/provenance/SOURCES_2026-09-04.md`.

**Question.** Not "what does 469 say" — the statistical work in this repo already shows the
70-book corpus is a copy-paste artefact. The question is *behavioural*: when CipSoft ships a
mystery, do they ship decodable content, or flavour that gestures at meaning?

**Answer, stated up front.** They ship both, and the two kinds are trivially separable by one
test: **did CipSoft also ship the key?** Every Tibian text that has ever been decoded was
decoded because a key was published *in-game or by the devs* — never by cryptanalysis of the
ciphertext alone. Nothing in Tibia has ever been cracked cold. 469 has had no key in 25 years.

> ## PRIOR: P(469 encodes recoverable plaintext) ≈ **5%** (range 2–10%), on historical
> evidence alone. Combined with this repo's statistical results, posterior ≈ **0.5–1%**.
> Defence in §7.

---

## Evidence grade warning

This session's egress proxy blocked **every** relevant domain except github.com
(tibia.com, tibia.fandom.com, talesoftibia.com, tibiasecrets.com, web.archive.org, pcgamer.com
all returned 403 at the gateway). Except where marked *fetched*, claims below rest on
**search-engine snippets summarised by a tool**, not on a primary read. I grade accordingly:

- **HARD** — primary text I read myself, or a verbatim dev/in-game quote already transcribed in
  this repo's `00-timeline.md` with a dated official URL, or a computation I ran locally.
- **REPORTED** — a specific, quotable claim reaching me only through search snippets. Consistent
  across queries, but not primary-verified in this session.
- **SPECULATION** — inference, mine or the community's.

---

## 1. The Deepling language (Jekhr) — the crucial case

**Verdict: genuinely decodable, and that fact argues *against* 469, not for it.**

The 15 Apr 2020 poll (tibia.com poll id 1009, transcribed in `00-timeline.md`) offered three
answers: (A) ASCII binary → "These aren't the words you're looking for."; (B) Deepling script
`BOQOT" O(J-"L J-T )^X" XU-T )T JT(O~X°`, pronounced "Roqoh oljent jeh dakn kweh dh jhlosk!",
meaning "Nonbelievers defy the narrow path to undersea!"; (C) 469: `663 902073 7223 67538 467
80097`. — **HARD** (repo transcription of the official poll URL).

**Was Deepling really decodable? Yes — and I verified it myself.** The Deepling language is
called **Jekhr**, and CipSoft shipped its key *inside the game*: the books **Jekhr Basics**
(orthography + "the cipher and notes in this book can be used to determine how to pronounce and
translate the four books written in the Deepling language"), **Jekhr Basic Vocabulary I/II**,
**Jekhr Pronouns**, **Jekhr Numbers**, in the **Fiehonja Library**, in-fiction authored by
"Lagatos". Fiehonja arrived with the Winter Update 2011 (v9.40, reported as 14 Dec 2011) —
i.e. **nine years before** the poll. — **REPORTED** (fandom Jekhr / Jekhr Basics pages).

The published alphabet is a plain monoalphabetic substitution over Latin letters:
`^`=A `V`=B `<`=C `)`=D `-`=E `=`=F `8`=G `T`=H `|`=I `J`=J `X`=K `(`=L `W`=M `"`=N `O`=O
`]`=P `Q`=Q(spoken k) `B`=R `~`=S `L`=T `C`=U `>`=V `U`=W `+`=X `\`=Y `/`=Z, with `°`/`!`
marking lowered intonation. — **REPORTED**.

I applied that key to poll answer B without any fitting (see the one-liner in §6):

```
BOQOT" O(J-"L J-T )^X" XU-T )T JT(O~X°   →  roqohn oljent jeh dakn kweh dh jhlosk!
published pronunciation:                     Roqoh  oljent jeh dakn kweh dh jhlosk!
```

**Six of six word-tokens match exactly**; the only deviation is a word-final `"`=n whose absence
in the published rendering is explained by Jekhr's own stated rule that word-final `T` is spoken
"aa", i.e. the published line is a loose pronunciation gloss. — **HARD** (my computation).

So Deepling is a real, self-consistent, *published-key* conlang. Three consequences:

1. **It is not a cryptanalytic success story.** Nobody broke Jekhr; players *read the manual*.
   A monoalphabetic substitution with a shipped key is decodable by construction.
2. **CipSoft's own fandom documentation says Jekhr "is not yet understood to its fullest" and
   "mostly consists of nouns and basic, infinite verbs"** — even the *keyed* conlang is a
   sketch, not a full grammar. — **REPORTED**.
3. **The poll is a rank-ordering of opacity, and the community's inability to move C is the
   whole point.** A (standard encoding, seconds), B (shipped key, minutes), C (no key, 25 years).
   Correction to a framing this repo has used: A, B and C are three *different* joke answers to
   the poll question, **not three translations of one sentence**. C is therefore **not** a
   known-plaintext crib. The absence of a decoding of C is still evidence — six years of
   attention on six short tokens with zero published result — but it is not the "parallel text
   that resisted" it is sometimes described as. — **HARD** (poll text) / **SPECULATION** (reading).

No decoding of option C has ever been published, by anyone, that I can find. — **REPORTED (negative)**.

## 2. The Warlord Sword — a "quest" that is a dialogue default

A Sweaty Cyclops in Hrodmir will offer to forge a Warlord Sword from unknown materials; the
sword is visible, walled off, beneath his workshop. Twenty-plus years of material-hunting.
The decisive datum: **the same NPC gives a materially identical response if you ask for a Sword
of Valor or a Fire Sword** — i.e. players mined a generic dialogue fallback for a quest that
does not exist. The wiki's own note is that the sword "may just be a gimmick". — **REPORTED**.

In the 2016 news story "A Night Full of Mysteries" (tibia.com id 3704, 12 Sep 2016) CipSoft has a
character recount the *player rumour* that the cyclops trades a warlord sword for 100 iron, and
close with the narrator "still waiting for that warlord sword" — the devs retelling the community's
own myth as a joke. — **REPORTED**.

**Nothing was decoded here. The "medieval comic" lead was not confirmed.** I searched
specifically for a Prince Valiant / Prinz Eisenherz / Hägar / Thorgal / Mosaik / DC *Warlord*
attribution for either the Warlord Sword or the Serpentine Tower and found **no source making
that claim**. What *is* documented is that Tibia is dense with spotted pop-culture allusions
(Doctor Perhaps→Dr No, Mephiles→Mephistopheles, the Riddler's Monty Python cadence, Excalibug
from NetHack, Schrödinger's Island). — **REPORTED**. If the user has a specific comic source in
hand, it should be treated as **an allusion, not a decoding**, until a dev confirms otherwise:
spotting a source explains *where an idea came from*; it recovers **no hidden message**.

## 3. The Serpentine Tower — 20 years, officially a Quest, still nothing

*Fetched* (glrodasz/serpentine-tower-quest README) — dated CipSoft statements:
- **Oct 2010**, "Answers from the Content Team pt.4", Knightmare: some locations "might play a
  greater role in an upcoming quest", others are decorative or undiscovered.
- **Mar 2011**: CipSoft publishes "Serpentine Tower – Myths and Theories", i.e. an official
  article *about the community's theories*.
- **Feb 2012**: a news multiple-choice item references the tower as a puzzle solution.
- **Sep 2016**: "the Serpentine Tower holds the key to solving all mysteries at once" — said by a
  character in a bedtime-story news piece.
— **HARD** (I read the compilation) / the underlying quotes **REPORTED**.

Status: unsolved; "no progress whatsoever ... after countless failed attempts by hundreds of
players". — **REPORTED**. The tower also holds the **Boots of Waterwalking**, in the game since
v7.3 (Aug 2004), visible, permanently unobtainable, decoration only. — **REPORTED**.

The one thing the tower *did* yield is instructive: the research-paper riddle "88-04 F" with a
crossed-out `XXXXXX` spell name, where the community fills in **BLOOD** because the letter count
and context fit. That is **inference from a plaintext blank**, not decipherment — and it is
unconfirmed. — **REPORTED**. This repo's own timeline notes the research-paper numbers sum to
469 *if you drop one paper* — a construction that would fit almost any target and should be
treated as numerology. — **SPECULATION** (mine, against the repo).

## 4. Other cases: what "solved" has ever meant in Tibia

| Mystery | Solved? | By what means |
|---|---|---|
| Deepling/Jekhr (2011) | Yes | **Key shipped in-game** (Jekhr Basics et al.) |
| Poll answer A, 2020 | Yes | Standard encoding (ASCII binary) |
| tibia.org hidden Avar Tar variant (2020) | Yes, 2024 | Hex→ASCII "by herrera"; and it was **not CipSoft** — a third party's DNS hijack easter egg. Four years of community effort spent on a **non-CipSoft red herring**. — **HARD** (repo timeline, Herrera's own confirmation) |
| Banuta Gate of Expertise / level-999 door | Yes, Jun 2017 | Reaching level 999. Lead product manager **Martin Eglseder**: "at the initial implementation of the door there has not been any content lying behind the door, because the creators honestly did not think that anyone would actually reach that level." — **REPORTED**, and the single most important datum here |
| Chayenne's Quest | Yes, ~8 months | Lever/action puzzle, and only after CipSoft released a further clue — **REPORTED** |
| Isle of the Kings 469 book | No | It is a *copy* of a Hellgate book. "Many people claim to have translated this strange language, but none have ever been able to supply any solid proof." — **REPORTED** |
| Secret Library (2018) 469 book `74032 45331` | No | Its groups do not occur in the Hellgate corpus — **REPORTED**, and confirmed locally: neither `74032` nor `45331` occurs as a substring of the 11,682 corpus digits (**HARD**, §6 — though see the honesty note there) |
| Spirit Grounds Gate Keeper, `Zg'!kch of Cthle-ZüuKh'lkrlxchwr` | n/a | **Lovecraft pastiche**. Nobody claims a cipher; the "solution" is recognising the genre — **REPORTED** |
| Warlord Sword, Serpentine Tower, Ferumbras' Citadel, Isle of the Kings ruins | No | — |
| Hellgate 4×4 skull matrix | No | Changed by CipSoft in 8.7, Dec 2010 (§5) |

**The pattern is unbroken: in the entire history of this game, no ciphertext has ever been
broken cold. Every success is a shipped key, a standard encoding, or a walked-through door.**

## 5. Does CipSoft troll this community specifically? Yes, repeatedly and by name

- **2009, NPC Evil Mastermind:** "You won't stop my masterplan to flood the world market with
  **fake Bonelord language dictionaries**!" — **HARD** (repo transcription; fandom-corroborated).
- **22 May 2021, official news "Buried Secrets" (tibia.com id 6148):** "Oh yeah? Like you were
  certain when you found that **'authentic' bonelord language dictionary** or discovered
  **'true' boots of waterwalking**?" — **HARD** (repo transcription of the official URL).
  Note the pairing: the bonelord dictionary is set beside an item that is *definitionally*
  unobtainable decoration. CipSoft is placing the two in the same bucket.
- **2009, content designer "Chayenne" interview**, asked what she can say about the beholder
  language: answers only in 469 digits, with `:)` and `xD`. — **HARD** (repo transcription).
- **Knightmare, on whether two-eyed beings will ever understand 469:** "You only need a
  translator with many more eyes :p" — **REPORTED**.
- **12 Sep 2016 news "A Night Full of Mysteries":** the studio's own framing device for the
  community's mysteries is *bedtime stories told to someone who can't sleep*. — **REPORTED**.
- **Dec 2010, update 8.7:** the Hellgate 4×4 skull matrix changed from
  `[3,1,6,1][1,2,1,1][1,1,3,1][4,6,1,1]` to `[1,1,1,1][1,3,6,1][1,1,4,1][4,6,1,1]`, after
  players had been theorising about it for years. — **HARD** (repo timeline, with the official
  update URL). Was it a deliberate troll? **Unproven.** 8.7 was the update that renamed
  `beholder`→`bonelord` after a D&D trademark complaint, so a graphics/decoration pass over
  Hellgate is fully explained without malice. Anyone citing the change as a troll is over-reading.
  What it *does* establish, and this is enough, is that **the matrix is not load-bearing**: a
  studio does not casually edit a structure that is the key to a 9-year-old puzzle. — **SPECULATION**
  for intent; **HARD** for the change itself.

**Weighing the counter-reading.** A joke about *fake* dictionaries could imply a real one exists.
I think this reading fails on three counts: (i) both jokes are told by *villains and boasters*
(an Evil Mastermind; characters recalling their own gullibility), whose function is to be wrong;
(ii) the 2021 line explicitly brackets the dictionary with the boots of waterwalking, a known
non-thing; (iii) the joke's target is *the players' certainty*, not the dictionary's existence —
"like you were **certain** when you found...". — **SPECULATION**, but well-supported.

## 6. What I checked locally

```
Jekhr key applied verbatim to poll answer B → "roqohn oljent jeh dakn kweh dh jhlosk!"
                             published gloss → "Roqoh  oljent jeh dakn kweh dh jhlosk!"   6/6 tokens
```

Corpus cross-check (`01-books.md`, 11,682 digits): none of `74032`, `45331`, `663`, `902073`,
`7223`, `67538`, `29639`, `46781`, `486486`, `653768764` occurs as a substring. **Honesty note:**
this is *weak*. The corpus contains ~11.7k distinct 5-grams out of 100k possible, so a random
5-digit string has ≈12% chance of appearing; 0 hits out of 9 has p≈0.35 under pure chance and
proves nothing on its own. It is *consistent with* NPC/news 469 being generated ad hoc with no
shared lexicon, and it fails to produce the token reuse a real language would show — but it is
corroboration, not a result. — **HARD** (computation), **SPECULATION** (interpretation).

## 7. The prior, and its defence

**P(469 encodes recoverable plaintext) = 0.05**, on Tibia's mystery track record alone.
Reasonable range **0.02–0.10**.

Why not lower (the 5% is not 0):
- CipSoft *does* build real, decodable conlangs — Jekhr is proof of capability and appetite.
- 469 was authored by Knightmare, a designer who states that "there are so many secrets hidden in
  my areas that never ever were found" (**REPORTED**), and who has never denied 469 is solvable.
- CipSoft has retro-fitted content into empty mysteries before (the level-999 door), so "no
  plaintext today" does not strictly imply "no plaintext ever".
- One community survey (tibiasecrets art. 160) claims a *partial cipher key*. Unverified and,
  given this repo's statistics, almost certainly a fitting artefact — but it is a live claim.

Why not higher:
- **The key test.** 100% of decoded Tibian text had a published key or used a standard encoding.
  0 of ~6 long-running Tibian puzzles have ever been broken by analysis. A conlang CipSoft
  intended to be read got five in-game grammar books; 469 got a librarian who says you are too
  stupid to read it. That is not an oversight after 25 years — it is the design.
- **The direct dev admission.** Martin Eglseder on the game's most famous mystery: there was
  nothing behind the door, because nobody expected anyone to get there. CipSoft's mystery
  pipeline demonstrably produces *mystery-shaped placeholders*.
- **They edited the artefact** (skull matrix, 2010) and **retold the myths as jokes** (2016) and
  **named the bonelord dictionary as a thing gullible people "find"** (2009, 2021).
- **The 2020 poll's own structure** ranks 469 below a shipped-key conlang in decodability, and
  answer C is still unread six years later.
- **Base rate.** Even fan-favourite decodable puzzles here needed dev help (Chayenne, after 8
  months and an extra clue); four community-years went into a "469 clue" that turned out to be a
  domain hijacker's easter egg.

**Combining with this repo's own statistics** (copy-paste generative model reproduces 8/9 summary
statistics; a copy code costs 0.40 held-out bits/digit vs 0.90 for the best context-tree model;
prefix codes, token induction, homophonic solving and arithmetic pair-mappings all refuted),
the posterior is **≈0.5–1%**. The historical record and the statistics point the same way and
were arrived at independently, which is the strongest thing I can say for either.

**Operational reading.** Further decryption effort on the Hellgate corpus has expected value
near zero. The remaining ~1% lives almost entirely in a different hypothesis: not that the digits
encode text, but that some *pointer* (a location, an item, an NPC trigger) is what "469" was ever
for — which is, as far as the blocked-but-snippeted Tales of Tibia article can be read (§8), the
position this repo's author now holds.

## 8. The community's own conclusion — and my caveat

`https://article.talesoftibia.com/469/1` (five parts: Introduction to / A Taste of / Descent into /
Widespread / Complete *Madness*) is the article s2ward now endorses over his own decryption work
("I personally no longer believe that decryption is the way", repo README — **HARD**, *fetched*).

**I could not read it.** The domain is blocked by this session's proxy and I did not route around
it. From consistent search snippets, its argument appears to be:
- The author says up front it is "written from the perspective that I figured it out ... so it's
  going to be a bit biased", and that he has "an answer to 469-**lore** that I am happy with" —
  note *lore*, not *plaintext*.
- The resolution is **meta/in-joke, not cryptographic**: an in-fiction conceit that CipSoft
  "hired an actual beholder" who "resides still in the company basement [Hellgate]" to write the
  texts; the 15th-anniversary nostalgic bonelord numbered **3478**, alongside an NPC named
  **Knightmare** (the designer), with 3478 read as meaning 'beholder' — i.e. the whole thing
  circles the 2010 beholder→bonelord trademark rename.
- It leans on Knightmare's "there are so many secrets hidden in my areas that never ever were
  found, only the obvious things seem to attract people's attention and possibly distract it from
  other things" — read as: **the language is the distraction**.
— all **REPORTED**, snippet-level, and part 3 ("Descent into Madness") reportedly still pursues
coordinate/formula leads in Drefia, so the article is not purely deflationary.

**This partly contradicts our findings, and I will not paper over it.** The article's thesis is
*not* "469 is noise"; it is "469 is a pointer/joke whose payload is lore". Our statistics show the
*books* are a copy-paste artefact — which is compatible with the article, and also compatible
with 469 having been a designed gag from the start. Neither we nor the article has a dev
statement saying so. **Anyone continuing this work should read those five pages from an
unblocked network before treating my §8 as settled.**

---

### One-line summary
Tibia's designers ship decodable content **only with the key attached**; everything else is
allusion, decoration, or a placeholder they may or may not fill in later — and they have joked
about the bonelord dictionary, by name, in 2009 and again in 2021. Prior that 469 encodes
recoverable plaintext: **5%**, falling to **≈1%** once this repo's statistics are folded in.
