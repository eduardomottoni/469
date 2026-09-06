"""Render every table in SEED_ATTACK.md from the three result files."""
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent


def load(n):
    p = HERE / n
    return json.loads(p.read_text()) if p.exists() else None


def residue_table():
    d = load("residues.json")
    want = ["PR_seed_estimate", "concat:lz76_innovation", "concat:greedy_mc3",
            "concat:greedy_mc6", "concat:union_mc5", "concat:union_mc6",
            "concat:union_mc8", "concat:union_mc10", "concat:union_mc12",
            "master:union_mc6", "master:union_mc8", "master:union_mc12"]
    by = {r["name"]: r for r in d["stats"]}
    print("| residue | n | unigram H | IC | bigram chi2 (df=81) | LZ76 factors | LZ76/n |")
    print("|---|---|---|---|---|---|---|")
    for w in want:
        r = by.get(w)
        if not r:
            continue
        print(f"| `{w}` | {r['n']} | {r['unigram_H']:.4f} | {r['ic']:.5f} | "
              f"{r['bigram_chi2']:.1f} | {r['lz76']} | {r['lz76']/r['n']:.3f} |")


def pipeline_table():
    rows = load("pipeline_power.json")
    if not rows:
        return
    agg = defaultdict(list)
    for r in rows:
        agg[(r["policy"], r["min_copy"])].append(r)
    print("\n| extraction | n_res (synthetic) | purity | seed recall | key acc (full) "
          "| n matched to 469 | **key acc (matched)** |")
    print("|---|---|---|---|---|---|---|")
    for (pol, mc), rs in agg.items():
        f = lambda k: sum(x[k] for x in rs) / len(rs)          # noqa: E731
        print(f"| `{pol}` min_copy={mc} | {f('n_res'):.0f} | {f('purity'):.3f} | "
              f"{f('recall'):.3f} | {f('key_acc'):.3f} | {rs[0].get('n_match','-')} | "
              f"**{f('key_acc_matched'):.3f}** |")


def numeric_table():
    d = load("numeric_results.json")
    if not d:
        return
    print(f"\n(n_nulls = {d['n_nulls']}, n_inject = {d['n_inject']})")
    for t, rec in d["targets"].items():
        print(f"\n**{t}** (n={rec['n']}, {rec['source']}, min_copy={rec['min_copy']}, "
              f"{rec['policy']})")
        print("\n| statistic | real | z ResidueShuffle | z ResidueMarkov3 | p (Mk3) | "
              "BH q (Mk3) | power a1z26 | ascii | dates | vig7 | sub10 | FP rate (iid) |")
        print("|---|---|---|---|---|---|---|---|---|---|---|---|")
        for s, sd in rec["stats"].items():
            n1 = sd["nulls"]["ResidueShuffle"]; n2 = sd["nulls"]["ResidueMarkov3"]
            pw = sd["power"]; q = sd.get("bh_q", {}).get("ResidueMarkov3", float("nan"))
            print(f"| `{s}` | {sd['real']:.5f} | {n1['z']:+.2f} | {n2['z']:+.2f} | "
                  f"{n2['p']:.4f} | {q:.3f} | {pw['a1z26']['rate']:.2f} | "
                  f"{pw['ascii']['rate']:.2f} | {pw['dates']['rate']:.2f} | "
                  f"{pw['vigenere7']['rate']:.2f} | {pw['subst10']['rate']:.2f} | "
                  f"{pw['iid_ctrl']['rate']:.2f} |")
        print("\nend-to-end null residue lengths: " +
              ", ".join(f"{k}={v:.0f}" for k, v in rec["null_lengths"].items()))


def solve_table():
    d = load("solve_results.json")
    if not d:
        return
    print(f"\n(n_nulls = {d['n_nulls']}, n_restarts = {d['n_restarts']})")
    print("\n| target | n | tokenisation | V | tokens | LM | best log10P/char | "
          "injected-cipher score | **recovery acc** | z Shuffle | z Markov3 | z CPMFitted | p (Mk3) |")
    print("|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for r in d["rows"]:
        z = {x["family"]: x for x in r["nulls"]}
        print(f"| {r['target']} | {r['n']} | {r['tok']} | {r['V']} | {r['n_tokens']} | "
              f"{r['lm']} | {r['real']:.4f} | {r['power_inj_score']:.4f} | "
              f"**{r['power_char_accuracy']:.3f}** | "
              f"{z['ResidueShuffle']['z']:+.2f} | {z['ResidueMarkov3']['z']:+.2f} | "
              f"{z['E2E:CopyPasteMutateFitted']['z']:+.2f} | "
              f"{z['ResidueMarkov3']['p']:.4f} |")
    print("\nBest decryptions:")
    for r in d["rows"]:
        print(f"  {r['target']:14s} {r['tok']:5s} {r['lm']:6s} : {r['plaintext'][:96]}")


if __name__ == "__main__":
    print("## Residues\n"); residue_table()
    print("\n## Pipeline power (message injected into the seed)"); pipeline_table()
    print("\n## Numeric / periodicity statistics"); numeric_table()
    print("\n## Fixed-V substitution solving"); solve_table()
