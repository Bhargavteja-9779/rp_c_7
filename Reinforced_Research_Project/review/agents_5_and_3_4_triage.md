# Triage of the two independent AI audits (implementation: `agent5_implementation_audit.md`; design & statistics: `agent3_agent4_design_statistics_audit.md`)

Both agents are AI sub-agents with fresh context (not human, not external peer reviewers). Every finding that changed an action was verified by me against code or data first.

| Finding | Verification | Action |
|---|---|---|
| Exp B shift sign inverted (impl F1) | Confirmed in my own code | Fixed before analysis (V1) + unit test |
| Search draws shared across instances/N (impl F2, design F03) | Confirmed from `hpo.py` | Disclosed (V5); analysis-only sensitivity planned; 'tuning' wording corrected in manuscript |
| POD+GP search space has 8 points; ML-II optimisation uncounted (impl F4) | Confirmed from `methods.py` | Manuscript: "B counts trials, not search coverage" |
| v1 hash seeding → D/E compare different config draws (impl F3) | Plausible, consistent with D5 | Disclosed |
| H4a/S1 cell-level vs manuscript 'unit = instance' (impl F7, design F09) | Confirmed | Sentence rewritten; instance-level result reported |
| A2 Q1 p0 miscounted; 7 qualifiers ≈ 4 families (impl F8, design F08) | **Verified**: 3/20, not 2/20 | Amended before A2 ran (V2); family-level report added |
| Exp A carried by one family; P2 knife-edge; power low (design F06) | **Verified**: nlheat 88.3 % of gain; ρ without nlheat = +0.486 | Wording → "inconclusive" (V3); MC p-values recomputed with 10⁶ draws |
| f1 confounded with p (design F07) | **Verified**: Spearman 0.708; all f1 < −2 have p = 3 | Exp A3 probe; manuscript states the confound |
| "LS advantage" is POD+GP, not the subspace (design F01) | **Verified** (direct MLP beats POD+MLP in 17/24; E6 earlier) | Exp G (no-POD GP); families re-described as POD-based vs direct-output |
| NN error floor / float32 / batch-step kink (design F02, impl F10) | Partly verified (floor 6.6e-4; code: 1500→3000 steps at N = 1024) | Exp F (float64, full-batch, L-BFGS) pre-registered |
| Tuning not matched: LS 24 vs NL 16 trials; HPO time differs 100× (design F04) | Confirmed (3 vs 2 members; B per method) | E6 already tests member asymmetry; wording in manuscript |
| KRR/GP ratio huge where GP error < 1e-5 → search can't reach sharp optimum (design F05) | Plausible, consistent with D2 | Interpretation limited; Exp E adds a control |
| Tie band ≈ seed noise (design F10) | Verified (seed SD 0.103; sign consistency 71 % / 50 %) | Band reported with sensitivity (0.05–0.30) and seed consistency |
| Cost table includes test prediction per trial (impl F9) | Confirmed from `hpo.py` | Cost table labelled indicative |
| advdiff_L2 FOM not mesh-converged (impl F12) | Reported by agent; consistent with first-order upwind | Wording: 'first-order upwind discretisation at n = 32; mesh error ≈ 14 %' |
| D/E/B comparators use oracle test minima (impl F13) | Confirmed | Labelled 'oracle' in the text; seed-set assertion added |
| Stale test; vacuous leakage test; thread env (impl F15, F16, F18) | Confirmed | Fixed |
| Extrapolation severity scales with p; helm_L2 near resonance (impl F11) | Plausible | Extrapolation (H3/E4) stays exploratory with the caveat |
| NL limited to plain MLPs; no FNO/operator-input (design F19) | Known limitation | Stated |
| Items 'could not verify' (git ordering of every result file, v1 reproduction from scratch, other hardware) | n/a | Added an automated prereg-ordering check in the final audit |
