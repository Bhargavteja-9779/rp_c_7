# Round 3: independent reproduction and final rejection attempt

Reviewer: fresh-context AI agent (not a human). Everything below was run in a fresh clone,
`/tmp/claude-0/-home-user-rp-c-7/d247ddca-2eb6-5163-bca0-57b556b9e2f0/scratchpad/fresh/rp` (HEAD 351c0cc, branch claude/happy-bell-9xorxs).
The original repository was not modified except for writing this file. Scratch scripts and logs are in
`.../scratchpad/repro/` (`repro.py`, `recompute*.py`, `out_*.json`, `log_*.txt`). The earlier round-1/2 files were read only after the
analyses below were done.

Environment: Python 3.13.16, numpy 2.5.3, scipy 1.18.1, pandas 3.0.5, torch 2.14.1+cpu, scikit-learn 1.9.1, matplotlib 3.11.2, pytest 9.1.1, 4 cores. All were already installed. The versions are identical to those in `results/raw_exp*/environment.json`. Nothing was installed.

---------------------------------------------------------------------------------------------------

## PART A. Independent reproduction

### A1. Unit tests
`cd Reinforced_Research_Project/code && python3 -m pytest tests -q`
Result: **50 passed, 0 failed**, 39 warnings (sklearn lbfgs ConvergenceWarning), 32 s.
Note: `code/README.md` still says "27 tests", "16 instances" and `Final_Manuscript.*`, and points to `review/final_audit.md`. It is stale (v1 text).
The repo also carries a legacy v1 tree at the top level (`/code`, `/results/raw`, `/manuscript/Final_Manuscript.*`) beside `Reinforced_Research_Project/`.
The 16 original instances' raw JSON live only in the legacy `/results/raw` (97 files).
The v4 builder and the audit scripts read it through `ROOT.parent/results/raw`, so this works, but it is easy to miss.

### A2. Regeneration of data and re-run (no data_cache; fresh cache dir)
Method (`repro.py`): build the instance dataset from code with `build_dataset` (4 workers), then for seed 0 and N in {32, 256} and all five methods:
(a) re-run the full `run_method` (8-trial random search plus refit);
(b) "replay": refit the stored `best_cfg` with the stored seed convention (seed*100+99).
Both are compared with the stored raw job JSON. One thread per process, float32 networks, 1500 epochs.

| Instance (stored in) | Re-run of the full search (HPO+refit) | Replay of stored best config |
|---|---|---|
| **kdv_L1** (Exp A, v2 code with a stable crc32 seed): 10 records (N=32, 256 x 5 methods, including pod_gp, pod_poly, pod_mlp, mlp_direct, bottleneck) | **bit-identical** test errors (relative difference 0.0 for all 10), identical trial configs and validation errors | bit-identical (0.0) |
| **darcy_L1** (v1 `/results/raw`): 10 records | **does not match**: only 1/10 best configs equal, trial configs differ; relative difference up to 0.76 (e.g. N=256 pod_gp 7.50e-4 stored vs 1.81e-4 re-run; mlp_direct 5.9e-3 vs 3.3e-3) | **bit-identical** (0.0) |
| **bratu_L1** (v1): 10 records | **does not match**: 0/10 best configs equal; relative difference up to 0.59 (N=32 mlp_direct 4.5e-3 vs 1.8e-3); pod_gp N=32 and N=256 happen to agree to 1e-7 and 4e-4 | **bit-identical** (0.0) |

Readings:
* pod_gp, pod_poly and the float32 CPU networks reproduce to full double precision on this hardware and these software versions, **given the stored configuration**. For the v2 experiments the whole pipeline reproduces from scratch.
* **The 16 original (v1) instances, which are two thirds of the "24 main problems" and of the 13/3/8 headline, cannot be regenerated from scratch.**
  The v1 run sampled its random-search trials with a process-salted `hash()` (fixed afterwards, commit 3268f47).
  A fresh run draws different configs, and in the examples above the per-record test errors change by up to 4x for pod_gp (darcy_L1 N=256) and up to 2.4x for a network (bratu_L1 N=32).
  Only the stored-config replay is reproducible. This is stated in `code/README.md` and in the legacy `deviations.md` (D5). **It is stated nowhere in Final_Manuscript_v4.md or the Supplement.** It is also a free demonstration of how much a single "draw" matters.
* What cannot be reproduced and why: (i) v1 HPO draws (salted hash, above). (ii) Bit-identical network results on other CPUs/BLAS builds are not guaranteed, because float32 and thread/BLAS reduction order matter (README says so). Here the CPU model is not recorded; the platform strings differ only in the kernel build. (iii) The timing columns (fit seconds) are machine- and load-dependent. (iv) `data_cache` is gitignored; datasets regenerate deterministically (seeded by instance name), kdv_L1 took ~86 s with 4 workers.
Not re-run: the other experiments' (B, D to H) training jobs. The recompute in A4 uses the stored raw JSON.

### A3. Manuscript rebuild
`cd Reinforced_Research_Project/manuscript && python3 -I build_v4.py --no-render`
Output: `words: 5787 refs: 15`. No missing-file error: the builder needs only committed files (`results/expA_primary/tables/*.csv`, `results/*.json`, `research_design/frozen_rules_from_v1.json`, `literature_review/references_verified.csv`, `literature/updated_literature_matrix.csv`).
It needs `code/src` and `../manuscript/unimath.py`, both in git.
It does **not** read the raw job JSON. It reads derived CSV tables, so the table-to-raw link is only as good as the analysis step that produced the CSVs (A4 covers this).
Diff against the committed `Final_Manuscript_v4.md`: **identical after normalising the absolute path prefix**. The rebuilt file embeds `/tmp/.../fresh/rp/...` in the figure links, and the committed one embeds `/home/user/rp_c_7/...`.
Consequence: the committed `.md` hard-codes an absolute sandbox path for every figure (`/home/user/rp_c_7/Reinforced_Research_Project/figures/...`). It will not render figures on any other machine. The builder also rewrites `fig_mech4.png` in the repo, and `git status` after a rebuild shows only the `.md` modified (the PNG was byte-identical).

### A4. Recompute from the raw job JSON only (own code; no `surrogate_bench` import and no summary CSV/JSON)
Definition used (as in the text): per seed, the validation-selected member of each group (LS = pod_gp/pod_poly/pod_mlp, NL = mlp_direct/bottleneck); y = log10(err_NL/err_LS); seed mean; tie if |y| <= 0.10.

| Claim in manuscript | Claimed | Recomputed | OK |
|---|---|---|---|
| 24 main problems, N=1024: RB better / tie / NN better | 13 / 3 / 8 | 13 / 3 / 8 | yes |
| same, N=32 | 5 / 14 / 5 | 5 / 14 / 5 | yes |
| NN-win count with tie band 0.15 / 0.05 | 6 / 10 | 6 / 10 | yes |
| Test-selected (oracle) variant, N=1024 and N=32 (not claimed) | n/a | 13/3/8 and 5/15/4. The headline is **robust to test-set selection**. Taking a ratio of seed-mean errors instead gives 12/4/8 and 5/13/6 | n/a |
| Table 1 per-class counts (36 problems, 6 classes) | 3/1/5, 7/0/2, 2/1/1, 2/0/0, 3/0/1, 6/1/1 | identical (sum 23/3/10) | yes |
| Table 3 by number of inputs (36 problems) | 20/2/8; 1/0/0; 2/1/2 | identical | yes |
| Table 2 target 10% / 1% / 0.1%, RB vs NN, 36 problems | 36/36, 27/28, 19/10 | 36/36, 27/28, 19/10 | yes |
| same on 24 main / on the 28 without the A2 problems | 9 vs 4 / 11 vs 5 | 9 vs 4 / 11 vs 5 | yes |
| Largest NN margin; bratu_L1, nlheat_L1, burgers_L1 factors | 2.8; ~2000; 530; 180 | 2.75 (heatmv3_L1); 2043; 529; 177 | yes |
| A2 problems' factors | "about 10 to 850" | 9.9 to 849 | yes |
| Exp H, 28 GP-clear cells (cells with y_GP>0.1 over the best NN by test error; 24 inst x N in {64,256,1024} = 72 cells): narrow KRR / wide KRR B=8 / B=32 median ratio to GP | 13 / 6.5 / 2.7 | 13.4 / 6.48 / 2.68 (quartiles 4.3-151 / 3.6-14.8 / 1.9-4.4) | yes |
| share within 3x for B=32; wide KRR clearly beats best NN (B=8 / B=32) | 57%; 61% / 64% | 57%; 61% / 64% | yes |
| Narrow KRR over all 6 budgets: 52 cells, median 14.3 | 14.3 | 14.28 | yes |
| Poly: median ratio, clearly beats NN | ~10x; 23 of 52 | 9.9x; 23 of 52 | yes |
| Exp G (full-field GP) in the 28 cells | 0.95 median, all <=3x | 0.95 (0.64-1.14), 100% | yes |
| Exp G3: GP-full vs best NN at N=1024 on heatmv3_L1, incl3_L1 | 1.2 and 1.0 decades | 1.17 and 0.98 | yes |
| Exp F: decisive instances keeping >= 1 decade after float64+L-BFGS | 5 of 7 | **5 of 7** (bratu_L1 2.72, bratu_L2 2.55, burgers_L1 1.78, nlheat_L1 2.26, nlheat_L2 2.04; darcy_L1 0.63, heat2d_L1 0.95); NN floor 2.0e-4 | yes |
| Exp B: classification change under 4x epochs; ties to NN wins; fits improved | 15 of 48, always toward NN; 9; "nine in ten" | 15 of 48 (all toward NN); 9; 89.6% | yes |
| Seed consistency (all 3 seeds beyond band): NN-clear / RB-clear | 57% / 80% | 20/35 = 57% / 43/54 = 80% | yes |
| Config-draw halves: class agreement; sign agreement | 83%; 99% | 83.3% (144 cells); 98.7% (78 cells) | yes |
| Median fit seconds at N=1024 (GP / POD+NN / direct NNs / poly) | 44 / 86 / 116-139 / 0.3 | 44.0 / 86.2 / 115.7-138.7 / 0.3 | yes |
| Extrapolation example bratu_L1, nlheat_L1 | 3.3->1.5; 2.7->1.8 | 3.31->1.49; 2.72->1.84 | yes |
| P1 (pilot-statistic test on the 8 Exp A instances) | rho=-0.38, p=0.180 (exact permutation); sign flips without nlheat | -0.381, 0.180; +0.486 | yes |

**All 24 headline numbers I recomputed reproduce, with no discrepancy.** Differences between my numbers and the text are only in rounding.

Findings of my own that are not discrepancies but affect wording:
* "Where networks had beaten the POD-based GP, the full-field GP **often** beat the networks again" (4.3). Recomputed over the 24 main problems (best NN by test error): the cells where a network beat POD+GP by more than 0.1 decade are 13 (N=64), 8 (N=256) and 9 (N=1024). The full-field GP then beat the network by more than 0.1 decade in 2, 2 and 3 of them, tied in 4, 1 and 1, and lost in 7, 5 and 5.
  At N=1024 the reversals are heat2d_L2, incl_L1 and incl_L2 (3 of 9). The networks stay clearly ahead of the full-field GP on kdv_L1, fisher_L2, transport_L2, darcy_L2 and darcyhd_L1. "Often" should read "in 3 of 9 cases at N=1024 (the narrow-source and inclusion problems), and in 7 of 30 cells across budgets".
* The Table 3 / checklist item 1 count "20 of 30" for p <= 4 contains the 7 p <= 4 problems of the A2 set, which the authors designed because they expected the GP to win (all 7 are RB-clear). Without them it is **13 / 2 / 8 of 23** (57% vs 35%).
  Round 2 flagged this split for the abstract (19 vs 10) and Section 4.2, but not for Table 3 / checklist item 1. The text there is silent on it.
* Problem-level counts are not independent samples. A family-cluster bootstrap (19 families, 5,000 draws, my own code) gives a 95% CI for the RB-clear share at N=1024 of [0.47, 0.79] (point 0.64), and for "RB minus NN share reaching 0.1%" of 0.25 with CI [0.14, 0.36]. The headline direction survives on exploratory terms. The family-level tally at N=1024 (median per family) is 12 RB-clear / 4 tie / 3 NN-clear across 19 families.
* A reference check by web fetch: arXiv 2604.00689 exists, and the title matches. It has **four** authors (Westermann, Huber, O'Leary-Roseberry, **Zech**). Reference [15] omits Zech and has no "et al.", so it is an incomplete citation. The arXiv abstract's conclusion ("polynomial surrogates more data-efficient for smooth inputs; FNO fastest for rough inputs") is very close to this paper's finding and should be discussed as the nearest prior result, not only as "no universally superior method".
  The arXiv 2006.13706 title/authors match. I could not confirm "a Gaussian process was reported to have several advantages over a neural network" from the abstract page alone.

### A5. Pre-registration chronology (git history, own check)
For every `raw_exp*` directory I compared the first commit containing its results with the commit holding its protocol/prediction (addenda, configs). I also checked that the addendum files were not edited after results, and I cross-checked `job_seconds` against the interval between the pre-registration commit and the first-results commit.

| Experiment | Protocol/prediction commit (UTC) | First commit of results | Order |
|---|---|---|---|
| v1 (16 inst) | 17a503c 2026-10-20 17:46 (+ analysis 16c9ae9 10-21 01:39) | c5c8535 10-21 02:32 | prereg first |
| A, D, B | bcf7f30 10-21 20:51 | 2d0e2d4 10-22 06:11 / 2abe263 07:50 / 72cb02c 07:55 | OK |
| A2, E | 72cb02c 10-22 07:55 (selection json, configs) | 0bcb608 09:25 / 703ad59 10:18 | OK |
| A3, G, F | c9a7b93 10-22 08:46 (addendum v2.2; also amended the A2 p0 before A2 ran; Exp B partial outputs were still being committed at 08:47, so chain 2 had not begun) | 82dbbe2 10:26 / 39b1b7f 12:26 | OK |
| H8, H32 | 48a0698 13:18:03 + code cc7a78f 13:18:35 | 84f2a21 13:22:55 | OK. The H8 and H32 logs show 111 s and 336 s of elapsed time at the last interim job, so the runs fit inside the 4m20s window |
| G3 | 4cd411a 13:32:23 (edit of addendum v2.3) | b37dd4e 13:35:08 (partial: 3 of 12 jobs; first jobs finish 81-114 s after start) | OK, tight (2m45s) but consistent with the logs |

**No experiment's protocol or prediction was committed after its results.** I found no post-hoc edit of any addendum except the intentional v2.3a addition (4cd411a).
Caveats, none of them violations:
(1) Exp H and Exp G3 were *designed after* the corresponding negative or unexpected results were seen. H was motivated by an AI review of the draft, and G3's prediction follows from Exp G's results and a reviewer's single-seed probe. They are pre-registered in prediction only, as the addendum says.
(2) A2 and A3 instances were authored after seeing which problems the GP won.
(3) Git timestamps, author and committer are all the same AI session, and author-set dates are trivially forgeable. This is not an independent registry, and the paper says so.
(4) The v1 pre-registration is for the original hypotheses; the paper builds its story on the v2 stages.

---------------------------------------------------------------------------------------------------

## PART B. Final rejection attempt

### B1. The strongest case for rejection

**1. The headline is a statement about a weak neural-network recipe on author-built toy problems.**
* The networks are plain MLPs, trained with Adam for 1,500 full-batch epochs (3,000 minibatch steps at N=1024) in float32. Their tuning is 8 random draws, and **the draws are shared across every instance and every N** (7 non-default configs per method per seed, i.e. 21 distinct configs per method in the whole study). The GP gets marginal-likelihood optimisation and ARD.
* No per-mode output scaling, no ensembles, no Fourier or operator-type architectures, and no learning-rate search beyond 10^-3 to 10^-2 are tried.
* The authors' own repair attempts (4x epochs; float64 + L-BFGS) lower the NN error by 0.5 to 0.6 decade and then plateau at the same ~2e-4 on four different problems (2.04e-4, 2.01e-4, 2.51e-4, 2.44e-4). A floor shared across problems points to a shared artefact of the recipe, not a property of the problems.
* The logged train losses give no sign of a generalisation gap: for bratu_L1 pod_mlp the L-BFGS-polished normalised train MSE of 3.7e-8 over 16 coefficients bounds the field error by roughly 8e-4, against a test error of 2.8e-4. This is *consistent with* the networks being optimisation-limited, not data-limited. The paper does not report train-versus-test error, so it cannot rule this out; it says "we do not know why the networks plateau there".
* The paper cites McGreivy & Hakim (weak baselines) and then produces a comparison with the same weakness, only labelled as such.
* A sample-efficiency verdict of "GP beats NN by 3 orders" on 3-4 input smooth problems is the textbook expected result (GP/kernel interpolation in low dimension) and is not news. The authors say so ("confirm earlier reports").

**2. The "application" framing is not supported by the authors' own data.**
* The problems are 1-D/2-D toy PDEs, solved on 128-256-point outputs with in-house solvers.
  The recorded `fom_seconds_per_solve` in the raw JSON has median **6 ms** (range 0.4 ms to 136 ms; 1,024 solves take a median of 6 s).
  The median GP tune-and-fit time at N=1024 is **44 s**, and the networks take 86-139 s.
  For **27 of 36 problems (75%) GP tune-and-fit takes longer than the 1,024 simulation runs it learns from** (median ratio 6.5, max 104).
  For **23 of 36, generating the entire 4,096-point pool is cheaper than one GP fit at N=1024.**
  On this benchmark a surrogate is not economically justified, so the question "which stand-in for slow physics simulations?" has no cost-benefit support here.
* Section 4.2 nonetheless states that "training time is a minor cost compared with the simulations themselves". The data behind that sentence say the opposite for these problems. The next sentence ("we did not ... compare with the cost of the simulations themselves") half-concedes the gap, but the first sentence is an unsupported assertion that a reader will take as a result.
  Earlier rounds listed "no total-cost accounting" as a limitation. They did not notice that the recorded solver times contradict the sentence in the paper.
* The six "application classes" are relabellings: porous-medium Darcy with a log-normal field, a Bratu equation called "thermal runaway (combustion-type)", Burgers/KdV/Helmholtz/wave grouped as "waves, shocks and acoustics", and 1-D diffusion filed under heat conduction. "Nothing here was calibrated to a real application, and no field or industrial data were used" is disclosed, but title, abstract opening, Table 1 and the "worked examples for a practitioner" still invite the reading that the findings transfer.
* The checklist ("Start with a Gaussian-process ... model") then gives action advice from this one synthetic suite.

**3. The evidence base is a convenience set whose composition drives the headline.**
* 36 problems from 19 authored families. L1/L2 pairs are near-duplicates. 8 problems (A2) were added *because* the authors expected the GP to win, and all 8 do (factors 10-850). 4 more (A3) were authored as probes.
* The abstract's 19-vs-10 and Table 3's 20 of 30 depend on those; without the 8 it is 11 vs 5 (disclosed in the abstract), and for p <= 4 it is 13/2/8 of 23 (not disclosed).
* Counts have no sampling interpretation. There is no population of "physics problems" that these were drawn from, and the 0.10-decade tie band is a convention, not a test. The three seeds are not independent either, because the search draws are shared.
* Choices that the authors set and could have moved include parameter ranges, grids, noise-free data, `K_OPT = 4` modes with ML-II and the 4th kernel reused for the remaining modes, and a maximum of 300 points for hyper-parameter fits. No sensitivity analysis is reported for them.

**4. Mechanism claims are interpretations after the fact, built on test-selected comparators.**
* "Largely how the settings are searched" rests on a kernel-ridge control that had to be redone after a review showed the first one was structurally handicapped. The final result is 6.5x at equal trials and 2.7x at 4x more trials. That is a MIXED pre-registered verdict (57% within 3x), and the authors' conclusion is "largely".
* An equally good reading is that kernel regressors have the right inductive bias for smooth low-dimensional maps and a 1,500-step Adam MLP does not: the wide KRR still beats the best NN in only 61-64% of the GP's clear-win cells.
* Cells for Exps D, E, G, H and the B/F class changes use the *best-by-test-error* network and cells *selected by a test-error gap*. Disclosed (4.3, 4.5), and conservative for NN losses, but the 28-cell selection conditions on the GP's own test error, so GP error is biased low in those cells and every "ratio to GP" is biased up. The size of this is unquantified.
* "Equal numbers of trials do not mean equal effort", and the GP's ML-II optimiser cost is not matched.

**5. The "pre-registration" and "audit" language overstates independence.**
* All commits, the pre-registration, the analyses, the audits and every review round were made by AI agents of one model family. Commit dates are author-controlled. There is no independent registry, no human reviewer and no external replication.
* The manuscript itself says "The authors must verify every number, citation and claim and take responsibility for the text". That is an instruction left in the text, and the author fields are placeholders ("[AUTHOR NAMES ... to be supplied]"). At the moment no accountable human is named.
* Correlated blind spots are likely, since the reviewers share training with the writer. (This report is the same.) For example, no earlier round noticed that recorded solver times contradict the cost sentence.

**6. Novelty and positioning.**
* GP-versus-NN and kernel-versus-NN surrogate comparisons exist (Batlle 2024, Bērziņš 2020, Westermann 2026 with a near-identical conclusion; Guo-Hesthaven, Hesthaven-Ubbiali).
* No new method, no real or public benchmark (no PDEBench), no operator-learning baseline (FNO/DeepONet, which the introduction cites as the competition), and no theory. Three of four pre-registered hypotheses and the pilot-diagnostic test failed.
* The contribution is an engineering checklist that is partly negative. That fits a benchmark/methodology venue, and the paper's own earlier journal analysis reached the same conclusion.

**7. Reproducibility and housekeeping.**
* The original 16 instances (two thirds of the headline) cannot be regenerated from scratch (A2). Changing the HPO draw moved individual errors by up to 4x. This is not mentioned in the manuscript or Supplement.
* Figures are linked by absolute sandbox paths. `code/README.md` is stale (27 tests, v1 file names). A legacy v1 tree sits beside the v2 project. There is no archive/DOI. The builder never touches raw JSON.
* Reference [15] drops an author. "Often" in 4.3 is overstated (3 of 9).

### B2. Status of each objection

| # | Objection | Does the manuscript answer it? | Severity | Minimal fix |
|---|---|---|---|---|
| 1a | Weak/lightly tuned NN baseline; sample-efficiency claims | **Partly.** Disclosed in the abstract, Sections 2, 4.5 and 7, and Exps B/F partly probe it. The abstract's headline still reads as an architecture verdict. Optimisation-limited training is not excluded. | Serious, **not fatal** if scoped | Report train vs test error for the stored best networks and for the Exp F refits (data already exist). If train error is about equal to test error, say explicitly that the NN floor is optimisation-limited. Add one stronger-NN arm for 3-4 problems (per-mode output scaling, one ensemble, 20k Adam steps) or reword the abstract to "lightly tuned 1,500-step MLPs" at every mention of NN performance. |
| 1b | Floor of ~2e-4 shared across problems | **No** ("we do not know why") | Moderate | Same train-vs-test diagnostic. |
| 2a | "Slow simulation" framing vs 6 ms solvers; cost sentence | **No**; contradicted. The cost limitation is disclosed, the false-sounding sentence is not. | **Fatal for the application framing as written; trivially fixable** | Delete "Training time is a minor cost compared with the simulations themselves" and replace with the measured fact (median solve 6 ms; GP fit 44 s; the surrogate would pay off only if a real solver costs more than roughly 10 s to 1 min per run). Add a "break-even solver cost" column or sentence per method (computable from existing JSON). Soften the title subtitle/abstract opening to "expensive simulations such as those a real application would have; our problems are cheap stand-ins". |
| 2b | Application-class relabelling, practitioner worked examples | **Largely**: "nothing was calibrated to a real application" appears in the abstract, intro and Section 3 | Moderate | Keep the disclosure; rename the Table 1 first column to the equation families (Darcy, Bratu, Burgers ...) with the application as a parenthetical; mark the worked examples "illustrative, on synthetic stand-ins" in the heading. |
| 3a | Convenience, author-selected problem set; counts without sampling meaning | **Partly.** Abstract gives 11 vs 5; Section 7 names the non-independence. | Serious, not fatal | Report family-level tallies next to problem counts (my values: 12/4/3 over 19 families; family-cluster CI [0.14, 0.36] for the 0.1% difference). Add the Table 3 / checklist item 1 split without the A2 problems (13/2/8 of 23). |
| 3b | Researcher degrees of freedom in solver/problem design and GP settings (K_OPT=4, 300-point fits) | **Partly** (frozen v1 problems and pre-registered stages; limitations list) | Moderate | One sentence listing the unexplored design choices; run the GP with K_OPT=8 on three problems as a sensitivity check. |
| 4a | Mechanism over-interpretation ("largely search") | **Largely answered.** Wording is hedged, the verdict is MIXED, "residual factor of 2-3 unexplained", and the test-selection note is explicit. | Minor to moderate | Quantify the selection bias: recompute the Exp H ratios using cells selected on *validation* y (or on seeds 0-1 and ratios on seed 2). Replace "largely" by "in part". |
| 4b | "Full-field GP often beat the networks again" | **Overstated** (3 of 9 cells at N=1024; 7 of 30 across budgets) | Minor | Give the counts. |
| 4c | Test-set selection in the headline? | **No dependence.** The 13/3/8 and 5/14/5 counts come from validation-selected members and are unchanged under test-oracle selection (13/3/8; 5/15/4). Mechanism/B/F sections use test-oracle NN, disclosed. | Not an issue for the headline | Add one sentence: "the 13/3/8 counts are the same when members are chosen by test error". |
| 5a | Independence of pre-registration and audits | **Answered by disclosure** (Sections 2 and 7, Declarations). My order check found no violation. | Inherent limitation | Add the sentence "git dates are author-controlled" next to the existing "own history" caveat. Ideally deposit the repo at a time-stamping archive (Zenodo, OSF) before submission. |
| 5b | No accountable human; placeholders; "authors must verify" left in the text | **Disclosed, not resolved** | **Fatal for submission as is** | A named human author must verify, sign and remove the instruction. Name affiliations, contributions, funding and competing interests. Mention AI involvement in one clause of the abstract or a cover note, because journals' AI policies expect it in the methods and declarations, not only in the final section. |
| 6 | Novelty; closest prior work (Westermann et al.) | **Partly.** The text concedes "confirm earlier reports", but Westermann's polynomial-vs-FNO conclusion is closer than the text lets on. | Moderate; venue-limiting | Fix reference [15] (add Zech; add arXiv version). Add two sentences contrasting directly with Westermann et al. State the target venue as methodology/benchmark; do not submit to a method-oriented journal. |
| 7a | v1 HPO draws not regenerable | **No** (README only) | Moderate | One sentence in the Section 7 "Who checked this"/Data availability: "the 16 original instances' tuning draws used a process-salted seed; results are reproducible by replaying stored configurations (`experiments/replay_check.py`), not by re-running the search; re-running changes individual errors by up to 4x". |
| 7b | Absolute figure paths; stale README; legacy tree; no DOI | **No** | Minor | Use relative image paths in `build_v4.py`; update `code/README.md`; archive; move legacy v1 to a subfolder or document it. |
| 7c | Table 1 caption is garbled (the log-ratio sentence repeats) | No | Cosmetic | Edit the caption. |

### B3. What survives
* Every number I could recompute from raw JSON reproduces (24 of 24 checked claims, including the 13/3/8, 5/14/5, 36/36 - 27/28 - 19/10, Exp H 6.5x/2.7x, Exp G3 1.17/0.98, Exp F 5 of 7, Exp B 15 of 48).
* The headline classification does not depend on test-set selection. The pre-registration chronology holds. The pilot-statistic failure is reported honestly. Over-claiming is mostly already hedged: the 2.8x NN maximum, the tie bands, "lightly tuned", 36 vs 28 split, the draw-sensitivity numbers.
* The honest, defensible claim is: *on these 36 cheap synthetic problems, with 1,500-step MLPs that were lightly tuned, GP/kernel stand-ins reach 0.1% error on roughly twice as many problems (family-level CI excludes zero), and the size and even the sign of NN-vs-GP differences move with training length, tuning effort and random draws.*

---------------------------------------------------------------------------------------------------

## FINAL VERDICT: **conditionally ready**

Ready for a methodology/benchmark-type venue, and not for a method-oriented journal, once the following are done:

**Must fix before submission (all are text/metadata changes; none needs new experiments):**
1. Resolve the cost framing (objection 2a): remove the "minor cost" sentence and report the measured solver-time to fit-time relation (6 ms vs 44 s; 75% of problems have GP fit > 1,024 solves). Re-scope the "slow simulations" language to "if your real solver is costly enough".
2. Name responsible human authors; remove the "authors must verify" instruction; state AI involvement in a clause of the abstract or cover note (5b).
3. Add the non-reproducibility of the v1 search draws (7a) and the Table 3 / checklist-1 split without the A2 problems (3a).
4. Fix reference [15], tone down "often" in 4.3, and fix figure paths and the stale README.

**Strongly recommended (cheap, using existing data):**
5. Train-versus-test error for the networks, to decide between "NN floor is optimisation-limited" and "sample-limited" (1a/1b).
6. Family-level tallies and cluster CIs next to the problem counts (3a).
7. A selection-bias check on the Exp H ratios (4a).

**Why not "ready":** items 1 and 2 are ones a referee would use to reject a submission as written. **Why not "not ready" or "fundamental redesign":** all headline numbers reproduce, nothing in the headline depends on the test set or on late-registered protocol, the main claims are already hedged, and the remaining defects are in framing and metadata, not in the experiments. The scientific ceiling is limited by the design (synthetic, cheap, lightly tuned networks, one problem suite), which no text edit fixes. The paper has to be sold as a carefully hedged benchmark-and-checklist report, which is what it mostly is.
