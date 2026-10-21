# Review 05 — Dataset and external validity

*Simulated adversarial pass by the Research Director (not an independent human or external reviewer). Each pass was written separately after the previous one's fixes.*

**Stance:** challenge representativeness, leakage, generalisation claims.

| ID | Severity | Issue | Disposition |
|---|---|---|---|
| 5.1 | MAJOR | Everything is synthetic, low-dimensional (p<=10) and small (m<=256); levels 'L1/L2' were hand-chosen by us; conclusions can't be generalised to industrial problems. | Claims restricted to 'this suite'; §7 items 1, 2, 8. |
| 5.2 | MODERATE | Alternative explanation: GP's stationary ARD kernel (not manifold complexity) may explain GP losses on localised-feature instances. | Added to Discussion; experiments cannot separate it. |
| 5.3 | PASS | Leakage audit: separate seeded streams, train/test disjointness test, pilot features only from pilot data, preprocessing fit on training only, selection by validation only (unit-tested). | see data_leakage_audit.md |
| 5.4 | MINOR | Extrapolation set only 25% beyond the box; weak test of extrapolation. | Disclosed implicitly; E4 exploratory.
