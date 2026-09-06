"""Fast Lmax (longest match against the prefix) via an online suffix automaton,
so the residue extraction of residue.py can be run on hundreds of surrogates.

Lmax[p] = length of the longest prefix of s[p:] that occurs in s[:p], capped at
`maxlen`.  Verified digit-for-digit against the binary-search implementation in
c469.stats over the real master and corpus (see `selfcheck()`).
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))


class SAM:
    __slots__ = ("nxt", "link", "length", "last")

    def __init__(self):
        self.nxt = [{}]
        self.link = [-1]
        self.length = [0]
        self.last = 0

    def extend(self, ch):
        nxt, link, length = self.nxt, self.link, self.length
        cur = len(length)
        length.append(length[self.last] + 1); link.append(-1); nxt.append({})
        p = self.last
        while p != -1 and ch not in nxt[p]:
            nxt[p][ch] = cur
            p = link[p]
        if p == -1:
            link[cur] = 0
        else:
            q = nxt[p][ch]
            if length[p] + 1 == length[q]:
                link[cur] = q
            else:
                clone = len(length)
                length.append(length[p] + 1)
                nxt.append(dict(nxt[q]))
                link.append(link[q])
                while p != -1 and nxt[p].get(ch) == q:
                    nxt[p][ch] = clone
                    p = link[p]
                link[q] = clone
                link[cur] = clone
        self.last = cur


def max_match_len(s: str, maxlen: int = 400) -> list[int]:
    n = len(s)
    out = [0] * n
    sam = SAM()
    nxt = sam.nxt
    for p in range(n):
        if p:
            node, L = 0, 0
            lim = min(maxlen, n - p)
            while L < lim:
                t = nxt[node].get(s[p + L])
                if t is None:
                    break
                node = t
                L += 1
            out[p] = L
        sam.extend(s[p])
        nxt = sam.nxt
    return out


def selfcheck():
    from c469.stats import _longest_match
    from c469.corpus import load_books
    master = (REPO / "data" / "master_v1.txt").read_text().strip()
    concat = "".join(load_books(with_kharos=False).books)
    for name, s in (("master", master), ("concat", concat)):
        fast = max_match_len(s)
        slow = [_longest_match(s[:p], s, p)[0] for p in range(len(s))]
        assert fast == slow, name
        print(f"ok  fastlz matches c469.stats on {name} ({len(s)} digits)")


if __name__ == "__main__":
    selfcheck()
