# Hypotheses (frozen with protocol v1.0 — see experimental_protocol.md for exact tests)

| ID | Type | Statement | Primary outcome | Test | Falsified if |
|---|---|---|---|---|---|
| H1a | confirmatory | At N=32, LS beats NL in the median instance | ȳ(i,32) = mean_seeds log10(err_NL*/err_LS*) | one-sided Wilcoxon signed-rank vs 0, n=16 instances | median ȳ ≤ 0 or Holm-adjusted p ≥ 0.05 |
| H1b | confirmatory | NL catches up with data: ȳ decreases with N in most instances | Spearman ρ_i(log2 N, ȳ(i,N)) per instance | one-sided exact binomial on #(ρ_i<0) vs p0=0.5 | Holm-adjusted p ≥ 0.05 |
| H2 | confirmatory | Pilot features {log10 CV-POD err (r=4), spectral slope} improve leave-one-family-out prediction of y over a baseline using {log2 N, p} | ΔRMSE = RMSE(B1) − RMSE(M_spec), cell level, N∈{64..1024} | family-cluster bootstrap (10,000), one-sided | CI lower bound ≤ 0 or Holm-adjusted p ≥ 0.05 |
| H3 | exploratory | Extrapolation inflation log10(err_ext/err_interp) differs between NL* and LS* | paired difference at N=256 | two-sided Wilcoxon, n=16 | (no direction; descriptive) |
| H4a | confirmatory | Asymmetric tuning (NL b=8, LS b=1) yields more cells where NL "wins" than symmetric tuning (b=8 both) | cell-level NL-win indicator | exact McNemar, one-sided | Holm-adjusted p ≥ 0.05 |
| H4b | descriptive | Fraction of cells whose family winner differs between b=1 and b=8 (symmetric); Kendall τ of method rankings | — | Wilson CI | — |

Multiplicity: Holm correction over the four confirmatory tests {H1a, H1b, H2, H4a}, family-wise α = 0.05.
All other analyses are exploratory/descriptive and labelled as such.
