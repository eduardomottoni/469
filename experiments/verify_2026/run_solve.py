"""Substitution solving on the residue with the alphabet size FIXED A PRIORI.

Why this is not a repeat of Family C.  Family C's `C2_mdl` induced its symbol
inventory from the data by MDL, and on 578 digits MDL collapsed to V = 12 --
fewer symbols than the plaintext alphabet has letters, so the configuration was
ill-posed.  `C1_pairs` fixed V near 95 but had only 289 tokens, three per
symbol, and recovered 6.6% of an injected map.

Here the inventory is a *hypothesis*, declared before looking:

  V10     the residue read one digit at a time: exactly ten symbols.  A ten
          letter reduced-alphabet plaintext.  At n = 578 that is 58
          observations per symbol -- the most sample-efficient cipher
          hypothesis that a base-10 stream admits at all.
  V100    the residue read two digits at a time: exactly one hundred symbols,
          fixed by the encoding, not induced.  The homophonic hypothesis with
          the free parameter removed.

Every configuration is (a) power-tested by injecting a known cipher of the
identical shape and measuring character accuracy, and (b) scored against
matched nulls that hold length and symbol inventory fixed.

Usage:  python experiments/verify_2026/run_solve.py [n_nulls] [n_restarts]
"""
from __future__ import annotations

import json
import random
import sys
import time
from collections import Counter
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "experiments" / "e_c_homophonic"))

import attack_lib as AL                                  # noqa: E402
from solver import solve, load_table, CHARS              # noqa: E402
from c469.harness import summarize_null                  # noqa: E402
from c469.corpus import load_books                       # noqa: E402

LETTER_FREQ = {
    'e': .1202, 't': .0910, 'a': .0812, 'o': .0768, 'i': .0731, 'n': .0695,
    's': .0628, 'r': .0602, 'h': .0592, 'd': .0432, 'l': .0398, 'u': .0288,
    'c': .0271, 'm': .0261, 'f': .0230, 'y': .0211, 'w': .0209, 'g': .0203,
    'p': .0182, 'b': .0149, 'v': .0111, 'k': .0069, 'x': .0017, 'q': .0011,
    'j': .0010, 'z': .0007,
}


# ------------------------------------------------------------- tokenisations

def stream_V10(r: str) -> np.ndarray:
    return np.array([int(c) for c in r], dtype=np.int32)


def stream_V100(r: str) -> np.ndarray:
    return np.array([int(r[i:i + 2]) for i in range(0, len(r) - 1, 2)],
                    dtype=np.int32)


TOKENISERS = {"V10": stream_V10, "V100": stream_V100}


# ------------------------------------------------------------ power injection

def make_subst10_cipher(n_digits: int, seed: int):
    """Ten-letter reduced English enciphered as digits: the V10 hypothesis.

    Returns (digit stream, the TRUE letter plaintext, the kept alphabet).  The
    letter plaintext is what character accuracy is measured against -- comparing
    the solver's letters to the cipher digits would score 0 by construction."""
    t = AL.english_text(n_digits * 4, seed)
    keep = [c for c, _ in Counter(t).most_common(10)]
    m = {c: i for i, c in enumerate(keep)}
    letters = "".join(c for c in t if c in keep)[:n_digits]
    st = np.array([m[c] for c in letters], dtype=np.int32)
    return st, letters, keep


def make_homophonic_cipher(n_tokens: int, seed: int, n_sym: int = 100):
    """English text over 27 letters enciphered with `n_sym` homophones
    allocated in proportion to letter frequency: the V100 hypothesis."""
    rng = random.Random(seed)
    text = AL.english_text(n_tokens, seed)
    freq = dict(LETTER_FREQ)
    freq[" "] = 0.17
    tot = sum(freq.values())
    alloc, pool = {}, list(range(n_sym))
    rng.shuffle(pool)
    i = 0
    for ch, f in sorted(freq.items(), key=lambda kv: -kv[1]):
        k = max(1, int(round(n_sym * f / tot)))
        alloc[ch] = pool[i:i + k] or [pool[i % n_sym]]
        i += k
    stream = np.array([rng.choice(alloc.get(c, alloc[" "])) for c in text],
                      dtype=np.int32)
    return stream, text


def char_accuracy(pred: str, truth: str) -> float:
    m = min(len(pred), len(truth))
    return sum(1 for i in range(m) if pred[i] == truth[i]) / m if m else 0.0


# ------------------------------------------------------------------ the run

def main(n_nulls=60, n_restarts=30, n_power=5):
    books = list(load_books(with_kharos=False).books)
    targets = AL.load_targets()
    tables = {"en": load_table("en"), "de_ae": load_table("de_ae")}
    out = {"n_nulls": n_nulls, "n_restarts": n_restarts, "rows": []}
    # resumable: a run interrupted mid-plan is continued, not restarted
    prev = HERE / "solve_results.json"
    if prev.exists():
        old_rows = json.loads(prev.read_text())
        if old_rows.get("n_nulls") == n_nulls and old_rows.get("n_restarts") == n_restarts:
            out["rows"] = old_rows["rows"]
    done = {(r["target"], r["tok"], r["lm"]) for r in out["rows"]}

    plan = []
    for tname in ("R578_PR", "R1535_mc6_u", "R2058_mc8_u", "R2713_mc12_u"):
        for tok in ("V10", "V100"):
            plan.append((tname, tok, "en"))
    plan.append(("R2058_mc8_u", "V10", "de_ae"))
    plan.append(("R2058_mc8_u", "V100", "de_ae"))

    for tname, tok, lm in plan:
        if (tname, tok, lm) in done:
            continue
        res, src, mc, pol = targets[tname]
        table = tables[lm]
        t0 = time.time()
        st = TOKENISERS[tok](res)
        real, key, pt = solve(st, table, n_restarts=n_restarts, seed=1)

        # ---- power: solve an injected cipher of exactly this shape
        accs, inj_scores = [], []
        for k in range(n_power):
            if tok == "V10":
                cs, truth, _ = make_subst10_cipher(len(res), 200 + k)
            else:
                cs, truth = make_homophonic_cipher(len(st), 200 + k)
            sc, kk, dec = solve(cs, table, n_restarts=n_restarts, seed=2 + k)
            accs.append(char_accuracy(dec, truth))
            inj_scores.append(sc)
        acc = sum(accs) / len(accs)

        # ---- nulls.  E2E draws are truncated to the real residue's exact
        # length so that the comparison is not confounded by length -- the
        # analogue of Family C's symbol-inventory control.
        nulls = [AL.ResidueShuffle(res), AL.ResidueMarkov(res, 3),
                 AL.EndToEnd(AL.U.CopyPasteMutateFitted(), mc, pol),
                 AL.EndToEnd(AL.U.MarkovK(3), mc, pol)]
        nres = []
        for f in nulls:
            vals = []
            i = 0
            while len(vals) < n_nulls:
                d = f.draw(books, 555000 + i); i += 1
                if len(d) < len(res):
                    continue
                d = d[:len(res)]
                sc, _, _ = solve(TOKENISERS[tok](d), table,
                                 n_restarts=max(6, n_restarts // 3), seed=3 + i)
                vals.append(sc)
            nr = summarize_null(f.name, real, vals, "greater")
            nres.append(dict(family=f.name, mean=nr.mean, sd=nr.sd, p=nr.p,
                             z=nr.z, max=nr.maximum))

        row = dict(target=tname, n=len(res), tok=tok, V=int(st.max()) + 1,
                   n_tokens=int(st.shape[0]), lm=lm, real=real,
                   power_char_accuracy=acc, power_accs=accs,
                   power_inj_score=sum(inj_scores) / len(inj_scores),
                   nulls=nres, plaintext=pt[:110], runtime_s=time.time() - t0)
        out["rows"].append(row)
        zs = {d["family"]: d["z"] for d in nres}
        print(f"{tname:14s} {tok:5s} {lm:6s} n={len(res):5d} tok={st.shape[0]:5d} "
              f"V={row['V']:4d} real={real:8.4f} acc={acc:.3f} "
              f"z_shuf={zs['ResidueShuffle']:+6.2f} z_mk3={zs['ResidueMarkov3']:+6.2f} "
              f"z_cpmf={zs['E2E:CopyPasteMutateFitted']:+6.2f}", flush=True)
        print(f"   {pt[:110]}", flush=True)
        (HERE / "solve_results.json").write_text(json.dumps(out, indent=1))

    print("wrote solve_results.json")


if __name__ == "__main__":
    a = sys.argv[1:]
    main(int(a[0]) if a else 60, int(a[1]) if len(a) > 1 else 30)
