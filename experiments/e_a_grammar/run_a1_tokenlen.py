"""A1 — the pre-registered token-length test (see PREREGISTRATION.md).

Prediction P1: corpus-weighted mean token length in [1.5, 1.7]
Prediction P2: 8-10 length-1 tokens in the induced vocabulary
Arbiter: mdl_unigram (MDL-argmin vocabulary).  BPE/Re-Pair/LZ78 reported only.
"""
import json, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
sys.path.insert(0, str(Path(__file__).parent))
import inducers as I
from c469.corpus import load_books, load_contigs, dedup_core

OUT = Path(__file__).parent / "a1_tokenlen.json"


def streams():
    s = {}
    s["dedup_core"] = dedup_core(load_books())
    s["contigs"] = load_contigs()
    p = Path("data/master_v1.txt")
    if p.exists():
        from c469.corpus import Corpus
        txt = [x for x in p.read_text().split() if x.strip()]
        s["master_v1"] = Corpus(tuple("".join(c for c in t if c.isdigit()) for t in txt),
                                provenance="data/master_v1.txt")
    return s


def main():
    res = {}
    for sname, C in streams().items():
        books = list(C.books)
        res[sname] = {"provenance": C.provenance, "n_books": len(books),
                      "n_digits": sum(map(len, books)), "inducers": {}}
        curve = []
        t0 = time.time()
        ind = I.mdl_unigram(books, verbose=True, curve=curve)
        prof = ind.length_profile()
        res[sname]["mdl_curve"] = curve
        res[sname]["inducers"]["mdl_unigram"] = {
            "mdl": ind.mdl, "profile": prof, "runtime_s": time.time() - t0,
            "vocab_len1": sorted(t for t in ind.used_vocab if len(t) == 1),
            "top20": [t for t, _ in __import__("collections").Counter(ind.tokens).most_common(20)],
        }
        print(f"[{sname}] MDL-argmin V={prof['V_used']} meanlen="
              f"{prof['mean_token_len_weighted']:.3f} len1types={prof['n_len1_types']}")
        for V in (50, 100, 200, 400, 1000):
            b = I.bpe(books, V)
            res[sname]["inducers"][f"bpe{V}"] = {"mdl": b.mdl, "profile": b.length_profile()}
        for f, nm in ((I.repair, "repair"), (I.lz78, "lz78")):
            x = f(books)
            res[sname]["inducers"][nm] = {"mdl": x.mdl, "profile": x.length_profile()}
    OUT.write_text(json.dumps(res, indent=2))
    print("wrote", OUT)

    print("\n=== PRE-REGISTERED VERDICT (P1: mean in [1.5,1.7]; P2: 8-10 len-1 types) ===")
    for sname, r in res.items():
        p = r["inducers"]["mdl_unigram"]["profile"]
        p1 = 1.5 <= p["mean_token_len_weighted"] <= 1.7
        p2 = 8 <= p["n_len1_types"] <= 10
        print(f"{sname:12s} mean={p['mean_token_len_weighted']:.3f} P1={'PASS' if p1 else 'FAIL'}"
              f"  len1types={p['n_len1_types']} P2={'PASS' if p2 else 'FAIL'}"
              f"  frac_occ_len12={p['frac_occ_len12']:.3f}  V={p['V_used']}")


if __name__ == "__main__":
    main()
