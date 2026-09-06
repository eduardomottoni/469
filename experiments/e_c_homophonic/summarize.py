"""Render results_c/*.json into the table that goes in FINDINGS.md."""
import json, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
rows = []
for p in sorted((HERE / "results_c").glob("*.json")):
    r = json.loads(p.read_text())
    rows.append(r)
if not rows:
    sys.exit("no results yet")
print("| config | stream | LM | n | V | real best | Markov3(digits) mean±sd | z | p | "
      "Markov3(symbols) max | pi max | verdict |")
print("|---|---|---|---|---|---|---|---|---|---|---|---|")
for r in rows:
    n = r["nulls"]
    md = n.get("Markov3_digits", {})
    ms = n.get("Markov3_symbols", {})
    pi = n.get("Digits_pi", {})
    z = md.get("z", 0.0)
    verdict = "NOISE" if z < 3 else "investigate"
    print(f"| {r['kind']} | {r['stream']} | {r['lm']} | {r['n_symbols']} | {r['V']} | "
          f"**{r['real_best']:.4f}** | {md.get('mean',0):.4f}±{md.get('sd',0):.4f} | "
          f"{z:+.2f} | {md.get('p',1):.4f} | {ms.get('max',0):.4f} | "
          f"{pi.get('max',0):.4f} | {verdict} |")
print()
for r in rows:
    print(f"### {r['kind']} / {r['stream']} / {r['lm']}")
    print("real corpus  :", r["plaintext"][:150])
    for nm in ("Markov3_digits", "Markov3_symbols", "Digits_pi"):
        for e in r["nulls"].get(nm, {}).get("examples", [])[:1]:
            print(f"{nm:15s}:", e[:150])
    print()
