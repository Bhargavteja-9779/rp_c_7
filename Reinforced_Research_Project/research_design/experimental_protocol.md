# Experimental protocol of THIS paper (consolidated; the dated originals are the addenda listed in each row — their git commits predate the corresponding results; see `audit/prereg_order_check.json`)

## Research question
When only N = 32–1,024 runs of a slow parametric simulation can be afforded, (Q1) which stand-in model should be built, (Q2) can a cheap cross-validated procedure choose it reliably, (Q3) can it say how many more runs are needed, (Q4) can it detect when the POD basis (not the regressor) limits accuracy, and (Q5) does the answer hold against a strongly tuned neural network on problems solved by independent third-party code?
**Gap in one sentence.** Existing comparisons pit methods against each other under unequal tuning on a single set of problems and offer no validated procedure that a practitioner can run on their own data to choose a stand-in and estimate the runs still needed.

## Hypotheses (metric, test, pass/fail — fixed before the results they concern)
| ID | Statement | Metric / test | Pass criterion | Fixed in |
|---|---|---|---|---|
| H1a | The tool's cross-validated selection is close to the oracle choice | cell-wise ratio err(selected)/min over pool; 24 cells (8 problems × N ∈ {64, 256, 1024}) | median ≤ 1.5 and ≥ 75 % of cells ≤ 2.0 (criterion S1) | addendum v3.0 (a99c2c6) |
| H1b | It is no worse than always using a GP baseline | median ratio err(selected)/err(legacy POD+GP) | ≤ 1.0 (S2) | v3.0 |
| H1c | It is at least as good as the five-method benchmark's own selection | median ratio vs validation-selected legacy method; sign balance of > 10 % differences | ≤ 1.0 and wins > losses (S3) | v3.0 |
| H2 | The learning-curve predictor gives usable accuracy forecasts | 4N0 forecast within a factor 2 of the actual test error of the same candidate; 48 cases | ≥ 70 % (B1); reach-1 %/0.1 % classification ≥ 75 % (B2) | v3.0 |
| H3 | The basis-limit flag identifies cases where a full-field model is better | among flagged cells, share with GP-full better than best POD model by > 10 % | ≥ 75 % if ≥ 5 flagged cells (F1) | v3.0 |
| H4 | A strongly tuned network (twice the tuning budget of the tool's members) rarely beats the tool-selected model | share of 16 cells (N ∈ {256, 1024}) where the tuned network is better by > 25 % | ≤ 4/16 (S4) | v3.0 |
| H5 | The main benchmark finding holds on problems from independent third-party code | share of the 8 new problems that are reduced-basis-clear (ȳ > 0.10, validation-selected) at N = 1024 | ≥ 5 of 8 (PT) | v3.0 |
| H6–H9 (earlier stages, design evidence) | Pilot diagnostic, kernel-ridge mechanism, longer training, full-field GP | see `protocol_addendum_v2.*` and Supplement S3 | as written there | v2.0–v2.3a |
Multiple comparisons: the seven criteria S1–S4, B1–B2, F1 are reported individually with exact binomial/Wilson intervals and Holm-adjusted p-values for the tests against their thresholds.

## Experiments (models, data, seeds) and run-time estimate (4 cores)
| ID | What | Data / splits / seeds | Est. time |
|---|---|---|---|
| E1 | Original benchmark (v1): 5 methods, 16 problems | N ∈ {32 … 1,024}, 3 seeds | ~10 h (done) |
| E2 | Exp A/A2/A3 (new families, smooth candidates, confound probes), 20 problems | as E1 / N ∈ {64, 256, 1,024} | ~6 h (done) |
| E3 | Mechanism controls D, E, G, G3, H (kernel ridge, iso-GP, full-field GP) | 24 problems, N ∈ {64 … 1,024} | ~1 h (done) |
| E4 | Budget/precision controls B, F (longer training, float64, L-BFGS) | subset | ~3 h (done) |
| E5 | Third-party-solver benchmark T: 8 scikit-fem problems, 5 legacy methods | N ∈ {64, 256, 1,024}, 3 seeds | ~1.5 h |
| E6 | SurroSelect evaluation C (pool errors, selection, learning curve) | same 24 cells × 3 seeds | ~1–2 h |
| E7 | Strong tuned network S (Optuna, 16 trials, float64, L-BFGS) | 8 problems, N ∈ {256, 1,024}, 3 seeds | ~2.5 h |
| E8 | Tool validation on plain files via the command line (`fit/predict/evaluate`) | exported `.npz` files of 3 problems | minutes |
| E9 | Sampling-noise simulation (what seed-to-seed variation does selection regret show when candidates are exchangeable?) | simulation | minutes |
**Baselines:** the five legacy methods (B = 8, 1,500 epochs), always-POD+GP, the best member of the tool's pool (oracle), and the strongly tuned network (twice the tuning budget of the other methods, favouring the baseline). **Ablations:** removing the tie band, using a validation split instead of cross-validation, restricting the pool to POD-only members, and learning-curve fit with 3 versus 4 points (analysis-only on stored outputs). **Alternative explanations checked:** unequal tuning, training budget, search draw, basis rank, optimiser.

## What would reject each hypothesis
H1: median regret > 1.5 or fewer than 75 % of cells within 2×. H2: forecast within 2× in < 70 % of cases (the extrapolation is then not usable as advertised). H3: flag precision < 75 %. H4: the tuned network wins by > 25 % in > 4/16 cells (then the paper must say that the tool does not beat a strongly tuned network). H5: fewer than 5 of 8 problems favour the reduced basis.
