"""Scoring, pre-registration and reporting.

Rules enforced in code, not by good intentions:
  * an experiment must declare STATISTIC and NULL_FAMILIES before it may score
  * p is the empirical two-sided value with the +1 correction
  * a run that tests many candidates reports Benjamini-Hochberg q, not best raw p
  * a finding must clear every family in surrogate.DEFAULT_FAMILIES
"""
from __future__ import annotations

import json
import math
import os
import subprocess
import time
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Callable, Sequence

from . import surrogate as U

REPO = Path(__file__).resolve().parent.parent
RESULTS = REPO / "results"


def _code_sha() -> str:
    try:
        return subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=REPO,
                              capture_output=True, text=True, timeout=10).stdout.strip()
    except Exception:
        return "unknown"


@dataclass
class NullResult:
    family: str
    n: int
    mean: float
    sd: float
    p: float
    z: float
    maximum: float
    minimum: float


@dataclass
class Result:
    experiment: str
    statistic: str
    real_value: float
    direction: str                  # "greater" | "less"
    nulls: list[NullResult] = field(default_factory=list)
    corpus_provenance: str = ""
    n_candidates_tested: int = 1
    seed: int = 0
    runtime_s: float = 0.0
    code_sha: str = field(default_factory=_code_sha)
    extra: dict = field(default_factory=dict)

    @property
    def worst_p(self) -> float:
        """A finding is only as strong as the null family it does worst against."""
        return max((n.p for n in self.nulls), default=1.0)

    @property
    def verdict(self) -> str:
        if not self.nulls:
            return "UNSCORED"
        required = {f.name for f in U.DEFAULT_FAMILIES}
        if not required.issubset({n.family for n in self.nulls}):
            return "INCOMPLETE (missing required null families)"
        if self.worst_p < 0.01:
            return "SUPPORTED"
        if self.worst_p < 0.05:
            return "WEAK"
        return "REJECTED"

    def save(self) -> Path:
        RESULTS.mkdir(exist_ok=True)
        p = RESULTS / f"{self.experiment}.{self.statistic}.json"
        d = asdict(self)
        d["worst_p"] = self.worst_p
        d["verdict"] = self.verdict
        p.write_text(json.dumps(d, indent=2, default=str))
        return p


class Experiment:
    """Base class.  Subclasses declare what they will test BEFORE testing it."""
    NAME: str = ""
    STATISTIC: str = ""
    DIRECTION: str = "greater"
    NULL_FAMILIES: Sequence[U.Surrogate] = ()

    def compute(self, books: list[str]) -> float:
        raise NotImplementedError

    def run(self, books: list[str], provenance: str = "", n_nulls: int = 1000,
            seed: int = 0, n_candidates: int = 1, extra: dict | None = None,
            progress: bool = False) -> Result:
        if not self.NAME or not self.STATISTIC:
            raise ValueError("experiment must declare NAME and STATISTIC "
                             "before it may be scored (pre-registration)")
        if not self.NULL_FAMILIES:
            raise ValueError("experiment must declare NULL_FAMILIES")
        t0 = time.time()
        real = float(self.compute(list(books)))
        res = Result(self.NAME, self.STATISTIC, real, self.DIRECTION,
                     corpus_provenance=provenance, seed=seed,
                     n_candidates_tested=n_candidates, extra=extra or {})
        for fam in self.NULL_FAMILIES:
            vals = []
            for i in range(n_nulls):
                vals.append(float(self.compute(fam.generate(list(books), seed * 100003 + i))))
                if progress and i % max(1, n_nulls // 10) == 0:
                    print(f"  {fam.name} {i}/{n_nulls}", flush=True)
            res.nulls.append(summarize_null(fam.name, real, vals, self.DIRECTION))
        res.runtime_s = time.time() - t0
        return res


def summarize_null(family: str, real: float, vals: Sequence[float],
                   direction: str = "greater") -> NullResult:
    n = len(vals)
    mean = sum(vals) / n if n else float("nan")
    sd = (sum((v - mean) ** 2 for v in vals) / n) ** 0.5 if n else float("nan")
    if direction == "greater":
        hits = sum(v >= real for v in vals)
    else:
        hits = sum(v <= real for v in vals)
    p = (1 + hits) / (1 + n)
    z = (real - mean) / sd if sd else 0.0
    return NullResult(family, n, mean, sd, p, z, max(vals), min(vals))


def bh_qvalues(pvals: Sequence[float]) -> list[float]:
    """Benjamini-Hochberg.  A search over 5000 codebooks does not get to quote
    its best raw p."""
    m = len(pvals)
    order = sorted(range(m), key=lambda i: pvals[i])
    q = [0.0] * m
    prev = 1.0
    for rank, i in enumerate(reversed(order), 1):
        k = m - rank + 1
        prev = min(prev, pvals[i] * m / k)
        q[i] = prev
    return q


def report(results_dir: Path | None = None) -> str:
    d = results_dir or RESULTS
    rows = []
    for p in sorted(d.glob("*.json")):
        r = json.loads(p.read_text())
        rows.append(r)
    if not rows:
        return "no results yet\n"
    out = ["| experiment | statistic | real | worst null | p | verdict |",
           "|---|---|---|---|---|---|"]
    for r in sorted(rows, key=lambda r: r.get("worst_p", 1.0)):
        worst = max(r["nulls"], key=lambda n: n["p"]) if r["nulls"] else None
        wn = f"{worst['family']} {worst['mean']:.4g}+-{worst['sd']:.3g}" if worst else "-"
        out.append(f"| {r['experiment']} | {r['statistic']} | {r['real_value']:.6g} | "
                   f"{wn} | {r.get('worst_p', 1.0):.4g} | {r.get('verdict','?')} |")
    return "\n".join(out) + "\n"
