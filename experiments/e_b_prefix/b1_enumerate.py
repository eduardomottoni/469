"""B1: exhaustive prefix-code structure enumeration.

The reported statistic is `max n_books_parsed` *within a mean-codeword-length
band*, because parse success is trivially easy for codes whose mean codeword
length is near 1 and hard for long codes.  The band that matters for the
pre-registered 1.577 prediction is [1.50, 1.70].

Usage:  python -m experiments.e_b_prefix.b1_enumerate [full|reduced]
"""
from __future__ import annotations

import itertools
import json
import os
import sys
import time
from multiprocessing import Pool
from pathlib import Path

import numpy as np

from c469.corpus import load_books
from .enum_core import (NBIN, BIN0, BINW, enumerate_s1, pack, bin_center,
                        describe)

VLO, VHI = 20, 40         # "effective alphabet is letter-sized" window

OUT = Path(__file__).resolve().parent / "out"

#: (|S1|, tmax).  tmax caps sum|T_p|; codebook size = |S1| + 10k + 9*tmax.
#: |S1| = 9 and 10 are enumerated completely (all 2^10 T assignments).  For
#: smaller S1 the cap is set so each branch stays exhaustive up to a stated
#: codebook size; b3_frontier shows |S1| >= 8 can never reach mean codeword
#: length 1.5 whatever T is, so exhausting its 2^20 tail buys nothing.
FULL_SPACE = {10: 0, 9: 10, 8: 6, 7: 4, 6: 3, 5: 2, 4: 2, 3: 1, 2: 1, 1: 1}
#: the sub-space cheap enough to re-run identically on >=200 surrogates/family
REDUCED_SPACE = {10: 0, 9: 10, 8: 2, 7: 1, 6: 1, 5: 1, 4: 1, 3: 1, 2: 1, 1: 1}

BAND = (1.50, 1.70)       # the pre-registered 1.577 band

_G: dict = {}


def _init(flat, offs):
    _G["flat"], _G["offs"] = flat, offs


def _task(args):
    s1mask, tmax = args
    flat, offs = _G["flat"], _G["offs"]
    nb = offs.shape[0] - 1
    prefixes = np.array([d for d in range(10) if not (s1mask >> d) & 1],
                        dtype=np.int64)
    h2 = np.zeros((nb + 1, NBIN), dtype=np.int64)
    best = np.full((NBIN, 2, 5), -1, dtype=np.int64)
    n = enumerate_s1(flat, offs, s1mask, prefixes, tmax, h2, best, VLO, VHI)
    return n, h2, s1mask, best


def tasks(space):
    out = []
    for ns, tmax in space.items():
        for S1 in itertools.combinations(range(10), ns):
            m = 0
            for d in S1:
                m |= 1 << d
            out.append((m, tmax))
    return out


def run(books, space, procs=None, quiet=True):
    """Returns (n_structures, h2, best) where best[bin][slot] = record|None."""
    procs = procs or int(os.environ.get("C469_PROCS", "8"))
    flat, offs = pack(list(books))
    nb = len(books)
    ts = tasks(space)
    tot = 0
    h2 = np.zeros((nb + 1, NBIN), dtype=np.int64)
    best = [[None, None] for _ in range(NBIN)]
    with Pool(procs, initializer=_init, initargs=(flat, offs)) as p:
        for n, h, s1mask, bb in p.imap_unordered(_task, ts, chunksize=1):
            tot += n
            h2 += h
            for b in range(NBIN):
                for sl in range(2):
                    if bb[b, sl, 0] < 0:
                        continue
                    if best[b][sl] is None or bb[b, sl, 0] > best[b][sl]["parsed"]:
                        best[b][sl] = {"parsed": int(bb[b, sl, 0]),
                                       "s1mask": int(s1mask),
                                       "tcode": int(bb[b, sl, 1]),
                                       "ntok": int(bb[b, sl, 2]),
                                       "toklen": int(bb[b, sl, 3]),
                                       "V": int(bb[b, sl, 4])}
    return tot, h2, best


def band_max(h2, lo=BAND[0], hi=BAND[1]):
    """max n_books_parsed among structures whose mean codeword length is in
    [lo, hi).  Returns -1 if the band is empty."""
    b0 = max(0, int((lo - BIN0) / BINW))
    b1 = min(NBIN, int((hi - BIN0) / BINW) + 1)
    sub = h2[:, b0:b1]
    nz = np.nonzero(sub.sum(axis=1))[0]
    return int(nz.max()) if len(nz) else -1


def band_count(h2, lo=BAND[0], hi=BAND[1]):
    b0 = max(0, int((lo - BIN0) / BINW))
    b1 = min(NBIN, int((hi - BIN0) / BINW) + 1)
    return int(h2[:, b0:b1].sum())


def main():
    which = sys.argv[1] if len(sys.argv) > 1 else "full"
    space = FULL_SPACE if which == "full" else REDUCED_SPACE
    c = load_books()
    books = list(c.books)
    t0 = time.time()
    tot, h2, best = run(books, space)
    dt = time.time() - t0
    OUT.mkdir(exist_ok=True)

    overall = int(np.nonzero(h2.sum(axis=1))[0].max())
    bmax = band_max(h2)
    print(f"space={which} structures={tot:,} time={dt:.1f}s")
    print(f"max n_books_parsed overall     = {overall}/{len(books)}")
    print(f"max n_books_parsed in {BAND}  = {bmax}/{len(books)} "
          f"(n={band_count(h2):,} structures in band)")
    print("\nper mean-codeword-length bin: (bin, n_structures, max parsed, best S1)")
    for b in range(NBIN):
        n = int(h2[:, b].sum())
        if not n:
            continue
        mx = int(np.nonzero(h2[:, b])[0].max())
        r0, r1 = best[b]
        d = describe(r0["s1mask"], r0["tcode"]) if r0 else {}
        v1 = f"{r1['parsed']}(V={r1['V']})" if r1 else "-"
        print(f"  L~{bin_center(b):.2f}  n={n:>12,}  max={mx:>3}  "
              f"S1={d.get('S1','-'):<10} |cb|={d.get('codebook_size','-'):>4} "
              f"V={r0.get('V','-') if r0 else '-':>4}   bestV[{VLO}-{VHI}]={v1}")

    np.save(OUT / f"b1_{which}_h2.npy", h2)
    recs = []
    for b in range(NBIN):
        for sl in range(2):
            if best[b][sl] is None:
                continue
            r = dict(best[b][sl])
            r["slot"] = ["any", f"V_in_{VLO}_{VHI}"][sl]
            r["bin_center"] = bin_center(b)
            r["mean_len"] = r["toklen"] / r["ntok"]
            r.update(describe(r["s1mask"], r["tcode"]))
            recs.append(r)
    Path(OUT / f"b1_{which}.json").write_text(json.dumps({
        "space": which, "space_spec": {str(k): v for k, v in space.items()},
        "n_structures": int(tot), "runtime_s": dt, "n_books": len(books),
        "n_digits": c.n_digits, "provenance": c.provenance,
        "max_books_parsed_overall": overall,
        "max_books_parsed_in_band": bmax,
        "n_structures_in_band": band_count(h2),
        "best_per_length_bin": recs,
    }, indent=2))


if __name__ == "__main__":
    main()
