# Candidate research directions (Step 3) — portfolio and Director decision

Scored 1 (bad) – 5 (good) by the Director's *simulated* specialist passes (Agents 2, 4, 5, 8, 9, 13). These are my own analytical judgements, not independent human review. Feasibility = CPU-only (4 cores, 15 GB, no GPU), no paid data. Prior-art notes are from the searches recorded in `literature_review/`.

| # | Direction | Importance | Novelty (prior-art check) | Feasible on CPU | Evidence depth | Verdict |
|---|---|---|---|---|---|---|
| 1 | **Pilot-data diagnostic predicting when neural vs. linear-subspace surrogates win; leave-one-family-out validation; tuning-budget ranking sensitivity** | 4 | 3 – cost-accuracy comparisons exist (2604.00689, 2609.24021, 2605.15399, de Hoop 2022); *predictive pilot rule* not found in any abstract/full-text read | 5 | 5 | **SELECTED** |
| 2 | Conformal calibration of PDE surrogates under parameter shift | 4 | 2 – conformal neural-operator papers already exist (e.g. 2606.29440 appeared in search) | 4 | 4 | rejected (crowded) |
| 3 | Predicting PINN training failure from PDE features | 3 | 2 – Krishnapriyan 2021, NTK literature | 3 | 3 | rejected |
| 4 | Weak-baseline audit beyond fluids (systematic review) | 4 | 3 – extends McGreivy & Hakim; named open problem | 2 (needs reading ~70+ paywalled papers) | 2 | rejected (cannot read primary sources reliably) |
| 5 | A-posteriori residual error certificates for NN surrogates | 4 | 2 – Kleikamp 2026 etc. | 3 | 3 | rejected |
| 6 | Learning-curve scaling-law fits per surrogate family | 3 | 2 – used in 2605.15399 | 4 | 4 | folded into #1 as secondary analysis |
| 7 | Hybrid coarse-solver + learned correction vs pure NN | 4 | 2 – warm-start/correction literature (NOWS) | 4 | 4 | rejected |
| 8 | Extrapolation in parameter space: NN vs ROM | 4 | 3 | 5 | 4 | folded into #1 as secondary hypothesis (H3) |
| 9 | Data-splitting bias in surrogate validation | 3 | 2 – MLCSE already published a case study | 5 | 3 | rejected |
| 10 | Koopman/DMD vs NN forecasting benchmark | 3 | 1 – crowded | 4 | 3 | rejected |
| 11 | SINDy/PDE discovery noise robustness | 3 | 1 – crowded | 4 | 3 | rejected |
| 12 | Derivative-informed training for small-data surrogates | 4 | 2 – covered in 2604.00689 | 3 | 3 | rejected |
| 13 | Active-learning sample selection for POD-GP surrogates | 4 | 2 – classical RB greedy / active learning | 4 | 3 | rejected |
| 14 | LLM agents for constitutive modelling | 3 | 3 | 1 (no LLM access/compute) | 1 | rejected |
| 15 | Foundation-model PDE surrogates fine-tuning cost | 4 | 2 – crowded, needs GPU | 1 | 1 | rejected |
| 16 | Cross-fidelity transfer between grid resolutions | 3 | 2 | 4 | 3 | rejected |

## Director's rationale for #1
It is the only candidate that (a) yields a falsifiable, quantitative, *predictive* claim, (b) can be fully executed on CPU with real solvers and honest statistics, and (c) has a defensible fallback value even if the central prediction fails (a pre-registered negative result about the limits of cheap diagnostics, plus the first matched-tuning comparison that includes POD–GP and POD-polynomial baselines alongside neural surrogates on one problem suite). Novelty risk (moderate) is disclosed in `novelty_map.md`.
