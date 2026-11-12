# SurroSelect report
256 runs, 5 inputs, 108 outputs. Cross-validated mean relative L2 error (4 folds).

| model | CV error | within tie band of best | seconds |
|---|---:|:---:|---:|
| pod_gp[rbf,r=32] | 4.311e-03 | yes | 7.7 |
| gp_full[rbf] | 4.895e-03 | yes | 21.7 |
| gp_full[matern52] | 9.161e-03 |  | 19.5 |
| pod_gp[matern52,r=32] | 9.461e-03 |  | 7.6 |
| pod_gp[matern52,r=8] | 9.472e-03 |  | 7.3 |
| pod_krr_wide | 4.405e-02 |  | 0.6 |
| pod_poly | 5.099e-02 |  | 0.1 |

**Selected:** pod_gp[rbf,r=32] (CV error 4.31e-03). Models tied with it (within 1.26x): pod_gp[rbf,r=32], gp_full[rbf].

**Basis check.** Best POD-based model: pod_gp[rbf,r=32] (CV error 4.31e-03); error of projecting held-out fields on a 32-mode basis: 1.63e-06. The POD basis is not the limiting factor at this training size.

**Learning curve** (pod_gp[rbf,r=32]): n=24: 1.86e-01, n=48: 8.82e-01, n=96: 2.88e-02, n=192: 4.31e-03
Extrapolated error with 1024 runs: about 5.4e-06 (range 5.4e-06 to 2.1e-04); extrapolation over 4x the data is a rough guide only (in the authors' evaluation on 16 test problems, about two thirds of such forecasts were within a factor two of the actual error, and they were more often too optimistic than too pessimistic).
Runs needed for error 0.001: about 263.

**Cost.** 256 runs at 10.08 s take 0.72 h; with the tool the fixed cost is 0.74 h, and the stand-in is cheaper than the solver after about 264 evaluations. For 10000 expected evaluations: solver 28.00 h against 0.74 h with the stand-in. Validation runs, parallel solver evaluation and the accuracy given up are not counted.