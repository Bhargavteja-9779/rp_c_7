# Experimental protocol v1.0 (pre-registered — committed to git BEFORE any comparative result existed)

Machine-readable settings: `code/configs/protocol.json`. Code: `code/`. Entry: `python run_all.py --mode full`.

## 1. Problem suite (16 instances = 8 PDE families × 2 difficulty levels)
darcy (p=4/10), advdiff (p=4, ε ranges), transport (p=4, pulse width), burgers (p=4, viscosity), fisher (p=4, horizon T), heat2d (p=4, source width/diffusivity), bratu (p=3, λ range), wave (p=4, pulse width). Definitions: `code/src/surrogate_bench/problems.py`. Each is solved by a verified numpy/scipy FOM (tests: exact Poisson series, exact translation, d'Alembert, grid-refinement, Burgers self-convergence, Fisher front speed). Output m ∈ {128, 256}. **All data are synthetic simulations of known PDEs; none are real-world observations.** A separate DEV problem (1-D heat) was used for all debugging and design.

## 2. Data
Per instance: pool of 4096 i.i.d. U[0,1]^p training parameters, 1000 i.i.d. interpolation-test parameters, 500 extrapolation-test parameters (uniform on [−0.25,1.25]^p, rejected if inside [0,1]^p). Draw streams are seeded from the instance name only. Seed s uses the first N elements of permutation `default_rng(1000+s)` of the pool, N ∈ {32,64,128,256,512,1024} (nested).

## 3. Methods (all in `methods.py`)
LS: pod_gp (POD + ARD-GP, Matérn-5/2 or RBF), pod_poly (POD + total-degree polynomial ridge), pod_mlp (POD + MLP). NL: mlp_direct (μ→field), bottleneck (μ→k-dim latent→field). Intrusive POD-Galerkin is **not** included (needs operator access; limitation).

## 4. Matched tuning
Every method receives exactly B=8 random-search trials (trial 0 = fixed default; trials 1–7 sampled from method-specific spaces defined in `methods.py`), evaluated on an 80/20 split of the N samples; the config with the lowest **validation** error is refit on all N. NN: Adam, cosine LR, 1500 epochs, float32, 1 thread, batch = N (N ≤ 512) else 512. Test error of every trial's (80%-trained) model is logged for H4 but **never used for selection**.

## 5. Outcomes
err = mean over test points of ‖û−u‖₂/‖u‖₂. Family winner chosen by validation: LS* = argmin_{LS} val_best, NL* likewise. y = log10(err(NL*)/err(LS*)) (y>0: LS better). ȳ(i,N) = mean over seeds.

## 6. Pilot diagnostics (`diagnostics.py`)
From the first n0=32 training snapshots only: f1 = log10 of mean leave-one-out POD reconstruction error with r=4 modes; f2 = slope of log10 σ_k vs k (k=1..10; floor 1e-12·σ_1). Secondary: r=8 error, r_tol (smallest r with LOO error ≤ 1e-2).

## 7. Analyses (frozen) — see hypotheses.md
H2 details: rows = (instance, N∈{64,…,1024}); seed-averaged cells. Models fitted by ridge (λ = 1e-3 × n_rows on standardised predictors) with leave-one-family-out (8 folds, both levels of a family held out together): M_spec: y ~ log2N + f1 + f2; B0: y ~ log2N; B1: y ~ log2N + p. Cluster bootstrap resamples the 8 families with replacement (10,000 draws). Also report sign-accuracy of ŷ vs majority-class.
H4a details: trial-level (80%-trained) errors; err_b(m) = test error of the best-by-validation config among trials 0..b−1; condition SYM: both families b=8; ASYM: NL b=8, LS b=1. NL-win = ȳ<0 per (instance, N) cell, N ∈ all 6 levels.
Exploratory (labelled): H3; feature ablations; pilot-size sensitivity n0 ∈ {16,24,32,48,64}; learning-curve exponents; per-method win tables; oracle-vs-validation selection regret; cost analysis (measured FOM s/solve, fit time, HPO time, inference time; break-even N* = (N·t_FOM + t_HPO+t_fit)/(t_FOM − t_inf) under stylised FOM-cost multipliers {1,10,100,1000}× — a *model*, not a measurement).

## 8. Stopping / data-handling rules
* Seeds 0–2 are mandatory; seeds 3–4 are added **only** as complete batches (all 16 instances) if compute time allows, decided by wall-clock, not by results. Analysis uses all completed complete batches.
* No instance, method, N, or seed is excluded after the fact. A diverged config counts as err=+∞ for selection. If a FOM solve fails the run aborts and the solver is fixed *before* rerunning everything.
* No change to methods/search spaces/analysis after the first full-run result is seen. Any later change is a recorded *deviation* in `research_design/deviations.md` and affected results are labelled exploratory.

## 9. What was seen before registration (honest disclosure)
(a) DEV-problem results during debugging. (b) A one-off timing benchmark on heat2d_L2 printed default-config test errors for five methods at N=64 and N=1024 (E=1000/1500 epochs); epochs were retained at 1500 for fairness to NNs; only timing informed design. (c) Quick-mode run on darcy_L1 and burgers_L1 (N=32,64, B=2, 40 epochs): structure/finite-ness inspected, one darcy_L1 error value (pod_gp, N=32) was seen. (d) The slope feature was given a noise floor after a unit test on synthetic data, before any real-data result.

## 10. Known limitations declared in advance
16 instances from 8 hand-chosen families are not a random sample of PDEs — inference is about this suite; generalisation is argued, not tested. Low-dimensional parameter spaces (p ≤ 10). FOM costs are milliseconds, so cost break-even is stylised. CPU-only, small networks, no operator-input (field-valued) architectures such as FNO. Hyper-parameter spaces are mine; other reasonable spaces may change absolute numbers.

## 11. Pre-registration evidence (commit hashes; git tags could not be pushed to the remote)
* Protocol, hypotheses, problem suite, methods, tests: commit `17a503c60783fb1661c7b1b58f7dc9362d029569` (local tag `prereg-v1.0`).
* Analysis code, statistics unit tests, figure code: commit `16c9ae95164053f4592cd6d3e2e4d20f7951746b` (local tag `prereg-v1.0-analysis`).
* Both precede every file in `results/raw/`. Remote history: branch `claude/happy-bell-9xorxs`.
* Operational note: the first launch of the full run (BLAS thread oversubscription) was killed before any job finished and relaunched with identical protocol and code; no results were discarded.
