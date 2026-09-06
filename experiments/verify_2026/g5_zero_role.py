"""G5 -- the librarian's 0 taboo, taken literally.

Game content, not statistics, motivates this one.  The Hellgate librarian has a
dedicated keyword for the digit 0:

    Player: 0
    A Wrinkled Bonelord: "Go and wash your eyes for using this obscene number!"

and none of the four 469 strings that CipSoft ever attached an English meaning
to (653768764 / 659978 / 54764 / 486486) contains a 0 -- yet the books contain
855 zeros (7.6%).  If 0 is not a normal symbol of the language, the natural
reading is that it is punctuation: a word or phrase delimiter.

PRE-REGISTRATION.

  H4  0 IS A DELIMITER.  If 0 separates tokens, the gaps between consecutive
      zeros should be a token-length distribution -- i.e. MORE regular than the
      corpus's own local structure predicts.
      statistic: Shannon entropy of the gap-length distribution between
      consecutive 0s (concatenating within books, never across).
      direction: less.

  H5  0 IS A BOUNDARY MARKER.  A delimiter should be enriched at book edges.
      statistic: number of books whose first or last digit is 0.
      direction: greater.

Both are scored against surrogate.DEFAULT_FAMILIES.  Shuffle destroys ordering
but preserves the number of zeros; Markov2/3 and CopyPasteMutate preserve local
structure, so they are the tests that matter.
"""
from __future__ import annotations

import json
import math
import sys
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
from c469 import corpus, harness  # noqa: E402
from c469 import surrogate as U  # noqa: E402

N_NULLS = 400
SEED = 469


def gap_entropy(books) -> float:
    gaps = Counter()
    for b in books:
        prev = None
        for i, ch in enumerate(b):
            if ch == "0":
                if prev is not None:
                    gaps[i - prev] += 1
                prev = i
    n = sum(gaps.values())
    if n == 0:
        return 0.0
    return -sum((c / n) * math.log2(c / n) for c in gaps.values())


class GapEntropy(harness.Experiment):
    NAME = "G5_H4_zero_gap_entropy"
    STATISTIC = "gap_entropy_bits"
    DIRECTION = "less"
    NULL_FAMILIES = U.DEFAULT_FAMILIES

    def compute(self, books):
        return gap_entropy(books)


class EdgeZeros(harness.Experiment):
    NAME = "G5_H5_zero_at_book_edge"
    STATISTIC = "n_books_edge_zero"
    DIRECTION = "greater"
    NULL_FAMILIES = U.DEFAULT_FAMILIES

    def compute(self, books):
        return sum(b[0] == "0" or b[-1] == "0" for b in books)


def main() -> None:
    c = corpus.load_books()
    books = list(c.books)
    s = "".join(books)
    print(f"zeros: {s.count('0')}/{len(s)} = {s.count('0') / len(s):.4f}")
    gaps = Counter()
    for b in books:
        prev = None
        for i, ch in enumerate(b):
            if ch == "0":
                if prev is not None:
                    gaps[i - prev] += 1
                prev = i
    print("commonest 0-to-0 gaps:", gaps.most_common(12))
    print(f"gap entropy = {gap_entropy(books):.4f} bits over "
          f"{sum(gaps.values())} gaps, {len(gaps)} distinct")
    print("books starting with 0:", sum(b[0] == '0' for b in books),
          " ending with 0:", sum(b[-1] == '0' for b in books))

    results = []
    for e in (GapEntropy(), EdgeZeros()):
        r = e.run(books, provenance=c.provenance, n_nulls=N_NULLS, seed=SEED,
                  n_candidates=2)
        results.append(r)
        print(f"\n{e.NAME}: real={r.real_value:.5f}  {r.verdict} "
              f"(worst p={r.worst_p:.4f})")
        for nr in r.nulls:
            print(f"    {nr.family:22s} {nr.mean:.5f}+-{nr.sd:.5f}  "
                  f"z={nr.z:+.2f}  p={nr.p:.4f}")
        r.save()

    out = REPO / "experiments" / "verify_2026" / "out"
    out.mkdir(exist_ok=True)
    (out / "g5_zero_role.json").write_text(json.dumps(
        [{"name": r.experiment, "real": r.real_value, "worst_p": r.worst_p,
          "verdict": r.verdict,
          "nulls": {n.family: {"mean": n.mean, "sd": n.sd, "z": n.z, "p": n.p}
                    for n in r.nulls}} for r in results], indent=2))


if __name__ == "__main__":
    main()
