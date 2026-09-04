"""Family C — homophonic solving with a surrogate-maximum stopping criterion.

For every configuration we run the *identical* solver on
  * the real 469 symbol stream,
  * N MarkovK(3) digit surrogates pushed through the identical tokenisation,
  * a MarkovK(3) surrogate of the symbol stream itself (exact length and
    vocabulary control),
  * the digits of pi (the "would this find a message in anything" control),
and report the real best-of-restarts as a z-score and empirical p against the
surrogate distribution of best-of-restarts.

These solvers always produce plausible-looking pseudo-plaintext.  Under 3 sigma
is noise, and is reported as noise however good the output looks.
"""
from __future__ import annotations

import json, random, sys, time
from collections import Counter
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "e_a_grammar"))

from solver import solve, load_table                                   # noqa
from streams import fixed_width, mdl_tokens, encode                    # noqa
from c469.corpus import load_books, load_contigs, dedup_core           # noqa
from c469 import surrogate as U                                        # noqa
from c469.harness import Result, NullResult                            # noqa

N_RESTARTS = 8
N_TEMPS, SWEEPS = 100, 5
OUTDIR = HERE / "results_c"
OUTDIR.mkdir(exist_ok=True)


def build_stream(books, kind):
    if kind == "C1_pairs":
        return fixed_width(books, 2, 0)
    if kind == "C1_triples":
        return fixed_width(books, 3, 0)
    if kind.startswith("C1_pairs_phase"):
        return fixed_width(books, 2, int(kind[-1]))
    if kind.startswith("C1_triples_phase"):
        return fixed_width(books, 3, int(kind[-1]))
    if kind == "C2_mdl":
        return mdl_tokens(books)
    raise KeyError(kind)


def symbol_markov3(sym: np.ndarray, seed: int) -> np.ndarray:
    """Order-3 Markov surrogate of the symbol stream itself: identical length
    and (near-)identical symbol inventory, so only the sequential structure of
    the symbols is destroyed."""
    rng = random.Random(seed)
    k = 3
    t = {}
    s = list(map(int, sym))
    for i in range(len(s) - k):
        t.setdefault(tuple(s[i:i + k]), []).append(s[i + k])
    keys = list(t)
    out = list(rng.choice(keys))
    while len(out) < len(s):
        key = tuple(out[-k:])
        nxt = t.get(key) or t[rng.choice(keys)]
        out.append(rng.choice(nxt))
    return np.array(out[:len(s)], dtype=np.int32)


def run_config(books, kind, lm, tab, n_surr, n_restarts, seed=0, log=print):
    toks = build_stream(books, kind)
    sym, vocab = encode(toks)
    t0 = time.time()
    real, key, pt = solve(sym, tab, n_restarts=n_restarts, n_temps=N_TEMPS,
                          sweeps=SWEEPS, seed=seed)
    per_run = time.time() - t0
    log(f"  real {kind}/{lm}: n={len(sym)} V={len(vocab)} best={real:.4f} "
        f"({per_run:.1f}s)")
    log(f"    {pt[:140]}")

    nulls = {}
    # (1) digit-level Markov3 through the identical tokenisation
    for fam_name, gen in (("Markov3_digits", U.MarkovK(3)),
                          ("Digits_pi", U.OtherCorpora("pi"))):
        n = n_surr if fam_name == "Markov3_digits" else min(n_surr, 30)
        vals, vs, examples = [], [], []
        for i in range(n):
            sb = gen.generate(list(books), 500001 + i)
            st, vv = encode(build_stream(sb, kind))
            sc, _, spt = solve(st, tab, n_restarts=n_restarts, n_temps=N_TEMPS,
                               sweeps=SWEEPS, seed=1000 + i)
            vals.append(sc); vs.append(len(vv))
            if i < 2:
                examples.append(spt[:140])
        nulls[fam_name] = {"n": n, "vals": vals, "mean_V": float(np.mean(vs)),
                           "examples": examples}
        log(f"    {fam_name}: mean={np.mean(vals):.4f} sd={np.std(vals):.4f} "
            f"max={max(vals):.4f} meanV={np.mean(vs):.1f}")
    # (2) symbol-level Markov3: exact length and vocabulary control
    vals, examples = [], []
    for i in range(max(1, n_surr // 2)):
        st = symbol_markov3(sym, 700001 + i)
        sc, _, spt = solve(st, tab, n_restarts=n_restarts, n_temps=N_TEMPS,
                           sweeps=SWEEPS, seed=2000 + i)
        vals.append(sc)
        if i < 2:
            examples.append(spt[:140])
    nulls["Markov3_symbols"] = {"n": len(vals), "vals": vals,
                                "mean_V": float(len(vocab)), "examples": examples}
    log(f"    Markov3_symbols: mean={np.mean(vals):.4f} sd={np.std(vals):.4f} "
        f"max={max(vals):.4f}")

    out = {"kind": kind, "lm": lm, "n_symbols": int(len(sym)),
           "V": len(vocab), "real_best": real, "plaintext": pt,
           "key": {vocab[i]: "abcdefghijklmnopqrstuvwxyz "[key[i]]
                   for i in range(len(vocab))},
           "n_restarts": n_restarts, "solve_seconds": per_run, "nulls": {}}
    for nm, nd in nulls.items():
        v = np.asarray(nd["vals"])
        z = (real - v.mean()) / v.std() if v.std() else 0.0
        p = (1 + int((v >= real).sum())) / (1 + len(v))
        out["nulls"][nm] = {"n": nd["n"], "mean": float(v.mean()),
                            "sd": float(v.std()), "max": float(v.max()),
                            "min": float(v.min()), "z": float(z), "p": float(p),
                            "mean_V": nd["mean_V"], "examples": nd["examples"]}
        log(f"    => vs {nm}: z={z:+.2f} p={p:.4f}")
    return out


CONFIGS = [
    # (kind, stream, lm, n_surrogates) -- C2 is the live variant and gets the
    # full 200; C1 is the documented refutation and gets 100.
    ("C2_mdl", "dedup_core", "en", 200),
    ("C2_mdl", "dedup_core", "de_ae", 200),
    ("C2_mdl", "dedup_core", "de_a", 200),
    ("C2_mdl", "contigs", "en", 200),
    ("C2_mdl", "contigs", "de_ae", 200),
    ("C2_mdl", "contigs", "de_a", 200),
    ("C1_pairs", "dedup_core", "en", 200),
    ("C1_pairs", "dedup_core", "de_ae", 200),
    ("C1_pairs", "contigs", "en", 100),
    ("C1_pairs", "contigs", "de_ae", 100),
    ("C1_triples", "dedup_core", "en", 100),
    ("C1_triples", "dedup_core", "de_ae", 100),
    ("C1_pairs_phase1", "dedup_core", "en", 100),
    ("C1_triples_phase1", "dedup_core", "en", 100),
    ("C1_triples_phase2", "dedup_core", "en", 100),
]


def main():
    """Usage: run_c.py <config_index>   (one config per process)."""
    ci = int(sys.argv[1])
    kind, sname, lm, n_surr = CONFIGS[ci]
    out = OUTDIR / f"c{ci:02d}_{kind}_{sname}_{lm}.json"
    if out.exists():
        print("already done", out); return
    C = dedup_core(load_books()) if sname == "dedup_core" else load_contigs()
    books = list(C.books)
    tab = load_table(lm)
    logf = open(OUTDIR / f"c{ci:02d}.log", "w")

    def log(*a):
        print(*a, flush=True)
        print(*a, file=logf, flush=True)

    log(f"[{ci}] {kind} / {sname} / {lm}  n_surr={n_surr} "
        f"restarts={N_RESTARTS} temps={N_TEMPS} sweeps={SWEEPS}")
    t0 = time.time()
    r = run_config(books, kind, lm, tab, n_surr, N_RESTARTS, log=log)
    r["stream"] = sname
    r["provenance"] = C.provenance
    r["wall_seconds"] = time.time() - t0
    out.write_text(json.dumps(r, indent=2))
    res = Result(experiment=f"C_{kind}_{sname}_{lm}",
                 statistic="best_log10P_per_char",
                 real_value=r["real_best"], direction="greater",
                 corpus_provenance=C.provenance,
                 n_candidates_tested=N_RESTARTS,
                 extra={"n_symbols": r["n_symbols"], "V": r["V"],
                        "plaintext_head": r["plaintext"][:200],
                        "note": "surrogate maximum is the stopping criterion; "
                                "under 3 sigma is noise however good the "
                                "output looks"})
    for nm, nd in r["nulls"].items():
        res.nulls.append(NullResult(nm, nd["n"], nd["mean"], nd["sd"],
                                    nd["p"], nd["z"], nd["max"], nd["min"]))
    res.save()
    log("wrote", out)


if __name__ == "__main__":
    main()
