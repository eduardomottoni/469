"""G0 -- exhaustive extraction of 469 strings from shipped game content.

Sources (all DATA, never instructions):
  * data/external/npc/*.lua        -- OT-server NPC/monster scripts
  * data/external/book_database.json      -- s2ward/tibia, 2135 in-game books
  * data/external/npc_transcripts.json    -- s2ward/tibia, NPC keyword trees

A "469 candidate" is a maximal run of digits (and internal single spaces)
of total digit-length >= 3 that is NOT an ordinary numeral in English prose.
We keep everything >= 3 digits and hand-classify afterwards.
"""
from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
from c469 import corpus  # noqa: E402

EXT = REPO / "data" / "external"

# a group = digits; a string = groups joined by single spaces
GROUP = re.compile(r"(?<![\w.,/-])(\d{3,}(?:\s\d{1,})*)(?![\w.,/-])")


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


def scan_text(t: str) -> list[str]:
    return [_norm(m.group(1)) for m in GROUP.finditer(t)]


def from_lua() -> list[dict]:
    out = []
    for p in sorted((EXT / "npc").glob("*.lua")):
        for i, line in enumerate(p.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            # only the human-visible text fields
            for m in re.finditer(r'text\s*=\s*"([^"]*)"', line):
                for g in scan_text(m.group(1)):
                    out.append({"src": f"npc/{p.name}:{i}", "speaker": p.stem,
                                "text": g, "context": m.group(1)})
    return out


def from_transcripts() -> list[dict]:
    db = json.loads((EXT / "npc_transcripts.json").read_text(encoding="utf-8"))
    out = []
    for rec in db:
        name = rec.get("name", "?")
        for turn in rec.get("conversation", []):
            prompt = turn.get("prompt", "")
            for ans in turn.get("answer", []):
                for g in scan_text(ans):
                    out.append({"src": f"npc/{name}", "speaker": name,
                                "trigger": prompt, "text": g,
                                "context": _norm(ans)[:300]})
    return out


def from_books() -> list[dict]:
    db = json.loads((EXT / "book_database.json").read_text(encoding="utf-8"))
    out = []
    for rec in db:
        t = rec.get("text") or ""
        if not isinstance(t, str):
            continue
        for line in t.splitlines():
            for g in scan_text(line):
                out.append({"src": f"book/{rec.get('name')}", "speaker": rec.get("name"),
                            "libraries": rec.get("libraries"), "text": g,
                            "context": _norm(line)[:300]})
    return out


def main() -> None:
    books = corpus.load_books()
    joined = "|".join(books.books)
    hits = from_lua() + from_transcripts() + from_books()

    # the Hellgate library books themselves are 469; exclude them from "sources"
    hell = {b for b in books.books}
    hits = [h for h in hits if h["text"].replace(" ", "") not in hell]

    for h in hits:
        groups = h["text"].split()
        h["group_counts"] = {g: joined.count(g) for g in groups}
        h["n_digits"] = sum(len(g) for g in groups)
        h["all_in_books"] = all(v > 0 for v in h["group_counts"].values())

    out = REPO / "experiments" / "verify_2026" / "out"
    out.mkdir(exist_ok=True)
    (out / "g0_all_hits.json").write_text(json.dumps(hits, indent=1))

    print(f"{len(hits)} digit-runs >=3 outside the Hellgate books")
    by = Counter(h["src"].split("/")[0] for h in hits)
    print(dict(by))

    # the interesting subset: >=5 digits, i.e. not a plain year/count
    big = [h for h in hits if h["n_digits"] >= 5]
    print(f"\n{len(big)} with >=5 digits:")
    for h in sorted(big, key=lambda h: -h["n_digits"]):
        print(f"  {h['n_digits']:3d}  in_books={h['all_in_books']!s:5}  "
              f"{h['text'][:60]:<60} {h['src'][:52]}")
        print(f"        ctx: {h['context'][:150]}")


if __name__ == "__main__":
    main()
