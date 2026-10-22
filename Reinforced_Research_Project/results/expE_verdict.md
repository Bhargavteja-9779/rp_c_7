# Exp E verdict (isotropic-kernel GP control; rule pre-registered in addendum v2.1)
Source: `results/expE_statistics.json`, `results/expA_primary/tables/expE_cells.csv`. 24 instances x N in {64,256,1024} = 72 cells; POD+GP-iso (ML-II, one shared length-scale) vs POD+GP-ARD vs POD+KRR (matched random search, no ML-II), identical training subsets and seeds.

| Quantity (cells where GP-ARD beats best NN by > 0.10 decade; n = 28) | q25 | median | q75 |
|---|---|---|---|
| err(GP-iso) / err(GP-ARD) | 1.32 | **1.92** | 3.46 |
| err(KRR) / err(GP-iso) | 1.44 | **8.12** | 74.6 |
| err(KRR) / err(GP-ARD) | 4.29 | 13.4 | 150.8 |

**Pre-registered verdict: M-MLII** (median KRR/iso > 3 and median iso/ARD <= 3): marginal-likelihood fitting of kernel hyperparameters, not per-dimension anisotropy, accounts for most of the GP advantage over matched-search kernel ridge in these cells.

## Caveats
- Selection of cells is by GP-ARD clear wins, which exist only for p = 3 (12 cells) and p = 4 (16 cells) — the low-dimensional, smooth instances. Anisotropy is expected to matter little at p = 3-4; **Exp E says nothing about high-dimensional parameter spaces** (darcyhd p=16/32), where no clear GP-ARD win occurred. The mechanism claim is limited to low-p regimes.
- The 'KRR/iso' ratio is dominated by p = 3 cells (median 110x) vs 1.6x at p = 4; heterogeneous.
- ARD still gives a modest 1.9x median (q75 3.5x, max 45x) — anisotropy is not irrelevant, just second-order here; 25% of cells exceed the 3x line.
- KRR used the same random search budget B=8 (hyperparameters: kernel, length-scale, ridge), so "ML-II vs random search" is the contrast; a stronger KRR search (e.g., gradient-based or CV grid) was not run.
