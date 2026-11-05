# Project package map (final state)
**Paper** (LaTeX, journal-neutral `elsarticle` template): `paper/main.tex` + `paper/sections/`, supplement `paper/supplement.tex`, cover letter `paper/cover_letter.tex`, Word version `paper/main_word.docx`; build: `bash paper/build.sh` (runs the aggregation, compiles, checks pages / overfull boxes / undefined references / typed-number lint). Every number in the paper is a macro or table written by `code/experiments/aggregate.py` from `results/`.
**Tool**: `surroselect/` (installable package, CLI `surroselect fit|predict|evaluate`, 10 tests, MIT licence, copyright holder to be set).
**Code**: `code/` (benchmark package `src/surrogate_bench`, experiments `experiments/`, figure scripts `visualization/`, tests `tests/`, one-command rerun `run_all.py`, pinned `requirements.txt`).
**Records**: `research_design/` (project details, consolidated protocol, addenda v2.0-v3.1, deviations V1-V13, leakage audit), `results/` (raw per-job JSON, derived JSON/CSV, logs), `review/` (simulated AI-agent reviews 01-03, triage, claim-evidence matrix, final audit), `audit/` (recompute scripts, pre-specification order check, journal decision), `data_real/` (two measured datasets, CC BY 4.0), `literature/`.
**Earlier drafts** (superseded): `manuscript/` (Markdown/pandoc versions v3-v4 and technical report).
**Submission package**: `submission/` (see its README.txt).
