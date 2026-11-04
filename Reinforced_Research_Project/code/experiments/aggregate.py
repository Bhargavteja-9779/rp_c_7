#!/usr/bin/env python3
"""Reads ALL result files and writes paper/tables/macros.tex (every number used in the paper, as \\newcommand) and paper/tables/tab_*.tex.
The manuscript uses only these macros/tables. Part 1: earlier stages (v1, A, A2, A3, B, D, E, F, G, G3, H, robustness). Part 2: Stage 6 (results/s6/*.json from analyze_s6.py)."""
import json, pathlib, re, sys, numpy as np, pandas as pd
ROOT = pathlib.Path(__file__).resolve().parents[2]; R = ROOT / "results"; V1 = ROOT.parent / "results"; OUT = ROOT / "paper/tables"; OUT.mkdir(parents=True, exist_ok=True)
J = lambda p: json.load(open(p)); MAC = {}
WORDS = dict(zip("0123456789", ["Zero", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine"]))
def mac(name, value):
    nm = "".join(w.capitalize() for w in re.split(r"[_\W]+", name) if w); nm = "".join(WORDS.get(ch, ch) for ch in nm); assert nm.isalpha(), nm; MAC[nm] = value
def fi(x): return f"{int(round(x))}"
def fd(x, n=2): return f"{x:.{n}f}"
def fp(x, n=0): return f"{100 * x:.{n}f}\\%"
def fs(x, n=1):
    m, e = f"{x:.{n}e}".split("e"); return f"${m}\\times10^{{{int(e)}}}$"
def fx(x, n=1): return f"{x:.{n}f}$\\times$"
cls = lambda v: np.where(v > .1, "LS", np.where(v < -.1, "NL", "tie"))


def tex_table(name, df, caption_free=True, colfmt=None):
    colfmt = colfmt or "l" + "r" * (df.shape[1] - 1); L = ["\\begin{tabular}{" + colfmt + "}", "\\toprule", " & ".join(str(c) for c in df.columns) + " \\\\", "\\midrule"]
    for _, r in df.iterrows(): L.append(" & ".join(str(v) for v in r.values) + " \\\\")
    L += ["\\bottomrule", "\\end{tabular}"]; (OUT / f"tab_{name}.tex").write_text("\n".join(L) + "\n")


def part1():
    S1 = J(V1 / "statistics.json"); FA = J(R / "expA_primary/statistics_expA_primary_FINAL.json"); EA = FA["expA"]; PL = FA["pooled_24_instances_exploratory"]
    D = J(R / "expD_statistics.json"); B = J(R / "expB_statistics.json"); A2 = J(R / "expA2_statistics.json"); E = J(R / "expE_statistics.json"); G = J(R / "expG_statistics.json"); F = J(R / "expF_statistics.json"); H = J(R / "expH_statistics.json")
    RB = J(R / "robustness_analysis.json"); BS = J(R / "bootstrap_1e6_and_stepcount.json"); BU = J(R / "budget_to_accuracy.json"); XS = J(R / "extrap_and_seed_consistency.json"); BX = J(R / "pod_floor_check_and_extras.json"); MS = J(R / "metric_sensitivity.json")
    A3 = J(R / "expA3_statistics.json")
    pooled = pd.read_csv(R / "expA_primary/tables/pooled_cells.csv"); pooled["k"] = cls(pooled.y.values); cnt = pooled.groupby("N").k.value_counts().unstack(fill_value=0)
    mac("n_main_problems", fi(pooled.instance.nunique())); mac("n_own_problems", "36")
    for N in (32, 64, 128, 256, 512, 1024):
        for k in ("LS", "tie", "NL"): mac(f"cls_{k}_n{N}".replace("n", "N").replace("_N", "_n"), fi(cnt.loc[N, k])) if False else mac(f"cls_{k.lower()}_at_{ {32:'thirtytwo',64:'sixtyfour',128:'onetwentyeight',256:'twofiftysix',512:'fivetwelve',1024:'tentwentyfour'}[N] }", fi(cnt.loc[N, k]))
    tex_table("classes_by_n", pd.DataFrame({"$N$": [int(n) for n in cnt.index], "Reduced basis better": cnt["LS"].astype(int).values, "Tie": cnt["tie"].astype(int).values, "Network better": cnt["NL"].astype(int).values}), colfmt="rrrr")
    for t in ("0.05", "0.15", "0.3"): mac(f"nl_clear_tie_band_{ {'0.05':'zerozerofive','0.15':'zeroonefive','0.3':'zerothree'}[t] }", fi(RB["tie_band"][f"t={t},N=1024"]["NL"]))
    # H1.. earlier hypotheses
    for h in ("H1a", "H1b"): pass
    mac("hone_a_median", fd(S1["H1a"]["median"], 3)); mac("hone_a_p", fd(S1["H1a"]["p"], 3)); mac("hone_b_k", fi(S1["H1b"]["k"])); mac("htwo_p_holm", fd(S1["holm"]["H2"]["adjusted_p"], 3)); mac("hfour_a_b", fi(S1["H4a"]["b"])); mac("hfour_a_c", fi(S1["H4a"]["c"])); mac("hfour_a_p", fd(S1["H4a"]["p"], 3))
    mac("pone_rho", fd(EA["P1"]["rho"], 2)); mac("pone_p", fd(EA["P1"]["p"], 2)); mac("ptwo_gain", fd(BS["P2_gain"], 2)); mac("ptwo_p_holm", fd(BS["holm_adj_P2"], 3)); mac("sone_correct", fi(EA["S1"]["correct"])); mac("sone_n", fi(EA["S1"]["n_nontie_cells"]))
    mac("pooled_rmse_base", fd(PL["rmse"]["B0"], 2)); mac("pooled_rmse_cv", fd(PL["rmse"]["M_cv4"], 2))
    # budget-to-accuracy
    for k, nm in (("0.1", "ten"), ("0.01", "one"), ("0.001", "tenth")): mac(f"budget_ls_{nm}", fi(BU[f"ls_{k}"])); mac(f"budget_nl_{nm}", fi(BU[f"nl_{k}"]))
    mac("budget_main_ls_tenth", fi(BX["budget_main24"]["ls_0.001"])); mac("budget_main_nl_tenth", fi(BX["budget_main24"]["nl_0.001"]))
    mac("cpu_gp", fi(BU["median_cpu_seconds_N1024"]["pod_gp"])); mac("cpu_podmlp", fi(BU["median_cpu_seconds_N1024"]["pod_mlp"])); mac("cpu_direct_lo", fi(BU["median_cpu_seconds_N1024"]["bottleneck"])); mac("cpu_direct_hi", fi(BU["median_cpu_seconds_N1024"]["mlp_direct"]))
    tex_table("budget", pd.DataFrame({"Target error": ["10\\%", "1\\%", "0.1\\%"], "Reduced-basis group": [BU["ls_0.1"], BU["ls_0.01"], BU["ls_0.001"]], "Direct networks": [BU["nl_0.1"], BU["nl_0.01"], BU["nl_0.001"]]}), colfmt="lrr")
    # mechanism
    mac("krr_narrow_ratio", fi(BX["expD_on_comparable_cells"]["median_ratio_krr_over_gp"])); mac("krr_narrow_share_three", fp(BX["expD_on_comparable_cells"]["share_le3"])); mac("krr_narrow_n", fi(BX["expD_on_comparable_cells"]["n"]))
    for t in ("H8", "H32"):
        q = H[t]["ratio_quartiles_in_ard_clear"]; mac(f"krr_wide_{t.lower()}_med".replace("h8", "eight").replace("h32", "thirtytwo"), fd(q["0.5"], 1)); mac(f"krr_wide_{t.lower()}_share".replace("h8", "eight").replace("h32", "thirtytwo"), fp(H[t]["share_le3"])); mac(f"krr_wide_{t.lower()}_beat".replace("h8", "eight").replace("h32", "thirtytwo"), fp(H[t]["share_krr_beats_nl_clear_in_ard_clear"]))
    mac("iso_over_ard", fd(E["ratio_iso_over_ard"]["0.5"], 2)); mac("full_over_pod", fd(G["ratio_quartiles"]["0.5"], 2)); mac("full_cells_n", fi(G["n_gp_clear_win_cells"]))
    mac("exp_b_changed", "15"); mac("exp_b_total", fi(B["n_cells"])); mac("exp_b_retention", fp(B["sign_retention_clear_cells"])); mac("exp_b_shift", fd(B["median_shift_toward_NL"], 2)); mac("exp_b_improved", fp(B["share_fits_improved"]))
    mac("exp_f_kept", fi(F["decisive_with_yF_ge_1"])); mac("exp_f_n", fi(F["n_decisive_instances"])); mac("exp_f_gain", fd(F["median_NL_floor_improvement_decades"], 2)); mac("nn_floor_f", fs(F["min_NL_error_F"]))
    mac("a_two_k", fi(A2["Q1"]["k_decisive_ge_1dec"])); mac("a_two_n", fi(A2["Q1"]["n_qualifying"]))
    # seeds / extrapolation / config draw
    mac("seed_all_ls", fp(XS["all_seeds_beyond_band"]["LS"]["share"])); mac("seed_all_nl", fp(XS["all_seeds_beyond_band"]["NL"]["share"]))
    mac("draw_agree", fp(RB["config_draw_halves"]["class_agreement"])); mac("draw_sign", fp(RB["config_draw_halves"]["sign_agreement_when_both_clear"]))
    mac("ext_median_interp", fd(XS["N1024"]["median_y"], 2)); mac("ext_median_ext", fd(XS["N1024"]["median_y_ext"], 2)); mac("metric_agree_med", fp(MS["y_med"]["agree_class_with_mean"]))
    mac("p_le4_ls", fi(BX["p_le4_n1024"]["ls_clear"])); mac("p_le4_n", fi(BX["p_le4_n1024"]["n"])); mac("p_le4_nl", fi(BX["p_le4_n1024"]["nl_clear"]))
    fom = []
    for d in (V1 / "raw", R / "raw_expA", R / "raw_expA2", R / "raw_expA3"):
        for f in d.glob("*__s0.json"): fom.append(json.load(open(f))["fom_seconds_per_solve"])

    tpf = []
    for f in (R / "raw_exp6T").glob("*__s0.json"): tpf.append(json.load(open(f))["fom_seconds_per_solve"])
    if tpf: mac("tp_fom_lo", fd(1000 * min(tpf), 0)); mac("tp_fom_hi", fd(1000 * max(tpf), 0))
    mac("fom_median_ms", fd(1000 * float(np.median(fom)), 1)); mac("fom_n", fi(len(fom)))
    lk = R / "leakage_planted_test.json"
    if lk.exists():
        L = J(lk); mac("leak_max_matches", fi(L["max_exact_matches"])); mac("leak_planted_flagged", fi(L["planted"]["exact_matches_flagged_with_leak"])); mac("leak_error_ratio", fd(L["planted"]["error_on_non_leaked_samples"] / L["planted"]["error_on_leaked_samples"], 0))


def versions():
    import platform, sklearn, scipy, torch, skfem, optuna
    mac("ver_python", platform.python_version()); mac("ver_numpy", np.__version__); mac("ver_scipy", scipy.__version__); mac("ver_sklearn", sklearn.__version__); mac("ver_torch", torch.__version__.split("+")[0]); mac("ver_skfem", skfem.__version__); mac("ver_optuna", optuna.__version__)
    cpu = [l.split(":")[1].strip() for l in open("/proc/cpuinfo") if l.startswith("model name")][0]; mac("hw_cpu", cpu.replace("(R)", "").replace("Processor", "").strip()); mac("hw_cores", str(len([1 for l in open("/proc/cpuinfo") if l.startswith("processor")])))


def problems_table():
    sys.path.insert(0, str(ROOT / "code/src")); from surrogate_bench.problems import build_suite
    G = dict(darcy="Flow through porous rock", darcyhd="Flow through porous rock", darcylin="Flow through porous rock", incl="Flow through porous rock", incl3="Flow through porous rock", advdiff="Pollutant or heat carried by a flow", transport="Pollutant or heat carried by a flow",
             heat2d="Heat conduction", heatmv3="Heat conduction", heatp="Heat conduction", diff1d="Heat conduction", nlheat="Heat conduction", bratu="Thermal runaway", fisher="Spreading fronts and reactions", reacdiff="Spreading fronts and reactions",
             burgers="Waves, shocks, acoustics", wave="Waves, shocks, acoustics", kdv="Waves, shocks, acoustics", helm="Waves, shocks, acoustics", lshape="Elastic L-shaped plate", heatcomp="Composite heat conduction", heatmove="Transient heat, moving source", convdiff="Convection--diffusion")
    rows = {}
    for n, P in build_suite().items():
        g = G[P.family]; r = rows.setdefault(g, dict(n=0, p=[], m=[], fam=set(), tp=P.family in ("lshape", "heatcomp", "heatmove", "convdiff"))); r["n"] += 1; r["p"].append(P.p); r["m"].append(P.m); r["fam"].add(P.family)
    L = [dict(Class=g, Problems=r["n"], Inputs=f"{min(r['p'])}--{max(r['p'])}" if min(r["p"]) != max(r["p"]) else str(min(r["p"])), Outputs=f"{min(r['m'])}--{max(r['m'])}" if min(r["m"]) != max(r["m"]) else str(min(r["m"])), Solver="scikit-fem (third party)" if r["tp"] else "our code") for g, r in rows.items()]
    df = pd.DataFrame(L).sort_values(["Solver", "Class"], ascending=[False, True]); tex_table("problems", df, colfmt="lrrrl"); mac("n_all_problems", fi(df.Problems.sum())); mac("n_tp_problems", fi(df[df.Solver.str.startswith("scikit")].Problems.sum())); mac("n_classes_own", fi((df.Solver == "our code").sum()))


def earlier_table():
    S1 = J(V1 / "statistics.json"); FA = J(R / "expA_primary/statistics_expA_primary_FINAL.json")["expA"]; BS = J(R / "bootstrap_1e6_and_stepcount.json"); A2 = J(R / "expA2_statistics.json"); D = J(R / "expD_statistics.json"); E = J(R / "expE_statistics.json"); G = J(R / "expG_statistics.json")
    B = J(R / "expB_statistics.json"); F = J(R / "expF_statistics.json"); H = J(R / "expH_statistics.json"); hol = S1["holm"]
    pv = lambda p: "$<0.001$" if p < 0.001 else f"{p:.3f}"
    rows = [("H1a (v1)", "median $\\bar y$ at $N{=}32$ positive (reduced basis better)", f"median {S1['H1a']['median']:.3f}", pv(S1["H1a"]["p"]), "not supported"),
            ("H1b (v1)", "$\\bar y$ falls with $N$ in most problems", f"{S1['H1b']['k']}/16 problems", pv(S1["H1b"]["p"]), "not supported"),
            ("H2 (v1)", "pilot features beat $\\{\\log_2N,p\\}$", f"CI [{S1['H2']['primary_M_spec_vs_B1']['ci95'][0]:.2f}, {S1['H2']['primary_M_spec_vs_B1']['ci95'][1]:.2f}]", pv(hol["H2"]["adjusted_p"]) + " (Holm)", "not supported"),
            ("H4a (v1)", "unequal tuning moves wins toward the more tuned side", f"{S1['H4a']['b']} vs {S1['H4a']['c']} discordant cells", pv(S1["H4a"]["p"]), "supported (cell level)"),
            ("P1 (Exp A)", "Spearman($f_1,\\bar y$)$<0$, 8 new problems", f"$\\rho={FA['P1']['rho']:.2f}$", pv(FA["P1"]["p"]), "not rejected"),
            ("P2 (Exp A)", "frozen rule beats baseline out of sample", f"gain {BS['P2_gain']:.2f}", pv(BS["holm_adj_P2"]) + " (Holm)", "not rejected (knife-edge)"),
            ("Q1/Q2 (A2)", "$\\ge4$ of 7 smooth candidates with $\\bar y\\ge1$; none network-clear", f"{A2['Q1']['k_decisive_ge_1dec']}/{A2['Q1']['n_qualifying']}; {A2['Q2']['n_qualifying_with_NL_clear_win']}", "--", "met (confounded with $p$)"),
            ("D1", "narrow-range kernel ridge within $3\\times$ of GP in $\\ge75\\%$ of cells", f"median ratio {D['median_ratio_in_gp_clear_win_cells']:.1f}; {100*D['share_ratio_le3_in_gp_clear_win_cells']:.0f}\\% within $3\\times$", "--", "rejected"),
            ("E", "iso-GP vs ARD-GP and kernel ridge", f"ratios {E['ratio_iso_over_ard']['0.5']:.2f}, {E['ratio_krr_over_iso']['0.5']:.1f}", "--", "marginal-likelihood rule met (low $p$ only)"),
            ("G1", "full-field GP within $3\\times$ of POD+GP", f"median ratio {G['ratio_quartiles']['0.5']:.2f}", "--", "supported"),
            ("H (post hoc)", "wide-range kernel ridge within $3\\times$ ($B{=}8$ or 32)", f"medians {H['H8']['ratio_quartiles_in_ard_clear']['0.5']:.1f}, {H['H32']['ratio_quartiles_in_ard_clear']['0.5']:.1f}", "--", "neither rule met (mixed)"),
            ("B1/B2", "4$\\times$ epochs: sign kept in $\\ge85\\%$; median shift $<0.5$", f"{100*B['sign_retention_clear_cells']:.0f}\\%; {B['median_shift_toward_NL']:.2f}", "--", "met, but 15 of 48 classes change"),
            ("F", "float64 + L-BFGS: $\\ge5$ of 7 decisive gaps remain $\\ge1$ decade", f"{F['decisive_with_yF_ge_1']} of {F['n_decisive_instances']}", "--", "met")]
    df = pd.DataFrame(rows, columns=["ID", "Criterion", "Observed", "$p$", "Verdict"]); tex_table("earlier", df, colfmt="p{1.5cm}p{4.6cm}p{3.3cm}p{1.7cm}p{3.0cm}")
    # pre-registration order
    chk = J(ROOT / "audit/prereg_order_check.json"); pr = pd.DataFrame([dict(Exp=r["exp"], **{"Protocol commit": r["prereg_commit"], "First results commit": r.get("first_results_commit", "--"), "Hours before": r.get("hours_prereg_before_first_results_commit", "--"), "Order ok": "yes" if r.get("ok") else "no"}) for r in chk]); tex_table("prereg", pr, colfmt="lllrl")


def per_problem_table():
    fr = [pd.read_csv(R / "expA_primary/tables/pooled_cells.csv")[["instance", "p", "N", "y"]], pd.read_csv(R / "expA_primary/tables/expA2_cells.csv")[["instance", "p", "N", "y"]], pd.read_csv(R / "expA_primary/tables/expA3_cells.csv")[["instance", "p", "N", "y"]]]
    tp = R / "s6/tp_cells.csv"
    if tp.exists(): d = pd.read_csv(tp); fr.append(d[["instance", "p", "N", "y"]])
    a = pd.concat(fr); M = a[a.N.isin([64, 256, 1024])].pivot_table(index=["instance", "p"], columns="N", values="y").reset_index().sort_values("instance")
    L = ["\\begin{longtable}{lrrrr}", "\\caption{$\\bar y$ per problem and budget (positive: reduced basis better).}\\label{tab:S-perproblem}\\\\", "\\toprule", "Problem & $p$ & $N{=}64$ & $N{=}256$ & $N{=}1024$ \\\\", "\\midrule", "\\endhead"]
    for _, r in M.iterrows(): L.append(f"\\texttt{{{r.instance.replace('_', chr(92) + '_')}}} & {int(r.p)} & {r[64]:.2f} & {r[256]:.2f} & {r[1024]:.2f} \\\\")
    L += ["\\bottomrule", "\\end{longtable}"]; (OUT / "tab_perproblem.tex").write_text("\n".join(L) + "\n"); mac("n_perproblem_rows", fi(len(M)))


if __name__ == "__main__":
    part1(); problems_table(); versions(); earlier_table(); per_problem_table()
    try:
        sys.path.insert(0, str(pathlib.Path(__file__).parent)); import aggregate_s6; aggregate_s6.part2(sys.modules[__name__])
    except ImportError: print("Stage 6 aggregation not available yet")
    (OUT / "macros.tex").write_text("% generated by code/experiments/aggregate.py -- do not edit\n" + "\n".join(f"\\newcommand{{\\{k}}}{{{v}}}" for k, v in sorted(MAC.items())) + "\n"); print(len(MAC), "macros")
