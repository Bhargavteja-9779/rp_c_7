# SurroSelect

**Choose a fast stand-in (surrogate) for a slow simulation — and find out how many simulation runs you need.**

You have run a slow simulation N times (inputs `X`, output fields `Y`). SurroSelect

1. fits a small pool of stand-in models (Gaussian processes on a POD basis or on the full field, wide-range kernel ridge, polynomial; optionally a tuned neural network),
2. chooses by **k-fold cross-validation** and tells you which models are **tied** with the best (within about 26% error),
3. **checks whether the POD basis is your bottleneck** (compares the model error with the error of just projecting held-out fields onto the basis),
4. warns when **no pool member is usable** (best cross-validated error above 0.25: the selection then only ranks models that all fail),
5. fits a **learning curve** and estimates **how many runs you would need** for a target error (flagged as unreliable when the curve is flat or the extrapolation is far),
6. optionally prints a **cost-benefit paragraph** from the time of one solver run (`--solver-seconds`, `--queries`): after how many evaluations the stand-in is cheaper than the solver.

It is built on the findings of a 44-problem benchmark study (see the paper in `../manuscript`): on smooth problems with few inputs a well-regularised Gaussian-process or kernel model is hard to beat; polynomials are a strong cheap baseline; the winner depends on the training budget, tuning effort and basis limits.

## Install and use

```bash
pip install -e .            # numpy, scipy, scikit-learn
pip install -e ".[nn]"      # optional: torch + optuna for the tuned neural-network candidate
```

```python
import numpy as np
from surroselect import SurrogateSelector, make_report

sel = SurrogateSelector(cv=4).fit(X, Y)      # X: (runs, inputs), Y: (runs, outputs)
sel.learning_curve()                         # optional: needed for the budget estimate
print(make_report(sel, target=0.01))         # table, tie set, basis check, runs needed for 1% error
Y_new = sel.predict(X_new)                   # prediction with the selected model
```

Command line: `surroselect fit data.npz --target 0.01 --solver-seconds 30 --queries 10000 --model model.pkl --report report.md` (the `.npz` holds arrays `X` and `Y`); then `surroselect predict model.pkl X_new.npy --out Y_new.npy` and `surroselect evaluate model.pkl test.npz`.

Cost-benefit in Python: `from surroselect import cost_benefit; cost_benefit(solver_seconds=30, n_train=256, tool_seconds=120, n_queries=10000)`.

Neural network candidate: `from surroselect.nn import TunedMLP; SurrogateSelector(candidates=default_candidates(m, N) + [TunedMLP()])`.
Experimental pole-aware member: `surroselect fit data.npz --with-rational` (or `default_candidates(m, N, p, with_rational=True)`): POD with a rational regression of the mode coefficients; it helped on single-resonance frequency-response problems with enough runs and did no harm on 52 earlier problems, but it missed its pre-specified gain criterion and is not in the default pool.
Command line: `surroselect fit data.npz --with-network [--network-trials 16]` adds the tuned network to the pool (slow: minutes to hours).

## What the numbers mean
* *Error* is the mean relative L2 error over held-out samples (cross-validated).
* *Tie band* 0.1 decade: errors within a factor of about 1.26 are treated as tied; do not read a winner into a tie.
* *Runs needed* extrapolates a power law through the last three learning-curve points; treat it as a rough guide (it is validated on third-party-solver problems in the paper, with the results reported there, including where it fails).

## Tests
`python -m pytest tests` (13 tests: closed-form leave-one-out against brute force, exact polynomial recovery, selection, basis-limit flag, power-law inversion, report/CLI round trip, numerically stable near interpolation, alternative metric, scalar outputs, the optional network, the no-usable-model warning, the cost arithmetic).

## Limitations
Designed for smooth parametric maps with up to a few tens of inputs and outputs on a fixed grid; no uncertainty quantification beyond the learning-curve range; the neural candidate is tuned with a small budget; results on your problem may differ from the benchmark.

## Licence
MIT (copyright holder to be set by the authors).

## API summary
| Object | Purpose |
|---|---|
| `SurrogateSelector(candidates=None, cv=4, tie_band=0.1, random_state=0, metric="rel_l2", usable_threshold=0.25)` | `.fit(X, Y, refit_all=False)`; attributes `best_name_`, `ties_`, `cv_table_`, `floor_report_`, `usable_`; `.learning_curve()`, `.predict_error(n)`, `.runs_needed(target)`, `.predict(X)` |
| `make_report(sel, target=None, solver_seconds=None, n_queries=None, tool_seconds=None)` | plain-text/markdown report |
| `cost_benefit(solver_seconds, n_train, tool_seconds=0, n_queries=None, predict_seconds=0)` | break-even arithmetic |
| `default_candidates(m, N)`, `make_candidate(name)`, `PodGP`, `GPFull`, `PodKRRWide`, `PodPoly`, `POD` | pool members |
| `surroselect.nn.TunedMLP` | optional tuned network (torch + optuna) |

Inputs are scaled to the unit cube internally; outputs must share one grid; runs are assumed exchangeable and deterministic.
