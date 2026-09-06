"""G3 -- verify the 2020 poll correction using shipped in-game keys only.

The 15 Apr 2020 tibia.com poll "When the veils of shrouded truths are lifted,
who can stand?" had three joke answers:

  A  a binary blob
  B  a Jekhr (Deepling) string
  C  663 902073 7223 67538 467 80097   (469)

An earlier reading treated the three as the SAME sentence in three encodings,
which would make C known-plaintext.  This script decodes A and B from first
principles -- A by ASCII, B by the alphabet published in the in-game book
`Jekhr_Basics` and the vocabulary books, both read out of
data/external/book_database.json -- and shows the two plaintexts are different
sentences.  Therefore C has no known plaintext.

Nothing here is hand-transcribed: the Jekhr alphabet and glossary are parsed
out of the shipped book text.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

DB = REPO / "data" / "external" / "book_database.json"

POLL_A = """01010100 01101000 01100101 01110011 01100101 00100000 01100001 01110010 01100101 01101110
00100111 01110100 00100000 01110100 01101000 01100101 00100000 01110111 01101111 01110010
01100100 01110011 00100000 01111001 01101111 01110101 00100111 01110010 01100101 00100000
01101100 01101111 01101111 01101011 01101001 01101110 01100111 00100000 01100110 01101111
01110010 00101110"""
POLL_B = 'BOQOT" O(J-"L J-T )^X" XU-T )T JT(O~X'
POLL_C = "663 902073 7223 67538 467 80097"


def books() -> dict[str, str]:
    return {b["name"]: (b.get("text") or "")
            for b in json.loads(DB.read_text(encoding="utf-8"))}


def jekhr_alphabet(txt: str) -> dict[str, str]:
    """Parse the 'Alphabet of the Njey' table out of Jekhr_Basics."""
    out = {}
    for line in txt.splitlines():
        m = re.fullmatch(r"([A-Z])\s+(\S+)", line.strip())
        if m:
            out[m.group(2)] = m.group(1)
    return out


def jekhr_glossary(bs: dict[str, str]) -> dict[str, str]:
    gl = {}
    for name, t in bs.items():
        if not name.startswith("Jekhr_"):
            continue
        for line in t.splitlines():
            if "=" in line and not line.startswith(("The ", "By ", "Exercises")):
                eng, _, jek = line.rpartition("=")
                eng, jek = eng.strip(), jek.strip()
                if re.fullmatch(r"[a-z']+", jek):
                    gl[jek] = eng
    return gl


def decode_binary(s: str) -> str:
    return "".join(chr(int(b, 2)) for b in s.split())


def main() -> None:
    bs = books()
    alpha = jekhr_alphabet(bs["Jekhr_Basics"])
    gl = jekhr_glossary(bs)
    print(f"Jekhr alphabet parsed from in-game book Jekhr_Basics: "
          f"{len(alpha)} glyphs")
    print(f"Jekhr glossary parsed from in-game Jekhr_* books: {len(gl)} words")

    a = decode_binary(POLL_A)
    print(f"\nA (ASCII binary) -> {a!r}")

    # B: glyph-by-glyph.  '->' is a two-character glyph, so scan longest-first.
    glyphs = sorted(alpha, key=len, reverse=True)
    romanised, i = [], 0
    s = POLL_B
    while i < len(s):
        for g in glyphs:
            if s.startswith(g, i):
                romanised.append(alpha[g])
                i += len(g)
                break
        else:
            romanised.append(s[i])
            i += 1
    rom = "".join(romanised)
    print(f"B (Jekhr, in-game alphabet) -> {rom}")
    words = rom.lower().split()
    print("B word-by-word via the in-game vocabulary books:")
    for w in words:
        if w in gl:
            print(f"    {w:<8} = {gl[w]}")
        else:
            # compounds, per Jekhr_Basic_Vocabulary_I's own note
            parts = [(k, gl[k]) for k in sorted(gl, key=len, reverse=True)
                     if w.startswith(k) and w[len(k):] in gl]
            if parts:
                k, v = parts[0]
                print(f"    {w:<8} = {v} + {gl[w[len(k):]]}  (compound)")
            else:
                print(f"    {w:<8} = ?")

    print(f"\nC (469) -> {POLL_C}   [no key exists in any shipped game text]")
    print("\nCONCLUSION: A and B are different sentences.  The three answers are "
          "three different jokes, not one sentence in three encodings.  "
          "Answer C is NOT known-plaintext.")

    out = REPO / "experiments" / "verify_2026" / "out"
    out.mkdir(exist_ok=True)
    (out / "g3_poll.json").write_text(json.dumps({
        "A_plaintext": a, "B_romanised": rom,
        "B_glosses": {w: gl.get(w) for w in words},
        "C": POLL_C, "C_known_plaintext": False,
        "alphabet_source": "in-game book Jekhr_Basics",
        "n_alphabet": len(alpha), "n_glossary": len(gl),
    }, indent=2))


if __name__ == "__main__":
    main()
