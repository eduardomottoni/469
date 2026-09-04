"""B4: null calibration of the family-B search.

The identical REDUCED-space enumeration is run on the real corpus and on
surrogates from every family in `c469.surrogate.DEFAULT_FAMILIES` plus the
digits of pi.  Four statistics come out of each run:

  max_parsed            max n_books_parsed over the whole space
  band_parsed           max n_books_parsed with mean codeword length in [1.5,1.7]
  vwin_parsed           max n_books_parsed with effective alphabet V in [20,40]
  best_chi2_de / _en    smallest per-symbol chi-square against German/English
                        letter frequencies among the best-per-length-bin
                        structures, under the optimal Hungarian assignment

If the surrogates reach the same values as the corpus, the search has no power
and that is the result to report.

Usage: python -m experiments.e_b_prefix.b4_nulls [n_per_family]
"""
from __future__ import annotations

import json
import math
import sys
import time
from multiprocessing import Pool
from pathlib import Path

import numpy as np

from c469 import surrogate as U
from c469.corpus import load_books
from c469.harness import Result, summarize_null, bh_qvalues
from c469.stats import letter_chi2

from .enum_core import NBIN, enumerate_s1, pack, hist_structure, tmatrix, describe
from .b1_enumerate import REDUCED_SPACE, VLO, VHI, BAND, tasks, band_max

STATISTICS = ("max_parsed", "band_parsed", "vwin_parsed",
              "best_chi2_de", "best_chi2_en")
NULL_FAMILIES = [f.name for f in U.DEFAULT_FAMILIES] + ["Digits_pi"]

OUT = Path(__file__).resolve().parent / "out"
_TASKS = tasks(REDUCED_SPACE)
N_STRUCTURES = sum(math.comb(10 * (10 - bin(m).count("1")), t)
                   for m, tmax in _TASKS for t in range(tmax + 1)
                   if t <= 10 * (10 - bin(m).count("1")))


def search(books) -> dict:
    """One complete reduced-space enumeration; returns the statistic bundle."""
    flat, offs = pack(list(books))
    nb = len(books)
    h2 = np.zeros((nb + 1, NBIN), dtype=np.int64)
    best = np.full((NBIN, 2, 5), -1, dtype=np.int64)
    bmask = np.zeros((NBIN, 2), dtype=np.int64)
    bb = np.empty((NBIN, 2, 5), dtype=np.int64)
    for s1mask, tmax in _TASKS:
        prefixes = np.array([d for d in range(10) if not (s1mask >> d) & 1],
                            dtype=np.int64)
        # h2 accumulates across tasks in place; only `bb` needs resetting.
        bb.fill(-1)
        enumerate_s1(flat, offs, s1mask, prefixes, tmax, h2, bb, VLO, VHI)
        better = bb[:, :, 0] > best[:, :, 0]
        if better.any():
            best[better] = bb[better]
            bmask[better] = s1mask

    vwin = max((int(best[b, 1, 0]) for b in range(NBIN) if best[b, 1, 0] >= 0),
               default=-1)
    out = {
        "max_parsed": int(np.nonzero(h2.sum(axis=1))[0].max()),
        "band_parsed": band_max(h2),
        "vwin_parsed": vwin,
    }
    # letter chi2 over the best-per-bin structures (slot 0), identical rule
    # for real and surrogate
    c_de, c_en = [], []
    for b in range(NBIN):
        if best[b, 0, 0] < 0:
            continue
        s1mask, tcode = int(bmask[b, 0]), int(best[b, 0, 1])
        hist = np.zeros(1110, dtype=np.int64)
        hist_structure(flat, offs, s1mask, tmatrix(tcode), hist)
        counts = hist[hist > 0]
        if len(counts) < 10:
            continue
        c_de.append(letter_chi2(counts, "de"))
        c_en.append(letter_chi2(counts, "en"))
    out["best_chi2_de"] = min(c_de) if c_de else float("inf")
    out["best_chi2_en"] = min(c_en) if c_en else float("inf")
    return out


def _job(args):
    fam_name, seed, books = args
    if fam_name == "real":
        b = books
    else:
        b = U.get(fam_name).generate(list(books), seed)
    return fam_name, seed, search(b)


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 200
    c = load_books()
    books = list(c.books)
    t0 = time.time()
    real = search(books)
    print("real:", json.dumps(real, indent=None), f"({time.time()-t0:.1f}s)")

    jobs = [(f, s, books) for f in NULL_FAMILIES for s in range(n)]
    nulls: dict[str, list[dict]] = {f: [] for f in NULL_FAMILIES}
    t0 = time.time()
    done = 0
    with Pool(4) as p:
        for fam, seed, r in p.imap_unordered(_job, jobs, chunksize=1):
            nulls[fam].append(r)
            done += 1
            if done % 50 == 0:
                el = time.time() - t0
                print(f"  {done}/{len(jobs)}  {el:.0f}s  eta {el/done*(len(jobs)-done):.0f}s",
                      flush=True)

    OUT.mkdir(exist_ok=True)
    Path(OUT / "b4_nulls_raw.json").write_text(json.dumps(
        {"real": real, "nulls": nulls, "n_per_family": n}, indent=2))

    # ---- score each statistic against every family ------------------------
    pvals, labels, results = [], [], []
    for stat in STATISTICS:
        direction = "less" if stat.startswith("best_chi2") else "greater"
        res = Result("e_b_prefix.b4", stat, float(real[stat]), direction,
                     corpus_provenance=c.provenance,
                     n_candidates_tested=len(_TASKS),
                     extra={"space": "reduced",
                            "n_structures": N_STRUCTURES,
                            "band": list(BAND), "V_window": [VLO, VHI]})
        for fam in NULL_FAMILIES:
            vals = [x[stat] for x in nulls[fam]]
            vals = [v for v in vals if np.isfinite(v)]
            if not vals:
                continue
            res.nulls.append(summarize_null(fam, float(real[stat]), vals, direction))
        for nr in res.nulls:
            pvals.append(nr.p)
            labels.append(f"{stat}/{nr.family}")
        results.append(res)

    q = bh_qvalues(pvals)
    qmap = dict(zip(labels, q))
    for res in results:
        res.extra["bh_q"] = {nr.family: qmap[f"{res.statistic}/{nr.family}"]
                             for nr in res.nulls}
        res.save()
        print(f"\n{res.statistic}: real={res.real_value:.4g}  verdict={res.verdict}")
        for nr in res.nulls:
            print(f"   {nr.family:<18} mean={nr.mean:9.4g} sd={nr.sd:8.4g} "
                  f"min={nr.minimum:9.4g} max={nr.maximum:9.4g} "
                  f"p={nr.p:.4f} q={res.extra['bh_q'][nr.family]:.4f} z={nr.z:+.2f}")


if __name__ == "__main__":
    main()
