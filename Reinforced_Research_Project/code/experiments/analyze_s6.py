#!/usr/bin/env python3
"""Stage 6 analysis (protocol_addendum_v3.0.md, criteria fixed BEFORE the runs). Reads results/raw_exp6T (legacy five methods), raw_exp6C (SurroSelect), raw_exp6S (strong tuned network).
Writes results/s6/*.json and tp_cells.csv. Wilson / bootstrap intervals; Holm-adjusted exact binomial tests against the thresholds."""
import json, glob, pathlib, sys, numpy as np, pandas as pd
from scipy import stats as sps
ROOT = pathlib.Path(__file__).resolve().parents[2]; R = ROOT / "results"; OUT = R / "s6"; OUT.mkdir(exist_ok=True)
sys.path.insert(0, str(ROOT / "code/src")); from surrogate_bench import analysis as A
LEG = ["pod_gp", "pod_poly", "pod_mlp", "mlp_direct", "bottleneck"]; RNG = np.random.default_rng(0)


def wilson(k, n, z=1.96):
    if n == 0: return (np.nan, np.nan)
    p = k / n; d = 1 + z * z / n; c = (p + z * z / (2 * n)) / d; h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d; return (c - h, c + h)
def boot_ci(x, f=np.median, B=2000):
    x = np.asarray(x, float); return tuple(np.percentile([f(RNG.choice(x, len(x))) for _ in range(B)], [2.5, 97.5]))


def load_C():
    rows = []
    for f in sorted(glob.glob(str(R / "raw_exp6C/*__s*.json"))):
        m = json.load(open(f))
        for r in m["records"]: rows.append(dict(instance=m["instance"], seed=m["seed"], p=m["p"], N=r["N"], rec=r))
    return rows


def main():
    # ---------- T: legacy methods on the new problems
    dfT, ftT, seedsT = A.load(R / "raw_exp6T"); y = A.family_y(dfT); cT = y.groupby(["instance", "family", "p", "N"], as_index=False).agg(y=("y", "mean")); cT.to_csv(OUT / "tp_cells.csv", index=False)
    cl = lambda v: "LS" if v > .1 else ("NL" if v < -.1 else "tie")
    t1024 = cT[cT.N == 1024]; nLS = int(sum(cl(v) == "LS" for v in t1024.y)); n_inst = int(t1024.instance.nunique())
    PT = dict(n_ls_clear=nLS, n_problems=n_inst, criterion_met=bool(nLS >= 5), classes_1024={r.instance: cl(r.y) for r in t1024.itertuples()}, y_1024={r.instance: float(r.y) for r in t1024.itertuples()}, seeds=[int(s) for s in seedsT])
    json.dump(PT, open(OUT / "PT.json", "w"), indent=1)
    # legacy per-seed errors and validation-selected method
    leg = dfT.copy(); idx = leg.groupby(["instance", "N", "seed"]).val.idxmin(); sel_leg = leg.loc[idx][["instance", "N", "seed", "method", "err"]].rename(columns={"err": "err_leg_sel", "method": "leg_method"})
    pg = leg[leg.method == "pod_gp"][["instance", "N", "seed", "err"]].rename(columns={"err": "err_leg_gp"})
    # ---------- C: tool
    rows = load_C()
    if not rows: json.dump(PT, open(OUT / "PT.json", "w")); print("no C results yet"); return
    recs = []
    for r in rows:
        rr = r["rec"]; sel = rr["selected"]; te = rr["test_err"]; best = min(te.values()); recs.append(dict(instance=r["instance"], seed=r["seed"], N=r["N"], selected=sel, err_sel=te[sel], err_oracle=best, oracle=min(te, key=te.get),
            err_gp_best=min(v for k, v in te.items() if k.startswith("pod_gp")), err_full=min([v for k, v in te.items() if k.startswith("gp_full")] or [np.nan]), err_pod_best=min(v for k, v in te.items() if k.startswith("pod_")),
            basis_limited=bool(rr["floor"]["basis_limited"]), floor=rr["floor"]["pod_floor_cv"], sec_fit=rr["seconds_fit"], sec_total=rr["seconds_total"], n_ties=len(rr["ties"]), pred=rr["pred_err_4N"].get(str(4 * r["N"]), [np.nan] * 3), curve=rr["curve"], te=te,
            rn1=rr["runs_needed_1pct"], rn01=rr["runs_needed_01pct"]))
    C = pd.DataFrame(recs); C = C.merge(sel_leg, on=["instance", "N", "seed"], how="left").merge(pg, on=["instance", "N", "seed"], how="left"); C.to_pickle(OUT / "C_records.pkl")
    cell = C.groupby(["instance", "N"]).apply(lambda g: pd.Series(dict(sel=np.exp(np.log(g.err_sel).mean()), orc=np.exp(np.log(g.err_oracle).mean()), leg_gp=np.exp(np.log(g.err_leg_gp).mean()), leg_sel=np.exp(np.log(g.err_leg_sel).mean()),
                                                                       full=np.exp(np.log(g.err_full).mean()), podb=np.exp(np.log(g.err_pod_best).mean())))).reset_index()
    cell["regret"] = cell["sel"] / cell.orc; cell["r_gp"] = cell["sel"] / cell.leg_gp; cell["r_leg"] = cell["sel"] / cell.leg_sel; ncell = len(cell)
    S1 = dict(n_cells=ncell, median_regret=float(cell.regret.median()), median_ci=boot_ci(cell.regret), share_le2=float((cell.regret <= 2).mean()), wilson_le2=wilson(int((cell.regret <= 2).sum()), ncell), criterion_met=bool(cell.regret.median() <= 1.5 and (cell.regret <= 2).mean() >= .75),
              per_N={int(N): dict(median=float(g.regret.median())) for N, g in cell.groupby("N")})
    # null model: picking a pool member uniformly at random (no information); expected regret per cell from the same test errors
    nulls = []
    for (inst, N), g in C.groupby(["instance", "N"]):
        mem = sorted(set().union(*[set(t.keys()) for t in g.te])); ge = {m_: np.exp(np.mean([np.log(t[m_]) for t in g.te if m_ in t])) for m_ in mem}; mn = min(ge.values()); nulls.append(np.mean([v / mn for v in ge.values()]))
    S1["null_random_pick_median_regret"] = float(np.median(nulls)); S1["null_random_pick_share_le2"] = float(np.mean(np.array(nulls) <= 2))
    S2 = dict(median_ratio=float(cell.r_gp.median()), ci=boot_ci(cell.r_gp), criterion_met=bool(cell.r_gp.median() <= 1.0), n_better=int((cell.r_gp < 0.9).sum()), n_worse=int((cell.r_gp > 1.1).sum()))
    S3 = dict(median_ratio=float(cell.r_leg.median()), ci=boot_ci(cell.r_leg), n_better_10pct=int((cell.r_leg < 1 / 1.1).sum()), n_worse_10pct=int((cell.r_leg > 1.1).sum()))
    S3["criterion_met"] = bool(S3["median_ratio"] <= 1.0 and S3["n_better_10pct"] > S3["n_worse_10pct"])
    # ---------- B1/B2
    bc = []
    for (inst, seed), g in C.groupby(["instance", "seed"]):
        g = g.set_index("N")
        for N0 in (64, 256):
            if N0 in g.index and 4 * N0 in g.index:
                name = g.loc[N0, "selected"]; act = g.loc[4 * N0, "te"].get(name, np.nan); pr = g.loc[N0, "pred"]; bc.append(dict(instance=inst, seed=seed, N0=N0, cand=name, pred=pr[0], lo=min(pr[1], pr[2]), hi=max(pr[1], pr[2]), actual=act))
    B = pd.DataFrame(bc); B["logratio"] = np.log10(B.pred / B.actual); B["within2"] = B.logratio.abs() <= np.log10(2); B["in_band"] = (B.actual >= B.lo) & (B.actual <= B.hi)
    n = len(B); k = int(B.within2.sum()); B1 = dict(n_cases=n, n_within_factor2=k, share=k / max(n, 1), wilson=wilson(k, n), criterion_met=bool(n and k / n >= .7), share_in_band=float(B.in_band.mean()) if n else None, median_abs_log10=float(B.logratio.abs().median()) if n else None,
                                                  bias_median_log10=float(B.logratio.median()) if n else None, by_N0={int(N0): dict(n=int(len(g)), share=float(g.within2.mean())) for N0, g in B.groupby("N0")}, p_binom_vs_70=float(sps.binomtest(k, n, 0.7, alternative="greater").pvalue) if n else None)
    B1["n_under_factor2"] = int((B.logratio < -np.log10(2)).sum()); B1["n_over_factor2"] = int((B.logratio > np.log10(2)).sum()); B1["n_within2_N256"] = int(B[B.N0 == 256].within2.sum()); B1["n_under_N256"] = int((B[B.N0 == 256].logratio < -np.log10(2)).sum())
    B.to_csv(OUT / "B1_cases.csv", index=False)
    b2 = {}
    for thr, nm in ((0.01, "one_pct"), (0.001, "tenth_pct")):
        c2 = B[B.N0 == 256]; pred_ok = c2.pred <= thr; act_ok = c2.actual <= thr; acc = float((pred_ok == act_ok).mean()) if len(c2) else None; kk = int((pred_ok == act_ok).sum()); b2[nm] = dict(n=int(len(c2)), accuracy=acc, wilson=wilson(kk, len(c2)), criterion_met=bool(acc is not None and acc >= .75), actual_reached=int(act_ok.sum()), predicted_reached=int(pred_ok.sum()), majority_baseline=float(max(act_ok.mean(), 1 - act_ok.mean())) if len(c2) else None)
    # ---------- ablation (analysis-only on stored outputs): pool restricted, selection by the stored CV errors, test error of the CV-best member of the subset
    def subset_err(g, pred):
        out = []
        for _, r in g.iterrows():
            cvt = {t["name"]: t["cv_error"] for t in rows_cv[(r.instance, r.seed, r.N)] if pred(t["name"]) and np.isfinite(t["cv_error"])}
            out.append(r.te[min(cvt, key=cvt.get)] if cvt else np.nan)
        return np.array(out, float)
    rows_cv = {(r["instance"], r["seed"], r["N"]): r["rec"]["cv_table"] for r in rows}
    subsets = {"full pool": lambda n: True, "POD-based members only": lambda n: n.startswith("pod_"), "no full-field GP": lambda n: not n.startswith("gp_full"), "GP members only": lambda n: "gp" in n, "no GP (ridge, polynomial)": lambda n: not ("gp" in n)}
    ABL = {}
    for nm, pr in subsets.items():
        e = subset_err(C, pr); d = C.assign(e=e); ce = d.groupby(["instance", "N"]).apply(lambda g: np.exp(np.nanmean(np.log(g.e)))); orc = C.groupby(["instance", "N"]).apply(lambda g: np.exp(np.log(g.err_oracle).mean()))
        full = cell.set_index(["instance", "N"])["sel"]; ABL[nm] = dict(median_regret=float((ce / orc).median()), median_ratio_to_full_pool=float((ce / full).median()), share_regret_le2=float(((ce / orc) <= 2).mean()))
    json.dump(ABL, open(OUT / "ablation.json", "w"), indent=1)
    # ---------- F1
    fl = C[C.basis_limited]; F1 = dict(n_flagged_cells=int(len(fl)), evaluable=bool(len(fl) >= 5))
    if len(fl): ok = (fl.err_full < fl.err_pod_best / 1.1); F1.update(share_full_better=float(ok.mean()), n_ok=int(ok.sum()), wilson=wilson(int(ok.sum()), len(fl)), criterion_met=bool(len(fl) >= 5 and ok.mean() >= .75), flagged_instances=sorted(set(fl.instance)))
    # ---------- S4 strong NN
    S4 = None; srows = []
    for f in sorted(glob.glob(str(R / "raw_exp6S/*__s*.json"))):
        m = json.load(open(f))
        for r in m["records"]: srows.append(dict(instance=m["instance"], seed=m["seed"], N=r["N"], err_strong=r["test_err"], params=r["best_params"], seconds=r["seconds"]))
    if srows:
        Sd = pd.DataFrame(srows).merge(C[["instance", "seed", "N", "err_sel", "err_leg_sel", "selected"]], on=["instance", "seed", "N"]); Sd.to_pickle(OUT / "S_records.pkl")
        sc = Sd.groupby(["instance", "N"]).apply(lambda g: pd.Series(dict(strong=np.exp(np.log(g.err_strong).mean()), tool=np.exp(np.log(g.err_sel).mean()), leg=np.exp(np.log(g.err_leg_sel).mean())))).reset_index(); sc["ratio_tool_over_strong"] = sc.tool / sc.strong
        nb = int((sc.strong < sc.tool / 1.25).sum()); S4 = dict(n_cells=int(len(sc)), strong_better_by_25pct=nb, wilson=wilson(nb, len(sc)), criterion_met=bool(nb <= 4), median_ratio_tool_over_strong=float(sc.ratio_tool_over_strong.median()), n_tool_better_10pct=int((sc.ratio_tool_over_strong < 1 / 1.1).sum()), n_strong_better_10pct=int((sc.ratio_tool_over_strong > 1.1).sum()),
                                                                                  median_seconds_strong={int(N): float(g.seconds.median()) for N, g in Sd.groupby("N")}); sc.to_csv(OUT / "S4_cells.csv", index=False)
    # ---------- costs
    K = dict(median_fit_seconds={int(N): float(g.sec_fit.median()) for N, g in C.groupby("N")}, median_total_seconds={int(N): float(g.sec_total.median()) for N, g in C.groupby("N")})
    # holm over exact binomial tests against thresholds
    tests = {}
    tests["S1_share_le2_vs_75"] = float(sps.binomtest(int((cell.regret <= 2).sum()), ncell, 0.75, alternative="greater").pvalue)
    if n: tests["B1_vs_70"] = B1["p_binom_vs_70"]
    if S4: tests["S4_strong_wins_vs_25pct"] = float(sps.binomtest(S4["strong_better_by_25pct"], S4["n_cells"], 0.25, alternative="less").pvalue)
    ps = sorted(tests.items(), key=lambda kv: kv[1]); m_ = len(ps); holm = {}; run = 0
    for i, (k_, p_) in enumerate(ps): run = max(run, min(1, (m_ - i) * p_)); holm[k_] = dict(p=p_, holm_adj=run)
    out = dict(PT=PT, S1=S1, S2=S2, S3=S3, B1=B1, B2=b2, F1=F1, S4=S4, K=K, holm=holm, n_C_records=int(len(C)))
    json.dump(out, open(OUT / "criteria.json", "w"), indent=1, default=float); cell.to_csv(OUT / "S1_cells.csv", index=False); print(json.dumps({k: (v if k not in ("PT",) else {"n_ls_clear": v["n_ls_clear"]}) for k, v in out.items() if k in ("S1", "S2", "S3", "B1", "F1", "S4", "PT")}, indent=1, default=float)[:3500])


if __name__ == "__main__": main()
