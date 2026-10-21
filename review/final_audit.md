# Final audit, gate status, rejection-risk report and readiness decision

## A. Readiness decision

# **NOT READY — ADDITIONAL WORK REQUIRED**

No fatal scientific or integrity flaw was found, but submission is blocked by items only the human authors (or further compute) can supply. Submission readiness would not mean acceptance; **acceptance cannot be predicted or guaranteed.** The most likely outcome at a high-impact journal is rejection on contribution grounds (see §D).

### Blockers (must be resolved before submission)
1. **Author block, affiliations, funding, conflict of interest, ethics statement, author contributions, originality/not-under-review declarations** — placeholders only; none fabricated.
2. **Permanent code/data deposit** (e.g. Zenodo DOI). The repository is a working branch of a GitHub repo; the manuscript says so and must be updated.
3. **Journal guidelines unverified** (Springer/Elsevier/IOP pages are bot-gated). Formatting, article type, word limits, reference style, figure specs, APC, AI-use policy must be checked and the manuscript converted to the journal template.
4. **"Five closest recent papers in the target journal" comparison not performed.**
5. **Impact factor / JCR quartile unverified for every journal** (no Clarivate access). The original hard constraints (JCR Q1/Q2 and a verifiable 72-day acceptance basis) could not be jointly met (journal_selection/selected_journal.md); the user subsequently directed "any high-IF journal, but it must get accepted" (selected_journal_v2.md).
6. **Human responsibility for AI-generated content** (study design, code, text) and compliance with the journal's AI policy.

### Optional scientific strengthening (would reduce risk, needs compute/new design)
Seeds 3–4 (pre-planned, not run); more PDE families (power for H2); FNO/DeepONet and intrusive POD-Galerkin comparators; multi-start GP optimiser; larger NN training budgets; N>1024; real-world engineering case study.

## B. Quality gates
| Gate | Status | Comment |
|---|---|---|
| A Journal feasibility | **FAILED as specified; revised by user instruction** | 72-day + Q1 not jointly satisfiable on public evidence; v2 selection is provisional, IF unverified |
| B Research opportunity | Pass (moderate) | gap chain documented; prior art read partly |
| C Novelty | **Conditional pass, low-moderate** | See review 01/10 |
| D Experimental feasibility | Pass | executed on CPU |
| E Methodological validity | Pass with disclosed limits | leakage tests, matched tuning, frozen protocol |
| F Evidence | Pass | all reported numbers traced to results files; two of four pre-registered hypotheses' predictions failed, reported |
| G Statistical validity | Partial | low power; H4a fragile; H2 inconclusive |
| H Independent review | Partial | reviews were simulated by the same agent; **no external reviewer** |
| I Reproducibility | Partial pass | tests 27/27 in fresh clone; analysis from committed raw results reproduces statistics with 0 differing fields; quick pipeline re-run (see §C); full NN re-execution on different hardware not performed |
| J Submission readiness | **FAIL** | blockers above |

## C. Reproducibility audit (fresh clone from the remote branch)
* `pytest`: 27 passed.
* `run_all.py --mode full --stage analysis`: all statistics and tables identical to the original (0 differing numeric fields; `cells.csv`, `family_winner_y.csv` identical).
* `run_all.py --mode quick` re-executed after moving the committed quick outputs aside: see `QUICK2` line below.
* Not done: full re-run of the 48 jobs; regeneration of exploratory analyses (need the data cache) in the clone; manuscript rebuild in the clone.
* Known non-determinism risk: NN training across hardware/BLAS; GP optimiser local optima.
QUICK2_PLACEHOLDER

## D. Rejection-risk report
| # | Risk | Evidence | Severity | Fixed? | Further experiments? | Residual |
|---|---|---|---|---|---|---|
| 1 | Journal-scope mismatch | fit audit: EwC moderate; CMAME/EAAI weaker | Moderate | n/a | no | Moderate |
| 2 | Insufficient novelty | reviews 01, 10 | **High** | No (inherent) | no | High at high-IF |
| 3 | Insufficient significance | synthetic suite | High | No | new problems/real case | High |
| 4 | Weak gap justification | prior art partly read | Moderate | Disclosed | full-text reading | Moderate |
| 5 | Methodological weaknesses | B1 degenerate; GP single start | Moderate | Disclosed/quantified | multi-start GP | Moderate |
| 6 | Dataset limits | synthetic, p<=10 | High | Disclosed | yes (real/high-dim) | High |
| 7 | Data leakage | tested | Low | Controlled | no | Low |
| 8 | Weak/unfair baselines | E1, E6; no FNO/DeepONet | Moderate | Partly | yes | Moderate |
| 9 | Statistical uncertainty | 3 seeds, 8 families, H4a fragile | Moderate-High | Disclosed | seeds 3-4, more families | Moderate-High |
| 10 | Insufficient robustness | E1,E2,E5,E6 done; no noise/shift tests | Moderate | Partly | optional | Moderate |
| 11 | Limited generalisation | suite-limited | High | Disclosed | yes | High |
| 12 | Incomplete experiments | seeds 3-4 not run | Moderate | Disclosed | yes | Moderate |
| 13 | Computational feasibility | N<=1024 | Low | — | — | Low |
| 14 | Reproducibility | no permanent deposit | Moderate | Partly | deposit | Low after deposit |
| 15 | Citation accuracy | 25 refs verified; abstract-level reading | Moderate | Partly | authors read full texts | Moderate |
| 16 | Manuscript clarity | 10 pages, figures checked visually | Low | Fixed | no | Low |
| 17 | Author-guideline compliance | unverified | High | **No** | no | High until checked |
| 18 | Ethics / integrity | simulated data; AI-use disclosure needed; pre-registration only a git timestamp | Moderate | Disclosed | no | Moderate |
| 19 | Timeline uncertainty | EwC observed median 151 d (n=206) | Moderate | n/a | no | Moderate |
| 20 | Technical limitations | see manuscript §7 | Moderate | Disclosed | — | Moderate |

## E. Consistency audit
`review/check_claims.py` (14 automated checks, all PASS at the time of writing): result-row counts, finite errors, Holm verdicts, hard-coded numbers (GP instability counts, 79% claim), pre-registration commit ordering, absence of template residue, placeholders preserved, no acceptance/SOTA claims. Manual checks: figures visually inspected (two defects found and fixed: invalid learning-curve bands; degenerate LOFO axes); every in-text citation resolves to the reference list and every reference is cited; manuscript numbers are generated by `manuscript/build_manuscript.py` from result files.
**Known inconsistencies/open items:** none numeric; the narrative states pre-registered expectations that proved wrong; the DOCX is a generic format, not a journal template.

## F. Items I could not do or verify (explicit)
JCR/Clarivate data; official author guidelines; five closest journal papers; independent external review; permanent archive; seeds 3-4; full-text reading of most cited works; any claim about acceptance probability.
