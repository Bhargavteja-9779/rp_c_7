# Final audit (2026-11-06) — written by the AI research assistant after four simulated review rounds by fresh-context AI agents (not human reviewers)

## Readiness decision: **conditionally ready — for a methodology/software venue, not for a venue that expects a validated general selection method**
Conditions: (1) human authors named, all numbers/claims/citations checked by them, and independent human review obtained; (2) journal and template chosen, guidelines and page limit checked; (3) archive DOI created; (4) the authors accept the limits below. No acceptance outcome or time is predicted or promised. Stage 7 (held-out confirmation) made the paper **more credible and less impressive**: some claims held, several did not, and the text now says so.

## What is established
* All headline numbers were recomputed from raw per-job JSON by independent agents (review 01: 24/24; review 03: all, plus bit-identical re-runs of the tool in a fresh clone; review 04: about 44 Stage 7 numbers recomputed from the raw files, three wording/count errors found and fixed). 67 benchmark tests and 11 tool tests pass; the paper builds with 0 undefined references, 0 LaTeX errors, 1 trivial overfull box per document; no typed numbers outside the allow-list.
* **Held-out confirmation (Stage 7, tool frozen and criteria + predictions committed before any fit; 8 further scikit-fem problems from 4 new families):** selection median regret 1.04, 23 of 24 cells within a factor 2 (worst cell 5.2, worst job 12.1, both on an undamped Helmholtz problem where no model is usable); not worse than always-GP (0.97); tuned network better by >25 % in 2 of 16 cells; reduced basis clearly better on 6 of 8 (predicted: not met). Pooled over 16 problems the same picture.
* **Did not hold:** the error forecast (28 of 48 within a factor 2, 58 %; 68 % pooled; problem-level interval contains the 70 % threshold; optimistic on the held-out problems, pessimistic on the expensive case); the comparison with the benchmark's own selection among methods that include networks (not met in either batch; without the Helmholtz problems it would be met — post hoc); the basis flag never fired (recall 0 of 13 fits where a full-field model was better); the reach-target classification is no better than a carry-forward rule at 1 % and only 9 points better at 0.1 %.
* Extra Stage 7 arms: a tuned network in the pool (meets its criteria, changes the result on 2 of 8 problems, 431 s per fit; offered as `--with-network`); a larger network search (better than the standard network on 12 of 16 problems, wins >25 % over the tool on 4 vs 3; tool's median error still about half the network's); an expensive-solver proxy (the first plate problem on a fine mesh, 1.5 s per run; break-even about 335 predictions, about 309 without the evaluation-only refit; forecast criterion not met).
* Failures, wrong predictions and post hoc analyses are in the main text (prediction table), the supplement (deviations V14, V15; pre-specification record) and the claim-evidence matrix (38 claims).

## Risk ratings (honest)
| Area | Risk | Why |
|---|---|---|
| Novelty | **High** | classical pool; main finding (GP/kernel hard to beat on smooth problems) known; novelty is the procedure, the controls and the evaluation; related-work search limited; no AutoML/stacking, ARD multi-output GP or operator-learning baseline; no public benchmark |
| Scale | **High → Medium-High** | 16 third-party problems from 8 families (was 8 from 4); 44 own problems; cells within a problem are not independent (problem-level intervals given); 3 seeds share pool and test set |
| Data | **High** | all simulated; fast solvers; the only slower case is a finer mesh of an already used problem (tests cost accounting, not selection); two held-out problems are undamped Helmholtz on which no model is usable; real check uses scalar noisy outputs |
| Statistics | Medium | criteria met at their limits in places; pooled thresholds are not rescaled (numbers only); Holm over few tests; B1 interval contains its threshold |
| Baselines | Medium | network tuned up to 48 trials, depth 5, width 512 on one core; larger budgets untested; H1c compares different effort levels |
| Contribution strength | **High** | after Stage 7 the evidence supports: near-oracle selection among classical members (a hindsight-fixed member does almost as well; a leave-one-problem-out fixed member does worse), usable reach-target classification at coarse targets; it does **not** support a validated forecast or flag |
| Registration / process | Medium | self-hosted git history (freeze commit a096980); interim result commits are not run-start times; several post hoc stages labelled; AI-agent reviews only |
| Writing | Low–Medium | plain style, numbers from macros (lint clean); length about 31 pages plus references (journal limit unknown); placeholders remain |
| Ethics / disclosure | Low | no human/animal subjects; public CC BY 4.0 data; AI involvement disclosed |
| Fit with the journal | **High / unresolved** | no verified Q1 journal with an observed ≤ 72-day acceptance history; see `audit/final_journal_decision.md` |

## Main remaining rejection risks (from review 04, §7)
1. "Thin contribution for a methods paper: the forecast and basis flag are unproven; selection among classical members is near a fixed GP." 2. "No genuinely expensive simulation; the cost case is a proxy." 3. "No comparison with generic selectors/AutoML, operator learning or a public benchmark." 4. "Two held-out problems are ill-posed as surrogate tasks; the tool has no 'no usable model' warning." 5. "Entire pipeline and reviews AI-made; no human accountability yet."

## What would remove the removable weaknesses (not done; needs a decision or resources)
A damped Helmholtz variant and a 'no usable model' warning (tool change, then a new frozen evaluation); a stacking/ensemble selector and an operator-learning baseline with a competent budget; a PDEBench subset; a real slow simulation with the full cost model; more seeds with independent pool/test draws; an improved forecast with an error-floor model and a calibrated interval, tested on held-out problems.

## What the authors must do (not done by the assistant)
Author names, affiliations, corresponding author, funding, competing interests, ethics statements, date; choose journal/template, check page limit and guidelines; create a public repository/archive DOI and fill the availability statement; approve the submission (all authors); decide whether to add the items above before submission; obtain human review.
