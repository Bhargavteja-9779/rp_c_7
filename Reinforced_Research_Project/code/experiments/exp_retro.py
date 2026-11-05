#!/usr/bin/env python3
"""Addendum v3.0 section 6.4 (design-informed, descriptive): run the tool on the 36 earlier problems at N=256, seed 0, with all pool members scored on test data. NOT evidence for criteria S1-B2 (the pool was designed with knowledge of these problems)."""
import json, os, sys, time, pathlib, warnings
for v in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS"): os.environ[v] = "1"
ROOT = pathlib.Path(__file__).resolve().parents[2]; sys.path.insert(0, str(ROOT / "code/src")); sys.path.insert(0, str(ROOT / "surroselect/src"))
import numpy as np
from multiprocessing import Pool
TP = ("lshape", "heatcomp", "heatmove", "convdiff")


def job(name):
    warnings.filterwarnings("ignore")
    from surrogate_bench.problems import build_suite
    from surrogate_bench.data import build_dataset, POOL
    from surroselect import SurrogateSelector, rel_l2
    out = ROOT / "results/raw_expRetro"; out.mkdir(exist_ok=True, parents=True); f = out / f"{name}__s0.json"
    if f.exists(): return f"skip {name}"
    P = build_suite()[name]; d = build_dataset(P, str(ROOT / "code/data_cache")); idx = np.random.default_rng(1000).permutation(POOL)[:256]; t0 = time.time()
    sel = SurrogateSelector(cv=4, random_state=0).fit(d["mu_train"][idx], d["u_train"][idx], refit_all=True); te = {k: rel_l2(d["u_test"], m.predict(sel._scale(d["mu_test"]))) for k, m in sel.all_models_.items()}
    tmp = f.with_suffix(".tmp"); tmp.write_text(json.dumps(dict(instance=name, seed=0, N=256, selected=sel.best_name_, test_err=te, floor=sel.floor_report_, seconds=time.time() - t0, protocol_version="3.0-retro"), default=float)); tmp.rename(f); return f"done {name} {time.time()-t0:.0f}s"


if __name__ == "__main__":
    sys.path.insert(0, str(ROOT / "code/src")); from surrogate_bench.problems import build_suite
    names = [n for n, P in build_suite().items() if P.family not in TP]
    with Pool(4) as pool:
        for r in pool.imap_unordered(job, names): print(r, flush=True)
