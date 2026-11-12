#!/usr/bin/env python3
"""Worked example for the paper: export 256 runs of the 3D cantilever (bracket3d_L1, about ten seconds per run) and run the command-line tool as a user would.
Writes results/s8/bracket3d_report.md; the paper listing is the same text wrapped to 96 columns. Needs results of exp_s8.py --exp gen."""
import subprocess, sys, pathlib, tempfile, numpy as np
ROOT = pathlib.Path(__file__).resolve().parents[2]; d = np.load(ROOT / "code/data_cache/bracket3d_L1_e8.npz"); perm = np.random.default_rng(1000).permutation(512)[:256]
with tempfile.TemporaryDirectory() as t:
    t = pathlib.Path(t); np.savez(t / "train.npz", X=d["mu_train"][perm], Y=d["u_train"][perm]); np.savez(t / "test.npz", X=d["mu_test"], Y=d["u_test"])
    env = dict(PYTHONPATH=str(ROOT / "surroselect/src"), OMP_NUM_THREADS="1", PATH="/usr/bin:/bin:/usr/local/bin")
    run = lambda *a: subprocess.run([sys.executable, "-m", "surroselect.cli", *a], capture_output=True, text=True, env=env, cwd=t)
    r = run("fit", "train.npz", "--target", "0.001", "--solver-seconds", f"{float(d['t_sim']):.2f}", "--queries", "10000", "--model", "m.pkl", "--report", str(ROOT / "results/s8/bracket3d_report.md")); print(r.stdout[-400:]); print(run("evaluate", "m.pkl", "test.npz").stdout)
