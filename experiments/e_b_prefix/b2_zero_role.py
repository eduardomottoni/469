"""B2 direct test: does the corpus want `0` to be a prefix or a codeword?

Hypothesis (i) for the missing bigram `07` says `0` is a prefix and `07...` is
an unassigned codeword.  That is a claim about S1 membership, and the whole
reduced-space enumeration can answer it directly: split every structure by
whether 0 is in S1, and compare the best parse each half achieves -- within a
mean-codeword-length band, so the comparison is not just "shorter codes parse
more easily".  The same split is applied to `3`, whose {2,3,9} continuations
are the other near-forbidden bigrams: hypothesis (i) has to make `3` a prefix
too, or it is explaining one gap with a mechanism it denies for the others.

Usage: python -m experiments.e_b_prefix.b2_zero_role
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from c469.corpus import load_books
from .enum_core import NBIN, BIN0, BINW, enumerate_s1, pack
from .b1_enumerate import REDUCED_SPACE, VLO, VHI, BAND, tasks

OUT = Path(__file__).resolve().parent / "out"


def split_by_digit(books, digit: int):
    flat, offs = pack(list(books))
    nb = len(books)
    h = {"codeword": np.zeros((nb + 1, NBIN), np.int64),
         "prefix": np.zeros((nb + 1, NBIN), np.int64)}
    for s1mask, tmax in tasks(REDUCED_SPACE):
        prefixes = np.array([d for d in range(10) if not (s1mask >> d) & 1],
                            dtype=np.int64)
        hh = np.zeros((nb + 1, NBIN), np.int64)
        bb = np.full((NBIN, 2, 5), -1, np.int64)
        enumerate_s1(flat, offs, s1mask, prefixes, tmax, hh, bb, VLO, VHI)
        h["codeword" if (s1mask >> digit) & 1 else "prefix"] += hh
    return h


def summarise(h, lo, hi):
    b0 = max(0, int((lo - BIN0) / BINW))
    b1 = min(NBIN, int((hi - BIN0) / BINW) + 1)
    out = {}
    for k, m in h.items():
        sub = m[:, b0:b1]
        n = int(sub.sum())
        nz = np.nonzero(sub.sum(axis=1))[0]
        out[k] = {"n_structures": n,
                  "max_books_parsed": int(nz.max()) if len(nz) else -1,
                  "mean_books_parsed": float((np.arange(m.shape[0])[:, None] * sub).sum() / n) if n else None}
    return out


def main():
    c = load_books()
    books = list(c.books)
    rep = {"provenance": c.provenance, "space": "reduced"}
    for digit in (0, 3, 1):
        h = split_by_digit(books, digit)
        rep[f"digit_{digit}"] = {
            "all_lengths": summarise(h, 1.0, 3.0),
            "band_1.50_1.70": summarise(h, *BAND),
        }
        print(f"\ndigit {digit}: is it better as a codeword or as a prefix?")
        for scope, d in rep[f"digit_{digit}"].items():
            print(f"  {scope}")
            for role, v in d.items():
                print(f"     as {role:<9} n={v['n_structures']:>7,}  "
                      f"max parsed={v['max_books_parsed']:>3}/70  "
                      f"mean parsed="
                      f"{v['mean_books_parsed']:.2f}" if v["mean_books_parsed"]
                      else f"     as {role}: empty")
    OUT.mkdir(exist_ok=True)
    Path(OUT / "b2_zero_role.json").write_text(json.dumps(rep, indent=2))


if __name__ == "__main__":
    main()
