# SurroSelect

**Choose a fast stand-in (surrogate) for a slow simulation — and find out how many simulation runs you need.**

You have run a slow simulation N times (inputs `X`, output fields `Y`). SurroSelect

1. fits a small pool of stand-in models (Gaussian processes on a POD basis or on the full field, wide-range kernel ridge, polynomial; optionally a tuned neural network),
2. chooses by **k-fold cross-validation** and tells you which models are **tied** with the best (within about 26% error),
3. **checks whether the POD basis is your bottleneck** (compares the model error with the error of just projecting held-out fields onto the basis),
4. fits a **learning curve** and estimates **how many runs you would need** for a target error (flagged as unreliable when the curve is flat or the extrapolation is far).

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

Command line: `surroselect data.npz --target 0.01 --out report.md` (the `.npz` holds arrays `X` and `Y`).

Neural network candidate: `from surroselect.nn import TunedMLP; SurrogateSelector(candidates=default_candidates(m, N) + [TunedMLP()])`.
Command line: `surroselect fit data.npz --with-network [--network-trials 16]` adds the tuned network to the pool (slow: minutes to hours).

## What the numbers mean
* *Error* is the mean relative L2 error over held-out samples (cross-validated).
* *Tie band* 0.1 decade: errors within a factor of about 1.26 are treated as tied; do not read a winner into a tie.
* *Runs needed* extrapolates a power law through the last three learning-curve points; treat it as a rough guide (it is validated on third-party-solver problems in the paper, with the results reported there, including where it fails).

## Tests
`python -m pytest tests` (7 tests: closed-form leave-one-out against brute force, exact polynomial recovery, selection, basis-limit flag, power-law inversion, report/CLI).

## Limitations
Designed for smooth parametric maps with up to a few tens of inputs and outputs on a fixed grid; no uncertainty quantification beyond the learning-curve range; the neural candidate is tuned with a small budget; results on your problem may differ from the benchmark.

## Licence
MIT (copyright holder to be set by the authors).
