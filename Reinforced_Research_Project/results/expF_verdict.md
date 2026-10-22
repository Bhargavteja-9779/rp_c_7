# Exp F verdict (float64 + full-batch Adam 6000 steps + L-BFGS; rule pre-registered in addendum v2.2)
Source: `results/expF_statistics.json`, `results/expA_primary/tables/expF_cells.csv` (10 instances, N in {256,1024}, 3 seeds; stored best configs refit; oracle-best NL over {1500-epoch float32, f64 Adam, f64 Adam+L-BFGS}).

| Quantity (7 decisive instances at N=1024) | Value |
|---|---|
| decisive instances still with ybar_F >= 1 decade | **5 of 7** |
| median improvement of the NL error floor | 0.47 decade |
| median ybar: 1500-epoch float32 -> best-of-F | 2.51 -> 2.04 |
| smallest NL error reached | 6.8e-4 -> 2.0e-4 |
**Pre-registered verdict: ROBUST (>=5/7 remain >= 1 decade).**

## Caveats
- darcy_L1 (1.13 -> 0.63) and heat2d_L1 (1.38 -> 0.95) drop below one decade, so the pre-registered "decisive" set shrinks from 7 to 5 under a stronger optimiser; the LS wins of 1.8-2.7 decades on bratu, nlheat and burgers_L1 persist.
- The NL error floor is partly an optimiser/precision effect (0.25-0.72 decade improvements everywhere, including cells where NL already wins, where the NL margin grows: fisher_L2 -0.47 -> -0.56; heat2d_L2 -0.34 -> -0.59; transport_L2 -0.33 -> -0.48). So stronger NN optimisation helps in both regimes; it does not reverse any LS-clear cell (the two 'decisive' drops stay LS-clear: 0.63 and 0.95).
- Oracle-best selection over three refit variants uses *test* error to choose the NL variant (favourable to NL by design), so the reported NL improvement is an upper bound for what a validation-selected NL pipeline would obtain.
- Only stored configurations were refit; the search space was not re-tuned for the stronger optimiser.
