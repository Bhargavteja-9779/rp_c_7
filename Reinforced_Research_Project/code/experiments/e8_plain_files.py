#!/usr/bin/env python3
"""E8: validate the TOOL ITSELF on plain files, through the command line only (no benchmark pipeline in the loop): export three problems to .npz files, run
`surroselect fit`, `predict`, `evaluate` as subprocesses, and compare the error reported by `evaluate` with an independent computation from the predicted file."""
import json, os, pathlib, subprocess, sys, tempfile, time, numpy as np
ROOT = pathlib.Path(__file__).resolve().parents[2]; sys.path.insert(0, str(ROOT / "code/src"))
from surrogate_bench.problems import build_suite
from surrogate_bench.data import build_dataset, POOL
env = dict(os.environ, PYTHONPATH=str(ROOT / "surroselect/src"), OMP_NUM_THREADS="1"); out = {"problems": {}}; S = build_suite()
for name in ("heatcomp_L1", "lshape_L1", "convdiff_L1"):
    d = build_dataset(S[name], str(ROOT / "code/data_cache")); idx = np.random.default_rng(1000).permutation(POOL)[:256]
    with tempfile.TemporaryDirectory() as t:
        t = pathlib.Path(t); np.savez(t / "train.npz", X=d["mu_train"][idx], Y=d["u_train"][idx]); np.savez(t / "test.npz", X=d["mu_test"], Y=d["u_test"]); np.save(t / "xnew.npy", d["mu_test"])
        run = lambda *a: subprocess.run([sys.executable, "-m", "surroselect.cli", *a], capture_output=True, text=True, env=env); t0 = time.time()
        r1 = run("fit", str(t / "train.npz"), "--model", str(t / "m.pkl"), "--target", "0.01", "--json", str(t / "fit.json")); t_fit = time.time() - t0
        r2 = run("predict", str(t / "m.pkl"), str(t / "xnew.npy"), "--out", str(t / "yhat.npy")); r3 = run("evaluate", str(t / "m.pkl"), str(t / "test.npz"), "--json", str(t / "ev.json"))
        ok = all(r.returncode == 0 for r in (r1, r2, r3)); Yh = np.load(t / "yhat.npy"); Y = d["u_test"]; err_indep = float(np.mean(np.linalg.norm(Y - Yh, axis=1) / np.linalg.norm(Y, axis=1))); ev = json.load(open(t / "ev.json")); fit = json.load(open(t / "fit.json"))
        out["problems"][name] = dict(N=256, ok=bool(ok), selected=fit["selected"], cv_error=fit["cv_error"], test_error_cli_evaluate=ev["mean_relative_l2_error"], test_error_independent=err_indep, agree=bool(abs(ev["mean_relative_l2_error"] - err_indep) < 1e-12), seconds_fit_cli=t_fit,
                                     runs_needed_1pct=None if not fit.get("curve") else None, report_head=r1.stdout[:1500])
(ROOT / "results/s6").mkdir(exist_ok=True); (ROOT / "results/s6/plain_files_validation.json").write_text(json.dumps(out, indent=1)); print({k: (v["ok"], v["agree"], v["selected"], round(v["test_error_cli_evaluate"], 5)) for k, v in out["problems"].items()})
