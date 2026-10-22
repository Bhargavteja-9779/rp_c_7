# Protocol addendum v2.1 (pre-registered BEFORE Exp A2 and Exp E were run; written AFTER seeing Exp A and Exp D results)

**Honesty note.** These two follow-up experiments were conceived after the primary Experiment A (diagnostic not replicated: P1 p=0.180, P2 Holm 0.055, S1 60 % vs 70.8 %) and after Experiment D (D1 rejected: matched-search kernel ridge median 14× worse than POD+GP where GP clearly wins). They are therefore *post-hoc in motivation* but *pre-registered in prediction*: their instances, rules and success criteria are fixed here before any surrogate runs on them. They do not alter the verdicts of P1, P2, S1, D1.

## Exp A2 — replication of the "dominance regime" statement (what the diagnostic can and cannot do)
**Observation motivating it (post hoc, 24 instances):** the 4 instances with f1 < −2 (nlheat×2, bratu×2) were decisive LS wins at N=1024 (ȳ ≥ 2.58); for f1 ≥ −2 outcomes were mixed (median ȳ −0.05).
**Candidates (8; defined and unit-tested before any method was run):** reacdiff_L1/L2, helm_L1/L2, heatp_L1/L2, diff1d_L1/L2 (`problems.py::build_suite_v21`).
**Selection rule (pilot features only; no surrogate run):** an instance *qualifies* iff the 3-seed mean f1 < −2.0. Result (`expA2_selection.json`): qualifying = {diff1d_L1, heatp_L1, heatp_L2, helm_L1, helm_L2, reacdiff_L1, reacdiff_L2} (7); non-qualifying control = diff1d_L2 (f1 −1.72). All 8 are run (N ∈ {64, 256, 1024}, seeds 0–2, identical protocol).
**Predictions:** **Q1 (primary):** among the 7 qualifying instances, the number with ȳ(N=1024) ≥ 1.0 decade, tested by an exact one-sided binomial against p0 = 0.10 (the share of instances with f1 ≥ −2 in v1+Exp A that were ≥ 1.0 decades: 2/20); success iff p < 0.05 (k ≥ 3 of 7). **Q2:** no qualifying instance has ȳ(N=1024) < −0.10 (regime purity). Descriptive: all-7 claim; the control's outcome.
**Interpretation rules:** Q1 and Q2 hold → "very fast pilot decay identifies a regime where linear-subspace+GP is decisively better" is reported as replicated on seven new instances (still synthetic, family-limited); otherwise reported as not replicated.

## Exp E — mechanism: marginal-likelihood fitting vs anisotropy
POD + GP with an **isotropic** kernel (ML-II fitted; `pod_gp_iso`) on the 24 instances of Exp A/v1, N ∈ {64, 256, 1024}, seeds 0–2, same protocol, compared with POD+GP-ARD (v1/Exp A) and matched-search POD+KRR (Exp D) on identical training subsets. Restrict to cells where POD+GP-ARD clearly beats the best NL (ȳ > 0.10).
**M-MLII:** median err_KRR/err_GPiso > 3 **and** median err_GPiso/err_GPARD ≤ 3 → marginal-likelihood fitting (not anisotropy) explains the advantage.
**M-ARD:** median err_GPiso/err_GPARD > 3 → anisotropy (per-dimension length-scales) matters. Otherwise: mixed/inconclusive. Medians and quartiles are reported.

## Rules
Seeds 0–2; no changes to methods, instances or criteria after the first result; failed configs = ∞; all outputs preserved; any deviation logged in `deviations_v2.md`.
