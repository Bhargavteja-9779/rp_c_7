#!/usr/bin/env python3
"""Real-data check (protocol_addendum_v3.1.md): tool vs always-GP vs strongly tuned network on two measured datasets (scalar outputs, noisy). Metric: normalised RMSE."""
import json, os, sys, time, pathlib, warnings
for v in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS"): os.environ[v] = "1"
ROOT = pathlib.Path(__file__).resolve().parents[2]; sys.path.insert(0, str(ROOT / "surroselect/src"))
import numpy as np
from multiprocessing import Pool
DATA = dict(airfoil="airfoil_self_noise.npz", ccpp="ccpp.npz")


def load(name):
    z = np.load(ROOT / "data_real" / DATA[name]); X, Y = z["X"].astype(float), z["Y"].astype(float)
    if name == "airfoil": X = X.copy(); X[:, 0] = np.log10(X[:, 0]); X[:, 4] = np.log10(X[:, 4])        # frequency and displacement thickness span two decades (decided in addendum v3.1)
    perm = np.random.default_rng(12345).permutation(len(X)); nt = int(0.3 * len(X)); te, pool = perm[:nt], perm[nt:]; return X[pool], Y[pool], X[te], Y[te]


def job(args):
    name, seed, out_dir = args; warnings.filterwarnings("ignore")
    from surroselect import SurrogateSelector, nrmse
    from surroselect.nn import TunedMLP
    out = pathlib.Path(out_dir); out.mkdir(parents=True, exist_ok=True); f = out / f"{name}__s{seed}.json"
    if f.exists(): return f"skip {f.name}"
    Xp, Yp, Xt, Yt = load(name); perm = np.random.default_rng(1000 + seed).permutation(len(Xp)); recs = []; t00 = time.time()
    for N in (64, 256, 1024):
        idx = perm[:N]; X, Y = Xp[idx], Yp[idx]; t0 = time.time(); sel = SurrogateSelector(cv=4, random_state=seed, metric="nrmse").fit(X, Y, refit_all=True); t_fit = time.time() - t0; sel.learning_curve()
        te = {k: nrmse(Yt, m.predict(sel._scale(Xt)), Y) for k, m in sel.all_models_.items()}; lo, sp = sel.lo_, sel.span_
        t1 = time.time(); nn = TunedMLP(n_trials=16, seed=seed, metric="nrmse").fit((X - lo) / sp, Y); err_nn = nrmse(Yt, nn.predict((Xt - lo) / sp), Y); t_nn = time.time() - t1
        recs.append(dict(N=N, selected=sel.best_name_, ties=sel.ties_, cv_table=[dict(name=r["name"], cv_error=r["cv_error"]) for r in sel.cv_table_], test_err=te, err_strong=err_nn, floor=sel.floor_report_, curve=sel.curve_,
                         pred_err_4N=[float(v) for v in sel.predict_error(4 * N)], seconds_fit=t_fit, seconds_nn=t_nn)); print(f"  {name} s{seed} N={N} {time.time()-t0:.0f}s", flush=True)
    tmp = f.with_suffix(".tmp"); tmp.write_text(json.dumps(dict(dataset=name, seed=seed, n_pool=int(len(Xp)), n_test=int(len(Xt)), records=recs, protocol_version="3.1-R"), default=float)); tmp.rename(f); return f"done {f.name} in {time.time()-t00:.0f}s"


if __name__ == "__main__":
    out = ROOT / "results/raw_expR"; jobs = [(n, s, str(out)) for n in DATA for s in (0, 1, 2)]
    with Pool(int(sys.argv[1]) if len(sys.argv) > 1 else 2) as pool:
        for r in pool.imap_unordered(job, jobs): print(r, flush=True)
