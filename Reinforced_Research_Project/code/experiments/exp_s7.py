#!/usr/bin/env python3
"""Stage 7 experiments (research_design/protocol_addendum_v3.2.md).  python experiments/exp_s7.py --exp C7|S7|SP|N7|E7gen|E7 [--workers 4]
C7  SurroSelect (default pool) on the 8 new problems, N in {64,256,1024}.   S7  tuned MLP (16 trials, Stage 6 search space), N in {256,1024}.
SP  stronger tuned MLP (48 trials, depth 2-5, width up to 512), N=256, all 16 third-party problems.   N7  SurroSelect with a tuned MLP in the pool, N=256, 8 new problems.
E7gen  solve the seconds-per-run problem (512 pool + 300 test runs).  E7  tool / always-GP / network on that problem, N in {64,256}, run serially so that timings are clean."""
import argparse, json, os, sys, time, pathlib, warnings, hashlib
for v in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS"): os.environ[v] = "1"
ROOT = pathlib.Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT / "src")); sys.path.insert(0, str(ROOT.parent / "surroselect/src"))
import numpy as np
from multiprocessing import Pool
NEW = ["helmholtz_L1", "helmholtz_L2", "reacdiff_fe_L1", "reacdiff_fe_L2", "disc_elast_L1", "disc_elast_L2", "advdiff_cell_L1", "advdiff_cell_L2"]
OLD = ["lshape_L1", "lshape_L2", "heatcomp_L1", "heatcomp_L2", "heatmove_L1", "heatmove_L2", "convdiff_L1", "convdiff_L2"]
SPEC = {"C7": (NEW, (64, 256, 1024)), "S7": (NEW, (256, 1024)), "SP": (OLD + NEW, (256,)), "N7": (NEW, (256,))}
SP_KW = dict(n_trials=48, depth_range=(2, 5), widths=(64, 128, 256, 512))
FINE = "lshape_fine_L1"; E_POOL, E_TEST = 512, 300


def _split(d, seed, N):
    from surrogate_bench.data import POOL
    perm = np.random.default_rng(1000 + seed).permutation(POOL)[:N]; return d["mu_train"][perm], d["u_train"][perm]


def _tool_record(sel, d, N, seed, t0, t_fit, with_curve):
    from surroselect import rel_l2
    errs = {k: rel_l2(d["u_test"], m.predict(sel._scale(d["mu_test"]))) for k, m in sel.all_models_.items()}
    ext = {k: rel_l2(d["u_ext"], m.predict(sel._scale(d["mu_ext"]))) for k, m in sel.all_models_.items()} if "u_ext" in d else {}
    rec = dict(N=N, selected=sel.best_name_, ties=sel.ties_, cv_table=[dict(name=r["name"], cv_error=r["cv_error"], seconds=r["seconds"], message=r["message"]) for r in sel.cv_table_],
               test_err=errs, ext_err=ext, floor=sel.floor_report_, seconds_fit=t_fit)
    if with_curve:
        sel.learning_curve(); rec.update(curve=sel.curve_, pred_err_4N={int(4 * N): [float(v) for v in sel.predict_error(4 * N)]}, seconds_total=time.time() - t0,
                                         runs_needed_1pct=sel.runs_needed(0.01), runs_needed_01pct=sel.runs_needed(0.001))
    return rec


def job(args):
    exp, name, seed, out_dir = args
    warnings.filterwarnings("ignore")
    from surrogate_bench.problems import get_problem
    from surrogate_bench.data import build_dataset
    from surroselect import SurrogateSelector, rel_l2
    from surroselect.models import default_candidates
    from surroselect.nn import TunedMLP
    out = pathlib.Path(out_dir); out.mkdir(parents=True, exist_ok=True); f = out / f"{name}__s{seed}.json"
    if f.exists(): return f"skip {f.name}"
    P = get_problem(name); d = build_dataset(P, str(ROOT / "data_cache")); recs = []; t00 = time.time()
    for N in SPEC[exp][1]:
        X, Y = _split(d, seed, N); t0 = time.time()
        if exp == "C7":
            sel = SurrogateSelector(cv=4, random_state=seed).fit(X, Y, refit_all=True); recs.append(_tool_record(sel, d, N, seed, t0, time.time() - t0, True))
        elif exp == "N7":
            sel = SurrogateSelector(candidates=default_candidates(Y.shape[1], N) + [TunedMLP(n_trials=16, seed=seed)], cv=4, random_state=seed).fit(X, Y, refit_all=True); recs.append(_tool_record(sel, d, N, seed, t0, time.time() - t0, False))
        else:
            kw = SP_KW if exp == "SP" else dict(n_trials=16)
            m = TunedMLP(seed=seed, **kw).fit(X, Y)
            recs.append(dict(N=N, best_params=m.best_params_, best_val_error=m.best_val_error_, test_err=rel_l2(d["u_test"], m.predict(d["mu_test"])), ext_err=rel_l2(d["u_ext"], m.predict(d["mu_ext"])), seconds=time.time() - t0))
        print(f"  {name} s{seed} N={N} done in {time.time()-t0:.0f}s", flush=True)
    meta = dict(instance=name, seed=seed, p=P.p, m=P.m, records=recs, protocol_version="3.2-" + exp, job_seconds=time.time() - t00)
    tmp = f.with_suffix(".tmp"); tmp.write_text(json.dumps(meta, default=float)); tmp.rename(f); return f"done {f.name} in {time.time()-t00:.0f}s"


# ------------------------------------------------------------------------------------------------ expensive-solver case
def _rng(name, stream): return np.random.default_rng(int(hashlib.sha256(f"{name}|{stream}".encode()).hexdigest()[:8], 16))   # same construction as surrogate_bench.data


def _solve_chunk(mus):
    from surrogate_bench.problems import get_problem
    P = get_problem(FINE); return np.array([P.solve(m) for m in mus])


def e7_data():
    from surrogate_bench.problems import get_problem
    cache = ROOT / "data_cache" / f"{FINE}_e7.npz"
    if cache.exists(): return {k: v for k, v in np.load(cache).items()}
    P = get_problem(FINE); mu_tr = _rng(FINE, "train").random((E_POOL, P.p)); mu_te = _rng(FINE, "test").random((E_TEST, P.p))
    rs = np.random.default_rng(0).random((20, P.p)); t0 = time.time(); [P.solve(m) for m in rs]; t_sim = (time.time() - t0) / 20          # idle-machine timing, one solve at a time
    allmu = np.vstack([mu_tr, mu_te]); t0 = time.time()
    with Pool(4) as pool: U = np.vstack(pool.map(_solve_chunk, np.array_split(allmu, 64)))
    d = dict(mu_train=mu_tr, u_train=U[:E_POOL], mu_test=mu_te, u_test=U[E_POOL:], t_sim=np.array(t_sim), gen_seconds=np.array(time.time() - t0))
    np.savez(cache, **d); return d


def e7_run():
    warnings.filterwarnings("ignore")
    from surroselect import SurrogateSelector, rel_l2
    from surroselect.nn import TunedMLP
    d = e7_data(); out = ROOT.parent / "results" / "raw_exp7E"; out.mkdir(parents=True, exist_ok=True)
    for seed in (0, 1, 2):
        f = out / f"{FINE}__s{seed}.json"
        if f.exists(): continue
        recs = []
        for N in (64, 256):
            perm = np.random.default_rng(1000 + seed).permutation(E_POOL)[:N]; X, Y = d["mu_train"][perm], d["u_train"][perm]; t0 = time.time()
            sel = SurrogateSelector(cv=4, random_state=seed).fit(X, Y, refit_all=True); t_fit = time.time() - t0; rec = _tool_record(sel, d, N, seed, t0, t_fit, True)
            if N == 256:
                t1 = time.time(); m = TunedMLP(seed=seed, n_trials=16).fit(X, Y); rec["network"] = dict(test_err=rel_l2(d["u_test"], m.predict(d["mu_test"])), seconds=time.time() - t1, best_params=m.best_params_)
            recs.append(rec); print(f"  E7 s{seed} N={N} done in {time.time()-t0:.0f}s", flush=True)
        f.write_text(json.dumps(dict(instance=FINE, seed=seed, records=recs, t_sim=float(d["t_sim"]), data_gen_seconds=float(d["gen_seconds"]), protocol_version="3.2-E7"), default=float))


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--exp", choices=["C7", "S7", "SP", "N7", "E7gen", "E7"], required=True); ap.add_argument("--workers", type=int, default=4); a = ap.parse_args()
    if a.exp == "E7gen": e7_data(); print("E7 data ready"); sys.exit(0)
    if a.exp == "E7": e7_run(); sys.exit(0)
    out = ROOT.parent / "results" / f"raw_exp7{ {'C7': 'C', 'S7': 'S', 'SP': 'SP', 'N7': 'N'}[a.exp] }"
    jobs = [(a.exp, n, s, str(out)) for n in SPEC[a.exp][0] for s in (0, 1, 2)]
    with Pool(a.workers) as pool:
        for r in pool.imap_unordered(job, jobs): print(r, flush=True)
