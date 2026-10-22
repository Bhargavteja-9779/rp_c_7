#!/usr/bin/env python3
"""v2 entry point.  python run_v2.py --exp A|D [--workers 4]   (run with OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1)
Exp A: independent replication on 8 new instances (pre-registered frozen-rule test). Exp D: POD+KRR matched-search mechanism test on 24 instances."""
import argparse, json, pathlib, sys
ROOT = pathlib.Path(__file__).resolve().parent; sys.path.insert(0, str(ROOT / "src"))
from surrogate_bench import experiment
ap = argparse.ArgumentParser(); ap.add_argument("--exp", choices=["A", "D", "A2", "E"], required=True); ap.add_argument("--workers", type=int, default=4); a = ap.parse_args()
cfg = json.load(open(ROOT / "configs" / f"exp{a.exp}.json")); R = ROOT.parent / "results"; R.mkdir(exist_ok=True)
experiment.run(cfg, str(ROOT / "data_cache"), str(R / f"raw_exp{a.exp}"), cfg["seeds"], workers=a.workers, log=str(R / f"progress_exp{a.exp}.log"))
