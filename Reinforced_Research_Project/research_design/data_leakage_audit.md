# Data-leakage audit
Scope: all experiments (v1 – Stage 6). Data are simulated, so image-style duplicate/near-duplicate and prompt/label-leakage checks reduce to the following checks. Tests: `code/tests/test_leakage.py`, `code/tests/test_problems*.py`, `surroselect/tests`, and `audit/leakage_planted_test.py` (planted leak).
| Check | Method | Result |
|---|---|---|
| Train/test overlap | Parameters of train pool, test set and extrapolation set are drawn from separate named streams (sha256 of name+stream); `audit/leakage_planted_test.py` verifies zero exact matches between sets for all 44 problems and a minimum nearest-neighbour distance in parameter space. | no overlap |
| Duplicates / near-duplicates | Minimum pairwise distance in the 4,096-point pool vs the expected minimum for i.i.d. uniform draws | consistent with i.i.d. (see script output) |
| Fitting on test data | Validation error unaffected when all test labels are corrupted (unit test); POD, scalers, GP/KRR/poly hyper-parameters, pilot features use training rows only; tool CV folds are built from training rows | passes |
| Test-set tuning | Winners are chosen by validation or cross-validation error; mechanism experiments that compare against the best network by *test* error are labelled as oracle comparisons in the paper | disclosed |
| Seed/subset overlap | Training subsets for different N are nested within a seed permutation; seeds share the pool and test set | disclosed (seed variance understates sampling variance at large N) |
| Planted-leak test | Plant a leak (copy 20 test samples into the training set) and show that the audit's overlap check flags it, and that a model evaluated on the leaked set shows a much lower error | see `audit/leakage_planted_test.py` and `results/leakage_planted_test.json` |
