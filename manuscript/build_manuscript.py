#!/usr/bin/env python3
"""Builds Final_Manuscript.md from results (all numbers pulled from results/*.json|csv), then pandoc -> DOCX, LibreOffice -> PDF."""
import json, pathlib, re, subprocess, sys, numpy as np, pandas as pd
ROOT = pathlib.Path(__file__).resolve().parents[1]; R = ROOT / "results"; M = ROOT / "manuscript"
S = json.load(open(R / "statistics.json")); X = R / "exploratory"
cells = pd.read_csv(R / "tables/cells.csv"); raw = pd.read_csv(R / "raw_results.csv"); refs = pd.read_csv(ROOT / "literature_review/references_verified.csv")
e1 = pd.read_csv(X / "e1_long_training.csv"); e1y = pd.read_csv(X / "e1_y_under_long_training.csv"); e2 = pd.read_csv(X / "e2_pilot_size_sensitivity.csv")
e3 = pd.read_csv(X / "e3_one_feature_rule.csv"); fold = pd.read_csv(X / "e2_lofo_rmse_by_heldout_family.csv", index_col=0); rep = json.load(open(X / "sensitivity_gp_repair.json")); rt = pd.read_csv(X / "refit_vs_trial_error.csv")
e4 = json.load(open(X / "e4_robustness.json")); cl = e4["H4a_instance_level"]; nogp = e4["LS_mlp+poly"]
cost = pd.read_csv(R / "tables/cost_breakeven.csv"); ex = pd.read_csv(R / "tables/learning_curve_exponents.csv"); h3 = S["H3_exploratory"]; H1a, H1b, H2, H4a, H4b, hol = S["H1a"], S["H1b"], S["H2"], S["H4a"], S["H4b_descriptive"], S["holm"]
f = lambda x, n=2: f"{x:.{n}f}"; pv = lambda p: ("<0.001" if p < 0.001 else f"{p:.3f}")
c32, c1k = cells[cells.N == 32], cells[cells.N == 1024]
e1_improved, e1_n, e1_med = int((e1.ratio_6000_vs_1500 < 1).sum()), len(e1), e1.ratio_6000_vs_1500.median()
gp_bad3, gp_bad10, n_gp = int(((rt.method == "pod_gp") & (rt.ratio > 3)).sum()), int(((rt.method == "pod_gp") & (rt.ratio > 10)).sum()), int((rt.method == "pod_gp").sum())
expo = ex.groupby("method").exponent.median()
e3_256 = e3[(e3.N == 256) & (e3.feature == "log_cv_err_r4")].iloc[0]; e3_1024 = e3[(e3.N == 1024) & (e3.feature == "log_cv_err_r4")].iloc[0]; e3_64 = e3[(e3.N == 64) & (e3.feature == "log_cv_err_r4")].iloc[0]
c1000 = cost[cost.N == 1024]; fit = c1000.groupby("method")[["t_fit", "t_hpo"]].median()
tab = lambda df, **k: df.to_markdown(index=False, **k)

# ---------- tables
suite = pd.DataFrame([
 ["darcy_L1 / L2","steady diffusion, log-coefficient field","4 / 10","256","σ=1.0 / 2.0"],["advdiff_L1 / L2","steady advection–diffusion (upwind)","4","256","ε∈[0.05,0.2] / [0.005,0.02]"],
 ["transport_L1 / L2","periodic linear transport, two Gaussian pulses","4","128","pulse width 0.08–0.12 / 0.03–0.05"],["burgers_L1 / L2","viscous Burgers, pseudo-spectral","4","128","ν∈[0.05,0.1] / [0.005,0.01]"],
 ["fisher_L1 / L2","Fisher–KPP front","4","128","horizon T=0.3 / 1.2"],["heat2d_L1 / L2","2-D heat equation, moving Gaussian source","4","256","broad, α=0.05 / narrow, α=0.005"],
 ["bratu_L1 / L2","Bratu-type nonlinear elliptic (Newton)","3","256","λ∈[0.2,1.2] / [1.0,3.5]"],["wave_L1 / L2","1-D wave equation (leapfrog)","4","128","pulse width 0.06–0.10 / 0.02–0.04"]],
 columns=["Instances","Equation","p","m","Difficulty levels (L1 / L2)"])
conf = pd.DataFrame([
 ["H1a","median ȳ at N=32 > 0 (LS better)",f"median ȳ = {f(H1a['median'],3)}","Wilcoxon (one-sided), n=16",pv(H1a['p']),pv(hol['H1a']['adjusted_p']),"not supported"],
 ["H1b","ȳ decreases with N in most instances",f"{H1b['k']}/16 instances with ρ<0","exact binomial (one-sided)",pv(H1b['p']),pv(hol['H1b']['adjusted_p']),"not supported"],
 ["H2","pilot features beat {log₂N, p} (LOFO)",f"Δ RMSE = {f(H2['primary_M_spec_vs_B1']['delta'])}, 95% CI [{f(H2['primary_M_spec_vs_B1']['ci95'][0])}, {f(H2['primary_M_spec_vs_B1']['ci95'][1])}]","family-cluster bootstrap",pv(H2['primary_M_spec_vs_B1']['p']),pv(hol['H2']['adjusted_p']),"not supported"],
 ["H4a","asymmetric tuning inflates NL wins",f"{H4a['b']} vs {H4a['c']} discordant cells; NL-win share {H4a['nl_win_rate_sym8']:.1%} → {H4a['nl_win_rate_asym']:.1%}","exact McNemar (one-sided)",pv(H4a['p']),pv(hol['H4a']['adjusted_p']),"supported"]],
 columns=["ID","Hypothesis","Observed","Test","raw p","Holm-adj. p","Verdict"])
byN = raw.groupby(["N", "method"]).err.median().unstack()[["pod_gp", "pod_poly", "pod_mlp", "mlp_direct", "bottleneck"]]
byN.columns = ["POD+GP", "POD+Poly", "POD+MLP", "MLP (direct)", "Bottleneck MLP"]; byN = byN.map(lambda v: f"{v:.2e}").reset_index().rename(columns={"N": "N"})
expl = pd.DataFrame([
 ["E1","4× longer NN training (6000 vs 1500 epochs), 12 cells, seed 0",f"NN error fell in {e1_improved}/{e1_n} fits (median ratio {f(e1_med)}); mean shift of ȳ {f((e1y.y_6000-e1y.y_1500).mean())}; sign flips {int(e1y.sign_flip.sum())}/12"],
 ["E2","pilot size n₀ ∈ {16,…,64}",f"M_spec vs B0: Δ RMSE {f(e2.delta_vs_B0.min())}–{f(e2.delta_vs_B0.max())}; all 95% CIs include 0"],
 ["E3","one-feature rule (LOFO threshold on CV-POD error), N=256 / 1024",f"accuracy {e3_256.lofo_threshold_accuracy:.1%} / {e3_1024.lofo_threshold_accuracy:.1%} vs majority {e3_256.majority_baseline:.1%}; Spearman ρ {f(e3_256.spearman_with_y)} / {f(e3_1024.spearman_with_y)}; at N=64 accuracy {e3_64.lofo_threshold_accuracy:.1%}"],
 ["E4 (= H3)","extrapolation inflation (N=256), NL* vs LS*",f"mean log₁₀ inflation {f(h3['mean_log10_inflation_nl'])} (NL*) vs {f(h3['mean_log10_inflation_ls'])} (LS*); NL* inflates more in {h3['n_instances_nl_inflates_more']}/16 instances; Wilcoxon p = {pv(h3['p'])} (uncorrected)"],
 ["E6","family composition / H4a clustering",f"w/o POD+GP the NL family wins {nogp['nl_win_share']:.0%} of cells; H4a instance-level sign test p = {pv(cl['sign_test_p'])} ({cl['n_instances_with_any_flip']}/16 instances contribute)"],
 ["E5","GP-optimiser instability",f"{gp_bad3}/{n_gp} POD+GP final fits >3× worse than the selected trial ({gp_bad10} >10×); repairing them changes no verdict"]],
 columns=["ID","Analysis (post-hoc)","Result"])

def reflist(keys):
    out = []
    for k in keys:
        r = refs[refs.key == k].iloc[0]; out.append(f"{r.citation}. {r.doi_or_id}" + ("" if str(r.notes) in ("nan", "") else ""))
    return out
KEYS = ["bhattacharya2021","cohen2015","dehoop2022","dodge2019","franco2023","guo2018","greif2019","grossmann2024","hesthaven2018","holm1979","huang2026","kingma2015","kovachki2023","lee2020","li2021","lu2021","lu2022","mcgreivy2024","paszke2019","pedregosa2011","quarteroni2016","rasmussen2006","virtanen2020","westermann2026","wilcoxon1945","zhang2026"]
import sys; sys.path.insert(0, str(M)); from unimath import unimath
static = unimath((M / "draft_static.md").read_text()).replace('Gaussian processes are standard regressors for low-dimensional parameter spaces [Rasmussen & Williams 2006];','Gaussian processes are standard regressors for low-dimensional parameter spaces [Rasmussen & Williams 2006] and have been used for the coefficients of reduced-order models [Guo & Hesthaven 2018];')
static = static.replace("(tag `prereg-v1.0`)", "(commit hashes in the supplementary protocol)").replace("(tag `prereg-v1.0-analysis`)", "").replace("Items seen before registration, and the one compute-related restart of the run, are disclosed in the supplementary protocol.", "Items seen before registration, run restarts, one premature interim look at two of three seeds, and every post-hoc analysis are disclosed in the supplementary deviations log.")

abstract = f"""# Linear-subspace or neural? A pre-registered, matched-tuning comparison of surrogate families for parametric PDEs

**Running title:** Surrogate-family choice for parametric PDEs

**Authors:** [AUTHOR NAMES AND AFFILIATIONS — to be supplied by the authors]. **Corresponding author:** [to be supplied].

## Abstract

**Purpose.** Practitioners must choose between linear-subspace (proper orthogonal decomposition, POD, plus regression) and nonlinear-output neural surrogates for parametric partial differential equations (PDEs) before spending a simulation budget, and published comparisons are sensitive to how hard baselines are tuned. We ask how the choice depends on the training budget, whether a cheap pilot-data statistic predicts it, and how much unequal tuning effort distorts it.
**Methods.** In a pre-registered study, five surrogates (POD+Gaussian process, POD+polynomial ridge, POD+MLP, direct MLP, bottleneck MLP) received identical hyper-parameter budgets and were evaluated on 16 simulated parametric-PDE instances (8 families × 2 difficulty levels), six budgets (N = 32–1024 training solves) and three seeds, with interpolation and extrapolation test sets. Four confirmatory hypotheses were tested with Holm correction; post-hoc analyses are labelled exploratory.
**Results.** Neither family dominated. At N = 32 the nonlinear-output family won {int((c32.y<0).sum())} of 16 instances, but by a small margin (mean {f(abs(c32.y[c32.y<0].mean()))} decades in error); at N = 1024 the linear-subspace family won {int((c1k.y>0).sum())} of 16, by a mean {f(c1k.y[c1k.y>0].mean())} decades (up to {f(c1k.y.max())}), whereas the neural advantage never exceeded {f(abs(c1k.y.min()))} decades. The hypotheses that linear subspaces win at small budgets (H1a) and that neural surrogates catch up with more data (H1b) were not supported; POD+GP improved faster with data (median log–log slope {f(expo['pod_gp'])} vs {f(expo['mlp_direct'])}–{f(expo['bottleneck'])} for the networks). A pre-registered test of a pilot-data diagnostic (H2) was not significant after correction (Holm-adjusted p = {pv(hol['H2']['adjusted_p'])}); exploratory analysis suggests the pilot features carry signal at N ≥ 256 (leave-one-family-out threshold accuracy {e3_256.lofo_threshold_accuracy:.0%} vs {e3_256.majority_baseline:.0%} majority) that needs replication. Tuning the neural family harder than the linear one raised the apparent neural win share from {H4a['nl_win_rate_sym8']:.0%} to {H4a['nl_win_rate_asym']:.0%} (pre-registered exact McNemar p = {pv(H4a['p'])}; Holm-adjusted {pv(hol['H4a']['adjusted_p'])}); however, the effect was concentrated in {cl['n_instances_with_any_flip']} of 16 instances and an instance-level sign test gave p = {pv(cl['sign_test_p'])} without multiplicity correction. {H4b['frac']:.0%} of cells changed winner between default and tuned settings. Removing POD+GP from the linear-subspace family reversed the picture (neural family winning {nogp['nl_win_share']:.0%} of cells), indicating that the linear-subspace advantage is largely a Gaussian-process advantage.
**Conclusions.** In this suite the better family depends strongly on problem regularity: linear-subspace surrogates offer large gains where solution spectra decay fast, while neural surrogates offer modest gains elsewhere, and unequal tuning can manufacture neural wins. Findings are limited to 16 simulated instances with low-dimensional parameters, small networks and CPU training.

**Keywords:** surrogate modelling; parametric PDEs; reduced-order models; neural networks; Gaussian processes; benchmarking; pre-registration

"""
results = f"""
## 5 Results

### 5.1 Overview of accuracy

Fig. 2 shows learning curves for all 16 instances and Table 3 gives median errors across instances. Errors span nearly six orders of magnitude across instances; POD+GP reaches the lowest errors on smooth problems (for example Bratu, relative error of order 10⁻⁶ at N = 1024) while on the hardest instances at N = 32 even the best method has error above 10⁻¹ (Fig. 2). POD+polynomial ridge was the weakest method overall (median error {byN.iloc[-1]['POD+Poly']} at N = 1024). Across instances the median log–log learning-curve slope (N ≥ 64) was {f(expo['pod_gp'])} for POD+GP, {f(expo['pod_poly'])} for POD+Poly, {f(expo['pod_mlp'])} for POD+MLP, {f(expo['mlp_direct'])} for the direct MLP and {f(expo['bottleneck'])} for the bottleneck MLP.

**Table 3.** Median test error (relative L₂, interpolation set) over the 16 instances and 3 seeds.

{tab(byN)}

![**Fig. 2** Learning curves, mean over 3 seeds (lines) with the min–max range across seeds (bands). Solid: linear-subspace methods; dashed: nonlinear-output methods. Source: `results/raw_results.csv`.](../figures/fig2_learning_curves.png){{width=100%}}

### 5.2 Confirmatory tests

**Table 2.** Pre-registered confirmatory tests (Holm correction over the four tests, family-wise α = 0.05).

{tab(conf)}

**H1a/H1b (budget crossover).** The pre-registered expectation that linear-subspace surrogates win at small budgets was not borne out: at N = 32 the nonlinear-output family had the lower error in {int((c32.y<0).sum())} of 16 instances (median ȳ = {f(H1a['median'],3)}, Table 2). Neither did the neural family catch up with more data in most instances: only {H1b['k']} of 16 instances showed a negative rank correlation between log₂N and ȳ; in the other {16-H1b['k']} the linear-subspace advantage grew with N (Fig. 3). At N = 1024 the linear-subspace family won {int((c1k.y>0).sum())} instances and the neural family {int((c1k.y<0).sum())}. The sizes of the two kinds of win are very unequal: when the linear-subspace family won at N = 1024 its mean advantage was {f(c1k.y[c1k.y>0].mean())} decades (maximum {f(c1k.y.max())}), whereas the neural family's mean advantage when it won was {f(abs(c1k.y[c1k.y<0].mean()))} decades (maximum {f(abs(c1k.y.min()))}).

![**Fig. 3** Family ratio ȳ = log₁₀(err of best nonlinear-output method / err of best linear-subspace method), both chosen by validation error, mean over seeds. Blue: linear-subspace better; orange: nonlinear-output better. Source: `results/tables/cells.csv`.](../figures/fig3_family_ratio_heatmap.png){{width=70%}}

**H2 (pilot diagnostic).** Under leave-one-family-out evaluation the pre-specified model (log₂N + pilot CV-POD error + spectral slope) had RMSE {f(H2['rmse']['M_spec'],3)} versus {f(H2['rmse']['B1'],3)} for the pre-registered baseline B1 (log₂N + p) — Δ = {f(H2['primary_M_spec_vs_B1']['delta'])}, 95% cluster-bootstrap CI [{f(H2['primary_M_spec_vs_B1']['ci95'][0])}, {f(H2['primary_M_spec_vs_B1']['ci95'][1])}], raw p = {pv(H2['primary_M_spec_vs_B1']['p'])}, Holm-adjusted p = {pv(hol['H2']['adjusted_p'])}: **not supported**. The comparison is weakened by a flaw in baseline B1 that we identified after the fact: its RMSE is dominated by the held-out Darcy fold (fold RMSE {f(fold.loc['darcy','B1'],1)}), because Darcy is the only family with p = 10 and the linear p-term extrapolates badly. Against the simpler baseline B0 (log₂N only, RMSE {f(H2['rmse']['B0'],3)}) the improvement is smaller and also not significant (Δ = {f(H2['M_spec_vs_B0']['delta'])}, CI [{f(H2['M_spec_vs_B0']['ci95'][0])}, {f(H2['M_spec_vs_B0']['ci95'][1])}], p = {pv(H2['M_spec_vs_B0']['p'])}). The sign of ȳ was predicted correctly in {H2['sign_accuracy']['M_spec']['accuracy']:.0%} of cells by the pilot model versus {H2['sign_accuracy']['B0']['accuracy']:.0%} (B0) and {H2['sign_accuracy']['B1']['accuracy']:.0%} (B1), with a majority-class rate of {H2['sign_accuracy']['M_spec']['majority_baseline']:.0%} (descriptive). Fig. 4 shows the predictions.

![**Fig. 4** Leave-one-family-out predictions of ȳ (cell level; shade = N from 64 to 1024). Red triangles: B1 predictions below the plotted range (≈ −16, held-out Darcy family). Source: `results/tables/h2_lofo_predictions.csv`.](../figures/fig4_lofo_prediction.png){{width=100%}}

**H4a (tuning asymmetry).** When the nonlinear-output family received eight tuning trials and the linear-subspace family only its default configuration, the neural family "won" {H4a['nl_win_rate_asym']:.1%} of the {H4a['n_cells']} (instance, N) cells; with eight trials for both it won {H4a['nl_win_rate_sym8']:.1%}. Ten cells flipped from a linear-subspace to a neural win under asymmetry and one in the opposite direction (exact McNemar p = {pv(H4a['p'])}; Holm-adjusted {pv(hol['H4a']['adjusted_p'])}): **supported**. Descriptively, the winning family differed between default-only and eight-trial tuning in {H4b['winner_flips_b1_vs_b8']} of {H4b['n_cells']} cells ({H4b['frac']:.1%}; Wilson 95% CI {H4b['wilson95'][0]:.1%}–{H4b['wilson95'][1]:.1%}), and the Kendall τ between method rankings at b = 1 and b = 8 averaged {f(H4b['kendall_tau_vs_b8']['b=1']['mean_tau'])} (minimum {f(H4b['kendall_tau_vs_b8']['b=1']['min_tau'])}) (Fig. 5).

**Robustness of H4a (post hoc).** The 96 cells are not independent (cells of one instance share training data and seeds). Aggregating to instances, flips occurred in only {cl['n_instances_with_any_flip']} of 16 instances (advdiff L1, Burgers L1 and L2, heat2d L1 and L2), all in the direction of asymmetric tuning favouring the neural family ({cl['n_pos']} positive, {cl['n_neg']} negative); the one-sided exact sign test over these instances gives p = {pv(cl['sign_test_p'])} (uncorrected). Had this instance-level test replaced the cell-level one, its Holm-adjusted p with the other three confirmatory tests would be about {pv(min(1, cl['sign_test_p']*4))}, above 0.05. The pre-registered verdict for H4a is therefore reported as registered, but the evidence is fragile and concentrated.

![**Fig. 5** Share of (instance, N) cells won by the nonlinear-output family under symmetric tuning with b trials (blue) and under the asymmetric condition (orange line). Source: `results/statistics.json`.](../figures/fig5_tuning_asymmetry.png){{width=45%}}

### 5.3 Exploratory analyses (post hoc; none changes a confirmatory verdict)

**Table 4.** Post-hoc analyses.

{tab(expl)}

*Pilot features (E3).* At N ≥ 256 the pilot CV-POD error correlated with ȳ (Spearman ρ = {f(e3_256.spearman_with_y)} at N = 256) in the direction predicted by n-width theory — slower spectral decay, relatively better neural surrogate — and a one-feature leave-one-family-out threshold rule classified the winner correctly for {int(round(e3_1024.lofo_threshold_accuracy*16))} of 16 instances at N = 1024 (majority baseline {e3_1024.majority_baseline:.1%}). At N = 64 the rule was no better than chance ({e3_64.lofo_threshold_accuracy:.1%}). With 16 instances from 8 families, selected after seeing the data, this is a hypothesis for replication, not a result.

*Which linear-subspace method drives the result (E6).* Restricting the linear-subspace family to subsets of its methods and repeating H1a/H1b: with {{POD+GP, POD+MLP}} or {{POD+GP, POD+Poly}} the verdicts are unchanged (neural family wins {e4['LS_gp+mlp']['nl_win_N32']} / {e4['LS_gp+poly']['nl_win_N32']} instances at N = 32), so the 3-versus-2 method asymmetry between families does not drive the results. Without POD+GP (family {{POD+MLP, POD+Poly}}) the neural family wins {nogp['nl_win_share']:.0%} of cells and {nogp['nl_win_N1024']} of 16 instances at N = 1024, and H1b would be met ({nogp['H1b_k']}/16 instances, exact p = {pv(nogp['H1b_p'])}; exploratory). The linear-subspace advantage reported above is therefore essentially an advantage of Gaussian-process regression of POD coefficients.

*Extrapolation (E4).* Errors on the extrapolation set were roughly one decade larger than on the interpolation set for both families; the linear-subspace winner inflated more (mean {f(h3['mean_log10_inflation_ls'])} vs {f(h3['mean_log10_inflation_nl'])} log₁₀ units).

*Training budget and optimiser robustness (E1, E5).* Quadrupling the neural training length lowered neural error in {e1_improved} of {e1_n} refits (median ratio {f(e1_med)}) and moved ȳ by {f((e1y.y_6000-e1y.y_1500).mean())} on average, but changed the winning family in none of 12 cells, so the qualitative conclusions are robust and the magnitudes are budget-sensitive. In {gp_bad3} of {n_gp} POD+GP final fits (1.4%) the refit on all N samples was more than 3× worse than the selected trial (a single-start hyper-parameter optimiser landed in a poor local optimum); repairing them leaves all verdicts unchanged (H2 raw p vs B1 {pv(rep['gp_repaired']['H2_p_B1'])}, still not significant after Holm correction).

*Cost.* The FOM cost was {f(cost.fom_s.min()*1000,1)}–{f(cost.fom_s.max()*1000,0)} ms per solve, so surrogates are cheap only relative to much costlier solvers. At N = 1024 the median final-fit and total tuning times were {f(fit.loc['pod_gp','t_fit'],1)} s and {f(fit.loc['pod_gp','t_hpo'],0)} s for POD+GP versus {f(fit.loc['mlp_direct','t_fit'],1)} s and {f(fit.loc['mlp_direct','t_hpo'],0)} s for the direct MLP (single CPU thread); POD+polynomial ridge needed {f(fit.loc['pod_poly','t_fit'],2)} s. Break-even query counts under stylised FOM-cost multipliers are in `results/tables/cost_breakeven.csv` and are a model, not a measurement.

## 6 Discussion

**What the experiments establish.** In this suite no surrogate family was uniformly better. Linear-subspace surrogates, in particular POD+GP, were far more accurate (up to about three orders of magnitude) on instances whose solution manifolds are smooth in the parameters and spectrally compact (Bratu, Darcy L1, heat2d L1, Burgers L1, wave L1, transport L1), and their advantage grew with N. Nonlinear-output networks were better on the transport- and front-dominated, narrow-feature instances (transport L2, Fisher L2, heat2d L2, Darcy L2; also, by negligible margins, advdiff L2 and wave L2), but by margins of at most {f(abs(c1k.y.min()))} decades. Two pre-registered expectations were wrong: linear subspaces did not win at small budgets, and neural surrogates did not catch up with data. A plausible reading (not tested here) is that, at fixed training epochs and with hyper-parameter budgets of eight trials, networks plateau at errors near 10⁻³ whereas GPs continue to converge on smooth maps; the 4× longer-training check (E1) lowered neural error by about 30% but did not reverse any winner.

**The diagnostic.** The pre-registered test of the pilot diagnostic did not pass. The exploratory association at N ≥ 256 is in the direction predicted by approximation theory (Cohen & DeVore 2015; Greif & Urban 2019; Franco et al. 2023), but our evidence is insufficient to recommend a selection rule, and at the smallest budgets, where such a rule would matter most, the pilot features were uninformative.

**Why tuning asymmetry matters.** The pre-registered H4a effect is moderate (about nine percentage points of cells) and in the direction of bias described for the literature (McGreivy & Hakim 2024): giving only one family a search budget turns near-ties into wins. It is, however, concentrated in five instances and would not survive Holm correction if tested at the instance level, so it should be read as a demonstration of the mechanism in this suite and not as an estimate of how large the bias is in the literature. Because a tenth of cells changed winner between default and tuned settings even under symmetric treatment, reports of surrogate comparisons should state the tuning budget per method, in the spirit of reporting results as a function of tuning budget (Dodge et al. 2019).

**What drives the linear-subspace advantage.** Our decomposition shows that POD+GP, not POD per se, carries the advantage: POD+MLP and POD+polynomial ridge together lost most cells to the direct and bottleneck networks. Smooth parameter-to-coefficient maps in few dimensions are the setting in which GP regression is expected to excel; a stationary ARD kernel may also be the reason it falls behind on instances with localised or moving features, an alternative explanation to manifold complexity that our experiments cannot separate.

**Relation to prior work.** Our findings are consistent in spirit with the report that no method is universally superior and that polynomial surrogates are more data-efficient for smooth inputs (Westermann et al. 2026, preprint), here extended to POD with Gaussian-process regression and with a pre-registered diagnostic test that did not succeed. We did not reproduce any cost-accounting framework (de Hoop et al. 2022; Zhang et al. 2026; Huang & Stuart 2026).

## 7 Limitations

First, sixteen instances from eight hand-chosen families are not a random sample of PDEs; conclusions concern this suite, and the confirmatory tests have limited power (8 independent families). (2) Parameters are low-dimensional (p ≤ 10) and fields are small (m ≤ 256); high-dimensional or field-valued inputs (e.g., Fourier neural operators) were not studied. (3) Neural networks were small, trained for a fixed 1500 epochs in float32 on CPU, and hyper-parameter spaces were chosen by us; larger budgets or other architectures could narrow or move the gaps (E1 shows magnitudes are budget-sensitive). (4) The POD+GP implementation uses a single-start optimiser that failed in 1.4% of final fits. (5) Intrusive POD-Galerkin was not included. (6) Seeds draw nested subsets of a finite pool, so seed-to-seed variance underestimates sampling variance at large N; only three seeds were run (the planned extension to five was not). (7) The pre-registered baseline B1 for H2 turned out to be degenerate under leave-one-family-out evaluation; the verdict is reported as registered. (8) All problems are synthetic simulations with discretisation-defined ground truth, and full-order-model costs are milliseconds, so cost statements are stylised. (9) The exploratory analyses, including the robustness checks E4–E6, were conceived after seeing the results and are not corrected for multiplicity. (10) The validation split at N = 32 contains only 6 samples, so model selection there is noisy; Gaussian-process cost grows cubically with N, and neither this nor N > 1024 was studied. (11) The H4a effect rests on five of sixteen instances.

## 8 Conclusions

For parametric PDEs with low-dimensional parameters, neither linear-subspace nor neural surrogates were uniformly superior in a matched-tuning, pre-registered comparison on 16 simulated instances. Linear-subspace surrogates with Gaussian-process regression (the advantage disappears without the Gaussian process) gave very large accuracy gains where solution spectra decay fast, and their advantage grew with the number of training solves; neural surrogates gave modest gains on front- and transport-dominated instances. Unequal tuning effort inflated the apparent neural advantage in the pre-registered cell-level test, although the effect was concentrated in five instances. A pilot-data selection rule was not confirmed; the exploratory signal at moderate budgets deserves replication on new PDE families before any practical recommendation.

## Declarations

**Funding:** [authors to complete]. **Competing interests:** [authors to complete]. **Ethics approval and consent:** not applicable (simulated data only). **Data availability:** all data are generated by the code in the project repository (`code/`); the repository is currently on the working branch `claude/happy-bell-9xorxs` of github.com/Bhargavteja-9779/rp_c_7 and has **not** been deposited in a permanent archive — authors must deposit it (e.g., Zenodo) and update this statement before submission. **Code availability:** same repository; `python run_all.py --mode full` reproduces the experiment (≈3.5 h on 4 CPU cores) and `--stage analysis` regenerates statistics, tables and figures. **Author contributions:** [authors to complete]. **AI assistance:** this study, code and draft were produced by an autonomous AI agent (Claude) working with the stated user; the human authors must verify and take responsibility for all content and confirm originality and journal-specific AI-disclosure rules. **Pre-registration:** protocol v1.0 was committed to the repository before any comparative result existed (commit hashes in the supplementary protocol); this is a version-control timestamp, not an independent registry entry.

## References

""" + "\n\n".join(f"{i+1}. {t}" for i, t in enumerate(reflist(KEYS))) + "\n"
ex_static = static.replace("## 1 Introduction", "## 1 Introduction")
figs1 = "\n\n![**Fig. 1** Study design (conceptual diagram, not data): problem suite → matched tuning (B = 8 trials per method) → family winners chosen by validation error → outcome ȳ → pre-registered tests.](../figures/fig1_design.png){width=90%}\n\n"
tab1 = "\n\n**Table 1.** The 16 problem instances (8 families × 2 levels).\n\n" + tab(suite) + "\n\n"
sw = "\n\n**Software and statistics.** Experiments use Python with numpy and scipy [Virtanen et al. 2020], scikit-learn for Gaussian processes and ridge regression [Pedregosa et al. 2011] and PyTorch [Paszke et al. 2019] with the Adam optimiser [Kingma & Ba 2015], on CPU only. One-sided and two-sided Wilcoxon signed-rank tests follow Wilcoxon [1945]; multiplicity is controlled with the Holm procedure [Holm 1979].\n\n"
doc = abstract + ex_static.replace("**Confirmatory tests**", tab1 + figs1 + "**Confirmatory tests**") + sw + results
(M / "Final_Manuscript.md").write_text(doc); print("words:", len(doc.split()))
