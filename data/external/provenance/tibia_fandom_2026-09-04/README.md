# tibia.fandom.com raw wikitext archive — retrieved 2026-09-04

Retrieved read-only via the Fandom MediaWiki API with `curl`. The HTML pages return a
Cloudflare "Just a moment..." challenge and `WebFetch` returned HTTP 402, but
`api.php` served HTTP 200 JSON on every request.

Endpoint template:

```
https://tibia.fandom.com/api.php?action=query&prop=revisions&rvprop=content&rvslots=main&format=json&titles=<TITLE>
```

| File | Source page(s) | Human-readable URL |
|---|---|---|
| `Hellgate_Library.wikitext` | `Hellgate Library` | https://tibia.fandom.com/wiki/Hellgate_Library |
| `book_pages_wikitext.json` | the 71 `<prefix> (Book)` pages linked from that overview (3 batched requests, 25 titles each); JSON object mapping page title -> raw wikitext | https://tibia.fandom.com/wiki/<prefix>_(Book) |
| `Kharos_book_5159564611.json` | `5159564611 (Book)` — the Kharos / Ferumbras Citadel book; includes the extracted `text` value, the raw wikitext, the API URL and the retrieval date | https://tibia.fandom.com/wiki/5159564611_(Book) |

Each book page carries its full digit string in the `text =` parameter of the
`{{Infobox Book}}` template, with `<br>` tags used only as display line breaks (the
overview page states the line breaks do not exist in the books). No image reading or
hand transcription was involved.

Consumed by `experiments/verify_2026/verify_books.py`; see
`experiments/verify_2026/BOOKS_VERIFICATION.md` for the verification result.

Nothing was posted to or edited on the wiki.
