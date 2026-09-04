# Provenance research — source log

Retrieval date: **2026-09-04**. Researcher: Claude Opus 5 (agent session), branch `claude/cypher-solving-agents-hqnbq7`.

## IMPORTANT METHODOLOGICAL LIMITATION — READ BEFORE TRUSTING ANYTHING HERE

This session's network egress proxy allowed **only github.com / raw.githubusercontent.com**.
Every other host returned HTTP 403 at the CONNECT stage, including:

    en.wikipedia.org, tibia.com, tibia.fandom.com, forgottenrealms.fandom.com,
    tibiawiki.com.br, tibiasecrets.com, talesoftibia.com, article.talesoftibia.com,
    otland.net, reddit.com, forums.xenobot.net, forumarchive.xenobot.net,
    web.archive.org / archive.org, dtdnd.neocities.org, dnd-wiki.org, enworld.org,
    dumpstatadventures.com, completecompendium.com, duckduckgo.com, google.com, r.jina.ai

Verified with both WebFetch and `curl` (see proxy status endpoint `recentRelayFailures`).

**Consequence: I could not fetch or save a single primary source page.** Everything below
arrived as *search-engine-mediated extraction* — the WebSearch backend read the page and
paraphrased/quoted it back to me. That is one uncontrolled paraphrase step away from the
primary text. Quotes marked `[SE]` below are search-engine-reported quotes, NOT verified
transcriptions. **Anyone continuing this work from a machine with normal web access should
re-verify every `[SE]` quote against the source URL before relying on it.**

Per repo policy nothing was hand-transcribed from images; no digit strings were copied.

## URLs referenced, with what they were used for

| URL | Used for | Fetched? |
|---|---|---|
| https://forums.tibiabr.com/threads/378403-TibiaBR-entrevista-Knightmare | 2010 Knightmare interview; the beholder-language answer | NO (403) — [SE] only |
| https://www.tibiasecrets.com/article75 | Knightmare / TibiaHispano interview on hidden secrets | NO (403) — [SE] only |
| https://tibia.fandom.com/wiki/Allusions | Catalogue of Tibia's external references | NO (403) — [SE] only |
| https://tibia.fandom.com/wiki/Bonelord | Beholder→Bonelord rename, 2010-08-23 | NO (403) — [SE] only |
| https://www.tibiaqa.com/10125/why-cipsoft-changed-beholder-name-to-bonelord | Rename + WotC product-identity reason | NO (403) — [SE] only |
| https://forgottenrealms.fandom.com/wiki/Beholder_language | D&D beholder language "Quevquel" | NO (403) — [SE] only |
| https://forgottenrealms.fandom.com/wiki/Spectator , https://www.dndbeyond.com/monsters/17094-spectator | Spectator = 4 eyestalks + 1 central eye = 5 eyes | NO (403) — [SE] only |
| https://en.wikipedia.org/wiki/Royal_Vale_Heath , https://en.wikipedia.org/wiki/Donald_in_Mathmagic_Land , https://en.wikipedia.org/wiki/Mathemagician | Etymology of "mathemagic" | NO (403) — [SE] only |
| https://github.com/glrodasz/serpentine-tower-quest (README fetched via raw.githubusercontent.com) | Serpentine Tower community research record | **YES** — the only page actually retrieved |
| https://article.talesoftibia.com/469/1/ , https://tibiasecrets.com/article160 | Modern 469 write-ups | NO (403) — [SE] only |
| https://forumarchive.xenobot.net/archive/index.php/t-7529.html | Old 469 discussion | NO (403) — [SE] only |

## The one page actually retrieved

`https://raw.githubusercontent.com/glrodasz/serpentine-tower-quest/master/README.md`
(retrieved 2026-09-04). Community research notes on the Serpentine Tower. It cites only
generic real-world serpent-symbolism material (a Wikipedia serpent-symbolism article and a
Gary Osborn "Serpent-Grail" manuscript), attributed to a user "Thascius", **as community
speculation**. It contains **no CipSoft confirmation** and **no comic-book source**.
