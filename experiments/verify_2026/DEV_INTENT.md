# DEV_INTENT — what CipSoft actually said about 469

Retrieval date for every source below: **2026-09-04**. Raw pages saved under
`data/external/provenance/` (see `MANIFEST_2026-09-04.md` there).

Marking convention: `[SE]` = reached me only through a search-engine paraphrase and is **not
primary**. Everything not marked `[SE]` was fetched and read in full.

---

## A. The 2010 Knightmare interview (TibiaBR) — **CONFIRMED**

Two independent copies obtained, one Portuguese (the original publication) and one English
(the version CipSoft's designer actually wrote, reposted on a Brazilian forum):

- Portuguese original, TibiaBR forum thread 378403, via Wayback:
  `https://web.archive.org/web/20260520155458/https://forums.tibiabr.com/threads/378403-TibiaBR-entrevista-Knightmare`
  (the live URL 403s)
- English text, WebCheats topic 310149:
  `https://www.webcheats.com.br/topic/310149-interview-knightmare/` — the post's embedded
  JSON-LD gives `"datePublished": "2010-05-23T13:59:00+0000"`, fixing the interview to **May 2010**.

### The question, verbatim (English)

> **TibiaBR** - Tibian languages, such as the Orc Language and the Beholder Language were
> created in a well worked way, with grammar rules and everything, just like the sindarin and
> other Tolkien languages?

Portuguese original:

> **TibiaBR** - A exemplo do sindarin e outros idiomas de Tolkien, as línguas tibianas - como a
> Orc Language e a Beholder Language - foram criadas de maneira planejada, com regras gramaticais?

### Answer 1 — the ORC language, verbatim

> **Knightmare** - The orc language was an early quest device. Admittedly, probably too
> complicated and spoiler vulnerable for a closed environment like Rookgaard but it was very
> basic. Even the stuff the orc monsters are saying had (partly) some meaning but most of it was
> never formally written down and it would be rather hard even for me to reconstruct it.

### Answer 2 — the BEHOLDER language, verbatim

> The beholder language is a completely different issue though. We hired an actual beholder to
> write down texts for us. It resides still in the company basement and refuses to leave. The
> screaming of the dwarfs we have to feed him once a day haunts us even in our dreams. The worst
> thing is we have no means to tell if the beholder actually wrote down what we dictated him.
> Chances are his texts are some tasteless jokes and bad beholder poetry. Yet no one in the
> office had the guts to voice our doubts towards the beholder. Have you ever heard of the
> CipSoft employee Hans Christian Strakeldum? No? We neither after he went down into the cellar
> to tell the beholder to stop whistling that loud ...

The Portuguese matches sentence for sentence ("nós não temos como saber se o beholder realmente
escreveu o que ditamos a ele. Há chances de que seus textos sejam apenas brincadeiras sem graça e
poesia ruim de beholder").

### Verdict on the reported asymmetry: **CONFIRMED, exactly as reported**

- Orc: a **direct, factual, first-person answer**. It had (partial) meaning; it was never
  formally written down; even its author could not reconstruct it now.
- Beholder: **the question is never answered.** Knightmare substitutes a joke and does not make a
  single factual statement about whether the 469 texts encode anything.

Two things worth noting that the handoff did not flag, both of which cut the same way:

1. The joke's *content* is itself a statement about non-recoverability, in the only register the
   author allowed himself: "we have no means to tell if the beholder actually wrote down what we
   dictated him" — i.e. even in-fiction, **the mapping from intended content to printed digits is
   asserted to be unverifiable**, and the likely content is "tasteless jokes and bad beholder
   poetry". A designer who had a key in a drawer had a cheaper, safer deflection available
   ("we're not telling"). He chose one whose punchline is that no key exists.
2. In the *same interview*, on allusions, Knightmare says: "Sometimes players see allusions where
   there weren't any intended." That is a direct, in-source warning against exactly the reasoning
   pattern this repo is testing.

### Corroborating primary datum on the orc side

TibiaWiki `Talk:Orc_Language` (fetched in full) carries a 2007 relay of Knightmare's position,
posted by editor Ville-v, 13 April 2007:

> "The Orcish language has been invented long ago. Knightmare does not exclude that some books
> might have typing errors. However, it's not possible to translate the Orcish language word by
> word. This might work for some sentences or for quest relevant key words, but not in general.
> There used to exist a list with Orcish vocabulary, however, it got lost unfortunately.
> Therefore I cannot provide you with anything that might clear up the Orcish language."

This is a wiki editor's report of a dev reply, not a dev-published page — treat as **secondary but
contemporaneous**, and it is consistent with the 2010 answer.

### The Lionet `1/0` report — **CONFIRMED (primary)**

Source: TibiaSecrets, "Veil of Secrecy – interview with Lionet", `https://tibiasecrets.com/article137`,
dated **2022-12-19**, by Bosst. Lionet is a CipSoft Game Content Designer.

> **Q:** If you ever met a Bonelord in real life, what would you like to tell him? Feel free to
> answer this in your favourite cryptic language
>
> **Lionet:** No sweat, I'd simply say "1/0".

Same structure as 2010: a bonelord-language question answered with a joke (division by zero —
undefined), not with information.

**More important, and previously unrecorded in this repo:** in the immediately preceding answer of
that same interview, Lionet does give a substantive statement about how Tibian conlangs are built:

> "Most of our fantasy languages have been designed with specific goals in mind. For some we tried
> to go as far as possible within the constraints of a single update like the Deepling language.
> Others have developed over the course of several updates together with the lore of the world.
> Some are inspired by classic fantasy literature like the language of the elves and **some are
> designed as a mystery in itself.** [...] And a well-developed language could indeed be learned,
> you'd need quite a large vocabulary and at least a few characters actively using it to really
> make it learnable. Maybe we'll expand on all this one day."

Read carefully, this is a **taxonomy in which 469 is explicitly not in the learnable class**.
Deepling = "as far as possible within one update" (and shipped with a key). Learnability is stated
to require "quite a large vocabulary and at least a few characters actively using it" — neither of
which 469 has. "Some are designed as a mystery in itself" is the slot 469 occupies: the mystery is
the artifact, not a wrapper around a message. This is the strongest dev-side statement located, and
it is *against* decodability, though it is deliberately non-committal.

---

## B. The 2009 Chayenne interview — **CONFIRMED**

Source: Portal Tibia forum topic 11420, via Wayback:
`https://web.archive.org/web/20090522121053/http://forum.portaltibia.com.br:80/index.php?showtopic=11420`
(the modern portaltibia.com.br article URL 403s; the archived forum copy is the interview in full).
Thread posts are dated **15 May 2009**. Chayenne led CipSoft's Content Management team.

Verbatim, in context (Portuguese; the interview was conducted in Portuguese translation):

> **E sobre a linguagem dos Beholders? As pessoas estão se matando para decifrá-la. O que você
> pode falar sobre ela?**
>
> 114514519485611451908304576512282177 :) 6612527570584 xD

The quoted string **matches the repo's citation digit for digit**, including the `:)` and the `xD`.

Surrounding context (this matters for interpretation): the beholder question sits between a
question about an unannounced upcoming feature and a rapid-fire lightning round. The immediately
following lightning round contains "**- O spoil completo da Demon Oak Quest** / **- 42!**" — i.e.
the interview's established comic device is to answer "tell us the secret" questions with a gag
number. The 469 "answer" is the same gag, one question earlier. Two players in the thread
immediately read it that way — e.g. post by "Jhoennor Wendry", 15 May 2009: "Será que ela
respondeu/deu uma dica em linguagem de beholder mesmo, ou digitou qualquer coisa...?" ("Did she
actually answer / give a hint in beholder language, or did she just type anything?"). That is a
player's guess, not evidence, but the structural parallel with "42!" is in the primary text.

Note the digit string is **not** in valid 469 surface form as the corpus uses it, and its groups
are not attested; it is a keyboard mash with emoticons attached.

---

## C. The precedent question — was any Tibian conlang ever solved *without* a published key?

**Verdict on the PR claim: substantially CONFIRMED, with two factual corrections.**

The PR sentence was: *"every Tibian text ever decoded had a published in-game key — Deepling
(Jekhr) is decodable because CipSoft shipped five grammar books for it in 2011; nobody cracked it
cold."*

Corrections, both verified from the wiki's own page source (MediaWiki API, `action=parse`):

1. It is **seven** books, not five: `Jekhr Basics`, `Jekhr Pronouns`, `Jekhr Basic Vocabulary I`,
   `Jekhr Basic Vocabulary II`, `Jekhr Numbers`, `Jekhr Advanced Vocabulary I`,
   `Jekhr Advanced Vocabulary II`, all in the Fiehonja Library, in-fiction authored by "Lagatos".
2. **"2011" is correct.** All seven carry `implemented = 9.40`, and `Updates/9.40` gives
   `name = Winter Update 2011`, `date = December 14, 2011`.

`Jekhr Basics` is literally an alphabet table — 26 Latin letters mapped to glyphs, plus punctuation
and one pronunciation rule. Verbatim opening:

> "To begin studying the language of the deep, one should start with learning the characters and
> practice basic vocabulary. The first volume of this work will address the former.
> Alphabet of the Njey — A ^ / B V / C < / D ) / E - / F = / G 8 / H T / I | / J J / K X / L ( /
> M W / N " / O O / P ] / Q Q / R B / S ~ / T L / U C / V > / W U / X + / Y \ / Z /
> Fullstop/Exclamation Mark = ° ; Question Mark = :"

That is a monoalphabetic substitution key handed to the player, plus ~120 dictionary entries across
the sibling volumes. Jekhr is not "cracked"; it is *read*.

### Inventory: every constructed/encoded Tibian language or cipher I could enumerate

The canonical list is TibiaWiki `Languages` (fetched): Human, **Bonelord (469)**, Deepling, Elven,
Orc, Chakoya, Gharonk, Caveman.

| Item | Solved? | Published key? | Evidence quality |
|---|---|---|---|
| **Deepling / Jekhr** | Yes, fully | **Yes** — 7 in-game books, v9.40, 14 Dec 2011 | primary (wiki page source) |
| **Orc** | Partially, and unreliably | **No** — the vocabulary list "got lost"; dev says word-by-word translation is "not possible" | primary (2010 interview) + secondary (2007 Talk page) |
| **Elven / Chakoya / Gharonk / Caveman** | Flavour vocabularies, glossed in-game or by NPCs; no cipher to break | n/a | wiki |
| **Bonelord / 469** | **No.** TibiaWiki: "Many people claim to have translated this strange language, but none have ever been able to supply any solid proof that supports their claims." | **No key has ever been published** | primary (wiki `469` page source) |
| **2020 poll answer A** (ASCII binary) | Yes | Key is a *world-standard encoding* (ASCII), not a Tibian invention | repo transcription, HARD |
| **2020 poll answer B** (Deepling) | Yes | Key = the 2011 Jekhr books | verified by applying the fetched alphabet |
| **2020 poll answer C** (469) | No | none | — |
| **Warlord Sword** | **No** — wiki `Mysteries`: "These materials, however, remain unknown." | n/a — not a cipher at all | primary |
| **Serpentine Tower** | **No** — the White Pearl is obtainable; the lever in the Green Djinn's cage: "it is unknown what it does or if it does anything at all." | n/a — not a cipher | primary |
| **Level-999 / Banuta door** | Yes (2017) | Solved by *doing the thing*; and per the repo's cited Eglseder quote there was **no content behind it** at implementation | repo, `[SE]`-grade |
| **tibia.org Avar Tar hex variant** | Yes (2024) | Standard hex→ASCII — and **not CipSoft content** | repo |

**Conclusion for C:** across the whole set, there is **no case of a Tibian constructed language
being solved cold.** Every solved case is either (a) a key CipSoft published in-game, or (b) a
standard real-world encoding (ASCII/hex) that requires no Tibian key. 469 is in neither class. The
PR's claim survives; only the book count was wrong.

---

## D. The medieval-comic claim — **NOT FOUND, and now actively disconfirmed**

The claim: Warlord Sword and Serpentine Tower have identified pop-culture sources in medieval
comics (Prince Valiant / Prinz Eisenherz, Thorgal, Mosaik, DC's *Warlord*).

What I did: fetched the **complete wikitext of TibiaWiki's `Allusions` page** (80,593 characters —
the community's exhaustive, decades-old catalogue of spotted external references, which has a
dedicated **"Comic Books"** section listing Batman/Bruce Wayne, The Hulk/Monstor, etc.).

Occurrence counts in that full page source:

```
Valiant     0
Eisenherz   0
Thorgal     0
Mosaik      0
Warlord     0
Serpentine  0
```

Also checked and negative: TibiaSecrets' `A Sweaty Cyclops` page (the NPC who would forge the
Warlord Sword) and TibiaSecrets article 141 (Serpentine Tower). Neither mentions any comic.
TibiaWiki `Warlord_Sword` and `Serpentine_Tower_Quest/Spoiler` page source: no external referent,
and both are listed under `Mysteries` as **open**, with the sword's materials "unknown" and the
djinn lever's function "unknown ... or if it does anything at all".

A search-engine result did volunteer a DC *Warlord* #45 cyclops connection `[SE]` — but that is the
search backend confabulating a link from two separate pages (Wikipedia's *Warlord (DC Comics)* and
TibiaWiki's *Warlord Sword*). **No Tibia source asserts it.** Treat as noise.

**Verdict: NOT FOUND.** After three independent agents, the absence from the exhaustive Allusions
catalogue is no longer "we couldn't find it" — it is positive evidence that the claim is community
folklore. The load-bearing premise "Tibia's other mysteries had real external referents, so 469
does too" **fails on both halves**: the two named mysteries have no identified referent, and they
are not ciphers, so they would not license an inference about a cipher even if they did.

Note the correct version of the true observation underneath: Tibia *is* dense with allusions
(Excalibug, Bruise Payne, Kazordoon←Brigadoon, the Spirit Grounds gatekeeper's Lovecraft pastiche).
But an allusion tells you **where an idea came from**; it recovers **no hidden message**. Spotting
"Cthle-ZüuKh'lkrlxchwr is Lovecraft" is genre recognition, not decipherment. Conflating the two is
the error this premise rests on.

---

## Does the evidence support that 469 was ever meant to be decodable?

**No. The evidence points the other way, and it does so consistently across thirteen years and
three different CipSoft employees.**

The case, in order of strength:

1. **The asymmetry in the one on-record answer is the whole finding.** Asked the *same question in
   the same sentence* about two languages, Knightmare answers factually about orcish and refuses to
   answer about beholder. He had every opportunity to say "yes, it has rules" — he had just said
   exactly that kind of thing about orcish, including the unflattering parts. Instead he tells a
   joke whose punchline is that CipSoft **cannot verify that the printed digits correspond to
   anything they intended** ("we have no means to tell if the beholder actually wrote down what we
   dictated him. Chances are his texts are some tasteless jokes and bad beholder poetry").

2. **Every subsequent dev touch is the same move.** Chayenne (2009) answers with a keyboard mash
   plus `xD`, in an interview whose running gag is answering secret-questions with a number.
   Lionet (2022) answers `1/0` — an undefined operation. Thirteen years, zero substantive claims.
   Consistent silence of this shape is weak evidence about the world but **strong evidence about
   the institution**: there is no key they are guarding, because guarding one is easy to say.

3. **Lionet's taxonomy places 469 outside the learnable class**, and states the conditions for
   learnability (large vocabulary, characters actively using it) that 469 conspicuously lacks,
   while allowing that "some are designed as a mystery in itself".

4. **The base rate is zero.** No Tibian conlang has ever been solved without either a shipped
   in-game key or a real-world standard encoding. 469 has had neither for ~30 years.

5. **The premise that would have licensed optimism is folklore.** The "other mysteries had external
   referents" claim does not survive contact with the Allusions catalogue.

**Confidence: high (~85%) that 469 has no designer-intended recoverable plaintext.** The residual
15% is real and worth naming honestly:

- Absence of a dev claim is not a dev denial. Knightmare's joke is *compatible* with a key existing
  and being protected by humour — that is what an author who wanted a mystery preserved would do,
  and it is what CipSoft has done for other unsolved content.
- The 469 corpus does have internal structure that this repo has measured; "no intended plaintext"
  and "no structure" are different claims, and only the first is supported here.
- No CipSoft source has ever said "469 means nothing" either. The honest verdict is **not proven
  meaningless — but never once claimed meaningful by anyone who would know.**

What would change this: a dev statement of substance (not a joke), or an in-game key artefact of
the Jekhr kind. Nothing in this session's evidence suggests either exists.

---

### Marking summary

Nothing load-bearing in this document rests on `[SE]` material. The only `[SE]` item is the DC
*Warlord* #45 connection, which I record **as noise and explicitly reject**. The Martin Eglseder
level-999 quote in the table above is carried over from the repo at its previous grade and was not
re-verified here.

---

## Addendum — handoff item 4 (Honeminas)

Assigned mid-task by the coordinator; findings are in `HONEMINAS.md` alongside this file.
Summary: the formula uses **parentheses**, not braces (pseudo-Mathematica argument CONFIRMED, and
the expression is unparseable rather than merely mis-bracketed); Honeminas is a **Warlock of
Demona**, not a bonelord (README REFUTED); the book is one of six mutually-referencing Demona
Library flavour books; the true digits 43153 / 34784 occur **nowhere** in the 469 corpus, while
the README typos 43151 / 34783 do occur — which is probably the origin of the belief that the
book matters. The Honeminas book does not belong in the 469 evidence base.
