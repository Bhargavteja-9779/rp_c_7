#!/usr/bin/env python3
"""One-command rerun of everything: experiments (resumable), analysis, aggregation (macros + tables), figures, tests, paper build.
    python code/run_all.py [--skip-experiments] [--skip-build]
Experiments are resumable: finished jobs (atomic JSON) are skipped; a full rerun of the original 16-problem stage is long (hours). Logs go to results/logs/."""
import argparse, os, pathlib, subprocess, sys, time
ROOT = pathlib.Path(__file__).resolve().parents[1]; CODE = ROOT / "code"; LOGS = ROOT / "results/logs"; LOGS.mkdir(parents=True, exist_ok=True)
ENV = dict(os.environ, OMP_NUM_THREADS="1", MKL_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1", PYTHONHASHSEED="0")
def run(name, cmd, cwd=CODE):
    t = time.time(); print(f"[{name}] ...", flush=True)
    with open(LOGS / f"{name}.log", "w") as f: r = subprocess.run(cmd, cwd=cwd, env=ENV, stdout=f, stderr=subprocess.STDOUT)
    print(f"[{name}] exit {r.returncode} in {time.time()-t:.0f}s", flush=True)
    if r.returncode: sys.exit(f"{name} failed; see {LOGS / (name + '.log')}")
ap = argparse.ArgumentParser(); ap.add_argument("--skip-experiments", action="store_true"); ap.add_argument("--skip-build", action="store_true"); a = ap.parse_args(); py = sys.executable
if not a.skip_experiments:
    for e in ("A", "D", "A2", "E", "A3", "G", "H8", "H32", "G3", "6T"): run(f"exp_{e}", [py, "run_v2.py", "--exp", e, "--workers", "4"])
    run("exp_B", [py, "experiments/exp_b_strong_nn.py"]); run("exp_F", [py, "experiments/exp_f_precision.py"])
    run("exp_6C", [py, "experiments/exp_s6.py", "--exp", "C"]); run("exp_6S", [py, "experiments/exp_s6.py", "--exp", "S"])
    run("exp_7E_data", [py, "experiments/exp_s7.py", "--exp", "E7gen"]); run("exp_7T", [py, "run_v2.py", "--exp", "7T", "--workers", "4"])
    for e in ("C7", "S7", "N7", "SP"): run(f"exp_{e}", [py, "experiments/exp_s7.py", "--exp", e])
    run("exp_7E", [py, "experiments/exp_s7.py", "--exp", "E7"])
    run("exp_real", [py, "experiments/exp_real.py", "4"]); run("exp_retro", [py, "experiments/exp_retro.py"]); run("recheck_real_tool", [py, "experiments/recheck_real_tool.py"]); run("e8_plain_files", [py, "experiments/e8_plain_files.py"]); run("case_study", [py, "experiments/case_study.py"])
run("tests_benchmark", [py, "-m", "pytest", "tests", "-q"]); run("tests_tool", [py, "-m", "pytest", "tests", "-q"], cwd=ROOT / "surroselect")
run("analyze_earlier", [py, "experiments/analyze_earlier.py"]); run("analyze_s6", [py, "experiments/analyze_s6.py"]); run("analyze_s7", [py, "experiments/analyze_s7.py"]); run("analyze_s7_posthoc", [py, "experiments/analyze_s7_posthoc.py"]); run("analyze_real", [py, "experiments/analyze_real.py"]); run("analyze_retro", [py, "experiments/analyze_retro.py"]); run("prereg_order", [py, "../audit/prereg_order_check.py"]); run("leakage_audit", [py, "../audit/leakage_planted_test.py"]); run("budget", [py, "../audit/budget_to_accuracy.py"])
run("aggregate", [py, "experiments/aggregate.py"])
for f in ("fig_framework", "fig_main_result", "fig_mechanism", "fig_validity", "fig_qualitative", "fig_strong_nn"):
    if (CODE / "visualization" / f"{f}.py").exists(): run(f, [py, f"visualization/{f}.py"])
if not a.skip_build: run("build", ["bash", "build.sh"], cwd=ROOT / "paper")
print("all done")
