#!/usr/bin/env python3
"""Stage 9 (research_design/protocol_addendum_v3.4.md): learning-curve dataset for calibrated budget forecasts.  python experiments/exp_s9.py --workers 4
Per (problem, seed) and N0 in {64, 128, 256}: run the tool (cross-validated selection, learning curve, no refit of all members), then fit the SELECTED member on the nested subsets of size 2*N0 and 4*N0 (same permutation) and
record its test error = the forecast target.  Development problems: the 44-problem suite.  Held-out problems: the 8 Stage 7 problems, plus bracket3d_L1 and lshape_fine_L1 (pools of 512 runs: N0 in {64, 128} only)."""
import argparse, json, os, sys, time, pathlib, warnings
for v in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS"): os.environ[v] = "1"
ROOT = pathlib.Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT / "src")); sys.path.insert(0, str(ROOT.parent / "surroselect/src"))
import numpy as np
from multiprocessing import Pool
HELD = ["helmholtz_L1", "helmholtz_L2", "reacdiff_fe_L1", "reacdiff_fe_L2", "disc_elast_L1", "disc_elast_L2", "advdiff_cell_L1", "advdiff_cell_L2"]; SPECIAL = {"bracket3d_L1": "bracket3d_L1_e8.npz", "lshape_fine_L1": "lshape_fine_L1_e7.npz"}


def all_jobs():
    from surrogate_bench.problems import build_suite
    dev = sorted(build_suite().keys()); return [("dev", n) for n in dev] + [("held", n) for n in HELD] + [("held", n) for n in SPECIAL]


def load(name):
    if name in SPECIAL:
        z = np.load(ROOT / "data_cache" / SPECIAL[name]); d = {k: z[k] for k in z.files}; pool = len(d["mu_train"]); from surrogate_bench.problems import get_problem; P = get_problem(name); return P, d, pool
    from surrogate_bench.problems import get_problem
    from surrogate_bench.data import build_dataset, POOL
    P = get_problem(name); return P, build_dataset(P, str(ROOT / "data_cache")), POOL


def job(args):
    split, name, seed, out_dir = args; warnings.filterwarnings("ignore")
    from surroselect import SurrogateSelector, make_candidate, rel_l2
    out = pathlib.Path(out_dir); out.mkdir(parents=True, exist_ok=True); f = out / f"{name}__s{seed}.json"
    if f.exists(): return f"skip {f.name}"
    P, d, pool = load(name); perm = np.random.default_rng(1000 + seed).permutation(pool); recs = []; t00 = time.time()
    for N0 in ((64, 128) if pool < 1000 else (64, 128, 256)):
        X0, Y0 = d["mu_train"][perm[:N0]], d["u_train"][perm[:N0]]; t0 = time.time()
        sel = SurrogateSelector(cv=4, random_state=seed).fit(X0, Y0); curve = sel.learning_curve(); name_sel = sel.best_name_; secs = time.time() - t0
        rec = dict(N0=N0, selected=name_sel, curve=dict(n=[float(v) for v in curve["n"]], error=[float(v) for v in curve["error"]]), best_cv_error=float(sel.best_cv_error_), pod_floor_cv=float(sel.floor_report_["pod_floor_cv"]), usable=bool(sel.usable_),
                   cv_table=[dict(name=r["name"], cv_error=r["cv_error"]) for r in sel.cv_table_], tool_seconds=secs, actual={})
        for h in (1, 2, 4):
            N = h * N0
            if N > pool: continue
            idx = perm[:N]; X, Y = d["mu_train"][idx], d["u_train"][idx]; lo = X.min(0); sp = np.where(X.max(0) - lo > 0, X.max(0) - lo, 1.0); sc = lambda Z: (Z - lo) / sp
            try: m = make_candidate(name_sel).fit(sc(X), Y); rec["actual"][str(h)] = float(rel_l2(d["u_test"], m.predict(sc(d["mu_test"]))))
            except Exception as e: rec["actual"][str(h)] = float("inf")
        recs.append(rec)
    meta = dict(split=split, instance=name, family=P.family, p=P.p, m=P.m, seed=seed, records=recs, protocol_version="3.4", job_seconds=time.time() - t00)
    tmp = f.with_suffix(".tmp"); tmp.write_text(json.dumps(meta, default=float)); tmp.rename(f); return f"done {f.name} in {time.time()-t00:.0f}s"


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--workers", type=int, default=4); ap.add_argument("--only", default=None); a = ap.parse_args()
    out = ROOT.parent / "results" / "raw_exp9L"; jobs = [(sp, n, s, str(out)) for sp, n in all_jobs() for s in (0, 1, 2) if a.only is None or n == a.only]
    # long jobs first so that the pool stays busy
    with Pool(a.workers, maxtasksperchild=1) as pool:
        for r in pool.imap_unordered(job, jobs): print(r, flush=True)
