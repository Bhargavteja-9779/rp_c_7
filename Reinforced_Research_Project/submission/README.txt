SurroSelect submission package (DRAFT -- the authors must complete the items marked TODO)
Target journal chosen for scope fit: Advances in Engineering Software (Elsevier). No quartile, impact factor or review time was verified for it; no acceptance probability can be given.

Files
 1_Main_Manuscript.pdf               main manuscript (40 pages including references, Elsevier "preprint" layout, journal name set)
 2_Supplementary_Material.pdf        supplement (proofs, pre-specification record, earlier stages, deviation log V1-V18, leakage audit, per-problem table, tool details, Stage 7 problems)
 3_Cover_Letter.docx / .pdf          cover letter (date and authors still to be filled in)
 4_Main_Manuscript_Word_version.docx editable copy generated from the LaTeX source (check tables, equations, figure placement)
 5_LaTeX_Source.zip                  standalone source: unzip, run `bash build_latex.sh` (pdfLaTeX + BibTeX); tested to compile from the zip (40 + 13 pages, 0 errors)
 6_Highlights.txt                    five highlights (each at most 85 characters), to upload as a separate file
 7_Graphical_Abstract.png            graphical abstract (check the journal's size requirements)

What the authors must still do (the AI assistant cannot and must not do these)
 TODO  Names, affiliations, corresponding author, e-mail, ORCID, funding, competing-interest and ethics statements, CRediT roles, date (placeholders in main.tex, declarations, supplement, cover letter).
 TODO  Read the journal's CURRENT guide for authors (its page could not be fetched here): article type, length, highlights, graphical abstract, declarations, reference style, data/code and AI-use policies, preprint policy. Verify impact factor / quartile yourselves.
 TODO  Create the public repository / archive DOI (Zenodo or similar), fill the software-availability table and the availability statement; set the copyright holder of the MIT licence in surroselect/LICENSE and CITATION.cff; run the CI workflow once (it was never run on GitHub).
 TODO  Read every number, claim and citation yourselves; obtain at least one independent human review. All five reviews in the project were AI-agent reviews.
 TODO  All authors must approve the submission. The paper declares the use of an AI system (Claude) in the standard Elsevier wording; keep or adapt it to the publisher's policy after confirming it is true.
 TODO  Consider before submission (review/review_05.md): a prospective, blind use of the tool on a non-trivial simulation with the recommended follow-up runs actually spent; a real slow simulation; baselines such as stacking/AutoML and operator learning; a public benchmark.

Everything else (code, data scripts, results, protocol and deviation records, simulated reviews 01-05, claim-evidence matrix with 48 claims, final audit, journal-decision record) is in the project repository (Reinforced_Research_Project/); code/run_all.py reruns the experiments, analyses, figures and the paper build.
