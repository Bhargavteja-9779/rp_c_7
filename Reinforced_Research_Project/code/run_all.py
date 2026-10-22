#!/usr/bin/env python3
"""Single entry point.  python run_all.py --mode quick   (pipeline check, NOT evidence)
                       python run_all.py --mode full    (pre-registered experiment + analysis)"""
import os
for _v in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS"): os.environ.setdefault(_v, "1")   # before numpy is imported (audit F18)
import argparse, json, pathlib, sys
ROOT = pathlib.Path(__file__).resolve().parent; sys.path.insert(0, str(ROOT / "src"))
from surrogate_bench import experiment

ap = argparse.ArgumentParser(); ap.add_argument("--mode", choices=["quick", "full"], required=True)
ap.add_argument("--workers", type=int, default=4); ap.add_argument("--seeds", type=int, nargs="*", default=None)
ap.add_argument("--stage", choices=["experiments", "analysis", "all"], default="all")
a = ap.parse_args()
cfg = json.load(open(ROOT / "configs" / "protocol.json"))
RES = ROOT.parent / "results"
if a.mode == "quick":
    cfg.update(cfg.pop("quick")); cfg["_quick"] = True; out = RES / "quick_NOT_EVIDENCE" / "raw"; cache = RES / "quick_NOT_EVIDENCE" / "cache"
    seeds = cfg["seeds_required"]
else:
    cfg.pop("quick"); out = RES / "raw"; cache = ROOT / "data_cache"; seeds = a.seeds if a.seeds is not None else cfg["seeds_required"]
if a.stage in ("experiments", "all"):
    experiment.run(cfg, str(cache), str(out), seeds, workers=a.workers, log=str(RES / "progress.log"))
if a.stage in ("analysis", "all"):
    import importlib
    try: mod = importlib.import_module("surrogate_bench.analysis")
    except ImportError: print("analysis module not yet available"); sys.exit(0)
    mod.main(str(out), str(RES / ("quick_NOT_EVIDENCE" if a.mode == "quick" else "")), quick=(a.mode == "quick"))
