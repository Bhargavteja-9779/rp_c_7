# Research project: linear-subspace vs neural surrogates for parametric PDEs (pre-registered, matched-tuning)

**Status: NOT READY FOR SUBMISSION** — see `review/final_audit.md`. Acceptance is not guaranteed and cannot be predicted.

| Folder | Contents |
|---|---|
| `manuscript/` | `Final_Manuscript.docx/.pdf/.md`, `cover_letter.docx/.md`, `build_manuscript.py` (numbers pulled from results) |
| `journal_selection/` | v1 (72-day constraint analysis, Gate A not met), v2 (user-directed high-IF target), data/tools for turnaround evidence, fit audit |
| `literature_review/` | candidate directions (`../research_design`), literature matrix, novelty map, verified references (with verification source) |
| `research_design/` | research questions, hypotheses, **pre-registered protocol v1.0**, leakage audit, deviations log |
| `code/` | `surrogate_bench` package, tests, `run_all.py`, configs, requirements |
| `results/` | raw per-job JSON, `raw_results.csv`, `statistics.json`, `metrics.json`, `tables/`, `exploratory/`, `interim_2seed_disclosed/` |
| `figures/` | Fig 1-6 (PNG/PDF) generated from results |
| `review/` | ten simulated adversarial reviews, automated claim checks, final audit and rejection-risk report |

Headline (pre-registered, 3 seeds): H1a, H1b, H2 not supported; H4a supported at cell level (Holm p=0.023) but fragile (5/16 instances). All data are synthetic.
