# Novelty map and prior-art audit (Agent 4 — skeptical competing researcher)

**Reading depth disclosure:** Of ~13 matrix entries only two were read beyond abstract level, and each only partially (arXiv:2604.00689: ~100k of 212k HTML characters; arXiv:2605.15399: ~100k of 108k). Nothing was read from paywalled full texts. Prior-art searches used web search (US-only) + arXiv API; Google Scholar/patent databases were not searched. **Absence of evidence is therefore weak evidence of novelty.**

| What existing work established | Remaining limitation | Does it matter scientifically? | What this project adds | How measured | What would falsify the claim |
|---|---|---|---|---|---|
| Slow Kolmogorov n-width ⇒ linear ROMs need many modes; deep autoencoders help (Franco 2021; Greif & Urban 2019; Ohlberger & Rave) | Qualitative; theory is per-problem; no *a-priori, pilot-data* rule | Yes: practitioners must choose a surrogate family *before* spending the data budget | A cheap pilot diagnostic (CV-POD tail error, effective rank, decay rate, parameter dimension) and a pre-registered test of whether it predicts the NN-vs-linear winner out-of-sample | Leave-one-family-out RMSE/rank-correlation vs trivial predictors (intercept; N only; N+p) | Diagnostic does not beat N+p baseline with cluster-bootstrap CI excluding 0 |
| Cost–accuracy / breakeven frameworks for neural surrogates (de Hoop 2022; 2604.00689; 2605.15399; 2609.24021) | They evaluate *after* training all candidates; no GP/POD-regression baselines; no rule | Yes | Not claimed as novel; used as accounting protocol | n/a | n/a |
| Weak baselines inflate ML-PDE claims (McGreivy & Hakim 2024) | Review only; no quantification of how tuning budget flips *rankings between surrogate families* | Yes | Direct experimental quantification: ranking stability vs hyper-parameter budget B ∈ {1,2,4,8,…} | Kendall τ between rankings at B and at B_max; fraction of winner flips | Rankings stable at B=1 (then claim is refuted and reported as such) |
| POD+NN, DeepONet, FNO, PCA-Net exist | Seldom compared with POD+GP / POD+polynomial under *identical* tuning and sample budgets | Moderate | One suite, one protocol, 5 method families, 16 problem instances, 7 sample budgets, 5 seeds, matched HPO | Test error with CIs and paired tests | n/a |

## Verdict of the Novelty Auditor (simulated adversary)
* Core idea "linear methods win with fast spectral decay" **is common knowledge**; claiming it would be incremental.
* The defensible contribution is **narrow**: an *operational, pre-registered, out-of-sample-tested* pilot predictor + a quantified ranking-instability result. If the predictor fails to beat trivial baselines, the paper becomes a *negative-result + benchmarking* paper, which is still publishable in an evaluation-oriented venue but is **not** a high-novelty contribution.
* Do not claim "first". Do not claim a new architecture. Do not claim state-of-the-art accuracy.
* Gate C decision: **conditionally passed** (moderate novelty risk, disclosed). Reviewed again after results (Review 1 and Review 8).
