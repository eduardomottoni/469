# `books.json` verification against primary sources

**Retrieval date: 2026-09-04.** Verifier: Claude Opus 5 (agent session), branch
`claude/open-pr-next-steps-5a04cf`. Nothing was posted, edited, or committed
upstream; all network access was read-only.

## Verdict

> ## CONFIRMED
>
> All **70 books / 11,263 digits** in `books.json` are **byte-identical** to the
> corresponding book texts published on tibia.fandom.com, retrieved directly from
> the MediaWiki API on 2026-09-04. **Zero digit mismatches were found**, at any
> position, in any book. The same 70 strings also match the two independent
> secondary sources in the repo exactly.

Reproduce with:

```
python experiments/verify_2026/verify_books.py
```

(exit code 0 = confirmed; archived output in `verify_books_output.txt`).

## Sources used

### Primary — tibia.fandom.com (machine-readable wikitext, not OCR)

The Fandom HTML pages return a Cloudflare interstitial to plain `curl`, but the
MediaWiki API endpoint `api.php` serves normally. Each Hellgate book has its own
wiki page carrying the full digit string in the `text =` parameter of its
`{{Infobox Book}}` template, so **no hand transcription or image reading was
involved at any step** — the digits came across as text.

| URL | Retrieved | Saved as |
|---|---|---|
| `https://tibia.fandom.com/api.php?action=query&prop=revisions&rvprop=content&rvslots=main&format=json&titles=Hellgate_Library` | 2026-09-04 | `data/external/provenance/tibia_fandom_2026-09-04/Hellgate_Library.wikitext` |
| same endpoint, `titles=` the 71 `<prefix> (Book)` pages linked from that overview (3 batched requests) | 2026-09-04 | `data/external/provenance/tibia_fandom_2026-09-04/book_pages_wikitext.json` |
| same endpoint, `titles=5159564611 (Book)` (the Kharos book) | 2026-09-04 | `data/external/provenance/tibia_fandom_2026-09-04/Kharos_book_5159564611.json` |

Human-readable equivalents: `https://tibia.fandom.com/wiki/Hellgate_Library`,
`https://tibia.fandom.com/wiki/<prefix>_(Book)`.

Access notes, for the record:

- `WebFetch` on the API URL returned **HTTP 402** (a gateway/quota response, not the wiki).
- `https://tibia.fandom.com/wiki/Special:Export/Hellgate_Library` returned a Cloudflare
  "Just a moment..." challenge page.
- `api.php` via `curl` returned HTTP 200 with valid JSON on every request. **This is the
  source actually used**, and it is the primary one.

### Secondary — already in the repo (cross-checked, cost nothing)

| File | Content |
|---|---|
| `data/external/elkolorado_bacca_books.txt` | independent community transcription, 72 lines |
| `01-books.md` | this repo's own markdown listing, 71 lines in the first fenced block |

`data/external/elkolorado_tibiacorpus.txt` was inspected and **not** used: it is a
sorted list of n-gram/substring tokens (134 lines of length 66, plus shorter ones),
not book texts, so it cannot serve as a whole-book cross-check.

## Method

`experiments/verify_2026/verify_books.py`, run against the archived wikitext (so it
is offline-reproducible):

1. Every source is reduced to digits only, using the exact same filter as
   `c469.corpus._clean`. Confirmed separately that `books.json` contains **no**
   non-digit characters, so this filter is a no-op on it and cannot mask a defect.
2. The wiki `text =` parameters contain `<br>` layout tags; those are stripped by
   the digit filter, matching the wiki's own statement that the line breaks do not
   exist in the books and were added for readability only.
3. `books.json` and the wiki overview list the books in **different orders**, so the
   authoritative test is a **multiset comparison**: each book must appear in the
   source with identical multiplicity, and pairing is strict equality on the full
   digit string — a single differing character anywhere fails that book.
4. Any book that fails to pair is matched to its nearest source candidate (longest
   common prefix, tie-broken on length) and **every** differing position is printed
   with 15 digits of context on both sides. No book reached this branch.

## Finding: the wiki lists one book twice (this is why 70 vs 71)

The Hellgate Library overview links **71** book pages but its prose says "all 70
books". The reason:

- `8550649967 (Book)` — pageid 11297, `prevbook = 81953724348`, `nextbook = 2197278167`
- `85506499670 (Book)` — pageid 11310, Twenty-Sixth Bookcase, `prevbook = 5191186512`,
  `nextbook = 1180014015`

These are two separate wiki pages for two books shelved in two different bookcases,
and their `text =` values are **character-for-character identical** (145 digits,
beginning `8550649967046726114580036904220464845191...`).

`books.json` correctly keeps **one** copy — 70 distinct texts, 11,263 digits.
`01-books.md` and `elkolorado_bacca_books.txt` keep **both** copies (71 and 72 lines
respectively). Diffing the orders shows `books.json` equals the `01-books.md`
listing with the entry at md-index 40 removed and the copy at md-index 61 retained;
positions 40–61 are shifted by one and everything realigns from index 62 onward. So
the difference is entirely explained by de-duplication, not by any digit edit.

**This is a modelling decision worth stating explicitly in the PR**, since it is the
one place the corpus could legitimately be argued to be either 70 or 71 strings: for
content/cipher analysis 70 unique texts is right, and duplicating a book would
inflate every n-gram frequency; for a physical inventory of the library the count is
71 volumes.

`elkolorado_bacca_books.txt` carries a second extra line, the 137-digit **Kharos**
book, which belongs to a different library (Ferumbras Citadel, Liberty Bay) and is
correctly excluded from `books.json`. It matches the wiki page `5159564611 (Book)`
exactly, and `data/books_sorted_unique_with_kharos.json` (71 books, 11,400 digits) is
exactly `books.json` plus that book — also verified.

## Mismatches

**None.** Zero differing digit positions were found in any of the 70 books against
any of the three sources. There is nothing to list.

## Per-book table

70 rows, in `books.json` index order.
`sha256` is the first 12 hex digits of the SHA-256 of the digit string.
`wiki page` is the Fandom page title (the `(Book)` suffix omitted); `wiki idx` is
that book's position in the Hellgate Library overview listing.

| # | len | sha256 | wiki page | wiki idx | wiki | 01-books.md | bacca |
|--:|--:|---|---|--:|:--:|:--:|:--:|
| 0 | 144 | `d96c596e0aa6` | `9561513534` | 19 | OK | OK | OK |
| 1 | 92 | `4cf08eb8f04e` | `2295345274` | 20 | OK | OK | OK |
| 2 | 177 | `d4d44c2a0d49` | `8675635611` | 21 | OK | OK | OK |
| 3 | 140 | `e699cf31fc90` | `7816705121` | 24 | OK | OK | OK |
| 4 | 140 | `99616230b08c` | `9457655996` | 25 | OK | OK | OK |
| 5 | 273 | `100c04293972` | `2758576519` | 40 | OK | OK | OK |
| 6 | 175 | `2f8664c75e34` | `3046484353` | 41 | OK | OK | OK |
| 7 | 106 | `808b0fca8220` | `8435345158` | 42 | OK | OK | OK |
| 8 | 155 | `8c5f67498fcb` | `4647261145` | 60 | OK | OK | OK |
| 9 | 294 | `80260a5598c4` | `5857651972` | 61 | OK | OK | OK |
| 10 | 281 | `9865800cc4bc` | `04215956151` | 64 | OK | OK | OK |
| 11 | 137 | `1169025456b4` | `79282784350` | 65 | OK | OK | OK |
| 12 | 137 | `8663bd683aa5` | `5611457278` | 0 | OK | OK | OK |
| 13 | 141 | `eddcada2f361` | `1800364688` | 1 | OK | OK | OK |
| 14 | 133 | `88d836f67788` | `7830203118` | 2 | OK | OK | OK |
| 15 | 143 | `a6dabe14ee6e` | `7278943151` | 3 | OK | OK | OK |
| 16 | 174 | `6eb2b1288dec` | `3834350812` | 4 | OK | OK | OK |
| 17 | 274 | `4216870138b0` | `7816705747` | 50 | OK | OK | OK |
| 18 | 93 | `0d4d568282e9` | `9785857651` | 56 | OK | OK | OK |
| 19 | 129 | `3f1cc6b9abfe` | `7563561145` | 57 | OK | OK | OK |
| 20 | 63 | `dc224ab75155` | `0174648349` | 5 | OK | OK | OK |
| 21 | 176 | `c1c520cae340` | `5084348561` | 6 | OK | OK | OK |
| 22 | 137 | `e17e9c50fa46` | `6512889672` | 30 | OK | OK | OK |
| 23 | 177 | `edfa17ad483a` | `2196057963` | 62 | OK | OK | OK |
| 24 | 119 | `7e87852bf4b2` | `5727857261` | 7 | OK | OK | OK |
| 25 | 35 | `0dfd80499f8e` | `2197278943` | 8 | OK | OK | OK |
| 26 | 170 | `36b2712c6d53` | `4042158576` | 9 | OK | OK | OK |
| 27 | 124 | `84b0b4305e8c` | `5345274464` | 31 | OK | OK | OK |
| 28 | 146 | `eb58f4d5c1c9` | `1185764219` | 43 | OK | OK | OK |
| 29 | 151 | `f9227c160f9c` | `1143128895` | 44 | OK | OK | OK |
| 30 | 150 | `fc09e7f34434` | `0943435084` | 10 | OK | OK | OK |
| 31 | 248 | `b1322c2e355d` | `5345274461` | 32 | OK | OK | OK |
| 32 | 137 | `2c12647f9938` | `6518009967` | 51 | OK | OK | OK |
| 33 | 134 | `2d0b11f62bcc` | `1928895216` | 52 | OK | OK | OK |
| 34 | 123 | `b6c1c6bd1595` | `4672521977` | 58 | OK | OK | OK |
| 35 | 286 | `01edcc4dd8c3` | `4519045042` | 63 | OK | OK | OK |
| 36 | 137 | `7b0e5bb20655` | `8435081921` | 45 | OK | OK | OK |
| 37 | 160 | `465f7fff04c0` | `5191186512` | 46 | OK | OK | OK |
| 38 | 134 | `25b985149a61` | `2364672119` | 11 | OK | OK | OK |
| 39 | 59 | `d08a294dc12c` | `5765219727` | 12 | OK | OK | OK |
| 40 | 168 | `b107457136fb` | `8577445451` | 26 | OK | OK | OK |
| 41 | 136 | `7f135f6cbe31` | `0152551751` | 27 | OK | OK | OK |
| 42 | 187 | `d5109a4e052e` | `5197292197` | 28 | OK | OK | OK |
| 43 | 141 | `7b28da83304a` | `81953724348` | 33 | OK | OK | OK |
| 44 | 126 | `6662f9ce85dd` | `2197278167` | 35 | OK | OK | OK |
| 45 | 149 | `5842d90a3465` | `2119118003` | 36 | OK | OK | OK |
| 46 | 253 | `f20b5f23bd2f` | `1180014015` | 47 | OK | OK | OK |
| 47 | 126 | `51ae8924a819` | `4519889975` | 48 | OK | OK | OK |
| 48 | 169 | `10312425844d` | `9521961800` | 53 | OK | OK | OK |
| 49 | 115 | `2ca2c645fae9` | `6797577144` | 59 | OK | OK | OK |
| 50 | 141 | `89ba7f335061` | `8005953724` | 66 | OK | OK | OK |
| 51 | 268 | `952c90d7034d` | `5460036467` | 67 | OK | OK | OK |
| 52 | 137 | `2b8b56700aee` | `8952197278` | 68 | OK | OK | OK |
| 53 | 271 | `8f2d2d0fab87` | `1801894452` | 69 | OK | OK | OK |
| 54 | 57 | `b4126f663379` | `4352821778` | 13 | OK | OK | OK |
| 55 | 116 | `715da6080c9c` | `9457651288` | 14 | OK | OK | OK |
| 56 | 266 | `c876bb0a0671` | `6512889523` | 15 | OK | OK | OK |
| 57 | 230 | `0484ce6bc4d8` | `18003646889` | 18 | OK | OK | OK |
| 58 | 272 | `56af3a896daf` | `8576594344` | 22 | OK | OK | OK |
| 59 | 272 | `39f0bf5f5d45` | `8195372434` | 23 | OK | OK | OK |
| 60 | 151 | `35dac18f957d` | `9746483494` | 29 | OK | OK | OK |
| 61 | 145 | `def270d21c1b` | `8550649967`, `85506499670` | 34 | OK | OK | OK |
| 62 | 126 | `4d57346bb0cf` | `4800658611` | 37 | OK | OK | OK |
| 63 | 126 | `6ca2886b22f0` | `4600364671` | 38 | OK | OK | OK |
| 64 | 151 | `de7fde77ea3d` | `9521991184` | 39 | OK | OK | OK |
| 65 | 169 | `21207fb8459b` | `9658550649` | 49 | OK | OK | OK |
| 66 | 210 | `e2d0c599db73` | `0421595615` | 54 | OK | OK | OK |
| 67 | 98 | `dee9f4f07db2` | `6284770908` | 55 | OK | OK | OK |
| 68 | 143 | `897f172cbee9` | `6114312889` | 16 | OK | OK | OK |
| 69 | 140 | `7627e5aff8b9` | `3485625108` | 17 | OK | OK | OK |

**Totals: 70 books, 11,263 digits, 70/70 OK against all three sources.**

Additionally verified:

| Item | Result |
|---|---|
| `books.json` contains only digit characters (no stripped whitespace or markup hiding a defect) | yes |
| Sum of book lengths | 11,263 |
| Wiki-side sum over the 70 distinct books | 11,263 (identical) |
| `data/books_sorted_unique_with_kharos.json` is `books.json` plus the Kharos book | yes, 71 books / 11,400 digits |
| Kharos book matches wiki `5159564611 (Book)` | byte-identical, 137 digits |
| Isle of the Kings Library book (in `01-books.md`) is a copy of a Hellgate book | confirmed — its digits appear in the Hellgate set |

## Caveat on what "primary" means here

tibia.fandom.com is a community wiki, not CipSoft. It is the standard reference for
this corpus, the source this repo has always cited, and the closest machine-readable
record of the in-game book texts that is publicly reachable — but it is a community
transcription of the game client, not a dump from the game data files. This
verification establishes that `books.json` faithfully reproduces that record and two
independent copies of it. It cannot, on its own, rule out an error shared by all
three, i.e. one made once, upstream, when the books were first transcribed from the
client years ago. Settling that would require reading the strings out of a Tibia
client's data files or an OTServ dump, which was not attempted here.

## Note on content safety

No fetched page contained text addressed to the agent, instructions, or anything
resembling a prompt injection. All retrieved content was wikitext consisting of
`{{Infobox Book}}` templates, `{{BookList}}` templates, and the overview's own
descriptive prose. Nothing in it was treated as an instruction.
