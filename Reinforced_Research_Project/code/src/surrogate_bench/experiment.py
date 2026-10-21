"""Experiment driver: one job = (instance, seed). Resumable; writes JSON records + per-sample error arrays."""
from __future__ import annotations
import json, os, sys, time, pathlib, platform, numpy as np
from multiprocessing import Pool


def _init_worker():
    for v in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS"): os.environ[v] = "1"
    import torch; torch.set_num_threads(1)


def run_job(args):
    name, seed, cfg, cache_dir, out_dir = args
    from . import methods as M
    from .problems import build_suite
    from .data import build_dataset, POOL
    from .hpo import run_method
    from .diagnostics import pilot_features
    out = pathlib.Path(out_dir); out.mkdir(parents=True, exist_ok=True)
    fjson = out / f"{name}__s{seed}.json"
    if fjson.exists(): return f"skip {fjson.name}"
    M.NN_EPOCHS = cfg["nn_epochs"]; M._train.__defaults__ = (cfg["nn_epochs"],)
    P = build_suite()[name]; d = build_dataset(P, cache_dir)
    perm = np.random.default_rng(1000 + seed).permutation(POOL)
    feats = pilot_features(d["u_train"][perm[: cfg["pilot_n0"]]])
    recs, errs, t0 = [], {}, time.time()
    for N in cfg["N_levels"]:
        idx = perm[:N]
        for meth in cfg["methods"]:
            r, e_te, e_ex = run_method(meth, d["mu_train"][idx], d["u_train"][idx], d["mu_test"], d["u_test"], d["mu_ext"], d["u_ext"],
                                       cfg["hpo_budget_B"], seed, P.p, P.m)
            r.update(instance=name, family=P.family, level=P.level, p=P.p, m=P.m); recs.append(r)
            errs[f"{N}__{meth}__interp"] = e_te; errs[f"{N}__{meth}__ext"] = e_ex
    meta = dict(instance=name, seed=seed, pilot_features=feats, fom_seconds_per_solve=float(d["fom_seconds_per_solve"]),
                job_seconds=time.time() - t0, records=recs, protocol_version=cfg["protocol_version"], quick=bool(cfg.get("_quick", False)))
    np.savez_compressed(out / f"{name}__s{seed}__errors.npz", **errs)
    tmp = fjson.with_suffix(".tmp"); tmp.write_text(json.dumps(meta, default=float)); tmp.rename(fjson)   # atomic: file exists only when complete
    return f"done {fjson.name} in {time.time()-t0:.0f}s"


def environment():
    import numpy, scipy, sklearn, torch
    return dict(python=sys.version.split()[0], numpy=numpy.__version__, scipy=scipy.__version__, sklearn=sklearn.__version__,
                torch=torch.__version__, platform=platform.platform(), cpu_count=os.cpu_count(), device="cpu")


def run(cfg, cache_dir, out_dir, seeds, workers=4, log=None):
    from .problems import build_suite
    from .data import build_dataset
    S = build_suite(); t0 = time.time()
    for n in cfg["instances"]:
        build_dataset(S[n], cache_dir, workers=workers)
    jobs = [(n, s, cfg, cache_dir, out_dir) for s in seeds for n in cfg["instances"]]
    pathlib.Path(out_dir).mkdir(parents=True, exist_ok=True)
    (pathlib.Path(out_dir) / "environment.json").write_text(json.dumps(environment(), indent=1))
    with Pool(workers, initializer=_init_worker) as pool:
        for msg in pool.imap_unordered(run_job, jobs):
            line = f"[{time.time()-t0:8.0f}s] {msg}"; print(line, flush=True)
            if log: open(log, "a").write(line + "\n")
