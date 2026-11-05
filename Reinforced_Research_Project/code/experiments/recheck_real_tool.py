#!/usr/bin/env python3
"""Re-run ONLY the tool part of the real-data check after the scalar-output shape fix (review 03) and compare with the stored results/raw_expR (selected model, test errors)."""
import json, os, sys, pathlib, warnings
for v in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS"): os.environ[v] = "1"
ROOT = pathlib.Path(__file__).resolve().parents[2]; sys.path.insert(0, str(ROOT / "surroselect/src")); sys.path.insert(0, str(ROOT / "code/experiments"))
import numpy as np
from multiprocessing import Pool
import exp_real
def job(a):
    name, seed = a; warnings.filterwarnings("ignore"); from surroselect import SurrogateSelector, nrmse
    Xp, Yp, Xt, Yt = exp_real.load(name); perm = np.random.default_rng(1000 + seed).permutation(len(Xp)); old = json.load(open(ROOT / f"results/raw_expR/{name}__s{seed}.json")); out = []
    for N, o in zip((64, 256, 1024), old["records"]):
        idx = perm[:N]; X, Y = Xp[idx], Yp[idx]; sel = SurrogateSelector(cv=4, random_state=seed, metric="nrmse").fit(X, Y, refit_all=True)
        te = {k: nrmse(Yt, m.predict(sel._scale(Xt)), Y) for k, m in sel.all_models_.items()}
        out.append(dict(dataset=name, seed=seed, N=N, selected_new=sel.best_name_, selected_old=o["selected"], same_selection=sel.best_name_ == o["selected"], err_new=te[sel.best_name_], err_old=o["test_err"][o["selected"]], gp_full_err_new=min(v for k, v in te.items() if k.startswith("gp_full")), gp_full_err_old=min(v for k, v in o["test_err"].items() if k.startswith("gp_full"))))
    return out
if __name__ == "__main__":
    jobs = [(n, s) for n in exp_real.DATA for s in (0, 1, 2)]
    with Pool(3) as pool: res = [r for rr in pool.map(job, jobs) for r in rr]
    (ROOT / "results/s6/real_recheck_after_shape_fix.json").write_text(json.dumps(res, indent=1, default=float)); print(sum(r["same_selection"] for r in res), "of", len(res), "selections unchanged; max abs change in selected error:", max(abs(r["err_new"] - r["err_old"]) for r in res))
