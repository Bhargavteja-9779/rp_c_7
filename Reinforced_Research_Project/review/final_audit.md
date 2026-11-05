# Final audit (2026-11-05) — written by the AI research assistant after three simulated review rounds by fresh-context AI agents (not human reviewers)

## Readiness decision: **conditionally ready — for a methodology/software venue, not for a venue that expects a validated general selection method**
Conditions: (1) human authors named, all numbers/claims/citations checked by them, and independent human review obtained; (2) journal and template chosen, guidelines and page limit checked; (3) archive DOI created; (4) the authors accept the limits below. No acceptance outcome or time is predicted or promised.

## What is established
* All headline numbers were recomputed from raw per-job JSON by independent agents (review 01: 24/24; review 03: all, plus bit-identical re-runs of the tool in a fresh clone). 56 benchmark tests, 10 tool tests pass; the paper builds with 0 undefined references, 0 LaTeX errors, 1 trivial overfull box per document.
* The tool selects a near-oracle member in all 24 cells of eight third-party-solver problems (regret ≤ 1.18) and beats a fixed member chosen without hindsight (regret 1.69). It was no worse than always-POD+GP. Its basis check flagged only cases where a full-field model was better (low recall). The error forecast is usable from 64 runs (92 %) but not from 256 (62 %).
* Negative or mixed results are in the main text: H1c (does not match the benchmark's own selection among methods that include networks), H5 (benchmark finding on 3 of 8 problems only), forecast too optimistic at 256 runs, tuned-network criterion met only at its limit, in-sample worst-case regret 9.25, cost exceeds the simulation cost on our fast solvers, pilot diagnostic not confirmed, real-data check degenerate (scalar outputs).

## Risk ratings (honest)
| Area | Risk | Why |
|---|---|---|
| Novelty | **High** at method-oriented venues | classical pool; main finding (GP/kernel hard to beat on smooth problems) known; novelty is the procedure, the controls and the evaluation; related-work search limited |
| Scale | **High** | 8 third-party problems from 4 families; 44 simulated problems in total; cells within a problem not independent |
| Data | **High** | all simulated; fast solvers (ms); real check uses scalar noisy outputs; no public benchmark (e.g. PDEBench), no slow-simulation case |
| Statistics | Medium | problem-level intervals given; several criteria met at their limits; Holm over only the tests that admit one; seeds share pool and test set |
| Baselines | Medium–High | tuned network (16 trials, narrowed space, one core) is probably under-trained; the default pool has no network and the tool never recommends one |
| Registration / process | Medium | self-hosted git history; some post hoc stages (labelled); known exceptions listed in Supplement S2 and V9–V13; AI-agent reviews only |
| Writing | Low–Medium | plain style, numbers from macros (lint clean); length 29 pp (journal limit unknown); placeholders remain |
| Ethics / disclosure | Low | no human/animal subjects; public CC BY 4.0 data; AI involvement disclosed in acknowledgments and cover letter |
| Fit with the journal | **High / unresolved** | no verified Q1 journal with an observed ≤ 72-day acceptance history; see `audit/final_journal_decision.md` |

## Main remaining rejection risks
1. "No new method; known finding" (method venues). 2. "Only simulated, fast-solver problems; no slow-simulation case; no comparison with existing surrogate-selection tools." 3. "Few independent problems; criteria met at their limits; forecast fails from 256 runs." 4. "Network baseline weak; tool cannot recommend a network." 5. "Entire pipeline and reviews AI-made; no human accountability yet."

## What the authors must do (not done by the assistant)
Author names, affiliations, corresponding author, funding, competing interests, ethics statements, date; choose journal/template, check page limit and guidelines; create a public repository/archive DOI and fill the availability statement; approve the submission (all authors); decide whether to add a slow-simulation case study or a public benchmark before submission; obtain human review.
