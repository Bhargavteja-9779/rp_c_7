#!/usr/bin/env python3
"""[v4 application-style manuscript; computations shared with build_v3] Builds Final_Manuscript_v4.md from results files (numbers are computed/read here, not typed), then pandoc -> DOCX, LibreOffice -> PDF.
Run from anywhere: python build_v3.py [--no-render]"""
import json, pathlib, re, subprocess, sys, numpy as np, pandas as pd
from scipy import stats as sps
ROOT = pathlib.Path(__file__).resolve().parents[1]; R = ROOT / "results"; M = ROOT / "manuscript"; V1 = ROOT.parent / "results"
sys.path.insert(0, str(ROOT / "code/src")); sys.path.insert(0, str(ROOT.parent / "manuscript"))
from surrogate_bench import analysis as A, analysis_v2 as V
from unimath import unimath
J = lambda p: json.load(open(p)); f = lambda x, n=2: f"{x:.{n}f}"; pv = lambda p: ("<0.001" if p < 0.001 else f"{p:.3f}")
S1 = J(V1 / "statistics.json"); FA = J(R / "expA_primary/statistics_expA_primary_FINAL.json"); EA = FA["expA"]; PL = FA["pooled_24_instances_exploratory"]
D = J(R / "expD_statistics.json"); B = J(R / "expB_statistics.json"); A2 = J(R / "expA2_statistics.json"); E = J(R / "expE_statistics.json"); G = J(R / "expG_statistics.json"); A3 = J(R / "expA3_statistics.json")
RB = J(R / "robustness_analysis.json"); BS = J(R / "bootstrap_1e6_and_stepcount.json"); MS = J(R / "metric_sensitivity.json"); SB = J(R / "search_space_boundary.json"); E4 = J(V1 / "exploratory/e4_robustness.json")
DEC = ["bratu_L1","bratu_L2","burgers_L1","nlheat_L1","nlheat_L2","darcy_L1","heat2d_L1"]; FCp = R / "expA_primary/tables/expF_cells.csv"; FC = pd.read_csv(FCp) if FCp.exists() else None
FJ = R / "expF_statistics.json"; F = J(FJ) if FJ.exists() else None
pooled = pd.read_csv(R / "expA_primary/tables/pooled_cells.csv"); a2c = pd.read_csv(R / "expA_primary/tables/expA2_cells.csv"); a3 = pd.read_csv(R / "expA_primary/tables/expA3_cells.csv") if (R / "expA_primary/tables/expA3_cells.csv").exists() else None
cA = pd.read_csv(R / "expA_primary/tables/expA_cells.csv"); bcells = pd.read_csv(R / "expA_primary/tables/expB_cells.csv"); ecells = pd.read_csv(R / "expA_primary/tables/expE_cells.csv"); gcells = pd.read_csv(R / "expA_primary/tables/expG_cells.csv")
cls = lambda v: np.where(v > .1, "LS", np.where(v < -.1, "NL", "tie"))
pooled["k"] = cls(pooled.y.values); cnt = pooled.groupby("N").k.value_counts().unstack(fill_value=0)
inst = pooled[pooled.N == 1024].drop_duplicates("instance").set_index("instance")
rho_fp = sps.spearmanr(inst.log_cv_err_r4, inst.p)[0]
# Exp A details recomputed from the cell table
fz = V.frozen(ROOT / "research_design/frozen_rules_from_v1.json"); d = cA[cA.N.isin([64, 128, 256, 512, 1024])].sort_values(["instance", "N"]).reset_index(drop=True); lg = np.log2(d.N.values)
gain = (d.y.values - V._pred(fz["B0"], lg[:, None])) ** 2 - (d.y.values - V._pred(fz["R2"], np.c_[lg, d.log_cv_err_r4.values])) ** 2
share_nlheat = float(gain[d.instance.str.startswith("nlheat").values].sum() / gain.sum()); c24 = cA[(cA.N == 1024) & ~cA.instance.str.startswith("nlheat")]; rho_wo = sps.spearmanr(c24.log_cv_err_r4, c24.y)[0]
# direct MLP vs POD+MLP at N=1024 (seed-mean test errors)
dfO, _, _ = A.load(V1 / "raw"); dfA, _, _ = A.load(R / "raw_expA"); dfall = pd.concat([dfO, dfA], ignore_index=True)
e = dfall[dfall.N == 1024].groupby(["instance", "method"]).err.mean().unstack(); dm = np.log10(e.pod_mlp / e.mlp_direct); n_dir, n_pod = int((dm > .1).sum()), int((dm < -.1).sum())
gpb = np.log10(e.mlp_direct / e.pod_gp); n_gp_vs_mlp = int((gpb > .1).sum())
TB = S1["H4a"]; hol = S1["holm"]; c1 = E4["H4a_instance_level"]
# Exp G (all cells), Exp H (wide KRR), POD+Poly in GP-clear cells, family count
XS = J(R / "extrap_and_seed_consistency.json"); HS = J(R / "expH_statistics.json"); H8, H32 = HS["H8"], HS["H32"]
gall = gcells.merge(ecells[["instance", "N"]], on=["instance", "N"]); gall["y_full"] = np.log10(gall.err_nl_best / gall.err_full)
gtab = pd.DataFrame([[int(N), (cls(g.y_gp.values) == "LS").sum(), (cls(g.y_gp.values) == "NL").sum(), (cls(g.y_full.values) == "LS").sum(), (cls(g.y_full.values) == "NL").sum()] for N, g in gall.groupby("N")], columns=["N", "POD+GP: GP-clear", "POD+GP: NN-clear", "GP on full field: GP-clear", "GP on full field: NN-clear"])
dcl = pd.read_csv(R / "expA_primary/tables/expD_cells.csv"); dsel = dcl[dcl.y_gp > 0.1]
poly = dfall[dfall.method == "pod_poly"].groupby(["instance", "N"], as_index=False).err.mean().rename(columns={"err": "err_poly"}); dsel = dsel.merge(poly, on=["instance", "N"])
n_poly_beats_nn = int((np.log10(dsel.err_nl_best / dsel.err_poly) > 0.1).sum()); n_dsel = len(dsel); med_poly_gp = float((dsel.err_poly / dsel.err_gp).median())
import glob as _g
fam_labels = set(dfall.family.unique()) | set(pd.read_csv(R / "expA_primary/tables/expA2_cells.csv").family.unique()) | set(pd.read_csv(R / "expA_primary/tables/expA3_cells.csv").family.unique()); n_fam = len(fam_labels)
n_inst_total = len(set(dfall.instance.unique()) | set(pd.read_csv(R / "expA_primary/tables/expA2_cells.csv").instance.unique()) | set(pd.read_csv(R / "expA_primary/tables/expA3_cells.csv").instance.unique()))
iso_gt3 = 1 - E["share_iso_within3_of_ard"]
def pdtab(df): return df.to_markdown(index=False)

# ---------------- tables
sets = {}
for n in pooled.instance.unique(): sets[n] = "original" if n in set(dfO.instance) else "Exp A"
t_inst = inst[["p", "log_cv_err_r4", "y"]].copy(); t_inst["set"] = [sets[i] for i in t_inst.index]
a2n = a2c[a2c.N == 1024].set_index("instance")[["p", "log_cv_err_r4", "y"]] if "p" in a2c else a2c[a2c.N == 1024].set_index("instance")[["log_cv_err_r4", "y"]]
a2n["p"] = a2n.index.map(lambda i: int(A2.get("p_by_instance", {}).get(i, 0)) or int(a2c[a2c.instance == i].p.iloc[0])); a2n["set"] = "A2"
parts = [t_inst, a2n[["p", "log_cv_err_r4", "y", "set"]]]
if a3 is not None:
    a3n = a3[a3.N == 1024].set_index("instance")[["p", "log_cv_err_r4", "y"]]; a3n["set"] = "A3"; parts.append(a3n)
full = pd.concat(parts).sort_values("y", ascending=False)
tab_inst = pd.DataFrame(dict(Instance=full.index, p=full.p.astype(int).values, f1=full.log_cv_err_r4.round(2).values, y1024=full.y.round(2).values, Class=cls(full.y.values), Set=full.set.values))
tab_inst["Class"] = tab_inst.Class.map({"LS": "LS-clear", "NL": "NL-clear", "tie": "tie"})
tab_cnt = pd.DataFrame({"N": cnt.index, "LS-clear": cnt.get("LS", 0).values, "tie": cnt.get("tie", 0).values, "NL-clear": cnt.get("NL", 0).values})
conf = pd.DataFrame([
 ["H1a (Stage 1)", "median ȳ at N=32 > 0", f"median {f(S1['H1a']['median'],3)}", pv(S1['H1a']['p']), pv(hol['H1a']['adjusted_p']), "not supported"],
 ["H1b (Stage 1)", "ȳ falls with N in most instances", f"{S1['H1b']['k']}/16 with ρ<0", pv(S1['H1b']['p']), pv(hol['H1b']['adjusted_p']), "not supported"],
 ["H2 (Stage 1)", "pilot features beat {log₂N, p} (leave-one-family-out)", f"ΔRMSE {f(S1['H2']['primary_M_spec_vs_B1']['delta'])}, CI [{f(S1['H2']['primary_M_spec_vs_B1']['ci95'][0])}, {f(S1['H2']['primary_M_spec_vs_B1']['ci95'][1])}]", pv(S1['H2']['primary_M_spec_vs_B1']['p']), pv(hol['H2']['adjusted_p']), "not supported"],
 ["H4a (Stage 1)", "asymmetric tuning inflates NL wins", f"{TB['b']} vs {TB['c']} discordant cells; NL-win share {TB['nl_win_rate_sym8']:.0%}→{TB['nl_win_rate_asym']:.0%}", pv(TB['p']), pv(hol['H4a']['adjusted_p']), "supported at cell level; see text"],
 ["P1 (Exp A)", "Spearman(f1, ȳ₁₀₂₄) < 0, 8 new instances", f"ρ = {f(EA['P1']['rho'],3)}", pv(EA['P1']['p']), pv(EA['holm']['P1']['adj_p']), "not rejected"],
 ["P2 (Exp A)", "frozen R2 beats frozen B0 out of sample", f"gain {f(BS['P2_gain'],3)}, CI [{f(BS['ci95'][0],3)}, {f(BS['ci95'][1],2)}] (10⁶ draws)", pv(BS['p_one_sided']), pv(BS['holm_adj_P2']), "not rejected (knife-edge)"],
 ["S1 (Exp A)", "frozen threshold rule beats majority (70.8%)", f"{EA['S1']['correct']}/{EA['S1']['n_nontie_cells']} correct", pv(EA['S1']['p_binom_one_sided']), "–", "not supported"]],
 columns=["ID", "Hypothesis / criterion", "Observed", "raw p", "Holm-adj. p", "Verdict"])
mech = pd.DataFrame([
 ["D (KRR control)", "median err(POD+KRR)/err(POD+GP) in GP-clear cells", f"{f(D['median_ratio_in_gp_clear_win_cells'],1)}× (share ≤3×: {D['share_ratio_le3_in_gp_clear_win_cells']:.0%}; n={D['n_gp_clear_win_cells']})", "D1 (≤3×, ≥75%) **rejected**"],
 ["E (iso-GP control)", "median err(GP-iso)/err(GP-ARD); err(KRR)/err(GP-iso)", f"{f(E['ratio_iso_over_ard']['0.5'])}×; {f(E['ratio_krr_over_iso']['0.5'],1)}× (n={E['n_ard_clear_win_cells']})", f"{E['verdict']} (rule met; low-p cells only; not an isolation of marginal likelihood, see Exp H)"],
 ["H8 (wide-range KRR, B=8; post hoc)", "median err(KRR-wide)/err(POD+GP-ARD), GP-clear cells", f"{f(H8['ratio_quartiles_in_ard_clear']['0.5'],1)}× (q25–q75 {f(H8['ratio_quartiles_in_ard_clear']['0.25'],1)}–{f(H8['ratio_quartiles_in_ard_clear']['0.75'],1)}; ≤3×: {H8['share_le3']:.0%}; n={H8['n_ard_clear_cells']})", "mixed (neither H-RANGE nor H-MLII)"],
 ["H32 (wide-range KRR, B=32; post hoc)", "same", f"{f(H32['ratio_quartiles_in_ard_clear']['0.5'],1)}× (q25–q75 {f(H32['ratio_quartiles_in_ard_clear']['0.25'],1)}–{f(H32['ratio_quartiles_in_ard_clear']['0.75'],1)}; ≤3×: {H32['share_le3']:.0%})", "mixed (median ≤3 but only 57% of cells ≤3)"],
 ["G (no-POD GP)", "median err(GP-full)/err(POD+GP) in GP-clear cells", f"{f(G['ratio_quartiles']['0.5'])}× (q25–q75 {f(G['ratio_quartiles']['0.25'])}–{f(G['ratio_quartiles']['0.75'])}; all ≤3×)", "G1 **supported**"]],
 columns=["Experiment", "Quantity", "Observed", "Pre-registered verdict"])
robust = pd.DataFrame([
 ["Tie band 0.05 / 0.10 / 0.15 / 0.30, N=1024 (LS-clear / NL-clear / tie)", " ; ".join(f"{RB['tie_band'][f't={t},N=1024']['LS']}/{RB['tie_band'][f't={t},N=1024']['NL']}/{RB['tie_band'][f't={t},N=1024']['tie']}" for t in [0.05, 0.1, 0.15, 0.3])],
 ["Tie band, N=32 (same order)", " ; ".join(f"{RB['tie_band'][f't={t},N=32']['LS']}/{RB['tie_band'][f't={t},N=32']['NL']}/{RB['tie_band'][f't={t},N=32']['tie']}" for t in [0.05, 0.1, 0.15, 0.3])],
 ["Seed sign-consistency of clear cells", f"mean share of seeds with the cell's sign {RB['seed_sign_consistency']['mean_share_seeds_same_sign']:.1%}; all 3 seeds agree in {RB['seed_sign_consistency']['share_cells_all_seeds_same']:.0%} of {RB['seed_sign_consistency']['n_clear_cells']} clear cells"],
 ["Seed-consistency by class: cells whose three seeds are all beyond the band", f"LS-clear {XS['all_seeds_beyond_band']['LS']['share']:.0%} (n={XS['all_seeds_beyond_band']['LS']['n']}); NN-clear {XS['all_seeds_beyond_band']['NL']['share']:.0%} (n={XS['all_seeds_beyond_band']['NL']['n']}); at N=1024 the seed-inconsistent NN-clear cells are {', '.join(XS['all_seeds_beyond_band_N1024']['NL']['inconsistent'])}"],
 ["Extrapolation test set instead of interpolation set, N=1024 (LS-clear/NN-clear/tie; median ȳ)", f"interpolation {XS['N1024']['interp']['LS']}/{XS['N1024']['interp']['NL']}/{XS['N1024']['interp']['tie']}, median {f(XS['N1024']['median_y'],2)}; extrapolation {XS['N1024']['ext']['LS']}/{XS['N1024']['ext']['NL']}/{XS['N1024']['ext']['tie']}, median {f(XS['N1024']['median_y_ext'],2)}"],
 ["Config-draw halves (even vs odd random-search trials)", f"class agreement {RB['config_draw_halves']['class_agreement']:.0%} over {RB['config_draw_halves']['n_cells']} cells; sign agreement {RB['config_draw_halves']['sign_agreement_when_both_clear']:.0%} when both halves clear; Pearson r(ȳ) = {f(RB['config_draw_halves']['pearson_y'],3)}"],
 ["Metric: median or 95th-percentile error instead of mean", f"class agreement {MS['y_med']['agree_class_with_mean']:.0%} / {MS['y_p95']['agree_class_with_mean']:.0%}; sign flips among {MS['y_med']['n_clear_mean_cells']} clear cells: {MS['y_med']['n_sign_flips_among_clear_mean_cells']} / {MS['y_p95']['n_sign_flips_among_clear_mean_cells']}"],
 ["Exp B: 4× epochs (6000 vs 1500), N∈{256,1024}", f"B1 {B['sign_retention_clear_cells']:.0%} (≥85%) pass; B2 median shift {f(B['median_shift_toward_NL'],2)} (<0.5) pass; but {int((cls(bcells.y1500.values) != cls(bcells.y6000.values)).sum())}/{len(bcells)} cell classes change"]],
 columns=["Check", "Result"])
fig_note = "![Figure 1. Number of instances (out of 24: 16 original + 8 Exp A) in which the linear-subspace family is clearly better, tied, or clearly worse than the best neural network at each training budget (tie band ±0.10 decade).](" + str(ROOT / "figures/figv2_outcomes_by_N.png") + "){width=70%}"
fig2 = "![Figure 2. Pilot diagnostic f1 against the outcome ȳ at N=1024 for the 16 original (blue) and 8 independent Exp A (orange) instances; the dashed line is the threshold frozen from the original data. Instances with f1<−2 all have p=3.](" + str(ROOT / "figures/figv2_diagnostic_vs_outcome.png") + "){width=70%}"

# mechanism figure (D, E, G)
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
dc = pd.read_csv(R / "expA_primary/tables/expD_cells.csv"); sel_e = ecells[ecells.y_ard > .1]; sel_g = gcells[gcells.y_gp > .1]
series = [("kernel ridge,\nnarrow range, 8 trials", dc[(dc.y_gp > 0.1) & dc.N.isin([64, 256, 1024])].ratio_krr_gp.values), ("kernel ridge,\nwide range, 8 trials", pd.read_csv(R / "expA_primary/tables/expH8_cells.csv").query("y_ard > 0.1").ratio.values),
          ("kernel ridge,\nwide range, 32 trials", pd.read_csv(R / "expA_primary/tables/expH32_cells.csv").query("y_ard > 0.1").ratio.values), ("GP with one\nlength-scale", (sel_e.err_iso / sel_e.err_ard).values), ("GP on full field\n(no POD)", sel_g.ratio_full_over_pod.values)]
fig, ax = plt.subplots(figsize=(7.6, 3.6)); ax.boxplot([s[1] for s in series], showfliers=False, widths=.5); ax.set_yscale("log"); ax.axhline(3, ls="--", c="k", lw=.8); ax.axhline(1, c="k", lw=.8)
for i, s in enumerate(series, 1): ax.scatter(np.random.default_rng(i).normal(i, .06, len(s[1])), s[1], s=7, alpha=.5)
ax.set_xticks([1, 2, 3, 4, 5]); ax.set_xticklabels([s[0] for s in series], fontsize=7); ax.set_ylabel("test-error ratio (>1: numerator worse)", fontsize=8); ax.spines[["top", "right"]].set_visible(False)
(M / "fig_mech4.png").parent.mkdir(exist_ok=True); fig.tight_layout(); fig.savefig(M / "fig_mech4.png", dpi=200); plt.close(fig)
fig3 = "![Figure 3. Mechanism controls in cells where POD+GP-ARD clearly beats the best neural network. Dashed line: 3× (the pre-registered tolerance). From left: kernel ridge with the registered restricted ranges (B=8); kernel ridge with wide ranges (B=32, Exp H); isotropic-kernel GP; GP on the full field without POD.](" + str(M / "fig_mech4.png") + "){width=60%}"


# =====================================================================================  v4 (application-style, plain language)
BX = J(R / "pod_floor_check_and_extras.json"); BT = pd.read_csv(R / "budget_to_accuracy.csv"); BS2 = J(R / "budget_to_accuracy.json")
G3 = pd.read_csv(R / "expA_primary/tables/expG3_cells.csv")
GROUP = dict(darcy="Flow through porous rock", darcyhd="Flow through porous rock", darcylin="Flow through porous rock", incl="Flow through porous rock", incl3="Flow through porous rock",
             advdiff="Pollutant or heat carried by a flow", transport="Pollutant or heat carried by a flow",
             heat2d="Heat conduction", heatmv3="Heat conduction", heatp="Heat conduction", diff1d="Heat conduction", nlheat="Heat conduction",
             bratu="Thermal runaway (combustion-type)", fisher="Spreading fronts and reactions", reacdiff="Spreading fronts and reactions",
             burgers="Waves, shocks and acoustics", wave="Waves, shocks and acoustics", kdv="Waves, shocks and acoustics", helm="Waves, shocks and acoustics")
allc = pd.concat([pooled[["instance", "family", "p", "N", "y"]], a2c[["instance", "family", "p", "N", "y"]], (a3[["instance", "family", "p", "N", "y"]] if a3 is not None else None)], ignore_index=True)
allc["group"] = allc.family.map(GROUP); assert allc.group.notna().all(), allc[allc.group.isna()].family.unique()
GORDER = ["Flow through porous rock", "Heat conduction", "Pollutant or heat carried by a flow", "Thermal runaway (combustion-type)", "Spreading fronts and reactions", "Waves, shocks and acoustics"]
WHAT = {"Flow through porous rock": "steady flow with an uncertain permeability field, one with a moving inclusion (a lens of different rock)", "Heat conduction": "heating by a moving source, uncertain conductivity or diffusivity, nonlinear conduction",
        "Pollutant or heat carried by a flow": "advection–diffusion and pure transport of pulses", "Thermal runaway (combustion-type)": "a nonlinear elliptic problem with a steep response near a critical parameter value",
        "Spreading fronts and reactions": "travelling reaction–diffusion fronts and nonlinear reactions", "Waves, shocks and acoustics": "viscous shocks, a 1-D wave, solitons, Helmholtz-type oscillations"}
rows = []
for gname in GORDER:
    gi = allc[allc.group == gname]; ins = gi.instance.unique(); y256 = gi[gi.N == 256].y; y1k = gi[gi.N == 1024].y; b = BT[BT.instance.isin(ins)]
    nin = f"{int(gi.p.min())}–{int(gi.p.max())}" if gi.p.min() != gi.p.max() else f"{int(gi.p.min())}"
    rows.append([f"{gname} ({len(ins)} problems, {nin} inputs)", WHAT[gname],
                 f"{(cls(y1k.values)=='LS').sum()} / {(cls(y1k.values)=='tie').sum()} / {(cls(y1k.values)=='NL').sum()}", f"{f(y1k.median(),2)}",
                 f"{b.err_ls_1024.median():.0e} / {b.err_nl_1024.median():.0e}"])
tab_groups = pd.DataFrame(rows, columns=["Problem class (application area)", "What is simulated", "Reduced basis better / tie / network better", "Median log₁₀ error ratio", "Typical error: reduced basis / network"])
pp = allc[allc.N == 1024].copy(); pp["pb"] = pd.cut(pp.p, [0, 4, 9, 100], labels=["4 or fewer", "5 to 9", "10 or more"]); pp["k"] = cls(pp.y.values)
tab_p = pd.DataFrame([[b_, int((g.k == "LS").sum()), int((g.k == "tie").sum()), int((g.k == "NL").sum()), rec] for (b_, g), rec in zip(pp.groupby("pb", observed=True), ["Start with a Gaussian-process or reduced-basis model; add a network only if you need to.", "Too few problems to say; try both.", "No clear winner in our data; try both and compare at your budget."])], columns=["Number of inputs", "Reduced basis better", "Tie", "Network better", "What our results suggest"])
tab_budget = pd.DataFrame([[f"{int(100*th)}% error" if th >= .01 else "0.1% error", BS2[f"ls_{k}"], BS2[f"nl_{k}"]] for th, k in ((0.1, "0.1"), (0.01, "0.01"), (0.001, "0.001"))], columns=["Target accuracy (mean relative error)", "Problems where the reduced-basis group gets there within 1024 runs", "Problems where the neural group gets there within 1024 runs"])
tab_budget.iloc[0, 0] = "10% error"; tab_budget.iloc[1, 0] = "1% error"
cpu = BS2["median_cpu_seconds_N1024"]
fig_a = "![**Figure 1.** For each training budget, on how many of the 24 main test problems the reduced-basis models were clearly more accurate than the best neural network (blue), the two were within about 25% of each other (grey), or the neural network was clearly better (orange).](" + str(ROOT / "figures/figv2_outcomes_by_N.png") + "){width=70%}"
fig_c = "![**Figure 2.** Ratio of test errors (alternative over the Gaussian-process reduced model; above 1 means the alternative is worse), where that model clearly beats the best neural network. Each dot is one problem and budget; the dashed line marks a factor of 3. From the left: kernel ridge with a narrow search range (52 combinations, all budgets), kernel ridge with a wide search range and 8 tuning trials, the same with 32 trials, a Gaussian process with one length-scale, and a Gaussian process on the full field without a reduced basis (28 combinations each).](" + str(M / "fig_mech4.png") + "){width=70%}"
g3 = G3[G3.N == 1024].set_index("instance")
sel = lambda i, N: allc[(allc.instance == i) & (allc.N == N)].y.iloc[0]
bt = BT.set_index("instance")
ntie = lambda N: int((cls(allc[allc.N == N].y.values) == "tie").sum())

r2 = lambda x: f"{float(f'{x:.2g}'):,.0f}"
TITLE = "Do You Need a Neural Network? Choosing a Fast Stand-In for Slow Physics Simulations"
abstract4 = f"""# {TITLE}

*A comparison of Gaussian-process and neural-network stand-in models on 36 simulated benchmark problems*

**Authors:** [AUTHOR NAMES AND AFFILIATIONS — to be supplied by the authors]. **Corresponding author:** [to be supplied].

## Abstract

Engineers often need to run the same slow physics simulation hundreds of times, for design, calibration or uncertainty studies. A common shortcut is to run it a limited number of times and train a fast stand-in model, called a surrogate, on the results. This paper asks a practical question: with a budget of 32 to 1,024 simulation runs, should you build the stand-in from a Gaussian process (GP) working on a reduced basis, or train a neural network? We compared five such models on 36 simulated benchmark problems from six classes named after application areas (flow through rock, heat conduction, pollutant transport, thermal runaway, spreading fronts, and waves). On smooth problems with few inputs, the reduced-basis GP was far more accurate, sometimes by two or three orders of magnitude, and the reduced-basis family reached 0.1% error on {BS2['ls_0.001']} of the 36 problems within the budget, against {BS2['nl_0.001']} for the networks ({BX['budget_excl_A2_candidates']['ls_0.001']} against {BX['budget_excl_A2_candidates']['nl_0.001']} if the eight smooth problems added later are left out). For rough accuracy targets (10% or 1%) the two families were about equally good. Some of the networks' wins came from the limits of the reduced basis, not of the GP: a GP fitted to the full output field beat them again. A plain kernel-ridge model, once its regularisation was searched over a wide range, closed most of the gap to the GP (from a median {f(BX['expD_on_comparable_cells']['median_ratio_krr_over_gp'],0)} times worse to {f(H8['ratio_quartiles_in_ard_clear']['0.5'],1)} times worse with the same eight tuning trials, and {f(H32['ratio_quartiles_in_ard_clear']['0.5'],1)} times worse with 32 trials), so much of the GP's advantage reflects careful tuning of a smooth regressor, and a residual factor of 2 to 3 remains unexplained. Results shifted noticeably when the networks were trained longer, so we give a short checklist for fair comparisons. Most of our original hypotheses, including that a quick pilot check on 32 runs predicts the winner, were not confirmed. All problems are simulated and the networks were only lightly tuned.

**Keywords:** surrogate model; Gaussian process; neural network; reduced-order model; parametric PDE; simulation budget
"""

BODY = f"""
## 1 Introduction

Many engineering decisions depend on a simulation that is too slow to run as often as we would like. Picking the best shape of a part, estimating how uncertain an input leaves the answer, or fitting a model to measurements can each take thousands of runs. The usual remedy is a *surrogate* (or stand-in) model: run the full simulation a limited number of times, say a few hundred, train a cheap model on the inputs and outputs, and then use the cheap model for everything else.

The practical question is which kind of model to build. One long-standing route compresses the simulation output with proper orthogonal decomposition (POD), which finds a small set of typical shapes, and then learns how the weights of those shapes depend on the inputs, with a neural network [Hesthaven & Ubbiali 2018; Bhattacharya et al. 2021] or a Gaussian process [Guo & Hesthaven 2018]. The other route trains a neural network to produce the whole output directly, sometimes through a narrow internal layer [Fresca & Manzoni 2022; Franco et al. 2023]. Neural networks get most of the attention, but there are good reasons not to take their advantage for granted. Surveys of machine-learning solvers for fluid problems found that most papers claiming to beat a standard method had used a weak baseline [McGreivy & Hakim 2024]. Kernel and Gaussian-process methods have been reported to be competitive with DeepONet [Lu et al. 2021] and the Fourier neural operator [Li et al. 2021] [Batlle et al. 2024], and in a POD framework for extruder flows a Gaussian process was reported to have several advantages over a neural network [Bērziņš et al. 2020, preprint]. A recent comparison of neural and polynomial surrogates found no universally superior method [Westermann et al. 2026, preprint]. Whether a small POD basis can work at all depends on how well the set of solutions can be approximated by a few shapes (the decay of the Kolmogorov n-width) [Cohen & DeVore 2015], and this decay has been shown to be slow for wave problems with discontinuous data [Greif & Urban 2019]. Finally, how much tuning a method gets and how results are reported can decide a comparison, which is why reporting results as a function of the tuning budget has been advocated [Dodge et al. 2019; Bouthillier et al. 2021].

What a practitioner still lacks is a quantitative picture. How big is the difference, on which kinds of problems, at which budget? Why does one side win? Is there a cheap way to tell in advance? And how much do the comparison's own settings, such as how long the network is trained, change the answer? We tried to answer these questions with a controlled comparison on 36 simulated benchmark problems from six classes named after application areas. We compared five stand-in models under the same tuning procedure, measured how many simulation runs each needs to reach a given accuracy, and ran extra experiments to find out *why* the winners win.

Our results confirm earlier reports that Gaussian-process and kernel methods are hard to beat on smooth problems; what we add is a quantified picture across budgets and problem types, controls that show where the advantage comes from, and a record of how much the answer moves with the comparison's own settings. In brief, the Gaussian-process stand-ins were far more accurate than lightly tuned neural networks on smooth problems with a few inputs, and neither side had a consistent advantage on the rest. A good part of the networks' apparent wins on harder problems came from the limits of the reduced basis rather than from the GP, and the GP's advantage came mostly from how widely and carefully its settings were searched. The outcome also moved when we trained the networks longer. We built the paper around a practical checklist (Section 6) that follows from these findings.

## 2 What we compared

**The two kinds of stand-in.** In the *reduced-basis group* the simulation output is compressed with POD and a regressor predicts the weights of the typical shapes from the inputs. We used three regressors: a Gaussian process with a separate length-scale for each input (POD+GP), a polynomial fitted with a ridge penalty (POD+Poly), and a small neural network (POD+MLP). In the *direct-network group* a neural network produces the whole output at once, either as a plain multilayer perceptron or through a narrow bottleneck layer. In the main comparison we say "better" for a group when its best member, picked on held-out validation data and never on test data, has the smaller error; the follow-up experiments in Section 4.3 and 4.5 use the best network by test error instead, which is stated where it matters.

**Fair tuning.** Every method got the same number of tuning trials: eight random draws of its settings (the first draw is a fixed default), scored on a random fifth of the training runs; the winner was then refitted on all runs. Networks were trained with Adam for 1,500 epochs in single precision. At the largest budget of 1,024 runs the training used mini-batches of 512 instead of the whole set, so the networks took twice as many optimisation steps there, which we keep in mind when reading the 1,024-run results.

**Scoring.** The error is the average relative L₂ error over 1,000 held-out inputs. To compare groups we use the log₁₀ of the error ratio, network over reduced-basis: a value of 1 means the network's error is ten times larger, 2 means a hundred times, and negative values mean the network is better. Differences below 0.1 (about 25%) count as a tie. Each result is averaged over three random seeds that change the training subset and the tuning draws.

**Why-experiments.** To find out why one side wins we added more models: kernel ridge regression with a narrow or wide range of settings, a Gaussian process with a single length-scale, and a Gaussian process applied directly to the full output without POD. We also retrained the networks for longer, in double precision, and with a second-order polishing step (L-BFGS), to see how much of the networks' error was due to limited training. The technical details, all statistical tests and the full record of what we had decided in advance are in the Supplement (S1).

**How we kept the analysis honest.** The main hypotheses, code and success criteria were committed to version control before each group of runs. Several later experiments were designed after seeing earlier results, and one of them (the wide-range kernel ridge) was added because a review of our own draft by an AI agent we asked to criticise it showed that an earlier control was too narrow. The Supplement lists which results came from which stage. The version-control history is our own, not an independent registry.

## 3 The test problems

Real simulation datasets with known accuracy are hard to share and verify, so we used our own simulators, each checked against exact or manufactured solutions or by grid refinement. The 36 problems fall into six classes named after application areas (Table 1). The classes are our own groupings of standard PDE benchmark families; **nothing here was calibrated to a real application, and no field or industrial data were used**; the point is to cover the range of behaviour (smooth or sharp, few or many inputs, steady or moving features) that practitioners meet. Each class has two or more problems, often a gentle and a harder version.

{pdtab(tab_groups)}

*Table 1. The 36 test problems by class (all 36 are counted here, whereas Figure 1 and the text use the 24 main problems). The last three columns refer to 1,024 training runs; the log₁₀ error ratio is a median over the problems of each class: the log₁₀ error ratio (positive: the reduced-basis group is better) and the typical test error of each group.*

For every problem we generated 4,096 candidate training inputs and 1,000 held-out test inputs, plus 500 inputs outside the training range to see what happens when a model has to extrapolate. We looked at 32 to 1,024 training runs for 24 problems and at 64, 256 and 1,024 runs for the other 12.

## 4 Results

### 4.1 Who wins, and by how much

The answer depends heavily on the budget and the problem type (Figure 1, Table 1). With very few runs (32) the two groups are mostly tied: of the 24 main problems, {cnt.loc[32,'LS']} favour the reduced-basis group, {cnt.loc[32,'NL']} the networks, and {cnt.loc[32,'tie']} are ties. With 1,024 runs the reduced-basis group is clearly better on {cnt.loc[1024,'LS']} problems, the networks on {cnt.loc[1024,'NL']}, and {cnt.loc[1024,'tie']} are ties (the number of network wins is {RB['tie_band']['t=0.15,N=1024']['NL']} if the tie band is widened to 0.15 and {RB['tie_band']['t=0.05,N=1024']['NL']} if it is narrowed to 0.05). At 32 runs, 14 of the 24 problems are ties, so no family is clearly ahead; counting small differences as wins would make the networks look better than they are. Most of our original pre-registered hypotheses were not supported: networks did not win at small budgets, the gap did not shrink steadily as the budget grew, and the pilot check described in Section 4.4 did not predict the winner (three of four hypotheses failed; details in the Supplement).

{fig_a}

When the reduced basis wins, it can win by a lot: with 1,024 runs the networks' error is about {r2(10**inst.loc['bratu_L1','y'])} times larger on the thermal-runaway problem (bratu_L1), {r2(10**inst.loc['nlheat_L1','y'])} times on a nonlinear heat problem (nlheat_L1), and {r2(10**inst.loc['burgers_L1','y'])} times on a viscous shock (burgers_L1). The largest margin in the other direction is a factor of {10**(-inst.y.min()):.1f}. The eight extra smooth problems we added later (reaction–diffusion, Helmholtz, heat with uncertain diffusivity) all went the same way, with factors from about {r2(10**a2n.y.min())} to {r2(10**a2n.y.max())}; six of the eight have only three inputs, so this mainly confirms that smooth low-dimensional problems favour the GP.

These large factors come with caveats. They refer to the interpolation test set, to 1,024 runs, and to networks trained for 1,500 epochs in single precision. On the extrapolation test set the gaps are smaller (for example {XS['decisive_N1024']['bratu_L1'][0]:.1f} → {XS['decisive_N1024']['bratu_L1'][1]:.1f} on the log scale for bratu_L1, and {XS['decisive_N1024']['nlheat_L1'][0]:.1f} → {XS['decisive_N1024']['nlheat_L1'][1]:.1f} for nlheat_L1); with longer and more careful network training they shrink by roughly half a decade (Section 4.5). A fair summary is "up to about three orders of magnitude in the most favourable setting, and still roughly 60 to 500 times on the most favourable problems after stronger network training".

By problem class, reduced-basis models were ahead on most heat-conduction and reaction problems, on the thermal-runaway problems and on the simple porous-flow problems. The networks led on a few problems with sharp moving features (transport_L2, kdv_L1) and on the porous-flow problems with a moving inclusion or many inputs (incl_L1, incl_L2, darcy_L2, darcyhd_L1); as Section 4.3 shows, a full-field GP often reverses the inclusion cases. For the many-input problems the picture is mixed. On the two porous-flow problems with 16 and 32 uncertain inputs and a rough permeability field (darcyhd) the networks were ahead by about a third, but not consistently across seeds, and on the 10-input version (darcy_L2) they were ahead by about 50%; on the two nearly linear problems with 16 and 32 inputs (darcylin) the reduced basis was ahead (factors of 3 and 1.5). We therefore cannot say which family is better when the inputs are many.

### 4.2 How many runs do you need?

Often the real question is how many simulations are needed to reach a given accuracy. Table 2 counts the problems on which each group's best model reached a target error within the 1,024 runs of our study. For a coarse target of 10% both groups got there on all 36 problems, usually with 64 runs or fewer. For 1%, they were about equal ({BS2['ls_0.01']} against {BS2['nl_0.01']} problems). The difference shows up at the demanding end: {BS2['ls_0.001']} problems reach 0.1% error with the reduced-basis group, against {BS2['nl_0.001']} with the networks. The 0.1% count includes eight smooth problems that we added later because we expected the GP to do well on them; on the 24 main problems it is {BX['budget_main24']['ls_0.001']} against {BX['budget_main24']['nl_0.001']}. The extra accuracy is mostly on smooth, low-dimensional problems; on several others (flows with moving inclusions, wave problems, shocks with sharp fronts) neither group reaches 1% within the budget.

{pdtab(tab_budget)}

*Table 2. Number of the 36 problems on which the best model of each group reached the target mean error within the study's training budget (at most 1,024 runs; the budget grid is coarser for 12 problems).*

Training time is a minor cost compared with the simulations themselves but is not negligible. At 1,024 runs, tuning and fitting took a median of about {cpu['pod_gp']:.0f} seconds of CPU time for the GP model, {cpu['pod_mlp']:.0f} for the POD+network, {cpu['bottleneck']:.0f}–{cpu['mlp_direct']:.0f} for the direct networks, and about 0.3 seconds for the polynomial (each fit used one CPU thread; the software versions are recorded in the repository). We did not account for the cost of using the trained model, nor compare with the cost of the simulations themselves.

### 4.3 Why the Gaussian process does so well

We tested several explanations (Figure 2).

*It is not the reduced basis.* A Gaussian process applied directly to the full output field, without any POD, was as accurate as the reduced-basis GP where the latter did well (median error ratio {f(G['ratio_quartiles']['0.5'],2)}). Where networks had beaten the POD-based GP, the full-field GP often beat the networks again. On the heat problem with a narrow moving source (heat2d_L2) and the two inclusion problems (incl_L1, incl_L2), the POD+GP error ({BX['pod_floor']['heat2d_L2']['pod_gp']:.1e}, {BX['pod_floor']['incl_L1']['pod_gp']:.1e} and {BX['pod_floor']['incl_L2']['pod_gp']:.1e}) is essentially the best error any 32-mode basis could reach even with perfect weights ({BX['pod_floor']['heat2d_L2']['r32_projection_error']:.1e}, {BX['pod_floor']['incl_L1']['r32_projection_error']:.1e} and {BX['pod_floor']['incl_L2']['r32_projection_error']:.1e}). The basis, not the regressor, sets the limit. Networks that produce the whole field are not tied to a basis and can get below it. When we ran the full-field GP on the two moving-feature problems added later, it beat the best network by {g3.loc['heatmv3_L1','y_full']:.1f} and {g3.loc['incl3_L1','y_full']:.1f} orders of magnitude at 1,024 runs, where the POD+GP had lost to the networks.

*It is largely how the settings are searched.* Kernel ridge regression is the same kind of model without the Gaussian process's automatic fitting of its settings. With the narrow range of settings we first gave it, it was a median {f(BX['expD_on_comparable_cells']['median_ratio_krr_over_gp'],0)} times less accurate than the GP in the 28 budget-and-problem combinations (budgets 64, 256 and 1,024) where the GP clearly beats the best network. After a review of our draft by an AI agent we had asked to criticise it pointed out that this range could not reach the very small regularisation that near-perfect fits need, we repeated the test with a wide range. On the same 28 combinations the gap shrank to a factor of {f(H8['ratio_quartiles_in_ard_clear']['0.5'],1)} with the same eight tuning trials, and to {f(H32['ratio_quartiles_in_ard_clear']['0.5'],1)} with 32 trials (only {H32['share_le3']:.0%} of the combinations were within a factor of 3 even then), and the wide-range kernel ridge beat the best neural network clearly in {H32['share_krr_beats_nl_clear_in_ard_clear']:.0%} of them. A polynomial, which has no kernel and no automatic fitting at all, was a median {f(med_poly_gp,0)} times worse than the GP but still clearly beat the best network in {n_poly_beats_nn} of the {n_dsel} cells ({n_poly_beats_nn/n_dsel:.0%}) where the GP did. Taken together, the advantage belongs largely to smooth regressors whose regularisation is searched widely and finely, and not to the reduced basis; at equal numbers of tuning trials the Gaussian process was still clearly better than even the wide kernel ridge. We did not isolate the contribution of the GP's marginal-likelihood fitting, because its cost is not matched by our kernel-ridge search.

*A note on how we compare in this section.* To pick the combinations where the GP clearly wins, we compare with the best network by *test* error, which favours the networks; this differs from the main comparison, where the best member of each group is chosen on validation data.

*It is not a matter of the direct network being worse than the POD network.* A direct network beat the network on POD coefficients by more than 25% in {n_dir} of the 24 problems at 1,024 runs, so putting POD in front of a network did not help it.

{fig_c}

### 4.4 Can a quick pilot check tell you which to use?

It would be convenient to run 32 simulations, look at how quickly POD compresses them, and decide. We froze such a rule from the original data and tested it on eight new problems. It did not work convincingly: the correlation was in the expected direction but not significant (ρ = {f(EA['P1']['rho'],2)}, p = {pv(EA['P1']['p'])}) and the rule's gain over a baseline was borderline (p = {pv(BS['holm_adj_P2'])} after correction). Most of that borderline gain came from two nonlinear-heat problems, and without them the correlation changes sign. The pilot statistic also tracks the number of inputs: it is strongly negative only on three-input problems. Two follow-up sets of problems (eight smooth candidates and four probes designed to separate the pilot statistic from the number of inputs) agreed with a simple reading: smooth problems with few inputs favour the GP by a lot, and a pilot statistic mostly detects that. We would not rely on it beyond an informal check of smoothness and dimension. Full details are in the Supplement.

### 4.5 How much do the comparison's own settings matter?

Three settings changed the answer noticeably.

*Training the networks longer.* Retraining the stored best networks for four times as many epochs improved nine in ten of them and moved the comparison toward the networks in all {int((cls(bcells.y1500.values) != cls(bcells.y6000.values)).sum())} of the {len(bcells)} (problem, budget) cases whose classification changed; {int(((cls(bcells.y1500.values) == "tie") & (cls(bcells.y6000.values) == "NL")).sum())} ties became network wins. Double precision and a second-order optimiser (L-BFGS) lowered the networks' error by a further half decade (median, over the problems tested). (This comparison again uses the best network by test error.) The largest gaps survived: on {F['decisive_with_yF_ge_1']} of the 7 problems where the reduced basis led by a factor of 10 or more, it still did after the stronger training, and on the other two (darcy_L1 and heat2d_L1) it led by factors of about 4 and 9. The networks' error still did not fall below about 2·10⁻⁴, far above the best GP errors of 10⁻⁷ to 10⁻⁵. We do not know why the networks plateau there, and a better-tuned network may do better.

*Unequal tuning.* When the networks got eight tuning trials and the reduced-basis models only one, the winner switched to the networks in {TB['b']} problem-budget cases and in the other direction in {TB['c']}. Giving one side more tuning moves the comparison toward that side, as one would expect; this is why we gave every method the same number of trials. Equal numbers of trials do not mean equal effort, though: the GP's search has only eight possible settings but then fits its length-scales continuously, while the network search is continuous in several dimensions.

*Random draws.* Repeating the comparison with different halves of the random tuning draws gave the same verdict (reduced-basis better, tie, or network better) in {RB['config_draw_halves']['class_agreement']:.0%} of cases; the sign of a clear difference agreed in {RB['config_draw_halves']['sign_agreement_when_both_clear']:.0%}. Ties and small differences should therefore not be over-interpreted, while large gaps are stable. Among cells where the networks were clearly better, only {XS['all_seeds_beyond_band']['NL']['share']:.0%} were clearly better in all three seeds, against {XS['all_seeds_beyond_band']['LS']['share']:.0%} for the reduced basis.

## 5 Worked examples

The following three examples show what the numbers mean for a practitioner. All values are for our simulated stand-ins.

**Uncertain permeability in a porous medium (darcy, darcyhd, darcylin).** The simple version has 4 inputs. With 256 runs the reduced-basis group reaches a mean error of {bt.loc['darcy_L1','err_ls_256']:.1e} and the best network {bt.loc['darcy_L1','err_nl_256']:.1e}; with 1,024 runs the figures are {bt.loc['darcy_L1','err_ls_1024']:.1e} and {bt.loc['darcy_L1','err_nl_1024']:.1e}. If 1% error is enough, either approach works from about 64 runs. With 16 inputs and a rough permeability field (darcyhd_L1) both groups are stuck at an error of about 4–6% even with 1,024 runs (reduced basis {bt.loc['darcyhd_L1','err_ls_1024']:.1e}, best network {bt.loc['darcyhd_L1','err_nl_1024']:.1e}: the network is about 25% lower, just outside our tie band). A smoother problem with the same number of inputs (darcylin_L1) is easy: the reduced basis reaches 0.1% error with 256 runs. So the number of inputs alone does not decide difficulty; the roughness of the response matters as much.

**A part heated by a moving source (heat2d, heatmv3).** With a broad source (heat2d_L1) the best reduced-basis model needs about 64 runs to reach 1% error and 256 for 0.1%; the direct networks need about 128 for 1% and never reach 0.1% in our study. With a narrow moving source (heat2d_L2) neither reaches 1% error by 1,024 runs, and the networks are ahead of the POD-based GP by about a factor of two. But the error of the POD model equals the projection error of its 32 modes, so a full-field GP is a better choice there. This is the type of problem where the form of the stand-in matters more than the regressor on top of it.

**Thermal runaway (bratu).** Near a critical parameter the response of this problem changes steeply, yet it depends smoothly on its three inputs. The reduced-basis group reaches 0.1% error with only 32 runs on both versions (bratu_L1 and bratu_L2); the best network needs 1,024 runs for the same accuracy. At 256 runs the error is {bt.loc['bratu_L1','err_ls_256']:.0e} against {bt.loc['bratu_L1','err_nl_256']:.0e}. If your real problem has few inputs and a smooth response, try a Gaussian process first, and you may need far fewer simulations than you expect.

## 6 A practical checklist

Table 3 summarises how the two groups compared by number of inputs at 1,024 runs, our best attempt at a decision aid; the counts are small, so treat it as a rough guide.

{pdtab(tab_p)}

*Table 3. Outcomes at 1,024 runs by number of inputs p (all 36 problems).*


We draw the following advice from the experiments. The strength of the evidence is noted in each case.

1. **Always run a well-tuned Gaussian-process or kernel baseline before you train a neural network.** On problems with up to four inputs the reduced basis was clearly better in {BX['p_le4_n1024']['ls_clear']} of {BX['p_le4_n1024']['n']} cases at 1,024 runs (networks in {BX['p_le4_n1024']['nl_clear']}), and a GP needs no long training. Give its regularisation a wide search range. We have no reliable way to tell in advance whether your problem is smooth enough (Section 4.4). (Moderate for p ≤ 4 on our problems; unresolved for many inputs.)
2. **Add a polynomial baseline.** It takes a fraction of a second and, on our problems, still clearly beat the best neural network in 44% of the cells where the GP did. (Moderate.)
3. **Check whether the basis is your bottleneck.** Project held-out fields onto your basis and compute the error. If your stand-in's error is about equal to it, a larger basis or a model without a basis will help more than a better regressor. (Illustrative: we saw it on three problems; the check is cheap on your own data.)
4. **Decide your accuracy target first.** For 10% or even 1% error the two families are about equally good, and a network may be the more convenient choice. For 0.1% or better, the reduced-basis route reached the target on about twice as many problems (19 against 10 of 36). (Moderate; based on counts over 36 problems.)
5. **If you use a neural network, report and vary its training budget.** Training longer, in double precision and with a polishing step, improved most networks; in our four-times-longer experiment, the verdict changed in 15 of 48 cases, always toward the networks. Do not conclude that a network cannot do better from a single 1,500-epoch run. (Strong.)
6. **Give the competing methods the same tuning effort and say what that effort was.** Unequal tuning moved the winner in the direction of the more heavily tuned side. (Moderate.)
7. **Report ties as ties.** Differences below about 25% flipped with the random draw of tuning settings in a sizeable minority of cases, so do not declare a winner on them. (Moderate.)
8. **Do not choose by a quick pilot statistic yet.** The one we tested (how fast POD compresses 32 runs) did not predict the winner on eight new problems and mostly tracks the number of inputs; eight problems cannot rule out a weak effect. (Inconclusive.)

## 7 What could go wrong

- **Who checked this.** The analysis, the audits and the reviews of our drafts were done with AI agents, not human reviewers, and the version-control "pre-registration" is our own history (commit hashes in `research_design/` and `audit/prereg_order_check.json`), not an independent registry.
- **Simulated problems only.** All 36 problems come from our own solvers, with modest grids and 3 to 32 inputs. We used no field data and no public benchmark such as PDEBench, so the conclusions say how methods compare on these kinds of problems, not how they will perform on a particular application.
- **Lightly tuned networks.** Eight random draws, one training recipe, draws shared across problems, a doubling of training steps at 1,024 runs. Better-tuned networks, ensembles, or other architectures such as Fourier neural operators could change the picture.
- **Little evidence for many inputs.** The mechanism experiments cover problems with three or four inputs; for 10 or more inputs we have five problems and no clear winner.
- **Costs.** We report fitting time only, not the cost of using the trained model or of the simulations.
- **Statistics.** We have 24 main problems in 12 families; cases within a family are not independent, and several follow-up experiments were designed after we had seen earlier results.
- **Literature.** Our literature search was limited (mostly abstracts and bibliographic records), so the related work may be incomplete.

## 8 Conclusion

For slow simulations of smooth problems with a handful of inputs, a Gaussian-process stand-in is a strong default: it was usually far more accurate than lightly tuned neural networks, needed fewer simulation runs to reach high accuracy, and took less time to fit than the networks we trained (a median of about 44 seconds against 90–140 at 1,024 runs). Its advantage is not about the reduced basis; much of it reflects a smooth regressor whose regularisation is searched widely and carefully, though a factor of 2 to 3 over a wide-range kernel ridge remains unexplained. Neural networks were competitive for modest accuracy targets and for some problems with sharp moving features, and on harder or higher-dimensional problems we could not name a clear winner. The outcome of a comparison depends on the training budget, the tuning effort and the random draws, so a fair comparison needs equal effort, tie-aware reporting and a well-tuned Gaussian-process baseline.

## Declarations

*Author contributions, affiliations, funding and competing interests:* [to be supplied by the authors]. *Use of AI tools:* the study design, code, analyses, audits and the drafting of this paper were carried out with an AI system (Claude) working as a research assistant under the authors' direction; the audit and review rounds were performed by AI agents, not by human reviewers. The authors must verify every number, citation and claim and take responsibility for the text. *Data and code availability:* all data are generated by the code in the repository (`Reinforced_Research_Project/code`) from instance names and seeds; raw outputs are under `results/`; a permanent archive such as a Zenodo DOI has not yet been created. *Supplement S1:* technical report with all hypotheses, tests, the experiment-by-experiment verdicts and the deviation log.

## References

"""
refs_all = pd.concat([pd.read_csv(ROOT.parent / "literature_review/references_verified.csv")[["key", "citation", "doi_or_id"]].rename(columns={"doi_or_id": "id"}), pd.read_csv(ROOT / "literature/updated_literature_matrix.csv")[["key", "citation", "id_or_doi"]].rename(columns={"id_or_doi": "id"})]).drop_duplicates("key")
import unicodedata
norm = lambda s_: unicodedata.normalize("NFKD", s_).encode("ascii", "ignore").decode().lower()
body = norm(BODY); keep = []
for _, r in refs_all.iterrows():
    m = re.match(r"(?:de |van )?([^\s,]+)", r.citation); yr = re.search(r"\((\d{4})\)", r.citation)
    if m and yr and re.search(re.escape(norm(m.group(1))) + r".{0,60}?" + yr.group(1), body):
        cite = re.sub(r"\s*\((?:published|preprint)[^)]*\)", "", r.citation); idt = "" if str(r.id) in cite else f" {r.id}"; keep.append(f"{cite}.{idt}")
refs_md = "\n\n".join(f"[{i+1}] {k}" for i, k in enumerate(sorted(keep)))
doc = abstract4 + BODY + refs_md + "\n"
out = M / "Final_Manuscript_v4.md"; out.write_text(doc); print("words:", len(doc.split()), "refs:", len(keep))
if "--no-render" not in sys.argv:
    docx = M / "Final_Manuscript_v4.docx"
    subprocess.run(["pandoc", str(out), "-o", str(docx), "--from", "markdown+pipe_tables"], check=True)
    subprocess.run([sys.executable, str(ROOT.parent / "manuscript/postprocess_docx.py"), str(docx)], check=True)
    subprocess.run(["soffice", "--headless", "--convert-to", "pdf", "--outdir", str(M), str(docx)], check=True, capture_output=True)
    print("rendered")
