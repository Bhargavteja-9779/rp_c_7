# Review 02 — Domain and literature

*Simulated adversarial pass by the Research Director (not an independent human or external reviewer). Each pass was written separately after the previous one's fixes.*

**Stance:** find missing competing work and mis-citations.

| ID | Severity | Issue | Disposition |
|---|---|---|---|
| 2.1 | MAJOR | No operator-input architectures (FNO, DeepONet) and no intrusive POD-Galerkin, which are the usual comparators. | Listed as limitation (§7 items 2, 5). Not fixable with the finite-dimensional-parameter setting without redesign. |
| 2.2 | MODERATE | Missing reduced-order-modelling literature on GP/kernel regression of POD coefficients beyond one citation (Guo & Hesthaven 2018, verified by Crossref metadata, title-level only). | Partially fixed (citation added). Authors should survey this literature. |
| 2.3 | MODERATE | Most cited papers were read at abstract level only (flagged in §2 and `literature_matrix.csv`). | Disclosed; cannot be fixed without full-text access. |
| 2.4 | MINOR | Reference accuracy: one DOI initially guessed incorrectly was caught by Crossref verification (McGreivy & Hakim). Remaining non-Crossref items (JMLR, ICLR, NeurIPS) are verified only via jmlr.org/arXiv listings. | `references_verified.csv` records provenance. |
| 2.5 | MINOR | Kontolati et al. and Krishnapriyan et al. were verified but removed because the manuscript does not use them. | Done (no uncited padding).
