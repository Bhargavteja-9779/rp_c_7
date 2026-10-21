# Review 07 — Efficiency and practical value

*Simulated adversarial pass by the Research Director (not an independent human or external reviewer). Each pass was written separately after the previous one's fixes.*

**Stance:** is the cost story supported?

| ID | Severity | Issue | Disposition |
|---|---|---|---|
| 7.1 | MODERATE | FOM solves take 3-136 ms; break-even analysis is a stylised model, not a measurement of any real expensive solver. | Stated as such in §5.3 and protocol. |
| 7.2 | MODERATE | GP cost is O(N^3); not studied beyond N=1024. | Added to limitation 10. |
| 7.3 | MINOR | Timings are single-thread CPU wall-clock under 4 parallel jobs; may have contention. | Reported as medians; no precision claims made.
