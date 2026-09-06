"""Family E, scored: is the corpus's copy signature reachable by anything else?

Statistic: `copy_code_advantage` = (prequential CTW-8 bits/digit)
                                 - (leave-one-book-out relative-LZ bits/digit).
Large and positive means "a copy model explains this corpus far better than any
sequential statistical model does".  Both terms are real code lengths, so the
difference is in bits and needs no calibration of its own.

The pre-registered expectation, given the LZ76 gap, is that the corpus clears
Shuffle / Markov / BlockShuffle by a mile and does NOT clear CopyPasteMutate.
That is the finding, not a failure: only a copy-paste process reproduces it.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from c469.corpus import load_books
from c469 import surrogate as U
from c469.harness import Experiment
from c469.stats import (ctw_bits_per_digit, relative_lz_bits_per_digit,
                        lz76_factors, distinct_ngrams)


class CopyCodeAdvantage(Experiment):
    NAME = "e_e_nullproc"
    STATISTIC = "copy_code_advantage_bits_per_digit"
    DIRECTION = "greater"
    NULL_FAMILIES = U.DEFAULT_FAMILIES

    def compute(self, books):
        return (ctw_bits_per_digit(books, 8)
                - relative_lz_bits_per_digit(books, loo=True))


class LZ76Factors(CopyCodeAdvantage):
    STATISTIC = "lz76_factors"
    DIRECTION = "less"

    def compute(self, books):
        return float(lz76_factors("".join(books)))


class Distinct4Grams(CopyCodeAdvantage):
    STATISTIC = "distinct_4grams"
    DIRECTION = "less"

    def compute(self, books):
        return float(distinct_ngrams("".join(books), 4))


def main(n=200):
    c = load_books(with_kharos=False)
    books = list(c.books)
    for E in (CopyCodeAdvantage(), LZ76Factors(), Distinct4Grams()):
        r = E.run(books, provenance=c.provenance, n_nulls=n, seed=3)
        print(E.STATISTIC, "real=%.4g" % r.real_value,
              {x.family: (round(x.mean, 3), round(x.p, 4)) for x in r.nulls},
              r.verdict, flush=True)
        r.save()


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 200)
