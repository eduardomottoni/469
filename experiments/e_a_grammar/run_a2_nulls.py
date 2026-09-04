"""A2 — Family A statistics scored against surrogates run through the *same*
inducer.

Three rules from the pre-registration:
  * Zipf slope and Heaps beta are compared to the surrogate distribution of the
    same statistic, never to a textbook value.
  * MDL bits are compared only to surrogates matched on LZ76 factor count.
  * Mean token length is likewise compared to surrogates, not just to 1.577.
"""
import json, math, statistics, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
sys.path.insert(0, str(Path(__file__).parent))
import inducers as I
from c469.corpus import load_books, load_contigs, dedup_core
from c469 import surrogate as U
from c469.stats import lz76_factors, token_zipf_slope, heaps_beta
from c469.harness import Result, summarize_null

MAXLEN = 8
N_NULL = 200
OUT = Path(__file__).parent / "a2_nulls.json"


def tune_copypaste(books, target_lz, n_probe=6, seed=7):
    """Find CopyPasteMutate parameters whose LZ76 factor count matches the real
    stream.  Reports the achieved match so an unmatched comparison is never
    quoted as if it were matched."""
    best = None
    grid = []
    # max_segments matters as much as seed_len: CopyPasteMutate pads a book
    # longer than its seed with independent random digits, which drives LZ76 up,
    # so long streams need more segments to stay in range.  Leaving it out of
    # the grid is what made the first contigs run unmatchable.
    for seed_len in (600, 900, 1200, 1800, 2500, 3500, 5000, 7000):
        for p_del in (0.0, 0.006, 0.03):
            for order in (2, 3):
                for mseg in (2, 3, 6, 10):
                    grid.append((seed_len, p_del, order, mseg))
    for (sl, pd, od, ms) in grid:
        g = U.CopyPasteMutate(seed_len=sl, seed_order=od, p_delete=pd,
                              max_segments=ms)
        vals = [lz76_factors("".join(g.generate(books, seed * 1000 + i)))
                for i in range(n_probe)]
        m = statistics.mean(vals)
        err = abs(m - target_lz) / target_lz
        if best is None or err < best[0]:
            best = (err, dict(seed_len=sl, p_delete=pd, seed_order=od,
                              max_segments=ms), m)
        if best[0] < 0.01:                      # good enough, stop searching
            break
    return best


def induce(books):
    return I.mdl_unigram(books, maxlen=MAXLEN)


def stats_of(books):
    ind = induce(books)
    toks = ind.tokens
    prof = ind.length_profile()
    s, r2 = token_zipf_slope(toks)
    return {
        "mdl_total_bits": ind.mdl["total"],
        "mdl_bits_per_digit": ind.mdl["total"] / sum(map(len, books)),
        "mean_token_len": prof["mean_token_len_weighted"],
        "n_len1_types": prof["n_len1_types"],
        "n_len2_types": prof["n_len2_types"],
        "frac_occ_len12": prof["frac_occ_len12"],
        "V_used": prof["V_used"],
        "zipf_slope": s,
        "zipf_r2": r2,
        "heaps_beta": heaps_beta(toks),
        "lz76": lz76_factors("".join(books)),
    }


KEYS = ["mdl_bits_per_digit", "mean_token_len", "frac_occ_len12", "V_used",
        "zipf_slope", "heaps_beta", "n_len2_types"]
# direction in which "language-like" would lie; used only for the empirical p
DIRECTION = {"mdl_bits_per_digit": "less", "mean_token_len": "less",
             "frac_occ_len12": "greater", "V_used": "greater",
             "zipf_slope": "greater", "heaps_beta": "greater",
             "n_len2_types": "greater"}


def main():
    want = sys.argv[1:] or ["dedup_core", "contigs"]
    out = json.loads(OUT.read_text()) if OUT.exists() else {}
    for sname, C in (("dedup_core", dedup_core(load_books())),
                     ("contigs", load_contigs())):
        if sname not in want:
            continue
        books = list(C.books)
        real = stats_of(books)
        print(f"[{sname}] real:", {k: round(real[k], 4) for k in KEYS},
              "lz76", real["lz76"], flush=True)
        err, params, achieved = tune_copypaste(books, real["lz76"])
        print(f"[{sname}] CopyPasteMutate tuned {params} -> lz76 {achieved:.1f} "
              f"vs real {real['lz76']} (rel err {err:.3f})", flush=True)
        fams = [U.Shuffle(), U.MarkovK(2), U.MarkovK(3), U.BlockShuffle(20),
                U.CopyPasteMutate(**params), U.OtherCorpora("pi")]
        nulls = {}
        for fam in fams:
            t0 = time.time()
            vals = {k: [] for k in KEYS}
            lzs = []
            for i in range(N_NULL):
                sb = fam.generate(books, 900001 + i)
                st = stats_of(sb)
                lzs.append(st["lz76"])
                for k in KEYS:
                    vals[k].append(st[k])
            nm = fam.name + ("_tuned" if fam.name == "CopyPasteMutate" else "")
            nulls[nm] = {"n": N_NULL, "mean_lz76": statistics.mean(lzs),
                         "runtime_s": time.time() - t0,
                         "stats": {k: {"mean": statistics.mean(vals[k]),
                                       "sd": statistics.pstdev(vals[k]),
                                       "min": min(vals[k]), "max": max(vals[k]),
                                       "z": ((real[k] - statistics.mean(vals[k])) /
                                             statistics.pstdev(vals[k]))
                                            if statistics.pstdev(vals[k]) else 0.0,
                                       "p": (1 + sum((v >= real[k]) if DIRECTION[k] == "greater"
                                                     else (v <= real[k]) for v in vals[k]))
                                            / (1 + N_NULL)}
                                   for k in KEYS}}
            print(f"  {nm:22s} lz76~{statistics.mean(lzs):6.1f} "
                  + " ".join(f"{k}:z={nulls[nm]['stats'][k]['z']:+.2f}" for k in KEYS),
                  flush=True)
        out[sname] = {"provenance": C.provenance, "real": real,
                      "copypaste_params": params, "copypaste_lz_relerr": err,
                      "nulls": nulls}

        # persist as harness Results, one per statistic
        for k in KEYS:
            r = Result(experiment=f"A2_{sname}", statistic=k,
                       real_value=real[k], direction=DIRECTION[k],
                       corpus_provenance=C.provenance, seed=900001,
                       extra={"inducer": f"mdl_unigram(maxlen={MAXLEN})",
                              "copypaste_params": params,
                              "copypaste_lz_relerr": err,
                              "real_lz76": real["lz76"]})
            for nm, nd in nulls.items():
                st = nd["stats"][k]
                fam_name = "CopyPasteMutate" if nm.startswith("CopyPasteMutate") else nm
                r.nulls.append(__import__("c469.harness", fromlist=["NullResult"]).NullResult(
                    family=fam_name, n=N_NULL, mean=st["mean"], sd=st["sd"],
                    p=st["p"], z=st["z"], maximum=st["max"], minimum=st["min"]))
            r.save()
        OUT.write_text(json.dumps(out, indent=2))
    OUT.write_text(json.dumps(out, indent=2))
    print("wrote", OUT)


if __name__ == "__main__":
    main()
