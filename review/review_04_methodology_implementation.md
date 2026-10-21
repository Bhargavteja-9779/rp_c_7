# Review 04 — Methodology and implementation

*Simulated adversarial pass by the Research Director (not an independent human or external reviewer). Each pass was written separately after the previous one's fixes.*

**Stance:** check equations, code, consistency between code and text.

| ID | Severity | Issue | Disposition |
|---|---|---|---|
| 4.1 | MODERATE | POD+GP final refit failed to reproduce selected-trial accuracy in 4/288 fits (>3x), 2/288 (>10x): single-start optimiser. | Quantified (E5), sensitivity analysis shows no verdict changes; disclosed. |
| 4.2 | MINOR | Text omitted that POD+MLP trains on coefficients scaled by sigma_1/sqrt(N); the batch rule (full batch if N<=512 else 512). | Documented in code; add to supplement (done in README). |
| 4.3 | MINOR | Code-manuscript consistency verified for: GP K_OPT=4 and N_OPT=300 subsampling, polynomial degree<=6 with 5,000-feature cap, 20% validation split, B=8 with default trial 0, 1500 epochs, float32, extrapolation box [-0.25,1.25]. | PASS by inspection. |
| 4.4 | MINOR | The FOM solvers define 'truth' at fixed grids; unit tests cover exact/refinement checks but not every parameter corner. | Disclosed in §7 item 8.
