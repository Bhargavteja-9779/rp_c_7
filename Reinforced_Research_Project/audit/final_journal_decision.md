# Final journal decision (supersedes `audit/journal_fit_assessment.md` interim) — 2026-10-22

## Constraints (from the master prompt; none silently relaxed)
Q1 by JCR preferred, Q2 only as fallback; no MDPI; **submission → final acceptance ≤ 72 days** (hard); never confuse first decision with acceptance; never state JCR quartile/IF or timelines that were not verified. An earlier user message ("any high impact factor journal, but it must get accepted") relaxed the timeline in one interim step; the later prompts re-imposed it. Both are reported.

## What could and could not be verified
* **JCR/Clarivate** (quartile, IF) is inaccessible from this environment → *no quartile is verified for any candidate*. Impact-factor figures in earlier notes come from journal pages or aggregators and are labelled unverified.
* **Observed accepted-paper histories** (not policies, not guarantees; survivor-biased because only accepted papers appear): Crossref received→accepted dates for Springer/Wiley records; Elsevier and IEEE do not deposit them (unmeasurable).

| Candidate | JCR quartile | IF (source) | Observed received→accepted | ≤72 d? | Scope fit for this manuscript |
|---|---|---|---|---|---|
| Machine Learning for Computational Science and Engineering (Springer) | none verified; journal appears to have **no JIF** | – | census n=102: median 50 d, Q75 65 d, 83% ≤72 d | passes the *observed-census* test; no guarantee | **good**: recent papers on surrogate selection, data splitting, hyper-parameter studies |
| Machine Learning: Science and Technology (IOP) | not verified | 4.2 (journal page, unverified) | Crossref has no dates; random sample of 150 recent (2025-07 to 2026-09) article pages, 35 with readable received/accepted dates: median 126 d, 8.6% ≤72 d (small, survivor-biased sample); page states first-decision times only | **not supported** | plausible (ML across sciences); benchmark/negative-result policy unknown |
| Engineering with Computers (Springer) | not verified | 4.9 (aggregator citing JCR, unverified) | n=206 all articles: median 151 d, 11% ≤72 d; surrogate/neural subset n=47: median 172 d, 4.3% ≤72 d | **not supported** | **weak**: 44/47 recent surrogate papers propose new methods; benchmark/negative-result papers atypical (title-level evidence) |
| J King Saud Univ – CIS (Springer) | reported Q1 by aggregators, unverified | conflicting (6.1/6.4/8.84) | census n=1280: median 74 d, 48% ≤72 d | **fails** (median > 72) | weak (CS-general) |
| CMAME / EAAI (Elsevier) | unverified | ≈7.3–7.6 / ≈8–11 (aggregators) | not measurable | **unverifiable** | stretch / mismatch for a benchmark with mostly negative confirmatory results |

## Decision
**NO VERIFIED JOURNAL MATCH UNDER THE CURRENT HARD CONSTRAINTS.** No candidate has both a verifiable Q1 (or Q2) quartile and observed ≤72-day acceptance histories. The 72-day requirement is therefore **not** satisfied and is not labelled as satisfied.

**Fit-based fallback ordering for the authors to decide (not a recommendation to submit, and not a claim that acceptance within any time is likely):**
1. MLCSE — the only candidate whose *observed* history is compatible with ≤72 days and whose scope matches a benchmark/methodology study; **no JIF**, so the quartile requirement fails outright.
2. MLST — Q1 status and IF must be checked by the authors in JCR; observed accepted-paper timeline (median 126 d) is incompatible with 72 days; first-decision timelines on the journal page are *not* acceptance times.
3. Engineering with Computers — best-known IF among the candidates, but poor scope fit and observed timeline far above 72 days.

**Actions required of the authors before any submission:** (a) verify current JCR quartile/IF and the journals' author guidelines (word/figure limits, reference style, data/code policies, AI-use disclosure rules, preprint policy); (b) decide whether the 72-day or the Q1 constraint takes priority, since no candidate meets both on available evidence; (c) fill in the author/affiliation/funding/competing-interest blocks; (d) deposit code and data with a persistent identifier.
