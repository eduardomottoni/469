"""Family E: which model explains the 469 corpus?

One held-out protocol for everything (leave-one-book-out), one unit (bits per
digit), and every model is a real decodable code so the numbers are commensurable.

  * order-k Markov, k=0..6, KT (alpha=1/2) smoothed
  * CTW / variable-order context tree, depths 2..16
  * relative-LZ copy code (the family-E hypothesis made into a code)

BIC/AIC are reported too, but the held-out numbers are the ones to trust: a
high-order Markov model on 11k digits is memorising, and only the held-out
protocol charges it for that.
"""
from __future__ import annotations

import json, math, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from c469.corpus import load_books
from c469 import surrogate as U
from c469.stats import (held_out_bits_per_digit, ctw_bits_per_digit,
                        ctw_heldout_bits_per_digit, relative_lz_bits_per_digit,
                        markov_logprob, lz76_factors)

HERE = Path(__file__).resolve().parent


def model_table(books, label):
    n = sum(map(len, books))
    rows = []
    for k in range(7):
        ho = held_out_bits_per_digit(books, k)
        insample = markov_logprob(books, books, k)
        params = 9 * (10 ** k)
        nll = insample * n
        rows.append(dict(model=f"Markov{k}", heldout_bpd=ho, insample_bpd=insample,
                         params=params,
                         aic=2 * params + 2 * nll * math.log(2) / math.log(2),
                         bic=params * math.log2(n) + nll))
    for d in (2, 4, 8, 16):
        rows.append(dict(model=f"CTW{d}", heldout_bpd=ctw_heldout_bits_per_digit(books, d),
                         insample_bpd=ctw_bits_per_digit(books, d),
                         params=float("nan"), aic=float("nan"),
                         bic=ctw_bits_per_digit(books, d) * n))
    rl = relative_lz_bits_per_digit(books, loo=True)
    rows.append(dict(model="RelativeLZ(copy)", heldout_bpd=rl,
                     insample_bpd=relative_lz_bits_per_digit(books, loo=False),
                     params=float("nan"), aic=float("nan"), bic=rl * n))
    for r in rows:
        r["corpus"] = label
    return rows


def main():
    c = load_books(with_kharos=False)
    books = list(c.books)
    out = {"real": model_table(books, "real")}
    print(f"{'model':18s} {'heldout b/d':>12s} {'in-sample':>10s} {'BIC bits':>10s}")
    for r in out["real"]:
        print(f"{r['model']:18s} {r['heldout_bpd']:12.4f} {r['insample_bpd']:10.4f} "
              f"{r['bic']:10.0f}")
    # the same table for surrogates: the copy code must NOT win on everything
    for fam in (U.Shuffle(), U.MarkovK(3), U.CopyPasteMutate()):
        s = fam.generate(books, 12345)
        out[fam.name] = model_table(s, fam.name)
        print(f"--- {fam.name} (lz76={lz76_factors(''.join(s))})")
        for r in out[fam.name]:
            if r["model"] in ("Markov3", "CTW8", "RelativeLZ(copy)"):
                print(f"{r['model']:18s} {r['heldout_bpd']:12.4f}")
    (HERE / "model_comparison.json").write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
