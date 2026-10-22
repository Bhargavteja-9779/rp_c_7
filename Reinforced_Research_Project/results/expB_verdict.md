# Exp B (strong-NN refit, 6000 vs 1500 epochs) — verdict against pre-registered criteria
Source: `results/expB_statistics.json`, `results/expA_primary/tables/expB_cells.csv` (48 cells = 24 instances x N in {256,1024}; 3 seeds; stored best configs refit with 6000 epochs).

| Criterion (protocol v2.0) | Observed | Verdict |
|---|---|---|
| B1: sign of ybar retained in >=85% of clear cells (|ybar_1500|>0.10) | 30/34 = 88.2% | **PASS** (margin 3 percentage points) |
| B2: median shift toward NL < 0.5 decade | median 0.239 (max 0.498, min -0.050) | **PASS** (max is just under the limit) |

## Material caveats (reported, not hidden)
- The criteria pass, but the 1500-epoch budget was **not saturated**: 89.6% of refits improved, median error ratio 0.63. The shift toward NL is systematic (~0.25 decade median).
- Cell classes (LS-clear / tie / NL-clear at the 0.10-decade band) change in **15/48 cells (31%)**: 9 ties become NL-clear, 2 LS-clear become NL-clear, 4 LS-clear become ties; no NL-clear cell reverts. NL-clear cells: 12 -> 23 of 48. LS-clear: 22 -> 16.
- Large LS advantages (bratu, darcy_L1, burgers_L1, heat2d_L1, nlheat) persist at 6000 epochs (e.g. bratu 2.6-2.9 decades). The "LS wins big in smooth cells" finding is robust to NN budget; the *tie/NL boundary* in the weakly-structured cells is not.
- Consequence for the manuscript: report outcomes as budget-conditional; do not state the 1500-epoch class counts as budget-free facts. Exp F (float64 + L-BFGS) addresses whether the residual large gaps are optimisation artefacts.
