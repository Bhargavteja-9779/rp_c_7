# Changelog
## 0.2.0 (2026-11)
* No-usable-model warning (`usable_threshold`, default 0.25 on the best cross-validated error) in the report, `SurrogateSelector.usable_` and the CLI (`--usable-threshold`).
* Cost-benefit paragraph and `cost_benefit()`; CLI options `--solver-seconds` and `--queries`.
* Report states how reliable the error forecast was in the authors' evaluation (about two thirds within a factor two; more often optimistic).
* Optional tuned network from the CLI (`--with-network`, `--network-trials`); `TunedMLP(depth_range=..., widths=...)`.
* Selection logic, pool, grids and tie band are unchanged from 0.1.0 (results of the 0.1.0 evaluation apply).
## 0.1.0 (2026-10)
* First version: cross-validated selection with ties, basis-limit check, learning-curve forecast, CLI.
