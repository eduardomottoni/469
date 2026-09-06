"""Cyclic mod-10 letter hypothesis: digit d = any letter with index = d (mod 10).

Pre-registered 2026-09-06.  A=0..Z=25, so 0 -> {A,K,U}, 6 -> {G,Q}, etc.
Unlike the a1z26_* statistics in SEED_ATTACK.md (which test whether digit
*groups* land in 1..26), this is a one-digit-to-many-letters lattice.  There is
no key to search: the map is fixed by the hypothesis, so the only question is
whether the best-scoring path through the lattice is language.

Statistic: best-path mean log2 P(char | previous chars) under a character
n-gram LM.  Higher = more language-like.
Supported only if real 469 beats Markov-3 surrogates decoded identically,
AND the decoder demonstrably recovers injected English at the same length.
"""
import glob, math, re, random, sys
from collections import defaultdict, Counter

AL = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
CAND = {str(d): [c for c in AL if (AL.index(c) % 10) == d] for d in range(10)}

def load_english():
    t = []
    for f in (glob.glob('data/external/provenance/*.txt')
              + glob.glob('experiments/*/FINDINGS.md') + ['README.md', '00-timeline.md']):
        try: t.append(open(f, encoding='utf-8', errors='ignore').read())
        except Exception: pass
    return re.sub('[^A-Z]', '', ' '.join(t).upper())

class LM:
    """Character n-gram with stupid backoff."""
    def __init__(self, text, order=5):
        self.order = order
        self.c = [defaultdict(Counter) for _ in range(order + 1)]
        for k in range(order + 1):
            for i in range(len(text) - k):
                self.c[k][text[i:i + k]][text[i + k]] += 1
        self.tot = [{ctx: sum(v.values()) for ctx, v in lvl.items()} for lvl in self.c]
    def logp(self, ctx, ch):
        for k in range(min(len(ctx), self.order), -1, -1):
            c = ctx[len(ctx) - k:] if k else ''
            d = self.c[k].get(c)
            if d and d.get(ch):
                return math.log2(d[ch] / self.tot[k][c]) + (0 if k == min(len(ctx), self.order) else -1.0)
        return math.log2(1 / 26) - 4.0

def viterbi(digits, lm, beam=400):
    """Best path through the candidate lattice. State = last `order` chars."""
    o = lm.order
    paths = {'': 0.0}
    for d in digits:
        nxt = {}
        for ctx, sc in paths.items():
            for ch in CAND[d]:
                s = sc + lm.logp(ctx, ch)
                k = (ctx + ch)[-o:]
                if k not in nxt or s > nxt[k][0]:
                    nxt[k] = (s, ctx, ch)
        best = sorted(nxt.items(), key=lambda kv: -kv[1][0])[:beam]
        paths = {k: v[0] for k, v in best}
        for k, v in best: BACK[(len(TRACE), k)] = v
        TRACE.append(None)
        nxt.clear()
    return max(paths.values()) / len(digits)

BACK = {}; TRACE = []

def decode(digits, lm, beam=400):
    """Same as viterbi but returns the string too."""
    o = lm.order
    paths = {'': (0.0, '')}
    for d in digits:
        nxt = {}
        for ctx, (sc, s) in paths.items():
            for ch in CAND[d]:
                v = sc + lm.logp(ctx, ch)
                k = (ctx + ch)[-o:]
                if k not in nxt or v > nxt[k][0]:
                    nxt[k] = (v, s + ch)
        paths = dict(sorted(nxt.items(), key=lambda kv: -kv[1][0])[:beam])
    k = max(paths, key=lambda k: paths[k][0])
    return paths[k][0] / len(digits), paths[k][1]

def encode(text):
    return ''.join(str(AL.index(c) % 10) for c in text if c in AL)

def markov_surrogate(src, k, n, rng):
    tbl = defaultdict(list)
    for i in range(len(src) - k): tbl[src[i:i + k]].append(src[i + k])
    out = list(src[:k])
    for _ in range(n - k):
        c = tbl.get(''.join(out[-k:]))
        out.append(rng.choice(c) if c else rng.choice(src))
    return ''.join(out)
