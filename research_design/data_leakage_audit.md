# Data-leakage and validity audit (pre-run; updated after the run in review/)

| Risk | Control | Verified by |
|---|---|---|
| Train/test parameter overlap | Separate seeded RNG streams for train/test/extrapolation; extrapolation set lies strictly outside the unit box | `tests/test_methods.py::test_no_train_test_parameter_overlap` |
| Preprocessing leakage | POD mean/basis, scalers, output standardisation are fit inside `fit()` on training data only | code review + `POD` class; `fit` never receives test data |
| Test-set model selection | HPO picks by validation error only; test error logged separately; refit winner | `tests/test_methods.py::test_hpo_selects_by_validation_not_test` |
| Pilot features use non-pilot data | `pilot_features` receives only the first 32 training snapshots | `tests/test_methods.py::test_pilot_features_use_only_given_snapshots` |
| Seed-subset overlap inflating precision | Pool 4096, N ≤ 1024: subsets of different seeds overlap by chance (~25% at N=1024) → seed-to-seed variance **underestimates** true sampling variance at large N | declared limitation |
| Leave-one-family-out leakage | both levels of a family held out together | analysis code |
| Cherry-picking | protocol committed before runs; deviations log | git history |
| Synthetic-data realism | all data are simulations; no real-world claim | manuscript wording |
