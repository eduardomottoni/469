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


# ------------------------------------------------- letter frequencies / codes

#: English letter frequencies (Norvig, Google Books corpus), a-z, normalised.
LETTER_FREQ_EN = {
    "e": .1249, "t": .0928, "a": .0804, "o": .0764, "i": .0757, "n": .0723,
    "s": .0651, "r": .0628, "h": .0505, "l": .0407, "d": .0382, "c": .0334,
    "u": .0273, "m": .0251, "f": .0240, "p": .0214, "g": .0187, "w": .0168,
    "y": .0166, "b": .0148, "v": .0105, "k": .0054, "x": .0023, "j": .0016,
    "q": .0012, "z": .0009,
}

#: German letter frequencies (Beutelspacher / Wikipedia), incl. umlauts and ss.
LETTER_FREQ_DE = {
    "e": .1740, "n": .0978, "i": .0755, "s": .0727, "r": .0700, "a": .0651,
    "t": .0615, "d": .0508, "h": .0476, "u": .0435, "l": .0344, "c": .0306,
    "g": .0301, "m": .0253, "o": .0251, "b": .0189, "w": .0189, "f": .0166,
    "k": .0121, "z": .0113, "p": .0079, "v": .0067, "ß": .0031,
    "ü": .0065, "ä": .0054, "ö": .0025, "j": .0027, "y": .0004,
    "x": .0003, "q": .0002,
}


def _target_vector(lang: str, m: int, floor: float = 1e-4) -> list[float]:
    """The letter-frequency target padded/truncated to exactly `m` slots.

    A codebook with more symbols than the alphabet has letters must put its
    surplus symbols on near-zero-frequency slots; padding with `floor` is what
    makes that cost show up in the chi-square instead of being ignored.
    """
    t = sorted((LETTER_FREQ_DE if lang == "de" else LETTER_FREQ_EN).values(),
               reverse=True)
    if m <= len(t):
        t = t[:m]
    else:
        t = t + [floor] * (m - len(t))
    s = sum(t)
    return [x / s for x in t]


def letter_chi2(counts, lang: str = "en", floor: float = 1e-4) -> float:
    """Chi-square of a symbol-frequency vector against German/English letter
    frequencies under the optimal one-to-one symbol->letter assignment.

    Assignment is by scipy's Hungarian algorithm on the per-cell chi-square
    contribution; with a single shared total this is provably the same as rank
    matching, but the Hungarian call keeps the code honest if the cost is ever
    made non-monotone.  Returned value is chi-square per symbol, so codebooks
    of different sizes stay comparable.
    """
    obs = sorted((float(c) for c in counts), reverse=True)
    m = len(obs)
    if m < 2:
        return float("inf")
    n = sum(obs)
    exp = [n * p for p in _target_vector(lang, m, floor)]
    try:
        import numpy as np
        from scipy.optimize import linear_sum_assignment
        o = np.asarray(obs)[:, None]
        e = np.asarray(exp)[None, :]
        cost = (o - e) ** 2 / e
        r, c = linear_sum_assignment(cost)
        return float(cost[r, c].sum() / m)
    except Exception:
        return sum((o - e) ** 2 / e for o, e in zip(obs, sorted(exp, reverse=True))) / m


def parse_prefix_code(s: str, codebook) -> list[str] | None:
    """Forced, unique parse of `s` under a prefix-free codebook.

    Returns the token list, or None if `s` ends with a dangling remainder that
    is not a codeword (the book does not parse cleanly).
    """
    cs = set(codebook)
    maxlen = max((len(c) for c in cs), default=0)
    out, i, n = [], 0, len(s)
    while i < n:
        for L in range(1, maxlen + 1):
            if s[i:i + L] in cs:
                out.append(s[i:i + L])
                i += L
                break
        else:
            return None
    return out


def mean_token_length(tokens) -> float:
    return (sum(len(t) for t in tokens) / len(tokens)) if tokens else 0.0


def abc_summary(books) -> dict:
    """The statistic vector family E fits `CopyPasteMutate` against by ABC.

    Chosen so that a generator has to get *both* long-range copying (lz76,
    longest_cross_repeat, repeat_coverage) and local diversity (distinct
    4-grams, h4, IC) right at the same time -- matching either alone is easy.
    """
    s = "".join(books)
    return {
        "lz76_factors": float(lz76_factors(s)),
        "distinct_4grams_concat": float(distinct_ngrams(s, 4)),
        "distinct_4grams_books": float(distinct_ngrams(books, 4)),
        "distinct_6grams_books": float(distinct_ngrams(books, 6)),
        "longest_cross_repeat": float(longest_cross_repeat(books)),
        "repeat_coverage20": repeat_coverage(books, 20),
        "h4": cond_entropy(books, 4),
        "unigram_H": unigram_H(s),
        "ic": ic(s),
    }


ABC_KEYS = ("lz76_factors", "distinct_4grams_concat", "distinct_4grams_books",
            "distinct_6grams_books", "longest_cross_repeat",
            "repeat_coverage20", "h4", "unigram_H", "ic")


class CTW:
    """Context-tree weighting over the 10-digit alphabet with KT estimators.

    A variable-order model: unlike a fixed order-k Markov chain it pays only for
    the context depth it actually uses, so it is the fair information-theoretic
    competitor to a copy-paste process.  Adaptive/sequential, so its total code
    length is already a held-out (prequential) quantity -- no train/test split.
    """

    def __init__(self, depth: int = 8, alphabet: int = 10):
        self.D = depth
        self.A = alphabet
        self.cnt: dict[str, list] = {}
        self.lpe: dict[str, float] = {}
        self.lpw: dict[str, float] = {}
        self.lch: dict[str, float] = {}

    def _mk(self, k):
        if k not in self.cnt:
            self.cnt[k] = [0] * self.A
            self.lpe[k] = 0.0
            self.lpw[k] = 0.0
            self.lch[k] = 0.0

    def _step(self, ctx: str, sym: int) -> float:
        """Code one symbol; returns its code length in bits."""
        D = min(self.D, len(ctx))
        path = [ctx[len(ctx) - d:] if d else "" for d in range(D + 1)]
        for k in path:
            self._mk(k)
        before = self.lpw[""]
        prev_delta = None
        for d in range(D, -1, -1):
            k = path[d]
            c = self.cnt[k]
            n = sum(c)
            self.lpe[k] += math.log2((c[sym] + 0.5) / (n + 0.5 * self.A))
            c[sym] += 1
            if prev_delta is not None:
                self.lch[k] += prev_delta
            new = self.lpe[k] if d == D else _log_add(self.lpe[k] - 1.0,
                                                      self.lch[k] - 1.0)
            prev_delta = new - self.lpw[k]
            self.lpw[k] = new
        return -(self.lpw[""] - before)

    def code_length(self, books) -> float:
        total = 0.0
        for b in books:
            for i, ch in enumerate(b):
                total += self._step(b[:i], int(ch))
        return total


def _log_add(a: float, b: float) -> float:
    m = max(a, b)
    if m == float("-inf"):
        return m
    return m + math.log2(2.0 ** (a - m) + 2.0 ** (b - m))


def ctw_bits_per_digit(books, depth: int = 8) -> float:
    """Prequential (adaptive) CTW code length per digit."""
    m = CTW(depth)
    n = sum(len(b) for b in books)
    return m.code_length(books) / n if n else float("inf")


def ctw_heldout_bits_per_digit(books, depth: int = 8) -> float:
    """Leave-one-book-out CTW: train on the other books, then code the held-out
    book with the model frozen-but-adaptive (standard prequential LOO)."""
    tot, n = 0.0, 0
    for i in range(len(books)):
        m = CTW(depth)
        m.code_length([b for j, b in enumerate(books) if j != i])
        bits = 0.0
        for t, ch in enumerate(books[i]):
            bits += m._step(books[i][:t], int(ch))
        tot += bits
        n += len(books[i])
    return tot / n if n else float("inf")


def _longest_match(ref: str, s: str, i: int, maxlen: int = 400):
    """Longest prefix of s[i:] occurring in ref; returns (length, position)."""
    lo, hi = 0, min(maxlen, len(s) - i)
    best, pos = 0, -1
    while lo < hi:
        m = (lo + hi + 1) // 2
        p = ref.find(s[i:i + m])
        if p >= 0:
            best, pos, lo = m, p, m
        else:
            hi = m - 1
    return best, pos


def relative_lz_bits_per_digit(books, loo: bool = True, min_copy: int = 3) -> float:
    """Code length per digit of a *copy* model: each book is encoded as a
    sequence of (copy from the reference / copy from itself) tokens plus
    literals.  Decodable, so the number is a real code length and directly
    comparable to a Markov or CTW bits/digit.

    loo=True codes each book against the other books only -- the leave-one-
    book-out protocol.  This is the sharpest single test of family E: if the
    corpus is cut-and-paste from shared material, a book costs far fewer bits
    under this code than under any sequential statistical model.
    """
    tot_bits, tot_n = 0.0, 0
    for i, b in enumerate(books):
        ref = "".join(books[j] for j in range(len(books)) if j != i) if loo \
            else "".join(books[:i])
        bits = 0.0
        p = 0
        while p < len(b):
            L, pos = _longest_match(ref + b[:p], b, p)
            lit_cost = 1 + math.log2(10)
            if L >= min_copy:
                cost = 1 + math.log2(max(2, len(ref) + p)) + math.log2(max(2, L))
                if cost / L < lit_cost:
                    bits += cost
                    p += L
                    continue
            bits += lit_cost
            p += 1
        tot_bits += bits
        tot_n += len(b)
    return tot_bits / tot_n if tot_n else float("inf")
