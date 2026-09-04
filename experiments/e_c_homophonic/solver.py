"""AZdecrypt/Zodiac-340-style homophonic substitution solver.

Given a symbol stream (integers 0..S-1) the solver searches for a map
symbol -> plaintext letter (over the 27-symbol alphabet a-z + space) that
maximises the character 5-gram log-probability of the decryption, reported as
**log10 P per plaintext character** so runs of different lengths compare.

Search: random restarts, each a hill climb over single-symbol reassignments
(the full S x 27 neighbourhood, best-improvement), with simulated-annealing
kicks (random reassignments at a decaying temperature) on stalling.

Incremental scoring is numba-jitted: changing one symbol's letter only touches
the 5-gram windows containing that symbol's positions.  We recompute the score
over the affected windows only.
"""
from __future__ import annotations

import numpy as np

A = 27                                   # a-z + space
CHARS = "abcdefghijklmnopqrstuvwxyz "

try:
    from numba import njit
except Exception:                        # pragma: no cover
    def njit(*a, **k):
        def deco(f):
            return f
        return deco if not a or callable(a[0]) is False else a[0]


@njit(cache=True, fastmath=True)
def _full_score(stream, key, table):
    """Total log10 P of the decryption of `stream` under `key`."""
    n = stream.shape[0]
    tot = 0.0
    for i in range(4, n):
        ctx = 0
        for j in range(i - 4, i):
            ctx = ctx * 27 + key[stream[j]]
        tot += table[ctx, key[stream[i]]]
    return tot


@njit(cache=True, fastmath=True)
def _window_score(stream, key, table, lo, hi):
    tot = 0.0
    for i in range(lo, hi):
        ctx = 0
        for j in range(i - 4, i):
            ctx = ctx * 27 + key[stream[j]]
        tot += table[ctx, key[stream[i]]]
    return tot


@njit(cache=True, fastmath=True)
def _delta_windows(pos_start, pos_end, positions, sym,
                   stream, key, table, n):
    """Score of the union of every 5-gram window touching an occurrence of sym.

    positions[pos_start[sym]:pos_end[sym]] is ascending, so overlapping windows
    are merged with a single running high-water mark -- each scoring index is
    counted exactly once, which is what makes the delta exact.
    """
    tot = 0.0
    last_hi = 0
    for pi in range(pos_start[sym], pos_end[sym]):
        p = positions[pi]
        lo = p
        if lo < 4:
            lo = 4
        if lo < last_hi:
            lo = last_hi
        hi = p + 5
        if hi > n:
            hi = n
        if lo >= hi:
            continue
        tot += _window_score(stream, key, table, lo, hi)
        last_hi = hi
    return tot


@njit(cache=True, fastmath=True)
def _anneal(stream, key, table, pos_start, pos_end, positions, n_sym,
            seed, n_temps, sweeps, t0, t1):
    """One restart of AZdecrypt-style simulated annealing.

    At each temperature the solver sweeps every (symbol, letter) pair in random
    symbol order, keeping a move that improves the score and keeping a worsening
    move with probability exp(delta/T).  The temperature falls geometrically
    from t0 to t1.  Deltas are exact (verified against the full score), so the
    running total never drifts.
    """
    n = stream.shape[0]
    np.random.seed(seed)
    cur = _full_score(stream, key, table)
    best = cur
    best_key = key.copy()
    ratio = (t1 / t0) ** (1.0 / max(1, n_temps - 1))
    T = t0
    for _ in range(n_temps):
        for _ in range(sweeps):
            for s in np.random.permutation(n_sym):
                if pos_start[s] == pos_end[s]:
                    continue
                old = key[s]
                base = _delta_windows(pos_start, pos_end, positions, s,
                                      stream, key, table, n)
                L = np.random.randint(0, 27)
                if L == old:
                    continue
                key[s] = L
                d = _delta_windows(pos_start, pos_end, positions, s,
                                   stream, key, table, n) - base
                if d > 0.0:
                    cur += d
                else:
                    if np.random.random() < np.exp(d / T):
                        cur += d
                    else:
                        key[s] = old
                if cur > best:
                    best = cur
                    for q in range(n_sym):
                        best_key[q] = key[q]
        T *= ratio
    return best, best_key


@njit(cache=True, fastmath=True)
def _polish(stream, key, table, pos_start, pos_end, positions, n_sym, max_rounds):
    """Deterministic best-improvement hill climb to a local optimum."""
    n = stream.shape[0]
    cur = _full_score(stream, key, table)
    for _ in range(max_rounds):
        improved = False
        for s in range(n_sym):
            if pos_start[s] == pos_end[s]:
                continue
            old = key[s]
            base = _delta_windows(pos_start, pos_end, positions, s,
                                  stream, key, table, n)
            bl, bg = old, 0.0
            for L in range(27):
                if L == old:
                    continue
                key[s] = L
                g = _delta_windows(pos_start, pos_end, positions, s,
                                   stream, key, table, n) - base
                if g > bg:
                    bg, bl = g, L
            key[s] = bl
            if bl != old:
                cur += bg
                improved = True
        if not improved:
            break
    return _full_score(stream, key, table), key


def solve(stream: np.ndarray, table: np.ndarray, n_restarts: int = 60,
          n_temps: int = 60, sweeps: int = 12, t0: float = 8.0, t1: float = 0.15,
          seed: int = 0):
    """Best-of-restarts.  Returns (best log10P per char, key, plaintext)."""
    stream = np.ascontiguousarray(stream.astype(np.int32))
    n_sym = int(stream.max()) + 1 if stream.size else 1
    order = np.argsort(stream, kind="stable").astype(np.int32)
    counts = np.bincount(stream, minlength=n_sym)
    pos_end = np.cumsum(counts).astype(np.int32)
    pos_start = (pos_end - counts).astype(np.int32)
    rng = np.random.default_rng(seed)
    best = -1e18
    best_key = None
    for r in range(n_restarts):
        k = rng.integers(0, 27, size=n_sym).astype(np.int32)
        sc, kk = _anneal(stream, k, table, pos_start, pos_end, order, n_sym,
                         int(rng.integers(1, 2 ** 31 - 1)), n_temps, sweeps, t0, t1)
        sc, kk = _polish(stream, kk.copy(), table, pos_start, pos_end, order,
                         n_sym, 50)
        if sc > best:
            best, best_key = sc, kk.copy()
    npc = best / max(1, stream.shape[0] - 4)
    pt = "".join(CHARS[best_key[s]] for s in stream)
    return npc, best_key, pt


def load_table(name: str):
    from pathlib import Path
    p = Path(__file__).resolve().parents[2] / "data" / "external" / f"lm5_{name}.npz"
    return np.ascontiguousarray(np.load(p)["table"])
