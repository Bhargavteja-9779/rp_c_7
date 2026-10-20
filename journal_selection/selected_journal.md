# Selected journal — decision record (Gate A: **FAILED as specified; best-available target chosen under a declared, non-silent interpretation**)

## 1. Gate-A outcome in one paragraph
The brief requires a journal that is (a) a JCR Q1 title (Q2 only as fallback), and (b) has a **credible, verifiable basis for ≤72 calendar days from submission to final acceptance**, with (b) a *mandatory eligibility filter* and (a) a *priority*. After scanning 2,423 non-MDPI journals (Springer, Wiley, T&F, ACM, IET, society publishers via Crossref) and PubMed-indexed Elsevier titles, **no journal was found that is both verifiably JCR-Q1/Q2 and credibly ≤72 days.** Specifically:

* Every JCR-listed AI / computing / computational-mechanics journal that could be measured has an observed median of **74–290 days** (e.g. JKSU-CIS 74; Computational Mechanics 116; Engineering with Computers 152; Scientific Reports 138; Neural Computing & Applications 254; Elsevier AI-in-medicine titles 91–287).
* Elsevier and IEEE do not deposit received/accepted dates in Crossref; their official "submission to acceptance" pages were bot-blocked (HTTP 403), so those journals are **TIMELINE UNVERIFIED — DOES NOT SATISFY THE HARD CONSTRAINT**.
* No journal can credibly promise a *maximum* of 72 days: all observed distributions have long tails (MLCSE max 205 d; JKSU-CIS max 266 d). The best any evidence can show is that most papers were accepted within 72 days.

## 2. Declared decision rule (stated before choosing; not tuned to a result)
Because a strict reading is unsatisfiable, the Director applied the brief's own priority order — **timeline = mandatory filter, quartile = priority** — with this operational test for "credible basis": *a full census (or ≥150-article sample) of recent articles shows median ≤60 d, Q75 ≤72 d and ≥75 % of papers ≤72 d.* Only a journal passing this is "timeline-supported". The test is explicitly **weaker than the brief's "maximum of 72 days"** and is flagged as such everywhere.

## 3. Result
| Role | Journal | Timeline evidence | JCR status | Verdict |
|---|---|---|---|---|
| **Primary target** | **Machine Learning for Computational Science and Engineering (MLCSE)**, Springer Nature, ISSN 3005-1428 (print) / 3005-1436 (online) | Full census of all 102 research articles 2024-09 → 2026-10: **median 50 d, Q75 65 d, Q90 97 d, 83.3 % ≤ 72 d, max 205 d** | **No Journal Impact Factor** (Springer collection page lists JIF "Not available"; journal began publishing 2024–25). Therefore **neither Q1 nor Q2 can be claimed.** | Passes the declared timeline test; **fails the Q1/Q2 priority**; fails strict "max 72 d". |
| Backup (Q1-first reading) | Journal of King Saud University – Computer and Information Sciences (Springer; 1319-1578 / 2213-1248) | Full census 2025-01 → 2026-10: n = 1,280, **median 74 d, Q75 99 d, 48.1 % ≤72 d, max 266 d** | Aggregators report Q1, but 2025 JIF values conflict (6.1 / 6.4 / 8.84); **not verified against JCR** | Fails timeline test; Q1 unverified. |
| Not eligible | All Elsevier / IEEE / PeerJ / OUP / SAGE journals in the candidate list | no accessible dates | not verified | TIMELINE UNVERIFIED |

**If the person commissioning this work reads the constraints as "Q1 first" the backup list above is the starting point, but it does not satisfy the 72-day requirement either.** The two constraints cannot currently be met together on public evidence.

## 4. Why MLCSE is scientifically appropriate (scope fit, independent of timeline)
* Recent MLCSE papers (listed from Crossref, `data/harvest_mlcse.csv`) are exactly this genre: PINN and neural-operator surrogates, reduced-order modelling, UQ for engineering systems, and *evaluation-methodology* papers ("The impact of data splitting methods on machine learning models", "Statistically grounded selection and validation of surrogate models for civil-engineering…", "Numerical study on hyperparameter settings for neural network approximation to PDEs", "Scientific reliability of physics-informed foundation models for engineering: a critical review").
* A rigorous, reproducible comparison of surrogate families with a predictive selection diagnostic is a natural fit; the journal explicitly welcomes ML-for-modelling work in science and engineering.

## 5. Not verified (must be confirmed by the authors before submission)
* Official aims & scope text, article-type list, word limits, reference style, figure specs, APC and data/code policy: **Springer pages are bot-gated (JS cookie challenge); not fetched.** The manuscript is therefore prepared in a generic Springer Nature research-article style and **must be re-checked against https://link.springer.com/journal/44379/submission-guidelines**.
* Whether "Received" in Springer metadata equals first-submission date (standard for Springer Nature, assumed, not verified for this journal; resubmitted manuscripts could differ).
* Publication model (hybrid; APC amount not verified).
* Any JCR/Scopus/WoS indexing (none verified).
* Observed timeline ≠ future timeline; our paper can be slower.

## 6. Principal rejection / mismatch risks
1. New journal with a thin track record; unknown rigor threshold (moderate quality bar visible in sample titles, but not measured).
2. Timeline outliers exist (17 % of papers > 72 d); a revision round alone can exceed 72 d.
3. No JIF → lower prestige than the brief intends.
4. Reviewers may regard a benchmarking/diagnostic paper as "not a new method".

Confidence in the *selection*: moderate on timeline (census), low on any prestige/quartile claim (none can be made).
