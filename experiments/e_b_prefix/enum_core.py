"""Numba kernels for the family-B exhaustive prefix-code enumeration.

A *structure* is: a set S1 of single-digit codewords (bitmask over 0..9); every
digit not in S1 is a length-1 prefix; for each prefix p, T[p][d] says whether
`pd` is itself a prefix (expanded to ten length-3 codewords) rather than a
codeword.  Codeword length is capped at 3, so the structure is fully specified
by (S1, T) and the parse of any string is forced and unique.

Codebook size = |S1| + 10*k + 9*sum|T_p|, where k = 10 - |S1|.

Parse success is strongly confounded with mean codeword length -- a code whose
codewords are nearly all one digit long lands on a book's final boundary almost
always.  So every kernel here reports the mean codeword length alongside the
book-parse count, and all downstream scoring is done *within* length bands.
"""
from __future__ import annotations

import numpy as np
from numba import njit

MAXHIST = 1110      # 10 length-1 + 100 length-2 + 1000 length-3 symbol ids
NBIN = 120          # mean-codeword-length bins
BIN0, BINW = 1.0, 0.02


@njit(cache=True, inline="always")
def _walk(flat, st, en, s1mask, T):
    """(ok, ntok, toklen) for one book.  A dangling remainder still contributes
    its digits so that mean codeword length is defined for every structure."""
    i = st
    ntok = 0
    toklen = 0
    ok = True
    while i < en:
        d0 = flat[i]
        if (s1mask >> d0) & 1:
            L = 1
        elif i + 1 >= en:
            ok = False
            L = 1
        elif T[d0 * 10 + flat[i + 1]] == 0:
            L = 2
        elif i + 2 >= en:
            ok = False
            L = 2
        else:
            L = 3
        i += L
        ntok += 1
        toklen += L
    return ok, ntok, toklen


@njit(cache=True)
def eval_structure(flat, offs, s1mask, T):
    """(n_books_parsed, tokens_over_all_books, digits_over_all_books)."""
    nb = offs.shape[0] - 1
    parsed = 0
    ntok = 0
    toklen = 0
    for b in range(nb):
        ok, a, c = _walk(flat, offs[b], offs[b + 1], s1mask, T)
        parsed += ok
        ntok += a
        toklen += c
    return parsed, ntok, toklen


@njit(cache=True, inline="always")
def _eval_full(flat, offs, s1mask, T, seen):
    """(parsed, ntok, toklen, V) where V is the number of DISTINCT codewords the
    forced parse actually uses.

    V, not the nominal codebook size, is the alphabet a homophonic/letter
    reading has to work with: a codeword that never occurs can be deleted from
    the codebook for free, and the code stays prefix-free (merely incomplete).
    That deletion is exactly hypothesis (i) for the missing bigram `07`.
    """
    for w in range(18):
        seen[w] = np.uint64(0)
    nb = offs.shape[0] - 1
    parsed = 0
    ntok = 0
    toklen = 0
    for b in range(nb):
        st = offs[b]
        en = offs[b + 1]
        i = st
        ok = True
        while i < en:
            d0 = flat[i]
            if (s1mask >> d0) & 1:
                sid = d0
                L = 1
            elif i + 1 >= en:
                ok = False
                break
            elif T[d0 * 10 + flat[i + 1]] == 0:
                sid = 10 + 10 * d0 + flat[i + 1]
                L = 2
            elif i + 2 >= en:
                ok = False
                break
            else:
                sid = 110 + 100 * d0 + 10 * flat[i + 1] + flat[i + 2]
                L = 3
            seen[sid >> 6] |= np.uint64(1) << np.uint64(sid & 63)
            i += L
            ntok += 1
            toklen += L
        if ok:
            parsed += 1
        else:
            # count the dangling remainder's digits so mean length stays defined
            ntok += 1
            toklen += en - i
    V = 0
    for w in range(18):
        x = seen[w]
        while x:
            x &= x - np.uint64(1)
            V += 1
    return parsed, ntok, toklen, V


@njit(cache=True)
def hist_structure(flat, offs, s1mask, T, hist):
    """Symbol histogram over all books (dangling remainders dropped).  Ids:
    len-1 -> d0; len-2 -> 10+10*d0+d1; len-3 -> 110+100*d0+10*d1+d2."""
    nb = offs.shape[0] - 1
    for b in range(nb):
        i = offs[b]
        en = offs[b + 1]
        while i < en:
            d0 = flat[i]
            if (s1mask >> d0) & 1:
                hist[d0] += 1
                i += 1
            elif i + 1 >= en:
                break
            elif T[d0 * 10 + flat[i + 1]] == 0:
                hist[10 + 10 * d0 + flat[i + 1]] += 1
                i += 2
            elif i + 2 >= en:
                break
            else:
                hist[110 + 100 * d0 + 10 * flat[i + 1] + flat[i + 2]] += 1
                i += 3
    return hist


@njit(cache=True)
def enumerate_s1(flat, offs, s1mask, prefixes, tmax, h2, best, vlo, vhi):
    """Exhaustive enumeration of every T with sum|T_p| <= tmax for one S1.

    Fills `h2[n_books_parsed, length_bin]`, and per length bin keeps the two
    best-parsing structures in `best[bin, slot, :] = (parsed, tcode, ntok,
    toklen, V)`: slot 0 unconstrained, slot 1 restricted to structures whose
    *effective* alphabet size V lies in [vlo, vhi] (the letter-code window).
    """
    k = prefixes.shape[0]
    nslots = 10 * k
    T = np.zeros(100, dtype=np.uint8)
    seen = np.zeros(18, dtype=np.uint64)
    idx = np.zeros(tmax + 2, dtype=np.int64)
    total = 0
    for t in range(tmax + 1):
        if t > nslots:
            break
        for a in range(t):
            idx[a] = a
        while True:
            code = np.int64(0)
            for a in range(t):
                j = idx[a]
                slot = prefixes[j // 10] * 10 + (j % 10)
                T[slot] = 1
                code |= np.int64(1) << np.int64(slot)
            parsed, ntok, toklen, V = _eval_full(flat, offs, s1mask, T, seen)
            L = toklen / ntok
            b = np.int64((L - BIN0) / BINW)
            if b < 0:
                b = 0
            elif b >= NBIN:
                b = NBIN - 1
            h2[parsed, b] += 1
            total += 1
            if parsed > best[b, 0, 0]:
                best[b, 0, 0] = parsed
                best[b, 0, 1] = code
                best[b, 0, 2] = ntok
                best[b, 0, 3] = toklen
                best[b, 0, 4] = V
            if vlo <= V <= vhi and parsed > best[b, 1, 0]:
                best[b, 1, 0] = parsed
                best[b, 1, 1] = code
                best[b, 1, 2] = ntok
                best[b, 1, 3] = toklen
                best[b, 1, 4] = V
            for a in range(t):
                j = idx[a]
                T[prefixes[j // 10] * 10 + (j % 10)] = 0
            if t == 0:
                break
            a = t - 1
            while a >= 0 and idx[a] == nslots - t + a:
                a -= 1
            if a < 0:
                break
            idx[a] += 1
            for b2 in range(a + 1, t):
                idx[b2] = idx[b2 - 1] + 1
    return total


def pack(books):
    flat = (np.frombuffer("".join(books).encode(), dtype=np.uint8) - 48).astype(np.uint8).copy()
    offs = np.zeros(len(books) + 1, dtype=np.int64)
    for i, b in enumerate(books):
        offs[i + 1] = offs[i] + len(b)
    return flat, offs


def codebook_from(s1mask: int, tcode: int) -> list[str]:
    """Materialise the explicit codeword list for a structure."""
    out = []
    for d in range(10):
        if (s1mask >> d) & 1:
            out.append(str(d))
    for p in range(10):
        if (s1mask >> p) & 1:
            continue
        for d in range(10):
            if (tcode >> (p * 10 + d)) & 1:
                out += [f"{p}{d}{e}" for e in range(10)]
            else:
                out.append(f"{p}{d}")
    return out


def tmatrix(tcode: int) -> np.ndarray:
    T = np.zeros(100, dtype=np.uint8)
    for j in range(100):
        if (tcode >> j) & 1:
            T[j] = 1
    return T


def bin_center(b: int) -> float:
    return BIN0 + (b + 0.5) * BINW


def describe(s1mask: int, tcode: int) -> dict:
    cb = codebook_from(s1mask, tcode)
    return {
        "S1": "".join(str(d) for d in range(10) if (s1mask >> d) & 1),
        "prefixes": "".join(str(d) for d in range(10) if not (s1mask >> d) & 1),
        "T": [f"{p}{d}" for p in range(10) for d in range(10)
              if (tcode >> (p * 10 + d)) & 1],
        "codebook_size": len(cb),
    }
