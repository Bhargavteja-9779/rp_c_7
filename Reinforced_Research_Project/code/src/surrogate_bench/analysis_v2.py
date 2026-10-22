"""Pre-specified v2 analyses (see research_design/revised_experimental_protocol.md). Frozen rules come from research_design/frozen_rules_from_v1.json."""
from __future__ import annotations
import json, glob, itertools, pathlib, math, numpy as np, pandas as pd
from scipy import stats as sps
from . import analysis as A, stats as S


def frozen(path): return json.load(open(path))
def _pred(spec, X): return ((np.asarray(X) - np.array(spec["mu"])) / np.array(spec["sd"])) @ np.array(spec["beta"]) + spec["ym"]


def perm_spearman_neg(x, y):
    """Exact one-sided permutation test for Spearman rho (alternative: rho < 0), all n! permutations (n<=9)."""
    n = len(x); rx = sps.rankdata(x); ry = sps.rankdata(y); obs = sps.pearsonr(rx, ry)[0]; cnt = tot = 0
    if n <= 9:                                                   # exact enumeration (the pre-registered case: n = 8 new instances)
        for p in itertools.permutations(range(n)):
            r = np.corrcoef(rx, ry[list(p)])[0, 1]; tot += 1; cnt += r <= obs + 1e-12
        return dict(rho=float(obs), p=float(cnt / tot), n=n, exact=True)
    rng = np.random.default_rng(0)                               # Monte Carlo fallback (plumbing / pooled use only)
    for _ in range(20000):
        r = np.corrcoef(rx, ry[rng.permutation(n)])[0, 1]; tot += 1; cnt += r <= obs + 1e-12
    return dict(rho=float(obs), p=float((cnt + 1) / (tot + 1)), n=n, exact=False)


def primary_tests(cells, fz, n_boot=10000, seed=0):
    """P1: Spearman(f1, ybar) at N=1024 over new instances (exact perm, one-sided <0). P2: out-of-sample squared-error gain of frozen R2 over frozen B0 (cluster bootstrap by instance)."""
    c = cells[cells.N == 1024].sort_values("instance"); P1 = perm_spearman_neg(c.log_cv_err_r4.values, c.y.values)
    d = cells[cells.N.isin([64, 128, 256, 512, 1024])].sort_values(["instance", "N"]).reset_index(drop=True); lg = np.log2(d.N.values)
    r2 = _pred(fz["R2"], np.c_[lg, d.log_cv_err_r4.values]); b0 = _pred(fz["B0"], lg[:, None]); gain = (d.y.values - b0) ** 2 - (d.y.values - r2) ** 2
    inst = d.instance.values; U = np.unique(inst); idx = {u: np.where(inst == u)[0] for u in U}; rng = np.random.default_rng(seed); boot = np.empty(n_boot)
    for b in range(n_boot): boot[b] = gain[np.concatenate([idx[u] for u in rng.choice(U, len(U), replace=True)])].mean()
    P2 = dict(mean_sq_error_gain=float(gain.mean()), ci95=[float(np.percentile(boot, 2.5)), float(np.percentile(boot, 97.5))], p=float((np.sum(boot <= 0) + 1) / (n_boot + 1)),
              rmse_B0=float(np.sqrt(np.mean((d.y.values - b0) ** 2))), rmse_R2=float(np.sqrt(np.mean((d.y.values - r2) ** 2))), n_cells=int(len(d)), n_instances=int(len(U)))
    return P1, P2


def secondary(cells, y, fz):
    tie = fz["tie_band"]; c = cells[cells.N.isin([256, 1024]) & (cells.y.abs() >= tie)].copy(); R1 = fz["R1"]
    pred_nl = c.log_cv_err_r4 > R1["t"]; acc = float(np.mean(pred_nl == (c.y < 0))) if len(c) else float("nan"); k = int(np.sum(pred_nl == (c.y < 0)))
    S1 = dict(n_nontie_cells=int(len(c)), correct=k, accuracy=acc, p0_v1_majority=R1["v1_majority_share"], p_binom_one_sided=float(sps.binomtest(k, len(c), R1["v1_majority_share"], alternative="greater").pvalue) if len(c) else None,
              new_data_majority_share=float(max((c.y < 0).mean(), (c.y >= 0).mean())) if len(c) else None)
    ties = {int(N): dict(ls_clear=int((g.y > tie).sum()), nl_clear=int((g.y < -tie).sum()), tie=int((g.y.abs() <= tie).sum())) for N, g in cells.groupby("N")}
    cons = y.groupby(["instance", "N"]).y.agg(lambda v: abs(np.sign(v).sum()) == len(v)).mean()
    return S1, dict(by_N=ties, seed_sign_consistency=float(cons), tie_band=tie)


def pooled_lofo(cells_all, n_boot=10000):
    d = cells_all[cells_all.N.isin([64, 128, 256, 512, 1024])].sort_values(["instance", "N"]).reset_index(drop=True); y, g = d.y.values, d.family.values; lg = np.log2(d.N.values)
    des = dict(B0=np.c_[lg], B1log=np.c_[lg, np.log2(d.p.values)], M_cv4=np.c_[lg, d.log_cv_err_r4.values], M_spec=np.c_[lg, d.log_cv_err_r4.values, d.slope.values])
    res = {k: S.lofo_residuals(X, y, g) for k, X in des.items()}; out = dict(n_cells=int(len(d)), n_families=int(len(np.unique(g))), rmse={k: float(np.sqrt(np.mean(v**2))) for k, v in res.items()})
    for k in ("M_cv4", "M_spec"): out[f"{k}_vs_B0"] = S.cluster_bootstrap_rmse_diff(res["B0"], res[k], g, n_boot); out[f"{k}_vs_B1log"] = S.cluster_bootstrap_rmse_diff(res["B1log"], res[k], g, n_boot)
    return out


def expB(dir_B, df_all):
    rows = []
    for f in glob.glob(str(pathlib.Path(dir_B) / "*.json")): rows += json.load(open(f))
    b = pd.DataFrame(rows); out = []
    for (inst, s, N), g in b.groupby(["instance", "seed", "N"]):
        r = df_all[(df_all.instance == inst) & (df_all.seed == s) & (df_all.N == N)].set_index("method").err
        ls1500 = r[["pod_gp", "pod_poly", "pod_mlp"]].min(); nl1500 = r[["mlp_direct", "bottleneck"]].min()
        e6 = g.set_index("method").err_6000; ls6 = min(r[["pod_gp", "pod_poly"]].min(), e6["pod_mlp"]); nl6 = e6[["mlp_direct", "bottleneck"]].min()
        out.append(dict(instance=inst, seed=s, N=N, y1500=math.log10(nl1500 / ls1500), y6000=math.log10(nl6 / ls6)))
    o = pd.DataFrame(out); c = o.groupby(["instance", "N"], as_index=False)[["y1500", "y6000"]].mean()
    # SIGN CONVENTION (fixed after independent audit F1, before Exp B was analysed): y = log10(err_NL/err_LS), so NL improving makes y SMALLER.
    # shift_toward_NL = y1500 - y6000 is POSITIVE when longer training moves the comparison toward the NL family; criterion B2 is median(shift_toward_NL) < 0.5.
    c["shift_toward_NL"] = c.y1500 - c.y6000; c["shift"] = c.shift_toward_NL
    clear = c[c.y1500.abs() >= 0.10]; kept = float((np.sign(clear.y1500) == np.sign(clear.y6000)).mean()) if len(clear) else float("nan")
    nn_improved = float((b.err_6000 < b.err_1500).mean()); ratio = float((b.err_6000 / b.err_1500).median())
    return dict(n_cells=int(len(c)), n_clear_cells=int(len(clear)), sign_retention_clear_cells=kept, median_shift_toward_NL=float(c["shift_toward_NL"].median()), mean_shift_toward_NL=float(c["shift_toward_NL"].mean()), max_shift_toward_NL=float(c["shift_toward_NL"].max()), max_abs_shift=float(c["shift_toward_NL"].abs().max()), B1_pass=bool(kept >= 0.85), B2_pass=bool(c["shift_toward_NL"].median() < 0.5),
                share_fits_improved=nn_improved, median_err_ratio_6000_vs_1500=ratio, frac_cells_LS_still_better_when_clear_ls=float((clear[clear.y1500 > 0].y6000 > 0).mean()) if (clear.y1500 > 0).any() else None), c


def expD(dir_D, df_all, tie=0.10):
    rows = []
    for f in glob.glob(str(pathlib.Path(dir_D) / "*__s*.json")):
        m = json.load(open(f)); rows += [dict(instance=m["instance"], seed=m["seed"], N=r["N"], err_krr=r["test_err"]) for r in m["records"]]
    kk = pd.DataFrame(rows); assert set(kk.seed.unique()) == set(df_all.seed.unique()), "Exp D seeds must match the seeds in df_all"
    k = kk.groupby(["instance", "N"], as_index=False).err_krr.mean()
    g = df_all[df_all.method == "pod_gp"].groupby(["instance", "N"], as_index=False).err.mean().rename(columns={"err": "err_gp"})
    nl = df_all[df_all.method.isin(["mlp_direct", "bottleneck"])].groupby(["instance", "N", "method"]).err.mean().groupby(["instance", "N"]).min().rename("err_nl_best").reset_index()
    t = k.merge(g, on=["instance", "N"]).merge(nl, on=["instance", "N"]); t["ratio_krr_gp"] = t.err_krr / t.err_gp; t["y_gp"] = np.log10(t.err_nl_best / t.err_gp); t["y_krr"] = np.log10(t.err_nl_best / t.err_krr)
    sel = t[t.y_gp > tie]; out = dict(n_cells=int(len(t)), n_gp_clear_win_cells=int(len(sel)), median_ratio_krr_over_gp_all=float(t.ratio_krr_gp.median()),
                                    median_ratio_in_gp_clear_win_cells=float(sel.ratio_krr_gp.median()) if len(sel) else None, share_ratio_le3_in_gp_clear_win_cells=float((sel.ratio_krr_gp <= 3).mean()) if len(sel) else None,
                                    share_krr_beats_nl_where_gp_clear_win=float((sel.y_krr > 0).mean()) if len(sel) else None, share_krr_better_than_gp_all=float((t.ratio_krr_gp < 1).mean()))
    out["D1_supported(median<=3 and share<=3 >=0.75)"] = bool(len(sel) and out["median_ratio_in_gp_clear_win_cells"] <= 3 and out["share_ratio_le3_in_gp_clear_win_cells"] >= 0.75); return out, t


def run_all(res_dir, dirA, dirB, dirD, fz_path, v1_raw, out_dir):
    out = pathlib.Path(out_dir); (out / "tables").mkdir(parents=True, exist_ok=True); fz = frozen(fz_path); report = {}
    dfA, ftA, seedsA = A.load(dirA); yA = A.family_y(dfA); cA = A.cell_table(yA, ftA); cA.to_csv(out / "tables/expA_cells.csv", index=False)
    P1, P2 = primary_tests(cA, fz); S1, S2 = secondary(cA, yA, fz); hol = S.holm(dict(P1=P1["p"], P2=P2["p"]))
    report["expA"] = dict(seeds=[int(s) for s in seedsA], n_instances=int(dfA.instance.nunique()), P1=P1, P2=P2, holm={k: dict(adj_p=v[0], reject=bool(v[1])) for k, v in hol.items()}, S1=S1, S2=S2,
                          nl_win_rate_by_N={int(N): float((g.y < 0).mean()) for N, g in cA.groupby("N")})
    dfO, ftO, seedsO = A.load(v1_raw); yO = A.family_y(dfO); cO = A.cell_table(yO, ftO); call = pd.concat([cO, cA], ignore_index=True)
    report["pooled_24_instances_exploratory"] = pooled_lofo(call); call.to_csv(out / "tables/pooled_cells.csv", index=False)
    if dirB and pathlib.Path(dirB).exists() and glob.glob(str(pathlib.Path(dirB) / "*.json")):
        dfall = pd.concat([dfO, dfA], ignore_index=True); rb, tb = expB(dirB, dfall); report["expB"] = rb; tb.to_csv(out / "tables/expB_cells.csv", index=False)
    if dirD and pathlib.Path(dirD).exists() and glob.glob(str(pathlib.Path(dirD) / "*__s*.json")):
        dfall = pd.concat([dfO, dfA], ignore_index=True); rd, td = expD(dirD, dfall); report["expD"] = rd; td.to_csv(out / "tables/expD_cells.csv", index=False)
    (out / "statistics_v2.json").write_text(json.dumps(report, indent=1, default=float)); return report


# ---------------------------------------------------------------------------------------------- v2.1 follow-ups (pre-registered in protocol_addendum_v2.1.md)
def expA2(dir_A2, sel_path, p0=0.10):
    sel = json.load(open(sel_path)); df, ft, seeds = A.load(dir_A2); y = A.family_y(df); c = A.cell_table(y, ft); g = c[c.N == 1024].set_index("instance")
    qual = sel["qualifying"]; yq = g.loc[qual, "y"]; k = int((yq >= 1.0).sum()); n = len(qual)
    Q1 = dict(n_qualifying=n, k_decisive_ge_1dec=k, p_binom_vs_p0=float(sps.binomtest(k, n, p0, alternative="greater").pvalue), p0=p0, success=bool(sps.binomtest(k, n, p0, alternative="greater").pvalue < 0.05))
    Q2 = dict(n_qualifying_with_NL_clear_win=int((yq < -0.10).sum()), success=bool((yq >= -0.10).all()))
    ctrl = {i: float(g.loc[i, "y"]) for i in g.index if i not in qual}
    return dict(seeds=[int(s) for s in seeds], Q1=Q1, Q2=Q2, y_N1024_qualifying={i: round(float(v), 3) for i, v in yq.items()}, control_instances_y_N1024=ctrl,
                f1_by_instance={i: round(float(g.loc[i, "log_cv_err_r4"]), 3) for i in g.index}), c


def expE(dir_E, df_all, dir_D):
    """Compare GP-iso (this run) with GP-ARD (v1/Exp A/A2 records) and KRR (Exp D) on identical training subsets, in GP-ARD clear-win cells (N in 64,256,1024)."""
    def load(d, key):
        rows = []
        for f in glob.glob(str(pathlib.Path(d) / "*__s*.json")):
            m = json.load(open(f)); rows += [dict(instance=m["instance"], seed=m["seed"], N=r["N"], **{key: r["test_err"]}) for r in m["records"]]
        return pd.DataFrame(rows)
    iso = load(dir_E, "err_iso"); krr = load(dir_D, "err_krr")
    ard = df_all[df_all.method == "pod_gp"][["instance", "seed", "N", "err"]].rename(columns={"err": "err_ard"})
    nl = df_all[df_all.method.isin(["mlp_direct", "bottleneck"])].groupby(["instance", "seed", "N", "method"]).err.mean().groupby(["instance", "seed", "N"]).min().rename("err_nl").reset_index()
    t = iso.merge(ard, on=["instance", "seed", "N"]).merge(krr, on=["instance", "seed", "N"]).merge(nl, on=["instance", "seed", "N"])
    t = t.groupby(["instance", "N"], as_index=False)[["err_iso", "err_ard", "err_krr", "err_nl"]].mean(); t["y_ard"] = np.log10(t.err_nl / t.err_ard)
    sel = t[t.y_ard > 0.10]; r_iso_ard = sel.err_iso / sel.err_ard; r_krr_iso = sel.err_krr / sel.err_iso; q = lambda s: {k: float(v) for k, v in s.quantile([.25, .5, .75]).items()}
    out = dict(n_cells=int(len(t)), n_ard_clear_win_cells=int(len(sel)), ratio_iso_over_ard=q(r_iso_ard), ratio_krr_over_iso=q(r_krr_iso), ratio_krr_over_ard=q(sel.err_krr / sel.err_ard),
               share_iso_within3_of_ard=float((r_iso_ard <= 3).mean()), share_krr_within3_of_iso=float((r_krr_iso <= 3).mean()))
    med_ia, med_ki = out["ratio_iso_over_ard"][0.5], out["ratio_krr_over_iso"][0.5]
    out["verdict"] = "M-MLII" if (med_ki > 3 and med_ia <= 3) else ("M-ARD" if med_ia > 3 else "mixed/inconclusive"); return out, t


# ---------------------------------------------------------------------------------------------- v2.2 follow-ups (pre-registered in protocol_addendum_v2.2.md)
def expF(dir_F, df_all, decisive, thr=1.0):
    rows = []
    for f in glob.glob(str(pathlib.Path(dir_F) / "*.json")): rows += json.load(open(f))
    b = pd.DataFrame(rows); out = []
    for (inst, s, N), g in b.groupby(["instance", "seed", "N"]):
        r = df_all[(df_all.instance == inst) & (df_all.seed == s) & (df_all.N == N)].set_index("method").err; g = g.set_index("method")
        best_var = lambda m: min(g.loc[m, "err_1500"], g.loc[m, "err_f64_adam"], g.loc[m, "err_f64_lbfgs"])
        ls = min(r["pod_gp"], r["pod_poly"], best_var("pod_mlp")); nl = min(best_var("mlp_direct"), best_var("bottleneck")); nl0 = min(g.loc["mlp_direct", "err_1500"], g.loc["bottleneck", "err_1500"])
        out.append(dict(instance=inst, seed=s, N=N, y_1500=math.log10(nl0 / min(r["pod_gp"], r["pod_poly"], g.loc["pod_mlp", "err_1500"])), y_F=math.log10(nl / ls), nl_floor_1500=nl0, nl_floor_F=nl, ls_best=ls))
    o = pd.DataFrame(out); c = o.groupby(["instance", "N"], as_index=False)[["y_1500", "y_F", "nl_floor_1500", "nl_floor_F", "ls_best"]].mean(); c["improvement_decades"] = np.log10(c.nl_floor_1500 / c.nl_floor_F)
    d = c[(c.N == 1024) & c.instance.isin(decisive)]; k_decisive_remaining = int((d.y_F >= thr).sum())
    return dict(n_decisive_instances=int(len(d)), decisive_with_yF_ge_1=k_decisive_remaining, median_NL_floor_improvement_decades=float(d.improvement_decades.median()), median_y_1500=float(d.y_1500.median()), median_y_F=float(d.y_F.median()),
                verdict=("ARTIFACT (decisive advantage falls below 1 decade in >=50% of decisive instances)" if k_decisive_remaining <= len(d) / 2 - 0.5 + 0.0 and k_decisive_remaining < len(d) / 2 else ("ROBUST (>=5/7 remain >= 1 decade)" if k_decisive_remaining >= 5 else "PARTIAL")),
                min_NL_error_1500=float(c.nl_floor_1500.min()), min_NL_error_F=float(c.nl_floor_F.min())), c


def expG(dir_G, df_all, tie=0.10):
    rows = []
    for f in glob.glob(str(pathlib.Path(dir_G) / "*__s*.json")):
        m = json.load(open(f)); rows += [dict(instance=m["instance"], seed=m["seed"], N=r["N"], err_full=r["test_err"]) for r in m["records"]]
    gf = pd.DataFrame(rows); assert set(gf.seed.unique()) == set(df_all.seed.unique()); gf = gf.groupby(["instance", "N"], as_index=False).err_full.mean()
    g = df_all[df_all.method == "pod_gp"].groupby(["instance", "N"], as_index=False).err.mean().rename(columns={"err": "err_gp"})
    nl = df_all[df_all.method.isin(["mlp_direct", "bottleneck"])].groupby(["instance", "N", "method"]).err.mean().groupby(["instance", "N"]).min().rename("err_nl_best").reset_index()
    t = gf.merge(g, on=["instance", "N"]).merge(nl, on=["instance", "N"]); t["ratio_full_over_pod"] = t.err_full / t.err_gp; t["y_gp"] = np.log10(t.err_nl_best / t.err_gp); sel = t[t.y_gp > tie]
    r = sel.ratio_full_over_pod; out = dict(n_cells=int(len(t)), n_gp_clear_win_cells=int(len(sel)), ratio_quartiles={k: float(v) for k, v in r.quantile([.25, .5, .75]).items()}, share_within3=float((r <= 3).mean()), median_all_cells=float(t.ratio_full_over_pod.median()),
                                            G1_supported=bool(len(sel) and r.median() <= 3 and (r <= 3).mean() >= 0.75)); return out, t


def expA3(dir_A3, sel_path):
    sel = json.load(open(sel_path)); df, ft, seeds = A.load(dir_A3); y = A.family_y(df); c = A.cell_table(y, ft); g = c[c.N == 1024].set_index("instance")
    rows = {i: dict(p=int(sel[i]["p"]), f1=round(float(g.loc[i, "log_cv_err_r4"]), 3), y_1024=round(float(g.loc[i, "y"]), 3), decisive_ge_1=bool(g.loc[i, "y"] >= 1.0)) for i in g.index}
    return dict(seeds=[int(s) for s in seeds], instances=rows, within_p3_contrast=dict(heatmv3_L1_not_decisive=bool(not rows["heatmv3_L1"]["decisive_ge_1"]), incl3_L1_not_decisive=bool(not rows["incl3_L1"]["decisive_ge_1"])),
                darcylin_f1_ge_minus2=bool(all(rows[i]["f1"] >= -2.0 for i in rows if i.startswith("darcylin")))), c


# ---------------------------------------------------------------------------------------------- v2.3 (protocol_addendum_v2.3.md): wide-range KRR control
def expH(dir_H, df_all, key):
    rows = []
    for f in glob.glob(str(pathlib.Path(dir_H) / "*__s*.json")):
        m = json.load(open(f)); rows += [dict(instance=m["instance"], seed=m["seed"], N=r["N"], p=r["p"], **{key: r["test_err"]}) for r in m["records"]]
    h = pd.DataFrame(rows); assert set(h.seed.unique()) == set(df_all.seed.unique()); h = h.groupby(["instance", "N", "p"], as_index=False)[key].mean()
    ard = df_all[df_all.method == "pod_gp"].groupby(["instance", "N"], as_index=False).err.mean().rename(columns={"err": "err_ard"})
    nl = df_all[df_all.method.isin(["mlp_direct", "bottleneck"])].groupby(["instance", "N", "method"]).err.mean().groupby(["instance", "N"]).min().rename("err_nl_best").reset_index()
    t = h.merge(ard, on=["instance", "N"]).merge(nl, on=["instance", "N"]); t["ratio"] = t[key] / t.err_ard; t["y_ard"] = np.log10(t.err_nl_best / t.err_ard); t["y_krr"] = np.log10(t.err_nl_best / t[key])
    sel = t[t.y_ard > 0.10]; q = lambda s: {k: float(v) for k, v in s.quantile([.25, .5, .75]).items()}
    out = dict(n_cells=int(len(t)), n_ard_clear_cells=int(len(sel)), ratio_quartiles_in_ard_clear=q(sel.ratio), share_le3=float((sel.ratio <= 3).mean()), median_ratio_all_cells=float(t.ratio.median()),
               share_krr_beats_nl_clear_in_ard_clear=float((sel.y_krr > 0.10).mean()), median_ratio_by_p={int(p): float(g.ratio.median()) for p, g in sel.groupby("p")})
    return out, t
