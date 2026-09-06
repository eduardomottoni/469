"""End-to-end power: put a message IN the seed, then try to get it back out.

This is the test that decides whether any of this is worth believing.  Family E
says 469 is a copy-paste artefact whose only possible carrier is the seed.  So
build exactly that object with a message in it:

  1. take a known plaintext, encipher it (V10 digit substitution, or A1Z26),
     and use the result as the SEED of `c469.surrogate.CopyPasteMutateFitted`
     at its posterior-median parameters;
  2. generate a 70-book corpus at the real book lengths, with the fitted
     rotation / deletion / substitution / book-reuse behaviour;
  3. run each residue-extraction policy on the result;
  4. solve the residue and ask how much of the injected key comes back.

If step 4 fails on a corpus we KNOW carries a message, then a null result on the
real corpus means nothing at all, and every "no signal in the seed" claim --
including this document's -- is a statement about the method, not about 469.

Metrics per (policy, min_copy):
  n_res        residue length
  purity       share of residue digits that are the FIRST corpus occurrence of
               their seed position (i.e. genuine innovation, not a re-copy)
  recall       share of the seed's digits that survive into the residue
  key_acc      frequency-weighted share of the ten cipher digits the solver
               maps to the correct letter
  char_acc     character accuracy of the decrypted residue against the true
               plaintext of the seed positions it came from
"""
from __future__ import annotations

import json
import math
import random
import sys
from collections import Counter
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "experiments" / "e_c_homophonic"))

import attack_lib as AL                                  # noqa: E402
from c469.corpus import load_books                       # noqa: E402
from c469.surrogate import CopyPasteMutateFitted, DIGITS  # noqa: E402
from solver import solve, load_table, CHARS              # noqa: E402


def generate_with_seed(params: CopyPasteMutateFitted, src: str, book_lens,
                       seed: int):
    """`CopyPasteMutateFitted.generate` with a caller-supplied seed string and
    per-digit provenance.  Mirrors the shipped generator line for line; the only
    additions are the provenance lists.  Provenance is the index into `src`, or
    -1 for a digit produced by the substitution mutator (a true novelty)."""
    rng = random.Random(seed)
    pool = [src]
    pool_prov = [list(range(len(src)))]
    out, prov = [], []
    for T in book_lens:
        nseg = min(6, 1 + params._pois(rng, params.seg_lambda))
        nseg = max(1, min(nseg, max(1, T // params.min_seg)))
        cuts = sorted(rng.randrange(T) for _ in range(nseg - 1))
        lens, prev = [], 0
        for cpos in cuts + [T]:
            lens.append(cpos - prev); prev = cpos
        lens = [max(1, x) for x in lens]
        parts, pparts = [], []
        for Lg in lens:
            di = 0
            if len(pool) > 1 and rng.random() < params.p_reuse:
                di = rng.randrange(1, len(pool))
            donor, dprov = pool[di], pool_prov[di]
            need = Lg + 8
            while len(donor) <= need:
                donor = donor + donor
                dprov = dprov + dprov
            i = rng.randrange(0, len(donor) - need)
            frag, fprov = donor[i:i + Lg], dprov[i:i + Lg]
            if rng.random() < params.p_rotate and len(frag) > 2:
                c = rng.randrange(1, len(frag))
                frag, fprov = frag[c:] + frag[:c], fprov[c:] + fprov[:c]
            if params.p_delete or params.p_sub:
                buf, bp = [], []
                for ch, pv in zip(frag, fprov):
                    r = rng.random()
                    if r < params.p_delete:
                        continue
                    if r < params.p_delete + params.p_sub:
                        ch, pv = DIGITS[rng.randrange(10)], -1
                    buf.append(ch); bp.append(pv)
                frag, fprov = "".join(buf), bp
            parts.append(frag); pparts.append(fprov)
        s = "".join(parts)
        sp = [x for p in pparts for x in p]
        while len(s) < T:
            k = T - len(s)
            i = rng.randrange(0, max(1, len(src) - k - 1))
            s += src[i:i + k]
            sp += list(range(i, i + k))
        out.append(s[:T]); prov.append(sp[:T])
    return out, prov


# ------------------------------------------------------------------ plaintext

def make_v10_seed(n_digits: int, seed: int = 11):
    """Seed = 10-letter reduced English under a fixed digit substitution."""
    t = AL.english_text(n_digits * 4, seed)
    keep = [c for c, _ in Counter(t).most_common(10)]
    letters = "".join(c for c in t if c in keep)[:n_digits]
    perm = list(range(10))
    random.Random(seed).shuffle(perm)
    m = {c: str(perm[i]) for i, c in enumerate(keep)}
    digits = "".join(m[c] for c in letters)
    true_map = {m[c]: c for c in keep}          # digit -> letter
    return digits, letters, true_map


def key_accuracy(key, stream, true_map):
    """Frequency-weighted share of digits mapped to the right letter."""
    cnt = Counter(int(x) for x in stream)
    tot = sum(cnt.values())
    good = 0
    for d, c in cnt.items():
        if CHARS[key[d]] == true_map.get(str(d)):
            good += c
    return good / tot if tot else 0.0


# ----------------------------------------------------------------------- run

POLICIES = [("greedy", 3), ("greedy", 6), ("union", 5), ("union", 6),
            ("union", 8), ("union", 12), ("lz76_innovation", 0)]


def main(n_rep=3, n_restarts=40, seed_len=2602):
    books = load_books(with_kharos=False).books
    lens = [len(b) for b in books]
    P = CopyPasteMutateFitted()
    table = load_table("en")
    real_concat = "".join(books)
    real_lens = {(pol, mc): len(AL.extract_residue(real_concat, mc, pol))
                 for pol, mc in POLICIES}
    print("real-corpus residue lengths:", real_lens, flush=True)
    rows = []
    for rep in range(n_rep):
        digits, letters, true_map = make_v10_seed(seed_len, 11 + rep)
        sur, prov = generate_with_seed(P, digits, lens, 4242 + rep)
        concat = "".join(sur)
        flat = [x for p in prov for x in p]
        # first corpus occurrence of each seed position = genuine innovation
        seen, first = set(), [False] * len(flat)
        for i, pv in enumerate(flat):
            if pv < 0 or pv not in seen:
                first[i] = True
                if pv >= 0:
                    seen.add(pv)
        print(f"rep {rep}: corpus {len(concat)} digits, "
              f"{sum(first)} are first-occurrences of {len(digits)} seed digits",
              flush=True)
        for pol, mc in POLICIES:
            r = AL.extract_residue(concat, mc, pol)
            # which corpus positions did the extraction keep?
            keep = _kept_positions(concat, mc, pol)
            purity = sum(1 for i in keep if first[i]) / max(1, len(keep))
            recall = len({flat[i] for i in keep if flat[i] >= 0}) / len(digits)
            st = np.array([int(c) for c in r], dtype=np.int32)
            sc, key, dec = solve(st, table, n_restarts=n_restarts, seed=7 + rep)
            ka = key_accuracy(key, st, true_map)
            truth = "".join(letters[flat[i]] if flat[i] >= 0 else "?" for i in keep)
            ca = sum(1 for a, b in zip(dec, truth) if a == b) / max(1, len(truth))
            # LENGTH-MATCHED control: the fitted generator is less redundant than
            # 469 itself, so its residue is longer.  Truncate to exactly the
            # length the same policy yields on the REAL corpus and re-solve, so
            # the power number quoted is the power available at 469's own size.
            nm = real_lens[(pol, mc)]
            st2 = st[:nm]
            sc2, key2, dec2 = solve(st2, table, n_restarts=n_restarts, seed=17 + rep)
            ka2 = key_accuracy(key2, st2, true_map)
            ca2 = sum(1 for a, b in zip(dec2, truth[:nm]) if a == b) / max(1, min(nm, len(truth)))
            rows.append(dict(rep=rep, policy=pol, min_copy=mc, n_res=len(r),
                             purity=purity, recall=recall, key_acc=ka,
                             char_acc=ca, score=sc, sample=dec[:80],
                             n_match=nm, key_acc_matched=ka2,
                             char_acc_matched=ca2, score_matched=sc2))
            print(f"  {pol:16s} mc={mc:2d} n={len(r):5d} purity={purity:.3f} "
                  f"recall={recall:.3f} key_acc={ka:.3f} char_acc={ca:.3f} "
                  f"score={sc:.4f} | matched n={nm:5d} key_acc={ka2:.3f} "
                  f"score={sc2:.4f}", flush=True)
            print(f"      {dec[:80]}", flush=True)
    (HERE / "pipeline_power.json").write_text(json.dumps(rows, indent=1))
    print("\nwrote pipeline_power.json")


def _kept_positions(s, mc, pol):
    """The positions extract_residue keeps, recomputed by the same code path."""
    n = len(s)
    if pol == "lz76_innovation":
        out, i = [], 0
        while i < n:
            L = 1
            while i + L <= n and s[i:i + L] in s[:i]:
                L += 1
            L = max(1, L - 1)
            out.append(i + L - 1)
            i += L
        return out
    Lmax = AL.max_match_len(s)
    if pol in ("greedy", "lazy", "optimal"):
        m = AL._mask(n, {"greedy": AL._greedy, "lazy": AL._lazy,
                         "optimal": AL._optimal}[pol](Lmax, n, mc))
    else:
        ms = [AL._mask(n, AL._greedy(Lmax, n, mc)),
              AL._mask(n, AL._lazy(Lmax, n, mc)),
              AL._mask(n, AL._optimal(Lmax, n, mc))]
        r = s[::-1]
        Lr = AL.max_match_len(r)
        ms.append(AL._mask(n, [(n - (p + L), L) for p, L in AL._greedy(Lr, n, mc)]))
        m = bytearray(1 if any(x[i] for x in ms) else 0 for i in range(n))
    return [i for i in range(n) if m[i]]


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 3)
