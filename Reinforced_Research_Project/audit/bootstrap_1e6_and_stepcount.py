"""Analysis-only: (d) Exp A P2 cluster-bootstrap with 10^6 draws (exact multinomial equivalent of resampling instances); (f) NN step-count at N=1024 vs Exp B shifts by N."""
import sys, json, pathlib, numpy as np, pandas as pd
ROOT = pathlib.Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT / "code/src"))
from surrogate_bench import analysis as A, analysis_v2 as V
fz = V.frozen(ROOT / "research_design/frozen_rules_from_v1.json"); dfA, ftA, _ = A.load(ROOT / "results/raw_expA"); cA = A.cell_table(A.family_y(dfA), ftA)
d = cA[cA.N.isin([64, 128, 256, 512, 1024])].sort_values(["instance", "N"]).reset_index(drop=True); lg = np.log2(d.N.values)
gain = (d.y.values - V._pred(fz["B0"], lg[:, None])) ** 2 - (d.y.values - V._pred(fz["R2"], np.c_[lg, d.log_cv_err_r4.values])) ** 2
U = np.unique(d.instance.values); S = np.array([gain[d.instance.values == u].sum() for u in U]); n = np.array([(d.instance.values == u).sum() for u in U])
rng = np.random.default_rng(12345); B = 1_000_000; counts = rng.multinomial(len(U), np.ones(len(U)) / len(U), size=B)
boot = (counts @ S) / (counts @ n)
out = dict(P2_gain=float(gain.mean()), ci95=[float(np.percentile(boot, 2.5)), float(np.percentile(boot, 97.5))], p_one_sided=float((np.sum(boot <= 0) + 1) / (B + 1)), n_boot=B)
# Holm with P1 exact p = 0.17994
p1, p2 = 0.17993551587301587, out["p_one_sided"]; out["holm_adj_P2"] = float(min(1, 2 * p2)) if p2 <= p1 else float(min(1, max(p2, p1)))
b = pd.read_csv(ROOT / "results/expA_primary/tables/expB_cells.csv"); out["expB_shift_toward_NL_by_N"] = {int(N): dict(mean=float(g.shift_toward_NL.mean()), median=float(g.shift_toward_NL.median())) for N, g in b.groupby("N")}
out["step_count_note"] = "Adam steps: N<=512 -> 1500 (full batch); N=1024 -> 3000 (batch 512). Exp B (6000 epochs) gives 4x/4x steps at N=256 (6000 vs 1500) and 4x at N=1024 (12000 vs 3000)."
(ROOT / "results/bootstrap_1e6_and_stepcount.json").write_text(json.dumps(out, indent=1)); print(json.dumps(out, indent=1))
