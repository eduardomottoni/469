"""Why the two nulls disagree, and which one is the matched one.

`Markov3_digits` generates surrogate *digits* and pushes them through the
identical tokenisation.  That is the right end-to-end null for the pipeline, but
it does not control the resulting symbol inventory: an MDL parse of a Markov-3
digit stream yields far fewer token types than a parse of the real corpus.  A
homophonic solver with more symbols has more free parameters and can always
reach a higher 5-gram score, so a vocabulary mismatch alone manufactures a
positive z.

`Markov3_symbols` resamples the symbol stream itself at order 3, so length and
vocabulary are exactly preserved and only the sequential arrangement is
destroyed.  That is the matched null for this family.

This script shows that every positive z against the digit-level null is
predicted by the vocabulary gap, and reports Benjamini-Hochberg q-values over
all configurations.
"""
import glob, json
from pathlib import Path

HERE = Path(__file__).resolve().parent
import sys
sys.path.insert(0, str(HERE.parents[1]))
from c469.harness import bh_qvalues

rows = [json.load(open(f)) for f in sorted(glob.glob(str(HERE / "results_c" / "*.json")))]
gap, zd, zs = [], [], []
print(f"{'config':34s} {'realV':>6s} {'nullV':>7s} {'gap':>6s} {'z_digits':>9s} {'z_symbols':>10s}")
for r in rows:
    md, ms = r["nulls"]["Markov3_digits"], r["nulls"]["Markov3_symbols"]
    g = r["V"] - md["mean_V"]
    gap.append(g); zd.append(md["z"]); zs.append(ms["z"])
    name = f"{r['kind']}/{r['stream']}/{r['lm']}"
    print(f"{name:34s} {r['V']:6d} {md['mean_V']:7.1f} {g:6.1f} {md['z']:+9.2f} {ms['z']:+10.2f}")


def pearson(x, y):
    n = len(x)
    mx, my = sum(x) / n, sum(y) / n
    sxy = sum((a - mx) * (b - my) for a, b in zip(x, y))
    sxx = sum((a - mx) ** 2 for a in x)
    syy = sum((b - my) ** 2 for b in y)
    return sxy / (sxx * syy) ** 0.5 if sxx and syy else 0.0


print(f"\nPearson r(vocabulary gap, z_digits)  = {pearson(gap, zd):+.3f}")
print(f"Pearson r(vocabulary gap, z_symbols) = {pearson(gap, zs):+.3f}")
print(f"max z_symbols over all {len(rows)} configurations = {max(zs):+.2f}")

pd = [r["nulls"]["Markov3_digits"]["p"] for r in rows]
ps = [r["nulls"]["Markov3_symbols"]["p"] for r in rows]
qd, qs = bh_qvalues(pd), bh_qvalues(ps)
print("\nBenjamini-Hochberg over all configurations "
      "(a family testing many configurations does not quote its best raw p):")
print(f"{'config':34s} {'p_digits':>9s} {'q_digits':>9s} {'p_symbols':>10s} {'q_symbols':>10s}")
for r, a, b, c, d in zip(rows, pd, qd, ps, qs):
    name = f"{r['kind']}/{r['stream']}/{r['lm']}"
    print(f"{name:34s} {a:9.4f} {b:9.4f} {c:10.4f} {d:10.4f}")
