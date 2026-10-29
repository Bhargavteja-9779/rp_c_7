# SIMULATED reviewer comments and author responses
**This is a simulation, not a real peer review.** The "reviewer comments" are the substantive points raised by three rounds of review performed by fresh-context AI agents (not human reviewers) on earlier drafts, rephrased as a journal referee would write them. The "responses" state what was changed in `manuscript/Final_Manuscript_v4.md` or why not. Use it as preparation; real referees will raise different points.

**R1.1 — The claim that the GP advantage is due to marginal-likelihood fitting is not isolated; the kernel-ridge control had a restricted ridge range.** *Agreed.* We ran a pre-registered wide-range control (Exp H). Kernel ridge with wide ranges is a median 6.5× (8 trials) and 2.7× (32 trials) worse than the GP, against 14× for the narrow control. The marginal-likelihood claim was withdrawn; the paper now attributes the advantage largely to regression/search quality and states that a residual 2–3× is unexplained (Sections 4.3, 8, abstract).

**R1.2 — The no-POD GP was reported only where it supports the story.** *Agreed.* Full table added to the Supplement and summarised in 4.3 (full-field GP clearly beats the best network in 7 of 30 cells where POD+GP had lost; 3 of 9 at 1,024 runs). Statements about networks winning on moving features were weakened.

**R1.3 — The networks are under-trained; N=1024 counts have a step-count confound; Exp F is capped at 400 L-BFGS iterations.** *Agreed in part.* The step-count change is stated in Section 2 and in the discussion of every 1,024-run count; Exp F is described as "not overturned by the tested refits"; optimisation vs generalisation error was not separated (limitation). We did not run further network tuning.

**R1.4 — Shared search draws, 3-vs-2 members, and an uninformative edge statistic.** *Agreed.* Disclosed; the edge statistic was withdrawn.

**R2.1 — "Application" framing is not justified; the problems are textbook benchmarks solved by in-house code.** *Agreed.* The abstract, introduction and Section 3 now say the classes are named after application areas, nothing was calibrated to a real application, and no field or public benchmark data were used. We kept the plain title requested by the authors but removed "engineering" from the subtitle.

**R2.2 — The 19-vs-10 headline includes problems chosen for smoothness.** *Agreed.* The split is reported (9 vs 4 on the 24 main problems; 11 vs 5 excluding the eight smooth candidates only).

**R2.3 — Several typed statements about 16/32-input problems and darcyhd were wrong.** *Agreed and corrected* (4.1, Section 5).

**R2.4 — Comparisons in the mechanism sections use the best network by test error, contradicting "never on test data".** *Agreed.* Stated explicitly where used (Sections 2, 4.3, 4.5).

**R3.1 — Recorded solver times (≈6 ms) contradict "training time is minor" and the slow-simulation framing.** *Agreed.* Section 4.2 and the limitations now state that fitting costs more than simulating on our test problems; the practical comparison is accuracy per simulation run; the cost case holds only for much slower simulations.

**R3.2 — Original 16 problems do not reproduce bit-for-bit on a full re-run (process-dependent seed).** *Agreed and disclosed* in Section 7; the later experiments reproduce exactly.

**R3.3 — Novelty: the main finding is known (Batlle 2024, Bērziņš 2020, Westermann 2026).** *Agreed.* The paper says it confirms and quantifies earlier reports; contribution is the budget-aware map, the controls, and the sensitivity of verdicts to the comparison's own settings.

**R3.4 — No accountable human author, and AI-only review.** *Cannot be resolved by us.* The declarations, limitations and cover letter disclose this; human authors must be named, verify all content, and ideally obtain independent human review before submission.
