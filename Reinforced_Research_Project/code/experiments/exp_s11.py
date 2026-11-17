#!/usr/bin/env python3
"""Stage 11 (research_design/protocol_addendum_v3.6.md): pole deflation.  python experiments/exp_s11.py --exp F|S|D|H [--workers 4]
F  tool (default 7-member pool + PoleDeflated(PodGP rbf), refit_all) on the 4 FRESH frequency-response problems, N in {64,256,1024}, seeds 0-2.   S  plain tuned MLP (16 trials), N in {256,1024}.
D  pole-deflated tuned MLP: PoleDeflated(TunedMLP(16 trials)), N in {256,1024}.   H  no-harm: the tool of F on the 52 earlier problems, N = 256, seeds 0-1.
The old-pool selection is derived in the analysis from the stored CV table of the same run."""
import argparse, json, os, sys, time, pathlib, warnings
for v in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS"): os.environ[v] = "1"
ROOT = pathlib.Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT / "src")); sys.path.insert(0, str(ROOT.parent / "surroselect/src")); sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import numpy as np
from multiprocessing import Pool
import exp_s7 as S7
FRF2 = ["mdk_chain_L1", "mdk_chain_L2", "disc_acoustic_L1", "disc_acoustic_L2"]


def h_problems():
    from surrogate_bench.problems import build_suite
    return sorted(build_suite().keys()) + S7.NEW


def job(args):
    exp, name, seed, out_dir = args; warnings.filterwarnings("ignore")
    from surrogate_bench.problems import get_problem
    from surrogate_bench.data import build_dataset
    from surroselect import SurrogateSelector, PoleDeflated, rel_l2
    from surroselect.models import default_candidates
    from surroselect.nn import TunedMLP
    out = pathlib.Path(out_dir); out.mkdir(parents=True, exist_ok=True); f = out / f"{name}__s{seed}.json"
    if f.exists(): return f"skip {f.name}"
    P = get_problem(name); d = build_dataset(P, str(ROOT / "data_cache")); recs = []; t00 = time.time()
    for N in {"F": (64, 256, 1024), "S": (256, 1024), "D": (256, 1024), "H": (256,)}[exp]:
        X, Y = S7._split(d, seed, N); t0 = time.time()
        if exp in ("F", "H"):
            cands = default_candidates(Y.shape[1], N, X.shape[1]) + ([PoleDeflated()] if X.shape[1] <= 6 else [])
            sel = SurrogateSelector(candidates=cands, cv=4, random_state=seed).fit(X, Y, refit_all=True); recs.append(S7._tool_record(sel, d, N, seed, t0, time.time() - t0, False))
        else:
            m = (TunedMLP(seed=seed, n_trials=16) if exp == "S" else PoleDeflated(TunedMLP(seed=seed, n_trials=16), seed=seed)).fit(X, Y)
            recs.append(dict(N=N, test_err=rel_l2(d["u_test"], m.predict(d["mu_test"])), chosen=getattr(m, "chosen", None), seconds=time.time() - t0))
        print(f"  {name} s{seed} N={N} done in {time.time()-t0:.0f}s", flush=True)
    meta = dict(instance=name, seed=seed, p=P.p, m=P.m, records=recs, protocol_version="3.6-" + exp, job_seconds=time.time() - t00)
    tmp = f.with_suffix(".tmp"); tmp.write_text(json.dumps(meta, default=float)); tmp.rename(f); return f"done {f.name} in {time.time()-t00:.0f}s"


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--exp", choices=["F", "S", "D", "H"], required=True); ap.add_argument("--workers", type=int, default=4); a = ap.parse_args()
    out = ROOT.parent / "results" / f"raw_exp11{a.exp}"; names = h_problems() if a.exp == "H" else FRF2; seeds = (0, 1) if a.exp == "H" else (0, 1, 2)
    from surrogate_bench.problems import get_problem
    from surrogate_bench.data import build_dataset
    for n in names: build_dataset(get_problem(n), str(ROOT / "data_cache"), workers=a.workers)       # data are generated in the parent process; no surrogate is fitted here
    jobs = [(a.exp, n, s, str(out)) for n in names for s in seeds]
    with Pool(a.workers, maxtasksperchild=1) as pool:
        for r in pool.imap_unordered(job, jobs): print(r, flush=True)
