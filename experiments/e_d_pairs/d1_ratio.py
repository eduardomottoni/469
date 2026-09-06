"""D1 -- is r/l a real constraint, or the shape of any correlated pair set?

Pre-registered statistic: CV of r/l over the FB pairs with no obscured digits.
Direction: "less" (a real constraint makes the CV small).

Four nulls, in increasing order of how much they concede to the hypothesis:

  UniformBand     l,r drawn independently, uniform over the observed ranges.
                  The strawman: it only asks "are l and r related at all".
  CorpusSubstr    l,r read as digit substrings of the real 469 corpus,
                  matched to the observed digit-length distribution.
  MarginalPairing keep the OBSERVED multisets of l and of r, repair at random.
                  This is the null that matters: it asks whether the specific
                  pairing carries information beyond the two marginals.
  RankPairing     pair the sorted l's with the sorted r's after jittering the
                  r ranks -- concedes monotone co-variation and asks whether
                  the ratio is tighter than monotonicity alone forces.
"""
from __future__ import annotations
import json, sys, random, time
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from c469.cribs import FB_PAIRS_CERTAIN
from c469 import corpus as C
from c469.harness import Result, summarize_null

STATISTIC = "cv_ratio"
DIRECTION = "less"
NULL_FAMILIES = ("UniformBand", "CorpusSubstr", "MarginalPairing", "RankPairing")


def cv_ratio(pairs) -> float:
    q = np.array([r / l for l, r in pairs], float)
    return float(q.std(ddof=1) / q.mean())


def _null_uniform(pairs, rng):
    l = [p[0] for p in pairs]; r = [p[1] for p in pairs]
    lo_l, hi_l, lo_r, hi_r = min(l), max(l), min(r), max(r)
    return [(rng.randint(lo_l, hi_l), rng.randint(lo_r, hi_r)) for _ in pairs]


def _null_corpus(pairs, rng, books):
    joined = "".join(books)
    out = []
    for l, r in pairs:
        nl, nr = len(str(l)), len(str(r))
        while True:
            i = rng.randrange(len(joined) - nl); a = int(joined[i:i + nl])
            j = rng.randrange(len(joined) - nr); b = int(joined[j:j + nr])
            if a and b:
                out.append((a, b)); break
    return out


def _null_marginal(pairs, rng):
    r = [p[1] for p in pairs]; rng.shuffle(r)
    return list(zip([p[0] for p in pairs], r))


def _null_rank(pairs, rng):
    """Concede monotonicity: sorted l's against sorted r's, ranks locally jittered."""
    l = sorted(p[0] for p in pairs); r = sorted(p[1] for p in pairs)
    idx = list(range(len(r)))
    for _ in range(len(r)):           # a few adjacent transpositions
        i = rng.randrange(len(r) - 1)
        idx[i], idx[i + 1] = idx[i + 1], idx[i]
    return list(zip(l, [r[i] for i in idx]))


def run(pairs, label, n_nulls=20000, seed=1):
    books = list(C.load_books().books)
    real = cv_ratio(pairs)
    nulls = []
    for fam in NULL_FAMILIES:
        rng = random.Random(seed * 7919 + hash(fam) % 10 ** 6)
        vals = []
        for _ in range(n_nulls):
            if fam == "UniformBand":
                s = _null_uniform(pairs, rng)
            elif fam == "CorpusSubstr":
                s = _null_corpus(pairs, rng, books)
            elif fam == "MarginalPairing":
                s = _null_marginal(pairs, rng)
            else:
                s = _null_rank(pairs, rng)
            vals.append(cv_ratio(s))
        nulls.append(summarize_null(fam, real, vals, DIRECTION))
    res = Result(experiment=f"e_d_pairs.d1_ratio.{label}", statistic=STATISTIC,
                 real_value=real, direction=DIRECTION, nulls=nulls,
                 corpus_provenance="c469.cribs.FB_PAIRS_CERTAIN (README FB image, "
                                   "digits the clay figure does not obscure)",
                 seed=seed, n_candidates_tested=1,
                 extra={"n_pairs": len(pairs), "pairs": [list(p) for p in pairs]})
    return res


if __name__ == "__main__":
    P = list(FB_PAIRS_CERTAIN)
    for label, pp in (("all18", P), ("no1280", [p for p in P if p != (1280, 625)])):
        t0 = time.time()
        res = run(pp, label)
        print(f"\n=== {label}: n={len(pp)} CV={res.real_value:.5f}  ({time.time()-t0:.0f}s)")
        for n in res.nulls:
            print(f"  {n.family:16s} mean={n.mean:.4f} sd={n.sd:.4f} min={n.minimum:.4f} "
                  f"p={n.p:.5f} z={n.z:+.2f}")
        print("  worst p =", res.worst_p)
        print("  saved ->", res.save())
