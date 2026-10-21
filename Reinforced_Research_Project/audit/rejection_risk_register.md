# Rejection Risk Register (Phase 3) — second adversarial board

*The board is **simulated** by one agent in separate passes (no external reviewers). Each reviewer was assigned a distinct failure mode. "Final resolution" is updated at the end of the project (see §Resolution).*

| ID | Rev. | Sev. | Type | Issue & evidence | Why a reviewer cares | New experiment? | Corrective action | Verification criterion | Status |
|---|---|---|---|---|---|---|---|---|---|
| RR-01 | B,J | **CRITICAL** | scientific | The only positive evidence for the pilot diagnostic (E3: ρ≈−0.7, 14/16 LOFO) is post hoc; the pre-registered H2 failed (adj p 0.145) | the paper's one novel claim is unconfirmed | **Yes — Exp A** (8 new instances, frozen rules) | pre-registered out-of-sample test (P1,P2,S1) | P1 & P2 pass Holm α=.05 | OPEN→Exp A |
| RR-02 | D,G | **CRITICAL** | methodological | "Matched tuning" (B=8 trials) is not matched in effective optimisation: each POD+GP trial maximises marginal likelihood over ARD hyper-parameters; NNs get 8 random configs. Without POD+GP the NN family wins 78 % of cells (E6) | the headline "LS advantage" may be a hyper-parameter-fitting artefact, not a property of linear subspaces | **Yes — Exp D** (POD+KRR with the same B=8 search) | D1/D2 criterion | pre-specified ratio test | OPEN→Exp D |
| RR-03 | G,D | MAJOR | methodological | NN under-training: fixed 1500 epochs; E1 covered 6 of 16 instances, 1 seed; no loss curves in v1 | competing group: "your NNs are not converged" | **Yes — Exp B** (24 inst × 3 seeds, 6000 ep, loss curves) | B1/B2 criteria | sign retention ≥ 85 %, shift < 0.5 dec | OPEN→Exp B |
| RR-04 | E,A | MAJOR | statistical/editorial | "NL won 12/16 at N=32" counts ties: 7 of 12 within ±0.1 decades; only 71 % of cells sign-consistent over seeds (independent re-analysis) | headline overstated | No (re-analysis); tie-aware reporting | equivalence band 0.10 in all headline statements | manuscript headline uses clear-win/tie counts | OPEN→Phase 9 |
| RR-05 | F,B | MAJOR | generalisation | 8 hand-chosen families, p ≤ 10, m ≤ 256, synthetic | external validity | **Yes — Exp A** adds p=16,32, discontinuous inclusion, dispersive solitons | new families; still synthetic | results by family reported | PARTIAL |
| RR-06 | C | MAJOR | novelty | Kernel/GP competitiveness already published (Batlle et al. 2024, *not cited in v1*); "no best surrogate" (Westermann 2026); low-dimensional manifolds make any competent ROM work (Duraisamy 2026 position paper); CTF benchmark (2510.23166) on weak baselines | novelty overclaimed; missing key citation | No | rebuilt novelty argument (novelty_reassessment.md) | all three cited and positioned | RESOLVED (writing) |
| RR-07 | A,I | MAJOR | editorial | Contribution type (benchmark + failed hypotheses) vs journal expectations; AI authorship disclosure; 72-day constraint unmet | desk-rejection | No | journal-fit reassessment | decision recorded | OPEN→Phase 5 |
| RR-08 | E | MAJOR | statistical | H4a McNemar treats 96 cells as independent; only 5/16 instances flip; Holm-adjusted p≈0.125 at instance level | fragile inference | partly (Exp A adds 8 instances for a descriptive replicate) | report instance-level result as primary descriptive | stated in text | OPEN |
| RR-09 | E,D | MODERATE | statistical | Pre-registered baseline B1 (log2N + p) degenerate under LOFO (Darcy fold RMSE 11.4) | H2 test uninformative | No | v2 baselines B0 and B1log; frozen R2 | done in v2 protocol | RESOLVED (design) |
| RR-10 | H | MODERATE | reproducibility | hash-seeding bug in v1 HPO (fixed after run); no loss curves; per-sample predictions not stored; data cache not archived | cannot re-execute v1 bit-for-bit | v2 logs curves; archive hashes | fix + disclose + record dataset hashes | tests pass; hashes recorded | PARTIAL |
| RR-11 | D | MODERATE | methodological | At N=32 validation set = 6 samples → selection noise; GP single-start failures 1.4 % | N=32 conclusions noisy | No | tie-aware framing; limitation | stated | OPEN |
| RR-12 | C | MODERATE | literature | Most v1 sources read at abstract level | mis-citation risk | No | read closest full texts (Westermann ~200k/212k chars now); flag others | matrix 'reading depth' column | PARTIAL |
| RR-13 | F | MODERATE | statistical | Seeds draw nested subsets; seed variance underestimates sampling variance at large N | CIs too narrow | No | state; use instance-level inference | stated | OPEN |
| RR-14 | I | MODERATE | editorial | Journal guidelines/IF/quartile unverifiable (bot-gated, paywalled); "five closest recent papers" never done | compliance risk | No (can do for Engineering with Computers via Crossref) | Phase 5 | list produced | OPEN→Phase 5 |
| RR-15 | G | MODERATE | scientific | Alternative explanation for GP losses: stationary kernel rather than manifold complexity | mechanism unclear | partly (Exp D isotropic KRR) | discuss | stated | OPEN |
| RR-16 | A | MINOR | editorial | Title "Linear-subspace or neural?" implies general guidance | over-claim | No | precise title | title revised | OPEN→Phase 9 |
| RR-17 | H | MINOR | documentation | README/fit audit say six figures; manuscript has five | consistency | No | fix | corrected | OPEN |
| RR-18 | J | MODERATE | integrity | Pre-registration is a git history on the authors' own repo; reviews by same agent; AI-generated work | credibility | No | disclose clearly | declarations | OPEN |
| RR-19 | E | MINOR | statistical | Exploratory analyses uncorrected for multiplicity | false positives | No | labelled exploratory | stated | OPEN |
| RR-20 | D | MINOR | methodological | Cost analysis stylised (FOM ms-scale) | practical-value claims | No | keep descriptive | stated | OPEN |

**FATAL issues found: none** (no leakage, fabrication, or irreproducible reported number was found; the independent recomputation passed 11/11).
**Priority order for action:** RR-01 → RR-02 → RR-03 (new experiments, running) → RR-04/06/07/08 (re-analysis and rewrite) → rest.

## Resolution (updated at the end)
*(filled in `review/second_adversarial_review.md` and `submission_readiness_report.md`)*
