SIMULATED REVIEW (written by an AI agent, Claude; not a human referee and not an external reviewer for any journal)

# Review 05: Stage 8 revision for Advances in Engineering Software (expensive 3D case, no-usable-model warning, software section)

Object: `paper/main.pdf` and sources at HEAD `87c4c79` (paper commit `8aa17ed`): subsection `sec:confirm` (`paper/sections/s6d_confirm.tex`, paragraphs "An expensive engineering case" and "A warning for the case where no model is usable"), abstract, discussion/limitations, conclusion, `sec:software` (`s4b_software.tex`), declarations, highlights; `surroselect` 0.2.0; `.github/workflows/tests.yml`; `research_design/protocol_addendum_v3.3.md`, `freeze_v3.3.txt`, `deviations_v2.md` (V14-V16); `results/s8/*`, `results/raw_exp8E/*`, `results/raw_exp6C`, `raw_exp7C`.
Stance: adversarial but fair referee for Advances in Engineering Software (AES), plus numerical and software auditor. Reviewed 2026-11-12.
Method: recomputed every Stage 8 number from the raw per-job JSON with my own scripts (in the scratchpad, `.../scratchpad/review5/`), not from `E8.json`/`U.json`; re-ran the tool on seed 0 from the stored data cache; ran both test suites; installed a scratch copy of the package in a virtualenv and drove the CLI with synthetic data (no repository file was modified; the report you are reading is the only file written). I did not re-run the tuned network and did not re-run the 812 solves. I did not check anything about the journal itself (guide for authors, indexing, quartile, timelines); none is asserted here. Earlier reviews 01-04 were read; resolved points (cell-level pseudo-replication, fixed-member baseline, scalar-output bug, post hoc labelling, "only a finer mesh" proxy, break-even tautology as such) are not repeated except where Stage 8 changed them.

---

## 1. Summary

The Stage 8 record is, again, honestly kept at the level of the main numbers: all four E8 verdicts, the cost arithmetic and the U confusion counts recompute exactly from raw files, the freeze holds (no change after the freeze to the tool, the benchmark package, the run and analysis scripts or the protocol), both test suites pass, and a re-run of the tool for seed 0 reproduces the stored selection, cross-validation errors and test errors bit for bit. The text states the weak points in the places where it states results (E8-3 predicted to fail but met at the limit of 2 of 3 seeds; U design-informed; one expensive problem; forecast mostly optimistic; no network in the default pool).

What I found that the record does not say:

1. **One stated fact is wrong and it comes from the aggregation script, not from the data.** "The false alarms are all on disc_elast_L2" is false: of the 3 false alarms, 2 are `disc_elast_L2` and 1 is `lshape_L2` (seed 1, N = 64). The macro `su_fp_inst` is computed as the set difference "warned problems minus unusable problems", which hides any false alarm on a problem that also has true positives. The same wrong sentence is in `review/claim_evidence_matrix.md` row 42.
2. **The worked report the paper shows to users (Figure 7) contains a number that the paper's own data refute.** It says "Runs needed for error 0.001: about 263" for 256 runs. The pool of 512 runs was available: the same two tied models trained on the first 512 runs of the same permutation give test errors of 1.37e-3 and 1.36e-3, still above 0.1%. The inversion was disclosed as "not evaluated" in section 4.5, but 512 stored runs allowed it to be evaluated at no cost, and the case study then prints it without the caveat that accompanies the forecast. Learning curves of the GP members on this problem are also not monotone (see section 3).
3. **A failed prediction is missing from the prediction table.** Addendum 8.4 predicted a break-even "close to the number of training runs plus a tool time of about two to three solver runs per ten runs of training" (about 51-77 solver runs at N = 256). Observed tool time at N = 256 was 7.6 to 10.9 solver runs (4% of N) and 0.55 to 0.72 at N = 64. The prediction was wrong by a factor 5 to 20 (in the favourable direction). Table 10 lists the E8-3 reversal but not this one; the text says "we had predicted that it would fail" for E8-3 only.
4. **Three different break-even numbers circulate** for the same quantity: 267 (abstract, text, conclusion, limitations; uses the evaluation-only refit that the same sentence says is not needed in use), 264 (Figure 7 and the CLI; in-use cost) and 265 (`paper/highlights.txt`, which matches neither). Hours for 10,000 evaluations are 0.75 in the text and 0.74 in Figure 7.
5. **The engineering evidence is thin in the way an AES referee will notice**: one linear-elastic cantilever with 5 inputs and 108 outputs, smooth by construction, on which E8-1 and E8-2 could not realistically fail (both were predicted to hold, and the thresholds are lax: regret <= 2, error <= 25%). "Four of four criteria met" in the abstract therefore overstates how much was tested; the only risky criterion (E8-3) was met at its limit, against the prediction, with all three ratios optimistic.
6. **The software is a prototype, not yet a paper-worthy software contribution**: no input validation (raw tracebacks on 1-D `Y`, NaN, wrong keys, N < folds, cv = 1), a degenerate learning curve at small N is silently used for a forecast, extremely dense code (422-character lines, 52 lines over 160 characters), global warning suppression at import, pickle persistence, CI configured but never run, placeholders in licence/citation/availability, no comparison with existing tools.

Recommendation: **major revision** (details in section 8). The scientific record is honest and the software works on well-formed data; the contribution is adequate for AES only if it is presented as a software-plus-evidence paper with a hardened tool, a corrected and fully consistent cost/forecast section, and at least one non-trivial engineering case. I do not predict an outcome.

---

## 2. Verification of numbers (independent recomputation)

"Pass" = my recomputation equals the paper value after the paper's rounding. Sources: raw files `results/raw_exp8E/bracket3d_L1__s{0,1,2}.json`, `results/raw_exp6C/*`, `results/raw_exp7C/*` (24 files each, 144 jobs).

| # | Quantity (location) | Paper | Recomputed | Result |
|---|---|---|---|---|
| 1 | Seconds per solver run (abstract, sec:confirm) | 10.1 s | 10.0787 s (identical in all three files) | pass. Note: protocol 8.2 says "median of 8 idle solves"; `exp_s8.py` computes the mean of one timed block of 8 solves. Undeclared, immaterial |
| 2 | DOF (sec:confirm) | about 39,500 | 57 x 21 x 11 nodes x 3 = 39,501 | pass |
| 3 | E8-1 selection | oracle at 64; "within 1.09" at 256 | regret 64: 1.00/1.00/1.00; 256: 1.000/1.208/1.062; geometric mean 1.0865 | pass (the 1.09 is the seed mean; the worst seed is 1.21, not stated) |
| 4 | E8-2 error and warning | 3.6% at 64, 0.31% at 256, no warning | geomean 0.03564 and 0.003114; `usable_` true in all 6 fits | pass |
| 5 | E8-3 forecast | within x2 in 2 of 3, ratios 0.44-0.92, all optimistic | ratios 0.828, 0.917, 0.441; seed 2 fails (log10 = -0.355) | pass (the extrapolation is from training-fold size 48, not 64: see section 3) |
| 6 | E8-4 network | 0.60% vs 0.31% tool vs 0.60% always-POD+GP; zero seeds better; 69 s | network geomean 0.00599; tool 0.00311; POD+GP 0.00603; network never better by >25% (never better at all); network seconds 66.8 / 68.8 / 134.6, median 68.8 | pass (the 69 s hides a 2x range) |
| 7 | Training hours | 0.72 h | 256 x 10.0787 s = 0.717 h | pass |
| 8 | Tool seconds "110, of which 77 needed in use" | 110 / 77 | median of total seconds 99.1 / 109.7 / 123.3 = 109.7; median of "without refit" (CV sums + learning curve) 71.4 / 76.8 / 82.2 = 76.8 | pass, with a precision remark: the 77 s excludes the final fit of the selected model (3.1 s in my re-run, seed 0) and the basis-floor step, and includes the test-set predictions of all members; "needed in use" is about 3-7 s low. Immaterial for the conclusion |
| 9 | Break-even 267 | 267 | (256 x 10.0787 + 109.7)/10.0787 = 266.9 with the evaluation-only refit; 263.6 without; 264.3 with the in-use final fit | arithmetic pass; **consistency fail**: Figure 7 says 264, highlights say 265, text/abstract/conclusion say 267 |
| 10 | 10,000 evaluations | 28.0 h vs 0.75 h, "about 37" | 27.996 h vs 0.747 h (0.738 h without refit); ratio 37.5 | pass (Figure 7 prints 0.74; rounding of 37.5 to "about 37" is acceptable). The surrogate's query time is taken as zero, which should be said |
| 11 | U counts | 23 of 23 (sens 100%); 3 of 121 (spec 97.5%) | tp 23, fn 0, fp 3, tn 118; 0.975 | pass |
| 12 | Unusable problems | heatcomp_L2, helmholtz_L1, helmholtz_L2, lshape_L2 | the same; jobs 3, 9, 9, 2 | pass |
| 13 | "the false alarms are all on disc_elast_L2" | all on disc_elast_L2 | false alarms: disc_elast_L2 s0 N=64 (CV 0.258, test 0.2495), disc_elast_L2 s2 N=64 (0.274, 0.244), **lshape_L2 s1 N=64 (CV 0.258, test 0.198)** | **FAIL** (2 of 3). Cause: `aggregate_s8.py` `su_fp_inst = set(warned) - set(unusable)` |
| 14 | Pooled forecast share (abstract) | 68% of 96 | 37/48 + 28/48 = 65/96 = 67.7% from the paper's own counts; not re-derived from raw files here (verified in review 04) | pass (arithmetic only) |
| 15 | Tests (sec:software) | 13 tool, 70 benchmark | `cd surroselect/tests && PYTHONPATH=../src python -m pytest -q -x`: 13 passed in 66 s; `cd code && PYTHONPATH=src python -m pytest tests -q`: 70 passed in 32 s | pass. CI runs 12 of the 13 (`-k "not network"`) |
| 16 | Highlights "17 third-party-solver problems" | 17 | 8 + 8 + 1 | pass (but only 9 of the 17 were run under frozen tool and prior criteria; see section 5) |
| 17 | Figure 7 text equals `results/s8/bracket3d_report.md` | equal | equal after whitespace normalisation | pass |
| 18 | Reproducibility of E8 from the data cache (my check) | stored selection and errors | tool re-run, seed 0, N = 64 and 256: same selected model, same CV error to the last digit, all 7 pool test errors identical (1e-12), fit time 6.7 s / 90.7 s vs stored 6.9 s / 89.4 s | pass |
| 19 | Determinism ("fits are deterministic for a given seed") | claim | CLI fit on a synthetic file with 1 vs 4 BLAS threads: identical CV errors | pass |
| 20 | Figure 7 "Runs needed for error 0.001: about 263" | 263 | same models on the first 320 / 384 / 512 runs of the same permutation: test error pod_gp[rbf,r=32] 4.6e-3 / 4.4e-3 / 1.37e-3; gp_full[rbf] 6.7e-3 / 2.1e-3 / 1.36e-3 (N = 256: 3.04e-3 / 3.13e-3, matching raw) | **refuted** as a prediction (not a transcription error): 0.1% is not reached at 512 runs; the learning curve is non-monotone between 256 and 384 |

Other Stage 8 sentences checked against the code and records: the paper's "ran serially so that timings are clean (one core)" is consistent with `exp_s8.py` (all thread variables set to 1, one process), but nothing in the record shows that no other load was on the machine during the 13:58-14:09 run (the same session was committing paper edits at 14:13). The 2x difference between the network times (67 vs 135 s) and the 99-123 s spread of tool times between seeds is not explained. I treat the timings as plausible, not as verified-clean.

---

## 3. Findings on the Stage 8 analysis

### 3.1 The worked report overstates what the tool can say (major)

* "Runs needed ... about 263" (Figure 7) is wrong by at least a factor of two on this very problem (row 20). The curve used (n = 24, 48, 96, 192 with errors 1.86e-1, **8.82e-1**, 2.88e-2, 4.31e-3) is itself non-monotone at n = 48; the power law is fitted to the last three points, so the exponent (about 3.8) is dominated by the outlier. For seeds 1 and 2 the curves are also non-monotone or extremely steep (0.703, 0.033, 0.018, 0.0052; 0.705, 0.741, 0.0155, 0.0057).
* The GP members' error is non-monotone in the number of training runs on this problem (256 -> 320 got worse for both members; row 20). That is a property of the fit (hyper-parameters are optimised on at most 300 randomly chosen runs, `n_opt = 300`, so for N >= 300 each member's hyper-parameter fit is a different random subset) and means that the power-law assumption, and therefore both the forecast and the runs-needed inversion, are fragile exactly where the tool says "256 runs". The paper's own caveat ("a rough guide only") does not tell the user that a larger training set can be worse.
* The case study prints the runs-needed statement without any caveat. The tool should refuse or flag it when the curve is non-monotone (a trivially checkable condition) and when the answer lies within 1.1x of the current N.
* The forecast in E8-3 starts from a 64-run fit whose learning curve has n = 12, 12, 24, 48 (the `min_n = 12` floor makes the first two points identical; the last training-fold size is 48). So the "forecast to 256 runs" extrapolates 48 -> 256 (x5.3), not 64 -> 256 (x4), and the four-point alternative fit has a duplicated point. Algorithm 1 in the paper writes n in {N/8, N/4, N/2, N}; the code uses fractions of the 3N/4 training fold with a floor of 12. This should be stated; at N = 64 the "alternative" forecast is not independent.

### 3.2 The cost argument (minor/major presentational)

* Break-even = N + t_tool/t_sim by construction (already noted in review 04). With N = 256 it says "after about 267 evaluations" when the tool adds 10.9 solver runs. Read as a headline in the abstract it is almost tautological: nobody doubts that a surrogate trained on 256 runs is cheaper than the solver for more than 256 evaluations. The informative numbers are (a) the tool costs 4% of the training cost at N = 256, (b) the 10,000-evaluation comparison, and (c) the accuracy given up (0.31%), which is stated only inside Figure 7. I would move (a) and (c) into the abstract and drop "after about 267 evaluations".
* The abstract says "ten thousand evaluations took 0.75 instead of 28.0 hours". Neither number was measured: the stand-in time is arithmetic (training runs + tool seconds), and the 10,000 surrogate queries are taken as free. "Would take".
* Validation runs are excluded (stated). In this case the 300 test runs that gave the 0.31% were themselves 50 minutes of solver time; a practitioner who wants a verified error pays that, and the paper's break-even should show the variant with, say, 10% extra validation runs.
* Selected statement in the addendum (8.4): "break-even ... tool time of about two to three solver runs per ten runs of training": see summary item 3.

### 3.3 The warning check U (minor, with a robustness remark)

* Honest label (design-informed) and the pre-set threshold are correctly reported. The criterion is met over a wide range of thresholds (my post hoc computation, not in the paper): thresholds 0.15 / 0.20 / 0.25 / 0.30 give sensitivity/specificity 1.00/0.93, 1.00/0.96, 1.00/0.975, 0.91/1.00; at 0.40 sensitivity falls to 0.74.
* But 18 of the 23 positives are the two Helmholtz problems with CV error near 1; only 5 positives (heatcomp_L2: 3, lshape_L2: 2) sit anywhere near the threshold, and all 3 false alarms are at N = 64, CV error 0.258-0.274, test error 0.20-0.25 (one at 0.2495). Effectively four problems carry the sensitivity estimate; "sensitivity 100%" should be reported with the 4-problem caveat and an interval.
* The warning is a threshold on the best cross-validated error. It cannot detect the failure mode that the paper itself documents in the earlier-problem run (largest regret 9.25 on `fisher_L1` "not visible in the cross-validated report"). The wording "separated the cases in which no model is usable" in the conclusion is fine; "the tool must say when its selection is not meaningful" (sec:confirm) is stronger than what U shows.

### 3.4 Tie reporting is advertised and never evaluated (minor, new)

The abstract and section 4 list "reports which models are tied" as a feature, but no criterion tests it. Computed from the same raw files (post hoc, mine): the oracle (best test error) lies in the reported tie set in 123 of 144 jobs (85%); the median tie set has 3 of 7 members; two jobs have all 7 members tied (noise-like data). In E8 the oracle is in the tie set in 5 of 6 fits (seed 1, N = 256: no). That is a usable result; it should be in the paper.

---

## 4. Freeze audit (task 2)

`git diff 7c0cc2eb1c8f92a34adb1b62c8be7f148606c9dd HEAD --stat -- surroselect code/src code/experiments/exp_s8.py code/experiments/analyze_s8.py research_design/protocol_addendum_v3.3.md` (run from `Reinforced_Research_Project/`, and from the repository root with the full prefix): **empty output**. Also unchanged since the freeze, and relevant to results: `code/experiments/exp_s7.py` (imported by `exp_s8.py` for `_tool_record`, `_rng`), `code/tests/test_problems_tp3.py`, `code/run_chain8.sh`.

Everything that changed after `7c0cc2e` (36 files; `git diff 7c0cc2e HEAD --stat`):

| Changed after freeze | Influences results? | Note |
|---|---|---|
| `research_design/freeze_v3.3.txt` (new) | no | records the hash; committed in the same second as the freeze commit (13:08:25), so "recorded before the first run" is plausible but cannot be shown from timestamps alone. The raw results were first committed at 14:13:31 (`8aa17ed`); the data cache file is dated 13:58:28, the raw result files 14:01-14:08 |
| `code/experiments/aggregate.py` (+1), `aggregate_s8.py` (new) | no (formatting) | **contains the `su_fp_inst` defect** (section 2, row 13). Declared in V16 as "presentation only" |
| `code/experiments/case_study_bracket.py` (new), `results/s8/bracket3d_report.md`, `paper/tables/case_report_wrapped.txt` | no | a second tool run (CLI) on seed-0-permutation 256 runs; its numbers differ slightly from E8 timings (84 s fixed cost vs 77/110 s) because it is a different run |
| `results/raw_exp8E/*`, `results/s8/E8.json`, `U.json`, `results/chain8_stdout.log` | outputs | consistent with the scripts |
| `research_design/deviations_v2.md` (V16) | no | accurate as far as it goes: does not mention the mean-versus-median detail of t_sim, nor the omitted cost prediction |
| `paper/*` (text, macros, logs, pdf, highlights, graphical abstract, lint allow-list), `review/claim_evidence_matrix.md` | no | |

Unrecorded point inside the frozen state: `problems_tp3.py` mesh size was changed from the prototype (40 x 16 x 8, commit `cdc31a0`) to 56 x 20 x 10 inside the freeze commit itself. This is allowed (before the freeze) and the addendum says the mesh was chosen from solver timings only; I flag it only because the stated problem is therefore a design choice made to hit a 10 s target.

Chronology caveats that remain (not new, stated in the paper's limitations): self-hosted git history; the freeze statement "no surrogate had been fitted" rests on the author's word; the tool 0.2.0 and the 0.25 threshold were written after the Stage 6 and 7 results were known (stated).

**Documentation gap:** the supplement (rebuilt 2026-11-12 14:13) stops at Stage 7: Table S1 and Sec. S2 have no row for the v3.3 freeze (no hash), the deviations list ends at V15 (no V16), and there is no table of the new problem. Claim-matrix row 39 cites `audit/prereg_order_check.json` for the Stage 8 order, but that file has no Stage 8 entry (grep: no `v3.3`, `8E`, `7c0cc2e`). The paper's statement "criteria and predictions committed before it was run (addendum v3.3...)" is true on the git evidence but not supported by the supplement it cites.

Verdict on the freeze: **holds**; nothing that could influence the results changed.

---

## 5. Integrity audit (task 4)

Stated plainly and correctly: E8-3 was predicted to fail and was met "at the limit" (2 of 3), "weak"; all ratios optimistic; U is "design-informed, not held-out"; "one problem is one data point for selection and forecasting"; limitation 6 (milliseconds solvers, only two slower problems, "simulations that take minutes or hours were not tested"); limitation 7 (no stacking/AutoML, no multi-output ARD GP, no operator-learning baseline, no public benchmark); forecast "not validated"; basis check never fired on held-out problems; Helmholtz problems "a weak test"; H1c failures; AI-agent reviews are not human reviews. No quartile, impact factor, turnaround time or indexing claim about the journal appears in the manuscript, highlights or cover letter text I read (grep over `paper/*.tex`, sections, highlights: only "quartiles" in a boxplot caption). `audit/final_journal_decision.md` labels all such figures unverified. Good.

Not stated, or overstated:

| # | Issue | Where | Severity |
|---|---|---|---|
| I1 | False alarm attribution ("all on disc_elast_L2"); the abstract's "numbers written by the aggregation script" invites trust that is misplaced here | sec:confirm; claim matrix row 42; `aggregate_s8.py` | minor error, but a factual error in a paragraph about reliability |
| I2 | Failed cost prediction (tool time 5-20x lower than predicted) not in Table 10 or text | addendum 8.4 vs Table 10 | minor-moderate (selective listing of predictions; the direction is favourable to the tool, which makes omission less likely to be innocent-looking to a referee) |
| I3 | "Four of four criteria were met" in the abstract, conclusion implied. E8-1 (regret <= 2) and E8-2 (error <= 25%, no warning) were predicted to hold on a smooth 5-parameter elasticity problem, with thresholds far from the observed 1.09 and 0.31%; the one risky criterion was met at its limit | abstract, sec:confirm | moderate: the count conveys more testing than took place. The abstract does say the forecast was "unreliable" elsewhere, which helps |
| I4 | "Ten thousand evaluations took 0.75 instead of 28.0 hours": not measured; query time of the stand-in taken as zero | abstract | minor (the body says "would take") |
| I5 | Break-even 267 / 264 / 265 | abstract, Figure 7, highlights | minor but visible; a reader cross-checking the highlights against the figure finds a mismatch |
| I6 | Runs-needed output in Figure 7 contradicted by the 512-run pool (my row 20). The paper states that the inversion "was not evaluated", but then showcases it | Figure 7 | moderate |
| I7 | Highlights: "Tested on 17 third-party-solver problems against criteria fixed before the runs" | `paper/highlights.txt` | moderate: only 9 of 17 (8 further + the cantilever) were run with the tool frozen; the first 8 informed the design (limitation 2). "Third-party" refers to the solver library, the problems and parameter ranges are the authors' own |
| I8 | "A continuous-integration workflow runs the tool tests on two Python versions" stated as a fact; the claim matrix row 43 says "CI workflow not yet run on GitHub" | sec:software | minor overclaim: it is configured, not demonstrated |
| I9 | README: the runs-needed forecast "is validated on third-party-solver problems in the paper"; the paper says the forecast is not validated | `surroselect/README.md` "What the numbers mean" | minor, but README and paper disagree on the central caveat |
| I10 | The statement in Table 2 / data availability that a public repository exists "to be supplied" is honest; but `README` points to "the paper in `../manuscript`", which is the stale v4 manuscript, and `submission/` and the cover letter (dated 2026-11-06) are the pre-AES versions (cover letter still reads "[journal name --- to be chosen by the authors]", "Why this journal" empty, numbers from Stage 7, Word version not rebuilt) | `surroselect/README.md`, `submission/`, `paper/cover_letter.*`, `paper/main_word.docx` | moderate (process): uploading from `submission/` would send the rejected version |
| I11 | Supplement not updated for Stage 8 (section 4) | supplement | moderate |
| I12 | Abstract is about 250 words (my count 255 including the page footer line); check against the journal's limit | abstract | trivial |

AI-use declaration (task 4): the section follows the usual heading and structure and is unusually frank (AI designed and ran experiments, wrote code and tests, analysed results, made figures, drafted text; reviews were AI-agent reviews). Remaining inadequacies: (a) it names "Claude, Anthropic" without model/version or dates; (b) the sentence "the authors reviewed and edited the content as needed [authors to confirm that they did]" cannot be true until human authors exist and have verified the numbers, code and citations, which the whole record says no human has done; (c) the practice described (AI conducting the research, not only language editing) is much wider than what many publishers' policies describe for AI in writing; whether the journal's current policy permits it, and where it wants it described (methods versus end-of-manuscript declaration), must be checked by the authors in the guide for authors (I did not and cannot verify it); (d) CRediT, competing-interest, funding and author blocks are placeholders. A short methods paragraph describing how AI agents were used as reviewers and what the humans verified would be more useful than the declaration alone.

---

## 6. Software review (task 3)

### 6.1 What works

* `pip install --no-build-isolation -e ".[test]"` in a scratch copy with a venv (system site-packages) gives a working `surroselect` entry point; `surroselect fit/predict/evaluate` round-trip works on a 64 x 3 -> 60 synthetic file (7.9 s); `examples/demo.py` runs; the `--json`, `--report`, `--model` outputs are written; `evaluate` agrees with an independent computation; results are deterministic across thread counts; the no-usable-model warning fires on pure noise (all 7 members tied at CV error about 1.01) and not on smooth data; the E8 numbers re-run bit-identically.
* 13 tests are meaningful for the numerical core (closed-form leave-one-out vs brute force, exact polynomial recovery, near-interpolation stability, CLI round trip, scalar shape, warning, cost). The benchmark package's 70 tests include mesh-convergence and identity checks for each scikit-fem problem family (verified by reading the test names in `test_problems_tp*.py`).
* README accurately lists the API, and the changelog states that the selection logic is unchanged from 0.1.0.

### 6.2 Bugs and defects found (exact locations)

| # | Defect | Reproduction / location | Severity |
|---|---|---|---|
| S1 | **1-D `Y` crashes** (`IndexError: tuple index out of range`), although the paper/README advertise scalar outputs (the test uses shape (N,1)). | `np.savez('s.npz', X=X, Y=y1d); surroselect fit s.npz` -> `select.py` line 33, `default_candidates(Y.shape[1], N)` | minor-moderate |
| S2 | **No input validation at all.** NaN in `Y` -> `LinAlgError: SVD did not converge` from deep inside `POD.__init__`; 1-D `X` -> `ValueError: not enough values to unpack`; file without keys `X`,`Y` -> `KeyError: 'X is not a file in the archive'`; `X` and `Y` with different row counts -> a scikit-learn message about inconsistent samples; `N = 3` -> `ValueError: Found array with 0 sample(s)`; `--cv 1` -> `need at least one array to concatenate`; `predict` with the wrong number of inputs -> broadcasting error. All are raw tracebacks. | `cli.py::_load_xy`, `select.py::fit` | moderate (usability) |
| S3 | **Degenerate learning curve silently used for a forecast.** For N = 10 (cv 4) the four curve points are all n = 8 with the same error, and the report still prints "Extrapolated error with 40 runs: about 9.4e-02 (range 9.4e-02 to 9.4e-02)". For N = 64 the curve is n = 12, 12, 24, 48 (duplicate first point). `select.py::learning_curve`, `min_n=12` | moderate |
| S4 | **Runs-needed output is not sanity-checked**: "Runs needed for error 0.5: about 5", "error 0.001: about 25" with N = 64 already at 6.5e-5; non-monotone curves (section 3.1) are not detected. `report.py`, `select.py::runs_needed` | moderate |
| S5 | **Report prints "range 6.8e-08 to 6.9e-08"** and a forecast below solver precision without comment; the "range" is described elsewhere in the paper as not an uncertainty interval, but the report's wording ("range") invites that reading | minor |
| S6 | `surroselect evaluate` always reports mean relative L2 error even for a model fitted with `metric="nrmse"`; the CLI has no `--metric` option, so offset or scalar outputs (the real-data use case in the paper) are Python-API only. `cli.py::cmd_evaluate`, `cmd_fit` | minor |
| S7 | `--queries` without `--solver-seconds` is silently ignored | minor |
| S8 | Import side effect: `models.py` calls `warnings.filterwarnings("ignore", category=ConvergenceWarning)` at module level, silencing scikit-learn convergence warnings for the whole user process | minor (API hygiene) |
| S9 | Persistence is `pickle` (`cli.py::cmd_fit`, `cmd_predict`, `cmd_evaluate`): loading an untrusted model file executes code; files are brittle across scikit-learn/NumPy versions; neither is documented in the README | minor-moderate |
| S10 | Code style: 394 lines in 7 modules, max line length 422, 52 lines over 160 characters, several statements per line separated by semicolons (23 semicolons in `select.py` alone), few docstrings, no type hints, no linter configuration. A referee reading the repository to judge maintainability and extensibility will object; third-party members must implement an undocumented `fit/predict/name` protocol | moderate for a software paper |
| S11 | The tool's cost report uses `tool_seconds` = wall time of the CLI including the learning curve, but there is no way to pass the cost of validation runs or of the user's own post-processing; fine, but the README does not warn that the break-even is `N + t_tool/t_sim` | minor |

Not bugs, probed and fine: constant input columns are handled (`span_` guard); n_opt cap; full-field GP is dropped when m > 2000 (README says "full-field Gaussian processes", the m <= 2000 rule is only in the paper); `make_candidate` regenerates members from names.

### 6.3 Packaging, documentation, CI, licence

* `surroselect/CITATION.cff`: `version: 0.1.0` (package is 0.2.0), no `date-released`, placeholder author and message.
* `LICENSE`: MIT text with "Copyright (c) 2026 [COPYRIGHT HOLDER --- to be set by the authors]"; the paper and README say so. Until the holder is set the grant is not usable in practice.
* `pyproject.toml`: `requires-python >= 3.9`, dependencies unpinned and without lower bounds. The environment documented in the paper is NumPy 2.5.3, SciPy 1.18.1, scikit-learn 1.9.1, Python 3.13.16, all newer than anything a user is likely to have; nothing says which minimum versions were tried. CI covers 3.10 and 3.12 only, so `>= 3.9` is untested.
* `.github/workflows/tests.yml` (read, not run; no remote CI run is on record, claim row 43): syntactically fine (`actions/checkout@v4`, `setup-python@v5`, matrix 3.10/3.12, `pip install -e ".[test]" && python -m pytest tests -q -k "not network"`). Two correctness concerns: (i) the workflow lives at `/home/user/rp_c_7/.github/` and uses `working-directory: Reinforced_Research_Project/surroselect`, which is right only if the published repository root is `rp_c_7` (not the project folder or the `surroselect` folder; if the authors publish `surroselect` alone, the file must move and the path change); (ii) `-k "not network"` deselects 1 of 13 tests, and the optional `nn` extra (torch, Optuna) is never installed in CI, so the `--with-network` path and `TunedMLP` are untested in CI. I confirmed locally that the filter selects exactly 12 tests.
* Documentation: README with an API table, changelog, one 12-line demo. No tutorial that goes from a real export to a decision, no description of the `.npz` contract beyond one sentence (shape conventions, grid, scaling, what "exchangeable" means in practice for design-of-experiments data such as Latin hypercubes or adaptive samples), no API reference, no statement of the pickle risk, no explanation of how to add a member. README refers to "the paper in `../manuscript`" (stale v4).
* Table 2 (software availability) is placeholder-laden: developers and contact, repository link, archive DOI. Without a DOI and a tagged release the software cannot be cited or archived, which for a software paper is a submission blocker.
* Reproducibility of the study: raw JSONs and scripts are in the repository; the E8 data cache (735 kB, 812 solves, about 48 minutes) is git-ignored, so it must be regenerated (hash-seeded, deterministic); the E8 timings are hardware-bound by design.

### 6.4 Is it paper-worthy for AES?

The tool is small, correct on well-formed data, and sensible in intent. As a software contribution it is currently a research prototype: no feature comparison with existing surrogate/UQ/ROM packages (the paper "did not compare their features with ours": pyMOR and UQLab are cited, but not SMT, OpenTURNS, scikit-learn's own `GridSearchCV` over the same pool, AutoML tools), no usability evidence (no user, no workflow integration with an FE package, no example with real exported data), no performance scaling beyond m = 256 outputs, and defects S1-S4 that an engineer will hit on day one. A software-oriented referee will want: validation, error messages, a documented extension point, CI that has run, an archived release and a comparison table.

---

## 7. Weaknesses ranked (task 5)

### Fatal as submitted (all fixable, none scientific)
F1. No archived public release or DOI; licence holder, authors, affiliations, CRediT, funding, competing interests, CITATION metadata are placeholders; the AI declaration's "authors reviewed" is unconfirmed. A software paper cannot be assessed without a citable artefact.
F2. The `submission/` folder, the cover letter and the Word version are the old (pre-Stage 8, pre-AES) files; uploading from them would submit the rejected version. Supplement not updated for Stage 8.

### Major
M1. **The engineering case is one smooth linear problem on which two of four criteria could not fail**, and the headline "four of four" plus "cheaper after 267 evaluations" make it look stronger than it is; the only real test (forecast) was met at its limit and the associated runs-needed number printed in Figure 7 is refuted by the paper's own 512-run pool. No nonlinear, transient, contact or non-smooth engineering model; no output with more than 108 values; no real simulation data.
M2. **The two features that distinguish the tool from plain cross-validation over seven models (error forecast, basis check) are not supported on held-out data** (forecast 68% pooled and failing on the held-out batch; basis flag never fires on held-out problems, recall 0 of 13), tie reporting is untested, and the warning is a design-informed threshold on CV error that four problems carry. What is supported is near-oracle argmin-CV over classical members, which a fixed full-field GP almost matches (regret 1.14).
M3. **No comparison with existing software or generic selectors** (AutoML, stacking, scikit-learn model selection over the same pool, SMT/OpenTURNS/UQLab/pyMOR workflows) and no multi-output ARD GP or operator-learning baseline with a competent budget. For AES the software comparison matters at least as much as the numerical one.
M4. **Software robustness and engineering quality** (S1-S4, S8-S10, CI never run, optional network path untested in CI).
M5. **Generality**: scikit-fem problems built by the authors, eight families; small output dimension; p <= 9 on the problems with held-out evidence; a single expensive problem. The claim "it is used with any simulation code, commercial or not" is a design intent, not a tested capability (no exported-from-solver example).
M6. **Human accountability and process**: the whole study, code, analysis, text and reviews are AI-made; the "independent" reviews are AI-agent reviews with shared priors; the record is a self-hosted git history. This is stated, but a journal will need named humans who have verified the work.

### Minor
m1. False-alarm attribution wrong (row 13) and claim-matrix row 42.
m2. Missing failed cost prediction in Table 10 (summary item 3).
m3. Break-even 267 vs 264 vs 265 and 0.75 vs 0.74; "took" vs "would take".
m4. t_sim: mean of 8 vs "median of 8" in the protocol; the first-solve effect is not reported; the 4-way parallel data generation implies 14.3 s per solve per core under load (2895.6 s x 4 / 812 solves), i.e. the 10.1 s figure is the idle single-solve time (appropriate, but say so).
m5. Learning-curve definition: Algorithm 1 writes n in {N/8,...,N}, the code uses 3N/32...3N/4 with a floor of 12; at N = 64 the first two points coincide; E8-3 extrapolates x5.3, not x4.
m6. The 77 s "needed in use" omits the final fit and floor (3-7 s) and includes test predictions.
m7. Network time "69 s" hides a 67-135 s spread; tool time varies 99-123 s across seeds; no load log for the timing run.
m8. `bracket3d` is called a "cantilever" in the text and a "bracket" in code/outputs; the production mesh (56 x 20 x 10 P1 tetrahedra) is checked only by a test with a 20% tolerance against Euler-Bernoulli at a coarser mesh and a monotone-convergence test, not an absolute discretisation error. For an engineering readership, report the discretisation error of the production mesh (it does not matter for surrogate learning, but it matters for the word "engineering").
m9. The 300 test runs (50 minutes of solver time) are not in the cost argument.
m10. Abstract length and density: the abstract carries about a dozen numbers and many hedges; AES readers will want the practical message first.
m11. Highlights: "17 third-party-solver problems against criteria fixed before the runs" (I7); "stand-in cheaper after about 265 evaluations" (I5).
m12. README: "validated" (I9); missing import in the network example; "../manuscript" link.
m13. CITATION version mismatch; Python 3.9 claim untested.

### Is the contribution adequate for AES?
Borderline. The journal's stated interest (as quoted in `audit/final_journal_decision.md`, from third-party text, not verified against the journal's own guide) is computer-based engineering techniques and software for simulation and AI methods. The paper has what such a venue values in part: honest validation, tests, a pre-specified protocol, negative results. It lacks what it also values: a mature, documented, comparable software artefact, and an engineering application with consequence. The paper is currently better described as a benchmark-and-negative-results study with a small utility; the Stage 8 additions move it in the right direction but do not yet close the gap. I cannot estimate acceptance probability and do not.

### Single most valuable additional piece of work
A **prospective, blind use of the tool on a genuinely non-trivial simulation, with the follow-up runs actually spent to check what the tool said**: choose an engineering model that is nonlinear or transient, has a field output with m >= 10^3-10^4 and p of 6-12, take the tool's statement at N0 runs (selected model, ties, warning status, runs needed for a stated tolerance), then run the additional budget and report whether the statement held and what the decision cost would have been with and without the tool, including validation runs. The cheapest first step, which needs no new solver run: use the 512 stored cantilever runs to test the runs-needed inversion and the 256 -> 512 forecast on all three seeds, report non-monotone curves, and fix or remove the "Runs needed" output accordingly.

---

## 8. Concrete fixes, ordered by value

1. **Fix the false-alarm attribution**: compute `su_fp_inst` from the false-alarm rows (`warn and not unusable`), not from a set difference; regenerate the macro; correct claim-matrix row 42. Expected text: "the false alarms are two jobs on `disc_elast_L2` and one on `lshape_L2`, all at N = 64 with cross-validated errors of 0.258-0.274".
2. **Test the runs-needed output with the 512 stored runs** (all three seeds; 256 -> 384 -> 512), report the result, and change the tool: refuse to give a number when the curve is non-monotone or when the answer is within about 1.1x of N; print "target already reached" when the target exceeds the current CV error; stop printing "range" as if it were an interval. Update Figure 7 and its caption.
3. **One break-even number everywhere**: use the in-use value (264) in abstract, text, conclusion, limitations, highlights, claim matrix; show 267 only as the conservative variant; "would take" instead of "took"; state that stand-in query time is neglected; move the tool-cost-as-fraction-of-training-cost (4%) and the accuracy given up (0.31%) into the abstract in place of the break-even.
4. **Add the failed cost prediction to Table 10** (predicted 2-3 solver runs per 10 training runs; observed 0.04 per run at N = 256 and 0.01 at N = 64) and to V16; also record the mean-versus-median detail of t_sim.
5. **Re-word "four of four"**: report E8-1/E8-2 as "predicted and met, with margin" and E8-3 as the only criterion that could have failed, met at its limit, with all ratios optimistic; add "single smooth linear problem" in the abstract.
6. **Make the software release-ready**: input validation with clear errors (S1, S2), a guard for degenerate/non-monotone curves (S3, S4), `--metric` in the CLI (S6), remove the global warning filter (S8), document pickle risk or add a non-pickle export (S9), refactor the one-liners into readable functions with docstrings and type hints (S10), add tests for each of these, install the `nn` extra in one CI job, make the workflow path match the published repository layout, run CI and add the badge, tag 0.2.0, deposit on an archive with a DOI, set the copyright holder, fix `CITATION.cff` (version, date, authors), update README links (`../paper`, not `../manuscript`), replace "validated" by the paper's own wording.
7. **Add a software-comparison table** (features, inputs, outputs, selection, forecast, cost report) against pyMOR, UQLab, SMT, OpenTURNS, scikit-learn model selection and one AutoML tool, based on reading their documentation (say so), and add at least a scikit-learn `GridSearchCV`/stacking baseline over the same pool on the 16 problems.
8. **Evaluate tie reporting** with the numbers in section 3.4 (oracle in the tie set in 123 of 144 jobs; median size 3 of 7), labelled post hoc.
9. **Replace the stale artefacts**: rebuild the cover letter (journal named, "why this journal" written by the authors from the guide for authors), Word version and `submission/` from the current sources; extend the supplement with the v3.3 freeze hash, the Stage 8 problem table, V16 and the Stage 8 entry in `prereg_order_check`.
10. **Report timing provenance**: record machine load (e.g. `uptime`/`ps` snapshot) during the E8 run, the spread across seeds, and the discretisation error of the production mesh; state that the 10.1 s is an idle single-solve time (the pooled data generation took 14.3 s per solve per core).
11. **AI declaration and accountability**: name the model and version and dates, add a methods paragraph on the AI-agent review process, and have named human authors verify numbers, code and references; resolve the "[authors to confirm]" sentence honestly.
12. Add the U robustness table (thresholds 0.15-0.4) and the four-problem caveat; state that 18 of 23 positives are the two Helmholtz problems.

---

## 9. Recommendation

Major revision. Integrity of the record: good on the main numbers, with one factual error, one omitted failed prediction and inconsistent break-even values that should be fixed before anyone else finds them. Freeze: holds. Software: works on well-formed data, reproducible, not yet release-quality. Evidence: honest but thin for the engineering claim. No acceptance outcome, quartile, impact factor or timeline is claimed or implied in this review.

Files written by this review: this file only. Scratch scripts and outputs (not part of the repository): `/tmp/claude-0/-home-user-rp-c-7/d247ddca-2eb6-5163-bca0-57b556b9e2f0/scratchpad/review5/` (`verify_e8.py`, `verify_u.py`, `runs_needed_check.py`, `rerun_e8.py`, CLI test files under `cli/`, scratch package copy and virtualenv).
