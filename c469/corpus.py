"""Loaders for every 469 data source in this repo.

Each loader returns a frozen dataclass carrying a `provenance` string so that a
Result can always say which bytes it was computed from.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

DIGITS = "0123456789"


@dataclass(frozen=True)
class Corpus:
    books: tuple[str, ...]
    provenance: str
    labels: tuple[str, ...] = field(default=())

    @property
    def concat(self) -> str:
        return "".join(self.books)

    @property
    def n_digits(self) -> int:
        return sum(len(b) for b in self.books)

    def __len__(self) -> int:
        return len(self.books)


def _clean(s: str) -> str:
    return "".join(c for c in s if c in DIGITS)


def load_books(with_kharos: bool = False) -> Corpus:
    """The 70 Hellgate books, optionally plus the Kharos book (71)."""
    if with_kharos:
        p = REPO / "data" / "books_sorted_unique_with_kharos.json"
    else:
        p = REPO / "books.json"
    raw = json.loads(p.read_text())
    books = tuple(_clean(b) for b in raw)
    assert all(books), "empty book after cleaning"
    return Corpus(books, provenance=str(p.relative_to(REPO)),
                  labels=tuple(f"B{i}" for i in range(len(books))))


def load_contigs(name: str | None = None) -> Corpus:
    """Contigs produced by the prior author's greedy assembler."""
    d = REPO / "try_combine_books" / "out" / "books"
    files = sorted(d.glob("*.txt"))
    if not files:
        raise FileNotFoundError(f"no contig files under {d}")
    if name is None:
        # default: the best published assembly, 49 books into one 6624-digit strand
        cand = [f for f in files if "#2_6624" in f.name]
        p = cand[0] if cand else files[0]
    else:
        p = d / name
    parts = tuple(_clean(x) for x in p.read_text().split() if _clean(x))
    return Corpus(parts, provenance=str(p.relative_to(REPO)),
                  labels=tuple(f"C{i}" for i in range(len(parts))))


def load_alignments() -> list[dict]:
    """The 2415 precomputed pairwise alignments (Biopython globalms)."""
    p = REPO / "dna_alignment_analysis" / "alignment_data.json"
    return json.loads(p.read_text())


_LABEL = re.compile(r"^\[B\s*\d+[A-Z]?\s*\]")
_BRACKET = re.compile(r"\[[^\]]*\]")


def parse_align_txt(path: str | Path) -> list[tuple[str, int, str]]:
    """Parse a hand-drawn alignment canvas (04-align.txt / 05-rearrange.txt).

    Returns (label, column_offset, digits) per annotated row.  Conventions per
    the files' own headers: tabs are layout, `+` runs are inserted gaps, `[...]`
    are bookkeeping tags occupying width, ` -- ` starts a trailing comment.
    """
    p = Path(path)
    if not p.is_absolute():
        p = REPO / p
    out: list[tuple[str, int, str]] = []
    for line in p.read_text(errors="replace").splitlines():
        line = line.expandtabs(4)
        m = _LABEL.match(line)
        if not m:
            continue
        label = m.group(0).strip("[] ")
        line = " " * len(m.group(0)) + line[m.end():]
        line = line.split(" -- ")[0]
        # blank bracket tags in place, preserving column width
        line = _BRACKET.sub(lambda mm: " " * len(mm.group(0)), line)
        line = line.replace("+", " ")
        digits = _clean(line)
        if not digits:
            continue
        col = next(i for i, c in enumerate(line) if c in DIGITS)
        out.append((label, col, digits))
    return out


def dedup_core(corpus: Corpus, k: int = 25, max_covered: float = 0.5) -> Corpus:
    """Greedy removal of books that are mostly repeats of already-kept material.

    Local structure that survives this is a property of the code, not of the
    corpus's heavy copy-paste redundancy.
    """
    seen: set[str] = set()
    kept, labels = [], []
    order = sorted(range(len(corpus.books)), key=lambda i: -len(corpus.books[i]))
    for i in order:
        b = corpus.books[i]
        grams = [b[j:j + k] for j in range(len(b) - k + 1)]
        if not grams:
            continue
        covered = sum(g in seen for g in grams) / len(grams)
        if covered <= max_covered:
            kept.append(b)
            labels.append(corpus.labels[i] if corpus.labels else f"B{i}")
        seen.update(grams)
    return Corpus(tuple(kept), provenance=f"{corpus.provenance}|dedup_core(k={k})",
                  labels=tuple(labels))
