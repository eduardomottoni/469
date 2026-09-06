"""G1b -- digit composition of the NPC 'translated' dialect vs the books.

Pre-registered statistic: chi-square of the 26-digit translated set's digit
counts against the Hellgate books' unigram distribution.

Matched null (the point of the exercise): draw 4 windows from the books of
exactly the observed lengths (9, 6, 5, 6) at uniformly random positions, and
recompute.  That preserves both the total n and the local digit correlations,
so the only thing the test can see is composition.  A second null draws the
digits i.i.d. from the book unigram, which is strictly weaker.

Secondary, reported but NOT the headline (it is a post-hoc observation, so it
is scored inside the same Monte Carlo rather than quoted on its own):
the 26 translated digits contain no 0, no 1 and no 2, while 1 is the single
commonest digit in the books.
"""
from __future__ import annotations

import json
import random
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
from c469 import corpus  # noqa: E402

TRANSLATED = ["653768764", "659978", "54764", "486486"]
N_MC = 200_000
DIGITS = "0123456789"


def chi2(counts: dict[str, int], p: dict[str, float], n: int) -> float:
    return sum((counts[d] - n * p[d]) ** 2 / (n * p[d]) for d in DIGITS if p[d] > 0)


def main() -> None:
    c = corpus.load_books()
    books = list(c.books)
    allb = "".join(books)
    p = {d: allb.count(d) / len(allb) for d in DIGITS}

    obs_s = "".join(TRANSLATED)
    n = len(obs_s)
    obs_counts = {d: obs_s.count(d) for d in DIGITS}
    obs_chi2 = chi2(obs_counts, p, n)
    obs_missing = sum(obs_counts[d] == 0 for d in DIGITS)
    print(f"observed n={n} chi2={obs_chi2:.3f}  digits never used: "
          f"{[d for d in DIGITS if obs_counts[d] == 0]}")

    lens = [len(s) for s in TRANSLATED]
    rng = random.Random(20260904)

    res = {}
    for null in ("window", "iid"):
        ge_chi2 = ge_missing = 0
        for _ in range(N_MC):
            if null == "window":
                parts = []
                for L in lens:
                    b = books[rng.randrange(len(books))]
                    while len(b) < L:
                        b = books[rng.randrange(len(books))]
                    j = rng.randrange(len(b) - L + 1)
                    parts.append(b[j:j + L])
                s = "".join(parts)
            else:
                s = "".join(rng.choices(DIGITS, weights=[p[d] for d in DIGITS], k=n))
            cnt = {d: s.count(d) for d in DIGITS}
            ge_chi2 += chi2(cnt, p, n) >= obs_chi2
            ge_missing += sum(cnt[d] == 0 for d in DIGITS) >= obs_missing
        res[null] = {
            "p_chi2": (1 + ge_chi2) / (1 + N_MC),
            "p_n_missing_digits": (1 + ge_missing) / (1 + N_MC),
        }
        print(f"null={null:7s}  p(chi2 >= obs) = {res[null]['p_chi2']:.5f}   "
              f"p(>= {obs_missing} unused digits) = {res[null]['p_n_missing_digits']:.5f}")

    print("\nNOTE: n = 26 digits.  Even a 'significant' composition difference "
          "here is 26 digits of evidence and cannot identify an encoding; it "
          "can only say the NPC lines were not sampled from the book text.")

    out = REPO / "experiments" / "verify_2026" / "out"
    out.mkdir(exist_ok=True)
    (out / "g1b_composition.json").write_text(json.dumps({
        "n": n, "obs_chi2": obs_chi2, "obs_counts": obs_counts,
        "book_unigram": p, "n_mc": N_MC, "nulls": res,
        "unused_digits": [d for d in DIGITS if obs_counts[d] == 0],
    }, indent=2))


if __name__ == "__main__":
    main()
