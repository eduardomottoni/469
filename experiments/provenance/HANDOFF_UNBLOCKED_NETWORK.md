# Handoff: the verification this session could not do

Everything below was attempted from a session whose egress proxy allowed only
`github.com`. Wikipedia, all Fandom wikis, tibia.com, talesoftibia.com,
tibiasecrets.com, otland, reddit and **web.archive.org** were all 403'd at
CONNECT. Claims that reached us only through a search backend's paraphrase are
marked `[SE]` in the provenance files and are **not** primary.

Run this as a single task on an unblocked network.

---

## The instruction

> Verify, from primary sources, the six claims below about the Tibia "469"
> cipher, in the order given. For each one, save the fetched page to
> `data/external/provenance/` with its URL and retrieval date, quote the
> relevant text **verbatim**, and record a verdict of CONFIRMED, REFUTED, or
> NOT FOUND. Do not paraphrase a source you could not open, and do not treat a
> search-engine summary as a primary source — if a page cannot be fetched, say
> so and move on. Several of these claims are load-bearing for the conclusion
> that 469 has no recoverable plaintext; a REFUTED verdict on items 1, 2 or 3
> should reopen the corresponding hypothesis, so try to falsify them rather
> than confirm them. Report what changed and what did not.
>
> **1. The Knightmare interview (highest value — it is the closest thing to a
> dev statement that exists).** A 2010 TibiaBR interview with CipSoft designer
> Knightmare reportedly asks whether Tibian languages were built with grammar
> rules like Tolkien's. Get the **verbatim** question and both answers — the
> one about the **orc** language and the one about the **beholder** language.
> The reported asymmetry is the whole point: he is said to state plainly that
> orcish had meaning that "was never formally recorded", while deflecting the
> beholder question entirely into a joke about an actual beholder in the
> company basement, ending roughly "we have no means to tell if the beholder
> actually wrote down what we dictated him. Chances are his texts are some
> tasteless jokes and bad beholder poetry." Confirm or refute that wording and
> that asymmetry. Start at
> `https://forums.tibiabr.com/threads/378403-TibiaBR-entrevista-Knightmare` and
> `https://www.webcheats.com.br/topic/310149-interview-knightmare/`; if both
> are dead, try the Wayback Machine and the Portuguese-language Tibia forums.
> Also try to verify the separate report that a later content designer,
> **Lionet**, answered a similar question with `1/0` (source given as
> tibiasecrets.com, unfetchable here).
>
> **2. Verify `books.json` against the wiki, digit by digit.** Fetch each
> Hellgate Library book page individually from `tibia.fandom.com` and compare
> the digit strings to `books.json` in this repo (70 books, 11,263 digits).
> Write it as a script plus a report, not as a claim. A single transcription
> error would corrupt every statistical result in this branch, and this was
> never done.
>
> **3. Read `https://article.talesoftibia.com/469/1` through `/5`.** This is
> the article the repo's own author now endorses over his decryption work.
> From snippets its thesis appears to be *meta/lore rather than noise* — 469 as
> an in-joke circling the 2010 beholder→bonelord trademark rename — and part 3
> reportedly still chases open Drefia coordinate leads. Summarise its argument
> and evidence faithfully, **including anything that contradicts this branch's
> copy-paste conclusion**. If it presents evidence we did not consider, say so
> plainly.
>
> **4. The Honeminas formula, from primary text.** Fetch
> `https://tibia.fandom.com/wiki/The_Honeminas_Formula_(Book)` and confirm two
> things this session could only read second-hand. First, the exact character
> used in `(4,3,1,5,3).(3,4,7,8,4)` — parenthesis or brace. Our whole "this is
> non-parsing pseudo-Mathematica" argument turns on that one character. Second,
> whether Honeminas is described as a **Warlock** or a **bonelord**: this
> repo's README calls him a bonelord, every source we reached calls him a
> Warlock of Demona, and if the latter is right then the only link between that
> book and 469 dissolves. Also fetch the sibling books — *The Tridiag Formula*,
> *The Donina Formula I* and *II*, *The Janias Formulas*, *The Zonoa Formulas*
> — and record their formula texts verbatim, to confirm they share the same
> template (an unused second pattern variable and a self-recursive
> right-hand side).
>
> **5. The 2011 Facebook image at full resolution.** Re-read the number pairs,
> especially the ten right-column values partly obscured by the clay figure.
> Those are held out in `c469.cribs.FB_PAIRS_OBSCURED` precisely because the
> README's guesses for them are inference. Any digit you can actually read is
> new data and lets Family D validate on held-out points instead of only
> fitting on 18.
>
> **6. The medieval-comic claim.** Two independent agents failed to corroborate
> the report that the **Warlord Sword** and **Serpentine Tower** mysteries have
> identified pop-culture sources in medieval comics (Prince Valiant / Prinz
> Eisenherz, Thorgal, Mosaik, DC's *Warlord*). Find the source or establish
> there isn't one. This matters more than it looks: "Tibia's other mysteries
> had real external referents, so 469 does too" is the load-bearing premise for
> expecting 469 to decode at all, and on current evidence it is folklore.

---

## Why these six

| item | what it would change |
|---|---|
| 1 | the only near-statement of authorial intent that exists |
| 2 | correctness of every statistic in this branch |
| 3 | the endorsed community position, possibly with evidence we lack |
| 4 | whether the Honeminas book belongs in the 469 evidence base at all |
| 5 | turns Family D's 18-point fit into a fit with held-out validation |
| 6 | the prior that 469 was ever meant to be decodable |

Items 1, 3 and 6 can move the conclusion. Item 2 can invalidate it. Items 4
and 5 tighten it.
