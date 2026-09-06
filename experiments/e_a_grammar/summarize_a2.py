"""Render a2_nulls.json into the Family A null table."""
import json, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
d = json.loads((HERE / "a2_nulls.json").read_text())
KEYS = ["mdl_bits_per_digit", "mean_token_len", "frac_occ_len12", "n_len2_types",
        "V_used", "zipf_slope", "heaps_beta"]
for sname, r in d.items():
    print(f"\n### {sname}  ({r['provenance']})")
    print(f"CopyPasteMutate tuned to LZ76: params {r['copypaste_params']}, "
          f"relative error {r['copypaste_lz_relerr']:.4f} "
          f"(real LZ76 = {r['real']['lz76']})\n")
    fams = list(r["nulls"])
    print("| statistic | real | " + " | ".join(fams) + " |")
    print("|---" * (len(fams) + 2) + "|")
    for k in KEYS:
        cells = []
        for f in fams:
            st = r["nulls"][f]["stats"][k]
            cells.append(f"{st['mean']:.3f}±{st['sd']:.3f} (z={st['z']:+.1f}, p={st['p']:.3f})")
        print(f"| `{k}` | **{r['real'][k]:.3f}** | " + " | ".join(cells) + " |")
    print("\nsurrogate mean LZ76 factors: " +
          ", ".join(f"{f} {r['nulls'][f]['mean_lz76']:.0f}" for f in fams))
