# Deviations, disclosures and corrections in the v2 / v2.1 / v2.2 cycle

| # | Item | Type | Detail | Effect on pre-registered verdicts |
|---|---|---|---|---|
| V1 | Exp B shift sign convention | bug found by independent audit (F1), fixed **before Exp B was analysed** | `shift = y6000 − y1500` is negative when NL improves; B2 "shift toward NL < 0.5" would have passed trivially. Replaced by `shift_toward_NL = y1500 − y6000`; unit test added. | none (B not yet analysed) |
| V2 | A2 baseline p0 miscounted | factual error in addendum v2.1 found by independent audit, verified | p0 stated 2/20; correct 3/20 (burgers_L1 f1 = −1.9972, ȳ = 2.25). Amended in addendum v2.2 **before A2 ran**: p0 = 0.15, success k ≥ 4 of 7. | none (A2 not yet run) |
| V3 | Diagnostic verdict wording | re-characterisation | "Not replicated" → *pre-registered criteria not met; inconclusive; carried by one family (nlheat 88.3 % of P2 gain; ρ = +0.49 without it); confounded with p (Spearman 0.708)*. | none (numbers unchanged) |
| V4 | Stage chronology | disclosure | Stage 3 (addendum v2.1) was committed within minutes after the Exp A and Exp D results; Stage 4 (addendum v2.2) after two independent audits. All preregistrations are on a self-hosted git history; git tags could not be pushed to the remote. | none |
| V5 | Shared search draws | design property found by audit (F2/F3) | The random-search RNG depends only on (seed, method): the same 7 sampled configs are used for every instance and N within a seed (3 distinct sets per method in the whole study). v1 additionally used a process-salted hash (D5). | none on verdicts; changes how "tuning" must be described; sensitivity analysis planned |
| V6 | Neural batch/step count | design property found by audit (F02) | batch = N for N ≤ 512 (1500 steps) but 512 for N = 1024 (3000 steps): the neural step count doubles at N = 1024. Exp F removes this (full batch). | none on verdicts |
| V7 | Test/doc fixes | housekeeping | stale test count fixed (36 instances); weaker leakage tests replaced; BLAS thread env set at the top of entry scripts. | none |
