#!/usr/bin/env python3
"""Real-data check analysis (addendum v3.1 criteria R1-R4)."""
import json, glob, pathlib, numpy as np, pandas as pd
ROOT = pathlib.Path(__file__).resolve().parents[2]; R = ROOT / "results"; OUT = R / "s6"; OUT.mkdir(exist_ok=True)
rows = []
for f in sorted(glob.glob(str(R / "raw_expR/*__s*.json"))):
    m = json.load(open(f))
    for r in m["records"]:
        te = r["test_err"]; sel = r["selected"]; rows.append(dict(dataset=m["dataset"], seed=m["seed"], N=r["N"], selected=sel, err_sel=te[sel], err_oracle=min(te.values()), err_gp=te["pod_gp[matern52,r=32]"], err_strong=r["err_strong"], pred=r["pred_err_4N"][0], lo=min(r["pred_err_4N"][1:]), hi=max(r["pred_err_4N"][1:]),
                         te=te, basis_limited=r["floor"]["basis_limited"], sec_fit=r["seconds_fit"], sec_nn=r["seconds_nn"], curve=r["curve"], ties=r["ties"]))
D = pd.DataFrame(rows)
if D.empty: raise SystemExit("no real-data results")
g = lambda s: np.exp(np.log(s).mean())
cell = D.groupby(["dataset", "N"]).apply(lambda x: pd.Series(dict(sel=g(x.err_sel), orc=g(x.err_oracle), gp=g(x.err_gp), strong=g(x.err_strong)))).reset_index(); cell["regret"] = cell["sel"] / cell.orc; cell["r_gp"] = cell["sel"] / cell.gp; cell["r_strong"] = cell["sel"] / cell.strong
R1 = dict(n_cells=int(len(cell)), median_regret=float(cell.regret.median()), criterion_met=bool(cell.regret.median() <= 1.5), per_cell={f"{r.dataset}_{r.N}": float(r.regret) for r in cell.itertuples()})
R2 = dict(n_not_worse=int((cell["sel"] <= cell.gp * 1.0000001).sum()), n_cells=int(len(cell)), criterion_met=bool((cell["sel"] <= cell.gp * 1.0000001).sum() >= 4))
nb = int((cell.strong < cell["sel"] / 1.25).sum()); R3 = dict(n_strong_better_25=nb, n_cells=int(len(cell)), criterion_met=bool(nb <= 2), median_ratio_tool_over_strong=float(cell.r_strong.median()))
# forecast
fc = []
for (ds, seed), x in D.groupby(["dataset", "seed"]):
    x = x.set_index("N")
    for N0 in (64, 256):
        if 4 * N0 in x.index:
            name = x.loc[N0, "selected"]; act = x.loc[4 * N0, "te"].get(name); fc.append(dict(dataset=ds, seed=seed, N0=N0, pred=x.loc[N0, "pred"], actual=act, ratio=x.loc[N0, "pred"] / act))
F = pd.DataFrame(fc); F["within2"] = F.ratio.between(0.5, 2.0); R4 = dict(n_cases=int(len(F)), n_within2=int(F.within2.sum()), share=float(F.within2.mean()), criterion_met=bool(F.within2.mean() >= .7), median_log10_ratio=float(np.log10(F.ratio).median()))
errtab = cell.round(5).to_dict("records"); out = dict(R1=R1, R2=R2, R3=R3, R4=R4, cells=errtab, selected_counts=D.groupby("dataset").selected.value_counts().to_dict() if False else {ds: x.selected.value_counts().to_dict() for ds, x in D.groupby("dataset")})
json.dump(out, open(OUT / "real_criteria.json", "w"), indent=1, default=float); cell.to_csv(OUT / "real_cells.csv", index=False); F.to_csv(OUT / "real_forecast_cases.csv", index=False); print(json.dumps({k: out[k] for k in ("R1", "R2", "R3", "R4")}, indent=1, default=float))
