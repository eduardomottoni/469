"""Token inducers for Family A.

Five inducers over a digit stream (a list of books, so no token straddles a
book boundary):

  bpe(V)      classic byte-pair encoding to a target vocabulary size
  repair      Re-Pair: replace the most frequent pair by a nonterminal until
              no pair repeats; the induced *terminal expansions* are the tokens
  sequitur    Sequitur (digram uniqueness + rule utility) online grammar
  lz78        LZ78 incremental dictionary
  mdl_unigram MDL-optimal dictionary segmentation: Viterbi shortest-path parse
              under a unigram token model, EM re-estimation, and vocabulary
              pruning by measured MDL gain.  This is the one to trust.

Every inducer returns an `Induction`: vocabulary, the parse of each book, and
the MDL description length in bits under one common accounting so the numbers
are comparable across inducers.
"""
from __future__ import annotations

import math
from collections import Counter, defaultdict
from dataclasses import dataclass, field

LOG10 = math.log2(10.0)
LOG11 = math.log2(11.0)


# ------------------------------------------------------------------ accounting

def mdl_bits(vocab, parses) -> dict:
    """Two-part description length, in bits, of `parses` given `vocab`.

    L(model): each dictionary entry written as a digit string over an 11-symbol
      alphabet (10 digits + terminator), plus Rissanen's (V-1)/2 log2 N cost of
      the token frequency table.
    L(data|model): N * H(token distribution) -- the empirical-entropy cost of
      the token sequence itself.

    The same accounting is applied to every inducer and to every surrogate, so
    the comparison is fair even where the absolute constant is arguable.
    """
    toks = [t for p in parses for t in p]
    N = len(toks)
    c = Counter(toks)
    V = len(vocab)
    L_dict = sum((len(t) + 1) * LOG11 for t in vocab)
    L_counts = 0.5 * max(0, V - 1) * math.log2(max(N, 2))
    L_data = 0.0
    for t, k in c.items():
        L_data -= k * math.log2(k / N)
    # cost of signalling the number of tokens per book is O(log) and common to all
    return {"L_dict": L_dict, "L_counts": L_counts, "L_data": L_data,
            "total": L_dict + L_counts + L_data, "n_tokens": N, "V": V}


@dataclass
class Induction:
    name: str
    vocab: list[str]
    parses: list[list[str]]
    mdl: dict = field(default_factory=dict)

    @property
    def tokens(self) -> list[str]:
        return [t for p in self.parses for t in p]

    @property
    def used_vocab(self) -> list[str]:
        return sorted(set(self.tokens))

    def length_profile(self) -> dict:
        """The numbers the pre-registered prediction is about."""
        toks = self.tokens
        uv = self.used_vocab
        n = len(toks)
        occ = Counter(len(t) for t in toks)
        typ = Counter(len(t) for t in uv)
        return {
            "mean_token_len_weighted": sum(len(t) for t in toks) / n if n else 0.0,
            "mean_token_len_types": sum(len(t) for t in uv) / len(uv) if uv else 0.0,
            "n_len1_types": typ[1],
            "n_len2_types": typ[2],
            "n_len3_types": typ[3],
            "frac_occ_len1": occ[1] / n if n else 0.0,
            "frac_occ_len12": (occ[1] + occ[2]) / n if n else 0.0,
            "V_used": len(uv),
            "n_tokens": n,
            "occ_by_len": dict(sorted(occ.items())),
            "types_by_len": dict(sorted(typ.items())),
        }


# ------------------------------------------------------------------------ BPE

def bpe(books, V: int) -> Induction:
    seqs = [[c for c in b] for b in books]
    vocab = sorted({c for b in books for c in b})
    while len(vocab) < V:
        pc = Counter()
        for s in seqs:
            for i in range(len(s) - 1):
                pc[(s[i], s[i + 1])] += 1
        if not pc:
            break
        (a, b), k = pc.most_common(1)[0]
        if k < 2:
            break
        new = a + b
        vocab.append(new)
        for si, s in enumerate(seqs):
            out, i = [], 0
            while i < len(s):
                if i + 1 < len(s) and s[i] == a and s[i + 1] == b:
                    out.append(new)
                    i += 2
                else:
                    out.append(s[i])
                    i += 1
            seqs[si] = out
    ind = Induction(f"bpe{V}", vocab, seqs)
    ind.mdl = mdl_bits(ind.used_vocab, seqs)
    return ind


# --------------------------------------------------------------------- Re-Pair

def repair(books, min_count: int = 2) -> Induction:
    """Re-Pair: repeatedly replace the most frequent digram by a new symbol.

    Tokens = the terminal expansions of the top-level sequence's symbols.
    """
    NT = {}                      # symbol id -> (left, right)
    next_id = 10
    seqs = [[int(c) for c in b] for b in books]
    while True:
        pc = Counter()
        for s in seqs:
            for i in range(len(s) - 1):
                pc[(s[i], s[i + 1])] += 1
        if not pc:
            break
        pair, k = pc.most_common(1)[0]
        if k < min_count:
            break
        NT[next_id] = pair
        a, b = pair
        for si, s in enumerate(seqs):
            out, i = [], 0
            while i < len(s):
                if i + 1 < len(s) and s[i] == a and s[i + 1] == b:
                    out.append(next_id)
                    i += 2
                else:
                    out.append(s[i])
                    i += 1
            seqs[si] = out
        next_id += 1

    memo: dict[int, str] = {}

    def expand(x: int) -> str:
        if x < 10:
            return str(x)
        if x in memo:
            return memo[x]
        a, b = NT[x]
        memo[x] = expand(a) + expand(b)
        return memo[x]

    parses = [[expand(x) for x in s] for s in seqs]
    vocab = sorted({t for p in parses for t in p})
    ind = Induction("repair", vocab, parses)
    ind.mdl = mdl_bits(vocab, parses)
    return ind


# -------------------------------------------------------------------- Sequitur

def sequitur(books) -> Induction:
    """Sequitur run over the concatenation of books with unique separators.

    Tokens are the terminal expansions of the symbols of the start rule,
    separators removed.
    """
    class Sym:
        __slots__ = ("val", "prev", "nxt", "rule", "is_guard")

        def __init__(self, val=None, rule=None, guard=False):
            self.val, self.rule, self.is_guard = val, rule, guard
            self.prev = self.nxt = None

        def key(self):
            return ("R", id(self.rule)) if self.rule is not None else ("T", self.val)

    class Rule:
        __slots__ = ("guard", "count")

        def __init__(self):
            self.guard = Sym(guard=True)
            self.guard.prev = self.guard.nxt = self.guard
            self.count = 0

        def first(self):
            return self.guard.nxt

        def last(self):
            return self.guard.prev

    digrams: dict = {}

    def dkey(a: Sym) -> tuple | None:
        b = a.nxt
        if a.is_guard or b is None or b.is_guard:
            return None
        return (a.key(), b.key())

    def insert_after(a: Sym, b: Sym):
        b.nxt = a.nxt
        b.prev = a
        a.nxt.prev = b
        a.nxt = b

    def delete(a: Sym):
        a.prev.nxt = a.nxt
        a.nxt.prev = a.prev
        k = dkey(a)
        if k and digrams.get(k) is a:
            del digrams[k]
        if a.rule is not None:
            a.rule.count -= 1

    def link(a: Sym):
        k = dkey(a)
        if k is None:
            return
        m = digrams.get(k)
        if m is None:
            digrams[k] = a
            return
        if m.nxt is a:          # overlapping, ignore
            return
        match(a, m)

    def replace(a: Sym, rule: Rule) -> Sym:
        b = a.nxt
        prev = a.prev
        k1, k2 = dkey(a.prev), dkey(a)
        for k, node in ((k1, a.prev), (k2, a)):
            if k and digrams.get(k) is node:
                del digrams[k]
        kb = dkey(b)
        if kb and digrams.get(kb) is b:
            del digrams[kb]
        delete_simple(a)
        delete_simple(b)
        s = Sym(rule=rule)
        rule.count += 1
        insert_after(prev, s)
        return s

    def delete_simple(a: Sym):
        a.prev.nxt = a.nxt
        a.nxt.prev = a.prev
        if a.rule is not None:
            a.rule.count -= 1

    def expand_rule_into(s: Sym):
        """Rule utility: a rule used once is inlined."""
        r = s.rule
        f, l = r.first(), r.last()
        prev = s.prev
        kp = dkey(prev)
        if kp and digrams.get(kp) is prev:
            del digrams[kp]
        ks = dkey(s)
        if ks and digrams.get(ks) is s:
            del digrams[ks]
        delete_simple(s)
        # splice f..l after prev
        nxt = prev.nxt
        prev.nxt = f
        f.prev = prev
        l.nxt = nxt
        nxt.prev = l
        r.guard.nxt = r.guard.prev = r.guard
        rules.discard(r)
        link(prev)
        link(l)

    def match(a: Sym, m: Sym):
        # m is an existing occurrence of the same digram
        if (m.prev.is_guard and m.nxt.nxt.is_guard):
            r = rule_of_guard[id(m.prev)]
            s = replace(a, r)
            link(s.prev)
            link(s)
        else:
            r = Rule()
            rules.add(r)
            rule_of_guard[id(r.guard)] = r
            a1, a2 = a, a.nxt
            # build the new rule body from copies of a, a.nxt
            for src in (a1, a2):
                c = Sym(val=src.val, rule=src.rule)
                if c.rule is not None:
                    c.rule.count += 1
                insert_after(r.last(), c)
            s2 = replace(m, r)
            s1 = replace(a, r)
            digrams[(r.first().key(), r.first().nxt.key())] = r.first()
            link(s2.prev); link(s2)
            link(s1.prev); link(s1)
        # Rule utility: only rules whose reference count could just have
        # dropped need checking -- scanning every rule on every match is
        # quadratic and was the reason this did not terminate on 400+ digits.
        # Rule utility.  Scanning every rule on every match is quadratic; it is
        # why this implementation is only usable on short streams (see
        # FINDINGS.md -- Re-Pair, the offline greedy equivalent, stands in for
        # Sequitur on the full corpus and answers the same question).
        for r2 in list(rules):
            if r2.count == 1:
                occ = find_occurrence(r2)
                if occ is not None:
                    expand_rule_into(occ)

    def find_occurrence(r2: Rule):
        for r in [start] + list(rules):
            if r is r2:
                continue
            s = r.first()
            while not s.is_guard:
                if s.rule is r2:
                    return s
                s = s.nxt
        return None

    rules: set = set()
    rule_of_guard: dict = {}
    start = Rule()
    rule_of_guard[id(start.guard)] = start

    stream = []
    for bi, b in enumerate(books):
        stream.extend(b)
        stream.append(f"#{bi}")          # unique separator, never in a digram twice
    for ch in stream:
        s = Sym(val=ch)
        insert_after(start.last(), s)
        link(s.prev)

    memo: dict[int, str] = {}

    def expand(s0: Sym) -> str:
        # iterative post-order so deeply nested grammars do not blow the stack
        if s0.rule is None:
            return s0.val
        stack = [(s0.rule, False)]
        while stack:
            r, done = stack.pop()
            if id(r) in memo:
                continue
            if done:
                out, x = [], r.first()
                while not x.is_guard:
                    out.append(memo[id(x.rule)] if x.rule is not None else x.val)
                    x = x.nxt
                memo[id(r)] = "".join(out)
                continue
            stack.append((r, True))
            x = r.first()
            while not x.is_guard:
                if x.rule is not None and id(x.rule) not in memo:
                    stack.append((x.rule, False))
                x = x.nxt
        return memo[id(s0.rule)]

    toks = []
    x = start.first()
    while not x.is_guard:
        toks.append(expand(x))
        x = x.nxt
    # split on separators back into books
    parses, cur = [], []
    for t in toks:
        parts = []
        buf = ""
        i = 0
        # a token may contain separators; split it
        seg = []
        j = 0
        while j < len(t):
            if t[j] == "#":
                k = j + 1
                while k < len(t) and t[k].isdigit() and (k == j + 1 or True):
                    # separator is '#' + book index digits; greedily consume digits
                    k += 1
                seg.append(("SEP", t[j:k]))
                j = k
            else:
                k = j
                while k < len(t) and t[k] != "#":
                    k += 1
                seg.append(("T", t[j:k]))
                j = k
        for kind, v in seg:
            if kind == "SEP":
                parses.append(cur)
                cur = []
            elif v:
                cur.append(v)
    if cur:
        parses.append(cur)
    parses = [p for p in parses if p]
    vocab = sorted({t for p in parses for t in p})
    ind = Induction("sequitur", vocab, parses)
    ind.mdl = mdl_bits(vocab, parses)
    return ind


# ----------------------------------------------------------------------- LZ78

def lz78(books) -> Induction:
    parses = []
    vocab = set()
    for b in books:
        d = {""}
        out, cur = [], ""
        for ch in b:
            if cur + ch in d:
                cur += ch
            else:
                d.add(cur + ch)
                out.append(cur + ch)
                cur = ""
        if cur:
            out.append(cur)
        parses.append(out)
        vocab |= set(out)
    vocab = sorted(vocab)
    ind = Induction("lz78", vocab, parses)
    ind.mdl = mdl_bits(vocab, parses)
    return ind


# ------------------------------------------------- MDL-optimal dictionary parse

def _viterbi(b: str, cost: dict, maxlen: int) -> list[str]:
    """Shortest-path segmentation of b under per-token bit costs."""
    n = len(b)
    INF = float("inf")
    dp = [INF] * (n + 1)
    bk = [0] * (n + 1)
    dp[0] = 0.0
    for i in range(n):
        if dp[i] == INF:
            continue
        di = dp[i]
        hi = min(maxlen, n - i)
        for L in range(1, hi + 1):
            c = cost.get(b[i:i + L])
            if c is not None:
                v = di + c
                if v < dp[i + L]:
                    dp[i + L] = v
                    bk[i + L] = L
    if dp[n] == INF:
        raise ValueError("stream not coverable by vocabulary")
    out, i = [], n
    while i > 0:
        L = bk[i]
        out.append(b[i - L:i])
        i -= L
    return out[::-1]


def mdl_unigram(books, maxlen: int = 8, seed_max: int = 4000,
                shrink: float = 0.85, em_iters: int = 6,
                min_vocab: int = 12, verbose: bool = False,
                curve: list | None = None) -> Induction:
    """MDL-optimal dictionary segmentation.

    Seed with every substring of length <= maxlen occurring at least twice
    (capped by count*len), then repeatedly: EM-reparse, measure the true MDL of
    the current vocabulary, and prune the lowest-utility tokens.  Returns the
    vocabulary at the MDL argmin over the whole shrink path.
    """
    digits = sorted({c for b in books for c in b})
    sub = Counter()
    for b in books:
        n = len(b)
        for L in range(2, maxlen + 1):
            for i in range(n - L + 1):
                sub[b[i:i + L]] += 1
    cands = [s for s, k in sub.items() if k >= 2]
    cands.sort(key=lambda s: -sub[s] * len(s))
    vocab = set(digits) | set(cands[:seed_max])

    best = None
    path = []
    while True:
        # ---- EM: reparse under current probabilities, re-estimate
        cnt = Counter({t: 1 for t in vocab})
        for _ in range(em_iters):
            N = sum(cnt.values())
            cost = {t: -math.log2(cnt[t] / N) for t in vocab if cnt[t] > 0}
            for d in digits:                      # digits always available
                cost.setdefault(d, -math.log2(0.5 / N))
            parses = [_viterbi(b, cost, maxlen) for b in books]
            new = Counter(t for p in parses for t in p)
            if new == cnt:
                break
            cnt = new + Counter({t: 1e-9 for t in vocab})
        parses = [_viterbi(b, cost, maxlen) for b in books]
        used = sorted({t for p in parses for t in p})
        m = mdl_bits(used, parses)
        path.append({"V_seed": len(vocab), "V_used": len(used),
                     "total_bits": m["total"], "L_dict": m["L_dict"],
                     "L_data": m["L_data"], "n_tokens": m["n_tokens"]})
        if verbose:
            print(f"  V_seed={len(vocab):5d} V_used={len(used):5d} "
                  f"MDL={m['total']:10.1f} bits  ntok={m['n_tokens']}")
        if best is None or m["total"] < best[0]:
            ind = Induction("mdl_unigram", used, parses)
            ind.mdl = m
            best = (m["total"], ind)
        if len(used) <= min_vocab:
            break
        # ---- prune: drop the tokens contributing least, never a single digit
        occ = Counter(t for p in parses for t in p)
        target = max(min_vocab, int(len(used) * shrink))
        droppable = sorted((t for t in used if len(t) > 1),
                           key=lambda t: occ[t] * (len(t) - 1))
        ndrop = max(1, len(used) - target)
        drop = set(droppable[:ndrop])
        newv = (set(used) - drop) | set(digits)
        if newv == vocab:
            break
        vocab = newv
    if curve is not None:
        curve.extend(path)
    return best[1]
