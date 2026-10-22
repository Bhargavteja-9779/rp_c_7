# Claim–evidence matrix (manuscript v3)
Evidence file paths are relative to `Reinforced_Research_Project/` (v1 files: repository root `results/`). Strength: S = supported by pre-registered test; D = descriptive/observational; X = exploratory; N = explicitly NOT claimed.

| # | Claim in manuscript | Evidence | Strength | Main threat / limit |
|---|---|---|---|---|
| C1 | At N=1024, LS clearly better in 13/24 instances, NL in 8, 3 ties; at N=32 5/5/14 | `results/expA_primary/tables/pooled_cells.csv`; Fig 1 | D | tie band 0.10 is a convention; config-draw halves agree on class in 83% of cells |
| C2 | LS advantage reaches ≥2 decades on smooth p=3 instances; 7/7 pre-selected new smooth instances ≥1 decade | `expA2_statistics.json`, `expA2_verdict.md` | S (prediction pre-registered) | 6/7 have p=3: confounded with dimension; NN budget (see C9) |
| C3 | NL wins appear on moving/discontinuous features and some high-p cases | `pooled_cells.csv`, A3 cells | D | few instances per feature type; 1500-epoch budget |
| C4 | H1a, H1b, H2 not supported (Stage 1); H4a supported at cell level | `../results/statistics.json` | S | H4a driven by 5/16 instances |
| C5 | Pilot diagnostic NOT confirmed out of sample; inconclusive | `expA_primary/statistics_expA_primary_FINAL.json`, `bootstrap_1e6_and_stepcount.json` | S | n=8 instances/4 families; power ≈0.5; nlheat carries 88% of gain |
| C6 | f1 correlated with p (ρ=0.71) | pooled cells | X | – |
| C7 | GP advantage due mostly to ML-II fitting (D1 rejected; M-MLII) | `expD_statistics.json`, `expE_statistics.json` | S (rules pre-registered) | p=3–4 cells only; KRR search B=8 (not an optimised KRR) |
| C8 | POD truncation is not the driver (G1) | `expG_statistics.json` | S | gp_full B=2, ≤300-pt hyper-fit, unmatched cost |
| C9 | Longer NN training moves outcomes toward NL; 15/48 classes change; large smooth-case gaps persist | `expB_statistics.json`, `expB_verdict.md` | S for B1/B2; D for class change | only 2 N values; stored configs refit, not re-tuned |
| C10 | Neural error floor is/is not an optimisation artefact | `expF_statistics.json` (when complete) | S (rule pre-registered) | 10 instances, seed 0–2 |
| C11 | Learning-curve crossover NOT claimed (step-count confound at N=1024) | design audit F02; `bootstrap_1e6_and_stepcount.json` | N | – |
| C12 | Direct MLP beats POD+MLP (17/24) so family label ≈ "GP vs NN" | computed in `build_v3.py` | X | seed-mean test errors, not validation-selected |
| C13 | Results are conditional on synthetic problems, in-house solvers, CPU float32 | limitations | N | – |
| C14 | No claim of SOTA, no new surrogate method, no real-world validation | – | N | – |
