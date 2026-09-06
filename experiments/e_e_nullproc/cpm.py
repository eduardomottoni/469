"""The fitted copy-paste generator for family E.

Richer than the shipped `surrogate.CopyPasteMutate`: the shipped defaults give
~1111 LZ76 factors against the corpus's 608, so they are not yet a null that
explains 469.  Free parameters here are exactly the ones the plan lists --
seed length, seed Markov order, segment-count/length distribution, rotation
probability, deletion rate -- plus a substitution rate (the documented `864`
anomaly is a substitution, not a deletion) and a reuse probability (a book may
copy from an earlier book rather than from the seed).
"""
from __future__ import annotations

import math
import random
from collections import defaultdict
from dataclasses import dataclass, asdict

DIGITS = "0123456789"

_MARKOV_CACHE: dict = {}


def _markov_table(books, k):
    key = (id(books), k) if False else (k, hash(tuple(books)))
    t = _MARKOV_CACHE.get(key)
    if t is None:
        t = defaultdict(list)
        for b in books:
            for i in range(len(b) - k):
                t[b[i:i + k]].append(b[i + k])
        t = {kk: "".join(v) for kk, v in t.items()}
        _MARKOV_CACHE[key] = t
    return t


@dataclass
class CopyPasteMutateFitted:
    seed_len: int = 2600
    seed_order: int = 2
    seg_lambda: float = 0.6      # nseg = 1 + Poisson(seg_lambda), capped at 6
    p_rotate: float = 0.10
    p_delete: float = 0.0015
    p_sub: float = 0.0015
    p_reuse: float = 0.35        # draw a segment from an earlier book, not the seed
    min_seg: int = 12

    name = "CopyPasteMutateFitted"

    def params(self):
        return asdict(self)

    # -- seed ---------------------------------------------------------------
    def make_seed(self, books, rng):
        k = max(1, int(self.seed_order))
        t = _markov_table(books, k)
        keys = list(t)
        s = rng.choice(keys)
        L = int(self.seed_len)
        while len(s) < L:
            nxt = t.get(s[-k:])
            if not nxt:
                s += rng.choice(keys)
                continue
            s += rng.choice(nxt)
        return s[:L]

    def _pois(self, rng, lam):
        if lam <= 0:
            return 0
        L, k, p = math.exp(-lam), 0, 1.0
        while True:
            p *= rng.random()
            if p <= L:
                return k
            k += 1
            if k > 20:
                return k

    def generate(self, books, seed):
        rng = random.Random(seed)
        src = self.make_seed(books, rng)
        pool = [src]
        out = []
        for b in books:
            T = len(b)
            nseg = min(6, 1 + self._pois(rng, self.seg_lambda))
            nseg = max(1, min(nseg, max(1, T // self.min_seg)))
            cuts = sorted(rng.randrange(T) for _ in range(nseg - 1))
            lens, prev = [], 0
            for cpos in cuts + [T]:
                lens.append(cpos - prev); prev = cpos
            lens = [max(1, x) for x in lens]
            parts = []
            for Lg in lens:
                donor = src
                if len(pool) > 1 and rng.random() < self.p_reuse:
                    donor = pool[rng.randrange(1, len(pool))]
                need = Lg + 8
                if len(donor) <= need:
                    donor = donor * (need // max(1, len(donor)) + 2)
                i = rng.randrange(0, len(donor) - need)
                frag = donor[i:i + Lg]
                if rng.random() < self.p_rotate and len(frag) > 2:
                    c = rng.randrange(1, len(frag))
                    frag = frag[c:] + frag[:c]
                if self.p_delete or self.p_sub:
                    buf = []
                    for ch in frag:
                        r = rng.random()
                        if r < self.p_delete:
                            continue
                        if r < self.p_delete + self.p_sub:
                            ch = DIGITS[rng.randrange(10)]
                        buf.append(ch)
                    frag = "".join(buf)
                parts.append(frag)
            s = "".join(parts)
            while len(s) < T:
                i = rng.randrange(0, max(1, len(src) - (T - len(s)) - 1))
                s += src[i:i + (T - len(s))]
            s = s[:T]
            out.append(s)
            pool.append(s)
        return out


PRIOR = dict(
    seed_len=(400, 8000),
    seed_order=(1, 4),
    seg_lambda=(0.0, 3.0),
    p_rotate=(0.0, 0.6),
    p_delete=(0.0, 0.012),
    p_sub=(0.0, 0.012),
    p_reuse=(0.0, 0.9),
)


def sample_prior(rng):
    return dict(
        seed_len=rng.randrange(*PRIOR["seed_len"]),
        seed_order=rng.randint(*PRIOR["seed_order"]),
        seg_lambda=rng.uniform(*PRIOR["seg_lambda"]),
        p_rotate=rng.uniform(*PRIOR["p_rotate"]),
        p_delete=rng.uniform(*PRIOR["p_delete"]),
        p_sub=rng.uniform(*PRIOR["p_sub"]),
        p_reuse=rng.uniform(*PRIOR["p_reuse"]),
    )
