# Review 01 — Novelty and significance

*Simulated adversarial pass by the Research Director (not an independent human or external reviewer). Each pass was written separately after the previous one's fixes.*

**Stance:** attempt to show the contribution is incremental or already known.

| ID | Severity | Issue | Evidence | Disposition |
|---|---|---|---|---|
| 1.1 | MAJOR | The headline qualitative result (linear subspaces win on smooth manifolds; networks gain on slow n-width problems) is textbook (Cohen & DeVore 2015; Greif & Urban 2019; Franco et al. 2023). | `literature_review/novelty_map.md`; Fig. 3 | **Accepted, not fixable by wording.** Manuscript no longer claims it as new; contribution restated as matched-tuning evidence + tuning-asymmetry measurement + a *failed* pre-registered diagnostic. |
| 1.2 | MAJOR | The two pre-registered "novel" hypotheses (H2 diagnostic, H1) failed; only H4a (an expected bias) passed and is fragile (5/16 instances). | statistics.json; e4_robustness.json | **Accepted.** Paper framed as benchmark / negative-result study; abstract and conclusions already state this. Novelty remains LOW-MODERATE. |
| 1.3 | MODERATE | Closest prior art (arXiv:2604.00689) was read only in part (~100k of 212k chars); novelty statements about 'no pilot predictor' are bounded to the read portion. | novelty_map.md | Disclosed in §2. Cannot be resolved without full reading by authors. |
| 1.4 | MINOR | "To our knowledge" claims rest on web search of arXiv/Crossref only; no Google Scholar, patents. | novelty_map.md | Disclosed. |
**Verdict:** significance is limited; the work would not suit a venue that requires methodological novelty.
