"""Is a short stream underpowered, or is 469 just not language?

The honest way to say "underpowered" is to show the identical solver failing on
a *known* homophonic cipher of the same shape.  For each real configuration's
(length, symbol count) we encipher real English text the same way and report
whether the solver recovers it.
"""
import sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).parent))
from solver import solve, load_table
from calibrate import make_cipher

SHAPES = [
    ("C2_mdl / dedup_core", 1923, 76),
    ("C2_mdl / contigs", 2241, 121),
    ("C2_mdl / master_v1", 2000, 100),
    ("C1_pairs / dedup_core", 1946, 96),
    ("C1_triples / dedup_core", 1293, 374),
    ("C1_pairs / seed", 289, 87),
    ("C2_mdl / seed", 554, 12),
]


def main():
    tab = load_table("en")
    print(f"{'shape':26s} {'n':>5s} {'S':>5s} {'recovered':>10s} {'accuracy':>9s}  verdict")
    for name, n, S in SHAPES:
        if S > 27:
            stream, txt = make_cipher(n, S)
            npc, key, pt = solve(stream, tab, n_restarts=8, n_temps=100,
                                 sweeps=5, seed=1)
            acc = sum(a == b for a, b in zip(pt, txt)) / len(txt)
            v = "solvable" if acc > 0.8 else "UNDERPOWERED"
        else:
            npc, acc, v = float("nan"), float("nan"), \
                "ILL-POSED (fewer symbols than letters: a homophonic cipher " \
                "needs at least 27 symbols to carry a 26-letter alphabet)"
        print(f"{name:26s} {n:5d} {S:5d} {npc:10.4f} {acc:9.3f}  {v}", flush=True)


if __name__ == "__main__":
    main()
