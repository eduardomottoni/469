"""Symbol streams for Family C.

C1  fixed-width pairs / triples at every phase offset (the documented
    refutation: positional chi-square mod 2/3/4/5 is already non-significant,
    so a fixed-width block code is a priori unlikely -- but it is cheap and it
    calibrates the solver).
C2  variable-width tokens from Family A's MDL parse (the live variant).
"""
from __future__ import annotations

import sys
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "e_a_grammar"))


def fixed_width(books, w: int, phase: int):
    """Concatenate w-digit blocks at the given phase, dropping the ragged ends."""
    toks = []
    for b in books:
        s = b[phase:]
        toks.extend(s[i:i + w] for i in range(0, len(s) - w + 1, w))
    return toks


def mdl_tokens(books, maxlen: int = 8):
    import inducers as I
    ind = I.mdl_unigram(books, maxlen=maxlen)
    return [t for p in ind.parses for t in p]


def encode(tokens, vocab=None):
    """Map tokens to contiguous integer ids, most frequent first."""
    from collections import Counter
    if vocab is None:
        vocab = [t for t, _ in Counter(tokens).most_common()]
    idx = {t: i for i, t in enumerate(vocab)}
    return np.array([idx[t] for t in tokens], dtype=np.int32), vocab
