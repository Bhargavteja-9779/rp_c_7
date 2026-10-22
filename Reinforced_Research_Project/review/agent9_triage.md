# Triage of the independent literature/citation audit (agent report: `agent9_literature_citation_audit.md`)

The agent is an AI sub-agent with fresh context (not a human, not an external peer reviewer). Each finding was checked by me before acting.

| Agent finding | My verification | Action |
|---|---|---|
| Huang & Stuart wrongly described as "end-to-end cost" | **Confirmed** — I read the abstract earlier ("data-acquisition and training costs … fixed and fully amortized"); my v3 draft regressed | Fixed in `static_v3.md` |
| Lee & Carlberg mis-cited as a μ→field regression network | **Confirmed** (projection ROM with convolutional autoencoder) | Replaced by Fresca & Manzoni 2022 / Franco 2023 in §1; Lee & Carlberg re-described in §2 |
| Greif & Urban / Cohen & DeVore over-stated | Accepted as plausible (my abstract-level reading cannot establish more) | Claims narrowed in §1 |
| "FNO faster for rough inputs" ambiguous | Confirmed: abstract says "fastest convergence rates" | Reworded |
| Bergstra & Bengio does not show B = 8 adequate | Accepted | Reworded to "efficient alternative to grid search" |
| Reading-depth percentages false precision; v1 vs v3 inconsistent | **Accepted** (my WebFetch windows of 100k chars each do not map reliably to a percentage) | Replaced by qualitative disclosure; search-coverage gap (q3 zero hits) disclosed |
| Missing: Bērziņš 2020 (POD+RBF/GPR/ANN; GPR advantageous) | **Verified** (arXiv abstract read in full) | Added; positioned as nearest precedent; reduces novelty of the qualitative POD+GP result |
| Missing: Lanthaler 2023 (slow PCA-eigenvalue decay as obstacle) | **Verified** (arXiv abstract) | Added as theoretical rationale for the spectral feature |
| Missing: Mora 2025 CMAME, Kontolati 2023, Dama & Nair 2026, Lanthaler & Stuart 2025, Kovachki et al. 2024 | Existence verified (Crossref/arXiv); relevance only at title/abstract level | Mora, Lanthaler & Stuart, Kovachki et al. added to matrix; Kontolati/Dama & Nair noted, not cited (not used) |
| Dodge 2019 / Bouthillier 2021 absent from v3 | Confirmed (they were only in the CSV) | Cited in §2 where tuning-budget reporting is discussed |
| Author lists of Westermann (+Zech) and Zhang (+Khodak) incomplete | **Verified** via arXiv API | Corrected in final reference list |
| Williams & Cremaschi pages 353-358 vs 353-359 | Not yet verified (publisher page 403) | Resolve in reference audit |
| Novelty verdict: DIFFERENTIATED BUT INCOMPLETELY VALIDATED | **Concur** | Adopted |
