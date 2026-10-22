"""Exp A2 candidate selection: compute ONLY pilot features (no surrogate is run) for the 8 candidate instances and apply the pre-stated rule
f1 (seed-mean log10 LOO CV-POD error, r=4, 32 pilot snapshots) < -2.0. Writes research_design/expA2_selection.json."""
import sys, json, pathlib, numpy as np
ROOT = pathlib.Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT / "src"))
from surrogate_bench.problems import build_suite_v21
from surrogate_bench.data import build_dataset, POOL
from surrogate_bench.diagnostics import pilot_features
S = build_suite_v21(); out = {}
for name, P in S.items():
    d = build_dataset(P, str(ROOT / "data_cache"), workers=4); f = []
    for s in (0, 1, 2):
        perm = np.random.default_rng(1000 + s).permutation(POOL); f.append(pilot_features(d["u_train"][perm[:32]])["log_cv_err_r4"])
    out[name] = dict(p=P.p, f1_seed_mean=float(np.mean(f)), f1_per_seed=[float(x) for x in f])
qual = sorted(k for k, v in out.items() if v["f1_seed_mean"] < -2.0)
res = dict(rule="qualifies iff seed-mean f1 < -2.0", candidates=out, qualifying=qual, n_qualifying=len(qual))
(ROOT.parent / "research_design/expA2_selection.json").write_text(json.dumps(res, indent=1)); print(json.dumps(res, indent=1))
