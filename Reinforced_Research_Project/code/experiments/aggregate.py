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
    mac("fom_median_ms", fd(1000 * float(np.median(fom)), 1)); mac("fom_n", fi(len(fom)))
    lk = R / "leakage_planted_test.json"
    if lk.exists():
        L = J(lk); mac("leak_max_matches", fi(L["max_exact_matches"])); mac("leak_planted_flagged", fi(L["planted"]["exact_matches_flagged_with_leak"])); mac("leak_error_ratio", fd(L["planted"]["error_on_non_leaked_samples"] / L["planted"]["error_on_leaked_samples"], 0))


if __name__ == "__main__":
    part1()
    try:
        sys.path.insert(0, str(pathlib.Path(__file__).parent)); import aggregate_s6; aggregate_s6.part2(sys.modules[__name__])
    except ImportError: print("Stage 6 aggregation not available yet")
    (OUT / "macros.tex").write_text("% generated by code/experiments/aggregate.py -- do not edit\n" + "\n".join(f"\\newcommand{{\\{k}}}{{{v}}}" for k, v in sorted(MAC.items())) + "\n"); print(len(MAC), "macros")
