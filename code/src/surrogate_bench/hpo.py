"""Matched hyper-parameter optimisation: identical budget B and identical protocol for every method."""
from __future__ import annotations
import time, zlib, numpy as np
from .methods import REGISTRY, rel_l2


def run_method(method, X, Y, Xte, Yte, Xex, Yex, B, seed, p, m):
    """X,Y: the N training samples. Random search of B configs (trial 0 = default) on an 80/20 split;
    selection uses VALIDATION error only. Test errors of every trial are logged for the tuning-budget
    analysis but never used for selection. Winner is refit on all N samples."""
    Cls = REGISTRY[method]; rng = np.random.default_rng(seed * 7919 + zlib.crc32(method.encode()) % 10007)   # stable across processes (built-in hash() is salted per process)
    N = len(X); nv = max(2, int(round(0.2 * N))); perm = np.random.default_rng(seed).permutation(N)
    iv, it = perm[:nv], perm[nv:]
    trials, t_hpo = [], 0.0
    for b in range(B):
        cfg = Cls.sample_config(rng, N, p, m, b); t0 = time.time()
        try:
            mdl = Cls().fit(X[it], Y[it], cfg, seed * 100 + b)
            val = float(rel_l2(Y[iv], mdl.predict(X[iv])).mean()); tst = float(rel_l2(Yte, mdl.predict(Xte)).mean())
        except Exception as e:                                       # a failed config counts as diverged (inf)
            val, tst = float("inf"), float("inf")
        dt = time.time() - t0; t_hpo += dt
        trials.append(dict(trial=b, cfg=cfg, val=val, test=tst, seconds=dt))
    best = min(trials, key=lambda t: t["val"])
    t0 = time.time(); mdl = Cls().fit(X, Y, best["cfg"], seed * 100 + 99); t_fit = time.time() - t0
    t0 = time.time(); Pte = mdl.predict(Xte); t_inf = (time.time() - t0) / len(Xte)
    e_te = rel_l2(Yte, Pte); e_ex = rel_l2(Yex, mdl.predict(Xex))
    return dict(method=method, N=N, seed=seed, best_cfg=best["cfg"], val_best=best["val"], trials=trials,
                test_err=float(e_te.mean()), test_med=float(np.median(e_te)), test_p95=float(np.quantile(e_te, .95)),
                ext_err=float(e_ex.mean()), t_fit=t_fit, t_hpo=t_hpo, t_infer_per_sample=t_inf), e_te.astype(np.float32), e_ex.astype(np.float32)
