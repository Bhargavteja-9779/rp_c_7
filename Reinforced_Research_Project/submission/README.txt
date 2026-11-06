SurroSelect submission package (DRAFT — the authors must complete the items marked TODO)

Files and where they go in a typical submission system
 1_Main_Manuscript.pdf               main manuscript (35 pages including references, journal-neutral Elsevier "preprint" layout; re-template for the chosen journal)
 2_Supplementary_Material.pdf        supplementary material (proofs, pre-specification record, earlier-stage results, deviation log, leakage audit, per-problem table, tool details)
 3_Cover_Letter.docx / .pdf          cover letter (journal name, date, authors still to be filled in)
 4_Main_Manuscript_Word_version.docx editable copy (generated from the LaTeX source; check tables, equations and figure placement before use)
 5_LaTeX_Source.zip                  standalone source: unzip, run `bash build_latex.sh` (pdfLaTeX + BibTeX); tested to compile from the zip (35 + 12 pages, 0 errors)

What the authors must still do (the AI assistant cannot and must not do these)
 TODO  Names, affiliations, corresponding author, e-mail, ORCID, funding, competing-interest and ethics statements, date (placeholders in main.tex, supplement.tex, cover letter, acknowledgments).
 TODO  Choose the journal; check scope, article type, page limit, template, reference style, data/code and AI-use policies; verify impact factor / quartile / review timeline yourself (none was verified in this project; no journal meets both "Q1" and "<= 72 days" on available evidence).
 TODO  Create the public repository / archive DOI (Zenodo or similar) and fill the availability statement; set the copyright holder of the MIT licence in surroselect/LICENSE.
 TODO  Read every number, claim and citation yourselves (all citations were checked against Crossref/arXiv/publisher records during the project, several only at abstract level); obtain at least one independent human review.
 TODO  All authors must approve the submission. The paper states that the work was done with an AI system (Claude) and that the internal reviews were AI-agent reviews; keep this disclosure as the publisher's policy requires.
 TODO  Decide whether to add a slow-simulation case study or a public benchmark (e.g. PDEBench) before submission; see review/final_audit.md for the remaining rejection risks.

Everything else (code, data scripts, results, protocol and deviation records, simulated reviews, claim-evidence matrix, final audit) is in the project repository (Reinforced_Research_Project/); `code/run_all.py` reruns the experiments, analyses, figures and the paper build.
