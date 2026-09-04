"""If family E holds, the only object that can carry a message is the seed:
the material the corpus is NOT a copy of.  This extracts three estimates of it.

  A. LZ76 innovation string -- the one new digit ending each of the 608 factors
     of the corpus, in order.  This is the classical "production" content.
  B. LZ77 literal digits of the master contig: digits the greedy copy parse
     could not take from earlier material.
  C. The information bound: the relative-LZ code length of the corpus in bits,
     divided by log2(10) -> equivalent digits of independent content.

Any real plaintext must live inside A/B; C is the hard upper bound on how much
plaintext there could be.
"""
from __future__ import annotations

import json, math, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from c469.corpus import load_books
from c469.stats import _longest_match, relative_lz_bits_per_digit

REPO = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent


def lz76_parse(s):
    out, i = [], 0
    while i < len(s):
        L = 1
        while i + L <= len(s) and s[i:i + L] in s[:i]:
            L += 1
        L = max(1, L - 1)
        out.append((i, L))
        i += L
    return out


def lz77_literals(s, min_copy=3):
    lits, p, copies = [], 0, 0
    while p < len(s):
        L, _ = _longest_match(s[:p], s, p)
        if L >= min_copy:
            p += L; copies += 1
        else:
            lits.append((p, s[p])); p += 1
    return lits, copies


def main():
    c = load_books(with_kharos=False)
    books = list(c.books)
    concat = "".join(books)
    master_p = REPO / "data" / "master_v1.txt"
    master = master_p.read_text().strip() if master_p.exists() else concat

    f_corpus = lz76_parse(concat)
    innov_corpus = "".join(concat[i + L - 1] for i, L in f_corpus)
    f_master = lz76_parse(master)
    innov_master = "".join(master[i + L - 1] for i, L in f_master)

    lits, ncopy = lz77_literals(master)
    lit_str = "".join(ch for _, ch in lits)

    bits = relative_lz_bits_per_digit(books, loo=False) * len(concat)
    equiv_digits = bits / math.log2(10)

    (REPO / "data" / "seed_estimate.txt").write_text(innov_master + "\n")
    out = dict(
        corpus_digits=len(concat), master_digits=len(master),
        lz76_factors_corpus=len(f_corpus), lz76_factors_master=len(f_master),
        seed_A_lz76_innovation_master_len=len(innov_master),
        seed_A_lz76_innovation_corpus_len=len(innov_corpus),
        seed_B_lz77_literals_master_len=len(lit_str),
        seed_B_copies=ncopy,
        information_bound_bits=bits,
        information_bound_equivalent_digits=equiv_digits,
        seed_A_master=innov_master,
        seed_A_corpus=innov_corpus,
        seed_B_master=lit_str,
    )
    (HERE / "seed_estimate.json").write_text(json.dumps(out, indent=1))
    print(json.dumps({k: v for k, v in out.items() if not k.startswith("seed_A_m")
                      and not k.startswith("seed_B_m") and k != "seed_A_corpus"},
                     indent=1))
    print("wrote data/seed_estimate.txt (%d digits)" % len(innov_master))


if __name__ == "__main__":
    main()
