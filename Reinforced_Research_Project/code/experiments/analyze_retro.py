#!/usr/bin/env python3
"""Descriptive, design-informed run (addendum v3.0 sec. 6.4): tool on the earlier problems at N=256, seed 0. Compares with the oracle, the legacy validation-selected method and legacy POD+GP (same seed and N)."""
import json, glob, pathlib, sys, numpy as np, pandas as pd
ROOT = pathlib.Path(__file__).resolve().parents[2]; R = ROOT / "results"; sys.path.insert(0, str(ROOT / "code/src")); from surrogate_bench import analysis as A
dfs = [A.load(p)[0] for p in (ROOT.parent / "results/raw", R / "raw_expA", R / "raw_expA2", R / "raw_expA3")]; df = pd.concat(dfs, ignore_index=True); df = df[(df.N == 256) & (df.seed == 0)]
idx = df.groupby(["instance"]).val.idxmin(); leg = df.loc[idx][["instance", "err"]].rename(columns={"err": "leg_sel"}); gp = df[df.method == "pod_gp"][["instance", "err"]].rename(columns={"err": "leg_gp"})
rows = []
for f in sorted(glob.glob(str(R / "raw_expRetro/*__s0.json"))):
    m = json.load(open(f)); te = m["test_err"]; rows.append(dict(instance=m["instance"], err_sel=te[m["selected"]], err_oracle=min(te.values()), selected=m["selected"], basis_limited=m["floor"]["basis_limited"]))
D = pd.DataFrame(rows).merge(leg, on="instance").merge(gp, on="instance"); D["regret"] = D.err_sel / D.err_oracle; D["r_leg"] = D.err_sel / D.leg_sel; D["r_gp"] = D.err_sel / D.leg_gp
out = dict(n_problems=int(len(D)), median_regret=float(D.regret.median()), share_regret_le2=float((D.regret <= 2).mean()), max_regret=float(D.regret.max()), median_ratio_vs_legacy_selection=float(D.r_leg.median()), tool_better_10=int((D.r_leg < 1 / 1.1).sum()), tool_worse_10=int((D.r_leg > 1.1).sum()),
           median_ratio_vs_pod_gp=float(D.r_gp.median()), n_basis_flagged=int(D.basis_limited.sum()), worst=D.sort_values("regret", ascending=False).head(3)[["instance", "regret"]].values.tolist())
(R / "s6").mkdir(exist_ok=True); json.dump(out, open(R / "s6/retro.json", "w"), indent=1, default=float); D.to_csv(R / "s6/retro_cells.csv", index=False); print(json.dumps(out, indent=1))
