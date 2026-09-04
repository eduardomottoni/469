"""The shared measurement vocabulary.

Every number reported by any experiment must come from here.  That is what
makes results from different attack families comparable.
"""
from __future__ import annotations

import math
from collections import Counter, defaultdict

DIGITS = "0123456789"


# ---------------------------------------------------------------- entropy / IC

def ngram_counts(seq, n: int) -> Counter:
    """n-gram counts.  Pass a list of books to avoid counting n-grams that
    straddle a book boundary -- those are artifacts of concatenation, and they
    are what hides the corpus's single forbidden bigram `07`."""
    if isinstance(seq, str):
        seq = [seq]
    c: Counter = Counter()
    for s in seq:
        for i in range(len(s) - n + 1):
            c[s[i:i + n]] += 1
    return c


def _H(c: Counter) -> float:
    t = sum(c.values())
    if not t:
        return 0.0
    return -sum((v / t) * math.log2(v / t) for v in c.values())


def block_entropy(seq, n: int) -> float:
    """H_n, the entropy of n-grams (bits per n-gram)."""
    return _H(ngram_counts(seq, n))


def unigram_H(seq) -> float:
    return block_entropy(seq, 1)


def cond_entropy(seq, n: int) -> float:
    """h_n = H_n - H_{n-1}, bits per digit given n-1 predecessors."""
    if n <= 1:
        return block_entropy(seq, 1)
    return block_entropy(seq, n) - block_entropy(seq, n - 1)


def ic(seq) -> float:
    """Index of coincidence.  Uniform base-10 = 0.100."""
    c = ngram_counts(seq, 1)
    n = sum(c.values())
    if n < 2:
        return 0.0
    return sum(v * (v - 1) for v in c.values()) / (n * (n - 1))


def distinct_ngrams(seq, n: int) -> int:
    return len(ngram_counts(seq, n))


def bigram_chi2(seq) -> float:
    """Chi-square against the independence model.  81 df."""
    c1 = ngram_counts(seq, 1)
    n = sum(c1.values())
    c2 = ngram_counts(seq, 2)
    t2 = sum(c2.values())
    out = 0.0
    for a in DIGITS:
        for b in DIGITS:
            e = t2 * (c1[a] / n) * (c1[b] / n)
            if e > 0:
                out += (c2[a + b] - e) ** 2 / e
    return out


def missing_bigrams(seq) -> list[str]:
    c = ngram_counts(seq, 2)
    return [a + b for a in DIGITS for b in DIGITS if not c[a + b]]


def positional_chi2(seq, mod: int) -> float:
    """Is the digit distribution position-dependent mod k?  df = 9(k-1)."""
    if isinstance(seq, str):
        seq = [seq]
    c1 = ngram_counts(seq, 1)
    n = sum(c1.values())
    tab = [Counter() for _ in range(mod)]
    for s in seq:
        for i, ch in enumerate(s):
            tab[i % mod][ch] += 1
    out = 0.0
    for r in range(mod):
        tot = sum(tab[r].values())
        for d in DIGITS:
            e = tot * c1[d] / n
            if e > 0:
                out += (tab[r][d] - e) ** 2 / e
    return out


# ------------------------------------------------------------- complexity

def lz76_factors(s: str) -> int:
    """Lempel-Ziv 1976 factor count: the exhaustive-history complexity.

    The discriminating statistic for 469: the real corpus sits far below any
    fixed-order Markov surrogate because it is built by long-range copy-paste.
    """
    n = len(s)
    i = 0
    k = 0
    while i < n:
        L = 1
        # longest prefix of s[i:] that already occurs in s[:i]
        while i + L <= n and s[i:i + L] in s[:i]:
            L += 1
        L = max(1, L - 1)
        k += 1
        i += L
    return k


def lz76_stats(s: str) -> dict:
    n = len(s)
    f = lz76_factors(s)
    return {"factors": f, "length": n, "avg_factor_len": n / f if f else 0.0}


def longest_repeat(s: str) -> int:
    """Longest substring occurring at least twice (binary search + hashing)."""
    def has(L: int) -> bool:
        if L <= 0:
            return True
        seen = set()
        for i in range(len(s) - L + 1):
            g = s[i:i + L]
            if g in seen:
                return True
            seen.add(g)
        return False
    lo, hi = 0, len(s)
    while lo < hi:
        m = (lo + hi + 1) // 2
        if has(m):
            lo = m
        else:
            hi = m - 1
    return lo


def longest_cross_repeat(books) -> int:
    """Longest substring shared by two different books."""
    def has(L: int) -> bool:
        if L <= 0:
            return True
        d: dict[str, int] = {}
        for bi, b in enumerate(books):
            for i in range(len(b) - L + 1):
                g = b[i:i + L]
                if d.get(g, bi) != bi:
                    return True
                d[g] = bi
        return False
    lo, hi = 0, max((len(b) for b in books), default=0)
    while lo < hi:
        m = (lo + hi + 1) // 2
        if has(m):
            lo = m
        else:
            hi = m - 1
    return lo


def repeat_coverage(books, k: int = 20) -> float:
    """Fraction of k-mer positions whose k-mer occurs in >=2 books."""
    d: dict[str, set] = defaultdict(set)
    for bi, b in enumerate(books):
        for i in range(len(b) - k + 1):
            d[b[i:i + k]].add(bi)
    tot = cov = 0
    for bi, b in enumerate(books):
        for i in range(len(b) - k + 1):
            tot += 1
            if len(d[b[i:i + k]]) >= 2:
                cov += 1
    return cov / tot if tot else 0.0


# ------------------------------------------------------------- code / tokens

def kraft_sum(codebook) -> float:
    """Sum 10^-|c| over codewords.  <=1 for a prefix code, ==1 if complete."""
    return sum(10.0 ** -len(c) for c in codebook)


def is_prefix_free(codebook) -> bool:
    cs = sorted(codebook, key=len)
    for i, a in enumerate(cs):
        for b in cs[i + 1:]:
            if b.startswith(a):
                return False
    return True


def token_zipf_slope(tokens) -> tuple[float, float]:
    """Least-squares slope s and R^2 of log f vs log rank.  Language: s ~ 1."""
    c = Counter(tokens)
    f = sorted(c.values(), reverse=True)
    if len(f) < 5:
        return 0.0, 0.0
    xs = [math.log(i + 1) for i in range(len(f))]
    ys = [math.log(v) for v in f]
    mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    sxx = sum((x - mx) ** 2 for x in xs)
    slope = sxy / sxx if sxx else 0.0
    yhat = [my + slope * (x - mx) for x in xs]
    ss_res = sum((y - h) ** 2 for y, h in zip(ys, yhat))
    ss_tot = sum((y - my) ** 2 for y in ys)
    r2 = 1 - ss_res / ss_tot if ss_tot else 0.0
    return -slope, r2


def heaps_beta(tokens) -> float:
    """Vocabulary growth exponent V = K N^beta.  Language: 0.4-0.6."""
    seen: set = set()
    xs, ys = [], []
    for i, t in enumerate(tokens, 1):
        seen.add(t)
        if i % max(1, len(tokens) // 50) == 0:
            xs.append(math.log(i))
            ys.append(math.log(len(seen)))
    if len(xs) < 5:
        return 0.0
    mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
    sxx = sum((x - mx) ** 2 for x in xs)
    return (sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sxx) if sxx else 0.0


# ------------------------------------------------------------- model fitting

def markov_logprob(train, test, k: int, alpha: float = 0.5) -> float:
    """Bits per digit of `test` under an order-k Markov model fitted on `train`.

    train/test are sequences of strings (books), so contexts never cross books.
    """
    ctx: dict[str, Counter] = defaultdict(Counter)
    for b in train:
        for i in range(len(b)):
            ctx[b[max(0, i - k):i]][b[i]] += 1
    bits = 0.0
    n = 0
    for b in test:
        for i in range(len(b)):
            c = ctx[b[max(0, i - k):i]]
            tot = sum(c.values())
            p = (c[b[i]] + alpha) / (tot + alpha * 10)
            bits -= math.log2(p)
            n += 1
    return bits / n if n else float("inf")


def held_out_bits_per_digit(books, k: int, alpha: float = 0.5) -> float:
    """Leave-one-book-out mean bits/digit under an order-k Markov model."""
    tot, n = 0.0, 0
    for i in range(len(books)):
        train = [b for j, b in enumerate(books) if j != i]
        bpd = markov_logprob(train, [books[i]], k, alpha)
        tot += bpd * len(books[i])
        n += len(books[i])
    return tot / n if n else float("inf")


def summary_vector(books) -> dict:
    """The six-statistic fingerprint used for ABC fitting in family E."""
    s = "".join(books)
    return {
        "lz76_factors": lz76_factors(s),
        "distinct_4grams": distinct_ngrams(s, 4),
        "longest_cross_repeat": longest_cross_repeat(books),
        "n_books": len(books),
        "mean_book_len": sum(len(b) for b in books) / len(books),
        "sd_book_len": (sum((len(b) - sum(map(len, books)) / len(books)) ** 2
                            for b in books) / len(books)) ** 0.5,
        "ic": ic(s),
        "unigram_H": unigram_H(s),
    }
