"""Null control for Phase 1: does the assembler collapse surrogates too?

If a copy-paste surrogate assembles as well as the real corpus, then assembly
proves nothing about meaning -- it is only dedup.  Same code path on real and
surrogate, no ILP (so the cost is bounded and identical), heuristic path cover.
"""
from __future__ import annotations

import sys, json, random
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from assembler import (collapse_containment, build_edges, greedy_path, or_opt,
                       order_score)
from c469.corpus import load_books
from c469 import surrogate as U
from c469.harness import Experiment, Result

PEN = dict(edit_penalty=6, rot_penalty=25)


def assemble_stats(books, min_ov=5, mode="edits"):
    labels = [f"B{i}" for i in range(len(books))]
    kept, dropped = collapse_containment(list(books), labels)
    S = [books[i] for i in kept]
    n = len(S)
    E = build_edges(S, min_ov=min_ov, allow_edits=(mode in ("edits", "rot")),
                    allow_rot=(mode == "rot"))
    rng = random.Random(11)
    best = or_opt(greedy_path(n, E, **PEN), E, 8000, rng, **PEN)
    for _ in range(20):
        o = or_opt(greedy_path(n, E, rng=rng, noise=6.0, **PEN), E, 2000, rng, **PEN)
        if order_score(o, E, **PEN) > order_score(best, E, **PEN):
            best = o
    used = [(best[i], best[i + 1]) for i in range(n - 1)
            if (best[i], best[i + 1]) in E]
    saved = sum(E[a].ov_b for a in used)
    tot = sum(map(len, books))
    kept_len = sum(map(len, S))
    return dict(n_nodes=n, contained=len(dropped), arcs=len(E),
                n_contigs=n - len(used), master_len=kept_len - saved,
                compression=1.0 - (kept_len - saved) / tot,
                rotations=sum(1 for a in used if E[a].rot),
                edits=sum(E[a].edits for a in used),
                max_overlap=max((E[a].ov_b for a in E), default=0))


class AssemblyCompression(Experiment):
    NAME = "e_f_assembly"
    STATISTIC = "assembly_compression"
    DIRECTION = "greater"
    NULL_FAMILIES = U.DEFAULT_FAMILIES

    def compute(self, books):
        return assemble_stats(books)["compression"]


class AssemblyContigs(AssemblyCompression):
    STATISTIC = "n_contigs"
    DIRECTION = "less"

    def compute(self, books):
        return float(assemble_stats(books)["n_contigs"])


class RotationsInvoked(AssemblyCompression):
    STATISTIC = "rotations_invoked"
    DIRECTION = "greater"

    def compute(self, books):
        return float(assemble_stats(books, mode="rot")["rotations"])


def main(n=100):
    c = load_books(with_kharos=True)
    books = list(c.books)
    print("real:", json.dumps(assemble_stats(books)), flush=True)
    print("real(rot):", json.dumps(assemble_stats(books, mode="rot")), flush=True)
    for E in (AssemblyCompression(), AssemblyContigs(), RotationsInvoked()):
        r = E.run(books, provenance=c.provenance, n_nulls=n, seed=1)
        print(r.statistic, "real=%.4g" % r.real_value,
              {x.family: (round(x.mean, 4), round(x.p, 4)) for x in r.nulls},
              r.verdict, flush=True)
        r.save()


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 100)
