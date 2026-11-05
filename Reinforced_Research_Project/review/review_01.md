SIMULATED REVIEW (AI agent, not an external reviewer)

# Review 01: "Choosing a Fast Stand-In for a Slow Simulation: a Selection Tool and a 44-Problem Study"

Reviewer stance: hostile but fair. Branch claude/happy-bell-9xorxs. Reviewed 2026-11-05.
Scope: paper/main.pdf (text extracted), paper/supplement.pdf, addenda v3.0 and v3.1, deviations_v2.md (V9, V10), raw per-job JSON in results/raw_exp6T, raw_exp6C, raw_exp6S, raw_expR, git history, results/s6 analysis code.
Method: every number in section 1 was recomputed by my own script from the raw per-job JSON. I did not read results/s6/*.json or macros.tex for the recomputation, only to compare afterwards. The scripts are in the session scratchpad: recompute.py, rv2.py, rv_nn.py.

## 1. Recomputation from raw per-job JSON

Cells are instance x N, with the geometric mean over 3 seeds, as in the paper.

| # | Quantity | Paper claims | Recomputed from raw | Match |
|---|---|---|---|---|
| 1 | H1a median regret (24 cells) | 1.00 | 1.000 | yes |
| 2 | H1a share of cells with regret <= 2 | 100% | 24/24 (max regret 1.18, convdiff_L1 N=64) | yes |
| 3 | H1a random-pick null | median 3.77, 38% within 2 | 3.770, 37.5% | yes |
| 4 | H1b median ratio vs always-POD+GP | 0.85 | 0.847 | yes |
| 5 | H1b better / worse by >10% | 15 / 1 | 15 / 1 | yes |
| 6 | H1c median ratio vs benchmark selection | 1.01 | 1.009 | yes |
| 7 | H1c better / worse by >10% | 11 / 9 | 11 / 9 (4 ties) | yes |
| 8 | H1c worst cell | 2.2 (heatcomp_L2, N=1024) | 2.19 | yes |
| 9 | H2 (B1) within a factor 2, both N0 | 37 / 48 | 37 / 48 | yes |
| 10 | H2 by N0 | 92% for N0=64, 15/24 (62%) for N0=256 | 22/24 and 15/24 | yes |
| 11 | H2 too low / too high by >2x | 7 / 4 | 7 / 4 | yes |
| 12 | H2 actual error inside the (low, high) band | 12% | 12.5% | yes |
| 13 | B2 reach 1% from N0=256 | accuracy 100%, majority baseline 75% | 24/24; actual reached 18/24, so baseline 75% | yes |
| 14 | B2 reach 0.1% | 88%, baseline 50% | 21/24 = 87.5%; actual reached 12/24, predicted reached 15 (all 3 errors are over-optimistic); baseline 50% | yes |
| 15 | H3 flagged "cells" and verdict | 15 flagged, 15 better (100%) | 15 flagged seed-jobs, 15 better. These are 5 distinct (problem, N) cells x 3 seeds. | numbers yes, "cells" is mislabelled (objection M3) |
| 16 | H4 tuned network better by >25% (tool/net > 1.25) | 4 of 16 | 4 of 16 (heatcomp_L2 at 256 and 1024, lshape_L2 at 256 and 1024) | yes |
| 17 | H4 median tool/net ratio; tool better / net better by >10% | 0.34; 11 / 4 | 0.338; 11 / 4 | yes |
| 18 | Run times | tuned net 146 / 429 s; tool 112 / 312 s | 146.4 / 429.3 s; 111.7 / 312.1 s | yes |
| 19 | H5 reduced basis clear at N=1024 | 3 of 8 | 3 of 8 (convdiff_L1, heatcomp_L1, lshape_L1); the same 3 with the test-oracle definition | yes |
| 20 | Real data R1 median regret | 1.04 | 1.039 | yes |
| 21 | Real data R2 not worse than always-GP | 5 / 6 | 5 / 6, but 2 of the 5 are exact ties (identical selection, airfoil N=256 and 1024) | yes (see m4) |
| 22 | Real data R3 net better by >25% | 0 / 6 | 0 / 6 | yes |
| 23 | Real data R4 within a factor 2 | 9 / 12 | 9 / 12 | yes |
| 24 | Table 5 spot checks (convdiff_L1 256 tool 4.2e-4, net 2.4e-3; heatcomp_L2 1024 net 3.6e-2) | as printed | match | yes |

Verdict on arithmetic: all 24 headline numbers reproduce. I found no numerical errors. The objections below concern what the numbers mean, not whether they are right.

## 2. Pre-registered criteria against the addendum text

The paper's verdicts follow from the addendum criteria and from the numbers.

| Criterion | Addendum | Observed | Verdict follows? |
|---|---|---|---|
| S1 (H1a) | median <= 1.5 and >= 75% of cells <= 2 | 1.00, 100% | yes |
| S2 (H1b) | median ratio <= 1 | 0.85 | yes |
| S3 (H1c) | median ratio <= 1 and better > worse by >10% | 1.01 (fails the median) and 11 > 9 | yes, "not met" is correct and is reported |
| S4 (H4) | strong net better by >25% in at most 4 of 16 | 4 | yes, met at the limit |
| B1 (H2) | >= 70% of 48 | 77% | yes (see M5 for the weight this deserves) |
| B2 (H2) | >= 75% for 1% and for 0.1% | 100%, 88% | yes |
| F1 (H3) | evaluable if >= 5 flagged cells; >= 75% have full-field better by >10% | 15 flagged seed-jobs = 5 cells exactly, 100% | technically yes; borderline evaluability (M3) |
| PT (H5) | reduced basis clear on >= 5 of 8 | 3 | "not met" is reported |
| R1-R4 (v3.1) | as stated | all met; R4 predicted to fail, did not | yes, and the wrong prediction is reported |
| Addendum 6.4 (retrospective run of the tool on the 36 earlier problems at N=256, seed 0, descriptive table) | promised in v3.0 | no table, no script output and no mention anywhere in the paper or supplement (grep over sections, tables, results/s6, code/experiments) | not delivered, and no deviation entry (M6) |

### Chronology (git)

- a99c2c6, 2026-11-02 08:40: addendum v3.0 committed with the scikit-fem problems, the tool core and the strong-network module.
- 781e318, 2026-11-02 08:50: the V9 fix to the leave-one-out computation and the length-scale grid, committed 10 minutes after the addendum.
- 2619b07, 2026-11-03 17:29: addendum v3.1 committed with the real datasets and the `metric` option.
- First results commit for any Stage 6 or real-data experiment: a88ad5f, 2026-11-04 13:14 (T and R).
- C results: commits 1dc799e / de16184, 2026-11-04 14:06.
- S results: 9ebaf04, 2026-11-04 17:39.
- Protocol-before-results ordering therefore holds for T, C, S and R.
- Diff of the surroselect code between 781e318 and 2619b07: the only changes are the `metric` option and `make_candidate`, which are default-preserving. I found no silent change to the pool, grids or selection rule between registration and the C run. The later 9ebaf04 change (V10 pickling) came after C and S had run. This is consistent with the paper.

Problems with the paper's account of timing:

1. The prereg-order table (Table S1, `audit/prereg_order_check.json`) lists only the earlier stages (A, D, B, A2, E, A3, G, F, H, G3). It has no row for T, C, S or R, which are the experiments the paper's headline claims rest on. Section 5.4 sends the reader to "commit hashes in Supplement S2" for these hypotheses, and the hashes are not there.
2. The paper says "a smoke test of the tool on one of them preceded the registration" (introduction, contribution 2) and "found in a smoke test on one independent problem" (limitation 2). Deviation V9 says test errors were seen for all pool members on lshape_L1 (seed 0, N=64 and 256) and for the KRR and polynomial members on heatcomp_L2 and convdiff_L1. That is 3 of the 8 problems, not one. The main text understates this.
3. The addendum itself states "No error of any surrogate on these problems had been seen." V9 admits this was false. The correction is in the supplement only. The paper does not say that the registered text was inaccurate when it was written.
4. The V9 fix (new KRR length-scale grid) was a design change made after test errors were seen, committed after the registration. The paper says the criteria were unchanged. That is true, but the tool the criteria evaluate was modified in light of test errors on the same problem family.
5. Table S1 measures order of commits, not order of execution. The Table S1 caption says so. The "Hours before" column is 0.05 and 0.08 for H and G3, which is only a git-order check. The T runs started about 8 hours after registration (file mtimes, Nov 2 ~16:48; mtimes are unreliable in this container). C ran after the T results had been seen (Nov 4). The paper does not say that the tool's evaluation ran after the legacy-method results, including the failed PT prediction, were known. The pool was not changed, so I judge this minor.

## 3. Objections

### CRITICAL

None. All headline numbers reproduce, the negative results are reported, and no protocol change after results was found. The objections below are serious enough to require major revision, but none is fatal.

### MAJOR

**M1. The H1a "oracle" headline is weak: a constant rule passes the pre-registered criterion, and the stated null is a strawman.**

Evidence (my recomputation, not in the paper):
- Always choosing the single pool member gp_full[rbf] gives median regret 1.085 and 75% of cells within a factor 2. That meets the pre-registered S1 criterion exactly (median <= 1.5, >= 75% <= 2).
- gp_full[matern52] gives 1.14 and 75%.
- The paper's null is a uniformly random pool member (median 3.77, 38%). That null includes members known to be poor (POD+GP rank 8, polynomial).
- The tool selected the oracle member in 56 of 72 jobs and selected a gp_full variant in 37 of 72.
- Value added over always-gp_full[rbf]: median ratio 0.91, better by >10% in 12 of 24 cells, worse in 2. This is real but modest, and it is not reported.
- The abstract says "within a factor 1.18 of the oracle in all 24 cells (median 1.00)" without saying that "oracle" means the best of the 7 pool members by test error. A reader will assume the oracle is the best of any method.
- The oracle is chosen on the same 1000 test inputs for every pool member and every seed. That is disclosed ("by test error, upper bound"), but the abstract does not repeat it.

Action: report regret against the best fixed pool member and against always-gp_full. Define "oracle" in the abstract. Present H1a as "the tool is not worse than the best fixed choice and is clearly better than random". Drop "far from chance" as evidence of value.

**M2. The "strongly tuned network" is not demonstrably strong, so H4 "met at the limit" carries little information.**

Evidence:
- The paper states the budget fairly in section 5.3: 2x the trials, 4x final epochs, L-BFGS, float64. It also discloses the restricted search space (depth 2-4, width 64-256, 16 trials) and that no ensembling is used. This is not hidden, and the extra training budget favours the network, so the direction of bias is conservative for the tool.
- But the label "twice the budget" in the abstract understates the network's training budget. Epochs are 4x, plus L-BFGS, plus float64, against single-precision Adam for the legacy networks.
- The tuned network improves on the legacy validation-selected networks in 15 of 16 cells, by a median factor of about 0.6. At N=1024 on the smooth problems it still has errors of 2e-3 to 3.6e-3 (lshape_L1 3.6e-3, convdiff_L1 2.1e-3, heatcomp_L1 2.1e-3), against 1e-4 to 1e-5 for the tool. The paper's own Exp F showed floors of about 2e-4 are reachable with stronger training. So the "strong" network is probably under-trained, and H4 says little about what a well-tuned network would do.
- The network loses where the tool is good and wins on exactly two problems (heatcomp_L2, lshape_L2, 9 and 7 inputs). The 4 "wins" are 2 problems x 2 budgets, not 4 independent results.
- H4 is met exactly at the limit. The heatcomp_L2 N=256 ratio is 1.36, only 9% above the 1.25 line. Wilson 95% interval for 4/16 is roughly [10%, 50%]. The Holm p of 0.63 is non-significant, which the paper does report.
- Both the tool and the network were designed by the authors, who have known results; the network was given no human tuning beyond a pre-set search.

Action: rename to "tuned network (16-trial Optuna)". State in the abstract that the budget differs in epochs, optimiser and precision as well as trials. Report H4 as 2 of 8 problems. Add a stronger network arm (ensembles, wider search, longer training), or say plainly that H4 does not bound what networks can do.

**M3. The H3 basis-flag evaluation counts seed replicates as cells, reports only precision, and the flag adds little over selection.**

Evidence:
- "15 flagged cells" are 15 seed-level jobs = 5 distinct (problem, N) cells: convdiff_L1 N=1024, convdiff_L2 N=1024, heatmove_L1 N=256, heatmove_L1 N=1024, heatmove_L2 N=1024. They come from 4 problems. The paper's own cell definition is a geometric mean over seeds. At cell level the evaluability threshold of 5 is met exactly.
- The flag was never raised on 6 of the 11 cells where the full-field GP beats the best POD member by >10%. At job level, 17 of the 32 jobs in which full-field is better by >10% were not flagged (recall about 47%, never reported).
- In all 15 flagged jobs the tool already selected a gp_full member, so the flag did not change any decision.
- The "best POD-based" and "best full-field" comparisons use the test-oracle minimum over members (5 POD members against 2 full-field members). The main text calls it "best POD-based member" without saying "by test error".
- The Discussion says the tool "flagged the cases in which the POD basis limited accuracy and a full-field model was better", which suggests recall the data do not support.

Action: report cells, not jobs. Report recall and the 17 unflagged cases. State that the comparison is by test error. Say that the flag adds no decision beyond selection on these data.

**M4. Cell-level statistics overstate precision, and the independence caveat is not carried into the verdicts.**

Evidence:
- Limitation 3 admits that the 24 cells are not independent, but Table 4 still reports a Holm p of 0.003 for H1a and a Wilson interval treating 24 cells as independent.
- The effective sample is 8 problems, with seeds sharing the pool and test set and nested training subsets.
- At the problem level, 8/8 problems have all cells within 2, and the Wilson 95% lower bound is about 68%, below the 75% threshold. So "H1a met" is not statistically supported at problem level.
- A problem-cluster bootstrap I ran gives: H1c median ratio interval [0.62, 1.30]; H1b [0.62, 0.98] (the original is [0.59, 0.97]); H2 share interval [65%, 90%]. The H2 point is above 70%, but P(share >= 70%) is only about 0.86 over resamples.
- B2 0.1%: 21/24 against 75% has exact one-sided p = 0.115. This is not tested or flagged in the paper. B2 1% (24/24) has the same pseudo-replication.
- Holm is applied to only 3 tests (S1, B1, S4), while 7 hypotheses and 4 real-data criteria are reported. This is declared as "the three that admit one", which is fine. But "met" labels next to p = 0.363 and 0.63 invite over-reading.

Action: use problem-level (cluster) intervals as the primary ones. Say in Table 4 that the verdicts are descriptive of 8 problems. Add a p-value or Wilson interval for B2.

**M5. H2 forecast: the pooled criterion hides a failure in the practically relevant regime.**

Evidence:
- Pooled 77% (37/48) is above the 70% threshold. But N0=64 -> 256 gives 22/24 (92%) and N0=256 -> 1024 gives only 15/24 (62%), below the threshold. A practitioner with 256 runs asking about 1024 is the case the paper itself motivates, and the criterion fails there.
- Seven forecasts were too low (optimistic) by more than a factor 2. All 3 reach-0.1% misclassifications are optimistic (predicting reachable when it is not).
- The abstract does give the 62% figure, which is honest. But "H2 met" and the Discussion's "usable forecasts ... when starting from 64 runs" frame this positively.
- The forecast range contains the actual error in only 12% of cases. This is reported.
- The interval [63%, 87%] includes the threshold, which the paper notes.

Action: state that the pre-registered pooled criterion was met and the criterion applied to N0=256 alone would not be. Frame B1 as "met in aggregate only because of N0=64".

**M6. Process and registration.**
- A pre-registered descriptive item (addendum v3.0 section 6.4: a retrospective run of the tool on the 36 earlier problems at N=256, seed 0) was not delivered or reported. There is no deviation entry for dropping it. It would have been the one in-sample/out-of-sample contrast for the design-knowledge concern in limitation 2.
- Table S1 omits all Stage 6 and real-data experiments (see section 2 above). The introduction and section 5.4 imply that hashes are listed there.
- The introduction says smoke-testing touched "one" problem; V9 says three (section 2, point 2).

Action: run and report the retrospective table or log a deviation. Extend Table S1 with the actual commits (a99c2c6 / 781e318 for T, C, S; 2619b07 for R). Correct the "one problem" statement.

**M7. "Independent problems" is solver-independence only, and the 44-problem study is not a sample.**

Evidence:
- The eight problems were specified by the authors after seeing the 36-problem results (addendum motivation), so they are third-party-solver problems, not third-party problem choices. The title, abstract and section headings say "independent".
- Section 6.1 says 8 of the problems added earlier were included because "we expected the Gaussian process to do well". The 44 problems were assembled in stages, partly selected to test expected GP wins. The counts "13 of 24 reduced basis clear at N=1024" describe this set only.
- The abstract says the 44-problem study "explains where each model family wins". The mechanism claim in section 6.2 ("largely an advantage of a smooth regressor whose regularisation is searched widely and finely") rests on: D1 pre-registered criterion rejected (narrow KRR 13x worse); wide-KRR control added post hoc after a review, with Table S2 verdict "neither rule met (mixed)" (6.5x and 2.7x median ratios, the GP still ahead); and an unconfirmed pilot diagnostic. "Explains" is an over-claim. The text does say "we did not isolate marginal-likelihood fitting", which should be in the abstract.
- The only strong support is G1 (full-field GP about as good as POD+GP, median ratio 0.95).

Action: replace "independent problems" with "problems solved by third-party code" in title-adjacent text and abstract. Replace "explains" with "describes". Note in the abstract that the mechanism controls are partly post hoc.

### MINOR

**m1. Internal inconsistency.** Section 6.1 says the reduced-basis picture "does not carry over to three of these eight independent problems". The Discussion and conclusion say "five of the eight". With 3 clear reduced-basis wins at N=1024, 5 did not hold (3 network-clear, 2 ties). The sentence in section 6.1 is hard-coded and wrong.

**m2. Two numbers for one control.** The narrow-range KRR control is "median 13 times, 18% within 3x" in the main text (28 combinations, macros KrrNarrowRatio and KrrNarrowShareThree) and "median ratio 14.3; 13% within 3x" in Table S2 (D1). I suspect these are different cell sets, but nothing says so.

**m3. Inconsistent "better/worse" thresholds.** The code uses `r < 0.9` for "better by >10%" (H1b) and `r < 1/1.1` for H1c. The counts happen to coincide here (15/1; 11/9), so no verdict changes.

**m4. R2 "5 of 6" includes 2 exact ties.** In airfoil at N=256 and N=1024 the tool selected the same model as always-POD+GP (ratio 1.000). Strictly better in 3 cells (all ccpp), tied in 2, worse in 1 (airfoil N=64, 1.6% worse). Also, with scalar outputs (m=1) "POD" has rank 1 and gp_full is a plain GP, so the real-data check says nothing about the POD-versus-full-field structure the tool is built around. The paper says "scalar, noisy", but not this specific degeneracy. One airfoil job (seed 2, N=64) has a gp_full test error of 25 and CV error of 4.0, which shows instability that is never discussed.

**m5. S4 operationalisation.** The code counts "better by >25%" as tool/net > 1.25 (a 20% error reduction), which is stricter against the tool than "error 25% lower" (ratio 1.33). Both give 4. This direction is conservative; I note it as fine but undocumented.

**m6. Reproducibility.** Deviation D5 (non-reproducible random-search seeds in earlier stages) means re-runs of earlier results will not be bit-identical. A DOI archive and author/affiliation placeholders are missing, and the acknowledgments say "to be confirmed by the authors". Not a scientific issue, but the submission is not final.

**m7. Related-work table.** Table 1 marks competitors "-" based on abstracts or partial reading, against "This paper" with all ticks. The caption discloses this. It is a weak basis for the "Gap" claim in the introduction.

**m8. Typesetting.** The reference [11] author name is garbled ("Bērzin, š et al." for Bērziņš). Table S2 and the main text both use "H1a" for earlier-stage and Stage 6 hypotheses.

## 4. Hunt checklist

- **Weak baselines / unequal tuning.** Legacy methods get 8 random-search trials on a 20% validation split, whereas the tool gets 4-fold CV over wide grids (including a wide-range KRR grid designed with knowledge of the earlier problems) and a full-field GP the benchmark did not have. So H1b and H1c compare a richer pool against a lightly tuned benchmark. The paper says this (the pool was designed with knowledge of the 36 problems) but never labels H1b as a likely-met-by-construction comparison, since the pool contains POD+GP itself. The tuned network is treated in M2.
- **Cherry-picking of cells or instances.** All 8 instances, all 3 seeds and all 3 N are in the analysis. No cell was dropped. N=64 is excluded from H4 by the pre-registered design (the network was not run there). The qualitative examples use a rule fixed in advance and include two failure cases.
- **Test-set selection / oracles.** Oracle regret uses test error over pool members (disclosed in section 5.3, not in the abstract). H3 uses best-by-test over members (not stated in the main text). The section 6.2 "best network by test error" is disclosed as an oracle favouring the networks. The random-pick null uses test errors. The H5 criterion uses validation-selected members, and the test-oracle version gives the same 3 of 8, so it is robust.
- **Leakage.** I read data_leakage_audit.md, the planted-leak results and the S job code. Inputs for train, test and extrapolation sets come from separate named hashed RNG streams. The tool's fitting, POD, scalers and CV use training rows only. The S job uses unscaled inputs in [0,1] consistently for fit and predict. The planted-leak test is credible (flagged, 20 matches). Remaining issues are those the paper already states: nested training sets, shared pool and test set across seeds. I found no leakage.
- **Statistical errors.** Cells treated as independent (M4). Wilson intervals are computed correctly. The Holm family is small and declared. "Met" with a CI including the threshold is disclosed for H2. The H4 test has the criterion boundary as its null, so p = 0.63 means no evidence either way.
- **Over-claims.** "Explains" (abstract); "independent problems"; "twice the budget"; "oracle" undefined in the abstract; Discussion implies flag recall; the conclusion's "the basis check pointed to full-field models where they were better" is the H3 precision claim again.
- **Claims without a macro or table.** The statements about 15 of 48 verdict changes, 0.47 decade, 83%/99% agreement, and the extrapolation medians come from macros built from earlier-stage JSON, which I did not recompute from the raw files in the earlier-stage directories. I only recomputed Stage 6 and real data. The 0.1-decade tie-band sensitivity counts (6 and 10 network wins at 0.15 and 0.05) are not in a table I could see.

## 5. Integrity rules

- **Citations.** I checked 12 entries against Crossref (8) or arXiv (4). All exist and match author lists, titles, venues and years as given: Batlle et al. JCP 496 (2024); de Hoop et al. JML 1(3) (2022); Mohr and van Rijn, Machine Learning 113 (2024); McGreivy and Hakim, Nat. Mach. Intell. 6 (2024); Williams and Cremaschi, Comput. Aided Chem. Eng. 47 (2019); Mora et al. CMAME 434 (2025); Bhattacharya et al. SMAI-JCM 7 (2021); Dodge et al. EMNLP-IJCNLP 2019 (Crossref); arXiv:2604.00689 (Westermann et al.), arXiv:2604.20061 (Duraisamy), arXiv:2510.23166 (Wyder et al.), arXiv:2006.13706 (Bērziņš et al.). Sources: api.crossref.org and arxiv.org/abs pages. The Westermann abstract does say "no single method is universally superior", and the Duraisamy abstract does say successes sit on "low-dimensional solution manifolds". No invented citations found.
- **Negative results reported.** Yes: H1c not met, H5 not met, PT prediction failed, R4 prediction wrong, forecast too optimistic at N0=256, forecast band coverage 12%, cost exceeds the simulation cost, the pilot diagnostic not confirmed. Not reported: flag recall, the best-fixed-member comparison, and the dropped retrospective run.
- **Post hoc labelling.** Largely done (Exp H, G3, T, C, S called post hoc in motivation in the supplement; the wide-KRR control labelled post hoc in the text). The abstract and the introduction's "pre-registered evaluation" do not mention that the problems, pool and thresholds were designed after the earlier results.
- **AI involvement.** Disclosed, including that the "reviews" were by AI agents.

## 6. Verdict

**Major revision.**

The work is careful and unusually candid: the numbers reproduce exactly, the registered criteria are applied as written, and the failures are reported. The weaknesses are in framing and statistical content:

- H1a is passed by a constant rule and is benchmarked against a weak null.
- H4 uses a network that is probably not strong.
- H3 counts seeds as cells and ignores recall.
- All intervals ignore that only 8 problems exist.
- The N0=256 forecast fails its own threshold.
- A promised retrospective analysis and the Stage 6 commit hashes are missing.
- "Explains" and "independent" over-reach.

None of these is fatal, but together they reduce the evidence for "the tool works" to: it picks well among a small pool on 8 author-chosen problems, and it is rarely clearly beaten by a modestly tuned network. Required actions before acceptance: M1 (best-fixed baselines, define oracle), M2 (relabel or strengthen the network), M3 (cell counts and recall), M4 (problem-level intervals), M5 (state the N0=256 result against the threshold), M6 (retrospective table or deviation entry, Table S1 rows for T/C/S/R, "three problems" in the smoke-test statement), and M7 (wording).
