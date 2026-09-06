#!/usr/bin/env python3
"""Digit-by-digit verification of books.json against primary and secondary sources.

PRIMARY SOURCE
--------------
tibia.fandom.com MediaWiki API (`api.php`, `action=query&prop=revisions&rvslots=main`),
retrieved 2026-09-04.  The Hellgate Library overview page links to 71 individual
`<prefix> (Book)` pages (70 distinct books; one book is listed twice under two page
titles).  Each page carries the complete digit string in the `text =` parameter of
its `{{Infobox Book}}` template -- i.e. the digits are machine-readable wikitext,
not something transcribed from an image.

The raw wikitext of every page fetched is archived under
    data/external/provenance/tibia_fandom_2026-09-04/
so this script runs fully offline and is reproducible.

SECONDARY SOURCES
-----------------
* data/external/elkolorado_bacca_books.txt -- independent community transcription.
* 01-books.md                              -- this repo's own markdown listing.

METHOD
------
Every source is reduced to digits only (identical to `c469.corpus._clean`).
`books.json` is a *set* of books; the wiki overview and books.json use different
orderings, so the authoritative test is a multiset comparison: every book in
books.json must appear in the source and vice versa, with identical multiplicity.
For books that do pair up, the comparison is a strict `==` on the digit string --
one differing character anywhere fails.  Books that fail to pair are then matched
to their nearest source book by length + longest common prefix, and the exact
differing positions are printed with surrounding context.

Usage:
    python experiments/verify_2026/verify_books.py [--json]
Exit code 0 = CONFIRMED, 1 = mismatches found.
"""
from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
PROV = REPO / "data" / "external" / "provenance" / "tibia_fandom_2026-09-04"
BOOKS_JSON = REPO / "books.json"
KHAROS_JSON = REPO / "data" / "books_sorted_unique_with_kharos.json"
BACCA = REPO / "data" / "external" / "elkolorado_bacca_books.txt"
BOOKS_MD = REPO / "01-books.md"

DIGITS = set("0123456789")

_TEXT_PARAM = re.compile(r"^\|\s*text\s*=\s*(.*?)(?=^\|\s*\w+\s*=|^\}\})", re.S | re.M)
_BOOK_LINK = re.compile(r"\|\s*(\d+ \(Book\))")


def clean(s: str) -> str:
    """Reduce to digits only -- identical to c469.corpus._clean."""
    return "".join(c for c in s if c in DIGITS)


# --------------------------------------------------------------------------- sources

def load_wiki() -> tuple[list[str], list[str], list[tuple[str, str, int]]]:
    """Return (unique page titles, digit strings, duplicate-page pairs)."""
    overview = (PROV / "Hellgate_Library.wikitext").read_text(encoding="utf-8")
    titles = _BOOK_LINK.findall(overview)
    pages = json.loads((PROV / "book_pages_wikitext.json").read_text(encoding="utf-8"))
    seen: dict[str, str] = {}
    u_titles, u_digits, dupes = [], [], []
    for t in titles:
        m = _TEXT_PARAM.search(pages[t])
        if not m:
            raise SystemExit(f"no `text =` parameter on wiki page {t!r}")
        d = clean(m.group(1))
        if d in seen:
            dupes.append((seen[d], t, len(d)))
        else:
            seen[d] = t
            u_titles.append(t)
            u_digits.append(d)
    return u_titles, u_digits, dupes


def load_books_md() -> list[str]:
    """The Hellgate code block of 01-books.md (first fenced block)."""
    txt = BOOKS_MD.read_text(encoding="utf-8")
    block = txt.split("```")[1]
    return [clean(l) for l in block.splitlines() if clean(l)]


# --------------------------------------------------------------------------- diffing

def diff_positions(a: str, b: str) -> list[tuple[int, str, str]]:
    return [(i, a[i] if i < len(a) else "", b[i] if i < len(b) else "")
            for i in range(max(len(a), len(b)))
            if (a[i] if i < len(a) else "") != (b[i] if i < len(b) else "")]


def context(s: str, i: int, w: int = 15) -> str:
    lo, hi = max(0, i - w), min(len(s), i + w + 1)
    return ("..." if lo else "") + s[lo:hi] + ("..." if hi < len(s) else "")


def common_prefix(a: str, b: str) -> int:
    n = 0
    for x, y in zip(a, b):
        if x != y:
            break
        n += 1
    return n


def nearest(book: str, pool: list[str]) -> str | None:
    """Best candidate partner for an unmatched book (longest common prefix,
    tie-broken by closest length)."""
    if not pool:
        return None
    return max(pool, key=lambda c: (common_prefix(book, c), -abs(len(c) - len(book))))


# --------------------------------------------------------------------------- compare

def compare(name_a: str, books_a: list[str], name_b: str, books_b: list[str]) -> dict:
    ca, cb = Counter(books_a), Counter(books_b)
    only_a = list((ca - cb).elements())
    only_b = list((cb - ca).elements())
    matched = sum((ca & cb).values())

    # positional map: where does each books_a entry sit in books_b?
    pos_in_b: dict[str, list[int]] = {}
    for i, b in enumerate(books_b):
        pos_in_b.setdefault(b, []).append(i)
    order = []
    used: Counter = Counter()
    for i, a in enumerate(books_a):
        idxs = pos_in_b.get(a, [])
        k = used[a]
        order.append(idxs[k] if k < len(idxs) else None)
        used[a] += 1

    mismatches = []
    pool = list(only_b)
    for a in only_a:
        n = nearest(a, pool)
        if n is not None:
            pool.remove(n)
        mismatches.append({
            "a": a, "b": n,
            "len_a": len(a), "len_b": len(n) if n else None,
            "diffs": diff_positions(a, n) if n else None,
            "index_a": books_a.index(a),
        })

    return {
        "name_a": name_a, "name_b": name_b,
        "n_a": len(books_a), "n_b": len(books_b),
        "digits_a": sum(map(len, books_a)), "digits_b": sum(map(len, books_b)),
        "matched_exactly": matched,
        "only_a": only_a, "only_b": only_b,
        "mismatches": mismatches,
        "order": order,
        "same_order": order == list(range(len(books_a))) and len(books_a) == len(books_b),
        "identical_content": not only_a and not only_b,
    }


def report(r: dict) -> bool:
    A, B = r["name_a"], r["name_b"]
    print(f"\n{'-' * 72}\n{A}   vs   {B}\n{'-' * 72}")
    print(f"  books                 : {r['n_a']} vs {r['n_b']}")
    print(f"  digits                : {r['digits_a']} vs {r['digits_b']}")
    print(f"  exact string matches  : {r['matched_exactly']} / {r['n_a']}")
    print(f"  same order            : {r['same_order']}")

    if r["identical_content"]:
        print(f"  RESULT: every one of the {r['n_a']} books in {A} is byte-identical to a "
              f"book in {B}\n          and vice versa (multiset equality)."
              + ("" if r["same_order"] else
                 f"\n          The two sources list them in DIFFERENT ORDER "
                 f"(content unaffected)."))
        return True

    if r["only_a"]:
        print(f"\n  !! {len(r['only_a'])} book(s) in {A} with no counterpart in {B}:")
    for m in r["mismatches"]:
        print(f"\n  [{A} index {m['index_a']}] length {m['len_a']}"
              f" vs nearest {B} book length {m['len_b']}")
        if m["b"] is None:
            print(f"    no candidate in {B} at all")
            print(f"    {A}: {m['a']}")
            continue
        print(f"    {len(m['diffs'])} differing position(s)")
        for pos, x, y in m["diffs"][:40]:
            print(f"      pos {pos:>4}: {A}={x or '<end of string>'}  "
                  f"{B}={y or '<end of string>'}")
            print(f"        {A}: {context(m['a'], pos)}")
            print(f"        {B}: {context(m['b'], pos)}")
        if len(m["diffs"]) > 40:
            print(f"      ... and {len(m['diffs']) - 40} more")

    extra = [b for b in r["only_b"] if b not in [m["b"] for m in r["mismatches"]]]
    if extra:
        print(f"\n  {len(extra)} book(s) present ONLY in {B} (not in {A}):")
        for e in extra:
            print(f"    len {len(e)}: {e}")
    return False


# --------------------------------------------------------------------------- main

def main() -> int:
    print("=" * 72)
    print("469 CORPUS VERIFICATION")
    print("books.json (70 books, 11263 digits) vs primary + secondary sources")
    print("primary: tibia.fandom.com api.php, retrieved 2026-09-04")
    print("=" * 72)

    wiki_titles, wiki_books, dupes = load_wiki()
    print(f"\nWiki: Hellgate Library overview links {len(wiki_titles) + len(dupes)} "
          f"book pages -> {len(wiki_books)} distinct digit strings, "
          f"{sum(map(len, wiki_books))} digits.")
    for a, b, n in dupes:
        print(f"  NOTE: pages {a!r} and {b!r} carry the SAME {n} digits "
              f"(the wiki lists one book twice; the page text says '70 books').")

    repo_books = [clean(x) for x in json.loads(BOOKS_JSON.read_text())]
    md_books = load_books_md()
    bacca = [clean(l) for l in BACCA.read_text().splitlines() if clean(l)]

    results = {
        "wiki": compare("books.json", repo_books, "tibia.fandom (PRIMARY)", wiki_books),
        "md": compare("books.json", repo_books, "01-books.md", md_books),
        "bacca": compare("books.json", repo_books, "elkolorado_bacca", bacca),
    }
    ok = {k: report(v) for k, v in results.items()}
    # The secondary sources keep the duplicated Hellgate book (and bacca also keeps
    # the Kharos book).  What matters is that nothing in books.json is unaccounted
    # for, and that every extra is one of those two known strings.
    dup_digits = {d for _, _, _ in dupes} if False else set()
    dupe_string = None
    if dupes:
        # recover the digits of the duplicated book
        for i, t in enumerate(wiki_titles):
            if t == dupes[0][0]:
                dupe_string = wiki_books[i]
    kharos_string = None
    kp = PROV / "Kharos_book_5159564611.json"
    if kp.exists():
        kharos_string = clean(json.loads(kp.read_text(encoding="utf-8"))["text"])
    known_extras = {s for s in (dupe_string, kharos_string) if s}
    for key in ("md", "bacca"):
        r = results[key]
        r["extras_all_known"] = (not r["only_a"]) and set(r["only_b"]) <= known_extras
        ok[key] = r["matched_exactly"] == r["n_a"] and r["extras_all_known"]

    # ---- bacca carries extras; that is expected, report them explicitly
    print(f"\n{'-' * 72}\nnote on elkolorado_bacca extras\n{'-' * 72}")
    for e in results["bacca"]["only_b"]:
        print(f"  len {len(e)}: {e[:70]}...")
    print("  (expected: the duplicated 145-digit Hellgate book + the Kharos book)")

    # ---- Kharos corpus
    if KHAROS_JSON.exists():
        kh = [clean(x) for x in json.loads(KHAROS_JSON.read_text())]
        kharos_wiki = clean(json.loads(
            (PROV / "Kharos_book_5159564611.json").read_text(encoding="utf-8")
        )["text"]) if (PROV / "Kharos_book_5159564611.json").exists() else None
        extra = [b for b in kh if b not in repo_books]
        print(f"\n{'-' * 72}\n{KHAROS_JSON.name}\n{'-' * 72}")
        print(f"  {len(kh)} books, {sum(map(len, kh))} digits; "
              f"{len(extra)} not present in books.json")
        for e in extra:
            tag = ""
            if kharos_wiki is not None:
                tag = "  <- matches wiki '5159564611 (Book)' EXACTLY" if e == kharos_wiki \
                      else "  <- DOES NOT match the wiki Kharos book"
            print(f"    len {len(e)}: {e}{tag}")
        c1, c2 = Counter(kh), Counter(repo_books)
        print(f"  books.json is a subset of the with_kharos file: {not (c2 - c1)}")

    print("\n" + "=" * 72)
    all_ok = ok["wiki"] and ok["md"] and ok["bacca"]
    print("VERDICT: " + ("CONFIRMED" if all_ok else "MISMATCHES FOUND"))
    print(f"  70/70 books byte-identical to tibia.fandom.com (PRIMARY) : {ok['wiki']}")
    print(f"  70/70 books byte-identical to 01-books.md                : {ok['md']}")
    print(f"  70/70 books byte-identical to elkolorado_bacca            : {ok['bacca']}")
    print(f"  digits verified                                          : "
          f"{results['wiki']['digits_a']}")
    print("  known, expected extras in secondary sources: the one Hellgate book that")
    print("  the wiki lists twice (145 digits, two bookcases, identical text) and the")
    print("  Kharos book (137 digits, a different library).")
    print("=" * 72)

    if "--json" in sys.argv:
        (Path(__file__).parent / "verify_books_result.json").write_text(
            json.dumps(results, indent=1))
    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
