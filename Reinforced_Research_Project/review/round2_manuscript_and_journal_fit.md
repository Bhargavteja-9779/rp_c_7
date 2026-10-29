# Round 2 review: manuscript quality and journal fit

Reviewer role: independent peer reviewer/editor (computational science and engineering, surrogate modelling).
Date of review: 2026-10-29. Object: `manuscript/Final_Manuscript_v4.md` (and the rendered 8-page PDF), with `Supplement_S1_Technical_Report.md`, `build_v4.py`, `results/`, `audit/final_journal_decision.md`.
No file other than this report was modified. All recomputation used my own script that reads the raw per-job JSON files (`results/raw` of the v1 study, `raw_expA`, `raw_expA2`, `raw_expA3`; 36 problems, 3 seeds each), the cell CSVs in `results/expA_primary/tables/`, and `results/*.json`. Scratch scripts are in the session scratchpad, not in the repository.

---------------------------------------------------------------------

## 0. Verdict

**MAJOR REVISION** (for a journal that accepts a benchmark-style paper; at a method-oriented Q1 journal the likely outcome is desk rejection, see 1.4).

Justification. The experimental core is sound and unusually well documented. Every headline count that is computed (13/8/3 at N=1024; 5/5/14 at N=32; Table 1; Table 2 = 36/36, 27/28, 19/10; CPU times) reproduces exactly from the raw files, and most typed numbers also reproduce. The paper is also honest about several limits (synthetic problems, light tuning, step-count confound, self-hosted preregistration). Its weaknesses are of three kinds. (a) Framing and over-claiming: a title and abstract that promise a practitioner answer ("Do you need a neural network?", "engineering problems", "application types") from 36 textbook PDE benchmark stand-ins and an 8-trial tuning of small MLPs, and a headline mechanism claim ("the GP's edge came mainly from searching its hyper-parameters over a wide range") that the authors' own controls do not support at matched effort. (b) Several typed statements and checklist labels that are wrong, overstated or contradicted by data in the repository (darcylin p=16/32 results; "within about 30%"; "one to two orders after stronger training"; "Strong; seen on three problems"; 4.3 using test-oracle selection while Section 2 says "never on test data"). (c) A headline sample (the 36 problems) that is not a representative sample: 8 of the 36 were selected after the fact because they were smooth (f1 < -2), and 4 more were added as probes, yet counts such as "19 against 10" are presented over all 36 with no breakdown. None of this is fatal; all of it is fixable by rewording, one extra table, and honest scoping. But the paper currently reads as a stronger practitioner recommendation than the evidence allows, and a careful referee will say so. The journal question has no clean answer under the authors' constraints (see section 5): the 72-day acceptance limit cannot be supported by any evidence in the repository except as an observed, survivor-biased history of one very young journal with no impact factor.

---------------------------------------------------------------------

## 1. Contribution and framing

### 1.1 What the contribution actually is
A tie-aware, multi-budget comparison of (best of 3 POD-regressor surrogates) versus (best of 2 direct MLPs) on 36 in-house parametric PDE problems, plus controls that locate the GP advantage and a negative result for a pilot predictor. The supplement is explicit that "we do not claim to be the first to observe that a GP beats a network on smooth problems" (S1 section 6). The main paper never says this plainly. A practitioner reader is left to infer the contribution is a new recommendation, when it is a calibration of a known fact (Batlle 2024, Bērziņš 2020, Westermann 2026 are cited but only in the introduction).

### 1.2 Over-claiming (ranked)

* **MAJOR – Title and subtitle.** "Do You Need a Neural Network?" is a general question; the evidence covers one NN class (small MLPs, 1,500 epochs, float32, 8 random-search trials, no ensembles, no neural operators, no inference-cost accounting) on 1-D/2-D toy-scale problems with outputs of 128-256 values (S1 section 7). The subtitle says "36 simulated engineering problems". They are textbook PDE benchmark families (Bratu, Burgers, KdV, Fisher-KPP, Helmholtz, advection-diffusion, Darcy) solved by in-house code. Suggested title: "Gaussian-process or neural-network stand-ins for parametric PDE simulations? A budget-aware comparison on 36 synthetic benchmark problems". "Engineering" should go.
* **MAJOR – "six types of application" / "application types" (abstract, Sections 1, 3, Table 1).** The six groups are the authors' own groupings of mathematical PDE families (e.g. "Waves, shocks and acoustics" = Burgers + KdV + 1-D wave + Helmholtz; "Thermal runaway (combustion-type)" = the Bratu equation). Nothing was modelled on an application. Section 3 does say "stand-ins ... not field or industrial data", which is good, but the abstract uses "modelled on six types of application" with no such qualifier. Use "six classes of benchmark problem".
* **MAJOR – "mainly" in the mechanism claim (abstract, 4.3, Conclusion).** The abstract says the GP's edge "came mainly from searching its hyper-parameters over a wide range, since kernel ridge with a wide search came within a factor of about 3". The data: at the same 8 trials as every other method, the wide-range kernel ridge is a median 6.5x worse than the GP (q25-q75 3.6-14.8x, only 21% of cells within 3x; `expH_statistics.json`). The "about 3x" figure (2.68x) needs 4x more tuning trials (B=32), and even then only 57% of cells are within 3x. The pre-registered rule D1 (within 3x in at least 75% of cells) was rejected for the registered control, and H-RANGE/H-MLII were "mixed". The isotropic-kernel GP control is a median 1.9x worse than the ARD GP (`expE_statistics.json`), so per-input length-scales alone account for about a factor of 2. Section 4.3 itself concedes "we did not isolate the contribution of the GP's marginal-likelihood fitting". The correct statement is "a wide-range kernel ridge closes most of the gap (median 14x to 6.5x at equal trials, to 2.7x with four times more trials); a residual factor of 2-3 remains unexplained". Also Figure 2 shows only the favourable B=32 variant of kernel ridge; the B=8 variant that matches the other methods' effort (6.5x) is not plotted.
* **MAJOR – the "19 against 10" headline (abstract, Table 2, checklist 4) rests on a selected sample.** I split the 36 by set (recomputed). Problems reaching 0.1%: original 16: reduced-basis 7 vs network 2; Exp A (8): 2 vs 2; Exp A2 (8, selected by the rule "seed-mean f1 < -2", i.e. chosen because POD compresses fast, see `research_design/expA2_selection.json`): 8 vs 5; Exp A3 (4, probes): 2 vs 1. So the 24 problems not selected for smoothness give 9 vs 4 (still about 2:1) and the 8 selected smooth ones add 8 vs 5. The conclusion survives, but the text says "36 problems" as if the sample were a neutral cross-section. Report the split, or report the 24-problem count as primary.
* **MINOR – "far more accurate", "needed fewer simulation runs for high accuracy, and was cheap to build" (Conclusion).** "Cheap" rests on 44 s median CPU time at N=1024 vs 86-139 s for networks, with no hardware, thread or GPU information, and without relating it to the cost of the simulations themselves, which is what a practitioner needs (`fom_seconds_per_solve` is in the raw files but unused). Inference cost is not discussed at all although `t_infer_per_sample` is recorded.
* **MINOR – "smooth" is not defined independently of the outcome.** The recommendation "try a GP first if your problem is smooth with few inputs" is circular: the only smoothness proxy tested (POD decay, f1) failed as a predictor (Section 4.4), and checklist 8 says not to rely on it. The reader cannot know in advance whether their problem is "smooth".

### 1.3 What is missing that an application-oriented audience expects
1. At least one problem or dataset that did not come from the authors' own solvers (e.g. a public benchmark such as PDEBench, or a published FE parametric problem). Self-written solvers, self-chosen families, a self-hosted "preregistration" and AI-agent-only audits give a referee nothing independent.
2. A clear statement of the decision rule: given my p, my N and my accuracy target, what do I do? The checklist gives advice but no decision table. A one-page table (p <= 4 / 5-10 / > 10 by N by target) would be the real practitioner deliverable.
3. Total-cost accounting: simulations plus training plus inference.
4. A stronger neural baseline (more tuning trials, ensembles, POD-DeepONet or FNO). The text concedes this in Section 7, but the conclusion is phrased more broadly than the evidence.

### 1.4 Would an editor desk-reject it?
* At a method-oriented Q1 journal (CMAME, Engineering with Computers per the repo's own title-level evidence that 44 of 47 recent surrogate papers propose new methods; EAAI): probable desk rejection, for (i) no new method, (ii) no real or public data, (iii) the main finding (GP beats lightly tuned NN on smooth low-dimensional problems) is known (Batlle 2024; Bērziņš 2020; Westermann 2026), (iv) most pre-registered confirmatory hypotheses were not supported, (v) whole audit/review/drafting pipeline carried out by AI agents with no human independent review.
* At a benchmark/methodology-friendly venue: it would go to review. The likely editor's first-round questions are listed in section 5.2.
* The main text never states the outcome of the original confirmatory hypotheses (H1a, H1b, H2: not supported; H4a: supported at cell level). Only the supplement does. "Earlier we had read the small-budget results as 'networks win most cases', but most of those were ties" (4.1) is an unexplained reference to a version the reader never saw. A referee who finds the supplement will conclude that the main paper under-reports the negative results. Add a half-paragraph in Section 2 or 4 listing the hypotheses and their outcomes.

---------------------------------------------------------------------

## 2. Findings ranked, with fixes

### CRITICAL
None of the findings below invalidates a computed result. The items I consider close to critical for submission are (C1) and (C2); I have ranked them CRITICAL because each is a statement of fact that the repository contradicts or cannot support.

**C1. Section 5 and Section 4.1 contradict the data for the high-input Darcy problems.**
* 4.1: "For the problems with 16 and 32 inputs the results are not consistent across seeds and we cannot say which family is better there." Section 5: "With 16 inputs (darcyhd_L1) both groups are stuck ... the difficulty comes from the number of inputs, not from the choice of model." Checklist 1: "unresolved for p >= 10".
* Recomputed: darcylin_L1 (p=16) and darcylin_L2 (p=32) are in the 36 problems and are the only 16/32-input problems that are not "darcyhd". darcylin_L1 has y = +0.48 at N=1024 (all three seeds positive: 0.37, 0.60, 0.48), +0.63 at N=256, and the reduced-basis group reaches 0.1% error at N=256 while the network reaches it only at 1,024. darcylin_L2 (p=32) is +0.18 at N=1024 (seeds 0.07, 0.30, 0.16). So with 16 inputs the problem is not "stuck at 6e-2"; the difficulty depends on the problem, not just on p, and the data show a consistent reduced-basis win on two of the four 16/32-input problems. The darcylin problems are named in the Section 5 heading "(darcy, darcyhd, darcylin)" but are never discussed.
* The seed-inconsistent network-win cells at N=1024 in `extrap_and_seed_consistency.json` are darcy_L2 (p=10) and darcyhd_L1 (p=16) only; darcyhd_L2 (p=32) is a tie (-0.07), and darcylin is consistent.
* Fix: rewrite the passage: "At 16-32 inputs the picture depends on the problem: for the 'linear' permeability version (darcylin) the reduced-basis group wins consistently (by 0.2-0.5 decades at 1,024 runs), whereas for the harder darcyhd problems the networks lead by 0.1 decades in seed-inconsistent cells." Drop "the difficulty comes from the number of inputs, not from the choice of model" or support it (it is a causal claim with no control).

**C2. Section 4.3 uses a different, test-based "best network" than Section 2 declares.**
Section 2: "better ... when its best member, picked on held-out validation data and never on test data". But the cell selection "cells where the GP clearly wins" (Exp D/E/G/H, Figure 2, the 14x/6.5x/2.7x/0.95 numbers, "23 of the 52 cells") uses `err_nl_best`, the best network by *test* error (the supplement says "oracle comparator (best network by test error)" under Table 4a). Likewise Exp F's "best-of-F" network variant is chosen by test error (S1 section 7; `expF_verdict.md`). This is conservative for the paper's direction (it favours the networks), but it contradicts a sentence the paper uses to reassure the reader. Fix: state in 4.3 and in the Figure 2 caption that these controls use the best network judged on test error, and that "GP clearly wins" is therefore a stricter criterion than in 4.1; and say that Exp F's improvement is an upper bound. Also note that the cell sets differ across panels (52 cells for the narrow kernel ridge vs 28 for the others), so the 14x -> 6.5x -> 2.7x sequence compares different populations. On the common 28 cells the narrow kernel ridge median is 13.4x (I recomputed), so the conclusion is unchanged, but Figure 2's four boxes should be drawn on one population.

### MAJOR
**M1. Abstract/4.3/Conclusion mechanism over-claim** (see 1.2). Rewrite as proposed.

**M2. Headline counts over a non-representative 36 (1.2).** Add the by-set split or lead with the 24-problem counts; add a family-level count (the 36 problems are 19 families with L1/L2 variants, so the effective n is closer to 19 than 36).

**M3. Section 4.1 contradicts itself on "one to two orders".** "A fair summary is 'up to about three orders of magnitude in the most favourable setting, one to two orders of magnitude after stronger network training'." Recomputed from `expF_cells.csv` at N=1024, the 5 decisive problems after Exp F: bratu_L1 519x, bratu_L2 356x, nlheat_L1 182x, nlheat_L2 109x, burgers_L1 60x (1.8-2.7 decades). The supplement abstract correctly says "about 1.8-2.7 decades". Correct text: "two to nearly three orders of magnitude after stronger training (about 60 to 500 times), and only about 4 to 9 times on darcy_L1 and heat2d_L1".

**M4. The checklist's strength labels are not all justified** (details in section 4 below). In particular item 3 "(Strong; seen on three problems)" is self-contradictory; item 1 "Strong" holds for only 20 of 30 problems with p <= 4 (67%); item 5 combines two experiments and attributes a one-third change rate to all three interventions.

**M5. Cited sources do not all support the sentence they are attached to (section 3 below).** In particular [Hesthaven & Ubbiali 2018] and [Bhattacharya et al. 2021] are neural-network regressors on POD/PCA coefficients, not GP; the supplement says so correctly, the main paper does not.

**M6. Negative confirmatory results absent from the main text** (1.4).

**M7. "Independent AI-agent review" wording.** The reviews and audits were produced by AI agents under the same project (Declarations). Calling one "independent" (Section 2 twice, Section 4.3) overstates it. A referee will also discount "statistical evidence" that cites "audits" done by the generating system. Use "an automated review by a separate AI agent" and do not list it as a form of independent validation. Human verification of every number and citation is required before submission (the Declarations already say this; it should be done, and stated).

**M8. Section 5 "small margin" for heat2d_L2.** "the networks are ahead of the POD-based GP by a small margin" - recomputed y = -0.335 at N=1024, i.e. network error 0.026 vs 0.054, a factor of 2.1, which is the third largest network win among the 24 (largest is 2.8 for fisher_L2, as the paper says in 4.1). Rewrite: "by a factor of about 2".

### MINOR
* m1. Section 5 darcy example: "both groups are stuck at an error of about 6e-02 ... within about 30%". Recomputed at N=1024: reduced-basis 5.8e-2, network 4.3e-2 (the template prints only the reduced-basis value and applies it to both). The ratio is 1.33 (y = -0.125), which is outside the paper's own 25% tie band, and this problem is counted as a network win in 4.1. Say "5.8e-2 vs 4.3e-2 (the network is about 25% lower, just beyond our tie band)".
* m2. Numbers in 4.3: POD+GP errors "0.055, 0.0020 and 0.0046" recompute to 0.0544, 0.00197, 0.00453 (0.054, 0.0020, 0.0045 when rounded). The supplement prints 5.5e-2, 2.0e-3, 4.6e-3 and says "verified". The projection floors "0.054, 0.0020, 0.0042" come from a script (`c10.py`, mentioned in `round1_counterfactual_adversarial.md`) that is not in the repository, so these three values cannot be reproduced from the repository. Add the script (a 10-line POD-projection computation) to `audit/`.
* m3. "nearly half the cells" (4.3 and checklist 2): recomputed 23 of 52 = 44%. Write "44% (23 of 52)".
* m4. "Double precision and a second-order polish lowered the networks' error by a further half decade on average": the statistic is the *median* improvement (0.47 decade over the 7 decisive instances at N=1024; 0.46 over all 20 cells), not the mean, and it is test-selected (see C2).
* m5. "which suggests training limits rather than a lack of capacity" (4.5): not supported. A network error floor of 2e-4 that does not fall under 4x epochs, float64 and L-BFGS is equally consistent with a capacity, architecture, data-size or conditioning limit (L-BFGS was capped at 400 iterations and changed the loss by <1% in 21% of refits, S1 section 7). Delete or flag as speculation.
* m6. "Changed the outcome on about a third of our cases" (checklist 5): 15 of 48 is from the four-times-longer-epochs experiment (Exp B) at N in {256, 1024} only. The double-precision/L-BFGS experiment (Exp F: 10 problems, 2 budgets) did not produce a case-change count. State which experiment the number belongs to.
* m7. Terminology collisions: "family" means (a) the method group (reduced-basis family, "two families are about equally good"), (b) the problem family ("24 main problems in 12 families", "19 family labels" in S1), (c) the application type. Also "group", "family", "side", "route", "stand-in", "surrogate" are used interchangeably. Pick: "reduced-basis methods" and "direct-network methods" for the two sides, "problem family" for PDE families, "problem class" for the six Table 1 rows. The figures carry the old internal labels "LS", "NL", "instances", "training solves N", "ȳ" (Figure 1) and "KRR / GP-ARD (Exp D)", "KRR-wide B=32", "GP-iso", "GP-full / POD+GP" (Figure 2), which the plain-language caption never explains; redraw both with plain labels.
* m8. Figure 2 caption says "How much worse each alternative is than the GP reduced model", but the right-hand box (GP-full / POD+GP) has median 0.95 and many dots < 1, i.e. "not worse". Say "ratio of test errors (above 1 means the alternative is worse)". The caption should also say the wide kernel ridge shown uses 32 tuning trials while the others use 8.
* m9. Table 1 counts use all 36 problems at N=1024 (23 / 3 / 10) whereas Figure 1 and the prose use the 24 main problems (13 / 3 / 8). Say so in the Table 1 caption.
* m10. Hardware/software for the timings is not stated ("CPU seconds"; thread count; PyTorch/scikit-learn versions).
* m11. "median of about 44 seconds ... and a third of a second for the polynomial": recomputed 0.29 s. "About 0.3 seconds" is more accurate.
* m12. Section 7's long single paragraph hides the key limitations; put them in a bulleted list and move "AI agents did the audits" to the front, not the back.
* m13. Section 2 "How we kept the analysis honest" asserts pre-commit of hypotheses to version control; the reader cannot check it (repository not yet archived, no DOI, no commit hashes in the main text). Either give the hashes/DOI or soften.
* m14. Section 4.4 "Follow-up experiments agreed with a simple reading" is vague; state which ones.

---------------------------------------------------------------------

## 3. Citation claims in Section 1 (against the reference list and repository evidence)

Repository evidence: `literature/updated_literature_matrix.csv` (21 rows, with "reading_depth"), `literature_review/references_verified.csv`, `literature_review/crossref_ref_hits.json`, `literature_review/data/arxiv_abstracts_core.json`, and `review/agent9_literature_citation_audit.md`. I could not read any of the cited papers; web access to publisher pages is bot-gated (see section 5), so "verified" below means "consistent with the metadata or abstract stored in the repository", not "full text read".

| # | Claim in Section 1 | Cited | Verdict from repository evidence |
|---|---|---|---|
| 1 | POD then learn the weights, "often with a Gaussian process" | Hesthaven & Ubbiali 2018; Guo & Hesthaven 2018; Bhattacharya et al. 2021 | **PARTLY WRONG.** Only Guo & Hesthaven is GP-based (and the matrix records "title only" reading depth for it). Hesthaven & Ubbiali (POD-NN) and Bhattacharya (PCA-Net) use neural networks; the supplement states this correctly ("neural networks were used for this by Hesthaven and Ubbiali and in PCA-Net, and GP regression by Guo and Hesthaven"). Split the sentence. Metadata of all three confirmed by Crossref (`references_verified.csv`). |
| 2 | Other route: NN producing the whole output, "sometimes through a narrow internal layer" | Fresca & Manzoni 2022; Franco et al. 2023 | Franco abstract (stored) matches: deep autoencoders for the solution manifold. Fresca & Manzoni is "title only" in the matrix; POD-DL-ROM actually applies POD before the network, so it is arguably a reduced-basis+NN method, not a direct network. Weakly supported as a pure "direct network" example. |
| 3 | Surveys found "most papers claiming to beat a standard method had used a weak baseline" | McGreivy & Hakim 2024 | **Supported as stated by the stored abstract** (79%, 60/76), but it is one review, not "surveys", and it concerns weak baselines among *numerical solvers*, not among competing surrogates. Using it to motivate "do not take the NN advantage for granted" in a surrogate-vs-surrogate comparison is a stretch; say "a systematic review of ML-for-PDE solvers". |
| 4 | Kernel/GP methods "reported competitive with DeepONet and FNO" | Batlle et al. 2024 (with Lu 2021, Li 2021) | Consistent with the matrix ("kernel methods competitive", abstract only). Not verifiable beyond the abstract. |
| 5 | "in a POD framework for extruder flows a GP was reported to have several advantages over a NN" | Bērziņš et al. 2020 (preprint) | The matrix says "arXiv API (full abstract read)" and the agent9 audit repeats that GPR was reported advantageous, but the abstract text itself is **not stored in the repository** (no JSON contains "extruder" or 2006.13706), so this cannot be re-checked here. The word "extruder" in particular is unverifiable from the repository. |
| 6 | "no universally superior method" among neural and polynomial surrogates | Westermann et al. 2026 (preprint) | Matrix: ~200k of 212k characters read; claim consistent. arXiv:2604.00689 text is not stored; cannot be re-checked here. |
| 7 | Small-POD feasibility depends on Kolmogorov n-width decay | Cohen & DeVore 2015 | Crossref metadata only; agent9 audit rates the support "PARTIAL" (abstract covers the rapid-decay case). Acceptable as a classical background reference. |
| 8 | "this decay has been shown to be slow for wave problems with discontinuous data" | Greif & Urban 2019 | Consistent with the agent9 audit's reading of the arXiv abstract (rate O(N^-1/2) for the wave equation with discontinuous initial conditions). The abstract is not stored in the repository; Crossref in the repo only confirms the title. |
| 9 | Reporting results as a function of tuning budget "has been advocated" | Dodge et al. 2019; Bouthillier et al. 2021 | Dodge: appropriate (expected validation performance vs budget). Bouthillier is about variance in benchmarks, only partly about tuning budgets; both are metadata-only in the repository. |

Other citation issues: GP regression itself (Rasmussen & Williams 2006), Adam, L-BFGS and the software stack are used but not cited in the main paper (they are in `references_verified.csv`); the reference list omits papers the repository's own audit flags as closest (Mora 2025, Kontolati 2024, Lanthaler 2023, de Hoop 2022, Lu 2022 "fair comparison of two neural operators"), most of which a referee in this area would expect. DOI/ID forms in the list are inconsistent ("10.xxx / arXiv:..." in [1]). Reference [4] begins "Bērziņš" but is sorted under B-e, harmless.

---------------------------------------------------------------------

## 4. Internal consistency and checklist evidence

### 4.1 Abstract vs body vs tables vs supplement
* Abstract "five such models" = pod_gp, pod_poly, pod_mlp, mlp_direct, bottleneck: consistent. "32 to 1,024 simulation runs": only 24 of 36 problems have the 32-run point (others 64/256/1024); stated in Section 3, not in the abstract.
* Abstract "sometimes by two or three orders of magnitude": consistent with bratu 2,043x, nlheat_L1 529x (interpolation set, 1,500-epoch float32).
* Abstract "kernel ridge ... within a factor of about 3": see M1 (inconsistent with the supplement's own table: 6.5x at equal trials).
* 4.1 "one to two orders after stronger training" vs S1 abstract "1.8-2.7 decades": inconsistent (M3).
* Supplement S1 section 6 says "7 of 7 pre-selected smooth instances ... mostly p = 3"; the main text says "eight extra smooth problems ... six of the eight have only three inputs" (6 of 8 recomputed: heatp x2, helm x2, reacdiff x2 at p=3, diff1d at p=4 and 8). Different counts (7 vs 8) for the same group, apparently because diff1d_L2 is excluded from the "7"; reconcile.
* S1 abstract: "a pilot-data diagnostic ... correlates with parameter dimension", main 4.4: "tracks the number of inputs: strongly negative only on three-input problems". Consistent.
* Table 1 vs Figure 1 denominators (m9).
* Figure 1 values (5/14/5, 8/11/5, 7/9/8, 9/11/4, 12/7/5, 13/3/8) reproduce exactly. The figure's legend and axes use the internal labels (m7).

### 4.2 Checklist labels
| Item | Label | Evidence recomputed | Assessment |
|---|---|---|---|
| 1 Always run a well-tuned GP/kernel baseline | "Strong for p <= 4; unresolved p >= 10" | p <= 4, N=1024: 30 problems; pod_gp is the lowest-error of the 5 methods in 20 (67%), reduced-basis group clearly better in 20, network clearly better in 8, ties 2. p >= 10: 6 problems incl. darcylin (reduced-basis clear), so "unresolved" is half right. | **Moderate**, not Strong; and "smooth" is undefined ex ante. The advice itself (run a GP baseline) is sound regardless of the label. |
| 2 Add a polynomial baseline | Moderate | 23/52 = 44% of GP-clear cells where POD+Poly clearly beats the best (test-selected) network; median poly/GP error ratio 9.9; 0.29 s median time. | Label fair. State 44%. |
| 3 Check whether POD is your bottleneck | "Strong; seen on three problems" | Three problems (heat2d_L2, incl_L1, incl_L2; plus G3 on heatmv3, incl3 showing the full-field GP wins). Floor numbers not reproducible from the repo (m2). | n=3-5 cannot be "Strong". Downgrade to "Moderate; five problems", and the advice (compare against the projection error) is a diagnostic anyone can run and is valuable. |
| 4 Decide your accuracy target first | Moderate | 36/36 vs 36/36; 27 vs 28; 19 vs 10 (reproduced). But see M2: 8 of the 36 selected as smooth. 24-problem split 9 vs 4. | Fair if the sample caveat is added. |
| 5 Report/vary NN training budget | Strong | Exp B: 4x epochs, pre-registered B1/B2 passed; 15/48 cells change class, all toward networks (reproduced; 9 ties to NN wins, 4 LS to tie, 2 LS to NN); 89.6% of fits improved. Exp F test-selected. | **Moderate-to-Strong**: direction is robust; the "about a third" belongs to Exp B only; Exp F is test-selected. |
| 6 Same tuning effort | Moderate | Stage-1 H4a: 10 vs 1 discordant cells (p=0.006 raw, 0.023 Holm), NN-win share 47% to 56% (reproduced from `results/statistics.json`). | Fair; this is the only Stage-1 confirmatory hypothesis that was supported; could be "Moderate-Strong". |
| 7 Report ties as ties | Moderate | Config-draw halves: class agreement 83% overall (reproduced: 83.3%); among cells that are ties at full budget, 30% differ between the two half-searches (my recomputation); 4% for LS-clear, 12% for NN-clear cells. | Well supported for ties ("sizeable minority" = 30%); but each half has only 4 trials, so this measures half-budget searches, not repeated 8-trial searches. Say so. |
| 8 Do not rely on a pilot statistic | "Weak evidence against, inconclusive" | rho = -0.38 (p = 0.18), reproduced; 6 instances without nlheat gives rho = +0.49. | The label is muddled. "Not supported at n=8; insufficient power to rule out" is clearer. |

---------------------------------------------------------------------

## 5. Journal fit (repository evidence only)

### 5.1 What the repository supports
All timeline and scope statements below come from `audit/final_journal_decision.md`, `journal_selection/*`, `results/mlst_turnaround_*`. I recomputed from the stored CSVs:
* MLST sample (`results/mlst_turnaround_sample.csv`): 35 usable received/accepted pairs out of 150 sampled pages; median 126 d, Q25-Q75 95-150.5 d, 3/35 (8.6%) within 72 d, range 60-339 d. Matches the decision file. The sample is small, survivor-biased (accepted papers only) and 77% of sampled pages lacked readable dates (the missing-date mechanism could bias it either way).
* MLCSE census (`journal_selection/data/harvest_mlcse.csv`): n=102, median 50 d, Q75 64.75 d, 83.3% within 72 d, max 205 d, min 8 d. Matches. But: all 102 records were accepted between 2024-Q2 and 2026-Q4 (the journal is about two and a half years old; 4 records in the final partial quarter), the shortest times (8, 9, 11 days) are implausibly short for peer review and suggest that "received" can be a revised-submission date or that acceptance can follow minimal review; the Springer record only deposits dates for accepted papers; I could not tell whether MLCSE publishes benchmark/negative-result papers beyond the three titles the authors list ("data splitting", "statistically grounded selection and validation of surrogate models", "numerical study on hyperparameter settings"). Those three titles are close in kind to this paper, which is the only genuine positive scope evidence.
* Engineering with Computers: n=206 median 151 d, 11% within 72 d; surrogate/neural n=47 median 172 d, 4.3% within 72 d; 44/47 recent surrogate papers propose a method (title-level only).
* No quartile or impact factor is verified for any candidate (JCR inaccessible; aggregator numbers conflict). MLCSE has no JIF (per a Springer collection snippet, recorded as secondary).

**Web check made in this review (2026-10-29).** I tried https://link.springer.com/journal/44379 (redirected to an authentication endpoint; no content) and a web search "Machine Learning for Computational Science and Engineering Springer journal impact factor indexing aims and scope" (results were unrelated: an arXiv preprint, other journals; no impact factor, indexing or scope text for the journal). I therefore add **no** new external facts about any journal. Everything about journals in this report is repository evidence or labelled as my inference.

### 5.2 Does a practitioner-oriented comparative study on simulated problems fit the candidates?
* **MLCSE.** Scope appears to fit (three similar-genre titles; benchmark/methodology papers evidently publishable) and observed timelines are compatible with 72 days. The authors' Q1 preference fails outright (no JIF). The 72-day figure is an observed property of accepted papers in a young journal, not a policy. Because first revisions depend on author turnaround, a paper whose revision needs new experiments (see below) can exceed 72 days at any journal.
* **MLST.** Plausible scope (ML across the sciences), journal-page IF 4.2 unverified, Q1 unverified; observed history (median 126 d, 8.6% within 72 d) is incompatible with the hard constraint. No stated policy on negative-result benchmarks in the repository.
* **Engineering with Computers.** Best-known IF among candidates (4.9, unverified, aggregator) but weak scope fit (method-proposing papers) and observed times (median 151 d) incompatible. Desk-rejection risk high for a no-new-method paper.
* **CMAME / EAAI.** Not measurable for timeline; scope stretch, high desk-rejection risk (CMAME does carry a "fair comparison of neural operators" precedent, Lu 2022, but that was with real methodological reach).
My assessment: the paper type fits only the methodology/benchmark niche (MLCSE; possibly MLST), not the method-journal Q1 options. Evidence for MLST's reception of negative-result benchmarks is absent from the repository.

### 5.3 What a referee at such a journal would demand
1. Public or externally generated problems; at least one problem with a third-party solver or dataset.
2. Neural baselines tuned beyond 8 random draws; ensembles; at least one neural-operator or POD-DeepONet baseline; a tuning-budget curve for the networks (the paper itself cites Dodge 2019 for this and does not do it).
3. Problem-level or family-level statistical treatment, with intervals on the headline counts; sensitivity to the problem selection (the 8+4 added problems).
4. Total-cost accounting (simulation + training + inference).
5. A persistent archive of code and data (Zenodo DOI not yet created), commit hashes for the claimed pre-commitment.
6. A reconciled and shortened main text with the negative confirmatory results stated.
7. Disclosure and human verification of AI-generated analysis, audits and text (the paper declares this; journals differ in what they accept for AI-assisted drafting; the authors must read each target journal's AI policy, which the repository does not contain).
8. Probably: comparison against a GP on full field as a first-class method rather than a control.

### 5.4 Can the 72-day constraint be supported?
No, not as a guarantee, and the repository's own decision (`final_journal_decision.md`) already says so. The only evidence compatible with it is MLCSE's observed received-to-accepted census (median 50 d, 83% <= 72 d), which (i) is survivor-biased, (ii) comes from a very young journal, (iii) cannot account for the rejection/resubmission path, and (iv) conflicts with the Q1 preference because no JIF exists. If the authors adopt "submit to MLCSE and report the observed history", they should say "observed history of accepted papers" and never "will be accepted within 72 days". Note also that after a desk rejection or a negative review the 72-day clock cannot be met by any journal. The two hard constraints (Q1 and 72 days) are mutually unsatisfiable on the available evidence; the authors must choose which one gives way, as the decision file already records. I recommend not stating any quartile, IF or timeline for any journal in the submission cover materials until the authors have checked JCR and the journal pages themselves.

---------------------------------------------------------------------

## 6. Readability: the five worst passages and proposed rewrites

**P1. Abstract, mechanism sentences (over-claim plus run-on).**
Original: "Several of the neural networks' apparent wins came from the limits of the reduced basis rather than of the GP, and disappeared when the GP was applied to the full field. The GP's edge was not caused by the reduced basis; it came mainly from searching its hyper-parameters over a wide range, since kernel ridge with a wide search came within a factor of about 3 of it."
Rewrite: "Some of the networks' wins came from the limits of the reduced basis, not of the GP: a GP fitted to the full output field beat them again. A plain kernel-ridge model, once its regularisation was searched over a wide range, closed most of the gap to the GP (from a median 14 times worse to 6.5 times worse with the same eight tuning trials, and 2.7 times worse with 32 trials), so much of the GP's advantage reflects careful tuning of a smooth regressor; a residual factor of 2 to 3 remains unexplained."

**P2. Section 4.3 first paragraph (jargon-heavy, numbers without a reader-friendly anchor).**
Original: "the error of the POD+GP model is the same as the error of the POD projection with 32 modes (0.055, 0.0020 and 0.0046 against 0.054, 0.0020 and 0.0042), so POD itself is the bottleneck and the networks, which are not confined to a basis, get below it."
Rewrite: "On three problems the POD+GP error equals the best error any 32-mode basis could reach even with perfect weights (about 5.4e-2, 2.0e-3 and 4.5e-3). The basis, not the regressor, sets the limit. Networks that produce the whole field are not tied to a basis and so can do better, and a GP fitted to the full field does better still."

**P3. Section 4.5, "Training the networks longer" (dense, stacked clauses, speculation).**
Original: "Retraining ... moved the comparison toward the networks in all 15 of the 48 (problem, budget) cases whose classification changed; ... which suggests training limits rather than a lack of capacity; but we did not explore every way of tuning a network, and a thoroughly tuned network could do better."
Rewrite: "We retrained the stored best networks for four times as many epochs. The error fell in about nine of ten fits. In 15 of the 48 problem-and-budget cases the verdict changed, and every change favoured the networks; nine ties became network wins. A further switch to double precision and a second-order optimiser (L-BFGS) lowered the network error by about 0.5 decades (a factor of about 3). The biggest gaps survived (60 to 520 times on five problems; 4 and 9 times on darcy_L1 and heat2d_L1). We do not know why network errors plateau near 2e-4; better-tuned networks may do better."

**P4. Section 4.1, opening and "Earlier we had read..." (refers to an unseen draft; hedges).**
Original: "Earlier we had read the small-budget results as 'networks win most cases', but most of those were ties."
Rewrite: "At 32 runs, 14 of the 24 problems are ties, so no family is clearly ahead. Our first analysis counted small differences as wins; a 25% tie band removes most of them."

**P5. Section 6 checklist item 3 and 8 (labels contradict their own text).**
Original 3: "(Strong; seen on three problems.)" Original 8: "(Weak evidence against, inconclusive.)"
Rewrite 3: "Check whether the basis is your bottleneck. Compute the error you would get by projecting held-out fields onto your basis. If your model's error equals it, a larger basis or a basis-free model will help more than a better regressor. (Moderate: we saw it on five problems; it is a cheap diagnostic you can run on your own data.)"
Rewrite 8: "Do not choose by a quick pilot statistic yet. The one we tested (how fast POD compresses 32 runs) did not predict the winner on eight new problems (rho = -0.38, p = 0.18) and mostly tracks the number of inputs. Eight problems cannot rule out a weak effect."

Also general: the paper repeatedly uses "stand-in" and "surrogate" interchangeably, "side", "route", "family", "group"; "tie-aware", "log10 error ratio", "Holm" appear without explanation for a student reader; define the tie band once (a 25% error difference) and use "network error / basis error" ratios in the text, not log units.

---------------------------------------------------------------------

## 7. Table of every typed (non-computed) number checked

"Claimed" is the number in `Final_Manuscript_v4.md`; "Recomputed" is from raw per-job files unless the source is given. OK = matches within the rounding used. Items computed by `build_v4.py` from result files are also listed because I re-derived them independently.

| # | Location | Claimed | Recomputed | Status |
|---|---|---|---|---|
| 1 | Abstract/Table 2 | 19 vs 10 problems reach 0.1% | 19 vs 10 (by set: orig 7/2, A 2/2, A2 8/5, A3 2/1) | OK; see M2 for selection caveat |
| 2 | Abstract/Table 2 | 10% target: 36/36 | 36/36 | OK |
| 3 | Table 2 | 1% target: 27 vs 28 | 27 vs 28 | OK |
| 4 | 4.2 | 10% reached "usually with 64 runs or fewer" | LS 28/36, NN 29/36 at N <= 64 | OK |
| 5 | 4.1 | N=32: 5 reduced-basis, 5 network, 14 ties | 5/5/14 | OK |
| 6 | 4.1 | N=1024: 13/8/3 | 13/8/3 | OK |
| 7 | 4.1 | network wins 6 at band 0.15, 10 at band 0.05 | 6 and 10 | OK |
| 8 | 4.1 | bratu_L1 "about 2,000" | 2,043 | OK |
| 9 | 4.1 | nlheat_L1 "530" | 529 | OK |
| 10 | 4.1 | burgers_L1 "180" | 177 | OK |
| 11 | 4.1 | largest network margin 2.8 | 2.76 (fisher_L2); heatmv3_L1 (selected set) 2.76 | OK |
| 12 | 4.1 | eight extra smooth problems factors "about 10 to 850" | 9.9 to 849 (all 8 positive) | OK |
| 13 | 4.1 | "six of the eight have only three inputs" | 6 (p=3), 2 others (p=4, 8) | OK |
| 14 | 4.1 | extrapolation bratu_L1 3.3 to 1.5; nlheat_L1 2.7 to 1.8 | `extrap_and_seed_consistency.json`: 3.31 to 1.49; 2.72 to 1.84 | OK |
| 15 | 4.1 | "one to two orders of magnitude after stronger training" | 60-520x (1.8-2.7 decades) on the 5 decisive problems | **MISMATCH** (M3) |
| 16 | 4.1 | "shrink by roughly half a decade" | median 0.47 (0.46 over all cells) | OK |
| 17 | 4.1 | networks led on transport_L2, kdv_L1, incl_L1, incl_L2, darcy_L2, darcyhd_L1 | NN-clear at N=1024: those six plus fisher_L2 and heat2d_L2 (the latter two mentioned elsewhere) | OK, incomplete (fisher_L2 never named in 4.1) |
| 18 | 4.1 | "problems with 16 and 32 inputs not consistent across seeds" | darcylin_L1/L2 (p=16/32) are seed-consistent reduced-basis wins; only darcyhd_L1 (16) and darcy_L2 (10) are seed-inconsistent; darcyhd_L2 (32) is a tie | **MISMATCH** (C1) |
| 19 | Table 1 | all 6 rows (counts, medians of log ratio, typical errors) | reproduced exactly (e.g. 3/1/5, -0.13, 4e-03/3e-03; 7/0/2, 2.58, 2e-06/1e-03; ...) | OK |
| 20 | Table 1 | 9, 9, 4, 2, 4, 8 problems; input ranges 3-32, 3-8, 4, 3, 3-4, 3-4 | reproduced | OK |
| 21 | 3 | 4,096 pool; 1,000 test; 500 extrapolation; 24 problems 32-1,024, 12 problems 64/256/1,024 | `data.py` POOL=4096, N_TEST=1000, N_EXT=500; N grids as stated | OK |
| 22 | 2 | 8 random draws (first is default), 1/5 validation, 1,500 epochs, batch 512 at N=1,024 (twice the steps) | `hpo.py` (trial 0 default, 20% split), `methods.py` (NN_EPOCHS=1500, bs = n if n<=512 else 512) | OK |
| 23 | 4.2 | CPU median GP 44 s | 43.99 | OK |
| 24 | 4.2 | POD+network 86 s | 86.19 | OK |
| 25 | 4.2 | direct networks 116-139 s | 115.7 (bottleneck) - 138.7 (mlp_direct) | OK |
| 26 | 4.2 | polynomial "a third of a second" | 0.293 s | OK (about 0.3) |
| 27 | 4.3 | full-field GP median error ratio 0.95 | 0.951 (`expG_statistics.json`) | OK |
| 28 | 4.3 | POD+GP errors 0.055, 0.0020, 0.0046 | 0.0544, 0.00197, 0.00453 | **Minor mismatch** (rounding; m2) |
| 29 | 4.3 | projection floors 0.054, 0.0020, 0.0042 | not reproducible: generating script (`c10.py`) is not in the repository; round-1 review quotes 5.4e-2, 2.0e-3, 4.2e-3 | UNVERIFIABLE from repo |
| 30 | 4.3 | full-field GP beats best network by 1.2 and 1.0 decades on heatmv3_L1, incl3_L1 | `expG3_cells.csv` at N=1,024: heatmv3_L1 1.17, incl3_L1 0.98 (the text prints 1.2 and 1.0) | OK |
| 31 | 4.3 | narrow kernel ridge "median 14 times worse" | 14.28 (52 cells); 13.4 on the 28 common cells | OK |
| 32 | 4.3 | wide kernel ridge 6.5x (B=8), 2.7x (B=32) | 6.48 and 2.68 (28 cells) | OK |
| 33 | 4.3 | wide kernel ridge beat best network clearly in 64% | 64.3% (B=32); 60.7% (B=8) | OK |
| 34 | 4.3 | polynomial median 10x worse than GP, beat best NN in 23 of 52 | 9.88; 23 of 52 | OK |
| 35 | 4.3 | direct network beat POD network by more than 25% in 17 of 24 | 17 (POD net better in 1) | OK |
| 36 | 4.4 | rho = -0.38, p = 0.180 | -0.381, 0.1799 (exact one-sided); two-sided 0.35 | OK (one-sided, not stated) |
| 37 | 4.4 | p = 0.051 after correction | 0.0506 (10^6 bootstrap draws, Holm) | OK; the CI [-0.001, 1.33] includes 0 |
| 38 | 4.4 | "without nlheat the correlation changes sign" | +0.49 on the 6 remaining | OK |
| 39 | 4.5 | 4x epochs improved "nine in ten" | 89.6% of fits | OK |
| 40 | 4.5 | 15 of 48 cells change class, all toward networks; 9 ties became NN wins | 15 of 48; all toward NN; 9 | OK |
| 41 | 4.5 | "half a decade on average" (double precision + L-BFGS) | median 0.47; mean 0.47 | OK (statistic is median in JSON) |
| 42 | 4.5 | "5 of the 7" decisive remain >= 1 decade | 5 (`expF_statistics.json`) | OK |
| 43 | 4.5 | darcy_L1 and heat2d_L1 led by "about 4 and 9" | 4.30 and 8.99 | OK |
| 44 | 4.5 | networks' error "around 2e-4 at best"; GP "10^-7 to 10^-5" | 2.0e-4; GP 3.9e-7 to 1.6e-5 for the 5 decisive, but 1.4e-4 and 1.5e-4 on heat2d_L1 and darcy_L1 | OK for the 5 decisive; the range is not general |
| 45 | 4.5 | unequal tuning: 10 vs 1 switched cells | 10 vs 1 (Stage 1, n=96) | OK |
| 46 | 4.5 | draw halves: 83% class agreement; 99% sign agreement | 83.3%, 98.7% (my replication also gives 83.3%) | OK |
| 47 | 4.5 | NN-clear cells clear in all three seeds 57%, reduced-basis 80% | 57.1% (n=35), 79.6% (n=54) | OK |
| 48 | 5 | darcy_L1 p = 4 | p = 4 | OK |
| 49 | 5 | darcy_L1 256 runs: 3.2e-04 (RB) vs 4.2e-03 (NN) | 3.19e-4, 4.19e-3 | OK |
| 50 | 5 | darcy_L1 1,024 runs: 1.5e-04 vs 2.1e-03 | 1.52e-4, 2.07e-3 | OK |
| 51 | 5 | darcy_L1 1% from about 64 runs, either approach | RB 64, NN 64 | OK |
| 52 | 5 | darcyhd_L1 "both stuck at about 6e-02" | RB 5.8e-2, NN 4.3e-2 | **Mismatch** (m1) |
| 53 | 5 | darcyhd_L1 "within about 30%" | ratio 1.33 (y = -0.125), beyond the paper's 25% band and counted as a network win in 4.1 | **Mismatch/tension** (m1) |
| 54 | 5 | "difficulty comes from the number of inputs" | contradicted by darcylin_L1 (p=16) reaching 0.1% at N=256 | **MISMATCH** (C1) |
| 55 | 5 | heat2d_L1: RB needs ~64 runs for 1%, 256 for 0.1% | 64; 256 | OK |
| 56 | 5 | heat2d_L1: NN ~128 for 1%, never 0.1% | 128; NaN | OK |
| 57 | 5 | heat2d_L2: neither reaches 1% | both NaN | OK |
| 58 | 5 | heat2d_L2 networks ahead "by a small margin" | 2.2x at N=1,024 (third largest NN margin) | **Mismatch** (M8) |
| 59 | 5 | bratu: 0.1% with 32 runs for RB on both; NN needs 1,024 | 32, 32; 1,024, 1,024 | OK |
| 60 | 5 | bratu_L1 at 256: 1e-06 vs 1e-03 | 1.4e-6 vs 1.4e-3 | OK (rounded) |
| 61 | 6.1 | "usually the most accurate option" for p <= 4 | pod_gp best of five in 20/30 (67%) | Supported, weak for "Strong" |
| 62 | 6.2 | polynomial beat NN in "nearly half" of GP cells | 23/52 = 44% | OK (say 44%) |
| 63 | 6.3 | "seen on three problems" | three plus two later | OK, label inconsistent |
| 64 | 6.4 | "about twice as many (19 against 10)" | 1.9 | OK |
| 65 | 6.5 | "outcome changed on about a third of our cases" | 15/48 = 31% (Exp B only) | OK, attribution (m6) |
| 66 | 6.7 | flipped "in a sizeable minority" | 30% of tie cells; 17% overall | OK |
| 67 | 7 | "24 main problems in 12 families" | 12 families in orig+A | OK |
| 68 | 3/Abstract | 36 problems | 16+8+8+4 = 36; 19 family labels | OK |
| 69 | Fig. 1 | counts per N | reproduced | OK |
| 70 | Abstract | "five such models" | 5 | OK |

---------------------------------------------------------------------

## 8. Prioritised to-do for the authors (minimum fixes before any submission)
1. Rewrite the mechanism claim in the abstract, 4.3, 8 (M1) and redraw Figure 2 on a single cell population with plain labels and both kernel-ridge budgets (C2, m7, m8).
2. Correct the Section 5 darcy example and 4.1 on 16/32 inputs using darcylin (C1); fix "one to two orders" (M3); "small margin" (M8).
3. Split headline counts by problem set; say 8 problems were selected for smoothness (M2).
4. State the negative Stage-1 confirmatory outcomes in the main text; delete "Earlier we had read..." (M6, P4).
5. Fix the Section 1 citation split (Hesthaven & Ubbiali and Bhattacharya are NN-based) and add the closest missing references (M5, section 3).
6. Downgrade checklist labels (items 1, 3) and attribute numbers to the experiment that produced them (item 5) (M4).
7. Retitle without "engineering" and state "synthetic benchmark problems" in abstract (1.2).
8. Add the projection-floor script, hardware for the timings, and an archive DOI with commit hashes.
9. Human verification of all numbers and citations, as the Declarations already require.
10. Decide which journal constraint (Q1 or 72 days) gives way; verify JCR/author guidelines/AI policy at the journal itself before quoting anything.
