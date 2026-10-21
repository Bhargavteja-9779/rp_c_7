# Journal-fit assessment (Phase 5) — INTERIM (finalised after Exp A/B/D in `submission_readiness_report.md`)

## Constraints applied (as instructed in this cycle)
No MDPI; prefer JCR Q1, Q2 only as fallback; **retain ≤ 72 days submission → final acceptance**; do not confuse first-decision with acceptance; do not misstate IF/quartile; do not label an unverified timeline as compliant. *Note:* an earlier user message in this session asked for "any high-IF journal, but it must get accepted"; the present instruction re-imposes the 72-day filter. Both are reported; neither is silently relaxed.

## Evidence (all observed history; none official)
| Journal | JCR/IF evidence | Observed received→accepted (Crossref, accepted papers only) | Fit for *this* paper type | 72-day verdict |
|---|---|---|---|---|
| **Engineering with Computers** (Springer) | IF 4.9 (2024) per Wikipedia citing JCR — **unverified** | all articles (v1 sample, n=206): median 151 d, Q75 220, 11 % ≤ 72 d. Surrogate/neural-type 2024-06→ (this cycle, n=47): **median 172 d, Q75 222, 4.3 % ≤ 72 d** | Of 47 recent surrogate/neural articles, **44 have method-proposing titles** (new PINN variants, new surrogates, reduction schemes); no benchmark or negative-result study was identifiable by title (crude, title-only) | **NOT satisfied / unverified** |
| MLST (IOP) | IF 4.2 (journal page) | no dates in Crossref; page: median 5 d pre-review decision, 52 d post-review *first decision* | scope "ML across the sciences"; benchmark/negative-result policy not stated on page | **UNVERIFIED** (first-decision ≠ acceptance) |
| **MLCSE** (Springer) | **no JIF** (neither Q1 nor Q2 can be claimed) | census n=102: median 50 d, Q75 65, 83 % ≤ 72 d, max 205 | **Strong**: recent MLCSE papers include "The impact of data splitting methods on ML models", "Statistically grounded selection and validation of surrogate models", "Numerical study on hyperparameter settings for NN approximation to PDEs" | passes the *declared* census test of v1; **not** a guaranteed maximum |
| JKSU-CIS (Springer) | Q1 reported by aggregators; IF conflicting (6.1/6.4/8.84) | census n=1,280: median 74, Q75 99, 48 % ≤ 72 | CS-general, weak | **fails** |
| CMAME / EAAI (Elsevier) | ≈7.3–7.6 / ≈8–11 (aggregators) | not measurable | stretch / scope mismatch (see v1) | **UNVERIFIED** |

## "Five closest recent papers in the target journal" (Engineering with Computers; from `ewc_recent_articles.json`, titles/metadata only — full texts not read)
1. *Non-stationary multi-fidelity surrogate model based on spatial warping* (2025) — new surrogate method.
2. *Physics-aware neural network-based parametric model-order reduction of the electromagnetic analysis for a coated component* (2024) — new reduction method (closest topic).
3. *Voroto: multiscale topology optimization … using surrogate neural networks* (2024) — new method/application.
4. *A novel surrogate model for optimizing lattice for desired force-displacement response* (2026) — new surrogate.
5. *Learning 1D stress resultant plasticity from 2D continuum plasticity: a PINN model reduction approach* (2026) — new method.
**Reading:** the journal's recent surrogate papers each propose a method for a named engineering problem. A paper that proposes none and reports mixed/negative findings on synthetic problems is atypical for it. This is title-level evidence and may be wrong; the authors must read the papers.

## Interim decision
**NO VERIFIED JOURNAL MATCH UNDER CURRENT CONSTRAINTS** (Q1 + verifiable ≤ 72-day acceptance). The only journal with credible timeline evidence and a genuine scope fit for this paper type is MLCSE (no JIF). Engineering with Computers is *not* retained as the best-fit target for a benchmark-type paper unless the reinforced work yields a clearly method-like or confirmed-diagnostic contribution. Final ranking after results: see `submission_readiness_report.md`.
