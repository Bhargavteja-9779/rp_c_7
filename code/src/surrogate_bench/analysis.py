"""Pre-registered analysis (protocol v1.0). Reads results/raw/*.json -> results/{raw_results.csv, metrics.json, statistics.json, tables/}."""
from __future__ import annotations
import json, glob, pathlib, numpy as np, pandas as pd
from . import stats as S

LS = ["pod_gp", "pod_poly", "pod_mlp"]; NL = ["mlp_direct", "bottleneck"]; METHODS = LS + NL
N_H2 = [64, 128, 256, 512, 1024]


# ------------------------------------------------------------------------------------------------ loading
def load(raw_dir, instances=None, seeds=None):
    rows, feats, errs = [], [], {}
    for f in sorted(glob.glob(str(pathlib.Path(raw_dir) / "*__s*.json"))):
        m = json.load(open(f)); inst, s = m["instance"], m["seed"]
        feats.append(dict(instance=inst, seed=s, fom_s=m["fom_seconds_per_solve"], **m["pilot_features"]))
        for r in m["records"]:
            rows.append(dict(instance=inst, family=r["family"], level=r["level"], p=r["p"], m=r["m"], seed=s, N=r["N"], method=r["method"],
                             val=r["val_best"], err=r["test_err"], err_med=r["test_med"], err_p95=r["test_p95"], ext=r["ext_err"],
                             t_fit=r["t_fit"], t_hpo=r["t_hpo"], t_inf=r["t_infer_per_sample"], trials=r["trials"]))
    df, ft = pd.DataFrame(rows), pd.DataFrame(feats)
    if df.empty: raise SystemExit("no results found")
    n_inst = df.instance.nunique(); full = [s for s, g in df.groupby("seed") if g.instance.nunique() == n_inst]   # complete batches only
    if seeds is not None: full = [s for s in full if s in seeds]
    return df[df.seed.isin(full)].reset_index(drop=True), ft[ft.seed.isin(full)].reset_index(drop=True), full


# ------------------------------------------------------------------------------------------------ winners / y
def family_y(df):
    """Per (instance,N,seed): validation-selected LS*/NL*, y = log10(err_NL*/err_LS*), plus oracle y and extrapolation values."""
    out = []
    for (inst, N, s), g in df.groupby(["instance", "N", "seed"]):
        g = g.set_index("method"); ls = g.loc[LS]; nl = g.loc[NL]
        a, b = ls.val.idxmin(), nl.val.idxmin()
        out.append(dict(instance=inst, family=g.family.iloc[0], p=int(g.p.iloc[0]), N=N, seed=s, ls_star=a, nl_star=b,
                        err_ls=ls.loc[a, "err"], err_nl=nl.loc[b, "err"], ext_ls=ls.loc[a, "ext"], ext_nl=nl.loc[b, "ext"],
                        y=float(np.log10(nl.loc[b, "err"] / ls.loc[a, "err"])),
                        y_oracle=float(np.log10(nl.err.min() / ls.err.min()))))
    return pd.DataFrame(out)


def cell_table(y, ft, n0_feats=("log_cv_err_r4", "slope", "log_cv_err_r8", "r_tol1e-2")):
    c = y.groupby(["instance", "family", "p", "N"], as_index=False).agg(y=("y", "mean"), y_oracle=("y_oracle", "mean"), nl_wins=("y", lambda v: float(np.mean(v < 0))))
    f = ft.groupby("instance")[list(n0_feats)].mean().reset_index()
    return c.merge(f, on="instance")


# ------------------------------------------------------------------------------------------------ H1
def h1(cells):
    a = cells[cells.N == 32].sort_values("instance"); H1a = S.wilcoxon_greater(a.y.values)
    rhos, k = [], 0
    for inst, g in cells.groupby("instance"):
        g = g.sort_values("N"); r = S.spearman(np.log2(g.N.values), g.y.values); rhos.append(dict(instance=inst, rho=r))
    rh = pd.DataFrame(rhos).dropna(); k = int((rh.rho < 0).sum()); H1b = S.sign_test_greater(k, len(rh)); H1b["rhos"] = rh.set_index("instance").rho.round(3).to_dict()
    return H1a, H1b


# ------------------------------------------------------------------------------------------------ H2
def h2(cells, extra_models=True, n_boot=10000):
    d = cells[cells.N.isin(N_H2)].sort_values(["instance", "N"]).reset_index(drop=True)
    y, g = d.y.values, d.family.values; logN = np.log2(d.N.values)
    designs = dict(B0=np.c_[logN], B1=np.c_[logN, d.p.values], M_spec=np.c_[logN, d.log_cv_err_r4.values, d.slope.values])
    if extra_models:
        designs.update(M_cv4_only=np.c_[logN, d.log_cv_err_r4.values], M_slope_only=np.c_[logN, d.slope.values],
                       M_spec_plus_p=np.c_[logN, d.p.values, d.log_cv_err_r4.values, d.slope.values],
                       M_rtol=np.c_[logN, d.p.values, d["r_tol1e-2"].values], M_cv8=np.c_[logN, d.p.values, d.log_cv_err_r8.values])
    res = {k: S.lofo_residuals(X, y, g) for k, X in designs.items()}
    out = dict(n_cells=int(len(d)), n_families=int(len(np.unique(g))), rmse={k: float(np.sqrt(np.mean(v**2))) for k, v in res.items()})
    out["primary_M_spec_vs_B1"] = S.cluster_bootstrap_rmse_diff(res["B1"], res["M_spec"], g, n_boot)
    out["M_spec_vs_B0"] = S.cluster_bootstrap_rmse_diff(res["B0"], res["M_spec"], g, n_boot)
    if extra_models:
        for k in ("M_cv4_only", "M_slope_only", "M_spec_plus_p", "M_rtol", "M_cv8"): out[f"exploratory_{k}_vs_B1"] = S.cluster_bootstrap_rmse_diff(res["B1"], res[k], g, n_boot)
    yhat = {k: y - res[k] for k in res}
    out["sign_accuracy"] = {k: S.sign_accuracy(y, yhat[k]) for k in ("B0", "B1", "M_spec")}
    d = d.assign(**{f"yhat_{k}": yhat[k] for k in ("B0", "B1", "M_spec")})
    return out, d


# ------------------------------------------------------------------------------------------------ H3 (exploratory)
def h3(y):
    g = y[y.N == 256].copy(); g["infl_nl"] = np.log10(g.ext_nl / g.err_nl); g["infl_ls"] = np.log10(g.ext_ls / g.err_ls)
    c = g.groupby("instance")[["infl_nl", "infl_ls"]].mean(); diff = (c.infl_nl - c.infl_ls).values
    r = S.wilcoxon_two_sided(diff); r.update(mean_log10_inflation_nl=float(c.infl_nl.mean()), mean_log10_inflation_ls=float(c.infl_ls.mean()),
                                              n_instances_nl_inflates_more=int((diff > 0).sum())); return r, c


# ------------------------------------------------------------------------------------------------ H4
def best_of_b(trials, b):
    t = min(trials[:b], key=lambda z: z["val"]); return t["val"], t["test"]


def trial_level_y(df, b_ls, b_nl):
    out = []
    for (inst, N, s), g in df.groupby(["instance", "N", "seed"]):
        g = g.set_index("method")
        ls = {m: best_of_b(g.loc[m, "trials"], b_ls) for m in LS}; nl = {m: best_of_b(g.loc[m, "trials"], b_nl) for m in NL}
        a = min(ls, key=lambda m: ls[m][0]); b = min(nl, key=lambda m: nl[m][0])
        out.append(dict(instance=inst, N=N, seed=s, y=float(np.log10(max(nl[b][1], 1e-300) / max(ls[a][1], 1e-300)))))
    return pd.DataFrame(out).groupby(["instance", "N"], as_index=False).y.mean()


def h4(df):
    sym8, asym, sym1 = trial_level_y(df, 8, 8), trial_level_y(df, 1, 8), trial_level_y(df, 1, 1)
    m = sym8.merge(asym, on=["instance", "N"], suffixes=("_sym", "_asym")).merge(sym1.rename(columns={"y": "y_sym1"}), on=["instance", "N"])
    nl_sym, nl_asym, nl_sym1 = m.y_sym < 0, m.y_asym < 0, m.y_sym1 < 0
    b, c = int((nl_asym & ~nl_sym).sum()), int((~nl_asym & nl_sym).sum())
    H4a = S.mcnemar_exact_greater(b, c); H4a.update(n_cells=int(len(m)), nl_win_rate_sym8=float(nl_sym.mean()), nl_win_rate_asym=float(nl_asym.mean()), nl_win_rate_sym1=float(nl_sym1.mean()))
    flips = int((nl_sym1 != nl_sym).sum()); H4b = dict(n_cells=int(len(m)), winner_flips_b1_vs_b8=flips, frac=float(flips / len(m)))
    ci = S.stats.binomtest(flips, len(m)).proportion_ci(0.95, method="wilson"); H4b["wilson95"] = [float(ci.low), float(ci.high)]
    # method-ranking stability: Kendall tau between ranking at b and at b=8 (per instance, N; mean over seeds of trial-level test error)
    taus = {}
    for b_ in (1, 2, 4):
        t = []
        for (inst, N), g in df.groupby(["instance", "N"]):
            e_b = [np.mean([best_of_b(r.trials, b_)[1] for r in g[g.method == mm].itertuples()]) for mm in METHODS]
            e_8 = [np.mean([best_of_b(r.trials, 8)[1] for r in g[g.method == mm].itertuples()]) for mm in METHODS]
            t.append(S.kendall_tau(e_b, e_8))
        taus[f"b={b_}"] = dict(mean_tau=float(np.nanmean(t)), min_tau=float(np.nanmin(t)))
    H4b["kendall_tau_vs_b8"] = taus
    curve = {}
    for bl, bn in [(1, 1), (2, 2), (4, 4), (8, 8), (1, 8)]:
        curve[f"LS_b{bl}_NL_b{bn}"] = float((trial_level_y(df, bl, bn).y < 0).mean())
    H4b["nl_win_rate_by_budget"] = curve
    return H4a, H4b, m


# ------------------------------------------------------------------------------------------------ descriptive
def learning_curves(df):
    g = df.groupby(["instance", "method", "N"]).err.agg(["mean", "std", "count"]).reset_index()
    exps = []
    for (inst, m), h in g.groupby(["instance", "method"]):
        h = h[h.N >= 64]; k = np.polyfit(np.log10(h.N), np.log10(h["mean"]), 1)[0]; exps.append(dict(instance=inst, method=m, exponent=float(k)))
    return g, pd.DataFrame(exps)


def selection_regret(y): return dict(mean_abs_gap_y_vs_oracle=float((y.y - y.y_oracle).abs().mean()), frac_same_sign=float((np.sign(y.y) == np.sign(y.y_oracle)).mean()))


def cost_table(df, ft):
    fom = ft.groupby("instance").fom_s.mean(); d = df[df.N.isin([64, 256, 1024])].groupby(["instance", "method", "N"])[["t_fit", "t_hpo", "t_inf", "err"]].mean().reset_index()
    d["fom_s"] = d.instance.map(fom); rows = []
    for mult in (1, 10, 100, 1000):
        offline = d.N * d.fom_s * mult + d.t_hpo + d.t_fit; dt = d.fom_s * mult - d.t_inf
        d[f"breakeven_N_x{mult}"] = np.where(dt > 0, offline / dt, np.inf)
    return d


def method_win_table(df):
    d = df.copy(); d["rank"] = d.groupby(["instance", "N", "seed"]).err.rank(); w = d[d["rank"] == 1].groupby(["N", "method"]).size().unstack(fill_value=0)
    return w.reindex(columns=METHODS, fill_value=0)


# ------------------------------------------------------------------------------------------------ main
def main(raw_dir, out_dir, quick=False, cache_dir=None):
    out = pathlib.Path(out_dir or pathlib.Path(raw_dir).parent); (out / "tables").mkdir(parents=True, exist_ok=True)
    df, ft, seeds = load(raw_dir); y = family_y(df); cells = cell_table(y, ft)
    flat = df.drop(columns=["trials"]); flat.to_csv(out / "raw_results.csv", index=False); y.to_csv(out / "tables" / "family_winner_y.csv", index=False); cells.to_csv(out / "tables" / "cells.csv", index=False)
    stats = dict(protocol="v1.0", quick=quick, seeds_used=[int(s) for s in seeds], n_instances=int(df.instance.nunique()), n_families=int(df.family.nunique()))
    if quick:
        stats["note"] = "QUICK MODE — pipeline check only; NOT scientific evidence"; (out / "statistics.json").write_text(json.dumps(stats, indent=1)); print(stats); return
    H1a, H1b = h1(cells); H2, h2cells = h2(cells); H3, h3c = h3(y); H4a, H4b, h4cells = h4(df)
    ps = {"H1a": H1a["p"], "H1b": H1b["p"], "H2": H2["primary_M_spec_vs_B1"]["p"], "H4a": H4a["p"]}
    hol = S.holm(ps); stats.update(H1a=H1a, H1b=H1b, H2=H2, H3_exploratory=H3, H4a=H4a, H4b_descriptive=H4b,
                                   holm={k: dict(adjusted_p=v[0], reject_alpha05=bool(v[1])) for k, v in hol.items()}, selection_regret=selection_regret(y))
    lc, ex = learning_curves(df); lc.to_csv(out / "tables" / "learning_curves.csv", index=False); ex.to_csv(out / "tables" / "learning_curve_exponents.csv", index=False)
    cost_table(df, ft).to_csv(out / "tables" / "cost_breakeven.csv", index=False); method_win_table(df).to_csv(out / "tables" / "method_wins_by_N.csv")
    h2cells.to_csv(out / "tables" / "h2_lofo_predictions.csv", index=False); h3c.to_csv(out / "tables" / "h3_inflation.csv"); h4cells.to_csv(out / "tables" / "h4_cells.csv", index=False)
    ft.to_csv(out / "tables" / "pilot_features.csv", index=False)
    (out / "statistics.json").write_text(json.dumps(stats, indent=1, default=float))
    summ = dict(n_rows=int(len(df)), median_err_by_N_method=df.groupby(["N", "method"]).err.median().unstack().round(6).to_dict(), nl_win_rate_by_N=cells.groupby("N").nl_wins.mean().round(3).to_dict())
    (out / "metrics.json").write_text(json.dumps(summ, indent=1, default=float)); print(json.dumps(stats["holm"], indent=1))
