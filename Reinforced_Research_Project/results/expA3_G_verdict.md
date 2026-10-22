# Exp A3 (descriptive, n=4) and Exp G (G1) — verdicts (pre-registered in addendum v2.2, commit c9a7b93)

## Exp A3 — probing the f1–p confound (no confirmatory power)
| Instance | p | f1 (pilot) | ybar at N=1024 |
|---|---|---|---|
| darcylin_L1 | 16 | -1.57 | +0.48 |
| darcylin_L2 | 32 | -1.60 | +0.18 |
| heatmv3_L1 (moving narrow source) | 3 | -0.23 | **-0.44** (NL-clear) |
| incl3_L1 (moving inclusion) | 3 | -1.29 | **-0.21** (NL-clear) |
Predictions: both p=3 instances with f1 > -2 are not LS-decisive (**met**); the nearly linear high-p instances do not reach f1 < -2 (**met**, f1 ~ -1.6).
Reading: (i) within p = 3, instances with weak reducibility (high f1) are NL-favoured, i.e. f1 carries signal *beyond* p (supportive, n = 2); (ii) a nearly linear high-p map is only mildly LS-favoured (0.18-0.48 decade) and f1 is mechanically bounded by r = 4 for such maps, so f1 partly proxies dimension. Together: f1 is informative but not a clean, dimension-free diagnostic. n = 4; descriptive only.

## Exp G — is POD truncation the driver? (GP on the full output, no POD)
Cells where POD+GP-ARD beats the best NN by > 0.10 decade: 28. err(GP-full) / err(POD+GP): quartiles 0.64 / **0.95** / 1.14; 100 % of cells <= 3; median over all 72 cells 0.85 (GP-full better at N=1024: 0.67).
**G1 supported**: removing the POD basis does not degrade the GP; the advantage over NNs is attributable to the (ML-II-fitted) GP regressor rather than to linear-subspace output compression.
Caveats: GP-full uses a shared ARD kernel across outputs, hyperparameters fitted on <= 300 points, B = 2 trials; cost is not matched (full-output GP is O(N^3) in samples but needs no POD). The 'LS vs NL' contrast is therefore best described as 'GP (ML-II) vs 1500-epoch NN regression'.
