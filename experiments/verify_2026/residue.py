"""Residue (innovation) extraction under several parse policies.

The PR's `extract_seed.py` produced ONE residue: the 578-digit LZ76 innovation
string of `data/master_v1.txt` (the one new digit terminating each factor).
Family C then found that 578 digits is too few for any homophonic method:
`C2_mdl` collapses to V=12 and `C1_pairs` recovers 6.6% of an injected map.

This module asks whether the extraction was throwing recoverable innovation
away.  It is a *chance-correction* question.  Over a 10-symbol alphabet, a
reference of N digits contains, by chance alone, essentially every string of
length L <= log10(N).  For the 6,057-digit master, log10(N) = 3.78: a 3-digit
"copy" is not evidence of copying at all, it is the birthday paradox.  The
shipped extraction charges every match of length >= 3 to the copy model, so
every digit that happens to land inside a chance 3-, 4- or 5-gram match is
deleted from the residue even though it is innovation.

Policies implemented
--------------------
greedy   classical LZ77/LZSS greedy parse against the prefix
lazy     LZSS lazy matching (emit a literal when p+1 offers a longer match)
optimal  minimum-code-length parse by dynamic programming (the parse an actual
         copy-paste encoder would use, not the greedy approximation)
backward the same greedy parse run on the reversed string, mapped back
union    permissive: a position is copied only if EVERY policy above calls it
         copied; innovation is the union of the four innovation sets

`min_copy` is swept.  min_copy = 3 reproduces the PR's setting; min_copy = 6 is
the chance-corrected threshold (P(a given 6-gram occurs in 6,057 digits) ~ 0.6%
per position, so a 6-match is ~100x less likely by chance than a 3-match).
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO))

from c469.corpus import load_books                      # noqa: E402
from c469.stats import _longest_match                   # noqa: E402
from c469 import stats as S                             # noqa: E402


# ---------------------------------------------------------------- primitives

def max_match_len(s: str, maxlen: int = 400) -> list[int]:
    """Lmax[p] = length of the longest prefix of s[p:] occurring in s[:p]."""
    out = [0] * len(s)
    for p in range(len(s)):
        L, _ = _longest_match(s[:p], s, p, maxlen=maxlen)
        out[p] = L
    return out


def lz76_innovation_positions(s: str) -> list[int]:
    """Positions of the one new digit ending each LZ76 factor (the PR's A)."""
    pos, i = [], 0
    n = len(s)
    while i < n:
        L = 1
        while i + L <= n and s[i:i + L] in s[:i]:
            L += 1
        L = max(1, L - 1)
        pos.append(i + L - 1)
        i += L
    return pos


def greedy_copy_intervals(s: str, min_copy: int, Lmax=None) -> list[tuple[int, int]]:
    Lmax = Lmax if Lmax is not None else max_match_len(s)
    out, p = [], 0
    while p < len(s):
        L = Lmax[p]
        if L >= min_copy:
            out.append((p, L)); p += L
        else:
            p += 1
    return out


def lazy_copy_intervals(s: str, min_copy: int, Lmax=None) -> list[tuple[int, int]]:
    Lmax = Lmax if Lmax is not None else max_match_len(s)
    out, p, n = [], 0, len(s)
    while p < n:
        L = Lmax[p]
        if L >= min_copy and not (p + 1 < n and Lmax[p + 1] > L):
            out.append((p, L)); p += L
        else:
            p += 1
    return out


def optimal_copy_intervals(s: str, min_copy: int, Lmax=None) -> list[tuple[int, int]]:
    """Minimum-code-length parse.  literal = 1 + log2(10) bits; a copy of
    length L starting at p = 1 + log2(p) + log2(L) bits (same accounting as
    c469.stats.relative_lz_bits_per_digit)."""
    Lmax = Lmax if Lmax is not None else max_match_len(s)
    n = len(s)
    lit = 1.0 + math.log2(10.0)
    INF = float("inf")
    cost = [INF] * (n + 1)
    back = [None] * (n + 1)
    cost[0] = 0.0
    for p in range(n):
        if cost[p] == INF:
            continue
        c = cost[p] + lit
        if c < cost[p + 1]:
            cost[p + 1] = c; back[p + 1] = (p, 0)
        Lm = Lmax[p]
        if Lm >= min_copy:
            base = cost[p] + 1.0 + math.log2(max(2, p))
            for L in range(min_copy, Lm + 1):
                c = base + math.log2(max(2, L))
                if c < cost[p + L]:
                    cost[p + L] = c; back[p + L] = (p, L)
    out, q = [], n
    while q > 0:
        p, L = back[q]
        if L:
            out.append((p, L))
        q = p
    out.reverse()
    return out


def backward_copy_intervals(s: str, min_copy: int) -> list[tuple[int, int]]:
    r = s[::-1]
    iv = greedy_copy_intervals(r, min_copy)
    n = len(s)
    return [(n - (p + L), L) for p, L in iv]


def innovation_mask(n: int, intervals) -> list[bool]:
    m = [True] * n
    for p, L in intervals:
        for i in range(p, min(n, p + L)):
            m[i] = False
    return m


# ---------------------------------------------------------------- residues

POLICIES = ("greedy", "lazy", "optimal", "backward")


def residues_for(s: str, min_copies=(3, 4, 5, 6, 8, 10, 12)) -> dict:
    Lmax = max_match_len(s)
    out = {}
    for mc in min_copies:
        masks = {}
        masks["greedy"] = innovation_mask(len(s), greedy_copy_intervals(s, mc, Lmax))
        masks["lazy"] = innovation_mask(len(s), lazy_copy_intervals(s, mc, Lmax))
        masks["optimal"] = innovation_mask(len(s), optimal_copy_intervals(s, mc, Lmax))
        masks["backward"] = innovation_mask(len(s), backward_copy_intervals(s, mc))
        for k, m in masks.items():
            out[f"{k}_mc{mc}"] = "".join(c for c, keep in zip(s, m) if keep)
        um = [any(masks[k][i] for k in POLICIES) for i in range(len(s))]
        out[f"union_mc{mc}"] = "".join(c for c, keep in zip(s, um) if keep)
        im = [all(masks[k][i] for k in POLICIES) for i in range(len(s))]
        out[f"intersect_mc{mc}"] = "".join(c for c, keep in zip(s, im) if keep)
    ip = lz76_innovation_positions(s)
    out["lz76_innovation"] = "".join(s[i] for i in ip)
    return out


def describe(name: str, r: str) -> dict:
    b = [r]
    return dict(
        name=name, n=len(r),
        unigram_H=round(S.unigram_H(b), 4),
        ic=round(S.ic(b), 5),
        h4=round(S.cond_entropy(b, 4), 4) if len(r) > 200 else None,
        bigram_chi2=round(S.bigram_chi2(b), 1),
        n_missing_bigrams=len(S.missing_bigrams(b)),
        lz76=S.lz76_factors(r),
        distinct_4grams=S.distinct_ngrams(b, 4),
        digit_freq={d: r.count(d) for d in "0123456789"},
    )


def main():
    master = (REPO / "data" / "master_v1.txt").read_text().strip()
    concat = "".join(load_books(with_kharos=False).books)
    res = {}
    for src_name, s in (("master", master), ("concat", concat)):
        rs = residues_for(s)
        for k, v in rs.items():
            res[f"{src_name}:{k}"] = v
    baseline = (REPO / "data" / "seed_estimate.txt").read_text().strip()
    res["PR_seed_estimate"] = baseline

    rows = [describe(k, v) for k, v in res.items()]
    (HERE / "residues.json").write_text(json.dumps(
        {"residues": res, "stats": rows}, indent=1))
    hdr = f"{'residue':34s} {'n':>6s} {'H':>7s} {'IC':>8s} {'h4':>7s} {'chi2':>8s} {'lz76':>5s}"
    print(hdr)
    for r in sorted(rows, key=lambda x: -x["n"]):
        print(f"{r['name']:34s} {r['n']:6d} {r['unigram_H']:7.4f} {r['ic']:8.5f} "
              f"{str(r['h4']):>7s} {r['bigram_chi2']:8.1f} {r['lz76']:5d}")


if __name__ == "__main__":
    main()
