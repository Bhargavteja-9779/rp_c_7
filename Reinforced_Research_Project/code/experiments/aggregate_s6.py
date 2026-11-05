"""Part 2 of aggregate.py: Stage 6 (criteria.json, PT.json), real-data check, plain-file validation, cost. Defines macros and tables."""
import json, pathlib, numpy as np, pandas as pd

def part2(ag):
    R, OUT, mac, fi, fc, fd, fp, fs, fx, tex_table = ag.R, ag.OUT, ag.mac, ag.fi, ag.fc, ag.fd, ag.fp, ag.fs, ag.fx, ag.tex_table; S = R / "s6"
    pm = lambda met: "met" if met else "not met"
    cj = S / "criteria.json"
    if cj.exists():
        C = json.load(open(cj)); PT = C["PT"]
        mac("tp_ls_clear", fc(PT["n_ls_clear"])); mac("tp_n", fc(PT["n_problems"])); mac("tp_not_clear", fc(PT["n_problems"] - PT["n_ls_clear"])); mac("tp_verdict", pm(PT["criterion_met"]))
        s1 = C["S1"]; mac("sone_n", fi(s1["n_cells"])); mac("sone_median", fd(s1["median_regret"], 2)); mac("sone_max", fd(s1["max_regret"], 2)); mac("sone_lo", fd(s1["median_ci"][0], 2)); mac("sone_hi", fd(s1["median_ci"][1], 2)); mac("sone_share", fp(s1["share_le2"])); mac("sone_wlo", fp(s1["wilson_le2"][0])); mac("sone_whi", fp(s1["wilson_le2"][1])); mac("sone_verdict", pm(s1["criterion_met"]))
        mac("null_regret", fd(s1["null_random_pick_median_regret"], 2)); mac("null_share", fp(s1["null_random_pick_share_le2"]))
        for N, nm in ((64, "sixtyfour"), (256, "twofiftysix"), (1024, "tentwentyfour")): mac(f"sone_median_{nm}", fd(s1["per_N"][str(N)]["median"], 2))
        s2 = C["S2"]; mac("stwo_median", fd(s2["median_ratio"], 2)); mac("stwo_lo", fd(s2["ci"][0], 2)); mac("stwo_hi", fd(s2["ci"][1], 2)); mac("stwo_better", fc(s2["n_better"])); mac("stwo_worse", fc(s2["n_worse"])); mac("stwo_verdict", pm(s2["criterion_met"]))
        s3 = C["S3"]; mac("sthree_median", fd(s3["median_ratio"], 2)); mac("sthree_lo", fd(s3["ci"][0], 2)); mac("sthree_hi", fd(s3["ci"][1], 2)); mac("sthree_better", fc(s3["n_better_10pct"])); mac("sthree_worse", fc(s3["n_worse_10pct"])); mac("sthree_verdict", pm(s3["criterion_met"]))
        b1 = C["B1"]; mac("bone_n", fi(b1["n_cases"])); mac("bone_k", fi(b1["n_within_factor2"])); mac("bone_share", fp(b1["share"])); mac("bone_lo", fp(b1["wilson"][0])); mac("bone_hi", fp(b1["wilson"][1])); mac("bone_band", fp(b1["share_in_band"])); mac("bone_verdict", pm(b1["criterion_met"]))
        mac("bone_median_abs", fd(10 ** b1["median_abs_log10"], 2)); mac("bone_bias", fd(10 ** b1["bias_median_log10"], 2))
        for N0, nm in ((64, "sixtyfour"), (256, "twofiftysix")): mac(f"bone_share_{nm}", fp(b1["by_N0"][str(N0)]["share"]))
        for key, nm in (("one_pct", "one"), ("tenth_pct", "tenth")):
            b2 = C["B2"][key]; mac(f"btwo_{nm}_acc", fp(b2["accuracy"])); mac(f"btwo_{nm}_verdict", pm(b2["criterion_met"])); mac(f"btwo_{nm}_actual", fi(b2["actual_reached"])); mac(f"btwo_{nm}_pred", fi(b2["predicted_reached"])); mac(f"btwo_{nm}_n", fi(b2["n"]))
        mac("bone_under", fi(b1["n_under_factor2"])); mac("bone_over", fi(b1["n_over_factor2"])); mac("bone_within_twofiftysix", fi(b1["n_within2_N256"])); mac("bone_under_twofiftysix", fi(b1["n_under_N256"]))
        mac("btwo_one_major", fp(C["B2"]["one_pct"]["majority_baseline"])); mac("btwo_tenth_major", fp(C["B2"]["tenth_pct"]["majority_baseline"]))
        f1 = C["F1"]; mac("fone_flagged", fi(f1["n_flagged_cells"])); mac("fone_evaluable", "yes" if f1["evaluable"] else "no")
        if f1.get("n_ok") is not None: mac("fone_ok", fi(f1["n_ok"])); mac("fone_share", fp(f1["share_full_better"])); mac("fone_verdict", pm(f1["criterion_met"]) if f1["evaluable"] else "not evaluable")
        else: mac("fone_ok", "0"); mac("fone_share", "n/a"); mac("fone_verdict", "not evaluable")
        if C.get("S4"):
            s4 = C["S4"]; mac("sfour_n", fc(s4["n_cells"])); mac("sfour_better", fc(s4["strong_better_by_25pct"])); mac("sfour_verdict", pm(s4["criterion_met"])); mac("sfour_median", fd(s4["median_ratio_tool_over_strong"], 2)); mac("sfour_wlo", fp(s4["wilson"][0])); mac("sfour_whi", fp(s4["wilson"][1])); mac("sfour_tool_better", fi(s4["n_tool_better_10pct"])); mac("sfour_strong_better", fi(s4["n_strong_better_10pct"]))
            for N, nm in ((256, "twofiftysix"), (1024, "tentwentyfour")): mac(f"strong_sec_{nm}", fi(s4["median_seconds_strong"][str(N)]))
        v = [PT["criterion_met"], s1["criterion_met"], s2["criterion_met"], s3["criterion_met"], b1["criterion_met"]] + ([C["S4"]["criterion_met"]] if C.get("S4") else []) + ([f1["criterion_met"]] if f1["evaluable"] else [])
        mac("cover_met_count", fc(sum(bool(x) for x in v))); mac("cover_not_met_count", fc(sum(not x for x in v))); mac("cover_not_evaluable", fc(7 - len(v)))
        sc0 = pd.read_csv(S / "S1_cells.csv"); mx = sc0.loc[sc0.r_leg.idxmax()]; mac("sthree_max_ratio", fd(mx.r_leg, 1)); mac("sthree_max_where", "\\texttt{" + mx.instance.replace("_", "\\_") + "} at $N=" + str(int(mx.N)) + "$")
        l2 = sc0[(sc0.instance == "lshape_L2") & (sc0.N == 1024)].r_leg.iloc[0]; mac("sthree_lshape_ratio", fd(l2, 1))
        mac("abl_podonly_gt", fp(1 - C["S1"].get("share_le2_podonly", 0.75)))
        K = C["K"]; mac("tool_scale_ratio", fd(K["median_fit_seconds"]["1024"] / K["median_fit_seconds"]["256"], 1))
        for N, nm in ((64, "sixtyfour"), (256, "twofiftysix"), (1024, "tentwentyfour")): mac(f"tool_fit_sec_{nm}", fi(K["median_fit_seconds"][str(N)])); mac(f"tool_total_sec_{nm}", fi(K["median_total_seconds"][str(N)]))
        mac("bone_p_raw", fd(C["holm"]["B1_vs_70"]["p"], 2)); mac("sone_p_raw", f"{C['holm']['S1_share_le2_vs_75']['p']:.3f}")
        for k, v in C["holm"].items(): mac("holm_" + k.replace("_vs_", "_").lower().replace("%", "p"), fd(v["holm_adj"], 3))
        # table of criteria
        rows = [("H5", "reduced basis clear on $\\ge5$ of 8", f"{PT['n_ls_clear']} of {PT['n_problems']}", "--", pm(PT["criterion_met"])),
                ("H1a", "median regret $\\le1.5$; $\\ge75\\%$ of cells $\\le2$", f"median {fd(s1['median_regret'])} [{fd(s1['median_ci'][0])}, {fd(s1['median_ci'][1])}]; {fp(s1['share_le2'])} [{fp(s1['wilson_le2'][0])}, {fp(s1['wilson_le2'][1])}]", f"{fd(C['holm']['S1_share_le2_vs_75']['holm_adj'], 3)}", pm(s1["criterion_met"])),
                ("H1b", "median ratio vs always-GP $\\le1$", f"{fd(s2['median_ratio'])} [{fd(s2['ci'][0])}, {fd(s2['ci'][1])}]; better/worse {s2['n_better']}/{s2['n_worse']}", "--", pm(s2["criterion_met"])),
                ("H1c", "median ratio vs benchmark selection $\\le1$; better $>$ worse", f"{fd(s3['median_ratio'])} [{fd(s3['ci'][0])}, {fd(s3['ci'][1])}]; better/worse {s3['n_better_10pct']}/{s3['n_worse_10pct']}", "--", pm(s3["criterion_met"])),
                ("H2", "forecast within $\\times2$ in $\\ge70\\%$ of 48", f"{b1['n_within_factor2']} of {b1['n_cases']} ({fp(b1['share'])} [{fp(b1['wilson'][0])}, {fp(b1['wilson'][1])}])", f"{fd(C['holm']['B1_vs_70']['holm_adj'], 3)}", pm(b1["criterion_met"])),
                ("H2 (reach 1\\%)", "classification accuracy $\\ge75\\%$", f"{fp(C['B2']['one_pct']['accuracy'])}", "--", pm(C["B2"]["one_pct"]["criterion_met"])),
                ("H2 (reach 0.1\\%)", "classification accuracy $\\ge75\\%$", f"{fp(C['B2']['tenth_pct']['accuracy'])}", "--", pm(C["B2"]["tenth_pct"]["criterion_met"])),
                ("H3", "$\\ge75\\%$ of flagged cells (if $\\ge5$)", f"{f1['n_flagged_cells']} flagged" + (f"; {f1['n_ok']} better ({fp(f1['share_full_better'])})" if f1.get("n_ok") is not None else ""), "--", pm(f1["criterion_met"]) if f1["evaluable"] else "not evaluable")]
        if C.get("S4"): rows.append(("H4", "strong network better by $>25\\%$ in $\\le4$ of 16", f"{s4['strong_better_by_25pct']} of {s4['n_cells']}", f"{fd(C['holm']['S4_strong_wins_vs_25pct']['holm_adj'], 3)}", pm(s4["criterion_met"])))
        rows = rows[1:] + rows[:1]   # H5 last
        tex_table("criteria", pd.DataFrame(rows, columns=["ID", "Criterion", "Observed (95\\% interval)", "Holm $p$", "Verdict"]), colfmt="p{1.5cm}p{4.4cm}p{5.2cm}p{1.3cm}p{1.6cm}")
        # per-problem table at N=256 and 1024: tool, always GP, benchmark selection, strong NN, oracle
        sc = pd.read_csv(S / "S1_cells.csv"); s4c = pd.read_csv(S / "S4_cells.csv") if (S / "S4_cells.csv").exists() else None
        L = []
        for _, r in sc[sc.N.isin([256, 1024])].sort_values(["N", "instance"]).iterrows():
            st = ""
            if s4c is not None:
                q = s4c[(s4c.instance == r.instance) & (s4c.N == r.N)]; st = fs(q.strong.iloc[0], 1) if len(q) else "--"
            L.append(dict(Problem="\\texttt{" + r.instance.replace("_", "\\_") + "}", N=int(r.N), Tool=fs(r["sel"], 1), Oracle=fs(r.orc, 1), **{"Always GP": fs(r.leg_gp, 1), "Benchmark sel.": fs(r.leg_sel, 1), "Tuned net": st}))
        tex_table("tp_errors", pd.DataFrame(L), colfmt="lrrrrrr")
    ab = S / "ablation.json"
    if ab.exists():
        A_ = json.load(open(ab)); rows_ = [dict(Pool=k, **{"Median regret": fd(v["median_regret"], 2), "Cells with regret $\\le2$": fp(v["share_regret_le2"]), "Median error vs full pool": fx(v["median_ratio_to_full_pool"], 2)}) for k, v in A_.items()]
        tex_table("ablation", pd.DataFrame(rows_), colfmt="lrrr"); mac("abl_podonly_share", fp(A_["POD-based members only"]["share_regret_le2"])); mac("abl_noGP_median", fd(A_["no GP (ridge, polynomial)"]["median_ratio_to_full_pool"], 1))
    ex = S / "extras.json"
    if ex.exists():
        X = json.load(open(ex)); fm = X["fixed_member"]; bf = X["best_fixed_member"]
        mac("fixed_best_name", "\\texttt{" + bf.replace("_", "\\_") + "}"); mac("fixed_best_regret", fd(fm[bf]["median_regret"], 2)); mac("fixed_best_share", fp(fm[bf]["share_le2"])); mac("fixed_best_ratio", fd(X["tool_vs_best_fixed"]["median_ratio"], 2)); mac("fixed_best_better", fc(X["tool_vs_best_fixed"]["better_10"])); mac("fixed_best_worse", fc(X["tool_vs_best_fixed"]["worse_10"]))
        pl = X["problem_level"]; mac("pl_sone_lo", fd(pl["s1_median_ci"][0], 2)); mac("pl_sone_hi", fd(pl["s1_median_ci"][1], 2)); mac("pl_sone_wlo", fp(pl["s1_problem_wilson"][0])); mac("pl_stwo_lo", fd(pl["s2_median_ci"][0], 2)); mac("pl_stwo_hi", fd(pl["s2_median_ci"][1], 2)); mac("pl_sthree_lo", fd(pl["s3_median_ci"][0], 2)); mac("pl_sthree_hi", fd(pl["s3_median_ci"][1], 2)); mac("pl_bone_lo", fp(pl["b1_share_ci"][0])); mac("pl_bone_hi", fp(pl["b1_share_ci"][1]))
        mac("btwo_tenth_p", fd(X["b2_p"]["tenth_pct"], 2)); h3 = X["h3"]; mac("hthree_jobs", fi(h3["flagged_jobs"])); mac("hthree_cells", fc(h3["flagged_distinct_cells"])); mac("hthree_problems", fc(h3["flagged_problems"])); mac("hthree_full_jobs", fi(h3["jobs_full_better"])); mac("hthree_recall", fp(h3["recall_jobs"])); mac("hthree_selected", fi(h3["flagged_jobs_already_full_selected"]))
        sl = X["strong_vs_legacy_network"]; mac("strong_legacy_ratio", fd(sl["median_ratio"], 2)); mac("strong_legacy_n", fi(sl["n_improved"])); mac("strong_problems_n", fc(len(X["strong_problems_better_25"])))
        mac("strong_worst_problem_ratio", fd(sl["tool_over_strong_at_1024_smooth"][0][1] ** -1, 0))
    rt = S / "retro.json"
    if rt.exists():
        Z = json.load(open(rt)); mac("retro_n", fi(Z["n_problems"])); mac("retro_median", fd(Z["median_regret"], 2)); mac("retro_share", fp(Z["share_regret_le2"])); mac("retro_max", fd(Z["max_regret"], 2)); mac("retro_leg", fd(Z["median_ratio_vs_legacy_selection"], 2)); mac("retro_better", fi(Z["tool_better_10"])); mac("retro_worse", fi(Z["tool_worse_10"])); mac("retro_gp", fd(Z["median_ratio_vs_pod_gp"], 2)); mac("retro_flagged", fi(Z["n_basis_flagged"]))
        mac("retro_worst", ", ".join("\\texttt{" + w[0].replace("_", "\\_") + "} (" + f"{w[1]:.1f}" + ")" for w in Z["worst"]))
    rc = S / "real_criteria.json"
    if rc.exists():
        Rr = json.load(open(rc)); mac("real_rone_median", fd(Rr["R1"]["median_regret"], 2)); mac("real_rone_verdict", pm(Rr["R1"]["criterion_met"])); mac("real_rtwo_k", fc(Rr["R2"]["n_not_worse"])); mac("real_rtwo_n", fc(Rr["R2"]["n_cells"])); mac("real_rtwo_verdict", pm(Rr["R2"]["criterion_met"]))
        mac("real_rthree_k", fc(Rr["R3"]["n_strong_better_25"])); mac("real_rthree_verdict", pm(Rr["R3"]["criterion_met"])); mac("real_rfour_k", fi(Rr["R4"]["n_within2"])); mac("real_rfour_n", fi(Rr["R4"]["n_cases"])); mac("real_rfour_verdict", pm(Rr["R4"]["criterion_met"]))
        cells = pd.DataFrame(Rr["cells"]); L = [dict(Dataset=r["dataset"], N=int(r["N"]), Tool=fd(r["sel"], 4), Oracle=fd(r["orc"], 4), **{"Always GP": fd(r["gp"], 4), "Tuned net": fd(r["strong"], 4)}, Regret=fd(r["regret"], 2)) for r in Rr["cells"]]; tex_table("real", pd.DataFrame(L), colfmt="lrrrrrr")
    pf = S / "plain_files_validation.json"
    if pf.exists():
        P = json.load(open(pf)); mac("plain_n", fi(len(P["problems"]))); mac("plain_agree", fi(sum(v["agree"] for v in P["problems"].values()))); mac("plain_ok", fi(sum(v["ok"] for v in P["problems"].values())))
