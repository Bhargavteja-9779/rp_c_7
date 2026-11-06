SIMULATED REVIEW (written by an AI agent, Claude; not a human referee and not an external reviewer)

# Review 04: Stage 7 revision (held-out confirmation, network in the pool, expensive solver)

Object: `paper/main.pdf` and sources at HEAD `5b4796a` (paper commit `d6f84c2`), new subsection `sec:confirm` (`paper/sections/s6d_confirm.tex`), abstract, introduction contribution 2, discussion and limitations, conclusion, supplement pre-specification note.
Reviewer stance: adversarial referee for a strong Q1 journal in computational science / surrogate modelling, plus numerical auditor. Reviewed 2026-11-06.
Method: I read the protocol addendum v3.2 and the paper, then recomputed the numbers independently from the raw per-job files (`results/raw_exp7{T,C,S,SP,N,E}`, `raw_exp6*`) with my own scripts (in the scratchpad), not by re-reading the analysis outputs. I compared them with `results/s7/*.json`, `results/s7_pooled/*.json`, `paper/tables/macros.tex` and the compiled PDF text. I used `git diff` against the freeze commit `a096980`. I ran the unit tests of `problems_tp2.py` and a few probes of the solvers. I did not refit any surrogate and did not re-run the tool; my verification is of the stored outputs. Nothing in the repository was modified except this file.
Earlier reviews (01 to 03 and triage) were read to avoid repeating resolved points (cell-level pseudo-replication, fixed-member baseline, scalar-output bug, retro run, post-hoc labelling). Where I return to one of them it is because Stage 7 re-introduced it.

---

## 1. Summary

The revision is, on the whole, honest about outcomes. Failures are reported in the text (forecast criterion not met on held-out problems, H1c not met, H3 not evaluable, E1 not met). The freeze discipline holds on the evidence available: nothing in the tool, the run scripts, the analysis scripts or the protocol changed after the freeze commit. Every headline number in the new subsection that I recomputed matches the raw data. I found no fabricated or mis-transcribed numbers.

The problems are elsewhere:

1. What the new evidence shows is much thinner than the framing. The "expensive solver" experiment re-uses a problem the paper has already seen (same four inputs, same 130 output probes, a refined mesh), and its break-even arithmetic is `N + t_tool/t_sim` by construction. The paper's premise (slow simulation) is still untested.
2. After Stage 7 the two components that distinguish the tool from plain cross-validation over a small pool (the error forecast, the basis flag) are not supported on held-out data. What remains supported is "cross-validation over seven classical models is near-oracle on smooth problems and about as good as one well-chosen fixed Gaussian process". That is a thin contribution for the claimed venue.
3. Two of the eight new problems (Helmholtz) are ill-posed as surrogate tasks (undamped, pole inside the parameter range; every model has a relative error of 25% to 300%). They drive three of the "interesting" findings (H1c failure, "wave problems", network-in-pool benefit). The paper describes them as "near resonance" and Table 8 says "several resonances" for L2, which is wrong (one double eigenvalue).
4. Several reporting choices flatter the result slightly: "six of eight verdicts" (the table supports five of seven evaluable), pooled instead of held-out numbers in the abstract and conclusion for the forecast, a narrower case-level interval for held-out B1, two wrong pre-registered predictions not listed, and a weak baseline for the reach classification.

Recommendation: major revision. The integrity of the record is good; the scientific contribution is not yet adequate for a strong Q1 methods journal and is better described as a pre-specified benchmark and negative-result study with a small utility. See sections 7 and 8.

---

## 2. Verification of numbers (independent recomputation from raw files)

"Pass" = my recomputation equals the paper value after the paper's rounding. All H-labels are the paper's (H1a = S1, H1b = S2, H1c = S3, H2 = B1, H2 reach = B2, H3 = F1, H4 = S4, H5 = PT).

| # | Quantity (paper location) | Paper | Recomputed from raw | Result |
|---|---|---|---|---|
| 1 | H1a median regret, held-out (sec:confirm, Table 9, abstract) | 1.04 | 1.0440 (24 cells, geometric seed means) | pass |
| 2 | H1a share of cells with regret <= 2 | 96% | 23/24 = 95.8% | pass |
| 3 | worst cell | helmholtz_L1, N=1024, 5.2 | same, 5.2009 | pass (note: worst per-job regret is 12.07, helmholtz_L1 N=1024 seed 2; not mentioned) |
| 4 | H1b median ratio vs legacy POD+GP | 0.97 | 0.9687; 7 cells better by >10%, 5 worse | pass |
| 5 | H1c median ratio vs benchmark selection | 1.08 | 1.0798 | pass |
| 6 | H1c better / worse cells | 6 / 10 | 6 / 10 | pass |
| 7 | "5 of the worse cells are Helmholtz" | 5 | 5 (helmholtz_L1 at 64, 256, 1024; helmholtz_L2 at 256, 1024) | pass |
| 8 | "benchmark's neural-network methods were selected" in those cells | NN | 14 of the 15 seed-level legacy selections in those 5 cells are NN methods (one is pod_gp) | pass |
| 9 | H2 forecast within x2 | 28 of 48, 58% | 28/48 | pass |
| 10 | H2 Wilson interval | 44% to 71% | 44.3% to 71.2% (case-level, 48 non-independent cases) | pass numerically; see W7 (it contains the 70% threshold) |
| 11 | forecasts too optimistic by > x2 | 18 | 18 (over: 2) | pass |
| 12 | median predicted/actual | 0.58 | 10^-0.2389 = 0.577 | pass |
| 13 | share from N0=64 / 256 | 54% / (62%) | 13/24 = 54.2% / 15/24 = 62.5% | pass |
| 14 | B2 accuracy 1% / 0.1% | 100% / 88% | 24/24, 21/24 | pass |
| 15 | B2 majority baseline | 62% / 54% | 62.5% / 54.2% | pass |
| 16 | H3 flagged cells | 0, "not evaluable" | 0 of 72 fits flagged; 13 of 72 fits in which a full-field GP beats the best POD member by >10% (recall 0/13) | pass; recall omitted, see W5 |
| 17 | H4 network > 25% better than tool | 2 of 16, median ratio 0.32 | 2 of 16 (helmholtz_L1 at 256 and 1024), 0.3243 | pass |
| 18 | H5 reduced basis clear at N=1024 | 6 of 8 | 6 of 8 (values 1.81, 1.16, 1.13, 0.115, 1.87, 0.45); 5 of 8 if disc_elast_L2 (0.115 vs threshold 0.10) is dropped | pass |
| 19 | Problem-level intervals H1a / H1b / H1c | 1.00-1.11 / 0.91-1.04 / 0.94-1.32 | same as `extras.json` (cluster bootstrap over 8 problems) | pass |
| 20 | Pooled B1 | 65 of 96 (68%), problem-level 56%-79% | 65/96; my own cluster bootstrap 56%-78% | pass |
| 21 | Pooled B1 by N0 / bias / under / over | 73% / 62%, 0.82, 25, 6 | 35 of 48 (72.9%) at N0=64, 30 of 48 (62.5%) at N0=256, median 0.821, 25 under, 6 over | pass |
| 22 | Pooled H1a / H1b / H1c / H4 / H5 (Table 9) | 1.01;98% / 0.93 / 1.02;17/19 / 6 of 32 / 9 of 16 | match `s7_pooled/criteria.json`; H4 = 4+2, H5 = 3+6 | pass |
| 23 | Network in pool: choice changed | 5 of 24 fits | 5 of 24 (helmholtz_L1 3, reacdiff_fe_L2 2) | pass |
| 24 | Error clearly lowered in 2 problems; helmholtz_L1 0.64 -> 0.36 (network alone 0.27) | as stated | 0.6398 -> 0.3602; 0.2746; reacdiff_fe_L2 0.00428 -> 0.00361 | pass |
| 25 | W1 median regret / max / share | 1.05 / 1.13 / 100% | 1.0526 / 1.1323 / 8 of 8 | pass |
| 26 | W2 | 7 of 8 | 7 of 8 (only helmholtz_L1 fails: 0.360 > 1.1 x 0.2746) | pass (but see W4: nearly vacuous) |
| 27 | Median fit seconds with network / default pool | 431 s / "about a hundred" | 431.4 s / 103.5 s (C7 at N=256) | pass |
| 28 | S5 improved on standard network | 12 of 16, median 0.85, 10 by >10%, 9 min | 12, 0.8539, 10, 525.7 s = 8.8 min | pass |
| 29 | S5 network beats tool by >25% (stronger / standard) | 4 (convdiff_L2, heatcomp_L2, lshape_L2, reacdiff_fe_L2) / 3 (heatcomp_L2, helmholtz_L1, lshape_L2) | identical lists | pass |
| 30 | S5 median ratio tool/stronger | 0.56 | 0.5589 | pass |
| 31 | Table 10 (N=256 per-problem errors, all six columns) | as printed | match `S1_cells.csv`, `S4_cells.csv`, `W.json` to the printed 2 significant digits | pass |
| 32 | E7 seconds per run | 1.52 | 1.5177 | pass |
| 33 | E7 mean regret at 64 / 256 | 1.28 / 1.35 | 1.281 / 1.347 (per seed 1.13, 1.13, 1.58 / 1.00, 1.40, 1.64) | pass |
| 34 | E7 geometric errors tool 64 / 256, fixed GP 256, network 256 | 3.7e-2, 8.2e-4, 4.4e-3, 6.2e-3 | 3.71e-2, 8.19e-4, 4.36e-3, 6.24e-3 | pass |
| 35 | E7 network seconds | 96 | median 95.7 | pass |
| 36 | E7 forecast | 1 of 3 within x2; ratios 1.25 to 3.14, "all too high" | 1.25, 2.11, 3.14; 1 of 3 | pass (direction caveat, see W6) |
| 37 | E7 tool seconds 64 / 256 | 9 / 120 | medians 9.14 / 119.6 (these include `refit_all=True`, an evaluation step; sum of CV seconds is only ~55 s of ~100 s fit at N=256) | pass; overstated cost, see m9 |
| 38 | E7 simulation hours 64 / 256 | 0.03 / 0.11 | 0.0270 / 0.1079 | pass |
| 39 | E7 break-even | 70 / 335 | (N t_sim + t_tool)/t_sim = 70.0 / 334.8 | pass (arithmetic right; see section 5) |
| 40 | 10 000 predictions: solver / surrogate hours | 4.2 / 0.14 | 4.216 / 0.141 | pass |
| 41 | "six of the eight verdicts were met" (sec:confirm) | six of eight | Table 9 has 8 rows: 5 met (H1a, H1b, H2 reach, H4, H5), 2 not met (H1c, H2), 1 not evaluable (H3). The macro counts B2 twice (1% and 0.1%) and drops H3 | **FAIL** (counting inflation; correct statement is 5 of 7 evaluable) |
| 42 | Abstract: forecast "within a factor two in only 68% of 96 cases over all sixteen problems" | 68% | correct as a pooled number, but the held-out value is 58% (28/48); the pooled number includes the problems on which the tool was developed | pass numerically; **selective** (see W3) |
| 43 | Abstract / limitation 5 / sec:confirm on the network in the pool | "one of the two wave problems" / "one of eight further problems" / "two problems" | the data give two problems with a clear change (helmholtz_L1 -0.44, reacdiff_fe_L2 -0.16) | **inconsistent** wording across three places |
| 44 | Table 8, helmholtz_L2 "k^2 in [30,70] (several resonances)" | several | Dirichlet eigenvalues of the unit square: 19.74, 49.35 (double), 78.96; FE (P1, refine 5): 19.75, 49.41 (x2), 79.15. Only one (double) eigenvalue lies in [30,70] | **FAIL** (factual error) |

I found no mismatch between `macros.tex`, the JSON files and the PDF text beyond items 41, 43, 44.

---

## 3. Pre-specification and freeze audit

Checked: `git diff a096980 HEAD` on `code/experiments/analyze_s6.py`, `analyze_s7.py`, `exp_s7.py`, `code/src/`, `surroselect/`, `research_design/protocol_addendum_v3.2.md` is empty. The only code changes after the freeze are `aggregate_s7.py` (new in `2da4dce`, after the S+ runs and before the final analysis), a one-line change in `aggregate.py`, the prereg-order script, the freeze hash file (appended 1 second after the freeze commit), the claim matrix. `aggregate_s7.py` only formats macros and tables. Between its first version and HEAD the only content changes are table layout, and one deliberate one: the "Pooled" column was changed to show numbers only without verdicts (the pooled thresholds were set for 8 problems). That was done after the results were seen, but it removes verdicts rather than adding them, and the paper states it ("numbers only"). Fine.

Timeline: freeze `a096980` 19:56:57; hash file `08d5259` 19:56:58; earliest raw output file mtime 20:15:44 (T7); first result commit `af431a1` 20:27:41. So the runs started after the freeze. Git cannot prove that no earlier run existed; the addendum discloses smoke runs on `lshape_L1`. I checked there is no result file for any other problem from before the freeze.

Criteria in Table 9 vs addendum v3.2 section 7.3: H1a (median <= 1.5 and >= 75% of cells <= 2), H1b (<= 1), H1c (median <= 1 and more cells better than worse by >10%), H2 (>= 70% of 48), H2 reach (>= 75%), H3 (evaluable if >= 5 flagged cells), H4 (<= 4 of 16), H5 (>= 5 of 8, validation-selected, y > 0.10), W1 (<= 1.5 and >= 75% <= 2), W2 (>= 6 of 8 within 1.1), E1 (regret <= 2 at both N; forecast within x2 in >= 2 of 3 seeds), S5 (descriptive): all match the code that was frozen and the code that produced the numbers. No threshold, pool member, grid or data protocol was changed. The pooled analysis is labelled descriptive, as in the addendum.

Weak points in the pre-specification itself (not violations):
* Addendum 7.4 says S3 "was only just met in Stage 6". It was **not** met in Stage 6 (median 1.01, 11/9 cells, "not met"; the paper's own Table 9 says so). The prediction text was wrong when written. The paper does not repeat the error, but the addendum is cited as a record of what was predicted.
* The addendum says "no error of any surrogate on any new problem had been seen", true, but the authors had looked at run times and "value ranges" of the new solvers and had run unit tests that exposed V14. The paper discloses V14 but not the value-range look. For Helmholtz this matters (see W1): output norms span three to four orders of magnitude and the authors would have seen that.
* The eight new problems were chosen by the authors after the Stage 6 results and three reviews, including "deliberately hard regimes". The paper says this (limitation 2). It does not follow that "held-out" means more than "the tool code was frozen".

---

## 4. Integrity: failures, predictions, overclaims

### 4.1 Are failures reported plainly?
Mostly yes. Reported: H2 not met (with an explicit "we describe the forecast as a rough guide ... not as validated"), H1c not met, H3 not evaluable, E1 not met, the stronger network wins more but "did not change the picture", expensive-solver claim explicitly limited. The abstract ends with "the evidence for much slower simulations is missing". That is good.

Omissions or softenings:
* H3: Stage 6 reported recall (47% of the 32 fits where a full-field GP was better were flagged). For Stage 7 the paper says only "the flag never fired (H3 not evaluable)". The raw data show 13 of 72 fits in which a full-field GP beats the best POD member by more than 10%, and the flag fired in none (recall 0/13; `extras.json` `h3.recall_jobs = 0.0`). That is a direct negative result about the flag and it is not stated. The discussion says "its usefulness rests on one batch of flags", which understates it.
* "Worst case is a regret of 5.2" is a cell-level geometric mean; the worst single job has regret 12.07 (helmholtz_L1, N=1024, seed 2: CV errors 3.6 vs 30.5, test errors 3.10 vs 0.26). Absolute errors there are above 1.
* B2: the paper writes "nevertheless right (100%, 88% against 62% and 54%)". The Stage 6 section, correctly, says the 1% result "carries no information beyond the base rate". For the held-out batch the majority baseline is 62.5% and the accuracy is 100%, so it does carry information relative to that baseline, but a better reference is "carry the current test error forward" (predict "reached" iff the selected model's error at N0 = 256 is already below the target). I computed that rule from the stored test errors: 100% at 1% and 79% at 0.1%. So the forecast adds nothing at 1% and 2 cases (24 x 0.09) at 0.1%. The paper presents the reach classification as a surviving positive result without this reference.

### 4.2 Predictions of addendum 7.4 vs outcomes

| Prediction (written before runs) | Outcome | Reported in paper? |
|---|---|---|
| S1 holds | held (1.04, 96%) | yes |
| S2 holds | held (0.97) | yes |
| S3 marginal, may fail | failed (1.08; 6/10) | yes |
| B1 holds from N0=64, may fail from 256 | failed from both (54%, 62%) | yes ("where we had predicted that it would hold") |
| B2 will probably not beat the majority baseline by much | beat it by 38 and 34 points | **no** (presented as a positive result; the wrong prediction is not named) |
| PT will probably not hold | held (6 of 8) | yes |
| Basis flag will probably fire on helmholtz_L2 (maybe advdiff_cell_L2) | never fired | yes |
| helmholtz_L2 is the likeliest source of a large regret | helmholtz_L1 N=1024 (5.2); helmholtz_L2 maximum cell regret is 1.55 | **no** |
| Stronger network wins more cells (S5) | 4 vs 3 | yes (weakly: one cell difference) |
| W1 holds, W2 uncertain | both held | yes |
| E1: regret small; forecast uncertain | regret 1.28/1.35; forecast 1 of 3 | yes |

Five predictions were wrong (B1 at 64, B2, PT, flag, helmholtz_L2 regret) out of about eleven. The paper lists three of them in the text plus H5. The two omitted are not damaging, but the claim "two of them against what we had predicted" is incomplete, and listing all of them in a small table would cost four lines.

### 4.3 Overclaim / "novel" / "SOTA" language
I found no "novel", "state of the art", "first" or "outperforms" in the new text. The introduction's "Gap" paragraph still says existing comparisons "do not give the practitioner a validated procedure"; after Stage 7 the forecast part of the "procedure" is explicitly not validated and the flag part rests on one batch. Suggest rewording to "a pre-specified evaluation of a procedure".

Claims not fully backed:
* Conclusion: "Adding a tuned network to the pool helped where networks win". Networks win (S5) on convdiff_L2, heatcomp_L2, lshape_L2 and reacdiff_fe_L2; N7 was run only on the eight new problems; it helped on helmholtz_L1 (three seeds: 0.69, 0.27, 0.25, very noisy) and reacdiff_fe_L2 (16%). "Helped where networks win" generalises from two problems.
* Discussion: held-out results "support these four claims beyond the eight problems on which the tool was developed". Two of the four (H1b, H4) are nearly true by construction (the legacy POD+GP is a pool member; the network is weak); the reach classification is not informative (4.1). Only selection quality (H1a) is a real held-out confirmation, and its problem-level share interval over eight problems has a lower limit of 53% (`s1_problem_wilson`), below the 75% threshold, as the Stage 6 text itself noted.
* Abstract: "always choosing one fixed pool member does almost as well". That holds for the member chosen **with hindsight** (median regret 1.14, 75% of cells <= 2). The leave-one-problem-out fixed member (chosen without hindsight) has median regret 1.44 and 71% of cells <= 2, which would fail H1a. The abstract should say so; as written it understates what selection adds.

### 4.4 Is the expensive-solver claim properly limited?
The wording is limited (1.52 s per run; "one problem"; "not evidence about simulations that take hours"). The limitation is stated three times and I have no objection to the phrasing. My objection is to what the experiment can show at all (W1 below).

### 4.5 Break-even arithmetic
Correct as defined in the addendum: Q* = (N t_sim + t_tool)/t_sim = N + t_tool/t_sim. It gives 70.0 and 334.8. Observations: (i) it is dominated by N, so "335 predictions" is essentially "256 training runs plus 79 runs worth of tool time"; (ii) the tool time includes `refit_all=True`, which refits every pool member to score it on test data (about 40% of the fit time at N=256) and is not needed in use; the cost is therefore overstated (conservatively); (iii) it ignores surrogate prediction cost, the validation/test runs a user would also want, and parallel evaluation of the solver; (iv) the N=64 value of 70 corresponds to a 3.7% error, the N=256 value to 0.08%, so "cheaper than the solver" is not "equally accurate as the solver".

### 4.6 Problem-level vs cell-level inference
Described correctly where it is described: "Problem-level 95% intervals (resampling the problems) for the medians" matches the code (`analyze_s6.py`, cluster bootstrap over the eight problems, 2000 resamples). Two inconsistencies:
* The held-out B1 interval printed in the text ("44% to 71%") is the case-level Wilson interval treating 48 cases (8 problems x 3 seeds x 2 N0, seeds sharing pool and test set) as independent. The problem-level interval (42% to 77%) is computed and has a macro (`\SvPlBoneLo/Hi`) but is not used. The pooled interval printed is the problem-level one (56% to 79%). Limitation 3 says case/cell-level intervals "are optimistic"; the new text should apply that to its own number.
* Both held-out and pooled intervals contain the 70% threshold. The verdict "not met" and the phrase "the forecast of H2 failed" are point-estimate verdicts. The Stage 6 section handled this correctly ("the interval includes the threshold; Holm p = 0.36"); the new subsection drops the qualification. The right wording is "criterion not met; not distinguishable from the threshold with eight problems".
The Holm-adjusted p-values in `criteria.json` (e.g. S1 share vs 75%: 0.027) are cell-level and are not reported in the new subsection; fine, since they would be pseudo-replicated.

---

## 5. Soundness of the new problems and their unit tests

I ran `code/tests/test_problems_tp2.py`: 10 passed (3 s). Assessment of what the tests do and do not establish:

| Problem | What the tests establish | What they do not | My own probes |
|---|---|---|---|
| helmholtz | mesh convergence at one parameter point k^2 = 9.2 (far from resonance), < 5e-3 between refine 5 and 6; symmetry and positivity at k^2 ~ 0 | nothing in the resonant regime; no exact or manufactured solution; no check that the pole is where it should be | Dirichlet problem, **undamped**, Gaussian source. FE eigenvalues 19.75, 49.41 (x2), 79.15. L1 range [2,20] contains the first pole at 98.6% of the range (the top 1.4% of the range lies beyond it). L2 range [30,70] contains **one** (double) pole, not "several resonances". Output norm over the 1000 test inputs: L1 median 3.07, 99th percentile 471, max 3507; L2 median 5.2, 99th percentile 175, max 72 600. About 4% (L1) and 2% (L2) of test inputs are within 0.5 of the pole. |
| reacdiff_fe | linear limit scales as 1/D; cubic sink lowers the peak; 30 Newton iterations equal 12; mesh convergence | does not assert convergence of the residual; the solver has no convergence flag, so a non-converged solve would pass silently | 200 random inputs each for L1 and L2: 12 Newton iterations equal 60 iterations to machine precision (relative difference 0.0). The Newton claim is fine. |
| disc_elast | after the V14 fix: load reversal, x10 stiffness scaling, centre probe moves, mesh convergence (3 -> 5 -> 6, error at refine 5 < 5%) | scaling and reversal identities would also pass if sector assignment were wrong; the 5% convergence tolerance is loose (the arcs are defined by facet-midpoint polar angle, so discretisation error is first order) | The fix is right in principle (boundary facets only, regions by polar angle, probes at fixed physical points). The regression test targets the actual bug (centre probe zero). |
| advdiff_cell | mesh convergence (refine 4, 5, 6; < 5% between 5 and 6) | the test is named "...and_positivity" but asserts no positivity | positivity holds (min/max >= 0.004 over 100 draws); at the hardest corner the difference between refine 5 and 7 is 1e-3. So the "thin layers" of L2 are resolved and smooth: the L2 problem is harder only through one more input. |

Soundness conclusions:
* The suite (other than Helmholtz) is smooth, mesh-converged and GP-friendly; six of eight problems are reduced-basis winners at N=1024 and the tool is near-oracle. That is a legitimate result but it is the regime in which any competent selection or a fixed GP works.
* Helmholtz is not a sound surrogate benchmark as defined: an undamped pole inside the sampling range makes the response non-analytic in k^2 and heavy-tailed. All pool members and all networks have relative L2 errors of 0.25 to 3 (Table 10: tool 0.64 and 1.0; best "benchmark" 0.23 and 0.92), and the cross-validation scores themselves are above 0.9 for the chosen members. Selection among models that are all unusable is noise (regret 6.8 and 12.1 at N=1024, seeds 1 and 2). It is therefore not evidence about "wave problems", and these two problems alone carry the H1c failure (5 of 10 worse cells), the largest regret, the B1 misses on helmholtz (2 of 6 cases within a factor two for each of the two problems), and most of the benefit of the network in the pool. A fair reading is: "on a problem with a pole inside the parameter range, no model in the study is usable and the tool does not warn."
* The tests are meaningful for the V14 bug and for basic correctness. They are not strong enough to support statements about the regimes that were chosen to be "deliberately hard" (resonance, strong reaction).

---

## 6. Ranked weaknesses

Ranking is from the viewpoint of a strong Q1 journal in computational science. "Fatal" means: the paper cannot be accepted as a methods paper unless this is fixed or the claims are reframed. It does not mean dishonest.

### Fatal

**F1. The central premise (slow simulation) is untested, and the one test is not a test.** (`s6d_confirm.tex`, "An expensive solver", Table 11; abstract; conclusion.)
`lshape_fine_L1` is the Stage 6 problem `lshape_L1` on a mesh refined seven times: same parametrisation (p=4), same 130 probe outputs, same input hash-seed protocol. The learning problem is the same function up to a 5.9% median (15% max) discretisation difference, which I measured by solving the coarse problem on the fine problem's test inputs. So the surrogate-selection result on it (regret 1.3, forecast failure) is a re-run of a seen problem with 800x more time per run; nothing about selection or forecasting depends on solver cost. The "break-even" is `N + t_tool/t_sim` by construction, i.e. the experiment measures a ratio of two clocks. The paper says "a measured trade-off"; the information is arithmetic. The title ("a Slow Simulation") and the framing ("hours-long simulations that motivate surrogates") remain unsupported by any simulation that is slow, with a genuinely different cost/accuracy trade-off (e.g. where a fine-mesh run is itself the reference and a coarse run is the cheap alternative, which is the competitor a practitioner actually has).

**F2. After Stage 7 the contribution that is left is thin and unsupported by a competitive baseline.** (abstract; introduction contributions 1 and 2; conclusion.)
Held-out evidence: the forecast does not meet its criterion (58%; 68% pooled; optimistic bias), the basis flag fired in none of 72 fits while missing 13 fits where it should have (recall 0/13), H1c fails, the reach classification is no better than carry-forward at 1%. What passes: near-oracle selection from a pool of seven classical models, which a fixed GP matches within 10% (hindsight) or loses 40% (LOPO), on smooth problems. There is no comparison with any generic selection or ensembling baseline (stacking or averaging the pool; marginal-likelihood selection; an AutoML system such as auto-sklearn or AutoGluon-Tabular on the POD coefficients; a single multi-output GP with ARD), no comparison with current operator-learning surrogates (DeepONet/POD-DeepONet, FNO, PCA-Net), and no problem with a large number of outputs, time dependence in the surrogate target, or N above 1024. A referee will write: "cross-validated model selection over a small pool is standard practice; what is new here, and is it validated?" At present the honest answer is "a pre-specified benchmark and a useful negative result about forecasting". That is publishable somewhere, but the abstract and contribution list must say so, and a Q1 methods journal will ask for the missing baselines.

### Major

**M1 / W1. Helmholtz is ill-posed as a surrogate task and carries much of the Stage 7 narrative.** See section 5. Locations: Table 8 ("several resonances" is false: one double eigenvalue); "Held-out result" item (ii) and the abstract ("in particular on wave problems"); "A network in the pool" (helmholtz_L1 0.64 to 0.36 from three noisy seeds, 0.69/0.27/0.25); Table 10. The tool has no guard: it should warn when the best cross-validated error exceeds, say, 0.5 ("no pool member is usable"), and the paper should report the Helmholtz results as "all models fail", not as regrets. The mean-of-per-sample-relative-error metric is also dominated by near-resonant samples; a reviewer will ask for a median or a pointwise-norm metric, and for a damped (complex-shift or absorbing) variant.

**M2 / W2. "Held-out" is weaker than it sounds.** The authors designed, chose and ran the problems after seeing Stage 6; they come from the same library, the same data protocol, with the same 4096/1000 pool/test split; the "four new families" overlap the classes of the earlier 36 own-solver problems (Table 4: waves/acoustics, spreading fronts and reactions, pollutant carried by a flow) so they are new in solver but not in physics; six of eight are in the smooth GP regime. Eight problems, three seeds; seeds share the pool and test set and nest their training sets; at N=1024 training sets are a quarter of the pool. Verdicts rest on point estimates against thresholds with intervals that cross them (H1b and H1c problem-level intervals contain 1.0; B1 contains 70%; the share-of-problems interval for H1a has lower limit 53%). The paper acknowledges most of this in limitations 2 and 3, but the section heading "Held-out confirmation" and the sentence "supports these four claims beyond the eight problems on which the tool was developed" overstate.

**M3 / W3. Selective headline numbers.** (a) "six of the eight verdicts" is not what Table 9 shows (5 of 7 evaluable; item 41). (b) Abstract and conclusion quote the pooled forecast number (68%, 96 cases) where the pre-specified held-out number is 58% (28 of 48), and the two batches differ sharply (77% on the developed-on problems, 58% held out; at N0=64, about 92% vs 54%), which is itself informative: the result is consistent with a forecast that works on the problems it was developed on and not elsewhere (not proven by these data). (c) The held-out interval printed is the narrower case-level one. Each choice is individually defensible; together they move every headline in the favourable direction. The abstract should lead with the held-out number.

**M4 / W5. Incomplete accounting of mispredictions and of negative diagnostics** (4.1, 4.2): B2 and helmholtz_L2 predictions wrong but not listed; H3 recall 0/13 not reported though Stage 6 reported recall; the B2 baseline is the wrong reference.

**M5 / W4. W1/W2 for the network in the pool are close to vacuous.** The network was selected in 5 of 24 fits and in 2 of 8 cells (helmholtz_L1 and reacdiff_fe_L2). In the other 6 cells the enlarged pool selects exactly what the default pool selects, so W1 (regret against the enlarged pool) differs from the default-pool regret only through the oracle, and W2 passes automatically whenever the network is worse than the tool, which it is by a factor 1.2 to 27 in those cells. The informative content is two cells (one pass, one fail on W2). The claim "the enlarged pool met both of its criteria" is true but carries little information; "helped" rests on two problems, one of which is Helmholtz.

**M6 / W6. The expensive-case forecast and baseline (E7).** (a) "Better than always using one Gaussian process (4.4e-3)": the fixed GP is `pod_gp[matern52, r=32]`, among the weakest of the seven members at N=256 (3.6e-3 in seed 0). `pod_gp[rbf, r=32]` (5.8e-4 in seed 0) is the oracle member in all three seeds and beats the tool (8.2e-4). The comparison therefore shows that kernel choice matters and that the tool picks a good kernel, not that it beats a fixed GP. (b) The forecast ratios (1.25, 2.11, 3.14) are all above 1, i.e. the forecast was **pessimistic**, opposite to the "tends to be optimistic" narrative used for the 48 held-out cases; the text says "all too high" without noting that the direction reverses. (c) The forecast is for the candidate selected at N0=64, not the candidate finally selected (seed 0: forecast target 4.1e-3, final selected model 5.8e-4); a 45x drop between N=64 and 256 means the learning curve is far from a power law, which is the likely reason. (d) Three seeds, and N=256 of a 512-run pool, so the seeds are strongly dependent; "regret <= 2 at both N" and "forecast 1 of 3" are anecdotes.

**M7 / W7. Neural baseline.** The tuned MLP is 3x to 30x worse than the tool on most problems (median tool/network ratio 0.32 held-out, 0.56 at N=256 over 16 problems). A referee will read this as a weak network baseline, not as a strong tool. The stronger search (48 trials, depth 2-5, width up to 512) is worse than the standard network on helmholtz_L1 (x4.15) and advdiff_cell_L1 (x1.31) and in 17 of 48 seed-level comparisons, which indicates validation overfitting with 20% of 256 points held out; this is not discussed. The statement "a network tuned further could do better" is true but leaves the 'is the benchmark's NN finding robust' question open. No modern operator-learning baseline is included.

### Minor

* m1. Table 8: "several resonances" (see above). Also "near resonance" for L1: the pole sits inside the range.
* m2. Inconsistent counts for the network-in-pool benefit across abstract ("one of the two wave problems"), results ("two problems") and limitation 5 ("one of eight further problems").
* m3. Limitation 1 says "All 44 problems ... the sixteen problems solved by third-party code" but the eight new problems are outside the 44-problem suite (`problems.py` says so explicitly); 52 problems are used. The title says 44-problem.
* m4. Conclusion: "the tuned network beat it by more than 25% in only 6 of 32 cells". "It" is ambiguous (the preceding noun is the fixed Gaussian process). The sentence means the tool.
* m5. The "worst case" regret is a cell mean (see 4.1); report the per-job worst (12.1) and the absolute error (>1).
* m6. H5 6 of 8 depends on one problem at y = 0.115 vs threshold 0.10; 5 of 8 without it. Mention.
* m7. `test_advdiff_mesh_convergence_and_positivity` does not test positivity; the Newton test named "converged residual" does not evaluate a residual; no solver has a convergence flag. Cheap to fix.
* m8. The tool time in the cost table includes `refit_all=True` (evaluation only). Report the time without it.
* m9. Addendum 7.4's statement about Stage 6 S3 ("only just met") is wrong; note it in the deviations or the supplement.
* m10. The introduction's "Gap" sentence ("do not give ... a validated procedure") should be reworded now that the forecast is explicitly not validated.
* m11. The N=64 break-even (70) is quoted next to a 3.7% error; add the error beside each break-even value.
* m12. The "benchmark's own selection" (five methods, 8 trials) and the tool (7 members, 4-fold CV) have different tuning budgets; H1c compares different effort levels in both directions. State it.

---

## 7. Is the contribution still adequate? What a Q1 referee would demand

As a methods paper: no, not yet. The new data make the paper more credible and less impressive. The strongest sentence the evidence supports is: "Cross-validation over a small pool of classical POD+GP/KRR/full-field GP members picks a near-oracle member on smooth parametric problems (median regret 1.04 on eight held-out problems), and a fixed GP is almost as good; the error forecast is unreliable beyond a 4x extrapolation and the basis flag is unproven". As a pre-specified, honestly reported benchmark with open code it is useful, and the process documentation (freeze, deviations, mispredictions) is the best part. A referee would demand:

1. A genuinely expensive case: either a real simulation, or a convincing proxy where the cheap alternative is a coarse-mesh run, with the full cost model (all runs including validation and test runs, parallelism, prediction cost, and error at equal cost).
2. Baselines: a generic selector/ensemble (stacking/averaging of the same pool; AutoML on the POD coefficients), a multi-output GP with ARD, and at least one operator-learning method run with a competent tuning budget (DeepONet/POD-DeepONet, FNO or PCA-Net), plus a PDEBench subset.
3. Fixes to the evaluation: a damped Helmholtz variant; a robust error metric (median, or relative to pointwise field norm); more than three seeds with independent pool/test draws (the 4096/1000 split is shared); inference at the problem level only, with 8 problems presented as 8 data points.
4. An honest account of what the forecast is for: either improve it (error-floor model, calibrated interval, test on held-out problems) or drop it from the headline.
5. A guard for the failure regime (no usable model), which the data show the tool lacks.
6. A bigger or different held-out set: ideally problems chosen by someone else (for example from a public benchmark) or chosen by a rule fixed before looking.

---

## 8. Concrete fixes (ordered by value for effort)

1. Replace "\SvMetCount of the eight verdicts" by "five of the seven evaluable criteria (H3 not evaluable)"; recount via the table, and have the macro derive from table rows.
2. In the abstract and conclusion state the held-out forecast result first (28 of 48, 58%, interval 42% to 77% at problem level) and the pooled one second; change the held-out interval to the problem-level one; add "not distinguishable from the 70% threshold".
3. Add a small table "Predictions of addendum 7.4 vs outcome" including B2 and helmholtz_L2; add the H3 recall (0 of 13) to the text and the discussion; state that addendum 7.4's S3 remark was wrong.
4. For B2 add the carry-forward baseline (100% / 79%) next to the majority baseline.
5. Correct Table 8 ("one double resonance at k^2 ~ 49.3"); describe Helmholtz as undamped with a pole inside the range; report that all models have errors of 0.25 to 3 there; add a column or note "no usable model" instead of regrets; add a tool warning when the best CV error exceeds a stated level; consider reporting H1a/H1c with and without Helmholtz.
6. Reword F1 honestly: "the same problem as lshape_L1 on a fine mesh; it tests the cost accounting, not selection or forecasting". Report break-even as `N + t_tool/t_sim`, show the tool time without `refit_all`, and put the error beside each break-even.
7. In E7 replace "better than always using one GP" by a statement that includes the best fixed member (`pod_gp[rbf,r=32]`, 5.8e-4 to 6.7e-4); say that the forecast was pessimistic here, opposite to the held-out pattern; report forecast target (the N0=64 candidate) vs the final model.
8. Make the network-in-pool wording consistent (two problems; three seeds; W2 informative in two cells) and drop "helped where networks win" from the conclusion.
9. State in the abstract that the "fixed member" comparison is with a hindsight-chosen member, and give the leave-one-problem-out figure (1.44, 71%).
10. Fix limitation 1's counts; name total problems (52) or keep "44" only for the original suite; clarify the ambiguous "it" in the conclusion.
11. Strengthen tests: add a Helmholtz test inside the resonant regime against the analytic pole; add a positivity assertion to the advdiff test; add a Newton convergence flag/assert; add a sector-sensitivity test to `disc_elast`.
12. Longer term (for the venue): items 1 to 6 of section 7.

---

## 9. What I could not verify

I did not refit any surrogate, so I cannot independently check that the stored `test_err` values are what the code would produce now (review 03 reproduced Stage 6 bit-for-bit; Stage 7 code is unchanged since the freeze, so the same holds in principle). I could not verify the claim that no run started before the freeze beyond file timestamps and commit order (the repository is self-hosted). I did not re-audit the literature.
