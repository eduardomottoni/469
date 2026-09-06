"""G1 -- is the two-dialect split real, or a length / collection artefact?

Claim under test (c469/cribs.py): every 469 string with a claimed English
meaning occurs ZERO times in the Hellgate books, while every 469 string that
DOES occur in the books is an untranslated quotation.

The obvious confound is length: short strings are more likely to occur by
chance, long ones less.  If the split were length-driven, the translated
(absent) set would be the LONG one.  It is the short one, so the confound runs
the wrong way -- but we measure it rather than assert it.

Null quantity: p_hit(L), the probability that a length-L window of genuine
469 book text occurs somewhere else in the corpus.  Computed leave-one-out
(a window of book i counts as a hit only if it also occurs in some book j!=i),
so it is the honest "would a real 469 utterance of this length show up in the
library?" rate, on a corpus that is famously repeat-heavy.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
from c469 import corpus, cribs  # noqa: E402

TRANSLATED = [  # (string, speaker) -- claimed English meaning, per cribs.py
    ("653768764", "The Evil Eye / Elder Bonelord"),
    ("659978", "Elder Bonelord"),
    ("54764", "Elder Bonelord"),
    ("486486", "A Wrinkled Bonelord (own name)"),
]
QUOTATION = [  # occurs in the books, no translation ever claimed
    ("485611800364197", "A Wrinkled Bonelord voice"),
    ("78572611857643646724", "A Wrinkled Bonelord voice"),
    ("114514519485611451908304576512282177", "Chayenne 2009"),
    ("6612527570584", "Chayenne 2009"),
]


def p_hit_table(books: list[str], lengths: list[int]) -> dict[int, dict]:
    out = {}
    for L in lengths:
        hit = tot = 0
        for i, b in enumerate(books):
            others = "|".join(books[:i] + books[i + 1:])
            for j in range(len(b) - L + 1):
                tot += 1
                hit += others.find(b[j:j + L]) >= 0
        out[L] = {"L": L, "n_windows": tot, "n_hit": hit,
                  "p_hit": hit / tot if tot else float("nan")}
    return out


def main() -> None:
    c = corpus.load_books()
    books = list(c.books)
    joined = "|".join(books)

    lengths = sorted({len(s) for s, _ in TRANSLATED + QUOTATION})
    tab = p_hit_table(books, lengths)

    print("leave-one-out hit rate for genuine 469 windows")
    print(" L   windows    hits   p_hit")
    for L in lengths:
        r = tab[L]
        print(f"{L:3d} {r['n_windows']:8d} {r['n_hit']:7d}  {r['p_hit']:.4f}")

    print("\ntranslated cribs -- predicted p(occurs), observed:")
    log_miss = 0.0
    for s, who in TRANSLATED:
        p = tab[len(s)]["p_hit"]
        occ = joined.count(s)
        log_miss += math.log(max(1e-12, 1 - p))
        print(f"  {s:<38} L={len(s):2d} p_hit={p:.4f}  observed={occ}  {who}")
    print(f"  => P(all {len(TRANSLATED)} absent | genuine-469 model) = {math.exp(log_miss):.4g}")

    print("\nquotation cribs -- predicted p(occurs), observed:")
    log_hit = 0.0
    for s, who in QUOTATION:
        p = tab[len(s)]["p_hit"]
        occ = joined.count(s)
        log_hit += math.log(max(1e-12, p))
        print(f"  {s:<38} L={len(s):2d} p_hit={p:.4f}  observed={occ}  {who}")
    print(f"  => P(all {len(QUOTATION)} present | genuine-469 model) = {math.exp(log_hit):.4g}")

    joint = math.exp(log_miss + log_hit)
    print(f"\nP(the exact observed 4-absent / 4-present split) = {joint:.4g}")

    # --- the anti-confound: is the absent set the SHORT set? -----------------
    mt = sum(len(s) for s, _ in TRANSLATED) / len(TRANSLATED)
    mq = sum(len(s) for s, _ in QUOTATION) / len(QUOTATION)
    print(f"\nmean length: translated/absent {mt:.2f}, quotation/present {mq:.2f}")
    print("the absent set is the SHORTER one -- length runs against the split, "
          "not for it")

    # --- how much corpus is there to work with on the NPC side? --------------
    n_npc = sum(len(s) for s, _ in TRANSLATED)
    print(f"\nNPC 'translated dialect' total size: {n_npc} digits "
          f"({len(TRANSLATED)} strings)")
    print(f"books: {c.n_digits} digits.  ratio 1:{c.n_digits / n_npc:.0f}")
    # SE of a unigram frequency estimate at n=26
    print(f"1-sigma error on any digit frequency at n={n_npc}: "
          f"+-{math.sqrt(0.1 * 0.9 / n_npc):.3f} (vs a 0.1 mean) -- i.e. the "
          f"NPC set cannot be attacked as a corpus at all")

    # --- digit composition, for the record ----------------------------------
    def freq(strings):
        s = "".join(strings)
        return {d: s.count(d) / len(s) for d in "0123456789"}, len(s)

    ft, nt = freq([s for s, _ in TRANSLATED])
    fq, nq = freq([s for s, _ in QUOTATION])
    fb, nb = freq(books)
    print("\ndigit  books   translated(n=%d)  quotation(n=%d)" % (nt, nq))
    for d in "0123456789":
        print(f"  {d}   {fb[d]:.4f}   {ft[d]:.4f}          {fq[d]:.4f}")
    print("\nzeros: books %d/%d = %.4f; translated set %d/%d; quotation set %d/%d"
          % ("".join(books).count("0"), nb, fb["0"],
             "".join(s for s, _ in TRANSLATED).count("0"), nt,
             "".join(s for s, _ in QUOTATION).count("0"), nq))
    p0 = fb["0"]
    print("P(no 0 in %d digits | book digit rate) = %.4f" % (nt, (1 - p0) ** nt))

    out = REPO / "experiments" / "verify_2026" / "out"
    out.mkdir(exist_ok=True)
    (out / "g1_dialect.json").write_text(json.dumps({
        "p_hit": tab,
        "P_all_translated_absent": math.exp(log_miss),
        "P_all_quotation_present": math.exp(log_hit),
        "P_joint": joint,
        "mean_len_translated": mt, "mean_len_quotation": mq,
        "npc_digits": n_npc, "book_digits": c.n_digits,
        "freq_books": fb, "freq_translated": ft, "freq_quotation": fq,
    }, indent=2))


if __name__ == "__main__":
    main()
