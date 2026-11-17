# Changelog
## 0.4.1 (2026-11)
* The rational member is opt-in again (`default_candidates(..., with_rational=True)`, CLI `--with-rational`): its pre-specified evaluation did not meet the gain criterion (3 of 12 cells instead of 6; no loss on 52 earlier problems). The default pool is the 7 members of earlier versions.
## 0.4.0 (2026-11)
* New pool member `PodRational` (`pod_rational`): POD with a shared-denominator rational regression of the mode coefficients, for responses with poles or sharp peaks inside the parameter range (resonances of lightly damped or undamped systems). In 0.4.0 it was in the default pool (the Stage 10 experiments used that pool).
## 0.3.0 (2026-11)
* Empirical interval for the budget forecast (`forecast_interval`, `runs_needed_confident`; `calibration.py`): the 80 % / 90 % quantiles of the forecast error over 960 forecasts of 54 problems (leave-family-out coverage 79 % / 89 %). The report now states how rough the forecast is. The old three-point-versus-four-point range (which contained the actual error in under 10 % of held-out cases) is no longer printed. `predict_error` is unchanged; selection logic, pool and thresholds are unchanged.
## 0.2.1 (2026-11)
* Input validation with clear errors (1-D Y, NaN, mismatched lengths, too few runs for the folds, cv < 2, missing keys in .npz files; the CLI exits with status 2).
* The report notes when the learning curve is not monotone (forecast unreliable). No change to selection, forecast numbers, pool or thresholds.
## 0.2.0 (2026-11)
* No-usable-model warning (`usable_threshold`, default 0.25 on the best cross-validated error) in the report, `SurrogateSelector.usable_` and the CLI (`--usable-threshold`).
* Cost-benefit paragraph and `cost_benefit()`; CLI options `--solver-seconds` and `--queries`.
* Report states how reliable the error forecast was in the authors' evaluation (about two thirds within a factor two; more often optimistic).
* Optional tuned network from the CLI (`--with-network`, `--network-trials`); `TunedMLP(depth_range=..., widths=...)`.
* Selection logic, pool, grids and tie band are unchanged from 0.1.0 (results of the 0.1.0 evaluation apply).
## 0.1.0 (2026-10)
* First version: cross-validated selection with ties, basis-limit check, learning-curve forecast, CLI.
