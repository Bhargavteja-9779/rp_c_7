"""Freeze the diagnostic rules from the ORIGINAL v1 data only (results/raw at commit 931b306). Run before any v2 comparative result exists."""
import sys, json, pathlib, numpy as np, pandas as pd
ROOT = pathlib.Path(__file__).resolve().parents[3]; sys.path.insert(0, str(ROOT / "code/src"))   # original (v1) analysis code, read-only
from surrogate_bench import analysis as A, stats as S
df, ft, seeds = A.load(str(ROOT / "results/raw")); y = A.family_y(df); cells = A.cell_table(y, ft)
TIE = 0.10
# ---- Rule R1: single-feature threshold. NL wins iff f1 = log10 CV-POD error (r=4) > t. Fitted on non-tie v1 cells with N in {256, 1024}.
c = cells[cells.N.isin([256, 1024]) & (cells.y.abs() >= TIE)].copy(); c["nl"] = c.y < 0
vals = np.sort(c.log_cv_err_r4.unique()); cand = (vals[:-1] + vals[1:]) / 2; acc = [np.mean((c.log_cv_err_r4 > t) == c.nl) for t in cand]
best = max(acc); ts = [t for t, a in zip(cand, acc) if a == best]; t_star = float(np.median(ts))
# ---- Rule R2: frozen ridge regression y ~ log2N + f1 on all v1 cells N in {64..1024}; baseline B0: y ~ log2N
d = cells[cells.N.isin([64, 128, 256, 512, 1024])]; lg = np.log2(d.N.values)
m2 = S.ridge_fit(np.c_[lg, d.log_cv_err_r4.values], d.y.values, 1e-3 * len(d)); m0 = S.ridge_fit(lg[:, None], d.y.values, 1e-3 * len(d))
frozen = dict(source_commit="931b306e90693e85a3d5fd368493515d11d1d981", tie_band=TIE, R1=dict(feature="log_cv_err_r4", rule="predict NL wins iff feature > t", t=t_star, v1_train_accuracy=float(best), v1_n_cells=int(len(c)), v1_majority_share=float(max(c.nl.mean(), 1 - c.nl.mean()))),
              R2=dict(features=["log2N", "log_cv_err_r4"], mu=m2["mu"].tolist(), sd=m2["sd"].tolist(), beta=m2["beta"].tolist(), ym=float(m2["ym"])),
              B0=dict(features=["log2N"], mu=m0["mu"].tolist(), sd=m0["sd"].tolist(), beta=m0["beta"].tolist(), ym=float(m0["ym"])),
              v1_instances=sorted(cells.instance.unique().tolist()), v1_feature_range=[float(cells.log_cv_err_r4.min()), float(cells.log_cv_err_r4.max())])
out = pathlib.Path(__file__).resolve().parents[2] / "research_design/frozen_rules_from_v1.json"; out.parent.mkdir(exist_ok=True, parents=True); out.write_text(json.dumps(frozen, indent=1))
print(json.dumps({k: frozen[k] for k in ("R1", "R2", "B0", "v1_feature_range")}, indent=1))
