"""B3: the 1.577 prediction from the token-induction side.

Two induction methods, both run on the deduplicated core (22 books / 3901
digits) and on the assembled contigs, and both on surrogates:

  * BPE, vocabulary budget V = 50 .. 1000
  * unigram-LM / MDL dictionary segmentation (SentencePiece-style): start from
    every substring of length <= 6 occurring >= 2 times, EM with a Viterbi
    (shortest-description) parse, prune to the target V by marginal likelihood
    loss.

Pre-registered pass criterion: mean induced token length in [1.50, 1.70].
Pre-registered honesty clause: the whole V-curve is reported, not the V that
happens to land on 1.577.

Usage: python -m experiments.e_b_prefix.b3_tokens [n_nulls]
"""
from __future__ import annotations

import json
import math
import sys
import time
from collections import Counter, defaultdict
from multiprocessing import Pool
from pathlib import Path

from c469 import surrogate as U
from c469.corpus import load_books, load_contigs, dedup_core
from c469.harness import Result, summarize_null, bh_qvalues
from c469.stats import mean_token_length, token_zipf_slope, heaps_beta

OUT = Path(__file__).resolve().parent / "out"
VGRID = (16, 20, 24, 26, 28, 30, 32, 36, 40, 50, 100, 200, 300, 500, 750, 1000)
TARGET = (1.50, 1.70)
PREDICTION = 1.577


# ------------------------------------------------------------------ BPE

def bpe(books, vocab_size: int, max_len: int = 8):
    """Standard byte-pair encoding, merges never crossing a book boundary."""
    seqs = [[c for c in b] for b in books]
    vocab = set("0123456789")
    while len(vocab) < vocab_size:
        pc: Counter = Counter()
        for s in seqs:
            for i in range(len(s) - 1):
                if len(s[i]) + len(s[i + 1]) <= max_len:
                    pc[(s[i], s[i + 1])] += 1
        if not pc:
            break
        (a, b), n = pc.most_common(1)[0]
        if n < 2:
            break
        merged = a + b
        vocab.add(merged)
        for si, s in enumerate(seqs):
            out, i = [], 0
            while i < len(s):
                if i + 1 < len(s) and s[i] == a and s[i + 1] == b:
                    out.append(merged)
                    i += 2
                else:
                    out.append(s[i])
                    i += 1
            seqs[si] = out
    return [t for s in seqs for t in s], sorted(vocab)


# ------------------------------------------------- unigram-LM / MDL dictionary

def _viterbi(s: str, logp: dict, maxlen: int):
    n = len(s)
    INF = float("inf")
    cost = [0.0] + [INF] * n
    back = [0] * (n + 1)
    for i in range(1, n + 1):
        for L in range(1, min(maxlen, i) + 1):
            lp = logp.get(s[i - L:i])
            if lp is None or cost[i - L] == INF:
                continue
            c = cost[i - L] + lp
            if c < cost[i]:
                cost[i] = c
                back[i] = L
    if cost[n] == INF:
        return None, INF
    toks, i = [], n
    while i > 0:
        toks.append(s[i - back[i]:i])
        i -= back[i]
    return toks[::-1], cost[n]


def mdl_dictionary(books, vocab_size: int, maxlen: int = 6, iters: int = 8,
                   shrink: float = 0.75):
    """SentencePiece-style unigram LM: seed with frequent substrings, then EM +
    pruning down to `vocab_size`.  Single digits are never pruned so the parse
    can always cover the string."""
    seed: Counter = Counter()
    for b in books:
        for L in range(1, maxlen + 1):
            for i in range(len(b) - L + 1):
                seed[b[i:i + L]] += 1
    keep = {t: c for t, c in seed.items() if len(t) == 1 or c >= 2}
    # score-order seed: frequency * length is the classic substring utility
    voc = dict(sorted(keep.items(), key=lambda kv: -kv[1] * len(kv[0]))[:8000])
    for d in "0123456789":
        voc.setdefault(d, seed.get(d, 1))

    for _ in range(200):
        tot = sum(voc.values())
        logp = {t: -math.log2(c / tot) for t, c in voc.items()}
        for _ in range(iters if len(voc) <= vocab_size * 2 else 2):
            nc: Counter = Counter()
            for b in books:
                toks, _c = _viterbi(b, logp, maxlen)
                if toks:
                    nc.update(toks)
            for d in "0123456789":
                nc[d] += 1
            voc = dict(nc)
            tot = sum(voc.values())
            logp = {t: -math.log2(c / tot) for t, c in voc.items()}
        if len(voc) <= vocab_size:
            break
        target = max(vocab_size, int(len(voc) * shrink))
        order = sorted(voc.items(), key=lambda kv: -kv[1] * len(kv[0]))
        voc = dict(order[:target])
        for d in "0123456789":
            voc.setdefault(d, 1)

    tot = sum(voc.values())
    logp = {t: -math.log2(c / tot) for t, c in voc.items()}
    toks, bits = [], 0.0
    for b in books:
        t, c = _viterbi(b, logp, maxlen)
        toks += t or []
        bits += c
    ndig = sum(len(b) for b in books)
    return toks, sorted(voc), bits / ndig


# ------------------------------------------------------------------ driver

def curve(books, method: str):
    rows = []
    for V in VGRID:
        t0 = time.time()
        if method == "bpe":
            toks, voc = bpe(books, V)
            bits = float("nan")
        else:
            toks, voc, bits = mdl_dictionary(books, V)
        zs, zr2 = token_zipf_slope(toks)
        rows.append({"V_target": V, "V_actual": len(voc),
                     "mean_token_len": mean_token_length(toks),
                     "n_tokens": len(toks), "bits_per_digit": bits,
                     "zipf_slope": zs, "zipf_r2": zr2,
                     "heaps_beta": heaps_beta(toks),
                     "runtime_s": time.time() - t0})
    return rows


def _job(args):
    fam, seed, books, method, V = args
    b = books if fam == "real" else U.get(fam).generate(list(books), seed)
    if method == "bpe":
        toks, voc = bpe(b, V)
    else:
        toks, voc, _ = mdl_dictionary(b, V)
    return fam, mean_token_length(toks)


def main():
    nn = int(sys.argv[1]) if len(sys.argv) > 1 else 200
    OUT.mkdir(exist_ok=True)
    c = load_books()
    core = dedup_core(c)
    contigs = load_contigs()
    datasets = {
        "books70": (list(c.books), c.provenance),
        "dedup_core22": (list(core.books), core.provenance),
        "contigs": (list(contigs.books), contigs.provenance),
    }

    curves = {}
    for dname, (bk, prov) in datasets.items():
        for method in ("bpe", "mdl"):
            key = f"{dname}/{method}"
            curves[key] = curve(bk, method)
            print(f"\n{key}   ({prov})")
            print("   V_target V_actual  mean_len  bits/dig  zipf_s  heaps_b")
            for r in curves[key]:
                print(f"   {r['V_target']:>8} {r['V_actual']:>8} "
                      f"{r['mean_token_len']:>9.3f} {r['bits_per_digit']:>9.3f} "
                      f"{r['zipf_slope']:>7.3f} {r['heaps_beta']:>8.3f}")
    Path(OUT / "b3_curves.json").write_text(json.dumps(curves, indent=2))

    # --- null-scored statistic: mean token length at a FIXED, pre-set V -----
    fams = [f.name for f in U.DEFAULT_FAMILIES] + ["Digits_pi"]
    pvals, labels, results = [], [], []
    for dname in ("dedup_core22", "contigs"):
        bk, prov = datasets[dname]
        # V = 32 is the letter-alphabet size at which the 1.577 prediction is
        # actually being made; V = 200 is a far-from-alphabet control.
        for method, V in (("bpe", 32), ("mdl", 32), ("bpe", 200), ("mdl", 200)):
            real = _job(("real", 0, bk, method, V))[1]
            res = Result(f"e_b_prefix.b3.{dname}.{method}.V{V}", "mean_token_len",
                         real, "greater", corpus_provenance=prov,
                         extra={"V": V, "prediction": PREDICTION,
                                "target_window": list(TARGET),
                                "in_target_window": TARGET[0] <= real <= TARGET[1]})
            jobs = [(f, s, bk, method, V) for f in fams for s in range(nn)]
            got = defaultdict(list)
            with Pool(4) as p:
                for fam, v in p.imap_unordered(_job, jobs, chunksize=4):
                    got[fam].append(v)
            for f in fams:
                res.nulls.append(summarize_null(f, real, got[f], "greater"))
            for nr in res.nulls:
                pvals.append(nr.p)
                labels.append(f"{res.experiment}/{nr.family}")
            results.append(res)
            print(f"\n{res.experiment}: real mean_token_len={real:.4f} "
                  f"(target {TARGET}) -> {'IN' if res.extra['in_target_window'] else 'OUT'}")
            for nr in res.nulls:
                print(f"   {nr.family:<18} {nr.mean:.4f} +- {nr.sd:.4f} p={nr.p:.4f}")

    q = bh_qvalues(pvals)
    qmap = dict(zip(labels, q))
    for res in results:
        res.extra["bh_q"] = {nr.family: qmap[f"{res.experiment}/{nr.family}"]
                             for nr in res.nulls}
        res.save()


if __name__ == "__main__":
    main()
