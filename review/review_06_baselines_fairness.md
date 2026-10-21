# Review 06 — Baselines and fairness

*Simulated adversarial pass by the Research Director (not an independent human or external reviewer). Each pass was written separately after the previous one's fixes.*

**Stance:** are competing methods strong, tuned, correct?

| ID | Severity | Issue | Evidence | Disposition |
|---|---|---|---|---|
| 6.1 | MAJOR | Neural nets trained for fixed 1500 epochs float32; plateau ~1e-3; may be under-trained -> biases toward LS. | E1: 4x epochs lowers NN error in 29/36 fits (median x0.70), mean shift of y -0.25, 0/12 sign flips. | **Tested.** Conclusions robust in sign, magnitudes budget-sensitive; reported (Table 4, §5.3, §7). |
| 6.2 | MAJOR | Family selection asymmetry: LS picks the best of 3 methods, NL of 2. | E6: restricting LS to 2-method subsets leaves H1a/H1b verdicts unchanged; excluding POD+GP flips the picture. | **Tested.** Reported; led to the key insight that the LS advantage is a GP advantage. |
| 6.3 | MODERATE | Hyper-parameter spaces and defaults were written by us; no tuning of epochs/architecture beyond B=8. | | Disclosed (limitation 3). |
| 6.4 | MODERATE | POD+Poly weak (capped features, ridge only). | | Reported as weakest; does not drive verdicts (E6).
