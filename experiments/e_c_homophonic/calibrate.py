"""Solver calibration: can it actually solve a homophonic cipher of this size?

A negative result from an unvalidated solver is worthless.  We take real
plaintext of the same length as the 469 symbol stream, encipher it
homophonically with the same number of symbols, and check that the solver
recovers a score near the language model's own held-out rate.
"""
import sys, time
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).parent))
from solver import solve, load_table, CHARS
from build_lm import synth, IDX


def make_cipher(n_chars: int, n_sym: int, lang="en", mode="en", seed=3):
    txt = synth(lang, mode, n_chars=n_chars, seed=seed)
    rng = np.random.default_rng(seed)
    # homophone allocation proportional to letter frequency, as a real
    # homophonic cipher would do
    letters = np.array([IDX[c] for c in txt], dtype=np.int32)
    freq = np.bincount(letters, minlength=27).astype(float)
    alloc = np.maximum(1, np.round(freq / freq.sum() * n_sym)).astype(int)
    while alloc.sum() > n_sym:
        alloc[np.argmax(alloc)] -= 1
    while alloc.sum() < n_sym:
        alloc[np.argmax(freq / alloc)] += 1
    homs, s = {}, 0
    for L in range(27):
        homs[L] = list(range(s, s + alloc[L])); s += alloc[L]
    stream = np.array([rng.choice(homs[L]) for L in letters], dtype=np.int32)
    return stream, txt


def main():
    tab = load_table("en")
    for n_chars, n_sym, nr in ((1200, 60, 40), (2400, 80, 40)):
        stream, txt = make_cipher(n_chars, n_sym)
        t0 = time.time()
        npc, key, pt = solve(stream, tab, n_restarts=nr, seed=1)
        # score of the true plaintext under the same model, same length
        from solver import _full_score
        true = np.array([IDX[c] for c in txt], dtype=np.int32)
        ident = np.arange(27, dtype=np.int32)
        tnpc = _full_score(true, ident, tab) / (len(true) - 4)
        acc = sum(a == b for a, b in zip(pt, txt)) / len(txt)
        print(f"n={n_chars} S={n_sym} restarts={nr}: solved={npc:.4f} "
              f"true_plaintext={tnpc:.4f} char_accuracy={acc:.3f} "
              f"({time.time()-t0:.1f}s)")
        print("   ", pt[:110])
        print("   ", txt[:110])


if __name__ == "__main__":
    main()
