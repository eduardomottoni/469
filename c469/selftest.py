"""Regression test: the harness must re-derive every established fact.

A mismatch here means a loader or a statistic is broken, and every downstream
result is void.
"""
from __future__ import annotations

from . import corpus as C, stats as S, surrogate as U, cribs as K

EXPECTED = {
    "n_books": 70,
    "n_digits": 11263,
    "unigram_H": 3.2647,
    "ic": 0.10825,
    "h4": 0.937,
    "bigram_chi2": 5277.1,
    "missing_bigrams": ["07"],
    "lz76": 608,
    "distinct_4grams": 984,
    "longest_cross_repeat": 279,
}


def main() -> int:
    b = C.load_books()
    bk = list(b.books)
    got = {
        "n_books": len(bk),
        "n_digits": b.n_digits,
        "unigram_H": round(S.unigram_H(bk), 4),
        "ic": round(S.ic(bk), 5),
        "h4": round(S.cond_entropy(bk, 4), 3),
        "bigram_chi2": round(S.bigram_chi2(bk), 1),
        "missing_bigrams": S.missing_bigrams(bk),
        "lz76": S.lz76_factors(b.concat),
        "distinct_4grams": S.distinct_ngrams(bk, 4),
        "longest_cross_repeat": S.longest_cross_repeat(bk),
    }
    bad = 0
    for k, v in EXPECTED.items():
        ok = got[k] == v
        print(f"{'ok  ' if ok else 'FAIL'} {k:22s} expected={v!r:12} got={got[k]!r}")
        bad += not ok

    # surrogates must preserve corpus shape and (where claimed) unigrams
    for fam in U.DEFAULT_FAMILIES:
        g = fam.generate(bk, 7)
        shape_ok = [len(x) for x in g] == [len(x) for x in bk]
        print(f"{'ok  ' if shape_ok else 'FAIL'} surrogate shape {fam.name}")
        bad += not shape_ok
    sh = U.Shuffle().generate(bk, 7)
    ex = abs(S.unigram_H(sh) - S.unigram_H(bk)) < 1e-9
    print(f"{'ok  ' if ex else 'FAIL'} Shuffle preserves unigrams exactly")
    bad += not ex

    # the crib dialect split must hold: nothing is both translated and in-books
    # (other than the trivial single digit "1")
    both = [r for r in K.annotate(bk)
            if r["claimed_plaintext"] and r["in_books"] and r["text"] != "1"]
    print(f"{'ok  ' if not both else 'FAIL'} no crib is both translated and in-books"
          + (f" -> {[r['text'] for r in both]}" if both else ""))
    bad += bool(both)

    print("\nSELFTEST", "PASS" if not bad else f"FAIL ({bad})")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
