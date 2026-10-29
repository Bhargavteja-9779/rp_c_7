# Submission readiness report — final cycle (2026-10-29)

## Decision: **B — conditionally ready (for a methodology/benchmark venue only)**
Not A: several blockers need human action and the journal constraints cannot be met on available evidence. Not C/D: the science is reproducible, honestly reported, and survived three review rounds without a fatal flaw.

## What was done in this cycle
* Ran and analysed all pre-registered follow-ups: B (stronger NN: pass, but 15/48 cell classes move toward NN), A2 (7/7 smooth candidates, confounded with p), E (iso-GP), A3/G/G3 (POD limits vs GP), F (float64+L-BFGS: 5/7 large gaps persist), and a post hoc wide-range kernel-ridge control H (prompted by review; narrows the GP gap from 14× to 6.5×/2.7×).
* Three review rounds by fresh-context AI agents (scientific validity + counterfactual; manuscript/journal fit; fresh-clone reproduction + rejection attempt), each triaged and fixed (`review/`).
* Rewrote the paper as a plain-language, application-oriented practitioner study with a simpler title; technical material moved to Supplement S1.

## Evidence status (see `audit/claim_evidence_matrix.md`)
Validated: arithmetic and tables (24/24 recomputed from raw JSON in a fresh clone; 50/50 tests; independent recompute scripts); chronology of pre-registration (no result precedes its protocol); bit-identical re-run of a later-experiment instance.
Established with caveats: GP/reduced-basis models far more accurate than lightly tuned networks on smooth low-input problems at ≥256 runs (strength depends on network budget, interpolation vs extrapolation set, and a step-count change at 1,024 runs); the advantage is not due to POD and is largely regression/search quality.
Not established: pilot diagnostic; learning-curve crossovers; marginal likelihood per se as mechanism; any statement about real applications, high-input problems, ensembles, or neural operators.

## Remaining risks / unresolved issues
1. **No human authors/affiliations/funding/competing interests; all audits and reviews were AI-agent-made.** A named human author must take responsibility and verify every number, citation and claim; independent human review is strongly advised.
2. **Journal/constraint blocker.** No verified Q1/Q2 journal with an observed ≤72-day acceptance history; the 72-day requirement is **not satisfied** and not claimed. The paper fits only methodology/benchmark venues (closest in our evidence: MLCSE, which has no JIF); method-oriented Q1 journals would probably desk-reject (no new method, no real/public data, known main finding). See `audit/final_journal_decision.md`. Authors must verify current JCR status and guidelines.
3. **No external or real data** (no public benchmark, no field data); in-house solvers; solver cost is milliseconds, so the surrogate cost case is not demonstrated.
4. Networks lightly tuned; optimisation vs generalisation error not separated; original 16 problems not bit-reproducible on a full re-run (disclosed).
5. Related work coverage limited (abstract-level reading for most sources); closest papers may be missing.
6. Pre-registration is a self-hosted git history; several experiments post hoc in motivation (disclosed).
7. Data/code not yet archived with a DOI; references need a final manual check against publisher records.

## Next steps (in order)
Name human authors and have at least one human domain expert read and challenge the paper; verify journal scope/IF/quartile/author guidelines and decide which constraint (Q1 vs 72 days) takes priority; consider adding one public benchmark problem (e.g. from PDEBench) and a stronger tuned-network baseline; archive code/data (DOI); manual reference check; then submit. No outcome or acceptance time is guaranteed or predicted by this report.

## Files
Paper: `manuscript/Final_Manuscript_v4.{md,docx,pdf}`; supplement `manuscript/Supplement_S1_Technical_Report.{md,docx,pdf}`; cover letter `manuscript/cover_letter_v4.md`; reviews and triage `review/`; simulated reviewer response `review/simulated_reviewer_response.md`; audits `audit/`; protocols and addenda `research_design/`; code `code/`; results `results/`.
