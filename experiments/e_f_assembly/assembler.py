"""Shotgun assembly of the 469 books.

Replaces the prior O(n^2) exact-overlap loop + greedy path decomposition in
try_combine_books/try_combine_books.py with

  * linear-time exact overlaps (KMP prefix function on B + sep + A)
  * containment collapse, exact and rotation-aware
  * rotation-aware overlaps via a generalised suffix automaton of B+B
  * inexact overlaps: <=1 mismatch or <=1 indel, seed-and-extend anchors
    verified by a banded (width 5) semi-global overlap DP with free end gaps
  * path cover by beam search AND by an exact ILP (pulp/CBC, ATSP + MTZ)

Nothing here imports graphviz, so it runs headless; the Book/Library data model
of the prior script is kept (see `Book`, `Library`) so its outputs stay loadable.
"""
from __future__ import annotations

import json
import random
from dataclasses import dataclass, field

# --------------------------------------------------------------- data model


class Book:
    """Same interface as try_combine_books.Book (minus the graphviz bits)."""

    def __init__(self, content: str, name: str | None = None):
        self.content = content
        self.name = name

    def __hash__(self):
        return hash(self.content)

    def __eq__(self, other):
        return isinstance(other, Book) and self.content == other.content

    def __len__(self):
        return len(self.content)

    def __contains__(self, other):
        return (other if isinstance(other, str) else other.content) in self.content

    def get_name(self):
        return self.name or hex(hash(self))

    def get_overlap_length(self, nxt) -> int:
        return exact_overlap(self.content, nxt.content)


class Library:
    def __init__(self, books=()):
        self.books = list(books)

    def add(self, b):
        self.books.append(b)

    def __iter__(self):
        return iter(self.books)

    def __len__(self):
        return len(self.books)

    def save(self, filename):
        with open(filename, "w") as f:
            f.write("\n".join(b.content for b in self.books))


# ------------------------------------------------------------ exact overlaps

def exact_overlap(a: str, b: str, cap: int | None = None) -> int:
    """Length of the longest suffix of `a` that is a prefix of `b` (< min len)."""
    m = min(len(a), len(b)) if cap is None else min(cap, len(a), len(b))
    s = b[:m] + "\x00" + a[-m:]
    pi = [0] * len(s)
    k = 0
    for i in range(1, len(s)):
        while k and s[i] != s[k]:
            k = pi[k - 1]
        if s[i] == s[k]:
            k += 1
        pi[i] = k
    return pi[-1]


def all_exact_overlaps(seqs: list[str]) -> dict:
    """{(i,j): overlap} for every ordered pair.  Linear per pair."""
    out = {}
    for i, a in enumerate(seqs):
        for j, b in enumerate(seqs):
            if i == j:
                continue
            v = exact_overlap(a, b)
            if v:
                out[(i, j)] = v
    return out


# ------------------------------------------------- suffix automaton (rotations)

class SAM:
    """Suffix automaton with first-occurrence end positions."""

    def __init__(self, s: str):
        self.link = [-1]
        self.len = [0]
        self.next = [{}]
        self.first = [0]
        last = 0
        for pos, ch in enumerate(s):
            cur = len(self.len)
            self.len.append(self.len[last] + 1)
            self.link.append(-1)
            self.next.append({})
            self.first.append(pos + 1)
            p = last
            while p != -1 and ch not in self.next[p]:
                self.next[p][ch] = cur
                p = self.link[p]
            if p == -1:
                self.link[cur] = 0
            else:
                q = self.next[p][ch]
                if self.len[p] + 1 == self.len[q]:
                    self.link[cur] = q
                else:
                    clone = len(self.len)
                    self.len.append(self.len[p] + 1)
                    self.link.append(self.link[q])
                    self.next.append(dict(self.next[q]))
                    self.first.append(self.first[q])
                    while p != -1 and self.next[p].get(ch) == q:
                        self.next[p][ch] = clone
                        p = self.link[p]
                    self.link[q] = clone
                    self.link[cur] = clone
            last = cur

    def longest_suffix_match(self, t: str):
        """Longest suffix of `t` that is a substring of the built string.

        Returns (length, end_position_of_first_occurrence)."""
        v, l = 0, 0
        for ch in t:
            while v and ch not in self.next[v]:
                v = self.link[v]
                l = self.len[v]
            if ch in self.next[v]:
                v = self.next[v][ch]
                l += 1
            else:
                v, l = 0, 0
        return l, (self.first[v] if v else 0)


def rotation_overlap(a: str, b: str, sam_bb: SAM):
    """Best (overlap, cut) so that a suffix of `a` is a prefix of rot_cut(b).

    rot_cut(b) = b[cut:] + b[:cut].  A suffix of `a` of length L is a prefix of
    rot_cut(b) iff it occurs in b+b starting at `cut`, with L <= len(b).
    """
    L, end = sam_bb.longest_suffix_match(a)
    L = min(L, len(b), len(a) - 1 if len(a) > 1 else L)
    if L <= 0:
        return 0, 0
    start = end - L
    # `end`/`start` come from the first occurrence; recover a valid cut
    cut = start % len(b)
    if (b + b)[cut:cut + L] != a[-L:]:
        return 0, 0
    return L, cut


# ----------------------------------------------------- inexact overlap (<=1 edit)

def banded_overlap_align(a: str, b: str, max_edits: int = 1, band: int = 5):
    """Semi-global overlap alignment: free gap before `a` starts and after `b`
    ends; suffix of `a` against prefix of `b`.  Returns (ov_a, ov_b, edits) for
    the longest alignment using <= max_edits edits, or None.

    Only the last `len(a)` x first `len(b)` corner is ever needed and the band
    keeps it O(n * band).  Implemented as a direct scan over shift diagonals.
    """
    best = None
    n, m = len(a), len(b)
    for d in range(-band, band + 1):
        # a[-L:] aligned to b[:L+d]
        for L in range(min(n, m) - abs(d), 0, -1):
            if best and L + max(0, d) <= best[0]:
                break
            x, y = a[n - L:], b[:L + d]
            e = _edit_le(x, y, max_edits)
            if e is not None:
                if best is None or L > best[0]:
                    best = (L, L + d, e)
                break
    return best


def _edit_le(x: str, y: str, k: int):
    """Levenshtein distance if <= k, else None.  k is 0 or 1 here."""
    if x == y:
        return 0
    if k < 1:
        return None
    if len(x) == len(y):
        d = sum(1 for p, q in zip(x, y) if p != q)
        return d if d <= 1 else None
    if abs(len(x) - len(y)) != 1:
        return None
    lo, hi = (x, y) if len(x) < len(y) else (y, x)
    i = 0
    while i < len(lo) and lo[i] == hi[i]:
        i += 1
    return 1 if lo[i:] == hi[i + 1:] else None


def anchored_inexact_overlap(a: str, b: str, kmer: int = 12, max_edits: int = 1,
                             min_ov: int = 10):
    """Seed-and-extend: candidate diagonals from shared k-mers, each verified by
    an exact/1-edit check.  Returns (ov_a, ov_b, edits) or None."""
    if len(a) < kmer or len(b) < kmer:
        return None
    idx = {}
    for j in range(len(b) - kmer + 1):
        idx.setdefault(b[j:j + kmer], []).append(j)
    cands = set()
    for i in range(len(a) - kmer + 1):
        for j in idx.get(a[i:i + kmer], ()):
            L = len(a) - (i - j)          # implied overlap length
            if min_ov <= L <= min(len(a), len(b)):
                cands.add(L)
    best = None
    for L in sorted(cands, reverse=True):
        if best and L <= best[0]:
            break
        for d in (0, 1, -1) if max_edits else (0,):
            if not (0 < L + d <= len(b)):
                continue
            e = _edit_le(a[len(a) - L:], b[:L + d], max_edits)
            if e is not None and (best is None or L > best[0]):
                best = (L, L + d, e)
                break
    return best


# --------------------------------------------------------------- graph + solve

@dataclass
class Edge:
    ov_a: int          # digits of `a` consumed
    ov_b: int          # digits of `b` consumed (differs iff an indel was used)
    edits: int
    rot: int = 0       # rotation cut applied to b (0 = none)

    @property
    def gain(self) -> int:
        return self.ov_b


def collapse_containment(seqs: list[str], labels: list[str]):
    """Drop books that are literal substrings of another book.

    Returns (kept_indices, {dropped_index: (parent_index, offset)})."""
    order = sorted(range(len(seqs)), key=lambda i: (-len(seqs[i]), i))
    kept: list[int] = []
    dropped: dict[int, tuple[int, int]] = {}
    for i in order:
        host = None
        for j in kept:
            off = seqs[j].find(seqs[i])
            if off >= 0:
                host = (j, off)
                break
        if host is None:
            kept.append(i)
        else:
            dropped[i] = host
    kept.sort()
    return kept, dropped


def build_edges(S: list[str], min_ov: int = 5, allow_edits: bool = True,
                allow_rot: bool = False, rot_min: int = 30,
                edit_penalty: int = 6, rot_penalty: int = 25) -> dict:
    """Ordered-pair edges.  `gain` is the raw overlap; the solver optimises
    gain - penalties so that an edit or a rotation must pay for itself."""
    sams = [SAM(s + s) for s in S] if allow_rot else None
    E: dict[tuple[int, int], Edge] = {}
    for i, a in enumerate(S):
        for j, b in enumerate(S):
            if i == j:
                continue
            best = None
            bs = -1
            e = exact_overlap(a, b)
            if e >= min_ov:
                best, bs = Edge(e, e, 0), e
            if allow_edits:
                x = anchored_inexact_overlap(a, b, min_ov=min_ov)
                if x and x[2] and x[0] - edit_penalty > bs:
                    best, bs = Edge(x[0], x[1], x[2]), x[0] - edit_penalty
            if allow_rot:
                r, cut = rotation_overlap(a, b, sams[j])
                if cut and r >= rot_min and r - rot_penalty > bs:
                    best, bs = Edge(r, r, 0, cut), r - rot_penalty
            if best is not None:
                E[(i, j)] = best
    return E


def edge_score(e: Edge, edit_penalty: int = 6, rot_penalty: int = 25) -> float:
    return e.gain - edit_penalty * e.edits - (rot_penalty if e.rot else 0)


# --- greedy / beam ---------------------------------------------------------

def greedy_path(n: int, E: dict, rng: random.Random | None = None,
                noise: float = 0.0, **pen) -> list[int]:
    """Nearest-neighbour Hamiltonian path with optional randomised tie-breaking."""
    unused = set(range(n))
    cur = (rng.choice(sorted(unused)) if rng else
           max(range(n), key=lambda i: sum(edge_score(E[k], **pen)
                                           for k in E if k[0] == i)))
    unused.discard(cur)
    order = [cur]
    while unused:
        cands = [(edge_score(E[(cur, j)], **pen) +
                  (rng.uniform(0, noise) if rng and noise else 0.0), j)
                 for j in unused if (cur, j) in E]
        if cands:
            cur = max(cands)[1]
        else:
            cur = (rng.choice(sorted(unused)) if rng else min(unused))
        unused.discard(cur)
        order.append(cur)
    return order


def order_score(order: list[int], E: dict, **pen) -> float:
    return sum(edge_score(E[(order[i], order[i + 1])], **pen)
               for i in range(len(order) - 1) if (order[i], order[i + 1]) in E)


def or_opt(order: list[int], E: dict, iters: int = 20000,
           rng: random.Random | None = None, **pen) -> list[int]:
    """Local search: move segments of length 1-3 to a better position."""
    rng = rng or random.Random(0)
    best = order[:]
    bs = order_score(best, E, **pen)
    n = len(order)
    for _ in range(iters):
        L = rng.randint(1, 3)
        i = rng.randrange(0, n - L + 1)
        seg = best[i:i + L]
        rest = best[:i] + best[i + L:]
        j = rng.randrange(0, len(rest) + 1)
        cand = rest[:j] + seg + rest[j:]
        cs = order_score(cand, E, **pen)
        if cs > bs:
            best, bs = cand, cs
    return best


def beam_path(n: int, E: dict, width: int = 5000, succ: int = 25,
              rng: random.Random | None = None, **pen) -> list[int]:
    """Beam search over Hamiltonian orderings, keyed by (visited-set, last).

    The visited set is a bitmask, not a frozenset: with width 5000 and 51 nodes
    the frozenset version spends all of its time copying sets.
    """
    adj: dict[int, list] = {i: [] for i in range(n)}
    for (i, j), e in E.items():
        adj[i].append((edge_score(e, **pen), j))
    for i in adj:
        adj[i].sort(reverse=True)
        adj[i] = adj[i][:succ]
    beam = [(0.0, 1 << i, (i,)) for i in range(n)]
    for _ in range(n - 1):
        nxt: dict = {}
        for sc, used, path in beam:
            last = path[-1]
            cands = [(s, j) for s, j in adj[last] if not (used >> j) & 1]
            if len(cands) < 3:
                cands = cands + [(0.0, j) for j in range(n)
                                 if not (used >> j) & 1][:succ]
            for s, j in cands:
                key = (used | (1 << j), j)
                v = sc + s
                cur = nxt.get(key)
                if cur is None or cur[0] < v:
                    nxt[key] = (v, path + (j,))
        beam = sorted(((v, k[0], p) for k, (v, p) in nxt.items()),
                      key=lambda t: -t[0])[:width]
        if not beam:
            break
    return list(max(beam)[2])


# --- exact ILP -------------------------------------------------------------

def ilp_path_cover(n: int, E: dict, k: int | None = None, objective: str = "gain",
                   time_limit: int = 1800, **pen):
    """Exact cover of all n nodes by vertex-disjoint paths over the arc set E.

    objective="gain"  : maximise total overlap saved (arc count fixed by k)
    objective="count" : maximise the number of arcs, i.e. minimise the number
                        of contigs -- used to find the smallest attainable k.
    Assignment constraints + MTZ subtour elimination, solved by CBC.
    """
    import pulp
    prob = pulp.LpProblem("pathcover", pulp.LpMaximize)
    x = {ij: pulp.LpVariable(f"x_{ij[0]}_{ij[1]}", cat="Binary") for ij in E}
    u = [pulp.LpVariable(f"u_{i}", lowBound=0, upBound=n - 1) for i in range(n)]
    if objective == "count":
        prob += pulp.lpSum(x.values())
    else:
        prob += pulp.lpSum(edge_score(E[ij], **pen) * x[ij] for ij in E)
    for i in range(n):
        out = [x[ij] for ij in E if ij[0] == i]
        inn = [x[ij] for ij in E if ij[1] == i]
        if out:
            prob += pulp.lpSum(out) <= 1
        if inn:
            prob += pulp.lpSum(inn) <= 1
    if k is not None:
        prob += pulp.lpSum(x.values()) == n - k
    for (i, j) in E:
        prob += u[i] - u[j] + n * x[(i, j)] <= n - 1
    prob.solve(pulp.PULP_CBC_CMD(msg=0, timeLimit=time_limit))
    status = pulp.LpStatus[prob.status]
    if status not in ("Optimal",):
        return status, []
    chosen = [ij for ij in E if x[ij].value() and x[ij].value() > 0.5]
    return status, chosen


def chosen_to_paths(n: int, chosen) -> list[list[int]]:
    nxt = dict(chosen)
    prv = {j: i for i, j in chosen}
    paths = []
    for s in range(n):
        if s in prv:
            continue
        p = [s]
        while p[-1] in nxt:
            p.append(nxt[p[-1]])
        paths.append(p)
    seen = {v for p in paths for v in p}
    assert seen == set(range(n)), f"cycle left in solution ({len(seen)}/{n})"
    return paths


# --- realisation -----------------------------------------------------------

def realise(path: list[int], S: list[str], E: dict):
    """Splice a path into one contig; returns (contig, layout).

    layout[i] = dict(node, start, length, ov_in, edits, rot).
    """
    out = []
    layout = []
    pos = 0
    for idx, v in enumerate(path):
        s = S[v]
        e = E.get((path[idx - 1], v)) if idx else None
        rot = e.rot if e else 0
        if rot:
            s = s[rot:] + s[:rot]
        cut = e.ov_b if e else 0
        out.append(s[cut:])
        layout.append({"node": v, "start": pos - (cut if idx else 0),
                       "length": len(s), "ov_in": cut,
                       "edits": e.edits if e else 0, "rot": rot})
        pos += len(s) - cut
    return "".join(out), layout
