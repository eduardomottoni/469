"""Character 5-gram language models for German and English.

Provenance: general web egress is blocked by this session's proxy policy
(403 on CONNECT to gutenberg.org, wikipedia.org, fandom.com), so no running-text
corpus could be fetched.  What *is* reachable is PyPI, and `wordfreq` bundles
the large Exquisite-Corpus frequency lists (300k word types each for de and en,
derived from Wikipedia, subtitles, news, books and web text).  We therefore
build the character models from text synthesised by sampling word types in
proportion to their corpus frequency, separated by spaces.

Limitation, stated up front: this captures within-word and word-boundary
character statistics faithfully but carries no syntax beyond word unigrams.
For AZdecrypt-style 5-gram scoring that is the dominant signal, but the models
are weaker than ones built from running text, and both the real and the
surrogate runs are scored with the identical model so the *comparison* is
unaffected.

Variants built:
  en          English, a-z + space
  de_ae       German, umlauts folded ae/oe/ue/ss  (a 2001 ASCII-folding dev)
  de_a        German, umlauts folded a/o/u/ss     (the cruder folding)
"""
from __future__ import annotations

import gzip, math, pickle, random, sys, unicodedata
from collections import Counter
from pathlib import Path

OUT = Path(__file__).resolve().parents[2] / "data" / "external"
N = 5
CHARS = "abcdefghijklmnopqrstuvwxyz "
IDX = {c: i for i, c in enumerate(CHARS)}
A = len(CHARS)


def fold(w: str, mode: str) -> str:
    w = w.lower()
    if mode == "de_ae":
        for a, b in (("ä", "ae"), ("ö", "oe"), ("ü", "ue"), ("ß", "ss")):
            w = w.replace(a, b)
    elif mode == "de_a":
        for a, b in (("ä", "a"), ("ö", "o"), ("ü", "u"), ("ß", "ss")):
            w = w.replace(a, b)
    w = unicodedata.normalize("NFKD", w)
    return "".join(c for c in w if c in CHARS)


def synth(lang: str, mode: str, n_chars: int = 20_000_000, seed: int = 1) -> str:
    import wordfreq
    ws = wordfreq.top_n_list(lang, 300_000)
    freqs = [wordfreq.word_frequency(w, lang) for w in ws]
    kept = [(fold(w, mode), f) for w, f in zip(ws, freqs)]
    # Clean the type list.  wordfreq's tail contains junk types ("aaa", "zzzz")
    # whose rare 5-grams then dominate otherwise-unseen contexts and create a
    # degenerate constant-string attractor for the solver.  Drop any type with
    # a run of 3+ identical letters, or shorter than 1 / longer than 20.
    def ok(w):
        if not w or len(w) > 20 or " " in w:
            return False
        run = 1
        for i in range(1, len(w)):
            run = run + 1 if w[i] == w[i - 1] else 1
            if run >= 3:
                return False
        return True
    kept = [(w, f) for w, f in kept if f > 1e-8 and ok(w)]
    rng = random.Random(seed)
    words = [w for w, _ in kept]
    wts = [f for _, f in kept]
    out, tot = [], 0
    while tot < n_chars:
        chunk = rng.choices(words, weights=wts, k=20000)
        s = " ".join(chunk) + " "
        out.append(s)
        tot += len(s)
    return "".join(out)[:n_chars]


def build(text: str, n: int = N, D: float = 0.75, min_count: int = 3):
    return _build(text, n, D, min_count)


def _build(text: str, n: int = N, D: float = 0.75, min_count: int = 3):
    """Witten-Bell interpolated character n-gram model.

    P_m(c|h) = (C(h,c) + T(h) P_{m-1}(c|h')) / (C(h) + T(h)),  h' = h minus its
    oldest character; P_m = P_{m-1} where the history was never seen.  Returns
    log10 P(c | 4 preceding characters) as a dense (A^4, A) float32 table.
    """
    import numpy as np
    codes = np.frombuffer(bytes(IDX[c] for c in text), dtype=np.uint8).astype(np.int32)
    probs = None
    for order in range(1, n + 1):
        m = len(codes) - order + 1
        key = np.zeros(m, dtype=np.int64)
        for j in range(order):
            key = key * A + codes[j:j + m]
        cnt = np.bincount(key, minlength=A ** order).astype(np.float64).reshape(-1, A)
        if probs is None:                       # order 1: histories of length 0
            lower = np.full((1, A), 1.0 / A)
        else:
            rows = np.arange(cnt.shape[0])
            back = rows % (A ** (order - 2)) if order >= 2 else np.zeros_like(rows)
            lower = probs[back]
        # Interpolated absolute discounting (Kneser-Ney form), with a minimum
        # evidence threshold: a context seen fewer than `min_count` times is not
        # trusted at all and backs off wholesale.  Without that threshold a
        # context seen 13 times (a junk type) outvotes the entire lower-order
        # model, which is exactly how the constant-string attractor arises.
        tot = cnt.sum(axis=1, keepdims=True)
        T = (cnt > 0).sum(axis=1, keepdims=True).astype(np.float64)
        disc = np.maximum(cnt - D, 0.0)
        lam = D * T / np.maximum(tot, 1e-12)
        pr = disc / np.maximum(tot, 1e-12) + lam * lower
        pr = np.where(tot >= min_count, pr, lower)
        pr /= pr.sum(axis=1, keepdims=True)
        probs = pr
        del cnt, key, lower
    return np.log10(np.maximum(probs, 1e-12)).astype(np.float32)


def main():
    import numpy as np
    for name, lang, mode in (("en", "en", "en"), ("de_ae", "de", "de_ae"), ("de_a", "de", "de_a")):
        p = OUT / f"lm5_{name}.npz"
        if p.exists():
            print("have", p); continue
        print("synthesising", name, flush=True)
        txt = synth(lang, mode)
        print("  chars", len(txt), flush=True)
        tab = build(txt)
        np.savez_compressed(p, table=tab, alphabet=np.array(list(CHARS)))
        # held-out sanity: log10 P per char of a fresh sample
        def rate(t):
            codes = [IDX[c] for c in t]
            s = 0.0
            for i in range(4, len(codes)):
                ctx = 0
                for j in range(i - 4, i):
                    ctx = ctx * A + codes[j]
                s += float(tab[ctx, codes[i]])
            return s / (len(codes) - 4)
        test = synth(lang, mode, n_chars=200_000, seed=99)
        held = rate(test)
        # Sanity gate: degenerate strings must score WORSE than real text, or the
        # solver has a constant-string attractor and every result is worthless.
        deg = {"const_a": "a" * 5000, "const_space": " " * 5000,
               "alt_ab": "ab" * 2500,
               "rand": "".join(__import__("random").Random(4).choice(CHARS)
                               for _ in range(5000))}
        print(f"  {name}: held-out log10P/char = {held:.4f}", flush=True)
        for k, v in deg.items():
            r = rate(v)
            flag = "OK" if r < held else "*** ATTRACTOR ***"
            print(f"     degenerate {k:12s} {r:8.4f}  {flag}", flush=True)


if __name__ == "__main__":
    main()
