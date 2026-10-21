# Journal-fit audit (provisional target: Engineering with Computers; fallbacks MLST, MLCSE)

*Based on secondary information only: Springer / Elsevier / IOP author-guideline pages are bot-gated here. Items marked UNVERIFIED must be checked by the authors on the journal sites.*

| Editorial requirement | Evidence in manuscript | Status | Required correction |
|---|---|---|---|
| Scope alignment (simulation-based engineering / CAE) | Parametric-PDE surrogates, solvers, reduced-order modelling | Pass (moderate) | Confirm scope text on journal page (UNVERIFIED) |
| Novelty threshold | Matched-tuning benchmark; failed pre-registered diagnostic; tuning asymmetry | **Borderline** | None possible by wording; consider MLST/MLCSE if rejected |
| Scientific significance | Limited to a 16-instance synthetic suite | Borderline | State limits (done) |
| Methodological rigor | Pre-registration (git), leakage tests, matched tuning, Holm correction | Pass | — |
| Experimental depth | 1,440 runs + post-hoc robustness | Pass | — |
| Baseline quality | POD+GP/Poly/MLP + MLPs; no FNO/DeepONet/POD-Galerkin | Partial | Disclosed |
| Statistical validity | Pre-specified tests; fragile H4a; low power | Partial | Disclosed |
| Reproducibility | Code, tests, fresh-clone audit | Pass (code) / **Fail (permanent data/code deposit missing)** | Deposit repository (e.g. Zenodo) |
| Writing and presentation | 10-page DOCX/PDF, Unicode math, 6 figures | Pass | Journal template conversion (UNVERIFIED requirements) |
| Journal compliance | Author block, funding, COI, AI-use disclosure placeholders | **Fail until completed** | Authors must supply |
| Impact factor / indexing | Engineering with Computers IF 4.9 (2024, via Wikipedia citing JCR); SCIE-indexed per Wikipedia | UNVERIFIED | Check Clarivate |

## Five closest recent papers in the target journal
**NOT PERFORMED.** I could not retrieve or verify the journal's recent articles on surrogate modelling (the closest evidence is a Crossref-derived list for MLCSE, not for Engineering with Computers). The brief requires this comparison; it remains an open task for the authors.

## Desk-rejection simulation
See `review/review_09_associate_editor.md`. Risk: MODERATE at Engineering with Computers, MODERATE-HIGH at CMAME/EAAI, LOWER at MLST/MLCSE.
