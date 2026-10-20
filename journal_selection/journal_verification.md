# Journal verification log — what was actually done

| Check | Method | Result | Limitation |
|---|---|---|---|
| Observed received→accepted, Springer/Wiley/T&F/ACM/IET | Crossref REST `works` with `assertion` names `received`,`accepted`; random sample (`sample=100`, ×2–3) per ISSN, window 2025-01 → 2026-09 (`tools/crossref_turnaround.py`, `tools/scan_journals.py`) | 932 of 2,423 enumerated journals expose dates; 828 with ≥30 dated records (`data/scan_v1.csv`) | Random samples; run-to-run median variation of ±2–4 d observed (JKSU-CIS 73→76); numeric dd/mm/yyyy parsing ambiguous for a minority of journals |
| Finalist census | Cursor harvest of every record in window (`tools/full_harvest.py`), textual dates only | MLCSE n=102 / JKSU-CIS n=1,280 (`data/harvest_*.csv`) | Observed accepted papers only; "received" may be revised-manuscript date in rare cases |
| Elsevier titles in PubMed | NCBI E-utilities `efetch` History `received`/`accepted` (`tools/pubmed_turnaround.py`) | 9 titles, medians 91–287 d | Only PubMed-indexed titles; ≤300 records each; biomedical-AI subset, not general CS |
| Publisher "submission-to-acceptance" pages | WebFetch / curl on springer.com, sciencedirect.com, elsevier.com, scimagojr.com | **Blocked (JS challenge / HTTP 403)** | Tier-1 evidence unavailable |
| JCR quartile / JIF | JCR is subscription-only; no access. Web search only returned secondary aggregators with conflicting values | **UNVERIFIED for every journal** | Nothing may be reported as JCR-verified |
| MLCSE indexing | Web search → Springer collection page showing "Journal Impact Factor: Not available" | No JIF | Secondary snippet; confirm on Clarivate MJL |
| MDPI excluded | Publisher filter at enumeration (`mdpi` and non-whitelisted publishers dropped) | — | — |

Reproduce: `python3 tools/crossref_turnaround.py data/candidates_v1.json out.csv`; `python3 tools/full_harvest.py 3005-1436 2023-01-01 2026-12-31 out.csv`.
