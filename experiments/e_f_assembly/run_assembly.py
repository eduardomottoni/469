"""Phase 1 driver: master_v1 plus the (contigs, length, edits) Pareto front."""
from __future__ import annotations

import json, random, sys, time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from assembler import (collapse_containment, build_edges, greedy_path, beam_path,
                       or_opt, order_score, ilp_path_cover, chosen_to_paths,
                       realise, edge_score)
from c469.corpus import load_books

REPO = Path(__file__).resolve().parents[2]
PEN = dict(edit_penalty=6, rot_penalty=25)


def _solution(n, E, paths, S):
    contigs, layouts = [], []
    for p in paths:
        c, lay = realise(p, S, E)
        contigs.append(c); layouts.append(lay)
    return dict(n_contigs=len(paths),
                total_len=sum(len(c) for c in contigs),
                contig_lens=sorted((len(c) for c in contigs), reverse=True),
                edits=sum(l["edits"] for lay in layouts for l in lay),
                rotations=sum(1 for lay in layouts for l in lay if l["rot"]),
                paths=paths, contigs=contigs, layouts=layouts)


def assemble(seqs, labels=None, min_ov=5, mode="edits", n_extra=4,
             beam_width=5000, restarts=200, time_limit=120, use_ilp=True,
             verbose=True):
    labels = labels or [f"B{i}" for i in range(len(seqs))]
    kept, dropped = collapse_containment(seqs, labels)
    S = [seqs[i] for i in kept]
    n = len(S)
    E = build_edges(S, min_ov=min_ov, allow_edits=(mode in ("edits", "rot")),
                    allow_rot=(mode == "rot"))
    if verbose:
        print(f"  nodes={n} (dropped {len(dropped)} contained) arcs={len(E)}",
              flush=True)
    # heuristic path cover: randomised greedy + or-opt restarts, then beam
    rng = random.Random(7)
    best = or_opt(greedy_path(n, E, **PEN), E, 20000, rng, **PEN)
    bs = order_score(best, E, **PEN)
    for _ in range(restarts):
        o = or_opt(greedy_path(n, E, rng=rng, noise=6.0, **PEN), E, 3000, rng, **PEN)
        if order_score(o, E, **PEN) > bs:
            best, bs = o, order_score(o, E, **PEN)
    bo = beam_path(n, E, width=beam_width, **PEN)
    if order_score(bo, E, **PEN) > bs:
        best, bs = bo, order_score(bo, E, **PEN)
    if verbose:
        print(f"  heuristic best score={bs:.0f}", flush=True)

    def heur_front(k):
        """Break the best order at its k-1 weakest joins (missing arc = -inf)."""
        cutkeys = sorted(range(n - 1),
                         key=lambda i: edge_score(E[(best[i], best[i + 1])], **PEN)
                         if (best[i], best[i + 1]) in E else -1e9)
        cuts = sorted(cutkeys[:k - 1])
        paths, prev = [], 0
        for cpos in cuts + [n - 1]:
            paths.append(best[prev:cpos + 1]); prev = cpos + 1
        return paths

    # smallest attainable contig count
    if use_ilp:
        st, chosen = ilp_path_cover(n, E, objective="count",
                                    time_limit=time_limit, **PEN)
        kmin = n - len(chosen) if chosen else n
    else:
        used = sum(1 for i in range(n - 1) if (best[i], best[i + 1]) in E)
        st, kmin = "heuristic", n - used
    if verbose:
        print(f"  min contigs ({st}) = {kmin}", flush=True)

    front = []
    for k in range(kmin, kmin + n_extra + 1):
        t = time.time()
        paths, src = None, "heuristic"
        if use_ilp:
            st, chosen = ilp_path_cover(n, E, k=k, time_limit=time_limit, **PEN)
            if chosen:
                paths, src = chosen_to_paths(n, chosen), "ILP:" + st
        if paths is None:
            paths = heur_front(k)
        sol = _solution(n, E, paths, S)
        sol.update(k=k, ilp_status=src, ilp_s=round(time.time() - t, 1),
                   score=sum(order_score(p, E, **PEN) for p in paths))
        front.append(sol)
        if verbose:
            print(f"  k={k:3d} {src:14s} len={sol['total_len']} "
                  f"edits={sol['edits']} rot={sol['rotations']} "
                  f"({sol['ilp_s']}s)", flush=True)

    return dict(n_nodes=n, kept=kept, dropped=dropped, arcs=len(E),
                kmin=kmin, front=front, S=S, heur_score=bs)


def build_provenance(contigs, layouts, res, seqs, labels, tag):
    kept, dropped = res["kept"], res["dropped"]
    master = "".join(contigs)
    cover = [0] * len(master)
    entries, host_of, junctions = [], {}, []
    base = 0
    for ci, (lay, contig) in enumerate(zip(layouts, contigs)):
        if ci:
            junctions.append(base)
        for l in lay:
            gi = kept[l["node"]]
            st = base + l["start"]
            e = dict(book=labels[gi], index=gi, start=st, length=l["length"],
                     edits=l["edits"], rot=l["rot"], ov_in=l["ov_in"], contig=ci)
            entries.append(e); host_of[gi] = e
            for p in range(st, min(len(master), st + l["length"])):
                cover[p] += 1
        base += len(contig)
    for di, (hi, off) in dropped.items():
        h = host_of.get(hi)
        if h is None:
            continue
        st = h["start"] + off
        entries.append(dict(book=labels[di], index=di, start=st,
                            length=len(seqs[di]), edits=0, rot=0,
                            contained_in=labels[hi], contig=h["contig"]))
        for p in range(st, min(len(master), st + len(seqs[di]))):
            cover[p] += 1
    single = [i for i, v in enumerate(cover) if v <= 1]
    return dict(assembly=tag, master_length=len(master), n_books=len(seqs),
                n_contigs=len(contigs),
                contig_lengths=[len(c) for c in contigs],
                contig_start_offsets=[0] + junctions,
                placements=sorted(entries, key=lambda e: e["start"]),
                coverage=cover, single_coverage_positions=single,
                n_single_coverage=len(single))


def verify(master, prov, seqs, labels, max_edits=1):
    """Assert every book is recoverable from the master under the budget."""
    from assembler import _edit_le
    by = {e["book"]: e for e in prov["placements"]}
    bad = []
    for i, b in enumerate(seqs):
        e = by.get(labels[i])
        if e is None:
            bad.append((labels[i], "unplaced")); continue
        cand = b
        if e.get("rot"):
            r = e["rot"]; cand = b[r:] + b[:r]
        ok = False
        for d in (0, 1, -1, 2, -2):
            seg = master[e["start"]:e["start"] + len(cand) + d]
            if seg == cand or _edit_le(seg, cand, max_edits) is not None:
                ok = True; break
        if not ok:
            bad.append((labels[i], "mismatch", e["start"]))
    return bad


def main():
    c = load_books(with_kharos=True)
    seqs, labels = list(c.books), list(c.labels)
    print(f"corpus: {len(seqs)} books, {sum(map(len,seqs))} digits ({c.provenance})")
    out = {}
    configs = [(5, "exact", True), (5, "edits", True), (5, "rot", True),
               (20, "edits", True), (1, "exact", False)]
    for min_ov, mode, use_ilp in configs:
        tag = f"minov{min_ov}_{mode}"
        print(f"[{tag}]", flush=True)
        out[tag] = assemble(seqs, labels, min_ov=min_ov, mode=mode,
                            use_ilp=use_ilp, n_extra=(0 if not use_ilp else 4))

    for tag, fname in (("minov5_edits", "master_v1"),
                       ("minov1_exact", "master_permissive_v1")):
        res = out[tag]
        sol = min(res["front"], key=lambda f: f["total_len"])
        master = "".join(sol["contigs"])
        prov = build_provenance(sol["contigs"], sol["layouts"], res, seqs, labels,
                                tag)
        bad = verify(master, prov, seqs, labels)
        print(f"{fname}: {len(master)} digits, {sol['n_contigs']} contigs, "
              f"{sol['edits']} edits, {sol['rotations']} rotations; "
              f"unrecoverable books: {bad}", flush=True)
        prov["unrecoverable"] = bad
        (REPO / "data" / f"{fname}.txt").write_text(master + "\n")
        (REPO / "data" / f"{fname.replace('master','master')}_provenance.json"
         if False else REPO / "data" / (
             "master_provenance.json" if fname == "master_v1"
             else "master_permissive_provenance.json")).write_text(json.dumps(prov))
        if fname == "master_v1":
            assert not bad, f"books not recoverable from master: {bad}"

    summary = {t: dict(n_nodes=r["n_nodes"], arcs=r["arcs"], kmin=r["kmin"],
                       heur_score=r["heur_score"],
                       front=[{k: v for k, v in f.items()
                               if k not in ("contigs", "layouts", "paths")}
                              for f in r["front"]])
               for t, r in out.items()}
    (Path(__file__).parent / "pareto.json").write_text(json.dumps(summary, indent=1))
    print("wrote pareto.json")


if __name__ == "__main__":
    main()
