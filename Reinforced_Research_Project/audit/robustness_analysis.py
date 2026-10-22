"""Analysis-only robustness checks (no new training). Reads v1 raw + Exp A raw. Outputs results/robustness_analysis.json.
 (1) tie-band sensitivity of the cell classification; (2) seed sign-consistency of clear cells;
 (3) config-draw sensitivity: y recomputed from two DISJOINT halves of the 8 random-search trials (even / odd trial index);
 (4) POD+MLP vs direct-MLP contrast at N=1024 is in expD/other files (not repeated)."""
import sys, json, pathlib, numpy as np, pandas as pd
ROOT = pathlib.Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT / "code/src"))
from surrogate_bench import analysis as A
v1 = ROOT.parent / "results/raw"; dA = ROOT / "results/raw_expA"
dfO, ftO, _ = A.load(v1); dfA, ftA, _ = A.load(dA); df = pd.concat([dfO, dfA], ignore_index=True)
y = A.family_y(df); cells = y.groupby(["instance", "N"], as_index=False).agg(y=("y", "mean"))
out = {"n_instances": int(df.instance.nunique()), "n_cells": int(len(cells))}
def cls(v, t): return np.where(v > t, "LS", np.where(v < -t, "NL", "tie"))
out["tie_band"] = {}
for t in [0.05, 0.10, 0.15, 0.30]:
    for N in [32, 1024]:
        c = cells[cells.N == N]; k = cls(c.y.values, t); out["tie_band"][f"t={t},N={N}"] = {s: int((k == s).sum()) for s in ["LS", "NL", "tie"]}
# seed sign consistency among clear cells (|ybar|>0.10)
clear = cells[cells.y.abs() > 0.10][["instance", "N", "y"]]; m = y.merge(clear, on=["instance", "N"], suffixes=("", "_cell"))
m["same"] = np.sign(m.y) == np.sign(m.y_cell); g = m.groupby(["instance", "N"]).same.mean()
out["seed_sign_consistency"] = dict(n_clear_cells=int(len(g)), mean_share_seeds_same_sign=float(g.mean()), share_cells_all_seeds_same=float((g == 1).mean()), share_cells_ge_2_of_3=float((g >= 2/3 - 1e-9).mean()))
# config-draw halves
LS, NL = A.LS, A.NL
def half_y(sub):
    rows = []
    for (inst, N, s), g in df.groupby(["instance", "N", "seed"]):
        g = g.set_index("method"); res = {}
        for mth in A.METHODS:
            tr = [g.loc[mth, "trials"][i] for i in sub if i < len(g.loc[mth, "trials"])]; t = min(tr, key=lambda z: z["val"]); res[mth] = (t["val"], t["test"])
        a = min(LS, key=lambda k: res[k][0]); b = min(NL, key=lambda k: res[k][0])
        rows.append(dict(instance=inst, N=N, seed=s, y=float(np.log10(res[b][1] / res[a][1]))))
    return pd.DataFrame(rows).groupby(["instance", "N"], as_index=False).y.mean()
h0, h1 = half_y([0, 2, 4, 6]), half_y([1, 3, 5, 7]); j = h0.merge(h1, on=["instance", "N"], suffixes=("_even", "_odd"))
ce, co = cls(j.y_even.values, .1), cls(j.y_odd.values, .1); cl = (np.abs(j.y_even) > .1) & (np.abs(j.y_odd) > .1)
out["config_draw_halves"] = dict(n_cells=int(len(j)), class_agreement=float((ce == co).mean()), sign_agreement_when_both_clear=float((np.sign(j.y_even[cl]) == np.sign(j.y_odd[cl])).mean()), n_both_clear=int(cl.sum()),
    pearson_y=float(np.corrcoef(j.y_even, j.y_odd)[0, 1]), mean_abs_diff=float((j.y_even - j.y_odd).abs().mean()),
    by_N={int(N): dict(agree=float((cls(g.y_even.values, .1) == cls(g.y_odd.values, .1)).mean())) for N, g in j.groupby("N")})
(ROOT / "results/robustness_analysis.json").write_text(json.dumps(out, indent=1)); print(json.dumps(out, indent=1))
