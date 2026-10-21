# Journal selection v2 — revised after user instruction (2026-10-21)

**User instruction (genuine message):** "Go for any journal with high impact factor, but for use need to get accepted." This **lifts the 72-day submission-to-acceptance filter** of the original brief. v1 (`selected_journal.md`, the 72-day analysis) is kept for the audit trail. New objective: the highest-impact journal at which this particular paper has a *realistic* chance of acceptance. No acceptance probability can be computed; the ranking below is a judgement from scope fit and the paper's actual strengths/weaknesses.

## Impact-factor evidence (ALL UNVERIFIED against Clarivate JCR — not accessible; aggregators conflict)
| Journal (publisher) | IF evidence | Source quality | Scope fit for this paper | Observed received→accepted (Crossref) |
|---|---|---|---|---|
| Computer Methods in Applied Mechanics and Engineering (Elsevier) | ~7.3–7.6 (8.39 outlier) | aggregators | Needs methodological novelty; a benchmark/diagnostic paper is a **stretch**. Precedent: CMAME published a "fair comparison of two neural operators" (Lu et al. 2022, DOI 10.1016/j.cma.2022.114778) | not measurable (Elsevier) |
| Engineering Applications of AI (Elsevier, IFAC) | ~8.0–10.9 (aggregators) | aggregators | Expects "novel AI for a real-world engineering application validated on public data sets" (secondary description); ours is synthetic PDEs → **scope risk** | not measurable |
| **Engineering with Computers** (Springer) | **4.9 (2024), "according to JCR"** | Wikipedia citing JCR (secondary); SCIE-indexed | Simulation-based engineering / CAE; strong topical fit | n=206 dated: **median 151 d**, Q75 220 d, 11 % ≤72 d |
| Machine Learning: Science and Technology (IOP) | **4.2** (CiteScore 6.7) | journal's own IOP page | "bridges the application of ML across the sciences"; also ML methods motivated by physics. Open access (APC amount not seen) | Crossref has no dates; IOP page: median 5 d to pre-review decision, 52 d after peer review (first decision, **not** acceptance) |
| Machine Learning for Computational Science and Engineering (Springer) | no JIF | — | good fit; fast (v1 census: median 50 d) | census n=102 |

## Decision
* **Provisional primary: Engineering with Computers.** Best balance of impact factor (≈ the highest I can support for a plausible fit), indexed in SCIE, and scope fit for a simulation-based-engineering benchmarking paper. Trade-off accepted: lower IF than the aggregator-reported figures of CMAME / EAAI, which I judge to have materially higher desk-rejection risk for *this* contribution (benchmark + diagnostic on synthetic problems, small networks, 16 instances).
* **Final choice is conditional on the pre-registered results** (decided when the analysis completes, by the rule below, not by preference):
  * If **H2 passes** (the pilot diagnostic reliably beats baselines out-of-sample) → the contribution is a genuine predictive result; a **stretch submission to CMAME** is defensible before falling back.
  * If **H2 fails** (negative/benchmark paper) → submit to **Engineering with Computers**, then **MLST**, then **MLCSE** (fastest, no JIF).
* Cascade rationale: rejection from a high-IF journal costs months; the fallback order goes from higher to lower selectivity only when the evidence supports the stretch.

## Honest limits
* No JCR access: every IF/quartile above is secondary. "Q1" cannot be asserted for any journal in this file (Engineering with Computers is reported Q1 only in Scopus-style subject categories by one aggregator).
* Springer/Elsevier/IOP author-guideline pages are bot-gated here; formatting must be checked by the authors on the journal site.
* APCs and open-access conditions not verified.
* Acceptance cannot be guaranteed or even estimated numerically.

## Decision after the pre-registered results (rule applied as declared above)
H2 **failed** (Holm-adjusted p = 0.145), so the stretch submission to CMAME is **not** justified. Applying the declared fallback order: **Engineering with Computers → Machine Learning: Science and Technology → Machine Learning for Computational Science and Engineering.** Editorial risk (review 09): moderate at Engineering with Computers, moderate-high at CMAME/EAAI, lower at MLST/MLCSE. Because the paper is a benchmark/negative-result study, a fit-matched journal is more likely to accept it than a higher-impact one; the user's goal ("high impact factor but must get accepted") is therefore best served by Engineering with Computers first, not by CMAME or EAAI. This remains a judgement, not a probability.
