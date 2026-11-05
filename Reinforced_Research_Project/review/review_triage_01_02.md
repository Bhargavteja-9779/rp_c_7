# Triage of simulated reviews 01 (scientific validity, integrity) and 02 (presentation, compliance)
Both reviews were written by fresh-context AI agents (not human reviewers). Each finding was checked before acting. "Fixed" = changed in the paper, tables or code; "Stated" = kept and disclosed; "Not fixable" = needs the authors.

## Review 01 (verdict: major revision; no critical issue; all 24 headline numbers reproduced from raw JSON)
| ID | Finding | Verified | Action |
|---|---|---|---|
| M1 | A fixed choice (always gp_full[rbf]) already passes the H1a criterion; the stated null (random pick) is a strawman; "oracle" undefined in the abstract | yes (median regret 1.14, 75 % within 2) | **Fixed**: fixed-member baseline and tool-vs-best-fixed counts reported (§6.3); "oracle" defined in abstract and §6.3; "far from chance" no longer used as evidence of value |
| M2 | "Strongly tuned" network not shown strong; "twice the budget" understates (4× epochs, float64, L-BFGS); H4 = 2 problems × 2 budgets | yes (tuned network improves on benchmark networks in 15 of 16 cells, median ratio 0.64, still far above the tool on smooth problems) | **Fixed**: renamed "tuned network"; budget described fully; H4 reported as problems; "says little about a well-tuned network" |
| M3 | H3: 15 "cells" are 5 distinct cells × 3 seeds from 4 problems; recall ≈ 47 %; flag adds no decision beyond selection | yes | **Fixed**: counts, recall, "explained a decision rather than changed it" |
| M4 | Intervals/Holm treat 24 cells as independent; problem-level Wilson lower bound 68 % | yes | **Fixed**: problem-level (cluster) intervals added; p-values for B2; verdicts stated as descriptive of 8 problems |
| M5 | H2 met only through N0 = 64; N0 = 256 gives 62 % | yes | **Fixed**: stated; abstract gives both numbers |
| M6 | Retrospective run (addendum 6.4) not delivered; Table S1 omits Stage 6; "one problem" should be three | yes | **Fixed**: run made and reported (Supplement S-retro, V11; the tool's largest regret there is a failure on fisher_L1); Table S-prereg extended; text says three problems; the addendum's false statement ("no error seen") is acknowledged |
| M7 | "Independent" = solver-independent; mechanism claim over-reaches | yes | **Fixed**: "problems solved by third-party code"; "explains" → "describes"; post hoc control labelled; marginal likelihood not isolated (stated in abstract-level wording and §6.2) |
| m1–m8 | wording inconsistency (3 vs 5 of 8), two numbers for the narrow KRR control (different cell sets), better/worse thresholds, R2 ties and POD rank one on real data, bib name | yes | Fixed (cell sets stated; real-data caveats stated; bib name repaired) |

## Review 02 (verdict: major revision on presentation; no result invalidated)
| ID | Finding | Action |
|---|---|---|
| M1 | Cross-document references printed file names (xr-hyper + cleveref) | **Fixed** (plain `\ref` for external labels; build check for leaks: 0) |
| M2 | "three of eight" vs five | **Fixed** (macro) |
| M3 | Abstract > 250 words, too many numbers, "explains" | **Fixed** (241 words; fewer numbers; "describes") |
| M4–M5 | "basis rank" claim not shown; "pre-registered" for a self-hosted history | **Fixed** ("pre-specified"; claim removed) |
| M6–M8 | Figure problems (colours, fonts, duplicated sample, uncited Fig. 5, tick collisions) | **Fixed** (Fig. 2 redesigned; fonts ≥ 6.5 pt; duplicates removed; Fig. 5 cited and relabelled) |
| M9 | Supplement deviations table cut off | **Fixed** (itemised list) |
| M10–M13 | Metrics as equations; complexity analysis; reach-target base rate; 16 vs 24 cells | **Fixed** |
| M14–M16 | Undefined "the benchmark"; typed numbers; counts below ten as digits | **Fixed** (defined; lint `lint_numbers.py` finds 0 typed numbers outside an allow-list of protocol constants; count macros emit words below ten) |
| M17 | Placeholders (authors, journal, DOI, funding) | **Not fixable** by the assistant: needs the authors |
| M18 | Empty conclusion file | **Fixed** |
| minor | double full stops, Table 1 header, bib formatting, software citations, hyphen as minus, 62.5 → 62 | **Fixed** |
| Journal fit | no slow-simulation case; no comparison with existing tools; few independent units | **Stated** as limitations (§Discussion 1, 3, 6) — would need new work |
