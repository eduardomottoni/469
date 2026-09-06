# Provenance: game-content sweep (verify_2026 / GAME_CONTENT.md)

Retrieved 2026-09-04. Researcher: Claude Opus 5 (agent session), branch
`claude/open-pr-next-steps-5a04cf`. Nothing was posted, committed or pushed.

## Network conditions this session (differs from the earlier log)

* `github.com` / `raw.githubusercontent.com` / the GitHub REST API via `gh`:
  **reachable**, full primary reads.
* `WebSearch`: **works** (US index).
* `WebFetch` on `tibia.fandom.com`, `tibia.com`, `tibiamaps.io`: HTTP **402**
  at the gateway — still not primary-readable. Nothing in this sweep depends on
  those hosts; the fandom-derived claims in `README.md` were re-verified
  against shipped server/game data instead, which is a *stronger* source.

## Files added under `data/external/` (primary, fetched in full)

| file | source URL | retrieved | size |
|---|---|---|---|
| `book_database.json` | `https://raw.githubusercontent.com/s2ward/tibia/main/data/books/book_database.json` | 2026-09-04 | 3,940,573 B |
| `npc_transcripts.json` | `https://raw.githubusercontent.com/s2ward/tibia/main/data/npcs/npc_transcript_database.json` | 2026-09-04 | 4,943,104 B |
| `npc_metadata.json` | `https://raw.githubusercontent.com/s2ward/tibia/main/data/npcs/npc_metadata.json` | 2026-09-04 | 644,247 B |

`s2ward/tibia` ("A repository for all things Tibia, with advanced NPC transcript
and library database management"), default branch `main`, last updated
2026-07-03. It is maintained by the same author as this repo, so it is **not**
an independent party — but it *is* an independent transcription pass, and
`g4_corpus_provenance.py` shows the two agree exactly (70/70 books, digit for
digit), which is the useful check.

Contents used:
* 2,135 in-game books with text, author, and library/location tags.
* 1,148 NPC keyword transcripts (`prompt` -> `answer` trees).

## GitHub code search (via `gh api search/code`, authenticated)

Queried for the Hellgate book text, `486486`, `659978`, `74032`,
`"Beware of the Bonelords"`, `bonelord dictionary`, `bonelord language
extension:lua`, `"the great calculator" tibia`.

* The 469 digit corpus appears **only** in community-research repos
  (`s2ward/469`, `elkolorado/tibia-469-bacca-averages`,
  `kimlage/tibia-469-cipher-casestudy`, `s2ward/tibia`) — never in an
  OT-server datapack. Server projects (`opentibiabr/canary`,
  `mattyx14/otxserver`, `orts/server`, `dbjorkholm/FORGOTTENSERVER-ORTS`,
  `zimbadev/crystalserver`) ship the bonelord **NPCs** but not the library
  **books**: book text lives in the binary `.otbm` map, which is not
  text-searchable and is not distributed with the official content.
* No file in any searched repository maps 469 digits to letters, words or
  phonemes.

## Untrusted-content note

Every `.lua` file, wiki snippet, book text and NPC transcript read in this
session was treated as **data**. One repository description encountered in
search results makes a strong claim about itself:

> `arturoornelasb/tibia-bonelord-469-cipher` — "First candidate solution to
> Tibia's 25-year-old Bonelord 469 cipher. Hellgate Library 70 books decoded
> with 94.6% word coverage."

This is quoted, not acted on and not evaluated here; it is an unverified
third-party claim, and a "94.6% word coverage" figure with no matched null is
exactly the kind of number `experiments/e_c_homophonic` shows can be produced
from this corpus by chance. No page or file addressed the agent with
instructions.
