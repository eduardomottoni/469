"""Shared machinery for the 2026 seed attack.

Three things live here:

1. `extract_residue` -- the residue policies of residue.py, but driven by the
   fast suffix-automaton Lmax so the *identical* extraction can be run on
   hundreds of surrogate corpora (end-to-end nulls).
2. Null families.  Two tiers, and the distinction is the whole lesson of the
   PR's `Markov3_digits` false positive:
     * END-TO-END  -- a surrogate *corpus* from c469.surrogate is pushed through
       the identical extraction.  Controls the pipeline, does NOT control the
       residue's length or digit inventory.
     * MATCHED     -- the real residue itself is shuffled / order-k resampled.
       Exact length, exact (or near-exact) digit inventory, arrangement
       destroyed.  This is the null that decides a claim.
   Every table in SEED_ATTACK.md reports both, and flags the length gap.
3. Plaintext injectors, so every statistic's power is measured before its
   null result is believed.
"""
from __future__ import annotations

import math
import random
import sys
from collections import Counter, defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(HERE))

from c469 import stats as S                       # noqa: E402
from c469 import surrogate as U                   # noqa: E402
from c469.corpus import load_books                # noqa: E402
from fastlz import max_match_len                  # noqa: E402


# ------------------------------------------------------------------ residues

def _greedy(Lmax, n, mc):
    iv, p = [], 0
    while p < n:
        L = Lmax[p]
        if L >= mc:
            iv.append((p, L)); p += L
        else:
            p += 1
    return iv


def _lazy(Lmax, n, mc):
    iv, p = [], 0
    while p < n:
        L = Lmax[p]
        if L >= mc and not (p + 1 < n and Lmax[p + 1] > L):
            iv.append((p, L)); p += L
        else:
            p += 1
    return iv


def _optimal(Lmax, n, mc):
    lit = 1.0 + math.log2(10.0)
    INF = float("inf")
    cost = [INF] * (n + 1); back = [None] * (n + 1); cost[0] = 0.0
    for p in range(n):
        cp = cost[p]
        if cp == INF:
            continue
        c = cp + lit
        if c < cost[p + 1]:
            cost[p + 1] = c; back[p + 1] = (p, 0)
        Lm = Lmax[p]
        if Lm >= mc:
            base = cp + 1.0 + math.log2(max(2, p))
            for L in range(mc, Lm + 1):
                c = base + math.log2(L)
                if c < cost[p + L]:
                    cost[p + L] = c; back[p + L] = (p, L)
    iv, q = [], n
    while q > 0:
        p, L = back[q]
        if L:
            iv.append((p, L))
        q = p
    return iv


def _mask(n, iv):
    m = bytearray(b"\x01") * n
    for p, L in iv:
        for i in range(p, min(n, p + L)):
            m[i] = 0
    return m


def extract_residue(s: str, min_copy: int = 8, policy: str = "union") -> str:
    """policy in {greedy, lazy, optimal, backward, union, intersect}."""
    n = len(s)
    if policy == "lz76_innovation":
        # the PR's estimate A: the one new digit terminating each LZ76 factor
        out, i = [], 0
        while i < n:
            L = 1
            while i + L <= n and s[i:i + L] in s[:i]:
                L += 1
            L = max(1, L - 1)
            out.append(s[i + L - 1])
            i += L
        return "".join(out)
    Lmax = max_match_len(s)
    if policy in ("greedy", "lazy", "optimal"):
        m = _mask(n, {"greedy": _greedy, "lazy": _lazy, "optimal": _optimal}[policy](Lmax, n, min_copy))
    elif policy == "backward":
        r = s[::-1]
        Lr = max_match_len(r)
        iv = [(n - (p + L), L) for p, L in _greedy(Lr, n, min_copy)]
        m = _mask(n, iv)
    else:
        ms = [_mask(n, _greedy(Lmax, n, min_copy)),
              _mask(n, _lazy(Lmax, n, min_copy)),
              _mask(n, _optimal(Lmax, n, min_copy))]
        r = s[::-1]
        Lr = max_match_len(r)
        ms.append(_mask(n, [(n - (p + L), L) for p, L in _greedy(Lr, n, min_copy)]))
        if policy == "union":
            m = bytearray(1 if any(x[i] for x in ms) else 0 for i in range(n))
        else:
            m = bytearray(1 if all(x[i] for x in ms) else 0 for i in range(n))
    return "".join(c for c, k in zip(s, m) if k)


# --------------------------------------------------------------------- nulls

class EndToEnd:
    """A c469.surrogate family pushed through the identical extraction."""

    def __init__(self, fam, min_copy: int, policy: str):
        self.fam, self.min_copy, self.policy = fam, min_copy, policy
        self.name = f"E2E:{fam.name}"

    def draw(self, books, seed) -> str:
        sur = self.fam.generate(list(books), seed)
        return extract_residue("".join(sur), self.min_copy, self.policy)


class ResidueShuffle:
    """Exact length, exact digit inventory, arrangement destroyed."""
    name = "ResidueShuffle"

    def __init__(self, residue): self.r = residue

    def draw(self, books, seed):
        rng = random.Random(seed)
        x = list(self.r); rng.shuffle(x)
        return "".join(x)


class ResidueMarkov:
    """Order-k resample of the residue itself: exact length, near-exact
    inventory, only sequential arrangement destroyed.  The digit-stream analogue
    of Family C's `Markov3_symbols`, which is the null that decided that family."""

    def __init__(self, residue, k=3):
        self.r, self.k = residue, k
        self.name = f"ResidueMarkov{k}"
        d = defaultdict(list)
        for i in range(len(residue) - k):
            d[residue[i:i + k]].append(residue[i + k])
        self.tab = {a: "".join(b) for a, b in d.items()}
        self.keys = list(self.tab)

    def draw(self, books, seed):
        rng = random.Random(seed)
        k, n = self.k, len(self.r)
        s = rng.choice(self.keys)
        while len(s) < n:
            nx = self.tab.get(s[-k:])
            s += rng.choice(nx) if nx else rng.choice(self.keys)
        return s[:n]


def default_nulls(residue: str, min_copy: int, policy: str):
    e2e = [EndToEnd(f, min_copy, policy) for f in U.DEFAULT_FAMILIES]
    return e2e + [ResidueShuffle(residue), ResidueMarkov(residue, 3)]


# ---------------------------------------------------------------- statistics
# Pre-registered.  Name -> (callable, direction).  Nothing outside this dict is
# scored, and it is written before any null is drawn.

def st_ic(r): return S.ic([r])


def st_bigram_chi2_pd(r): return S.bigram_chi2([r]) / max(1, len(r))


def st_lz76_pd(r): return S.lz76_factors(r) / max(1, len(r))


def _ic_of(x):
    n = len(x)
    if n < 2:
        return 0.0
    c = Counter(x)
    return sum(v * (v - 1) for v in c.values()) / (n * (n - 1))


def st_periodic_ic_max(r):
    best = 0.0
    for p in range(2, 41):
        cols = [r[i::p] for i in range(p)]
        cols = [c for c in cols if len(c) >= 8]
        if not cols:
            continue
        v = sum(_ic_of(c) * len(c) for c in cols) / sum(len(c) for c in cols)
        best = max(best, v)
    return best


def st_kasiski(r):
    """Max over d in 2..40 of the share of repeated-4-gram distances divisible
    by d, minus the 1/d expected under no periodicity."""
    pos = defaultdict(list)
    for i in range(len(r) - 3):
        pos[r[i:i + 4]].append(i)
    dists = []
    for v in pos.values():
        for a in range(len(v) - 1):
            dists.append(v[a + 1] - v[a])
    if len(dists) < 10:
        return 0.0
    return max((sum(1 for d in dists if d % m == 0) / len(dists)) - 1.0 / m
               for m in range(2, 41))


def st_diff_ic(r):
    return _ic_of([(int(r[i + 1]) - int(r[i])) % 10 for i in range(len(r) - 1)])


def _pairs(r, off, rev=False):
    out = []
    for i in range(off, len(r) - 1, 2):
        a, b = r[i], r[i + 1]
        out.append(int(b + a) if rev else int(a + b))
    return out


A1Z26_READINGS = [(0, False), (1, False), (0, True), (1, True)]


def st_a1z26_frac(r):
    return max(sum(1 for v in _pairs(r, o, rv) if 1 <= v <= 26) / max(1, len(_pairs(r, o, rv)))
               for o, rv in A1Z26_READINGS)


def st_a1z26_chi2(r):
    """English letter-frequency chi2 of the pairs that fall in 1..26, under the
    reading that fits best.  Direction: LESS."""
    best = float("inf")
    for o, rv in A1Z26_READINGS:
        vs = [v for v in _pairs(r, o, rv) if 1 <= v <= 26]
        if len(vs) < 30:
            continue
        c = Counter(vs)
        best = min(best, S.letter_chi2(list(c.values()), "en") / len(vs))
    return best if best < float("inf") else 99.0


ASCII_OK = set([32] + list(range(65, 91)) + list(range(97, 123)))


def st_ascii_frac(r):
    best = 0.0
    for o in (0, 1, 2):
        vs = [int(r[i:i + 3]) for i in range(o, len(r) - 2, 3)]
        if not vs:
            continue
        best = max(best, sum(1 for v in vs if v in ASCII_OK) / len(vs))
    return best


def _valid_date(a, b, c, order):
    if order == "ddmmyy":
        d, m, y = a, b, c
    elif order == "mmddyy":
        m, d, y = a, b, c
    else:
        y, m, d = a, b, c
    if not (1 <= m <= 12 and 1 <= d <= 31):
        return False
    if m in (4, 6, 9, 11) and d > 30:
        return False
    if m == 2 and d > 29:
        return False
    return True


def st_date_frac(r):
    best = 0.0
    for o in range(6):
        blocks = [r[i:i + 6] for i in range(o, len(r) - 5, 6)]
        blocks = [b for b in blocks if len(b) == 6]
        if not blocks:
            continue
        for order in ("ddmmyy", "mmddyy", "yymmdd"):
            k = sum(1 for b in blocks
                    if _valid_date(int(b[0:2]), int(b[2:4]), int(b[4:6]), order))
            best = max(best, k / len(blocks))
    return best


STATS = {
    "ic":              (st_ic, "greater"),
    "bigram_chi2_pd":  (st_bigram_chi2_pd, "greater"),
    "lz76_pd":         (st_lz76_pd, "less"),
    "periodic_ic_max": (st_periodic_ic_max, "greater"),
    "kasiski":         (st_kasiski, "greater"),
    "diff_ic":         (st_diff_ic, "greater"),
    "a1z26_frac":      (st_a1z26_frac, "greater"),
    "a1z26_chi2":      (st_a1z26_chi2, "less"),
    "ascii_frac":      (st_ascii_frac, "greater"),
    "date_frac":       (st_date_frac, "greater"),
}


# ------------------------------------------------------------ plaintext & injection

_TEXT_CACHE = {}
_WORDS = None


def _wordlist():
    """The Family C word-frequency list (wordfreq / Exquisite-Corpus), cached."""
    global _WORDS
    if _WORDS is None:
        sys.path.insert(0, str(REPO / "experiments" / "e_c_homophonic"))
        from build_lm import fold
        import wordfreq
        ws = wordfreq.top_n_list("en", 300_000)

        def ok(w):
            if not w or len(w) > 20 or " " in w:
                return False
            run = 1
            for i in range(1, len(w)):
                run = run + 1 if w[i] == w[i - 1] else 1
                if run >= 3:
                    return False
            return True
        pairs = [(fold(w, "en"), wordfreq.word_frequency(w, "en")) for w in ws]
        pairs = [(w, f) for w, f in pairs if f > 1e-8 and ok(w)]
        _WORDS = ([w for w, _ in pairs], [f for _, f in pairs])
    return _WORDS


def _synth(n_chars, seed):
    words, wts = _wordlist()
    rng = random.Random(seed)
    out, tot = [], 0
    while tot < n_chars:
        chunk = rng.choices(words, weights=wts, k=4000)
        piece = " ".join(chunk) + " "
        out.append(piece); tot += len(piece)
    return "".join(out)[:n_chars]


def english_text(n_chars: int, seed: int = 1) -> str:
    """Word-frequency-sampled English, the same source the Family C language
    models were built from (no running-text corpus is reachable from here).
    Carries real letter/bigram/word-boundary statistics."""
    if seed not in _TEXT_CACHE:
        _TEXT_CACHE[seed] = _synth(60_000, seed)
    t = _TEXT_CACHE[seed]
    while len(t) < n_chars:
        t = t + t
    return t[:n_chars]


def inj_a1z26(n, seed=1):
    t = english_text(n, seed)
    out = []
    for ch in t:
        if ch == " ":
            out.append("00")
        else:
            out.append(f"{ord(ch) - 96:02d}")
        if sum(len(x) for x in out) >= n:
            break
    return "".join(out)[:n]


def inj_ascii(n, seed=1):
    t = english_text(n, seed)
    out = []
    for ch in t:
        out.append(f"{ord(ch):03d}")
        if len(out) * 3 >= n:
            break
    return "".join(out)[:n]


def inj_dates(n, seed=1):
    rng = random.Random(seed)
    out = []
    while len(out) * 6 < n:
        m = rng.randint(1, 12)
        d = rng.randint(1, 28)
        y = rng.randint(0, 99)
        out.append(f"{d:02d}{m:02d}{y:02d}")
    return "".join(out)[:n]


def inj_vigenere(n, seed=1, period=7):
    rng = random.Random(seed)
    base = inj_a1z26(n, seed)
    key = [rng.randrange(10) for _ in range(period)]
    return "".join(str((int(c) + key[i % period]) % 10) for i, c in enumerate(base))


def inj_subst10(n, seed=1):
    """English reduced to its 10 commonest characters, then a fixed digit
    substitution: the V=10 simple-substitution hypothesis."""
    t = english_text(n * 3, seed)
    keep = [c for c, _ in Counter(t).most_common(10)]
    m = {c: str(i) for i, c in enumerate(keep)}
    return "".join(m[c] for c in t if c in keep)[:n], keep


def inj_iid(n, seed=1):
    rng = random.Random(seed)
    return "".join(str(rng.randrange(10)) for _ in range(n))


INJECTORS = {
    "a1z26":     inj_a1z26,
    "ascii":     inj_ascii,
    "dates":     inj_dates,
    "vigenere7": inj_vigenere,
    "subst10":   lambda n, seed=1: inj_subst10(n, seed)[0],
    "iid_ctrl":  inj_iid,
}


# ------------------------------------------------------------------- targets

def load_targets():
    master = (REPO / "data" / "master_v1.txt").read_text().strip()
    concat = "".join(load_books(with_kharos=False).books)
    pr = (REPO / "data" / "seed_estimate.txt").read_text().strip()
    return {
        # name: (residue, source, min_copy, policy)
        "R578_PR":       (pr, "master", 3, "lz76_innovation"),
        "R791_mc6_g":    (extract_residue(concat, 6, "greedy"), "concat", 6, "greedy"),
        "R1535_mc6_u":   (extract_residue(concat, 6, "union"), "concat", 6, "union"),
        "R2058_mc8_u":   (extract_residue(concat, 8, "union"), "concat", 8, "union"),
        "R2713_mc12_u":  (extract_residue(concat, 12, "union"), "concat", 12, "union"),
    }
