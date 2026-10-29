# Triage of Round 2 (manuscript quality, number check, journal fit) — reviewer: fresh-context AI agent
Verdict received: **major revision** (all computed headline numbers reproduced; wording and framing problems). Each item was checked before acting.

| Finding | Verified? | Action in Final_Manuscript_v4 |
|---|---|---|
| Darcy example/4.1 wrongly said 16/32-input problems are inconsistent and difficulty comes from the number of inputs; darcylin_L1/L2 (p=16/32) are reduced-basis wins | Yes | Rewrote 4.1 and the worked example: darcyhd, darcy_L2 and darcylin reported separately; "number of inputs alone does not decide difficulty". |
| darcyhd_L1 "within about 30%": ratio 1.33, outside the 25% tie band; errors 5.8e-2 vs 4.3e-2 | Yes | Both values printed; "about 25% lower, just outside our tie band". |
| heat2d_L2 network lead "small" (factor 2.1) | Yes | "about a factor of two". |
| "one to two orders after stronger training" wrong (60-520x) | Yes | Replaced by "roughly 60 to 500 times on the most favourable problems". |
| Projection-floor numbers not reproducible (script missing) | Yes | Added `audit/pod_floor_check_and_extras.py` (+ `results/pod_floor_check_and_extras.json`); text now computed from it. |
| Mechanism over-claim (abstract/conclusion); "about 3x" needs 4x trials, 57% of cells; fig mixes cell sets | Yes | Abstract and conclusion rewritten (14x → 6.5x at equal trials → 2.7x at 32 trials; residual 2-3x unexplained); Fig. 2 now shows narrow KRR, wide KRR B=8, B=32 on the same 28 cells, plus iso-GP and full-field GP. |
| Mechanism comparisons use test-selected "best network" (contradicts "never on test data") | Yes | Disclosed in Section 2 and in 4.3/4.5. |
| 19-vs-10 headline includes 8 smooth-selected problems | Yes (9 vs 4 on the 24 main problems) | Split reported in abstract and 4.2. |
| Citation split: Hesthaven & Ubbiali and Bhattacharya use NNs, not GPs | Yes (matches my earlier audit notes) | Sentence corrected. |
| Closest references missing; Bērziņš/Westermann not re-checkable | Partly (cannot be verified offline) | Limitation added ("literature search was limited"); no new citations added unverified. |
| Checklist labels (item 3 "Strong", item 1 "usually", item 5 "a third") | Yes | Relabelled; counts shown (20 of 30 at p ≤ 4). |
| Title/subtitle/"application types" over-promise | Yes | Subtitle changed; "classes named after application areas; nothing was calibrated to a real application" stated in abstract, intro, Section 3. Main title kept (user asked for a simple title). |
| Main text omits negative confirmatory results | Yes | Added to 4.1 (three of four hypotheses failed) and Section 4.4. |
| "independent AI review" overstates | Yes | "a review by an AI agent we asked to criticise it". |
| Missing decision rule, no external dataset, no total-cost accounting, weak NN baseline | Yes | Table 3 (decision aid by number of inputs); limitations list states: no public benchmark, no inference/simulation cost, lightly tuned networks. Not fixable with existing evidence. |
| Minor m1-m14 | Mostly yes | Fixed: m1-m6, m8-m9, m11-m14 (hardware note, list-form limitations, hashes pointer, follow-up experiments named); m7 (terminology) partly. |

## Journal fit (reviewer's reading, adopted)
Fits only methodology/benchmark venues (closest in the repository evidence: MLCSE, which has no JIF); method-oriented Q1 journals would probably desk-reject (no new method, no real/public data, main finding known, negative confirmatory results). The 72-day constraint cannot be supported with the evidence available. See `audit/final_journal_decision.md`.
