# Competing-work analysis and novelty stress test (Phase 4)

**Search coverage (honest):** arXiv API (8 query families, ≤8 hits each), web search (US-only, 6 queries), Crossref verification, full/near-full text of one preprint (Westermann et al., ~200k/212k chars) and one metric paper (Zhang et al.). Not searched: Google Scholar, Scopus/WoS, patents, publisher full texts. **Absence of a prior pilot-data selection rule is therefore weak evidence.**

## What the closest work establishes
* **No universally best surrogate; regime depends on smoothness** — Westermann et al. 2026 (read ~95 %): polynomial surrogates more data-efficient for smooth inputs, FNO for rough; Pareto frontiers over hyper-parameter ensembles; *no* pilot rule, *no* tuning-budget ranking test, *no* GP/kernel POD baseline.
* **Kernel/GP methods are competitive with DeepONet/FNO, with error analysis** — Batlle et al. 2024 (abstract). This was missing from v1 and weakens any claim that "GP-type baselines are neglected".
* **Benchmarks on low-dimensional manifolds flatter neural surrogates** — Duraisamy 2026 (position, abstract).
* **Weak baselines / reporting bias** — McGreivy & Hakim 2024; Wyder et al. 2025 (CTF).
* **Cost accounting** — de Hoop 2022; Zhang 2026; Huang & Stuart 2026.
* **Slow n-width motivates nonlinear ROMs** — Franco et al. 2023; Feng et al. 2026 (hybrid).

## Stress test answers
| Question | Answer (evidence) |
|---|---|
| Is the main contribution already known? | The *qualitative* result — yes (above). The *quantitative, matched-protocol* result and the pilot-rule test are not found in the sources read. |
| New principle? | No. |
| Only a combination of established components? | The surrogates are established; the contribution is evaluation design + evidence. |
| Mainly an application of a standard model to new data? | No model is proposed; it is an empirical study. |
| Is the claimed gap supported by primary evidence? | Partly: the gap "no validated a-priori rule and no tuning-asymmetry quantification" is supported only by search-limited absence. |
| Would removing the novelty invalidate the argument? | If the diagnostic fails out of sample, the paper reduces to a benchmark + mechanism + tie-aware analysis, which is still a coherent paper but a smaller one. |

## Path decision
**Path A+B (strengthen, then reformulate as needed):** run the out-of-sample replication (Exp A), the mechanism test (Exp D) and the stronger-NN test (Exp B); then reformulate the contribution to what survives. Path C/D (redesign / change direction) is *not* chosen: the infrastructure and a sharp, testable question exist, and no evidence shows the project is unsalvageable. If Exp A fails **and** Exp D shows the GP advantage is only hyper-parameter-fitting, the final decision will be reconsidered (possible FUNDAMENTAL REDESIGN).
