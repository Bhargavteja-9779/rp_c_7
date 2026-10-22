# Exp A2 verdict (pre-registered in protocol addendum v2.2, commit c9a7b93; p0 = 0.15, success k >= 4 of 7)
Source: `results/expA2_statistics.json`, `results/expA_primary/tables/expA2_cells.csv` (8 candidate instances, N in {64,256,1024}, 3 seeds, B=8, 1500 epochs).

| Criterion | Observed | Verdict |
|---|---|---|
| Q1: >= 4 of 7 pilot-qualifying (f1 < -2) instances have ybar >= 1.0 decade at N=1024 | **7 of 7** (ybar 2.38-2.93); exact binomial p vs p0=0.15 = 1.7e-6 | **PASS** |
| Q2: no qualifying instance with an NL-clear win (ybar < -0.10) at N=1024 | 0 of 7 | **PASS** |

## Caveats (reported, not hidden)
- **Confounded with parameter dimension again.** 6 of the 7 qualifying instances have p = 3 (heatp, helm, reacdiff); diff1d_L1 has p = 4. The only control (f1 = -1.72, p = 8, diff1d_L2) still has ybar = +1.00 at N=1024. The result supports "smooth, low-dimensional parametric maps strongly favour POD+GP over the 1500-epoch NNs", not that f1 carries information beyond p.
- Exp A2 shares the budget limitation shown by Exp B: the NN refits at 6000 epochs reduce LS advantages by ~0.25 decade (median), which does not threaten gaps of 2.4-2.9 decades; whether such large gaps survive precision/optimisation improvements is Exp F's question.
- At N=64, helm_L2 is already NL-ahead (-0.16) and several instances are near ties; the "decisive" claim is an N=1024 statement.
- The candidates were chosen *after* Exp A as post-hoc-motivated; the prediction and thresholds were pre-registered (v2.2) before any A2 run.
