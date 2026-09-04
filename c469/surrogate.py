"""Null models.

A "pattern" in 469 means nothing until it is scored against these.  The most
important generator is CopyPasteMutate: the corpus's LZ76 factor count (608)
sits far below every fixed-order Markov surrogate, so the honest null is not
"random digits" but "one seed string, cut up and pasted with mutation" -- which
is exactly what the repo's own alignment work describes.
"""
from __future__ import annotations

import random
from collections import defaultdict
from dataclasses import dataclass

DIGITS = "0123456789"


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
        s = str(v).replace(".", "").replace("-", "")
        return s[:n + 10]

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


#: The families a finding must clear before it may be called a finding.
DEFAULT_FAMILIES = [
    Shuffle(),
    MarkovK(2),
    MarkovK(3),
    BlockShuffle(20),
    CopyPasteMutate(),
]

ALL_FAMILIES = DEFAULT_FAMILIES + [IID(), MarkovK(1), MarkovK(4), MarkovK(5),
                                   BlockShuffle(5), BlockShuffle(50),
                                   OtherCorpora("pi")]


def get(name: str) -> Surrogate:
    for f in ALL_FAMILIES:
        if f.name == name:
            return f
    raise KeyError(name)
