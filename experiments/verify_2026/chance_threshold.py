"""How long must a match be before it is evidence of copying?

`extract_seed.py` charges every match of length >= 3 to the copy model.  Over a
ten-symbol alphabet that is almost free: an 11,263-digit i.i.d. stream already
contains a >= 3 match at 91% of its positions purely by chance.  This script
prints the false-copy rate of each `min_copy` threshold, which is what fixes the
chance-corrected threshold used by residue.py / attack_lib.py.
"""
from __future__ import annotations

import random
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1]))

from fastlz import max_match_len            # noqa: E402
from c469.corpus import load_books          # noqa: E402


def main(n_iid=20):
    c = "".join(load_books(with_kharos=False).books)
    L = max_match_len(c)
    real = Counter(L)
    tot = len(L)
    iid = Counter()
    for s in range(n_iid):
        rng = random.Random(1000 + s)
        x = "".join(str(rng.randrange(10)) for _ in range(len(c)))
        iid.update(max_match_len(x))
    itot = tot * n_iid
    print(f"corpus {tot} digits; {n_iid} i.i.d. streams of the same length\n")
    print("min_copy | share of REAL positions inside a copy | FALSE-copy rate (i.i.d.)")
    for k in (3, 4, 5, 6, 7, 8, 10, 12):
        r = sum(v for j, v in real.items() if j >= k) / tot
        i = sum(v for j, v in iid.items() if j >= k) / itot
        print(f"   {k:2d}    |            {r:.4f}                 |        {i:.4f}")


if __name__ == "__main__":
    main()
