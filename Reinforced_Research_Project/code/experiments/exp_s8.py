#!/usr/bin/env python3
"""Stage 8 (research_design/protocol_addendum_v3.3.md): the expensive three-dimensional problem.  python experiments/exp_s8.py --exp gen|run
gen: solve 512 training-pool runs and 300 test runs of bracket3d_L1 (about ten seconds per run).  run: tool (v0.2.0, refit_all for the oracle), always-POD+GP, tuned network (N = 256); N in {64, 256}, seeds 0-2, run serially so timings are clean."""
import argparse, json, os, sys, time, pathlib, warnings
for v in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS"): os.environ[v] = "1"
ROOT = pathlib.Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT / "src")); sys.path.insert(0, str(ROOT.parent / "surroselect/src")); sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import numpy as np
from multiprocessing import Pool
import exp_s7 as S7
NAME = "bracket3d_L1"; E_POOL, E_TEST = 512, 300
_prob = {}


def _solve_chunk(mus):
    from surrogate_bench.problems import get_problem
    P = _prob.setdefault(NAME, get_problem(NAME)); return np.array([P.solve(m) for m in mus])


def data():
    from surrogate_bench.problems import get_problem
    cache = ROOT / "data_cache" / f"{NAME}_e8.npz"
    if cache.exists(): return {k: v for k, v in np.load(cache).items()}
    P = get_problem(NAME); mu_tr = S7._rng(NAME, "train").random((E_POOL, P.p)); mu_te = S7._rng(NAME, "test").random((E_TEST, P.p))
    rs = np.random.default_rng(0).random((8, P.p)); t0 = time.time(); [P.solve(m) for m in rs]; t_sim = (time.time() - t0) / 8                       # idle machine, one solve at a time
    allmu = np.vstack([mu_tr, mu_te]); t0 = time.time()
    with Pool(4) as pool: U = np.vstack(pool.map(_solve_chunk, np.array_split(allmu, 100)))
    d = dict(mu_train=mu_tr, u_train=U[:E_POOL], mu_test=mu_te, u_test=U[E_POOL:], t_sim=np.array(t_sim), gen_seconds=np.array(time.time() - t0)); np.savez(cache, **d); return d


def run():
    warnings.filterwarnings("ignore")
    from surroselect import SurrogateSelector, rel_l2
    from surroselect.nn import TunedMLP
    d = data(); out = ROOT.parent / "results" / "raw_exp8E"; out.mkdir(parents=True, exist_ok=True)
    for seed in (0, 1, 2):
        f = out / f"{NAME}__s{seed}.json"
        if f.exists(): continue
        recs = []
        for N in (64, 256):
            perm = np.random.default_rng(1000 + seed).permutation(E_POOL)[:N]; X, Y = d["mu_train"][perm], d["u_train"][perm]; t0 = time.time()
            sel = SurrogateSelector(cv=4, random_state=seed).fit(X, Y, refit_all=True); t_fit = time.time() - t0; rec = S7._tool_record(sel, d, N, seed, t0, t_fit, True); rec["usable"] = bool(sel.usable_); rec["best_cv_error"] = float(sel.best_cv_error_)
            if N == 256:
                t1 = time.time(); m = TunedMLP(seed=seed, n_trials=16).fit(X, Y); rec["network"] = dict(test_err=rel_l2(d["u_test"], m.predict(d["mu_test"])), seconds=time.time() - t1, best_params=m.best_params_)
            recs.append(rec); print(f"  E8 s{seed} N={N} done in {time.time()-t0:.0f}s", flush=True)
        f.write_text(json.dumps(dict(instance=NAME, seed=seed, records=recs, t_sim=float(d["t_sim"]), data_gen_seconds=float(d["gen_seconds"]), protocol_version="3.3-E8"), default=float))


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--exp", choices=["gen", "run"], required=True); a = ap.parse_args()
    if a.exp == "gen": data(); print("E8 data ready")
    else: run()
