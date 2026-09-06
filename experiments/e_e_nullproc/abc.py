"""ABC fit of the copy-paste generator to the 469 corpus (family E)."""
from __future__ import annotations

import json, math, os, random, sys, time
from multiprocessing import Pool
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from cpm import CopyPasteMutateFitted, sample_prior, PRIOR
from c469.corpus import load_books
from c469.stats import abc_summary, ABC_KEYS

HERE = Path(__file__).resolve().parent
_BOOKS: list[str] = []
_OBS: dict = {}
_SCALE: dict = {}


def _init(books, obs, scale):
    global _BOOKS, _OBS, _SCALE
    _BOOKS, _OBS, _SCALE = books, obs, scale


def _sim(args):
    i, theta = args
    g = CopyPasteMutateFitted(**theta)
    try:
        sv = abc_summary(g.generate(_BOOKS, 1000003 * i + 17))
    except Exception:
        return theta, None, float("inf")
    d = math.sqrt(sum(((sv[k] - _OBS[k]) / _SCALE[k]) ** 2 for k in ABC_KEYS)
                  / len(ABC_KEYS))
    return theta, sv, d


def perturb(theta, rng, scale=0.25):
    t = dict(theta)
    for k, (lo, hi) in PRIOR.items():
        w = (hi - lo) * scale
        v = t[k] + rng.gauss(0, w)
        v = min(hi, max(lo, v))
        t[k] = int(round(v)) if k in ("seed_len", "seed_order") else v
    t["seed_order"] = max(1, min(4, int(t["seed_order"])))
    t["seed_len"] = max(200, int(t["seed_len"]))
    return t


def run(n_round1=40000, n_round2=40000, keep=60, procs=2, seed=0):
    c = load_books(with_kharos=False)
    books = list(c.books)
    obs = abc_summary(books)
    # prior-predictive scale: SD of each summary over 300 prior draws
    rng = random.Random(seed)
    pilot = [(i, sample_prior(rng)) for i in range(150)]
    scale = {k: 1.0 for k in ABC_KEYS}
    with Pool(procs, _init, (books, obs, scale)) as p:
        pil = p.map(_sim, pilot, chunksize=8)
    svs = [s for _, s, _ in pil if s]
    scale = {}
    for k in ABC_KEYS:
        vals = [s[k] for s in svs]
        m = sum(vals) / len(vals)
        sd = (sum((v - m) ** 2 for v in vals) / len(vals)) ** 0.5
        scale[k] = sd if sd > 1e-9 else max(1e-9, abs(obs[k]) * 0.01)
    print("prior-predictive scales:", {k: round(v, 4) for k, v in scale.items()},
          flush=True)

    def batch(jobs, tag):
        t0 = time.time()
        res = []
        with Pool(procs, _init, (books, obs, scale)) as p:
            for i, r in enumerate(p.imap_unordered(_sim, jobs, chunksize=8), 1):
                res.append(r)
                if i % 500 == 0:
                    best = min(x[2] for x in res)
                    print(f"  {tag} {i}/{len(jobs)} "
                          f"({time.time()-t0:.0f}s) best d={best:.3f}", flush=True)
        res = [r for r in res if r[1] is not None]
        res.sort(key=lambda r: r[2])
        print(f"{tag}: {len(res)} sims in {time.time()-t0:.0f}s "
              f"best d={res[0][2]:.3f}", flush=True)
        return res

    jobs = [(i, sample_prior(rng)) for i in range(n_round1)]
    r1 = batch(jobs, "round1")
    post = [t for t, _, _ in r1[:keep]]

    jobs2 = []
    for i in range(n_round2):
        jobs2.append((n_round1 + i, perturb(rng.choice(post), rng, 0.10)))
    r2 = batch(jobs2, "round2")

    allr = sorted(r1 + r2, key=lambda r: r[2])
    best_theta, best_sv, best_d = allr[0]
    posterior = allr[:keep]

    # posterior predictive: 300 draws from the accepted set
    pp_jobs = [(900000 + i, posterior[i % len(posterior)][0]) for i in range(150)]
    with Pool(procs, _init, (books, obs, scale)) as p:
        pp = p.map(_sim, pp_jobs, chunksize=8)
    pp_svs = [s for _, s, _ in pp if s]
    ppcheck = {}
    for k in ABC_KEYS:
        vals = sorted(s[k] for s in pp_svs)
        m = sum(vals) / len(vals)
        sd = (sum((v - m) ** 2 for v in vals) / len(vals)) ** 0.5
        lo, hi = vals[int(0.025 * len(vals))], vals[int(0.975 * len(vals)) - 1]
        p_two = 2 * min(sum(v <= obs[k] for v in vals),
                        sum(v >= obs[k] for v in vals)) / len(vals)
        ppcheck[k] = dict(observed=obs[k], pp_mean=m, pp_sd=sd,
                          ci95=[lo, hi], inside=bool(lo <= obs[k] <= hi),
                          z=(obs[k] - m) / sd if sd else 0.0,
                          pp_p=min(1.0, p_two))

    marg = {}
    for k in PRIOR:
        vals = sorted(t[k] for t, _, _ in posterior)
        marg[k] = dict(median=vals[len(vals) // 2], q05=vals[int(0.05 * len(vals))],
                       q95=vals[int(0.95 * len(vals)) - 1],
                       prior=list(PRIOR[k]))

    out = dict(n_sims=len(allr), observed=obs, scales=scale,
               best_theta=best_theta, best_distance=best_d, best_summary=best_sv,
               posterior_marginals=marg,
               posterior_predictive=ppcheck,
               accepted=[dict(theta=t, d=d) for t, _, d in posterior[:50]])
    (HERE / "abc_fit.json").write_text(json.dumps(out, indent=1, default=str))
    print(json.dumps(ppcheck, indent=1, default=str), flush=True)
    print("best theta:", best_theta, "d=%.3f" % best_d, flush=True)
    return out


if __name__ == "__main__":
    n1 = int(sys.argv[1]) if len(sys.argv) > 1 else 40000
    n2 = int(sys.argv[2]) if len(sys.argv) > 2 else 40000
    run(n1, n2)
