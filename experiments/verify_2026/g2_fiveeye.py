"""G2 -- the 5-eye premise, tested concretely.

PRE-REGISTRATION (fixed before any null was drawn).

The lore says a bonelord blinks with five eyes.  Three mechanised readings:

  H1  PERIOD-5 FRAME.  A 469 "word" is one digit per eye, so digit statistics
      depend on position mod 5 measured from each book's own start.
      statistic: stats.positional_chi2(books, 5).  direction: greater.

  H2  BASE-5 CARRIER.  Ten digits = five eye-values x a binary flag, i.e.
      d -> (hi = d // 5, lo = d % 5).  If that is the real carrier, one of the
      two derived streams should be MORE predictable than the digit-level
      Markov structure of the corpus already implies.
      statistics: stats.cond_entropy(hi_stream, 4)  and  (lo_stream, 4).
      direction: less.

  H3  FIVE-DIGIT WORDS.  If words are 5 digits, book lengths should be
      concentrated on multiples of 5.  statistic: number of books with
      len % 5 == 0.  direction: greater.

Every statistic is scored against surrogate.DEFAULT_FAMILIES, which includes
Markov2/Markov3 (preserve local digit structure) and CopyPasteMutate (preserves
the corpus's copy-paste redundancy).  A period-5 or base-5 carrier that is real
must survive those, since none of them knows about five-ness.

Control: H1 is also run for every modulus 2..12 and reported with a
Benjamini-Hochberg q, so "5 is special" cannot be claimed by picking 5 after
looking.
"""
from __future__ import annotations

import json
import sys
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

    def __init__(self, mod: int):
        self.mod = mod
        self.NAME = f"G2_H1_positional_mod{mod}"

    def compute(self, books):
        return stats.positional_chi2(books, self.mod)


def _split(books, which):
    if which == "hi":
        return ["".join(str(int(ch) // 5) for ch in b) for b in books]
    return ["".join(str(int(ch) % 5) for ch in b) for b in books]


class Base5Stream(harness.Experiment):
    STATISTIC = "cond_entropy_h4"
    DIRECTION = "less"
    NULL_FAMILIES = U.DEFAULT_FAMILIES

    def __init__(self, which: str):
        self.which = which
        self.NAME = f"G2_H2_base5_{which}"

    def compute(self, books):
        return stats.cond_entropy(_split(books, self.which), 4)


class LenMod5(harness.Experiment):
    NAME = "G2_H3_booklen_mod5"
    STATISTIC = "n_books_len_div5"
    DIRECTION = "greater"
    NULL_FAMILIES = U.DEFAULT_FAMILIES

    def compute(self, books):
        return sum(len(b) % 5 == 0 for b in books)


def main() -> None:
    c = corpus.load_books()
    books = list(c.books)
    out = REPO / "experiments" / "verify_2026" / "out"
    out.mkdir(exist_ok=True)
    results = []

    print("=== H1: period-5 frame (and the 2..12 control scan) ===")
    scan = {}
    for m in range(2, 13):
        e = PositionalMod(m)
        r = e.run(books, provenance=c.provenance, n_nulls=N_NULLS, seed=SEED,
                  n_candidates=11)
        scan[m] = r
        results.append(r)
        print(f"  mod {m:2d}: chi2={r.real_value:9.2f}  worst p={r.worst_p:.4f}  "
              f"{r.verdict}")
    ps = [scan[m].worst_p for m in range(2, 13)]
    qs = harness.bh_qvalues(ps)
    print("  BH q-values:", {m: round(q, 4) for m, q in zip(range(2, 13), qs)})
    print(f"  mod 5 specifically: p={scan[5].worst_p:.4f}  q={qs[3]:.4f}")

    print("\n=== H2: base-5 carrier ===")
    for which in ("hi", "lo"):
        e = Base5Stream(which)
        r = e.run(books, provenance=c.provenance, n_nulls=N_NULLS, seed=SEED,
                  n_candidates=2)
        results.append(r)
        print(f"  {which}: h4={r.real_value:.5f}  worst p={r.worst_p:.4f}  {r.verdict}")
        for nr in r.nulls:
            print(f"      {nr.family:22s} {nr.mean:.5f}+-{nr.sd:.5f}  z={nr.z:+.2f} p={nr.p:.4f}")

    print("\n=== H3: five-digit words ===")
    e = LenMod5()
    r = e.run(books, provenance=c.provenance, n_nulls=N_NULLS, seed=SEED)
    results.append(r)
    lens = sorted(len(b) for b in books)
    from collections import Counter
    print("  book lengths mod 5:", dict(sorted(Counter(l % 5 for l in lens).items())))
    print(f"  n divisible by 5 = {r.real_value:.0f}/70   worst p={r.worst_p:.4f}  {r.verdict}")

    for r in results:
        r.save()
    (out / "g2_summary.json").write_text(json.dumps(
        [{"name": r.experiment, "stat": r.statistic, "real": r.real_value,
          "worst_p": r.worst_p, "verdict": r.verdict,
          "nulls": {n.family: {"mean": n.mean, "sd": n.sd, "z": n.z, "p": n.p}
                    for n in r.nulls}} for r in results], indent=2))
    print("\nsaved", out / "g2_summary.json")


if __name__ == "__main__":
    main()
