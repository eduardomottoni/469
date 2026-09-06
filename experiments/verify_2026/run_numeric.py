"""Pre-registered numeric / periodicity attack on the residue.

PROTOCOL (fixed before any null was drawn):

  targets     the five residues of attack_lib.load_targets()
  statistics  attack_lib.STATS, ten of them, direction declared per statistic
  nulls       6 end-to-end families (c469.surrogate.DEFAULT_FAMILIES pushed
              through the identical extraction) + 2 matched families
              (ResidueShuffle, ResidueMarkov3 -- exact length, exact/near-exact
              digit inventory).  The matched families decide; the end-to-end
              ones are reported for the pipeline and are known to carry a
              length confound, which is printed alongside.
  power       every statistic is evaluated on 20 injected plaintexts per
              hypothesis at the target's exact length.  A statistic that does
              not separate an injected plaintext from its own matched null at
              alpha = 0.01 in at least 80% of injections is UNDERPOWERED for
              that hypothesis and its null result is reported as such.
  multiplicity  10 statistics x 5 targets = 50 tests; Benjamini-Hochberg q
              across all of them, and the raw p is never quoted alone.

Usage:  python experiments/verify_2026/run_numeric.py [n_nulls]
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1]))

import attack_lib as AL                                     # noqa: E402
from c469.harness import summarize_null, bh_qvalues         # noqa: E402
from c469.corpus import load_books                          # noqa: E402


def pct(vals, q):
    v = sorted(vals)
    i = min(len(v) - 1, max(0, int(round(q * (len(v) - 1)))))
    return v[i]


def main(n_nulls=200, n_inject=20):
    books = list(load_books(with_kharos=False).books)
    targets = AL.load_targets()
    out = {"n_nulls": n_nulls, "n_inject": n_inject, "targets": {}}

    for tname, (res, src, mc, pol) in targets.items():
        t0 = time.time()
        print(f"\n=== {tname}  n={len(res)}  ({src}, min_copy={mc}, {pol})", flush=True)
        nulls = AL.default_nulls(res, mc, pol)
        draws = {f.name: [] for f in nulls}
        lens = {f.name: [] for f in nulls}
        for f in nulls:
            for i in range(n_nulls):
                d = f.draw(books, 777000 + i)
                draws[f.name].append(d)
                lens[f.name].append(len(d))
            print(f"  drew {f.name}: mean len {sum(lens[f.name])/n_nulls:.0f}", flush=True)

        rec = {"n": len(res), "source": src, "min_copy": mc, "policy": pol,
               "null_lengths": {k: sum(v) / len(v) for k, v in lens.items()},
               "stats": {}}

        for sname, (fn, direction) in AL.STATS.items():
            real = float(fn(res))
            nres = {}
            for f in nulls:
                vals = [float(fn(d)) for d in draws[f.name]]
                nr = summarize_null(f.name, real, vals, direction)
                nres[f.name] = dict(mean=nr.mean, sd=nr.sd, p=nr.p, z=nr.z,
                                    max=nr.maximum, min=nr.minimum)
            # power: threshold from the matched ResidueShuffle null
            mvals = [float(fn(d)) for d in draws["ResidueShuffle"]]
            thr = pct(mvals, 0.99) if direction == "greater" else pct(mvals, 0.01)
            power = {}
            for iname, inj in AL.INJECTORS.items():
                hits, vals = 0, []
                for k in range(n_inject):
                    v = float(fn(inj(len(res), seed=100 + k)))
                    vals.append(v)
                    if (v > thr) if direction == "greater" else (v < thr):
                        hits += 1
                power[iname] = dict(rate=hits / n_inject,
                                    mean=sum(vals) / len(vals))
            rec["stats"][sname] = dict(real=real, direction=direction,
                                       threshold_alpha01=thr,
                                       nulls=nres, power=power)
            print(f"  {sname:16s} real={real:10.5f}  "
                  f"z_shuf={nres['ResidueShuffle']['z']:+6.2f} "
                  f"z_mk3={nres['ResidueMarkov3']['z']:+6.2f}  "
                  f"power(a1z26={power['a1z26']['rate']:.2f} "
                  f"ascii={power['ascii']['rate']:.2f} "
                  f"dates={power['dates']['rate']:.2f} "
                  f"vig7={power['vigenere7']['rate']:.2f} "
                  f"sub10={power['subst10']['rate']:.2f} "
                  f"iid={power['iid_ctrl']['rate']:.2f})", flush=True)
        rec["runtime_s"] = time.time() - t0
        out["targets"][tname] = rec

    # Benjamini-Hochberg over every (target, statistic) against each matched null
    for fam in ("ResidueShuffle", "ResidueMarkov3"):
        keys, ps = [], []
        for tname, rec in out["targets"].items():
            for sname, sd in rec["stats"].items():
                keys.append((tname, sname)); ps.append(sd["nulls"][fam]["p"])
        qs = bh_qvalues(ps)
        for (tname, sname), q in zip(keys, qs):
            out["targets"][tname]["stats"][sname].setdefault("bh_q", {})[fam] = q

    (HERE / "numeric_results.json").write_text(json.dumps(out, indent=1))
    print("\nwrote numeric_results.json")


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 200)
