"""G6 -- follow-up on the one SUPPORTED cell in G2's control scan.

G2 ran positional_chi2 for every modulus 2..12 purely as a control, so that
"5 is special" could not be claimed by picking 5 after looking.  Modulus 5 came
out REJECTED (p = 0.92) -- but modulus 8 came out at the p floor against all six
null families (+3.6 to +4.7 sigma, BH q = 0.027).

A finding that nobody predicted, produced by a control scan, gets tested harder
than one that was pre-registered, not softer.  Three follow-ups:

  F1  Does it survive removing the corpus's copy-paste redundancy?
      Same statistic on corpus.dedup_core(), which greedily drops books that
      are mostly repeats of already-kept material.

  F2  Is 8 special, or is every large modulus inflated?  Extend the scan to
      13..24 on the full corpus.

  F3  Where does it come from?  Residue x digit contingency, and a
      leave-one-book-out jackknife.
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
from c469 import corpus, harness, stats  # noqa: E402
from c469 import surrogate as U  # noqa: E402

N_NULLS = 400
SEED = 469


class PositionalMod(harness.Experiment):
    STATISTIC = "positional_chi2"
    DIRECTION = "greater"
    NULL_FAMILIES = U.DEFAULT_FAMILIES

    def __init__(self, mod: int, tag: str):
        self.mod = mod
        self.NAME = f"G6_positional_mod{mod}_{tag}"

    def compute(self, books):
        return stats.positional_chi2(books, self.mod)


def main() -> None:
    c = corpus.load_books()
    books = list(c.books)
    dc = corpus.dedup_core(c)
    out = REPO / "experiments" / "verify_2026" / "out"
    out.mkdir(exist_ok=True)
    results = []

    print("=== F1: mod 8 with the copy-paste redundancy removed ===")
    print(f"dedup_core: {len(dc.books)} books, {dc.n_digits} digits "
          f"(from {len(books)} / {c.n_digits})")
    for mod in (4, 8, 16):
        e = PositionalMod(mod, "dedupcore")
        r = e.run(list(dc.books), provenance=dc.provenance, n_nulls=N_NULLS,
                  seed=SEED, n_candidates=3)
        results.append(r)
        print(f"  mod {mod:2d}: chi2={r.real_value:8.2f} (df {9 * (mod - 1)})  "
              f"worst p={r.worst_p:.4f}  {r.verdict}")
        for nr in r.nulls:
            print(f"      {nr.family:22s} {nr.mean:8.2f}+-{nr.sd:6.2f} "
                  f"z={nr.z:+.2f} p={nr.p:.4f}")

    print("\n=== F2: is 8 special?  scan 13..24 on the full corpus ===")
    ps = {}
    for mod in range(13, 25):
        e = PositionalMod(mod, "books")
        r = e.run(books, provenance=c.provenance, n_nulls=N_NULLS, seed=SEED,
                  n_candidates=23)
        results.append(r)
        ps[mod] = r.worst_p
        print(f"  mod {mod:2d}: chi2={r.real_value:8.2f} (df {9 * (mod - 1)})  "
              f"worst p={r.worst_p:.4f}  {r.verdict}")

    print("\n=== F3: where does the mod-8 excess sit? ===")
    c1 = Counter("".join(books))
    n = sum(c1.values())
    tab = [Counter() for _ in range(8)]
    for b in books:
        for i, ch in enumerate(b):
            tab[i % 8][ch] += 1
    print("signed chi2 cell contributions (residue x digit)")
    print("res    tot  " + "  ".join(f"   {d}" for d in "0123456789"))
    cells_out = {}
    for r_ in range(8):
        tot = sum(tab[r_].values())
        row = []
        for d in "0123456789":
            e_ = tot * c1[d] / n
            o = tab[r_][d]
            row.append((o - e_) ** 2 / e_ * (1 if o > e_ else -1))
        cells_out[r_] = dict(zip("0123456789", [round(x, 2) for x in row]))
        print(f" {r_}  {tot:6d} " + " ".join(f"{x:+6.1f}" for x in row))

    base = stats.positional_chi2(books, 8)
    jk = sorted((stats.positional_chi2(books[:i] + books[i + 1:], 8), i)
                for i in range(len(books)))
    print(f"\njackknife on mod 8 (full = {base:.2f}): "
          f"min {jk[0][0]:.1f} (drop B{jk[0][1]}), max {jk[-1][0]:.1f} "
          f"(drop B{jk[-1][1]})  -- no single book drives it")

    for r in results:
        r.save()
    (out / "g6_mod8.json").write_text(json.dumps({
        "results": [{"name": r.experiment, "real": r.real_value,
                     "worst_p": r.worst_p, "verdict": r.verdict,
                     "nulls": {n_.family: {"mean": n_.mean, "sd": n_.sd,
                                           "z": n_.z, "p": n_.p}
                               for n_ in r.nulls}} for r in results],
        "scan_13_24_worst_p": ps,
        "mod8_cells": cells_out,
        "mod8_jackknife_min": jk[0], "mod8_jackknife_max": jk[-1],
    }, indent=2))
    print("\nsaved", out / "g6_mod8.json")


if __name__ == "__main__":
    main()
