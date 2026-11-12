# Protocol addendum v3.3 (Stage 8) — written and committed BEFORE any surrogate was fitted to the new problem
Written 2026-11-12, after the rejection of the manuscript by the first journal and the choice of a software-oriented engineering journal (`audit/final_journal_decision.md`). The remaining removable weaknesses named by simulated review 04 that need new data are: the only "expensive" case was a finer mesh of a problem already used, and the tool printed a selection even where no model is usable.

**What was looked at before this file was written.** Solver run times of the new problem (a few solves at several mesh sizes, to pick a size of about ten seconds per run), 3 unit tests (Euler–Bernoulli beam, load reversal, exact stiffness scaling, band sensitivity, mesh convergence), and a smoke test of the run script on the already-seen problem `lshape_L1` with a small network budget. No error of any surrogate on the new problem had been seen. For the warning check (U below) nothing had been computed from the stored results of Stages 6 and 7 with the 0.25 threshold; the threshold was chosen as "a relative error above 25 % is not a usable stand-in for an engineering decision", not from data. Because the Stage 6 and 7 results are known, U is **design-informed**, not held-out.

**Frozen.** SurroSelect 0.2.0 (`surroselect/`; selection logic, pool, grids and tie band unchanged from 0.1.0; new: the no-usable-model warning with threshold 0.25 on the best cross-validated error, a cost-benefit paragraph, CLI options), the benchmark package, the run script and these criteria, at the commit that contains this file (hash in `research_design/freeze_v3.3.txt`, recorded before the first run).

## 8.1 Problem (scikit-fem 12.0.2, `problems_tp3.py`)
`bracket3d_L1`: linear elasticity of a three-dimensional cantilever (4 × 1 × 0.5, tetrahedral mesh 56 × 20 × 10 cells, about 39,500 degrees of freedom), three stiffness bands along its length (moduli log-uniform 1 to 10), Poisson ratio in [0.2, 0.4], tip-load angle in [0, π]; p = 5; output: the three displacement components at 36 interior points (m = 108). About ten seconds per run on this machine. Data: 512 training-pool runs and 300 test runs (hash-seeded draws as before); training subsets `default_rng(1000+seed).permutation(512)[:N]`.

## 8.2 Experiment E8
N ∈ {64, 256}, seeds 0–2: the tool (default pool, 4-fold CV, `refit_all=True` so that the oracle is known; learning curve), always-POD+GP (matern52, rank 32), and at N = 256 the tuned network (16 trials, as in Stage 6). Runs are serial (one process, one thread) so that timings are clean. Measured: seconds per solver run (median of 8 idle solves), tool seconds with and without the evaluation-only refit, the break-even number of evaluations (N · t_sim + t_tool)/t_sim and the hours for 10,000 evaluations with and without the surrogate.

## 8.3 Criteria (E8 seed-means; U on stored results)
* **E8-1 selection**: regret (test error of the selected model divided by the best pool member's) ≤ 2.0 at both N.
* **E8-2 usable**: the no-usable-model warning does not fire in any of the 6 fits, and the selected model's test error is ≤ 0.25 at both N.
* **E8-3 forecast**: the forecast of the test error at 256 from the 64-run fit is within a factor 2 of the same candidate refit on 256 runs in at least 2 of 3 seeds.
* **E8-4 network**: the tuned network is better than the tool by more than 25 % in at most 1 of 3 seeds at N = 256.
* **E8-5 cost**: reported, no threshold.
* **U (warning, design-informed)**: over the 144 jobs of the 16 third-party problems (3 budgets × 3 seeds each; Stage 6 and Stage 7 results), "unusable" = the selected model's test error > 0.25; the warning is "best cross-validated error > 0.25". Criterion: sensitivity ≥ 0.9 and specificity ≥ 0.9. Reported with counts.

## 8.4 Predictions stated now
E8-1 and E8-2 will hold (smooth elasticity; selected test error of order 10⁻³); E8-4 will hold; E8-3 is uncertain and will probably **fail** (the forecast failed on the held-out problems of Stage 7 and was too pessimistic in the one expensive case); the break-even will be close to the number of training runs plus a tool time of about two to three solver runs per ten runs of training; U: sensitivity will be high (the failing Helmholtz jobs have cross-validated errors close to 1) and specificity high, but not certain near the threshold.

## 8.5 Rules
No criterion, pool member, grid or threshold is changed after the first result; deviations are logged (V16 onwards); analyses added after seeing results are labelled post hoc. One problem is one data point for selection and forecasting; E8 is a cost measurement and a smoke check of the tool on a realistic engineering model, not a general validation.
