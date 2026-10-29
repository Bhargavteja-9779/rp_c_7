# Reinforced research project — package map
Main paper (plain-language, application-style): `manuscript/Final_Manuscript_v4.{md,docx,pdf}` (built by `manuscript/build_v4.py` from `results/`).
Technical supplement S1: `manuscript/Supplement_S1_Technical_Report.*` (`build_v3.py`). Cover letter draft: `manuscript/cover_letter_v4.md`.
Readiness decision: `submission_readiness_report.md` (B: conditionally ready; blockers listed). Journal decision: `audit/final_journal_decision.md`.
`research_design/` protocols and addenda (v2.0–v2.3a), `code/` (package + tests; `python -m pytest code/tests`), `results/` (raw per-job JSON, tables, verdict notes), `audit/` (recompute scripts, risk register, claim–evidence matrix, pre-registration order check), `review/` (round 1–3 reports, triage notes, simulated reviewer response), `literature/`, `figures/`.
Reproduce: `cd code && OMP_NUM_THREADS=1 python run_v2.py --exp A` (etc.); rebuild paper: `python manuscript/build_v4.py`. The data cache is generated on demand (gitignored).
