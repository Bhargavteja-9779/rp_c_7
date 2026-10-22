# Round 1 - counterfactual / adversarial test of the central conclusions

Reviewer role: adversarial counterfactual tester (AI agent, fresh context). Target: `manuscript/Final_Manuscript_v3.md` and the code/results it rests on.
Constraints respected: no repository file was modified except this report; no long training run was launched. The probes below used existing data plus short CPU-only jobs (single-seed, 2-10 minutes each, four in parallel). All scratch scripts and outputs are in the session scratchpad (`.../scratchpad/c1.py ... c23.py`, `nn_cf.py`, `krr_cf.py`, `krr_cf2.py`, `gpfull_a3.py`; outputs `nn_cf_out.jsonl`, `krr_cf2.out`, `gpfull_a3.out`). Throughout, y = log10(err_NL / err_LS) as in the manuscript; "decade" = factor 10 in error. I reuse the notation C-n / M-n / m-n for findings.

Central claims tested:
(1) POD+GP beats lightly tuned NNs by up to ~3 decades on smooth low-dimensional instances.
(2) The advantage is due to marginal-likelihood fitting, not the POD subspace, not anisotropy.
(3) NNs are competitive/better on moving-feature and some high-p instances.
(4) Outcome classes depend on NN budget, tuning and random-search draw.
(5) The pilot diagnostic was not confirmed.

## 0. Bottom line

| Claim | Verdict after counterfactuals | Safety |
|---|---|---|
| (1) GP >> NN on smooth low-p | Sign and order of magnitude survive every probe (independent float64 + L-BFGS NN still 2.1-2.7 decades behind on the p=3 cells). The "up to 3 decades" number is specific to 1500-epoch float32 Adam, the interpolation test set and N=1024; it is about 0.7 decade smaller with a better optimiser and 1-2 decades smaller on the extrapolation set. | Safe in sign; magnitude needs qualifiers (M-2) |
| (2) "ML-II, not subspace, not anisotropy" | "Not the subspace" survives in GP-clear cells. "Because of marginal-likelihood fitting" does **not** survive: a plain kernel-ridge regressor tuned by leave-one-out on a 2-D grid matches or beats POD+GP on the smoothest cells once its ridge range is not truncated; the manuscript's KRR control was handicapped by its own search box. "Not anisotropy" fails in 8 of 28 cells (burgers_L1: isotropic GP 40x worse). | **Not safe as worded** (M-1) |
| (3) NNs better on moving features / some high p | **Largely an artefact of the POD rank cap (r <= 32) inside the "linear-subspace" family.** A GP on the full field (the authors' own Exp G runs, plus my two new runs on the Exp A3 instances) beats the best NN on the moving-inclusion/moving-source instances, so the neural "wins" there are not wins over Gaussian-process regression. | **Least safe** (C-1) |
| (4) Classes depend on budget/tuning/draw | Survives and is actually understated: single-seed class agreement is only 72%; headline counts move by +-3 between seeds; N=1024 count has a step-count discontinuity (M-3). | Safe |
| (5) Diagnostic not confirmed | Survives as stated ("inconclusive"). Exploratory partial rho(f1, y | p) = -0.70 over 36 instances suggests the "just a dimension proxy" worry is mild. | Safe |

No leakage, no metric mismatch, no dropped/replaced failed fits and no violated pre-registered selection rule were found (Section 2).

## 1. Findings ranked

### CRITICAL

**C-1. The neural "wins" on moving-feature instances are produced by the POD truncation cap, not by neural networks beating Gaussian-process regression; the manuscript's own Exp G data show this, and it is not reported.**

Evidence (all from existing data unless stated):
1. In the NL-clear and tie cells the POD+GP error equals the POD projection floor at r = 32 (the maximum rank in the search space). Test-set projection error with POD fitted on the N=1024 training subset (`c10.py`):
   heat2d_L2 floor(r=32) 5.4e-2 vs POD+GP 5.4e-2; heatmv3_L1 5.3e-2 vs 5.3e-2; incl3_L1 4.1e-3 vs 4.1e-3; incl_L1 2.0e-3 vs 2.0e-3; incl_L2 4.2e-3 vs 4.5e-3. The regressor is not the limiting factor there; the linear subspace is.
2. Exp G (`gp_full`, one shared ARD GP on the full field, no POD, B = 2 only) was analysed only in the "GP-clear" cells (median ratio 0.95, G1 supported). In the NL-clear cells the same runs show the opposite: median err_full/err_PODGP = 0.86 over 30 NL-clear cells, minimum 0.011. Adding `gp_full` as a fourth candidate to the validation-selected LS side (same validation protocol, same seeds; `c12.py`) changes the 24-instance classification:

   | N | primary (LS / tie / NL) | with gp_full on the LS side |
   |---|---|---|
   | 64 | 8 / 11 / 5 | 10 / 9 / 5 |
   | 256 | 9 / 11 / 4 | 14 / 6 / 4 |
   | 1024 | 13 / 3 / 8 | 18 / 2 / 4 |

   At N=1024 the instances that flip from NL-clear to LS-clear are heat2d_L2 (y -0.34 -> +0.68), incl_L1 (-0.25 -> +0.75), incl_L2 (-0.13 -> +0.48); darcyhd_L1 becomes a tie (-0.13 -> -0.04). Advdiff_L2 (tie) becomes LS-clear (+0.75). The NL-clear cells that survive are the travelling-front problems transport_L2 (-0.25), kdv_L1 (-0.23), fisher_L2 (-0.44) and the p = 10 Darcy darcy_L2 (-0.15).
3. New run (`gpfull_a3.py`, seed 0, N=1024, the Exp G protocol with B = 2) on the two Exp A3 probes that the manuscript cites as "moving features favour the neural family":
   heatmv3_L1: gp_full 1.2e-3 vs best NN 1.9e-2 (POD+GP 5.3e-2); incl3_L1: gp_full 2.7e-4 vs best NN 2.4e-3 (POD+GP 4.1e-3). The full-field GP is ~1.2 and ~0.95 decade better than the best NN, whereas the POD+GP was 0.44 and 0.21 decade worse.
Interpretation: parameter -> field maps with a moving feature are smooth in mu; what fails is the low-dimensional *linear* subspace (slow Kolmogorov n-width), not kernel regression. The manuscript text "neural networks are competitive or better on problems with moving or discontinuous features" (Sections 5.1, 6, 8 and abstract) is true only against POD-based surrogates truncated at r <= 32. It is false against a full-field GP for incl, heat2d_L2, heatmv3 and incl3, and mixed for the remaining travelling-front instances.
Does the conclusion survive? Claim (3) survives only in a narrower form: NNs beat all GP variants on travelling fronts (transport_L2, kdv_L1, fisher_L2) and on the p = 10 Darcy map at N=1024 (all margins 0.15-0.44 decade).
Fix: (a) report Exp G in all cells, not only GP-clear ones; (b) run `gp_full` (cheap) on the four Exp A/A3 instances missing from Exp G (incl3, heatmv3, darcylin x2) and on N=32-512; (c) either add `gp_full` to the primary LS family or rename the family "POD-based" and say that the neural wins are wins over a *truncated linear subspace*; (d) reword claim (3) and the abstract sentence "the neural family in 8" accordingly; (e) optionally allow r up to 64-128 in the POD+GP search space.

### MAJOR

**M-1. "The advantage is due to marginal-likelihood fitting" is confounded with search-space design and hyper-parameter-optimisation effort; the kernel-ridge control (Exp D) was handicapped.**
Evidence:
- `PodKRR.sample_config` (methods.py) draws ridge lam in [1e-10, 1e-2] (times N) and length-scale ell0 in [0.1, 3] x sqrt(p), eight random draws, one (ell, lam) shared by all POD modes. POD+GP's WhiteKernel lower bound is 1e-10 on a normalised target and its length-scales are optimised continuously per mode.
- New probe (`krr_cf2.py`, seed 0, POD r = 16, isotropic RBF or Matern-5/2, (ell, lam, kernel) chosen by closed-form leave-one-out error on a 40 x 29 grid, no marginal likelihood, no ARD, no per-mode tuning). Test errors, same training subsets as the stored runs:

  | instance, N | POD+GP-ARD (stored) | GP-iso (Exp E) | KRR random-8 (Exp D) | KRR LOO grid, **matched ranges** (lam >= 1e-10 N, ell <= 3 sqrt(p)) | KRR LOO grid, ridge allowed down to 1e-16 N | best NN (stored) |
  |---|---|---|---|---|---|---|
  | bratu_L1, 256 | 1.4e-6 | 1.4e-6 | 3.2e-4 | 3.0e-5 | **1.4e-7** | 1.8e-3 |
  | bratu_L1, 1024 | 3.9e-7 | 5.0e-7 | 2.9e-4 | 1.2e-5 | **4.4e-8** | 1.0e-3 |
  | nlheat_L1, 256 | 4.2e-6 | 3.8e-6 | 6.6e-4 | 2.3e-5 | **7.2e-7** | 1.2e-3 |
  | nlheat_L1, 1024 | 1.3e-6 | 1.3e-6 | 2.8e-4 | 1.2e-5 | **4.6e-8** | 5.9e-4 |
  | darcy_L1, 256 | 7.5e-4 | 2.6e-4 | 5.3e-3 | 2.8e-3 | 2.7e-3 | 5.1e-3 |
  | darcy_L1, 1024 | 1.9e-4 | 1.4e-4 | 2.0e-3 | 2.6e-3 | 2.6e-3 | 2.9e-3 |
  | burgers_L1, 1024 | 1.8e-5 | 7.2e-4 | 3.6e-3 | 6.7e-4 | 6.3e-4 | 3.9e-3 |

  (a) On the p = 3 cells that carry the "three decades" headline, plain kernel ridge tuned by LOO on a wider ridge range is 10-100x **better** than POD+GP; with the ridge range truncated at the control's own 1e-10 floor it is 10-30x better than the matched random-search KRR but still 10-30x worse than the GP. So most of the reported 14x (up to 490x) KRR gap is the control's ridge floor plus random-search coverage, not the absence of marginal likelihood. The optimum ridge in these cells is <= 1e-14 N, outside the control's search box.
  (b) In the moderate cells the picture is different and my probe cannot fully separate the causes. At darcy_L1 the shared-kernel LOO KRR stays 14x behind the GP (2.6e-3 vs 1.9e-4 at N=1024) although the isotropic ML-II GP matches the ARD GP (1.4e-4), so there either per-mode kernels or the ML-II criterion matters; at burgers_L1 the isotropic ML-II GP is itself 40x worse than the ARD GP (7.2e-4 vs 1.8e-5, Exp E stored), so anisotropy is decisive. Exp E lists 8 of 28 GP-clear cells with iso/ARD > 3 (burgers_L1 45x, transport_L1 10x, wave_L1 6.7x, fisher_L1 4.3x). The "median 1.92x" and rule M-MLII hide that anisotropy/per-mode kernels matter in the moderate-margin instances, which are exactly the cells where the GP advantage is 0.5-2.3 decades rather than 2.5-3.
Does the conclusion survive? "The subspace is not the driver" survives (Exp G, GP-clear cells). "Marginal likelihood is the driver" does not: the supported statement is "continuous, criterion-driven hyper-parameter optimisation over a wide range (ridge down to ~1e-14; ML-II or LOO alike) of a kernel regressor, with per-mode/ARD kernels where anisotropy matters". The abstract sentence "explained by marginal-likelihood hyper-parameter fitting (kernel ridge under matched search was a median 14x worse)" should be reworded; the M-MLII label from the pre-registered rule is a statement about that rule, not a mechanism.
Fix: add a LOO-tuned KRR arm with a widened ridge range (minutes per instance; closed-form LOO as in `krr_cf2.py`), report the optimum-ridge location relative to the Exp D search box, and state the confound in Section 5.3/Limitations. If the pre-registered D1/M-MLII verdicts are kept, label the new arm exploratory.

**M-2. The size of the headline ("up to three decades") depends on weak NN optimisation, on N=1024 and on the interpolation test set; the extrapolation results exist but are not reported.**
Evidence:
- The NN error floor is optimisation-limited, not search-limited: across the eight sampled configurations (width/depth/activation/lr/wd) the mean log10 test error of mlp_direct on the decisive instances at N=1024 spans only 0.4 decade (-2.9 to -2.5; `c16.py`), and for the nlheat/helm/reacdiff cells with logged training loss the test error is 0.3-0.5 x sqrt(train MSE), i.e. the nets do not even interpolate their training data (`c4.py`).
- New NN probe (`nn_cf.py`, seed 0, float64, tanh 128 x 3, no tuning at all: 2000 Adam steps then 3000 full-batch L-BFGS iterations, wd = 0). Best of {direct MLP, POD-MLP with per-mode standardised coefficients}, versus stored best NN and the selected LS model:

  | instance, N | stored best NN | probe NN | LS (stored) | y stored -> y probe |
  |---|---|---|---|---|
  | bratu_L1, 256 | 1.8e-3 | 2.0e-4 | 1.4e-6 | 3.11 -> 2.16 |
  | bratu_L1, 1024 | 1.0e-3 | 2.0e-4 | 3.9e-7 | 3.42 -> 2.72 |
  | nlheat_L1, 256 | 1.2e-3 | 1.7e-4 | 4.2e-6 | 2.45 -> 1.61 |
  | nlheat_L1, 1024 | 5.9e-4 | 1.6e-4 | 1.3e-6 | 2.67 -> 2.10 |
  | helm_L1, 256 / 1024 | 1.1e-3 / 7.0e-4 | 2.5e-4 / 1.7e-4 | 3.1e-6 / 9.6e-7 | 2.56 -> 1.89 / 2.86 -> 2.25 |
  | burgers_L1, 1024 | 3.9e-3 | 4.5e-4 | 1.8e-5 | 2.35 -> 1.41 |
  | darcy_L1, 256 / 1024 | 5.1e-3 / 2.9e-3 | 9.1e-4 / 5.0e-4 | 7.5e-4 / 1.9e-4 | 0.83 -> 0.09 / 1.18 -> 0.42 |
  | heat2d_L2, 1024 (NL-clear) | 3.3e-2 | 1.8e-2 | 5.5e-2 | -0.22 -> -0.48 |

  Median NN improvement 0.73 decade (12 cells), larger than Exp F's 0.47 (Exp F used the stored configs and 400 L-BFGS iterations). The p = 3 gaps stay at 1.6-2.7 decades (claim 1 survives), but the moderate instances shrink below one decade (darcy_L1) and the NL-clear boundary moves further toward the NN, exactly the pattern of Exp B/F. This is a single-seed, untuned probe, not a replacement result.
- Extrapolation set (500 points, coordinates in [-0.25, 1.25] outside [0, 1]^p): recomputed y_ext from the stored `ext_err` with the same validation-selected members (`c8.py`). At N=1024 the advantage shrinks by 1-2 decades on the decisive cells (bratu_L1 3.31 -> 1.49; nlheat_L1 2.72 -> 1.84; helm_L2 2.64 -> 0.69; burgers_L1 2.25 -> 1.02); on the decisive cells the GP error inflates by 2-4.3 decades from interpolation to extrapolation, the NN by 1.1-2.8. LS stays clear in 19 of the 23 interpolation-LS-clear cells (36-instance set); burgers_L2 (-0.56), wave_L1 (-0.22) and kdv_L2 (-0.27) move to NL-clear and transport_L1 to a tie. The manuscript never mentions this (H3 is absent from v3, only the data section mentions the extrapolation set).
- Exp F rule applied at N=256 (stored data, `c3.py`): 4 of 7 decisive instances keep y >= 1 (burgers_L1 0.26, heat2d_L1 0.37, darcy_L1 0.67 fall), i.e. verdict PARTIAL, not ROBUST. At N=1024 the verdict is exactly at its threshold (5/7; darcy_L1 0.63 and heat2d_L1 0.95).
Fix: state the headline as "up to ~3.3 decades at N=1024 against 1500-epoch float32 Adam; about 2.1-2.7 after float64 + L-BFGS; 0.7-1.9 decades on the extrapolation set", report the extrapolation table, and show Exp F at both N. Do not use "robust" without the N qualifier.

**M-3. The N=1024 headline (13/8/3) is contaminated by the batch/step discontinuity; N=512 is the last like-for-like budget.**
Evidence (`c15.py`): NN best error improves by a median 0.099 decade from 256 to 512 but by 0.242 decade from 512 to 1024 (larger in 96% of instances); the POD+GP improves by 0.235 and 0.220. Three cells that are ties at N=512 become NL-clear at N=1024 (darcyhd_L1 -0.05 -> -0.13, incl_L1 -0.03 -> -0.25, incl_L2 0.00 -> -0.13) while no cell moves the other way. Table 2 (NL-clear 5 at N=512, 8 at N=1024) therefore partly reflects the protocol change (1500 full-batch steps to 3000 mini-batch steps), which the manuscript flags only for the learning-curve hypothesis (H1b), not for the headline counts or the "(13, 8, 3)" in the abstract.
Fix: report the headline at N=512 as well (12 / 7 / 5), or re-fit the N=1024 NNs with full-batch 1500 steps for the final model (a short job on stored configs) and recompute.

**M-4. Several NL-clear cells are weakly supported, so the "some high-p instances" part of claim (3) rests on two instances.**
Evidence (`c9.py`, `c17.py`): of the 35 NL-clear (instance, N) cells only 57% have all three seeds beyond the +-0.10 band (LS-clear: 80%); at N=32 only 4 of 10 clear cells are consistent. At N=1024, darcyhd_L1 (p=16, y = -0.125, seed range -0.37 to +0.07) and darcy_L2 (p=10, y = -0.19, one seed +0.01) are inconsistent across seeds; darcyhd_L2 (p=32) is a tie and darcylin_L1/L2 (p=16/32) are LS-clear. Single-seed class counts at N=32 are NL-clear 5/5/10 and at N=1024 LS-clear 14/11/13 (`c19.py`); the class agreement between two single seeds is 72%.
Fix: give per-instance bootstrap/seed CIs next to every class; describe the high-p result as "unresolved at p >= 10" rather than "NNs competitive in some high-dimensional parameter spaces".

### MINOR

**m-1. Family bundling still matters at small N.** pod_mlp is inside the "linear-subspace" family and is LS* in 47% of N=32 cells (21% at N=1024). Treating POD+GP/POD+Poly as the LS side and all three NNs as the NL side gives 4 / 11 / 9 at N=32 (instead of 5 / 14 / 5) and 13 / 2 / 9 at N=1024 (instead of 13 / 3 / 8); POD+GP alone vs the two NL nets gives 5 / 10 / 9 at N=32. The statement "most N=32 cells are ties" is definition-dependent (14, 11 or 10 of 24). (`c5.py`; consistent with the earlier audit F13.)

**m-2. Exp F is a test-oracle comparison and sits on its verdict boundary** (see M-2); it only refits stored best configurations, so lr/wd/width were never re-tuned in float64. Direction of bias is conservative for the GP claim, but the "ROBUST" label is not informative about magnitude.

**m-3. Exp A2 (Q1) null is far too easy.** All 7 qualifying candidates were authored (after Exp A) as smooth p = 3-4 problems; Q1's null p0 = 0.15 is the rate among f1 >= -2 instances, so the nominal p = 1.7e-6 is meaningless (with the pooled base rate 7/24 = 0.29 it would be 1.7e-4; with 4 effective families about 5e-4 to 7e-3). The conclusion (decisive in 7/7) is correct, but "pre-selected new instances" does not make this an out-of-sample test of the regime beyond family-level generalisation.

**m-4. Exp D / E / G use oracle (test-error) comparators and different cell sets** (D: 144 cells, 52 GP-clear; E and G: 72 cells, 28 GP-clear), so "14.3x" and "8.1x x 1.92x" are not the same cells; the GP-clear selection also conditions on a low GP error (mild upward bias of all ratios). Label the numbers "oracle, cell set n = ...".

**m-5. Isolated ML-II failures of the GP.** pod_gp on burgers_L1 jumps to 4.7e-2 (seed 0, N=256) and 4.5e-2 (seed 1, N=512) against ~2e-4 and ~1e-5 for the other seeds, giving a non-monotone seed-mean curve (1.0e-3 at 128, 1.6e-2 at 256, 1.5e-2 at 512, 1.6e-5 at 1024). The failures are *kept* (conservative for the GP claim, validation then selects another LS member) but they are an unreported optimiser instability (n_restarts_optimizer = 0, start at length-scale 1). Mention it; a 2-3 restart variant would likely remove it.

**m-6. Pilot diagnostic.** The verdict "inconclusive" is fair. Additional descriptive context (all exploratory, features were first chosen on 16 of the 36): Spearman(f1, y1024) = -0.785 over 36 instances; partial rho given log p = -0.70; family-level (n = 19) rho = -0.68; the unfrozen slope feature gives rho = -0.62 on the 8 Exp A instances vs -0.38 for the frozen f1; the pooled LOFO claim 1.07 -> 0.62 reproduces (`c18.py`), and baseline {log2 N, log p} is *worse* (1.47) than {log2 N} alone. The threshold -2.0 sits 0.003 below burgers_L1 (f1 = -1.9972, y = 2.25), a decisive instance that the rule excludes.

**m-7. Reporting gaps.** Methods text states "1500 epochs, float32" for all N without the N > 512 mini-batch rule; the main text does not report the GP optimiser instability, the extrapolation results, or the Exp G NL-clear cells.

## 2. Checks run and outcomes

| # | Check | What I did | Evidence | Survives? |
|---|---|---|---|---|
| 1 | Train/test/ext disjointness, domain | `c6.py` on all 36 cached datasets: exact-duplicate parameters train-test and train-ext, min distance, test inside [0,1]^p, ext outside the box, NaN | 0 duplicates, 0 NaN, test always inside the box, ext always outside; (p = 32 test points are >= 1.1 from the nearest train point) | Yes |
| 2 | POD / scaler / output standardisation fit on training only | Code read (`methods.py` POD, PodPoly scaler, PodMLP/MLPDirect/Bottleneck scalers; `hpo.py`; `experiment.py`; pilot features use `perm[:32]` of the training pool) | All fitted inside `fit()` on the rows passed in; validation indices come from the N training rows; test only logged; refit uses the N rows | Yes |
| 3 | Selection used only validation error | Recomputed argmin(val) over trials for all 2,700 records (v1, A, A2, A3) | 0 mismatches between `best_cfg`/`val_best` and argmin val; selected-trial test error equals the oracle-trial test error for the median record | Yes |
| 4 | Identical error metric for all methods | `rel_l2` is the only metric; all methods go through `run_method`; stored per-sample arrays reproduce the JSON mean (`c7.py`); Exp B/F/D/E/G also use `rel_l2` on the same 1000-point test set | e.g. bratu_L1 s0: JSON 1.6529571e-4 vs npz mean 1.6529571e-4; 1000 interp and 500 ext samples for every method | Yes |
| 5 | Failed fits dropped or replaced | Scanned all trials/records in raw, expA, expA2, expA3, expD, expE, expG (`c1.py`); complete seeds per instance; records per job | 0 non-finite val/test in 25,000+ trials; every job has all seeds 0-2 and the full N x method grid (30/15/6/3 records); `A.load` drops no seed | Yes (note m-5: bad-but-finite GP fits are kept) |
| 6 | Reproduce headline tables | Recomputed Table 1, Table 2 (all N), 13/8/3, 5/14/5, Exp B 15/48 and its crosstab (LS->NL 2, LS->tie 4, tie->NL 9, none toward LS), Exp F (5/7, 0.47, 2.51 -> 2.04, 6.8e-4 -> 2.0e-4), Exp D (52 cells, 14.28x, 13%), Exp E (28 cells, 1.92x, 8.12x), Exp G (0.95x), even/odd halves (83%, 98.7%, r 0.988), seed consistency (86.5% / 95.5%), the 17-of-24 and 12 counts, pooled LOFO 1.07 -> 0.62 | All reproduce exactly | Yes |
| 7 | Pre-registered selection rules applied as written | Git log of first-commit dates of protocols, frozen rules, selection files, analysis functions and raw result directories; recomputed the Exp A2 qualifying set, Exp F decisive set, Exp D/E/G "GP-clear" definition (`y_gp > 0.10`, oracle comparator) | Frozen rules, analysis code (`expA2`, `expE`: e64ff3a; `expF/G/A3`: c9a7b93) and addenda precede the raw results they govern; decisive set = the seven instances with y1024 >= 1 in v1+Exp A (bratu x2, nlheat x2, burgers_L1, darcy_L1, heat2d_L1) as stated; Exp F verdict function implements the addendum (ROBUST iff >= 5/7). Caveats: Stage-3 designs were chosen after seeing earlier results (disclosed); Exp F's 5/7 threshold was set after Exp B's partial results | Yes (with the knife-edge noted in M-2) |
| 8 | NN handicapped by implementation choices? | Code read of `_train`, `_nn_cf`, scaling; trial-level analysis of sampled configs (`c16.py`, `c4.py`); independent float64 + L-BFGS probe (`nn_cf.py`) | Output scaling and standardised loss are sound (global std; energy-weighted POD loss equals the field-space L2 loss); lr in [1e-3, 1e-2] and wd in [1e-8, 1e-4] range have only a 0.4-decade effect; the floor is optimisation-limited (train loss ~ test error, flat learning curve 128-512 then a drop when steps double); a stronger optimiser gains 0.6-1.0 decade but not 2+ | Claim (1) survives; magnitude reduced (M-2) |
| 9 | Alternative family definitions | `c5.py`: GP only, {GP, poly} vs all NNs, no-GP LS, pod_mlp vs direct | GP vs NN picture stable at N=1024 (13/2-3/8-9); NL-clear count at N=32 4-9 depending on definition; without GP the "LS family" loses 17 of 24 instances at N=1024 | Yes with m-1 |
| 10 | Does POD truncation drive the NL wins? | POD projection floors; Exp G in NL-clear cells; new `gp_full` runs on A3 instances | See C-1 | **No** (claim 3) |
| 11 | Is KRR control a fair test of "ML-II"? | New LOO-tuned KRR with matched and widened ridge range | See M-1 | **No** (claim 2 wording) |
| 12 | Isotropy vs anisotropy | Exp E cell-level ratios, burgers_L1/darcy_L1 probes | 8/28 cells > 3x; burgers_L1 45x; darcy_L1 not separable by my probe | Partially |
| 13 | Interpolation vs extrapolation consistency | `c8.py` y_ext with the same validation-selected members | See M-2 | LS sign yes, magnitude no |
| 14 | Step-count discontinuity at N=1024 | `c15.py` | See M-3 | Headline counts partly artefact |
| 15 | Seed / draw dependence | Single-seed class counts, pairwise agreement, per-instance seed ranges, even/odd and non-default halves (`c13.py`, `c19.py`) | Agreement 72%; even/odd 83%, 79% (non-default halves 1-3 vs 4-7), signs 99-100% | Claim (4) yes |
| 16 | Pilot diagnostic sensitivity | Spearman by N, by feature, partial given p, family-level, p-restricted (`c14.py`, `c18.py`) | See m-6 | Claim (5) yes |
| 17 | GP optimiser failures | Non-monotone GP learning curves, per-seed spikes (`c22.py`) | One instance (burgers_L1), 2 of 432 seed-cells | Yes (m-5) |
| 18 | Leakage via shared pool / seeds | Seeds share pool and test set; nested subsets overlap (declared); config draws shared across instances (earlier audit F2/F03) | Not re-derived; consistent with `c13.py` per-seed best-trial table (each seed's 7 configs apply to all 24 instances) | Declared limitation |

## 3. Least safe central claims, in order

1. **Claim (3)**, in its present form ("moving features / some high-p favour NNs"): contradicted by the authors' own Exp G in the NL-clear cells and by two new full-field GP runs; what survives is "NNs beat POD-based surrogates truncated at r <= 32 on moving features, and beat all GP variants on travelling fronts and p = 10 Darcy at N=1024".
2. **Claim (2)**, the causal word "marginal likelihood": a LOO-tuned kernel ridge regressor with a widened ridge range beats POD+GP on the smoothest cells; the KRR control's search box excluded the optimum; anisotropy matters in 8/28 cells.
3. **Claim (1), magnitude**: the sign is safe; "up to three decades" is an upper value tied to float32/1500-epoch Adam/N=1024/interpolation.
4. Claim (4) is safe (and understated). Claim (5) is safe and appropriately hedged.

## 4. Concrete fixes (ordered by value for effort)

1. Report Exp G in all cells and add the two A3 instances (+ darcylin) and N in {32, 128, 512} to Exp G (full-field GP, a few minutes per instance). Add `gp_full` (or POD+GP with r up to 128) to the LS side, or rename the family "POD-based" and rewrite claim (3) and the abstract ("neural family in 8" -> state the 4 remaining travelling-front/p=10 instances).
2. Add one exploratory arm: KRR tuned by closed-form LOO (as in `krr_cf2.py`) over a widened ridge range, with per-mode and ARD variants; report where the optimum ridge lies relative to the Exp D box (<= 1e-14 N in the smooth cells). Reword "due to marginal-likelihood fitting" to "due to wide-range, criterion-driven fitting of the kernel regressor's hyper-parameters (ML-II or LOO), with anisotropy needed in moderate-margin cases".
3. Qualify the headline number: "up to 3.3 decades (N=1024, interpolation, 1500-epoch float32 Adam); about 2.1-2.7 with float64 + L-BFGS; 0.7-1.9 on the extrapolation set" and show the extrapolation table.
4. Remove the N=1024 step discontinuity from the headline (report N=512 as co-primary, or refit the N=1024 nets full-batch with 1500 steps on stored configs).
5. Put instance-level seed CIs and a "robustly clear" subset (all seeds beyond the band) next to Table 1; restate the high-p claim as unresolved.
6. Report the Exp F verdict for both N (ROBUST at 1024 only; PARTIAL at 256) and the oracle caveat in the abstract-level summary.
7. Mention the GP optimiser instability (burgers_L1) and consider `n_restarts_optimizer >= 2`; correct the Methods text on batch/steps at N=1024.
8. Treat A2 Q1's p-value as a family-level descriptive count, and label D/E/G numbers "oracle, n cells".

## 5. Limits of this review

The NN and KRR probes are single-seed (seed 0), hand-chosen and untuned; they test whether the headline is an artefact, not what the best achievable NN or KRR is. The `gp_full` runs on the A3 instances used one seed and one N. The extrapolation comparison inherits the heavy-tailed mean error on near-resonant helm_L2 draws. I did not re-solve the FOMs, re-derive the confirmatory p-values, or audit the literature; earlier audits (agent3/4, agent5, agent9) cover those, and I did not find reasons to dispute their verified items.
