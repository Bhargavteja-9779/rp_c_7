#!/usr/bin/env python3
"""Case study: run the command-line tool on plain files for heatmove_L1 (N=256, seed 0, target 0.1%) and store the verbatim report and the held-out error."""
import json, os, pathlib, subprocess, sys, tempfile, numpy as np
ROOT = pathlib.Path(__file__).resolve().parents[2]; sys.path.insert(0, str(ROOT / "code/src"))
from surrogate_bench.problems import build_suite
from surrogate_bench.data import build_dataset, POOL
env = dict(os.environ, PYTHONPATH=str(ROOT / "surroselect/src"), OMP_NUM_THREADS="1"); name, N, seed = "heatmove_L1", 256, 0
d = build_dataset(build_suite()[name], str(ROOT / "code/data_cache")); idx = np.random.default_rng(1000 + seed).permutation(POOL)[:N]
with tempfile.TemporaryDirectory() as t:
    t = pathlib.Path(t); np.savez(t / "train.npz", X=d["mu_train"][idx], Y=d["u_train"][idx]); np.savez(t / "test.npz", X=d["mu_test"], Y=d["u_test"]); run = lambda *a: subprocess.run([sys.executable, "-m", "surroselect.cli", *a], capture_output=True, text=True, env=env)
    r1 = run("fit", str(t / "train.npz"), "--model", str(t / "m.pkl"), "--target", "0.001", "--seed", str(seed)); r2 = run("evaluate", str(t / "m.pkl"), str(t / "test.npz"), "--json", str(t / "ev.json"))
    ev = json.load(open(t / "ev.json")); (ROOT / "paper/tables/case_report.txt").write_text(r1.stdout); (ROOT / "results/s6/case_study.json").write_text(json.dumps(dict(problem=name, N=N, seed=seed, held_out=ev, report=r1.stdout, ok=(r1.returncode == 0 and r2.returncode == 0)), indent=1)); print(r1.stdout, r2.stdout)
