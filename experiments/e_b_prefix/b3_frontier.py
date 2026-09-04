"""B3(a): the alphabet-size / mean-codeword-length frontier.

The 1.577 prediction has two halves that the plan assumed were compatible:
a mean codeword length of 1.577 digits per plaintext unit, AND an alphabet of
~26-32 letters with ~8 of them on single-digit codewords.

For a prefix code over {0..9} with codewords of length <= 3, those two halves
are a joint constraint that the corpus can settle exactly: for each codebook
size, what is the largest mean codeword length any structure attains?  Kraft
forces `10*m1 + m2 = 100` for a two-length code, so a 28-codeword letter code
is exactly 8 singles + 20 doubles -- there is no freedom left.

Usage: python -m experiments.e_b_prefix.b3_frontier
"""
from __future__ import annotations

import itertools
import json
from pathlib import Path

import numpy as np

from c469.corpus import load_books
from .enum_core import pack, eval_structure, tmatrix, codebook_from
from .b1_enumerate import REDUCED_SPACE, FULL_SPACE

OUT = Path(__file__).resolve().parent / "out"
PREDICTION = 1.577


def frontier(books, space=None):
    space = space or {10: 0, 9: 4, 8: 3, 7: 2, 6: 2, 5: 2, 4: 2, 3: 1, 2: 1, 1: 1}
    flat, offs = pack(list(books))
    best: dict[int, tuple] = {}
    for ns, tmax in space.items():
        for S1 in itertools.combinations(range(10), ns):
            m = sum(1 << d for d in S1)
            prefixes = [d for d in range(10) if d not in S1]
            slots = [(p, d) for p in prefixes for d in range(10)]
            for t in range(tmax + 1):
                cb = ns + 10 * (10 - ns) + 9 * t
                for combo in itertools.combinations(slots, t):
                    code = 0
                    for p, d in combo:
                        code |= 1 << (p * 10 + d)
                    parsed, ntok, toklen = eval_structure(flat, offs, m,
                                                          tmatrix(code))
                    L = toklen / ntok
                    if cb not in best or L > best[cb][0]:
                        best[cb] = (L, m, code, parsed)
    return best


def main():
    c = load_books()
    best = frontier(list(c.books))
    rows = []
    for cb in sorted(best):
        L, m, code, parsed = best[cb]
        rows.append({"codebook_size": cb, "max_mean_len": L,
                     "S1": "".join(str(d) for d in range(10) if (m >> d) & 1),
                     "books_parsed": parsed})
    print("codebook size -> largest attainable mean codeword length")
    print("  |cb|   max L    S1            books parsed")
    for r in rows:
        flag = "  <-- 1.577 reachable" if r["max_mean_len"] >= PREDICTION else ""
        print(f"  {r['codebook_size']:>4}  {r['max_mean_len']:.4f}  "
              f"{r['S1']:<12}  {r['books_parsed']:>2}/70{flag}")
    ok = [r for r in rows if r["max_mean_len"] >= PREDICTION]
    smallest = min((r["codebook_size"] for r in ok), default=None)
    print(f"\nsmallest codebook that can reach mean length {PREDICTION}: {smallest}")
    letter = [r for r in rows if 24 <= r["codebook_size"] <= 34]
    print("letter-sized codebooks (24-34 codewords): max mean length = "
          f"{max(r['max_mean_len'] for r in letter):.4f}")
    OUT.mkdir(exist_ok=True)
    Path(OUT / "b3_frontier.json").write_text(json.dumps({
        "prediction": PREDICTION, "provenance": c.provenance,
        "smallest_codebook_reaching_prediction": smallest,
        "max_mean_len_letter_sized": max(r["max_mean_len"] for r in letter),
        "frontier": rows}, indent=2))


if __name__ == "__main__":
    main()
