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
def _hill(stream, key, table, pos_start, pos_end, positions, n_sym,
          max_rounds, seed, n_kicks, kick_size):
    """One restart: best-improvement hill climb with annealing kicks."""
    n = stream.shape[0]
    np.random.seed(seed)
    best_key = key.copy()
    best = _full_score(stream, key, table)
    cur = best
    kick = 0
    while True:
        improved = True
        rounds = 0
        while improved and rounds < max_rounds:
            improved = False
            rounds += 1
            for s in range(n_sym):
                if pos_start[s] == pos_end[s]:
                    continue
                old = key[s]
                base = _delta_windows(pos_start, pos_end, positions, s,
                                      stream, key, table, n)
                bestl = old
                bestg = 0.0
                for L in range(27):
                    if L == old:
                        continue
                    key[s] = L
                    g = _delta_windows(pos_start, pos_end, positions, s,
                                       stream, key, table, n) - base
                    if g > bestg:
                        bestg = g
                        bestl = L
                key[s] = bestl
                if bestl != old:
                    cur += bestg
                    improved = True
        cur = _full_score(stream, key, table)   # exact, kills accumulated drift
        if cur > best:
            best = cur
            for s in range(n_sym):
                best_key[s] = key[s]
        kick += 1
        if kick > n_kicks:
            break
        # annealing kick: perturb from the best key found so far
        for s in range(n_sym):
            key[s] = best_key[s]
        for _ in range(kick_size):
            s = np.random.randint(0, n_sym)
            key[s] = np.random.randint(0, 27)
        cur = _full_score(stream, key, table)
    return best, best_key


def solve(stream: np.ndarray, table: np.ndarray, n_restarts: int = 60,
          max_rounds: int = 40, n_kicks: int = 8, kick_size: int = 3,
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
        sc, kk = _hill(stream, k, table, pos_start, pos_end, order, n_sym,
                       max_rounds, int(rng.integers(1, 2 ** 31 - 1)),
                       n_kicks, kick_size)
        if sc > best:
            best, best_key = sc, kk.copy()
    npc = best / max(1, stream.shape[0] - 4)
    pt = "".join(CHARS[best_key[s]] for s in stream)
    return npc, best_key, pt


def load_table(name: str):
    from pathlib import Path
    p = Path(__file__).resolve().parents[2] / "data" / "external" / f"lm5_{name}.npz"
    return np.ascontiguousarray(np.load(p)["table"])
