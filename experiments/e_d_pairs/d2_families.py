"""D2 -- exhaustive enumeration of the candidate "mathemagic" function families.

For every family F we compute the SAME statistic:

    E(F, pairs) = min_{f in F} max_i | f(l_i) - r_i |

i.e. the best achievable worst-case error of any member of the family.  E = 0
means the family contains an exact explanation of the pair table.

The number that decides whether a family is evidence is not E on the real
pairs, it is E on pair sets that the hypothesis is supposed to exclude.  Three
nulls, again in increasing order of concession:

  UniformBand       l, r independent uniform over the observed ranges.
  MarginalPairing   observed l and r multisets, re-paired at random.
  ProportionalNoise l's kept; r_i = round(a*l_i + N(0,s)) with a and s taken
                    from the least-squares proportional fit to the REAL pairs.
                    This concedes everything that is already established --
                    that r is about 0.61 l with ~44 units of scatter -- and
                    asks whether the family explains anything beyond that.

A family that reaches the real E just as easily on ProportionalNoise pairs has
too many degrees of freedom to count as evidence, however good its fit looks.
"""
from __future__ import annotations
import sys, time, itertools, random
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from c469.cribs import FB_PAIRS_CERTAIN, FB_PAIRS_OBSCURED, HONEMINAS
from c469.harness import Result, summarize_null

STATISTIC = "best_max_abs_error"
DIRECTION = "less"

RNG = np.random.default_rng(20260904)


# ---------------------------------------------------------------- helpers ----
def digits5(n: int) -> np.ndarray:
    s = str(n).rjust(5, "0")[-5:]
    return np.array([int(c) for c in s], dtype=np.int64)


def digit_matrix(ls, width=5):
    return np.stack([digits5(l) if width == 5 else
                     np.array([int(c) for c in str(l).rjust(width, "0")[-width:]])
                     for l in ls])


# ---------------------------------------------------------------- families ---
def fam_honeminas(ls, rs):
    """r = v . digits5(l), v in [0,9]^5 -- the README's dot-product reading.
    Variant B adds a free integer constant c in [-500,500]."""
    D = digit_matrix(ls)                        # (n,5)
    V = np.array(list(itertools.product(range(10), repeat=5)), dtype=np.int64)  # 1e5 x 5
    pred = V @ D.T                              # (1e5, n)
    err = np.abs(pred - rs[None, :])
    pure = int(err.max(axis=1).min())
    # with free additive constant: best c is the midrange of the residuals
    resid = pred - rs[None, :]
    span = (resid.max(axis=1) - resid.min(axis=1)) / 2.0
    withc = int(np.ceil(span.min()))
    return {"honeminas_dot": pure, "honeminas_dot_plus_c": withc}


def fam_modular(ls, rs, kmax=2000, mmax=2000):
    """r = (k*l) mod m."""
    best = 10 ** 9
    L = ls[None, :]
    for m in range(2, mmax + 1):
        k = np.arange(1, kmax + 1, dtype=np.int64)[:, None]
        pred = (k * L) % m
        e = np.abs(pred - rs[None, :]).max(axis=1).min()
        if e < best:
            best = int(e)
            if best == 0:
                break
    return {"modular_kl_mod_m": best}


def fam_basechange(ls, rs):
    """Read l's decimal digit string in base b1, write the value in base b2,
    read the result back as a decimal integer.  Optional 0-9 digit relabel is
    handled by the digit-permutation family below."""
    best = 10 ** 9; arg = None
    for b1 in range(2, 17):
        vals = []
        ok = True
        for l in ls:
            ds = [int(c) for c in str(l)]
            if max(ds) >= b1:
                ok = False; break
            v = 0
            for d in ds:
                v = v * b1 + d
            vals.append(v)
        if not ok:
            continue
        for b2 in range(2, 17):
            out = []
            for v in vals:
                s = ""
                x = v
                if x == 0:
                    s = "0"
                while x:
                    s = "0123456789abcdef"[x % b2] + s
                    x //= b2
                if any(c in "abcdef" for c in s):
                    out = None; break
                out.append(int(s))
            if out is None:
                continue
            e = int(np.abs(np.array(out) - rs).max())
            if e < best:
                best, arg = e, (b1, b2)
    return {"base_change": best if arg else 10 ** 9}


_FUNCTIONALS = {
    "identity":   lambda l: l,
    "digitsum":   lambda l: sum(int(c) for c in str(l)),
    "digitprod":  lambda l: np.prod([int(c) for c in str(l)]),
    "altsum":     lambda l: sum((-1) ** i * int(c) for i, c in enumerate(str(l))),
    "reversal":   lambda l: int(str(l)[::-1]),
    "sorted_asc": lambda l: int("".join(sorted(str(l)))),
    "sorted_desc": lambda l: int("".join(sorted(str(l), reverse=True))),
}


def fam_functionals(ls, rs, arange=60, brange=3, crange=300):
    """r = a*g(l) + b*l + c for g in the digit functionals."""
    out = {}
    A = np.arange(-arange, arange + 1)
    B = np.arange(-brange, brange + 1)
    for name, g in _FUNCTIONALS.items():
        G = np.array([int(g(l)) for l in ls], dtype=np.int64)
        best = 10 ** 9
        for a in A:
            for b in B:
                resid = a * G + b * ls - rs
                span = (resid.max() - resid.min()) / 2.0     # best c is midrange
                c = -int(round((resid.max() + resid.min()) / 2.0))
                if abs(c) > crange:
                    continue
                e = int(np.ceil(span))
                if e < best:
                    best = e
        out[f"affine_{name}"] = best
    return out


def _seq(name, upto):
    s = []
    if name == "fib":
        a, b = 1, 1
        while a <= upto:
            s.append(a); a, b = b, a + b
    elif name == "tetranacci":
        t = [0, 0, 0, 1]
        while t[-1] <= upto:
            t.append(sum(t[-4:]))
        s = [x for x in t if 0 < x <= upto]
    elif name == "primes":
        sieve = np.ones(upto + 1, bool); sieve[:2] = False
        for i in range(2, int(upto ** .5) + 1):
            if sieve[i]:
                sieve[i * i::i] = False
        s = list(np.flatnonzero(sieve))
    elif name == "catalan":
        c = 1; n = 0
        while c <= upto:
            s.append(c); n += 1; c = c * 2 * (2 * n - 1) // (n + 1)
    elif name == "squares":
        s = [i * i for i in range(1, int(upto ** .5) + 1)]
    elif name == "triangular":
        s = [i * (i + 1) // 2 for i in range(1, upto) if i * (i + 1) // 2 <= upto]
    return sorted(set(s))


def fam_sequences(ls, rs):
    """Index readings: l and r are the values at positions i and i+d of a
    named integer sequence, for a fixed offset d.  Also r = S[rank(l)]."""
    out = {}
    upto = int(max(ls.max(), rs.max()) * 40)
    for name in ("fib", "tetranacci", "primes", "catalan", "squares", "triangular"):
        S = np.array(_seq(name, upto), dtype=np.int64)
        if len(S) < 4:
            out[f"seq_{name}"] = 10 ** 9; continue
        # nearest index of each l in S, then r predicted as S[idx + d]
        idx = np.searchsorted(S, ls)
        idx = np.clip(idx, 0, len(S) - 1)
        best = 10 ** 9
        for d in range(-8, 1):
            j = np.clip(idx + d, 0, len(S) - 1)
            e = int(np.abs(S[j] - rs).max())
            best = min(best, e)
        # also r as the index (rank) of l in S, scaled affinely
        rank = idx.astype(np.int64)
        for a in range(-60, 61):
            resid = a * rank - rs
            best = min(best, int(np.ceil((resid.max() - resid.min()) / 2.0)))
        out[f"seq_{name}"] = best
    return out


FAMILIES = {
    "honeminas": fam_honeminas,
    "modular": fam_modular,
    "basechange": fam_basechange,
    "functionals": fam_functionals,
    "sequences": fam_sequences,
}


def evaluate(pairs) -> dict[str, int]:
    ls = np.array([p[0] for p in pairs], dtype=np.int64)
    rs = np.array([p[1] for p in pairs], dtype=np.int64)
    out = {}
    for fn in FAMILIES.values():
        out.update(fn(ls, rs))
    return out


# ------------------------------------------------------------------ nulls ----
def make_nulls(pairs, kind, n, rng):
    ls = np.array([p[0] for p in pairs]); rs = np.array([p[1] for p in pairs])
    a = float((ls @ rs) / (ls @ ls))
    s = float((rs - a * ls).std(ddof=1))
    sets = []
    for _ in range(n):
        if kind == "UniformBand":
            L = rng.integers(ls.min(), ls.max() + 1, len(ls))
            R = rng.integers(rs.min(), rs.max() + 1, len(rs))
        elif kind == "MarginalPairing":
            L = ls.copy(); R = rng.permutation(rs)
        elif kind == "ProportionalNoise":
            L = ls.copy()
            R = np.round(a * ls + rng.normal(0, s, len(ls))).astype(np.int64)
            R = np.maximum(R, 1)
        else:
            raise ValueError(kind)
        sets.append(list(zip(L.tolist(), R.tolist())))
    return sets


NULL_KINDS = ("UniformBand", "MarginalPairing", "ProportionalNoise")


def main(n_nulls=200):
    pairs = list(FB_PAIRS_CERTAIN)
    t0 = time.time()
    real = evaluate(pairs)
    print(f"real evaluated in {time.time()-t0:.1f}s")
    names = sorted(real)
    for k in names:
        print(f"  {k:26s} best max|err| = {real[k]}")

    rng = np.random.default_rng(4691)
    nullvals = {kind: {k: [] for k in names} for kind in NULL_KINDS}
    for kind in NULL_KINDS:
        sets = make_nulls(pairs, kind, n_nulls, rng)
        t0 = time.time()
        for i, s in enumerate(sets):
            v = evaluate(s)
            for k in names:
                nullvals[kind][k].append(v[k])
            if i % 50 == 0:
                print(f"  {kind} {i}/{n_nulls} ({time.time()-t0:.0f}s)", flush=True)
    return real, nullvals, names


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 200
    real, nullvals, names = main(n)
    import json
    from c469.harness import bh_qvalues
    ps = []
    results = []
    for k in names:
        nulls = [summarize_null(kind, real[k], nullvals[kind][k], DIRECTION)
                 for kind in NULL_KINDS]
        res = Result(experiment=f"e_d_pairs.d2_family.{k}", statistic=STATISTIC,
                     real_value=float(real[k]), direction=DIRECTION, nulls=nulls,
                     corpus_provenance="c469.cribs.FB_PAIRS_CERTAIN",
                     n_candidates_tested=len(names), seed=4691)
        results.append(res); ps.append(res.worst_p)
    qs = bh_qvalues(ps)
    print("\n| family | real E | UniformBand | MarginalPairing | ProportionalNoise | worst p | q |")
    print("|---|---|---|---|---|---|---|")
    for res, q in zip(results, qs):
        res.extra["bh_q"] = q
        cells = " | ".join(f"{nl.mean:.0f}+-{nl.sd:.0f} (p={nl.p:.3f})" for nl in res.nulls)
        print(f"| {res.experiment.split('.')[-1]} | {res.real_value:.0f} | {cells} | "
              f"{res.worst_p:.3f} | {q:.3f} |")
        res.save()
