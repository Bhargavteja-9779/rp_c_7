# Review 03 — Experimental design and statistics

*Simulated adversarial pass by the Research Director (not an independent human or external reviewer). Each pass was written separately after the previous one's fixes.*

**Stance:** challenge independence, sample sizes, tests.

| ID | Severity | Issue | Evidence | Disposition |
|---|---|---|---|---|
| 3.1 | MAJOR | H4a (McNemar over 96 cells) ignores dependence of cells within an instance. | e4_robustness.json: only 5/16 instances flip; instance-level sign test p=0.031 uncorrected (~0.125 Holm). | **Fixed by disclosure + re-analysis:** manuscript now reports the clustered result, tempers the claim in abstract/discussion/conclusion. Verdict as pre-registered is retained and labelled fragile. |
| 3.2 | MAJOR | Only 8 independent families → low power for H2/H1b; 3 seeds (planned 5 not run). | §7 items 1, 6 | Disclosed. Not fixable without new compute and would be post-hoc. |
| 3.3 | MODERATE | Pre-registered baseline B1 is degenerate under LOFO (Darcy fold RMSE 11.4 from p=10 extrapolation), making H2's primary comparison nearly uninformative. | e2_lofo_rmse_by_heldout_family.csv | Reported as registered with explicit explanation; B0 comparison also reported (n.s.). |
| 3.4 | MODERATE | Exploratory analyses uncorrected for multiplicity. | §7 item 9 | Labelled exploratory everywhere. |
| 3.5 | MINOR | Seed subsets overlap by chance at large N so seed variance is underestimated. | data_leakage_audit.md | Disclosed (§7 item 6).
