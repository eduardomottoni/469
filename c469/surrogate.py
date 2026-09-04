"""Null models.

A "pattern" in 469 means nothing until it is scored against these.  The most
important generator is CopyPasteMutate: the corpus's LZ76 factor count (608)
sits far below every fixed-order Markov surrogate, so the honest null is not
"random digits" but "one seed string, cut up and pasted with mutation" -- which
is exactly what the repo's own alignment work describes.
"""
from __future__ import annotations

import math
import random
from collections import defaultdict
from dataclasses import dataclass, asdict
from pathlib import Path

DIGITS = "0123456789"

#: on-disk home for the constants' digit expansions
_DIGIT_DIR = Path(__file__).resolve().parent.parent / "data" / "external"

#: memo for OtherCorpora.  The constants never change, only the requested
#: length; recomputing pi to 11k places on every generate() call was costing
#: ~10 s per surrogate, which is the entire null-calibration budget.
_DIGIT_CACHE: dict = {}


class Surrogate:
    """generate(real_books, seed) -> list[str] with the same shape as real."""
    name = "base"

    def generate(self, books: list[str], seed: int) -> list[str]:
        raise NotImplementedError


class IID(Surrogate):
    name = "IID"

    def generate(self, books, seed):
        rng = random.Random(seed)
        pool = "".join(books)
        return ["".join(rng.choice(pool) for _ in range(len(b))) for b in books]


class Shuffle(Surrogate):
    """Exact unigram match, all higher-order structure destroyed."""
    name = "Shuffle"

    def generate(self, books, seed):
        rng = random.Random(seed)
        pool = list("".join(books))
        rng.shuffle(pool)
        out, i = [], 0
        for b in books:
            out.append("".join(pool[i:i + len(b)]))
            i += len(b)
        return out


@dataclass
class MarkovK(Surrogate):
    k: int = 3
    alpha: float = 0.0

    @property
    def name(self):
        return f"Markov{self.k}"

    def generate(self, books, seed):
        rng = random.Random(seed)
        t = defaultdict(list)
        starts = []
        for b in books:
            if len(b) > self.k:
                starts.append(b[:self.k])
            for i in range(len(b) - self.k):
                t[b[i:i + self.k]].append(b[i + self.k])
        out = []
        for b in books:
            s = rng.choice(starts)[:len(b)]
            while len(s) < len(b):
                key = s[-self.k:]
                nxt = t.get(key)
                if not nxt:
                    key = rng.choice(list(t))
                    nxt = t[key]
                s += rng.choice(nxt)
            out.append(s[:len(b)])
        return out


@dataclass
class BlockShuffle(Surrogate):
    """Preserves local structure of length L, destroys long-range copying.

    The correct null for "is this long repeat meaningful".
    """
    L: int = 20

    @property
    def name(self):
        return f"BlockShuffle{self.L}"

    def generate(self, books, seed):
        rng = random.Random(seed)
        s = "".join(books)
        blocks = [s[i:i + self.L] for i in range(0, len(s), self.L)]
        rng.shuffle(blocks)
        s = "".join(blocks)
        out, i = [], 0
        for b in books:
            out.append(s[i:i + len(b)])
            i += len(b)
        return out


@dataclass
class CopyPasteMutate(Surrogate):
    """The generative form of the "no plaintext" hypothesis.

    A seed string is drawn from a low-order Markov model of the real corpus;
    each book is then built from 1-3 substrings of that seed, each optionally
    rotated at a random cut point (the documented B42/B43 relation is a
    rotation, not a mismatch) with occasional single-digit deletion.
    """
    seed_len: int = 3500
    seed_order: int = 2
    p_rotate: float = 0.15
    p_delete: float = 0.004
    max_segments: int = 3

    name = "CopyPasteMutate"

    def make_seed(self, books, rng: random.Random) -> str:
        k = self.seed_order
        t = defaultdict(list)
        for b in books:
            for i in range(len(b) - k):
                t[b[i:i + k]].append(b[i + k])
        s = rng.choice(list(t))
        while len(s) < self.seed_len:
            key = s[-k:]
            nxt = t.get(key) or t[rng.choice(list(t))]
            s += rng.choice(nxt)
        return s

    def generate(self, books, seed):
        rng = random.Random(seed)
        src = self.make_seed(books, rng)
        out = []
        for b in books:
            target = len(b)
            nseg = rng.randint(1, self.max_segments)
            lens = [max(8, target // nseg)] * nseg
            lens[-1] += target - sum(lens)
            parts = []
            for L in lens:
                L = max(1, min(L, len(src)))
                i = rng.randrange(0, max(1, len(src) - L))
                frag = src[i:i + L]
                if rng.random() < self.p_rotate and len(frag) > 2:
                    c = rng.randrange(1, len(frag))
                    frag = frag[c:] + frag[:c]
                frag = "".join(ch for ch in frag if rng.random() >= self.p_delete)
                parts.append(frag)
            s = "".join(parts)
            while len(s) < target:
                s += src[rng.randrange(len(src))]
            out.append(s[:target])
        return out


class PermuteBooks(Surrogate):
    """Book identities permuted; for leave-k-out replication checks."""
    name = "PermuteBooks"

    def generate(self, books, seed):
        rng = random.Random(seed)
        out = list(books)
        rng.shuffle(out)
        return out


@dataclass
class OtherCorpora(Surrogate):
    """Digits of pi / e / sqrt2 -- the "would this method find a message in
    anything" control."""
    which: str = "pi"

    @property
    def name(self):
        return f"Digits_{self.which}"

    def _digits(self, n: int) -> str:
        hit = _DIGIT_CACHE.get(self.which)
        if hit is None:
            p = _DIGIT_DIR / f"digits_{self.which}.txt"
            if p.exists():
                hit = _DIGIT_CACHE[self.which] = p.read_text().strip()
        if hit is not None and len(hit) >= n + 10:
            return hit[:n + 10]
        from decimal import Decimal, getcontext
        getcontext().prec = n + 20
        if self.which == "pi":
            # Chudnovsky is overkill; Machin-like with Decimal is plenty
            def arctan_inv(x):
                total = term = Decimal(1) / x
                x2 = x * x
                i = 1
                while term:
                    term /= -x2
                    total += term / (2 * i + 1)
                    i += 1
                return total
            v = 16 * arctan_inv(Decimal(5)) - 4 * arctan_inv(Decimal(239))
        elif self.which == "e":
            v, term = Decimal(1), Decimal(1)
            for i in range(1, n + 30):
                term /= i
                v += term
                if term == 0:
                    break
        else:
            v = Decimal(2).sqrt()
        s = str(v).replace(".", "").replace("-", "")[:n + 10]
        _DIGIT_CACHE[self.which] = s
        try:
            _DIGIT_DIR.mkdir(parents=True, exist_ok=True)
            (_DIGIT_DIR / f"digits_{self.which}.txt").write_text(s)
        except OSError:
            pass
        return s

    def generate(self, books, seed):
        total = sum(len(b) for b in books)
        d = self._digits(total + 50)
        off = (seed * 7) % max(1, len(d) - total)
        d = d[off:off + total] if len(d) >= off + total else d[:total]
        while len(d) < total:
            d += d
        out, i = [], 0
        for b in books:
            out.append(d[i:i + len(b)])
            i += len(b)
        return out


_MARKOV_CACHE: dict = {}


def _markov_table(books, k: int) -> dict:
    """Cached order-k successor table, keyed by the book set and order."""
    key = (k, hash(tuple(books)))
    t = _MARKOV_CACHE.get(key)
    if t is None:
        d = defaultdict(list)
        for b in books:
            for i in range(len(b) - k):
                d[b[i:i + k]].append(b[i + k])
        t = {kk: "".join(v) for kk, v in d.items()}
        _MARKOV_CACHE[key] = t
    return t


# --------------------------------------------------------------------------
# The ABC-fitted copy-paste model (family E).  Defaults are the posterior
# medians from experiments/e_e_nullproc/abc.py (4,000 simulations, 9-statistic
# summary).  Its posterior predictive covers 8 of the 9 summaries of the real
# corpus; only the 279-digit cross-book repeat sits outside (z = +2.0), and that
# one repeat is the documented B64/B65 near-duplicate.
#
# THIS, not the unfitted CopyPasteMutate above, is the null a claim about 469
# has to clear.
@dataclass
class CopyPasteMutateFitted:
    seed_len: int = 2602
    seed_order: int = 3
    seg_lambda: float = 0.26815
    p_rotate: float = 0.29446
    p_delete: float = 0.00091
    p_sub: float = 0.00148
    p_reuse: float = 0.3901
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


#: The families a finding must clear before it may be called a finding.
DEFAULT_FAMILIES = [
    Shuffle(),
    MarkovK(2),
    MarkovK(3),
    BlockShuffle(20),
    CopyPasteMutate(),
    CopyPasteMutateFitted(),
]

ALL_FAMILIES = DEFAULT_FAMILIES + [IID(), MarkovK(1), MarkovK(4), MarkovK(5),
                                   BlockShuffle(5), BlockShuffle(50),
                                   OtherCorpora("pi")]


def get(name: str) -> Surrogate:
    for f in ALL_FAMILIES:
        if f.name == name:
            return f
    raise KeyError(name)
