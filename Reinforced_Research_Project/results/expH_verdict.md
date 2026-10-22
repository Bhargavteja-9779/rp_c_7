# Exp H verdict — wide-range kernel-ridge control (addendum v2.3, committed before the runs: 48a0698 / code 4-line commit "Exp H code")
Source: `results/expH_statistics.json`, `results/expA_primary/tables/expH{8,32}_cells.csv`. Same 24 instances, N in {64,256,1024}, seeds 0-2, same training subsets; POD+KRR with ridge lam in [1e-16, 1e-2] (x N), length-scale ell0 in [0.1, 30] x sqrt(p), eigendecomposition solve, validation-only selection; B = 8 (H8) or 32 (H32). Cells: the 28 cells where POD+GP-ARD beats the best NN by > 0.10 decade.

| err(KRR-wide)/err(POD+GP-ARD) in GP-clear cells | q25 | median | q75 | share <= 3x |
|---|---|---|---|---|
| Exp D (restricted range, B=8) — for reference (52 cells, N-levels 32-1024) | 4.7 | 14.3 | 137 | 13% |
| H8 (wide range, B=8) | 3.6 | **6.5** | 14.8 | 21% |
| H32 (wide range, B=32) | 1.9 | **2.7** | 4.4 | 57% |

Share of GP-clear cells in which wide KRR beats the best NN by > 0.10 decade: 61% (H8), 64% (H32). Median ratio by p (H32): 2.6 (p=3), 2.7 (p=4).

**Pre-registered verdict: MIXED** (H-RANGE required median <= 3 and >= 75% of cells <= 3 for H8 or H32; H32 has median 2.7 but only 57% within 3x. H-MLII required median > 3 for both; H32's median is 2.7).

## Interpretation (what is and is not supported)
* The Exp D gap (14x) was **largely a consequence of the restricted ridge/length-scale range and the 8-draw search**: widening the range halves it (6.5x) and a 32-draw search of the same wide space brings the median to within 3x of the GP (2.7x), with a long upper tail (q75 4.4x; 43% of cells > 3x).
* A residual factor of ~2-3x between a validation-tuned wide KRR and the ARD GP is consistent with some benefit of continuous marginal-likelihood fitting (and of ARD) but **marginal likelihood per se is not isolated**: the cost of the 32-draw search was not matched to the GP's optimisation cost.
* A *kernel regressor with a sufficiently wide, finely searched ridge* beats the best 1500-epoch NN in the smooth cells. Hence the defensible attribution is: **hyper-parameter optimisation quality and range of a smooth regressor (notably the effective ridge), not the POD subspace and not a neural-vs-kernel architectural property**.
* The manuscript's M-MLII wording ("explained by marginal-likelihood fitting") must be withdrawn/rewritten; Exp D's D1 rejection stands as stated (for the restricted-range KRR) and is reported together with Exp H.
