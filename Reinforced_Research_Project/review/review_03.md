SIMULATED REVIEW (AI agent, not an external reviewer)

# Review 03: independent reproduction and final rejection attempt

Object: branch claude/happy-bell-9xorxs, commit f275c3c, "Choosing a Fast Stand-In for a Slow Simulation: a Selection Tool and a 44-Problem Study" (paper/main.tex, paper/supplement.tex, SurroSelect, benchmark code, results).
Reviewer stance: hostile final-round referee plus reproducibility auditor. Reviewed 2026-11-05.
Method: everything in Part A was done in a fresh clone at `/tmp/claude-0/-home-user-rp-c-7/d247ddca-2eb6-5163-bca0-57b556b9e2f0/scratchpad/clone/rp`. Nothing in `/home/user/rp_c_7` was modified except this report. I formed my own view first (paper text, code, raw JSON, git history) and read review_01.md and review_02.md afterwards. My scripts are in `.../scratchpad/work/` (`recompute.py`, `recompute_real.py`, `repro_tool.py`, `repro_real.py`, `repro_nn.py`, `real_fixed.py`, `gpfull_dbg.py`).

Limits of this audit. (a) The environment here has the same Python and package versions as the original runs (Python 3.13.16, numpy 2.5.3, scipy 1.18.1, scikit-learn 1.9.1, torch 2.14.1+cpu; compare `results/raw_exp6T/environment.json`), so bit-identical agreement shows determinism in one environment, not portability. (b) I did not re-run the 36-problem benchmark, the legacy five-method job grid (Experiment T), or the strong-network job grid; I re-ran one tuned-network job. (c) I cannot verify literature claims offline; the references I name in Part B are from my memory and must be checked by the authors.

---

# PART A. Reproduction

## A1. Packages

numpy 2.5.3, scipy 1.18.1, pandas 3.0.5, scikit-learn 1.9.1, torch 2.14.1+cpu, scikit-fem 12.0.2, optuna 5.0.0, matplotlib 3.11.2, pytest 9.1.1. All present, nothing installed. pdflatex and bibtex present.

## A2. Unit tests

| Suite | Result |
|---|---|
| `code/tests` (benchmark, solvers, leakage, statistics) | 56 passed, 0 failed (321 warnings, 56 s). Equals macro `\NBenchTests` = 56. |
| `surroselect/tests` | 9 passed, 0 failed (267 s). Equals macro `\NToolTests` = 9. |

Stale documentation: `code/README.md` still says "27 tests", points to `manuscript/Final_Manuscript.*`, `review/check_claims.py` and `review/final_audit.md`; the last two files do not exist.

## A3. Regenerating data and re-running the tool

Protocol: permutation = `default_rng(1000+seed).permutation(4096)[:N]`; data from `build_dataset`; `SurrogateSelector(cv=4, random_state=seed).fit(..., refit_all=True)`; test errors of every pool member on the 1000 test inputs.

| Problem | Source | N, seed | Compared with | Selected model | Test error of all 7 pool members | CV errors of all 7 |
|---|---|---|---|---|---|---|
| heatcomp_L1 (scikit-fem) | regenerated from code | 64, 0 | `results/raw_exp6C/heatcomp_L1__s0.json` | `gp_full[matern52]`, same; same tie set (4 models) | identical to the last digit (relative difference 0.0) | identical (0.0) |
| heatcomp_L1 | regenerated | 256, 1 | `raw_exp6C/heatcomp_L1__s1.json` | `pod_krr_wide`, same | identical (0.0) | identical (0.0) |
| kdv_L1 (own solver) | regenerated (105 s) | 256, 0 | `raw_expRetro/kdv_L1__s0.json` | `pod_gp[matern52,r=32]`, same | identical (0.0) | n/a (not stored) |
| heatcomp_L1, tuned network | regenerated | 256, 0 | `raw_exp6S/heatcomp_L1__s0.json` | n/a | test error 2.9923846601422987e-3, identical; same best Optuna parameters | n/a |

Tolerance: exact equality (double-precision identical) in this environment. The data are regenerated deterministically from problem names; the cache is gitignored and rebuilt on demand, as claimed. For heatcomp_L1 at N=64 the selected model (`gp_full[matern52]`, test error 0.01913) is 1.03 times the oracle (`pod_gp[matern52,r=32]`, 0.01861); that is within the paper's regret definition.

## A4. Real-data pipeline

Using `exp_real.load` and the `exp_real.job` logic without the strong network (`repro_real.py`):

| Dataset, seed, N | Selected | Max relative difference of 7 test errors | Forecast `predict_error(4N)` |
|---|---|---|---|
| ccpp, 0, 64 | `pod_poly`, same as `raw_expR` | 0.0 | identical |
| airfoil, 0, 64 | `pod_gp[matern52,r=32]`, same | 0.0 | identical |
| ccpp, 1, 256 | `pod_gp[rbf,r=32]`, same | 0.0 | identical |

Real-data pipeline reproduces exactly.

**New finding (tool defect, A4-1).** In the stored real-data results the full-field GP members have normalised RMSE of 20 to 74 (for example ccpp N=64: `gp_full` 72.6 against 0.27 for every other member; airfoil `gp_full` 21 to 30). The cause is a shape bug. For a scalar output `GPFull.predict` returns shape `(n,)` while `Y` is `(n,1)`; `nrmse` (and `rel_l2`) then broadcast `(n,1)-(n,)` to an `(n,n)` matrix. With the reshape fixed, the same model gives NRMSE 0.267 (`gpfull_dbg.py`). Consequences: (i) for any scalar-output data set the two full-field members receive a garbage cross-validation score and can never be selected, silently; (ii) review_01 minor m4 noted a "gp_full test error of 25, instability" on airfoil; it is this bug, not instability; (iii) I re-ran all six real-data cells x 3 seeds with the shape fixed (`real_fixed.py`): selections, regrets (R1 median 1.039), R2 (5 of 6), R4 (9 of 12) are unchanged, so no paper number changes. It is a latent defect in the released tool and the paper does not mention it.

## A5. Rebuilding the numbers

Ran `analyze_s6.py`, `analyze_real.py`, `analyze_retro.py`, `aggregate.py` in the clone and diffed.

* `analyze_s6.py` and `analyze_real.py`: no change to `results/s6` outputs (bootstrap RNGs are seeded). All Stage 6 and real-data macros regenerate identically.
* `analyze_retro.py` and `aggregate.py` change the committed files. This is a real inconsistency (A5-1):

| Macro | Committed | Regenerated from committed raw |
|---|---|---|
| `\RetroN` | 32 | 35 |
| `\RetroBetter` | 12 | 15 |
| `\RetroFlagged` | 2 | 4 |
| `\RetroWorst` | fisher_L1 (9.2), advdiff_L1 (1.7), helm_L1 (1.1) | fisher_L1 (9.2), advdiff_L1 (1.7), incl3_L1 (1.2) |

`results/raw_expRetro` has 35 files; `darcylin_L2` is missing (36 earlier problems exist). The committed summary and the committed PDF (Supplement S7: "On the 32 earlier problems...") were made from a mid-run snapshot, while the main text says "a descriptive run on the 36 earlier problems". Three different numbers (36, 35, 32) describe one run, and the run is incomplete. This is an artefact-consistency defect, not a scientific one. The diff is saved as `.../scratchpad/work/s6_regen.diff` and `macros_regenerated.tex`.

## A6. Paper build

`cd paper; bash build.sh --no-aggregate` (with committed macros):

```
main pages: 29   supplement pages: 9
main: overfull boxes: 1   undefined refs/citations: 0   multiply-defined labels: 0   LaTeX errors: 0
supplement: overfull boxes: 1   undefined refs/citations: 0   multiply-defined labels: 0   LaTeX errors: 0
macro leakage in text: 0
bibtex warnings: 6
cross-document name leaks: main 0 supplement 0
typed numbers not allow-listed: 0
```

The single overfull box in each file is 2.4 pt "while \output is active", cosmetic. The six bibtex warnings are "empty pages" in li2021, akiba2019, bouthillier2021, rosenfeld2020, marelli2014, paszke2019 (missing page fields). The rebuilt PDF text is identical to the committed `main.pdf` text (the committed PDF is built from the stale macros, A5-1). Review_02's cross-reference leaks and the cut-off supplement table are fixed. The typed-number lint passes using a 12-line allow-list, so it is a weak guarantee (it cannot see numbers in tables or captions that are hand-typed, and it cannot see text that is wrong but macro-derived).

## A7. Headline numbers recomputed from raw per-job JSON

Computed by my own script (`recompute.py`, `recompute_real.py`) from `results/raw_exp6C`, `raw_exp6T`, `raw_exp6S`, `raw_expR` only; no `results/s6` or macros used. Cells are problem x N with geometric means over seeds, as in the paper.

| Quantity | Paper | Recomputed | Match |
|---|---|---|---|
| 24-cell median regret vs oracle | 1.00 | 1.000 | yes |
| max regret | 1.18 | 1.181 (convdiff_L1, N=64); next 1.174 (lshape_L1, N=1024) | yes |
| cells within factor 2 | 24 of 24 | 24 of 24 (22 of 24 within 1.1) | yes |
| job-level (seed) | not reported | median 1.00, max 1.49, 4% of 72 jobs at 1.25 or worse; exact oracle hit in 56 of 72 | extra |
| always-best-fixed-member: name, median regret, share within 2 | `gp_full[rbf]`, 1.14, 75% | `gp_full[rbf]`, 1.14, 75% (18 of 24) | yes |
| tool/best fixed: median, better by >10%, worse by >10% | 0.91; 12; 2 | 0.915; 12; 2 | yes |
| random-pick null | 3.77; 38% | 3.77; 37.5% | yes |
| H1b: median ratio vs always POD+GP; better/worse | 0.85; 15/1 | 0.847; 15/1 | yes |
| H1c: median ratio vs benchmark selection; better/worse; worst | 1.01; 11/9; 2.2 | 1.009; 11/9; 2.19 | yes |
| H2: forecast within factor 2 | 37 of 48 | 37 of 48 | yes |
| H2 from N0=64; from N0=256 | 92%; 15 of 24 | 22 of 24; 15 of 24 | yes |
| too low / too high by >2x (all; N0=256) | 7 / 4; 7 under | 7 / 4; 7 under (all at N0=256) | yes |
| actual error inside the (low, high) band | 12% | 6 of 48 = 12.5% | yes |
| per problem within factor 2 (6 cases each) | not shown | 3,6,5,6,4,5,5,3 (lshape_L1, lshape_L2, heatcomp_L1, heatcomp_L2, heatmove_L1, heatmove_L2, convdiff_L1, convdiff_L2) | extra |
| B2 reach 1% / 0.1% from N0=256 | 100% / 88%; baselines 75% / 50% | 24/24, 21/24; 18/24, 12/24 | yes |
| H4: tuned network better by >25% (tool/net > 1.25) | 4 of 16 | 4 of 16 (heatcomp_L2 N=256 and 1024, lshape_L2 N=256 and 1024); same 4 if "error 25% lower" is used; median tool/net 0.34; 11 vs 4 better by >10%; at job level 11 of 48 | yes |
| H5: reduced-basis-clear at N=1024 (validation-selected, tie band 0.1) | 3 of 8 | 3 of 8 (lshape_L1 1.66, heatcomp_L1 0.88, convdiff_L1 0.48); 3 network-clear (heatcomp_L2 -0.12, heatmove_L1 -0.17, heatmove_L2 -0.15); 2 ties | yes |
| H3: flagged jobs / cells / problems; full-field better; recall; already chosen full-field | 15; five; four; 15; 47%; 15 | 15; 5; 4 (convdiff_L1, convdiff_L2, heatmove_L1, heatmove_L2); 15; 15 of 32; 15 | yes |
| Real data R1 median regret / R2 / R3 / R4 | 1.04 / 5 of 6 / 0 of 6 / 9 of 12 | 1.039 / 5 of 6 / 0 of 6 / 9 of 12 | yes |

Every headline number reproduces. I found no arithmetic error in Stage 6 or the real-data check. Additional observations from the same data, not in the paper:

* The best fixed member is only a good comparator in-sample. `gp_full[rbf]` has per-cell regret of 58 (lshape_L2, N=1024), 22 (lshape_L2, N=256), and 6.9, 10.8 and 7.4 on heatmove_L2 (N=64, 256, 1024); `gp_full[matern52]` has up to 12.3 (lshape_L1, N=1024). A leave-one-problem-out choice of the fixed member (choose on the other seven problems) gives median regret 1.69, 54% of cells within 2, max 58, against 1.00, 100%, 1.18 for the tool. So the paper's "a fixed rule also passes" is true only for a rule chosen after seeing these same test errors, and the honest comparison favours the tool more than the paper says. The paper reports the share within 2 but not the worst case of the fixed rule.
* Real-data R4 (9 of 12): the three failures are optimistic by 2 to 5 times (ccpp seed 1, N0=256: forecast 0.049, actual 0.252; ccpp seed 2, N0=64: 0.108 vs 0.253; airfoil seed 2, N0=256: 0.104 vs 0.219). On ccpp the error is flat in N (0.27 at N=64, 0.25 at N=1024), so "within a factor 2" is nearly automatic; the criterion is nearly non-informative where the learning curve is flat. The paper says "R4 predicted to fail, did not" but not this.
* The tuned network on the real data has NRMSE 0.75 at N=64 for ccpp (a linear model gives about 0.26); R3 ("net better by >25% in at most 2 of 6") is passed because the network is badly fitted, not because the tool is good.

## A8. Git history and the pre-registration account (Supplement S2)

`audit/prereg_order_check.py` re-run: output identical to the committed `audit/prereg_order_check.json`; all 15 rows "order ok". Statement checked against the history:

1. **Protocol before results in history: accurate** for all 15 rows (commit order). Experiment dates: addendum v3.0 a99c2c6 (2026-11-02 08:40); chain script e0af619 (08:51); addendum v3.1 2619b07 (2026-11-03 17:29); first R results a88ad5f (2026-11-04 13:14); C results 1dc799e (11-04 14:06); S results 9ebaf04 (11-04 17:39).
2. **"Analysis code were committed ... before the results they concern" is not accurate for Experiment T.** The first job JSONs of `raw_exp6T` are in commit 0e45aae (2026-11-03 17:15); the analysis script `analyze_s6.py` first appears in 2619b07 (17:29, 14 minutes later). For C, S and R the analysis scripts precede the first results commits.
3. **Table S1 "first results commit" is an `environment.json` stub for three rows.** For 6T (42fdacd, 11-02 16:33), A2 (0bcb608) and A3 (82dbbe2) the listed commit contains only `environment.json`; the first per-job JSON is in 0e45aae (11-03 17:15, 32.6 h after the protocol, not 7.87 h), 703ad59 and 39b1b7f. The error is conservative (the true gaps are larger) but the column is mislabelled.
4. **Experiments G3 and H32 finished running before the commit that "pre-registers" them.** The progress logs record elapsed times (`results/progress_expG3.log`: 599 s; `progress_expH32.log`: 336 s). G3: results commit b37dd4e at 13:35:08, protocol commit 4cd411a at 13:32:23, so the run began at least 7.2 minutes before its protocol commit; the commit message says "before running". H32: 0.7 minutes before. The S2 caption already says the check shows "protocol-before-results in history, not protocol-before-first-run", which is true and covers this, but `audit/prereg_order_check.py` says the order is "supported separately by the run chain logs", which the logs contradict for G3 and H32. The paper labels H and G3 post hoc and descriptive, so the effect is small; the statement "no protocol was committed after its results" holds only in the sense of the commit that contains results.
5. **The v3.0 addendum text for the tuned network was edited after the registration commit.** Commit 781e318 (11-02 08:50, ten minutes after a99c2c6) narrows the network search space from depth 2-5, width 64-512 to depth 2-4, width 64-256, and adds the 6,000-epoch specification. This precedes the chain script (08:51) so it precedes the runs, and the addendum says "restricted before any run for compute reasons". It is not in the deviations log (V9 covers the tool only), and Table S1 cites a99c2c6 as the protocol commit for 6S. The narrowing weakens the competitor in H4 and H4 is met exactly at its limit.
6. **V9 and the smoke tests are disclosed and accurate.** Test errors of all pool members on lshape_L1 (N=64, 256, seed 0) and of KRR and polynomial on heatcomp_L2 and convdiff_L1 were seen; the KRR grid (and the leave-one-out arithmetic) were changed afterwards (781e318). The main text now says three of eight problems. The statement in the addendum "no error had been seen" is corrected in V9 and in limitation 2.
7. The history is self-hosted and authored by the same AI system that ran the experiments ("Author: Claude" on every commit). Commit timestamps are not tamper-evident. The paper says this ("not an independent registry").

Overall: the account in S2 is honest and mostly accurate; items 2 to 5 are inaccuracies to correct.

## A9. Other reproducibility defects found

* `code/run_all.py` is described in the Conclusion as "reruns everything", but it omits `exp_real.py`, `analyze_real.py`, `exp_retro.py`, `analyze_retro.py`, `e8_plain_files.py` and `case_study.py`; `aggregate.py` reads their outputs.
* The top-level `README.md` still names `manuscript/Final_Manuscript_v4.*` as "Main paper" and says "rebuild paper: `python manuscript/build_v4.py`"; the paper under review is in `paper/`. The superseded v4 manuscript and its readiness report remain in the repo. A reader following the README reaches the old paper.
* `code/README.md`: stale test count and missing files (A2).

---

# PART B. Final rejection attempt

I try to reject the paper as a hostile referee, then sort the objections into those the paper already answers, those that are still open, and those that would be fatal.

## B1. The case for rejection

**1. Novelty and significance.** The tool is k-fold cross-validated model selection among seven near-neighbour regressors (three POD+GP variants, kernel ridge, polynomial, two full-field GPs), a projection-error floor check (a one-line consequence of orthogonal projection, Proposition 2), and a log-log power-law fit to a four-point learning curve. Each ingredient is standard. The paper states it proposes no new model and that the contribution is "the procedure, its validation, and the evidence". The related-work section reads only abstracts for the closest precedents ("we read only the abstract" for Berzins et al.) and its comparison table gives competitors dashes for everything on that basis while "This paper" has all ticks. To my knowledge the directly relevant literature on cross-validation-based selection among surrogates (for example Viana, Haftka and Steffen on multiple surrogates and PRESS-based selection; the SUMO toolbox of Gorissen et al., which automates model-type selection; SMT; Allen's PRESS statistic, which Proposition 1 rederives and attributes to Golub et al.) and on learning-curve extrapolation for sample-size planning (for example Domhan et al., Figueroa et al., Hestness et al.) is not cited. I could not verify these offline; the authors should check. If those precedents cover the procedure, the contribution reduces to an evaluation, and the evaluation covers eight problems from one library.

**2. The headline evidence is thin and partly by construction.**
* H1a "within 1.18 of the oracle in all 24 cells" compares the selector with the best of its own pool, where seven members include near-duplicates (the rank-8 and rank-32 POD+GP, Matern and squared-exponential variants); on scalar-output data two of the seven are identical. The null the authors use is a uniformly random member, which includes known-poor members. The informative comparison is with a fixed member (median 1.14, 75%) and the tool's improvement over it is 0.91 (better by >10% in 12 of 24 cells). Everything depends on eight problems and three seeds that share pool and test set.
* H1b is satisfied nearly by construction (the comparator is a pool member). H1c failed. H5 failed. H4 was met at the limit with a network the authors themselves call probably under-trained and whose search space was narrowed after the first commit (A8-5). H2 passes pooled only because of N0=64; from 256 runs, which is the regime where a practitioner decides about the next 768 runs, it fails (15 of 24), and the Holm-adjusted p of 0.36 means the pooled pass is within noise. H3 is five cells from four problems, 47% recall, and zero changed decisions. By my count the honest tally is: one criterion clearly met in substance (selection quality, and with qualifications), one trivially met, one met at the margin, two not met, two met only in a pooled or degenerate sense. The cover letter says "five of seven met".
* The runs-needed quantity, which the abstract and the introduction's Gap paragraph promise ("forecast the number of runs needed"), is never evaluated directly; only the error at 4N0 and a binary 1%/0.1% classification at 1024 are.

**3. Generalisation is not shown; the application framing is not tested.** All 44 problems are simulated, 36 with the authors' own solvers (median 6 ms per run) and 8 with scikit-fem (also milliseconds). The title and abstract concern a "slow simulation" and engineers with "a limited number of runs"; no slow simulation, no real field data, no run-count regime below N=64 for the tool, and the tool itself costs 112 s (N=256) to 312 s (N=1024) per selection on one core, which is more than the simulations. The two real data sets are scalar, noisy, four or five inputs, and make POD rank one, so the structure the tool is built around (POD floor, full-field versus POD) is absent; the paper says this. The real-data criteria were declared "descriptive; no threshold is a claim of success", yet the Discussion says "all four descriptive criteria were met", which a reader will read as success, and R3 and R4 pass for reasons given in A7. The most unfavourable numbers for generalisation (the in-sample 35-problem retrospective: max regret 9.25 on fisher_L1, 1.68 on advdiff_L1, two problems over 1.5) appear only in Supplement S7; the main text gives no numbers for them. The abstract's "within a factor 1.18 in all 24 cells" is a statement about eight smooth finite-element problems.

**4. Researcher degrees of freedom and selection effects.**
* The eight evaluation problems, their four families, the pool, the grids, the tie band, the 25% floor rule and the 70/75% thresholds were all chosen by the authors after the results for 36 earlier problems were known; the tool was adjusted after test errors on three of the eight problems (V9). "Pre-registered" refers to a git history written by the same AI agent that ran the study. Whether other finite-element problems were tried and dropped during development is not stated.
* The network arm: one architecture family, 16 trials, search space narrowed after registration, one core; no ensembling. The "strong" label is not earned by the paper's own evidence. A negative H4 finding (network wins in 4 of 16) is therefore uninformative about what a well-tuned network can do, and the tool's pool omits networks, so it cannot recommend a network where networks win (H1c, the cases p=7 and p=9 and moving sources).
* The N=1024 legacy comparisons carry the optimiser-step confound (batch 512 above N=512 doubles steps; V6), which affects H5.
* Test-set use: the oracle, the H3 "full-field better" label, the random-pick null and the mechanism study's "best network" all use test error. This is disclosed, and selection itself uses only training data (verified in code), but the abstract defines the oracle only in a parenthesis.

**5. Over-claiming and the risk of misleading a reader.**
* "We tested it against criteria committed before the evaluation runs" (abstract) is true for the order of commits, but omits that the tool had been adjusted after test errors on 3 of 8 of those problems and that the problems were chosen after the earlier results; both are in the body, neither in the abstract.
* "Five of seven met" (cover letter) and the "met" column of Table 4 are threshold checks; four of the five carry caveats in the body that the headline count hides.
* The two real-data pools and the tuned-network (R3) result.
* The conclusion's "`code/run_all.py` reruns everything" is wrong (A9).
* The committed derived numbers for the retrospective run disagree with the committed raw data (A5-1), and the paper contains three different problem counts for one run.

**6. AI-use disclosure.** The acknowledgments state that design, code, analysis, figures and drafting were "carried out with an AI system acting as a research assistant under the authors' direction", that the reviews were by AI agents, and that the authors "have checked it (to be confirmed by the authors before submission)". The disclosure exists and is candid. But: the author list and affiliations are placeholders; the repository shows every commit as authored by the AI, so "under the authors' direction" and "checked" are unverifiable claims; the reviews (including this one) are by the same model family as the author, so errors with correlated causes are not independently caught (for example the scalar-output shape bug was visible in the paper's own real-data table and in review_01 minor m4 and was not diagnosed); first-person statements such as "we read only the abstract", "we expected the Gaussian process to do well" and "decided now" attribute human reasoning to a process that cannot be audited. The abstract and title do not mention AI involvement. A journal with a human-accountability requirement could not accept the manuscript in its present authorship state.

## B2. What the paper already answers (do not repeat)

Verified against the current text and raw data:

* review_01 M1 (best-fixed comparison, null strawman): answered; the best fixed member and its numbers are reported, the oracle is defined in the abstract. (I add in A7 that the paper under-sells the tool here, because the fixed member is chosen post hoc.)
* review_01 M3 (H3 cells versus jobs, recall, flag already selected): answered in the text (five cells, 47% recall, all 15 already full-field).
* review_01 M4 (problem-level intervals): answered; Table 4 and the text give problem-level intervals and say verdicts describe eight problems.
* review_01 M5 (N0=256 forecast): answered in abstract and text (15 of 24; 7 too low).
* review_01 M6 (Table S1 rows for T, C, S, R; smoke-test count; retrospective run): the rows and the "three problems" statement are fixed; the retrospective run was delivered but is stale and incomplete (A5-1), so only partially answered.
* review_01 M7 ("independent", "explains"): wording changed to "third-party solver", "describes"; the cover letter and conclusion still say "independent finite-element library", which refers to the solver only.
* review_02 build and compliance items (cross-reference leaks, cut-off table, number lint): fixed (A6).
* Negative results are reported: H1c, H5, the failed PT and R4 predictions, 12% band coverage, cost exceeding simulation time, the unconfirmed pilot diagnostic.
* Leakage: separate named random streams, planted-leak test; I found no leakage in the fitting code (selection uses training data only).

## B3. Still-open objections, with severity and a minimal fix

I independently verified each of the following as unaddressed in the committed paper or artefacts.

| # | Objection | Severity | Minimal fix |
|---|---|---|---|
| O1 | Stale retrospective numbers: committed macros and PDF say 32 problems (main text says 36); raw has 35; `darcylin_L2` missing (A5-1). Worst-case regret of 9.25 (fisher_L1) is absent from the main text and abstract. | Moderate (integrity of derived artefacts); not fatal | Run `darcylin_L2`, rerun `analyze_retro.py` and `aggregate.py`, rebuild; give the retrospective median, max and the number of problems above 1.5 in the main text, and add "in-sample, one seed, max 9.25" to the abstract sentence about the oracle, or state that the 1.18 applies to the eight smooth finite-element problems. |
| O2 | S2 inaccuracies: analysis code for T committed after the first T results (A8-2); Table S1 uses `environment.json` stubs for 6T, A2, A3 (A8-3); G3 and H32 ran before their registration commit and the audit script's docstring claims the logs support protocol-before-run (A8-4); the narrowing of the network search space after the registration commit is not in the deviations log and Table S1 cites the earlier commit (A8-5). | Moderate (accuracy of a process claim the paper leans on) | Correct the S2 sentence ("hypotheses and criteria"; drop "analysis code" for T); use first per-job-JSON commits in Table S1; add V12 for the 781e318 edit to the v3.0 text; delete the docstring claim and add G3 and H32 to the caveat. |
| O3 | Tool defect for scalar outputs (A4-1): full-field GP members are silently disabled (garbage scores). No number changes (verified by a patched re-run: identical selections, R1 1.039, R2 5/6, R4 9/12). Real-data table implicitly hides it. | Moderate for the software claim; low for results | Reshape in `GPFull.predict` (or in the metrics), add a scalar-output unit test, state in the real-data paragraph that gp_full was affected and that a patched rerun gives identical results. |
| O4 | "Runs needed" is promised but never evaluated; only 4N0 error and a binary reach at 1024. | Moderate (claim-evidence gap) | Either evaluate `runs_needed` (error of predicted versus actual runs to reach 1% on cells where both exist, and the share of "declines") or remove "number of runs needed" from the Gap statement, abstract and the cover letter. |
| O5 | The tool cannot recommend a network; the cases where networks win (H1c, H4) are exactly the hard cases. The paper says so, but the abstract and title still present a tool that "chooses a stand-in". | Moderate (scope of claim) | Title/abstract: "chooses among classical models" and "does not cover networks"; keep (i) of future work. Do not add a network arm unless the authors want a stronger paper. |
| O6 | "Strongly tuned network" is not strong (own admission), search space narrowed after registration. H4 "met" is weak. | Moderate | Rename "16-trial tuned network" throughout, report H4 as two problems at two budgets; either add one stronger arm or say plainly that H4 gives no bound on what networks can reach. |
| O7 | Related work: abstract-only reading of the closest precedent; no cross-validation-based surrogate-selection or learning-curve-extrapolation literature (see B1.1; to be verified by the authors); the comparison table's dashes are not evidence. | Moderate; could decide the venue | Add and read the surrogate-selection and sample-size-prediction literature; read the full text of Berzins, Batlle, Westermann; drop the tick-table or restrict it to works read in full. |
| O8 | The cover-letter "five of seven met" and the Discussion "all four descriptive criteria were met" hide the caveats. | Low to moderate (reader could be misled) | Say "five met in the pre-specified sense, of which two carry the caveats ..." in the cover letter and replace the R-sentence by "the tool behaved sensibly; the criteria are weak on flat learning curves". |
| O9 | AI-authorship accountability: placeholder authors, "checked by authors" unconfirmed; AI-only review; abstract silent. | Moderate to high for a journal; not a scientific flaw | Authors must be named and must actually reproduce and check the study; add one sentence on AI use to the abstract or a statement section per the target journal's policy; label this review series "AI-agent review, correlated with the author model". |
| O10 | Artefact claims: "`run_all.py` reruns everything" false; README points to the superseded v4 manuscript and missing files; `code/README.md` stale (A9). | Low | Add the real-data, retrospective and plain-file steps to `run_all.py`; rewrite the top-level README to point to `paper/`; move `manuscript/` to `archive/`. |
| O11 | Reproducibility shown only in the original environment (identical package versions); NN reproduction across BLAS builds is not guaranteed (the code README says so); 3 seeds share pool and test set. | Low | State plainly that determinism was verified on the same environment; give a tolerance statement for other machines; if possible re-run one cell on a different CPU or BLAS. |
| O12 | The real-data check is degenerate for the tool (rank-one POD, two members identical, two broken) and its R3 and R4 passes are driven by a badly fitted network and flat curves (A7). | Low | Say so in the paragraph; do not count it as support for the tool's pool selection. |

## B4. Fatal objections

None that invalidates a number or a stated conclusion as written: all headline values reproduce exactly (and bit-identically in this environment), the negative results are stated, and the body generally caveats what the abstract compresses. The closest to fatal are O7 and O9: if the surrogate-selection and learning-curve literature already contains the procedure, the contribution shrinks to a small evaluation; and without human authors who stand behind the study, the paper cannot be submitted to a journal at all. Neither is a flaw in the evidence.

## B5. Verdict

**Conditionally ready.** The science as reported is honest and reproducible; what is claimed is mostly what is supported, with the caveats in the body. The conditions are: fix O1 and O2 (artefact and process accuracy, quick), O3 (one-line bug fix and a sentence), O4 (evaluate or drop the runs-needed claim), O5, O6 and O8 (wording of title, abstract, cover letter), O7 (literature work, the one that needs real effort), and O9 (human authors and checks). No new large experiment is required; the one new run is `darcylin_L2`. If the venue expects a validated, general selection method, the paper is not ready, because eight smooth finite-element problems, a pool of seven GP-like models and one fixed rule that nearly matches it do not establish that. For a candid methods or software note on that scope, it is close.
