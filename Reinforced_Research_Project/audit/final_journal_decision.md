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

## Outcome record (added 2026-11-12, from the decision email forwarded by the author)
The manuscript was submitted to Machine Learning for Computational Science and Engineering (the fit-based first choice above) and **rejected** on 2026-11-12. The editor's stated reason, in full: "The paper is not strong enough in its research considering the Aims & Scope of the journal." No reviewer reports or specific criticisms were given. This matches rejection risk 1 ("thin contribution for a methods paper") in `review/final_audit.md` and review 04, but the email does not say which weakness decided it, so no specific cause is claimed. Whether the 72-day constraint would have been met is unknown (the submission date is not in the record).

## Second selection round (2026-11-12) — user relaxed the limit to 100 days (Q1 still wanted; no MDPI)
Method: `audit/journal_census_v2.py` reads received/accepted dates that Springer Nature and Wiley deposit in Crossref for articles published since 2025-01 (results in `results/journal_census_v2.json`). Observed history only: accepted papers only, so it says nothing about the chance of acceptance, and the clock restarts after a rejection. Elsevier, IEEE and several others do not deposit dates (not measurable). Quartiles come from aggregator pages and were **not** verified in JCR or SCImago.

| Journal (publisher) | n with dates | median days | share ≤ 100 d | Quartile (unverified) | Scope fit |
|---|---|---|---|---|---|
| Acta Mechanica Sinica (Springer) | 530 | 34 | 93 % | aggregator: Q1, IF 4.6 (2024) | moderate: mechanics; publishes surrogate/ROM/neural-network application papers |
| Computational Mechanics (Springer) | 284 | 119 | 36 % | likely Q1 (unverified) | good: reduced-order and surrogate methods, but expects methodological novelty |
| Scientific Reports (Springer Nature) | 600 | 135 | 30 % | Q1/Q2 varies by category | broad; many surrogate application papers |
| Engineering with Computers (Springer) | 342 | 147 | 25 % | unverified | weak (new-method papers) |
| Structural and Multidisciplinary Optimization (Springer) | 494 | 140 | 17 % | aggregator: Q1 | needs link to design optimisation |
| Int J Numer Meth Eng (Wiley) | 460 | 168 | 20 % | unverified | moderate |
| Neural Computing and Applications, J Sci Computing, Stat and Computing, Soft Computing | 140–587 | 229–386 | < 6 % | – | not compatible with 100 days |

Only Acta Mechanica Sinica is compatible with a 100-day limit on observed history. No journal can be shown to meet "Q1 and ≤ 100 days and high chance of acceptance"; the last cannot be estimated from public data.

## Third selection round (2026-11-12) — no time limit; one journal chosen for fit, then the paper is adapted to it
**Choice: Advances in Engineering Software (Elsevier, ISSN 0965-9978).** Reasons (evidence in the record, all of it third-party text or Crossref titles; nothing below is verified against JCR/SCImago or the journal's own guide, which returned a bot-challenge page): (1) the journal's stated objective is advances in computer-based engineering techniques leading to practical problem solving in mechanical, civil, aerospace and environmental engineering, and its scope lists numerical algorithms, analysis and simulation, accuracy/efficiency control, AI-based methods, design automation, and software reviews; the paper is a software tool plus an evidence study for engineering simulation, which is the journal's kind of contribution; (2) recent Crossref titles show it publishes surrogate-modelling work for engineering simulations (mostly applications), so a selection tool is in scope; (3) an engineering-software journal values tested, documented software and honest validation more than a new regression method, which is where the paper was judged thin by the previous editor; (4) aggregators report CiteScore of about 7 and Q1-level standing (**unverified**; the authors must check JCR); (5) no time limit now, so the lack of observable acceptance dates (Elsevier does not deposit them) does not matter. Rejected after comparison: CMAME and Computational Mechanics (expect a new method; the paper has none), Machine Learning: Science and Technology (expects ML novelty), Engineering with Computers (new-method papers), Scientific Reports (broad; quality signal weaker), Data-Centric Engineering (fit is plausible, journal standing unverified).
**No probability of acceptance can be computed from public data and none is claimed.** Fit is the only lever; the other is the strength of the paper, addressed in Stage 8 (tool features, software documentation, a genuinely expensive engineering case, journal-specific framing).
**Fallback order if rejected (authors to decide):** Journal of Computational Science; Machine Learning: Science and Technology.

## Fourth selection round (2026-11-18) — user: submit as is, accepting the risk; no article charge (subscription route), low rejection risk, as fast as possible; or split into two papers
Method: web searches (journal pages, third-party aggregators) and `audit/journal_census_v3.py` (Crossref received/accepted dates, Springer and Wiley only; results in `results/journal_census_v3.json`). **No rejection probability can be computed; none is claimed.** Quartiles, impact factors and fee terms were not verified against primary sources and must be checked on the journals' own pages.
| Venue | Author charge (as found; verify) | Observed received→accepted | Scope fit for a software + evidence paper | Notes |
|---|---|---|---|---|
| Advances in Engineering Software (Elsevier) | hybrid: an open-access fee of about 3,980 USD is listed (Elsevier page snippet); the subscription route normally carries no author fee (verify) | not measurable (Elsevier does not deposit dates) | best: the journal's scope names software tools and AI methods for engineering simulation | paper already adapted for it |
| Acta Mechanica Sinica (Springer) | not found; Springer hybrid journals normally allow a no-fee subscription route (verify) | n=590, median 34 days, 93 % within 100 days | moderate: mechanics incl. data-driven mechanics; editors pre-screen suitability | fastest by far; a software/evidence paper is off its core |
| Acta Mechanica (Springer) | as above | n=591, median 101 days, 50 % within 100 days | weaker | |
| Engineering with Computers (Springer) | as above | n=342, median 147 days | good scope for software, but it discourages papers that only apply established methods | |
| Software: Practice and Experience (Wiley) | hybrid (verify) | n=152, median 214 days | software design and implementation in general | slow |
| Journal of Open Source Software | no author charge (verify) | n/a | software papers | **blocked for now**: requires a public repository with more than six months of active development history; AI use must be disclosed; earliest mid-2027 |
| JMLR Machine Learning Open Source Software | no fee found (verify) | n/a | open-source ML software, 4-page paper | needs evidence of an active user community; none yet |
Recommendation recorded: submit the single adapted paper to Advances in Engineering Software on the subscription (no-fee) route; fast fallback Acta Mechanica Sinica after re-framing to mechanics. A two-paper split (software paper + evidence paper) is possible but doubles the rewrite and gives the evidence paper the weaker novelty case.
