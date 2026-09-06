"""G4 -- independent provenance check of books.json against shipped game text.

`books.json` in this repo is a hand-collected transcription.  `s2ward/tibia`'s
`book_database.json` is an independent scrape of the in-game book text keyed by
library.  If the two agree the corpus is not a transcription artefact.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
from c469 import corpus  # noqa: E402


def hellgate() -> dict[str, str]:
    db = json.loads((REPO / "data" / "external" / "book_database.json")
                    .read_text(encoding="utf-8"))
    out = {}
    for b in db:
        if "Hellgate Library" in (b.get("libraries") or []):
            out[b["name"]] = re.sub(r"\D", "", b.get("text") or "")
    return out


def main() -> None:
    repo_books = list(corpus.load_books().books)
    ext = hellgate()
    print(f"books.json: {len(repo_books)} books, {sum(map(len, repo_books))} digits")
    print(f"book_database Hellgate Library: {len(ext)} books, "
          f"{sum(map(len, ext.values()))} digits")

    ext_set = set(ext.values())
    repo_set = set(repo_books)
    print(f"\nexact-match books: {len(repo_set & ext_set)}")
    only_repo = sorted(repo_set - ext_set, key=len)
    only_ext = sorted(ext_set - repo_set, key=len)
    print(f"only in books.json ({len(only_repo)}):")
    for b in only_repo:
        # nearest external book by containment
        near = [n for n, t in ext.items() if b in t or t in b]
        print(f"  len {len(b):4d} {b[:50]}...  containment-near: {near}")
    print(f"only in book_database ({len(only_ext)}):")
    for b in only_ext:
        name = next(n for n, t in ext.items() if t == b)
        near = [i for i, t in enumerate(repo_books) if b in t or t in b]
        print(f"  len {len(b):4d} {name:<14} {b[:40]}...  near repo idx: {near}")

    # duplicates inside the shipped data
    from collections import Counter
    dup = [t for t, c in Counter(ext.values()).items() if c > 1]
    print(f"\nduplicate texts inside book_database Hellgate: {len(dup)}")
    for t in dup:
        print("  ", [n for n, v in ext.items() if v == t], len(t))


if __name__ == "__main__":
    main()
