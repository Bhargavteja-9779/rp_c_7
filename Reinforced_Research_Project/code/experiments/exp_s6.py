#!/usr/bin/env python3
"""Stage 6 experiments (protocol_addendum_v3.0.md).  python experiments/exp_s6.py --exp C|S [--workers 4]
C: SurroSelect evaluation (pool errors, selection, tie set, floor report, learning curve).  S: strong tuned MLP (Optuna) at N in {256, 1024}."""
import argparse, json, os, sys, time, pathlib, warnings
for v in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS"): os.environ[v] = "1"
ROOT = pathlib.Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT / "src")); sys.path.insert(0, str(ROOT.parent / "surroselect/src"))
import numpy as np
from multiprocessing import Pool
INSTANCES = ["lshape_L1", "lshape_L2", "heatcomp_L1", "heatcomp_L2", "heatmove_L1", "heatmove_L2", "convdiff_L1", "convdiff_L2"]


def _split(d, seed, N):
    from surrogate_bench.data import POOL
    perm = np.random.default_rng(1000 + seed).permutation(POOL)[:N]; return d["mu_train"][perm], d["u_train"][perm]


def job(args):
    exp, name, seed, out_dir = args
    warnings.filterwarnings("ignore")
    from surrogate_bench.problems import build_suite
    from surrogate_bench.data import build_dataset
    from surroselect import SurrogateSelector, rel_l2
    out = pathlib.Path(out_dir); out.mkdir(parents=True, exist_ok=True); f = out / f"{name}__s{seed}.json"
    if f.exists(): return f"skip {f.name}"
    P = build_suite()[name]; d = build_dataset(P, str(ROOT / "data_cache")); recs = []; t00 = time.time()
    for N in (json.loads(os.environ["S6_N"]) if "S6_N" in os.environ else ([64, 256, 1024] if exp == "C" else [256, 1024])):
        X, Y = _split(d, seed, N); t0 = time.time()
        if exp == "C":
            sel = SurrogateSelector(cv=4, random_state=seed).fit(X, Y, refit_all=True); t_fit = time.time() - t0; sel.learning_curve(); t_all = time.time() - t0
            errs = {k: rel_l2(d["u_test"], m.predict(sel._scale(d["mu_test"]))) for k, m in sel.all_models_.items()}
            ext = {k: rel_l2(d["u_ext"], m.predict(sel._scale(d["mu_ext"]))) for k, m in sel.all_models_.items()}
            pe = {int(M): [float(v) for v in sel.predict_error(M)] for M in (4 * N,)}
            recs.append(dict(N=N, selected=sel.best_name_, ties=sel.ties_, cv_table=[dict(name=r["name"], cv_error=r["cv_error"], seconds=r["seconds"], message=r["message"]) for r in sel.cv_table_],
                             test_err=errs, ext_err=ext, floor=sel.floor_report_, curve=sel.curve_, pred_err_4N=pe, seconds_fit=t_fit, seconds_total=t_all,
                             runs_needed_1pct=sel.runs_needed(0.01), runs_needed_01pct=sel.runs_needed(0.001)))
        else:
            from surroselect.nn import TunedMLP
            m = TunedMLP(n_trials=16, seed=seed).fit(X, Y); Xs = (np.asarray(d["mu_test"], float)); 
            recs.append(dict(N=N, best_params=m.best_params_, best_val_error=m.best_val_error_, test_err=rel_l2(d["u_test"], m.predict(d["mu_test"])), ext_err=rel_l2(d["u_ext"], m.predict(d["mu_ext"])), seconds=time.time() - t0))
        print(f"  {name} s{seed} N={N} done in {time.time()-t0:.0f}s", flush=True)
    meta = dict(instance=name, seed=seed, p=P.p, m=P.m, records=recs, protocol_version="3.0-" + exp, job_seconds=time.time() - t00)
    tmp = f.with_suffix(".tmp"); tmp.write_text(json.dumps(meta, default=float)); tmp.rename(f); return f"done {f.name} in {time.time()-t00:.0f}s"


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--exp", choices=["C", "S"], required=True); ap.add_argument("--workers", type=int, default=4); a = ap.parse_args()
    out = ROOT.parent / "results" / f"raw_exp6{a.exp}"; jobs = [(a.exp, n, s, str(out)) for n in INSTANCES for s in (0, 1, 2)]
    with Pool(a.workers) as pool:
        for r in pool.imap_unordered(job, jobs): print(r, flush=True)
