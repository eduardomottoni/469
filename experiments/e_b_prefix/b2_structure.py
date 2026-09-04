"""B2: what explains the single forbidden bigram `07`?

Three candidate readings, each turned into something the data can refute:

  (i)   `0` is a prefix, not a codeword, and `07...` is simply an unassigned
        codeword.  Refutable: the family-B enumeration says whether high-parse
        structures put `0` in S1 (codeword) or outside it (prefix), and the
        SAME mechanism then has to explain `3`->{2,3,9}, so `3` must be a
        prefix too.
  (ii)  `0` is a delimiter / escape.  Refutable: a delimiter partitions the
        stream into "words"; `07` forbidden then means no word begins with `7`,
        `00` should be rare, and the gap-length distribution should look like a
        word-length distribution.
  (iii) `07` is a forbidden PLAINTEXT bigram.  Refutable: it requires `0` and
        `7` to be codewords for two letters whose bigram never occurs, but both
        are high-frequency digits, and no pair of high-frequency German or
        English letters has a forbidden bigram.

Everything is scored against the surrogate families.

Usage: python -m experiments.e_b_prefix.b2_structure [n_nulls]
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

import numpy as np

from c469 import surrogate as U
from c469.corpus import load_books
from c469.harness import Result, summarize_null, bh_qvalues
from c469.stats import (ngram_counts, missing_bigrams, unigram_H, DIGITS,
                        LETTER_FREQ_DE, LETTER_FREQ_EN)

OUT = Path(__file__).resolve().parent / "out"


def n_missing_bigrams(books) -> float:
    return float(len(missing_bigrams(books)))


def gap_lengths(books, sep: str = "0"):
    """Lengths of the maximal `sep`-free runs, if `sep` were a delimiter."""
    out = []
    for b in books:
        for piece in b.split(sep):
            out.append(len(piece))
    return out


def delimiter_profile(books, sep: str = "0") -> dict:
    g = gap_lengths(books, sep)
    nz = [x for x in g if x > 0]
    first = Counter()
    last = Counter()
    for b in books:
        for piece in b.split(sep):
            if piece:
                first[piece[0]] += 1
                last[piece[-1]] += 1
    tot = sum(first.values())
    return {
        "n_words": len(nz),
        "n_empty_gaps": len(g) - len(nz),          # i.e. `00` occurrences+edges
        "mean_word_len": float(np.mean(nz)) if nz else 0.0,
        "sd_word_len": float(np.std(nz)) if nz else 0.0,
        "max_word_len": max(nz) if nz else 0,
        "initial_dist": {d: first[d] / tot for d in DIGITS if tot},
        "final_dist": {d: last[d] / tot for d in DIGITS if tot},
        "n_initials_absent": sum(1 for d in DIGITS if not first[d]),
    }


def main():
    nn = int(sys.argv[1]) if len(sys.argv) > 1 else 500
    OUT.mkdir(exist_ok=True)
    c = load_books()
    books = list(c.books)
    rep: dict = {"provenance": c.provenance}

    # ---------------------------------------------------------- the raw facts
    c1 = ngram_counts(books, 1)
    c2 = ngram_counts(books, 2)
    n1, n2 = sum(c1.values()), sum(c2.values())
    uni = {d: c1[d] / n1 for d in DIGITS}
    rep["unigrams"] = uni
    rep["missing_bigrams"] = missing_bigrams(books)
    rep["expected_07"] = n2 * uni["0"] * uni["7"]
    lowest = sorted(((c2[a + b], a + b) for a in DIGITS for b in DIGITS))[:12]
    rep["rarest_bigrams"] = [{"bigram": g, "count": int(k),
                              "expected": n2 * uni[g[0]] * uni[g[1]]}
                             for k, g in lowest]
    print(f"missing bigrams: {rep['missing_bigrams']}  "
          f"(expected count of 07 under independence: {rep['expected_07']:.1f})")
    print("rarest bigrams (obs/exp):")
    for r in rep["rarest_bigrams"]:
        print(f"   {r['bigram']}  obs={r['count']:>4}  exp={r['expected']:6.1f}")

    # -------------------------------------------- book-final digits (parse gate)
    fin = Counter(b[-1] for b in books)
    ini = Counter(b[0] for b in books)
    rep["book_final_digits"] = dict(fin)
    rep["book_initial_digits"] = dict(ini)
    print(f"\nbook-final digits: {dict(sorted(fin.items()))}")
    print(f"book-initial digits: {dict(sorted(ini.items()))}")

    # ------------------------------------ (i) does 0 want to be a prefix?
    b1 = json.loads((OUT / "b1_full.json").read_text()) if (OUT / "b1_full.json").exists() \
        else json.loads((OUT / "b1_reduced.json").read_text())
    recs = [r for r in b1["best_per_length_bin"] if r["slot"] == "any"]
    with0 = [r for r in recs if "0" in r["S1"]]
    without0 = [r for r in recs if "0" not in r["S1"]]
    rep["hypothesis_i"] = {
        "source": b1["space"],
        "n_length_bins": len(recs),
        "bins_where_best_structure_has_0_as_codeword": len(with0),
        "bins_where_best_structure_has_0_as_prefix": len(without0),
        "best_parse_with_0_codeword": max((r["parsed"] for r in with0), default=-1),
        "best_parse_with_0_prefix": max((r["parsed"] for r in without0), default=-1),
        "bins_where_3_is_prefix": sum(1 for r in recs if "3" not in r["S1"]),
        "bins_where_0_prefix_and_3_prefix": sum(
            1 for r in recs if "0" not in r["S1"] and "3" not in r["S1"]),
    }
    print("\n(i) 0-as-prefix:", json.dumps(rep["hypothesis_i"], indent=2))

    # ------------------------------------------- (ii) 0 as a delimiter
    prof = delimiter_profile(books, "0")
    rep["hypothesis_ii"] = prof
    print("\n(ii) 0-as-delimiter:")
    print(f"   words={prof['n_words']}  mean len={prof['mean_word_len']:.2f} "
          f"+-{prof['sd_word_len']:.2f}  max={prof['max_word_len']}  "
          f"empty gaps (`00`) = {prof['n_empty_gaps']}")
    print("   word-initial digit distribution: " +
          " ".join(f"{d}:{prof['initial_dist'][d]:.3f}" for d in DIGITS))
    # the sharp form of (ii): if `0` delimits, no word starts with `7`
    rep["hypothesis_ii"]["p_word_initial_7"] = prof["initial_dist"]["7"]

    # ------------------------------------------ (iii) forbidden plaintext bigram
    # (iii) needs two letters at the frequencies of `0` and `7`.  Report the
    # letters those digits would have to be, and their plausibility.
    def nearest(freq, table):
        return sorted(table.items(), key=lambda kv: abs(kv[1] - freq))[:3]
    rep["hypothesis_iii"] = {
        "freq_0": uni["0"], "freq_7": uni["7"],
        "de_candidates_for_0": nearest(uni["0"], LETTER_FREQ_DE),
        "de_candidates_for_7": nearest(uni["7"], LETTER_FREQ_DE),
        "en_candidates_for_0": nearest(uni["0"], LETTER_FREQ_EN),
        "en_candidates_for_7": nearest(uni["7"], LETTER_FREQ_EN),
        "note": ("(iii) requires a forbidden bigram between two letters each of "
                 "frequency ~5-8%.  Those are among the ten commonest letters in "
                 "both languages; no such pair is forbidden."),
    }
    print("\n(iii) if 0 and 7 are single letters, they must be at "
          f"{uni['0']:.3f} / {uni['7']:.3f} frequency:")
    print("   DE nearest for 0:", rep["hypothesis_iii"]["de_candidates_for_0"])
    print("   DE nearest for 7:", rep["hypothesis_iii"]["de_candidates_for_7"])

    # ---------------------------------------------------------------- nulls
    fams = [f.name for f in U.DEFAULT_FAMILIES] + ["Digits_pi", "IID"]
    pvals, labels, results = [], [], []
    for statname, fn, direction in (
            ("n_missing_bigrams", n_missing_bigrams, "greater"),
            ("word_initial_7_rate",
             lambda bk: delimiter_profile(bk, "0")["initial_dist"]["7"], "less"),
            ("mean_word_len_sep0",
             lambda bk: delimiter_profile(bk, "0")["mean_word_len"], "greater")):
        real = float(fn(books))
        res = Result("e_b_prefix.b2", statname, real, direction,
                     corpus_provenance=c.provenance)
        for f in fams:
            vals = [float(fn(U.get(f).generate(list(books), s))) for s in range(nn)]
            res.nulls.append(summarize_null(f, real, vals, direction))
        for nr in res.nulls:
            pvals.append(nr.p)
            labels.append(f"{statname}/{nr.family}")
        results.append(res)

    q = bh_qvalues(pvals)
    qmap = dict(zip(labels, q))
    for res in results:
        res.extra["bh_q"] = {nr.family: qmap[f"{res.statistic}/{nr.family}"]
                             for nr in res.nulls}
        res.save()
        print(f"\n{res.statistic}: real={res.real_value:.5g}  {res.verdict}")
        for nr in res.nulls:
            print(f"   {nr.family:<18} {nr.mean:9.4g} +- {nr.sd:<8.3g} "
                  f"p={nr.p:.4f} q={res.extra['bh_q'][nr.family]:.4f}")

    Path(OUT / "b2_structure.json").write_text(json.dumps(rep, indent=2, default=str))


if __name__ == "__main__":
    main()
