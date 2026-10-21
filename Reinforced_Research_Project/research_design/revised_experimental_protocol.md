# Revised experimental protocol v2.0 (pre-registered before any v2 comparative result existed)

Original project: commit `931b306e90693e85a3d5fd368493515d11d1d981` (v1, untouched). v2 lives in `Reinforced_Research_Project/`. Frozen rules: `frozen_rules_from_v1.json` (derived from v1 data only).

## 0. Why v2 (weaknesses it addresses; see audit/rejection_risk_register.md)
RR-01 the only positive diagnostic signal was post hoc; RR-02 "matched tuning" is not matched in effective optimisation (GP maximises marginal likelihood inside each trial); RR-03 stronger-NN check covered 6 of 16 instances at one seed; RR-04 "wins" were dominated by practical ties; RR-05 external validity (8 families, p ≤ 10).

## 1. Experiment A — independent out-of-sample replication (CONFIRMATORY)
**Instances (8; defined and unit-tested before any method was run):** darcyhd_L1/L2 (p=16/32), incl_L1/L2 (moving discontinuous inclusion, contrast 3–10 / 30–300), kdv_L1/L2 (one soliton + background / two interacting solitons), nlheat_L1/L2 (smooth nonlinear conduction, β 0–1 / 1–8). Levels were fixed from solver timing and solver tests only; no method result was seen.
**Protocol:** identical to v1 (5 methods; B=8; 1500 epochs; N ∈ {32,…,1024}; seeds 0,1,2; family winners by validation error; ȳ = log10(err NL*/err LS*)), except that the v1 hash-seeding bug is fixed and neural networks log loss curves.
**Frozen rules (from v1 data, `frozen_rules_from_v1.json`):** tie band 0.10 decades; **R1:** predict "NL wins" iff f1 = log10 CV-POD error (r=4, 32-snapshot pilot) > t = −0.5203 (v1 accuracy on 24 non-tie cells at N=256,1024: 91.7 %, majority 70.8 %); **R2:** frozen ridge ŷ = f(log2 N, f1) with coefficients in the JSON; **B0:** frozen ŷ = f(log2 N).
**Primary tests (Holm over P1, P2; family-wise α = 0.05):**
* **P1** Spearman ρ between instance-level f1 and ȳ at N=1024 over the 8 new instances; alternative ρ < 0; exact permutation test (8! permutations).
* **P2** mean per-cell squared-error gain of frozen R2 over frozen B0 on the 40 new cells (8 instances × N ∈ {64,…,1024}); 10,000-draw bootstrap resampling instances; one-sided.
**Secondary (not corrected):** **S1** accuracy of R1 on non-tie new cells at N ∈ {256,1024}, exact binomial one-sided vs p0 = 0.708; **S2** tie/clear classification, seed sign-consistency, NL win rate by N; **S3** pooled 24-instance, 12-family leave-one-family-out comparison of {B0, B1log, M_cv4, M_spec} (exploratory).
**Decision rule for the manuscript:** P1 and P2 both significant → the diagnostic is reported as replicated out of sample; otherwise reported as not replicated, and the paper is built around the benchmark, equivalence-band, mechanism and tuning findings.

## 2. Experiment B — stronger neural-network challenge (ROBUSTNESS, pre-specified criteria)
For all 24 instances × seeds 0–2 × N ∈ {256, 1024}, refit each stored best configuration of POD+MLP, MLP and Bottleneck with 6000 epochs (4×). ȳ computed with oracle-best-of-family test errors in both conditions. **Criteria:** (B1) ≥ 85 % of clear cells (|ȳ_1500| ≥ 0.10) keep their sign; (B2) median shift toward NL < 0.5 decades. Failure of B1 or B2 means the v1 conclusions are budget-dependent and must be stated so.

## 3. Experiment D — mechanism: kernel prior vs marginal-likelihood fitting (EXPLORATORY-CONFIRMATORY, pre-specified)
POD + kernel ridge (Matérn-5/2 or RBF, isotropic length-scale, ridge), tuned with the **same** B=8 random search as every other method (no marginal-likelihood optimisation), on all 24 instances × 6 N × 3 seeds. Compare with POD+GP on the same training subsets. **D1 (kernel prior explains the LS advantage):** among cells where POD+GP clearly beats the best NL (ȳ_gp > 0.10), the median err_KRR/err_GP ≤ 3 and ≥ 75 % of such cells have ratio ≤ 3. **D2 (ML-II hyperparameter fitting is the driver):** otherwise. Either outcome is reported.

## 4. Rules
Fixed seeds 0–2 (no seed selection); no change of methods, search spaces, tie band, frozen rules or analysis after the first v2 result is seen (any change → `deviations_v2.md`); failed/diverged configs count as ∞ for selection; if a solver fails the run aborts and is fixed before re-running everything; all outputs preserved. v1 results are read-only inputs.

## 5. Disclosures before v2 results
Seen before registration: all v1 results and post-hoc analyses; solver timings and solver unit tests of the 8 new instances; plumbing tests of the analysis code on v1 data (outputs discarded). Not seen: any method error on any new instance.
Known limitations carried over: synthetic data; hand-chosen families; CPU-only small networks; 3 seeds; GP single-start optimiser (unchanged to keep comparability); the pre-registration is a git history, not an independent registry.
