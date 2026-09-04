"""Null control for Phase 1: does the assembler collapse surrogates too?

If a copy-paste surrogate assembles as well as the real corpus, then assembly
proves nothing about meaning -- it is only dedup.  Same code path on real and
surrogate, no ILP (so the cost is bounded and identical), heuristic path cover.
"""
from __future__ import annotations

import sys, json, random
from multiprocessing import Pool
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from assembler import (collapse_containment, build_edges, greedy_path, or_opt,
                       order_score)
from c469.corpus import load_books
from c469 import surrogate as U
from c469.harness import Experiment, Result, summarize_null

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
    for _ in range(3):
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


def _one(args):
    fam, books, seed = args
    s = fam.generate(list(books), seed)
    return assemble_stats(s), assemble_stats(s, mode="rot")


def main(n=100):
    """One surrogate -> one plain assembly + one rotation-mode assembly, and
    every statistic read off the same run (so the null draws are shared and the
    cost is 2 assemblies per surrogate rather than 6)."""
    c = load_books(with_kharos=True)
    books = list(c.books)
    real = assemble_stats(books)
    real_rot = assemble_stats(books, mode="rot")
    print("real:", json.dumps(real), flush=True)
    print("real(rot):", json.dumps(real_rot), flush=True)

    stats = {"assembly_compression": ("greater", lambda a, r: a["compression"]),
             "n_contigs": ("less", lambda a, r: float(a["n_contigs"])),
             "longest_overlap": ("greater", lambda a, r: float(a["max_overlap"])),
             "rotations_invoked": ("greater", lambda a, r: float(r["rotations"]))}
    realvals = {k: f(real, real_rot) for k, (d, f) in stats.items()}
    nulls = {k: {} for k in stats}
    for fam in U.DEFAULT_FAMILIES:
        acc = {k: [] for k in stats}
        with Pool(4) as pool:
            for a, r in pool.imap_unordered(
                    _one, [(fam, books, 100003 * (i + 1) + 7) for i in range(n)],
                    chunksize=2):
                for k, (d, f) in stats.items():
                    acc[k].append(f(a, r))
        for k in stats:
            nulls[k][fam.name] = acc[k]
        print("done", fam.name, flush=True)

    for k, (direction, _) in stats.items():
        res = Result(experiment="e_f_assembly", statistic=k,
                     real_value=float(realvals[k]), direction=direction,
                     corpus_provenance=c.provenance, seed=1,
                     nulls=[summarize_null(f, realvals[k], nulls[k][f], direction)
                            for f in nulls[k]],
                     extra=dict(real=real, real_rot=real_rot, n_nulls=n))
        print(k, "real=%.4g" % res.real_value,
              {x.family: (round(x.mean, 3), round(x.p, 4)) for x in res.nulls},
              res.verdict, flush=True)
        res.save()


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 100)
