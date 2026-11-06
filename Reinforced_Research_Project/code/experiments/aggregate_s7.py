"""Part 3 of aggregate.py: Stage 7 (results/s7, results/s7_pooled; protocol_addendum_v3.2.md). Defines macros (prefix 'sv') and tables."""
import json, pathlib, numpy as np, pandas as pd


def part3(ag):
    R, mac, fi, fc, fd, fp, fs, fx, tex_table = ag.R, ag.mac, ag.fi, ag.fc, ag.fd, ag.fp, ag.fs, ag.fx, ag.tex_table; S7, SP, S6 = R / "s7", R / "s7_pooled", R / "s6"
    pm = lambda met: "met" if met else "not met"
    if not (S7 / "criteria.json").exists(): return
    C7, CP, C6 = (json.load(open(d / "criteria.json")) for d in (S7, SP, S6)); X7 = json.load(open(S7 / "extras.json")); XP = json.load(open(SP / "extras.json"))
    # ---------------------------------------------------------------- held-out confirmation on the 8 new problems
    for tag, C, X in (("sv", C7, X7), ("svp", CP, XP)):
        s1, s2, s3, b1, f1, s4, pt = C["S1"], C["S2"], C["S3"], C["B1"], C["F1"], C["S4"], C["PT"]
        mac(f"{tag}_pt_k", fc(pt["n_ls_clear"])); mac(f"{tag}_pt_n", fc(pt["n_problems"])); mac(f"{tag}_pt_verdict", pm(pt["criterion_met"]))
        mac(f"{tag}_sone_n", fi(s1["n_cells"])); mac(f"{tag}_sone_median", fd(s1["median_regret"], 2)); mac(f"{tag}_sone_max", fd(s1["max_regret"], 1)); mac(f"{tag}_sone_lo", fd(s1["median_ci"][0], 2)); mac(f"{tag}_sone_hi", fd(s1["median_ci"][1], 2))
        mac(f"{tag}_sone_share", fp(s1["share_le2"])); mac(f"{tag}_sone_slo", fp(s1["wilson_le2"][0])); mac(f"{tag}_sone_shi", fp(s1["wilson_le2"][1])); mac(f"{tag}_sone_verdict", pm(s1["criterion_met"]))
        mac(f"{tag}_sone_null", fd(s1["null_random_pick_median_regret"], 2)); mac(f"{tag}_sone_nullshare", fp(s1["null_random_pick_share_le2"]))
        mac(f"{tag}_stwo_median", fd(s2["median_ratio"], 2)); mac(f"{tag}_stwo_lo", fd(s2["ci"][0], 2)); mac(f"{tag}_stwo_hi", fd(s2["ci"][1], 2)); mac(f"{tag}_stwo_better", fi(s2["n_better"])); mac(f"{tag}_stwo_worse", fi(s2["n_worse"])); mac(f"{tag}_stwo_verdict", pm(s2["criterion_met"]))
        mac(f"{tag}_sthree_median", fd(s3["median_ratio"], 2)); mac(f"{tag}_sthree_lo", fd(s3["ci"][0], 2)); mac(f"{tag}_sthree_hi", fd(s3["ci"][1], 2)); mac(f"{tag}_sthree_better", fi(s3["n_better_10pct"])); mac(f"{tag}_sthree_worse", fi(s3["n_worse_10pct"])); mac(f"{tag}_sthree_verdict", pm(s3["criterion_met"]))
        mac(f"{tag}_bone_n", fi(b1["n_cases"])); mac(f"{tag}_bone_k", fi(b1["n_within_factor2"])); mac(f"{tag}_bone_share", fp(b1["share"])); mac(f"{tag}_bone_lo", fp(b1["wilson"][0])); mac(f"{tag}_bone_hi", fp(b1["wilson"][1])); mac(f"{tag}_bone_verdict", pm(b1["criterion_met"]))
        mac(f"{tag}_bone_under", fi(b1["n_under_factor2"])); mac(f"{tag}_bone_over", fi(b1["n_over_factor2"])); mac(f"{tag}_bone_bias", fd(10 ** b1["bias_median_log10"], 2)); mac(f"{tag}_bone_band", fp(b1["share_in_band"]))
        for N0, nm in ((64, "sixtyfour"), (256, "twofiftysix")): mac(f"{tag}_bone_share_{nm}", fp(b1["by_N0"][str(N0)]["share"]))
        for key, nm in (("one_pct", "one"), ("tenth_pct", "tenth")):
            b2 = C["B2"][key]; mac(f"{tag}_btwo_{nm}_acc", fp(b2["accuracy"])); mac(f"{tag}_btwo_{nm}_major", fp(b2["majority_baseline"])); mac(f"{tag}_btwo_{nm}_verdict", pm(b2["criterion_met"])); mac(f"{tag}_btwo_{nm}_n", fi(b2["n"]))
        mac(f"{tag}_fone_flagged", fi(f1["n_flagged_cells"])); mac(f"{tag}_fone_evaluable", "yes" if f1["evaluable"] else "no"); mac(f"{tag}_fone_verdict", (pm(f1["criterion_met"]) if f1["evaluable"] else "not evaluable"))
        mac(f"{tag}_sfour_k", fc(s4["strong_better_by_25pct"])); mac(f"{tag}_sfour_n", fc(s4["n_cells"])); mac(f"{tag}_sfour_verdict", pm(s4["criterion_met"])); mac(f"{tag}_sfour_median", fd(s4["median_ratio_tool_over_strong"], 2))
        pl = X["problem_level"]; mac(f"{tag}_pl_sone_lo", fd(pl["s1_median_ci"][0], 2)); mac(f"{tag}_pl_sone_hi", fd(pl["s1_median_ci"][1], 2)); mac(f"{tag}_pl_stwo_lo", fd(pl["s2_median_ci"][0], 2)); mac(f"{tag}_pl_stwo_hi", fd(pl["s2_median_ci"][1], 2))
        mac(f"{tag}_pl_sthree_lo", fd(pl["s3_median_ci"][0], 2)); mac(f"{tag}_pl_sthree_hi", fd(pl["s3_median_ci"][1], 2)); mac(f"{tag}_pl_bone_lo", fp(pl["b1_share_ci"][0])); mac(f"{tag}_pl_bone_hi", fp(pl["b1_share_ci"][1]))
        mac(f"{tag}_lopo_regret", fd(X["lopo_fixed_member"]["median_regret"], 2)); mac(f"{tag}_fixed_best", "\\texttt{" + X["best_fixed_member"].replace("_", "\\_") + "}"); mac(f"{tag}_fixed_regret", fd(X["fixed_member"][X["best_fixed_member"]]["median_regret"], 2))
        mac(f"{tag}_fixed_share", fp(X["fixed_member"][X["best_fixed_member"]]["share_le2"])); mac(f"{tag}_fixed_ratio", fd(X["tool_vs_best_fixed"]["median_ratio"], 2))
    mac("sv_met_count", fc(sum(bool(x) for x in [C7["PT"]["criterion_met"], C7["S1"]["criterion_met"], C7["S2"]["criterion_met"], C7["S3"]["criterion_met"], C7["B1"]["criterion_met"], C7["B2"]["one_pct"]["criterion_met"], C7["B2"]["tenth_pct"]["criterion_met"], C7["S4"]["criterion_met"]])))
    # the problems where the tool loses to the benchmark's own selection
    sc = pd.read_csv(S7 / "S1_cells.csv"); worse = sc[sc.r_leg > 1.1]; mac("sv_sthree_worse_helm", fi(worse.instance.str.startswith("helmholtz").sum())); mac("sv_sthree_worse_other", fi((~worse.instance.str.startswith("helmholtz")).sum()))
    mac("sv_sthree_max", fd(sc.r_leg.max(), 1)); mac("sv_sthree_max_where", "\\texttt{" + sc.loc[sc.r_leg.idxmax()].instance.replace("_", "\\_") + "} at $N=" + str(int(sc.loc[sc.r_leg.idxmax()].N)) + "$")
    wh = sc[sc.instance == "helmholtz_L1"].set_index("N"); mac("sv_helm1_regret1024", fd(wh.loc[1024, "regret"], 1))
    # ---------------------------------------------------------------- criteria table: Stage 6, Stage 7 held out, pooled
    def row(idn, label, f6, f7, fp_): return {"ID": idn, "Criterion": label, "Stage 6 (8 problems)": f6, "Stage 7 (8 new, held out)": f7, "Pooled (16)": fp_}
    g = lambda C: dict(s1=f"{fd(C['S1']['median_regret'])}; {fp(C['S1']['share_le2'])}; {pm(C['S1']['criterion_met'])}", s2=f"{fd(C['S2']['median_ratio'])}; {pm(C['S2']['criterion_met'])}", s3=f"{fd(C['S3']['median_ratio'])}; {C['S3']['n_better_10pct']}/{C['S3']['n_worse_10pct']}; {pm(C['S3']['criterion_met'])}",
                       b1=f"{fp(C['B1']['share'])}; {pm(C['B1']['criterion_met'])}", b2=f"{fp(C['B2']['one_pct']['accuracy'])} / {fp(C['B2']['tenth_pct']['accuracy'])}; {pm(C['B2']['one_pct']['criterion_met'] and C['B2']['tenth_pct']['criterion_met'])}",
                       f1=(f"{C['F1']['n_flagged_cells']} flagged; " + (pm(C['F1']['criterion_met']) if C['F1']['evaluable'] else "not evaluable")), s4=f"{C['S4']['strong_better_by_25pct']} of {C['S4']['n_cells']}; {pm(C['S4']['criterion_met'])}", pt=f"{C['PT']['n_ls_clear']} of {C['PT']['n_problems']}; {pm(C['PT']['criterion_met'])}")
    a, b, c = g(C6), g(C7), g(CP)
    rows = [row("H1a", "median regret $\\le1.5$; $\\ge75\\%$ of cells $\\le2$", a["s1"], b["s1"], c["s1"]), row("H1b", "median ratio vs always-GP $\\le1$", a["s2"], b["s2"], c["s2"]), row("H1c", "median ratio vs benchmark selection $\\le1$; better/worse cells", a["s3"], b["s3"], c["s3"]),
            row("H2", "forecast within $\\times2$ in $\\ge70\\%$", a["b1"], b["b1"], c["b1"]), row("H2 (reach)", "classification accuracy $\\ge75\\%$ (1\\% / 0.1\\%)", a["b2"], b["b2"], c["b2"]), row("H3", "basis flag helps (if $\\ge5$ flagged)", a["f1"], b["f1"], c["f1"]),
            row("H4", "tuned network better by $>25\\%$ in $\\le4$ of 16", a["s4"], b["s4"], c["s4"]), row("H5", "reduced basis clear on $\\ge5$ of 8", a["pt"], b["pt"], c["pt"])]
    tex_table("sv_criteria", pd.DataFrame(rows), colfmt="p{1.3cm}p{3.6cm}p{3.0cm}p{3.3cm}p{3.0cm}")
    # ---------------------------------------------------------------- per-problem table (N = 256): tool, oracle, always GP, benchmark selection, tuned network, tool + network
    sc2 = sc[sc.N == 256].set_index("instance"); s4c = pd.read_csv(S7 / "S4_cells.csv"); s4c = s4c[s4c.N == 256].set_index("instance"); W = json.load(open(S7 / "W.json")) if (S7 / "W.json").exists() else None
    L = []
    for inst, r in sc2.iterrows():
        d = {"Problem": "\\texttt{" + inst.replace("_", "\\_") + "}", "Tool": fs(r["sel"], 1), "Oracle": fs(r.orc, 1), "Always GP": fs(r.leg_gp, 1), "Benchmark sel.": fs(r.leg_sel, 1), "Tuned net": fs(s4c.loc[inst, "strong"], 1)}
        if W: d["Tool + net"] = fs(W["per_cell"][inst]["tool_plus_net"], 1)
        L.append(d)
    tex_table("sv_errors", pd.DataFrame(L), colfmt="lrrrrrr")
    # ---------------------------------------------------------------- tool + network (N7)
    if W:
        w1, w2 = W["W1"], W["W2"]; mac("sv_wone_median", fd(w1["median_regret"], 2)); mac("sv_wone_max", fd(w1["max_regret"], 2)); mac("sv_wone_share", fp(w1["share_le2"])); mac("sv_wone_verdict", pm(w1["criterion_met"])); mac("sv_wtwo_k", fc(w2["n_ok"])); mac("sv_wtwo_n", fc(w2["n_cells"])); mac("sv_wtwo_verdict", pm(w2["criterion_met"]))
        mac("sv_w_sel_net", fi(W["n_jobs_selecting_network"])); mac("sv_w_jobs", fi(W["n_jobs"])); mac("sv_w_oracle_net", fi(W["n_jobs_network_is_oracle"])); mac("sv_w_sec", fi(W["median_fit_seconds"]))
        h = W["per_cell"]["helmholtz_L1"]; mac("sv_w_helm_tool", fd(h["tool_alone"], 2)); mac("sv_w_helm_both", fd(h["tool_plus_net"], 2)); mac("sv_w_helm_net", fd(h["net_alone"], 2))
        changed = [k for k, v in W["per_cell"].items() if abs(np.log(v["tool_plus_net"] / v["tool_alone"])) > 0.05]; mac("sv_w_changed", fc(len(changed))); mac("sv_w_changed_names", ", ".join("\\texttt{" + k.replace("_", "\\_") + "}" for k in changed))
    # ---------------------------------------------------------------- stronger network (S+)
    if (S7 / "S5.json").exists():
        S5 = json.load(open(S7 / "S5.json")); mac("sv_sfive_n", fc(S5["n_cells"])); mac("sv_sfive_std", fc(S5["n_better_than_tool_by_25pct_standard"])); mac("sv_sfive_str", fc(S5["n_better_than_tool_by_25pct_stronger"])); mac("sv_sfive_ratio", fd(S5["median_ratio_stronger_over_standard"], 2))
        mac("sv_sfive_better", fc(S5["n_stronger_better_than_standard"])); mac("sv_sfive_better10", fc(S5["n_stronger_better_by_10pct_than_standard"])); mac("sv_sfive_toolratio", fd(S5["median_ratio_tool_over_stronger"], 2)); mac("sv_sfive_toolratio_std", fd(S5["median_ratio_tool_over_standard"], 2))
        mac("sv_sfive_sec", fi(S5["median_seconds_stronger"] / 60)); mac("sv_sfive_wins", ", ".join("\\texttt{" + k.replace("_", "\\_") + "}" for k in S5["stronger_wins"])); mac("sv_sfive_stdwins", ", ".join("\\texttt{" + k.replace("_", "\\_") + "}" for k in S5["standard_wins"]))
    # ---------------------------------------------------------------- expensive solver (E7)
    if (S7 / "E7.json").exists():
        E = json.load(open(S7 / "E7.json")); e1 = E["E1"]; mac("sv_e_tsim", fd(E["t_sim_seconds"], 2)); mac("sv_e_regret64", fd(e1["regret64_mean"], 2)); mac("sv_e_regret256", fd(e1["regret256_mean"], 2)); mac("sv_e_fc_k", fc(e1["n_forecast_ok"])); mac("sv_e_fc_n", fc(e1["n_seeds"])); mac("sv_e_verdict", pm(e1["criterion_met"]))
        for N, nm in ((64, "sixtyfour"), (256, "twofiftysix")):
            c = E["cost"][str(N)]; mac(f"sv_e_simh_{nm}", fd(c["sim_hours"], 2)); mac(f"sv_e_toolsec_{nm}", fi(c["tool_seconds"])); mac(f"sv_e_break_{nm}", fi(c["break_even_queries"]))
        c = E["cost"]["256"]; mac("sv_e_direct_h", fd(c["solver_hours_for_1e4_queries"], 1)); mac("sv_e_surr_h", fd(c["surrogate_hours_for_1e4_queries"], 2)); mac("sv_e_err_tool64", fs(E["geo_err_tool"]["N64"], 1)); mac("sv_e_err_tool256", fs(E["geo_err_tool"]["N256"], 1)); mac("sv_e_err_gp256", fs(E["geo_err_gp"]["N256"], 1)); mac("sv_e_err_net256", fs(E["geo_err_net256"], 1))
        mac("sv_e_net_sec", fi(E["median_network_seconds"])); ps = E["per_seed"]; mac("sv_e_fc_ratio_min", fd(min(r["fc_ratio"] for r in ps), 2)); mac("sv_e_fc_ratio_max", fd(max(r["fc_ratio"] for r in ps), 2))
        mac("sv_e_sel", ", ".join(sorted({"\\texttt{" + r["sel256"].replace("_", "\\_") + "}" for r in ps})))


def problems_table_s7(ag):
    import sys
    sys.path.insert(0, str(ag.ROOT / "code/src")); from surrogate_bench.problems import build_suite_tp2
    L = [{"Problem": "\\texttt{" + n.replace("_", "\\_") + "}", "$p$": P.p, "$m$": P.m, "Description": P.description.replace("scikit-fem ", "").replace("^2", "$^2$").replace("_", "\\_")} for n, P in build_suite_tp2().items()]
    ag.tex_table("sv_problems", pd.DataFrame(L), colfmt="lrrp{9cm}")
