SIMULATED REVIEW (AI agent, not an external reviewer)

# Review 02: presentation, structure and compliance

Role: hostile but fair journal editor/reviewer. Object: `paper/main.pdf` (26 pp, built from `main.tex`, `sections/*.tex`, `tables/macros.tex`), `paper/supplement.pdf` (15 pp), `cover_letter.tex`, `references.bib`, logs, `check_build.sh`.
Method: all 26 main pages rendered with `pdftoppm` (70 dpi overview; 100 dpi for pages 4, 5, 7, 13, 14, 16, 17, 18, 19, 21; supplement pages 5-8) into `/tmp/claude-0/-home-user-rp-c-7/d247ddca-2eb6-5163-bca0-57b556b9e2f0/scratchpad/r2h/` and `.../r2s/`. Full text read via `pdftotext`. Typed-number scan done with a script over `sections/*.tex` (output in `.../scratchpad/digits2.txt`). No file other than this report was modified. I did not re-run any experiment. Numbers were cross-checked only between abstract, text, tables and figures. Where a statement depends on data I did not see, I say so.

---

## 0. Verdict

**MAJOR REVISION on presentation and compliance** (the paper is not submittable as it stands, but nothing below needs new experiments).

The prose is plain, short-sentence and mostly free of filler. Every headline number I could check agrees across abstract, text and tables. The macro system works: zero macro names leak into the PDF text. But the build has real defects that the author's own `check_build.sh` does not detect:

- 11 cross-references in the main text and 2 in the supplement print the other file's name ("section S3supplement.pdf", "proposition 1main.pdf").
- Roughly 20 run-in headings end in a double full stop.
- A supplement table runs off the page and is cut off.
- Figure 5 is never cited.
- Figure 2 uses blue for opposite meanings in its two panels.
- Figure 4 has a wrong legend symbol.
- Figure and table fonts are well below the 6.5 pt floor in several places.

On content, one sentence contradicts the abstract (Sec. 6.1, "three of these eight" should read five). The abstract is over the word limit. Contribution 3 claims a dependence on "basis rank" that no result in the paper shows. The abstract promises that the study "explains where each model family wins", while Sec. 6.2 says the mechanism was not isolated. The word "pre-registered" is used for a self-hosted git history. Conclusion-section source is in the wrong file. The paper has no computational-complexity analysis. Several items are placeholders (authors, affiliations, funding, archive DOI).

---

## 1. Rendered pages: figures, tables, layout (task 1)

### 1.1 Figures

| Fig. (page) | Finding | Severity |
|---|---|---|
| Fig. 1 (p. 7) | Schematic is drawn at about half the text width inside a full-width frame. Box text and the example-field labels are about 4-5 pt after scaling. The three-line note under the example fields ("heatcomp_L1, N=256, seed 0 / selected: gp_full[rbf] / relative error ...") is about 3 pt and floats detached from the images. The box labels use code names ("pod_gp[...]" style) in places where the text uses "POD+GP". | MAJOR (font) |
| Fig. 2 (p. 13) | **Colour meaning flips between panels.** In (a) blue means "reduced basis clearly better" and orange means "network clearly better". In (b) the colour bar says red means "reduced basis better" and blue means "network better". A reader who carries colour from (a) to (b) reads the figure backwards. Row labels in (b) are set at 4.6 pt in `code/visualization/fig_main_result.py` (about 3.5-4 pt on the page) and are unreadable in print. (b) shows 36 problems, while (a) says "24 main problems" and the caption says "every problem". The caption never says (b) is the 36 own-solver problems and omits the 8 independent ones. The text cites "panel b, top rows" but rows are not labelled by a family or group. The caption cites "section S3supplement.pdf" (leak, see 2.1). | MAJOR |
| Fig. 3 (p. 14) | Readable. Five boxes carry five different colours (pink, pink, pink, blue, green) with no meaning given. The "GP, one length-scale" box is never explained in the main text (it appears only in the supplement as "iso-GP"). The caption says the comparison uses "28 combinations where that model clearly beats the best network", and the text (Sec. 6.2) says the best network is chosen by test error, which is not in the caption. The dashed "factor 3" label is tiny. No sample size per box. | MINOR |
| Fig. 4 (p. 17) | Legend in panel (b) reads "N_1 = 256"; it should be N_0 (panel a and caption use N_0). The shaded factor-two band in (b) is not labelled. Four orange bars at log10 ratio of about -1.1 to -1.5 are the real forecast failures, but the caption says only "below -0.3". The float sits two pages after first mention (p. 15 to p. 17). | MINOR |
| Fig. 5 (p. 18) | **Never cited in the text** (no `\cref{fig:strong}` anywhere; verified by grep). The x tick labels collide ("convdiffconvdiff", "heatcompheatcomp", "heatmoveheatmove"), as seen on the page. Dark blue ("always POD+GP") and light blue ("benchmark selection") are hard to tell apart in print and for colour-blind readers. The legend sits at the upper right of the N = 1024 panel, close to the heatcomp_L2 points. The bars are min-to-max over only three seeds, which is barely an uncertainty display. The caption does not state its answer ("The tool is the lowest or tied in X of 16 cells ...") and names neither model class nor metric beyond "test error". | MAJOR (uncited, collisions) |
| Fig. 6 (p. 19) | The row labels (5.5 pt in the script) and the model/error notes (5 pt) are about 4 pt after scaling to 0.9 text width; unreadable in print. Rows 2 and 5 are the **same sample** (heatcomp_L1, error 2.8e-03). The text then talks of "four rule-selected examples" plus "two failure cases", but the figure shows six rows of which two are identical. 1-D problems are drawn as blue line plots and 2-D as colour maps with different colour scales per row, so error magnitudes cannot be compared. The caption does not state an answer in its first sentence. | MAJOR |
| Fig. 7 (p. 21) | This is a verbatim Markdown report in a `verbatim` box and shows raw markup: `# SurroSelect report`, `**Selected:**`, pipe tables. It is called a "Figure" and is hard to read. The text says only "unedited except for line wrapping". The case study has no commentary on what the reader should see. | MINOR |

Vector status: `pdffonts` shows embedded vector fonts (Type 1 and DejaVu TrueType). Only the heat maps are raster (393x420 px at 191 ppi in Fig. 2; 124x124 at 237 ppi in Fig. 6), which is acceptable. The four fonts counted in `fig_main_result`/`fig_qualitative` are below 6.5 pt in the sources.

Colour-blind palette: Fig. 2(a), Fig. 3, Fig. 4 use an Okabe-Ito-like blue/orange palette (fine). Fig. 2(b) uses a red-blue diverging map and Fig. 6 uses viridis/magma. Fig. 5 mixes two near-identical blues. The same method gets different colours in different figures: "reduced basis" is blue in Fig. 2(a), red in Fig. 2(b), and the tool is green in Fig. 5, which is the only figure where the tool appears.

### 1.2 Tables

- **Table 1 (p. 5):** column headers collide ("Kernel/GP/polyTuning or base-"), as the log reports (Overfull 6.2 pt, `main.log` line 699). The body is mostly dashes: of 42 cells, 6 are check marks, and the first two rows ([1], [3]) are all dashes. The caption admits the dashes mean "did not find in the parts we read (mostly abstracts)", so the table compares the paper with works it did not fully read. Statement "we read only the abstract" in Sec. 2.1 confirms this. A hostile reader will say the comparison table proves nothing.
- **Table 2 (p. 10):** fine. It lists problem classes, not dataset sizes, and the two real datasets are not in it (only in prose, Sec. 6.6). It gives no train/test sizes (4096/1000/500 are in the Sec. 5.1 text only). The "Solver" column repeats "scikit-fem (third party)" four times.
- **Table 3 (p. 11):** the caption says "cells: 8 problems x N in {64,256,1024} = 24", but H4 is "4 of 16 cells". The 16 (8 problems x N in {256,1024}) is nowhere explained. Table 5 shows why (no N = 64 row), but the text never says the tuned network was not run at N = 64.
- **Table 4 (p. 15):** H5 is listed first, out of the H1a..H5 order of Table 3. H1c is the only row with two criteria and a mixed verdict. The 1% reach-target criterion (accuracy at least 75%) equals the majority-class rate (75%, stated in the text), so a classifier that always guesses the common answer passes. The pass criterion does not discriminate. Reported accuracy is 100%.
- **Table 5 (p. 16):** legible. Only N = 256 and 1024 are shown, while the headline "all 24 cells" includes N = 64. Column "Always GP" is "always POD+GP" in the caption and "Benchmark sel." is abbreviated.
- **Table 6 (p. 17):** rows "POD-based members only" and "no full-field GP" carry identical numbers (1.07 / 75% / 1.02x). If the pool has seven members and the only non-POD members are the full-field GPs, the two rows are the same pool and one row is redundant. If they differ, the table does not show how.
- **Table 7 (p. 20):** NRMSE is not defined in an equation anywhere ("the normalised RMSE replaces the relative error"). Normalised by what (range, standard deviation)? The first column and N repeat the dataset name each row.

### 1.3 Float placement and order

Order of first mention vs position: Fig. 1, Tables 1-3 and 7 are placed within one page of the first mention. Fig. 4 is two pages away; Fig. 5 is never mentioned. Numbering follows order of appearance. No overlaps beyond those listed. No cut-off text in the main PDF. **Supplement p. 7 is cut off** (see 2.2).

---

## 2. Build and compliance checks

### 2.1 Cross-document references print the file name (MAJOR)

Evidence: `pdftotext main.pdf | grep -c "supplement.pdf"` returns 11. Examples: "(section S7supplement.pdf)" (Sec. 1, contribution 1; Sec. 6.6), "section S4supplement.pdf" (contribution 4), "table S5supplement.pdf" (Sec. 6.1), "Supplement, section S2supplement.pdf" (Sec. 5.4, Sec. 6.2), "(section S3supplement.pdf)" (Sec. 5.4, Fig. 2 caption, Sec. 6.2, Sec. 7). In the supplement: "Proof of proposition 1main.pdf" and "proposition 2main.pdf" (S1). The cause is `xr-hyper` together with `\cref`. The `check_build.sh` macro-leakage test greps only for a backslash, so it reports 0 and passes. The author's instruction asks for "Sec. S2" and "Table S1"; the PDF currently shows lower-case "section" and "table" with a file name glued on.
Fix: use `\externaldocument[S-]{supplement}[supplement.pdf]` and a small macro that prints "Sec.~\ref{S-sec:...}" or "Table~\ref{S-tab:...}" with `\ref`, not `\cref`. Add `pdftotext | grep -c 'supplement.pdf\|main.pdf'` to `check_build.sh`.

### 2.2 Supplement table runs off the page (MAJOR)

`supplement.log` line 768: "Overfull \vbox (420.8pt too high)". Page 7 of `supplement.pdf` (deviation D5) shows a one-row table with a very narrow "Detail" column. The text runs down through the page number and is cut off at the bottom ("code/ ..." is lost). Pages 5 and 6 each carry a single row (D2; D3 and D4) and are mostly white. The deviations table (`tables/deviations.tex`) uses fixed-width `p{}` columns inside a non-breaking tabular. Use `longtable` or `tabularx` with a wide Detail column, and allow row breaks. This is the page that documents the deviations, which is a main selling point of the paper.

### 2.3 Other log items

- Main: 3 "Overfull" lines (Table 1 header 6.2 pt; the Sec. 6 intro line with `code/experiments/aggregate.py` 14.9 pt; an output-routine overfull of 2.4 pt). Supplement: 9 (up to 34.6 pt for `environment.json`, 18 pt in a code listing). Target is zero. Fix: break paths with `\path{}`/`\url{}` or `\allowbreak`.
- Several "Underfull \hbox (badness 10000)" lines in Table 1 (narrow `p{}` columns).
- `main.log`: "Unused global option(s): [authoryear]". The `authoryear=false` option is ignored; remove it.
- `main.blg`: 5 warnings, all "empty pages" for [22], [23], [25], [28], [30] (Hyperband, Optuna, Bouthillier, Rosenfeld, UQLab).
- Undefined references/citations: 0 in both documents. Confirmed by grep: all `\cite` keys exist in `references.bib`.
- Page count: 26 main + 15 supplement, in single-column `elsarticle preprint` 11 pt format. The journal limit is unknown (the repo says the journal is "to be chosen"), so this cannot be assessed. A final-layout version will be shorter, but 26 preprint pages plus 15 of supplement is long for a paper whose headline is a tool.
- Macro leakage: 0 (confirmed). Hand-typed `-0.03`: the minus is a hyphen in the rendered text ("is -0.03 instead of 0.16", p. 14). Use `$-0.03$` in the macro.

### 2.4 Typography

- **Double full stop** after every run-in heading: "Gap..", "Problem..", "POD basis..", "Regressors..", "Assumptions..", "Data protocol..", "Main problems..", "Selection quality (H1a, H1b, H1c)..", "Limitations..", "Ethics and disclosure.." and about ten more (the `elsarticle` `\paragraph` already adds the period and the source adds another; see `grep` of "\.\. " in the text). About 20 occurrences.
- Cross-reference style is mixed: "section 6.5", "table 4", "fig. 4", "proposition 2", "algorithm 1" in running text (cleveref lower case) but "Figure 6", "Table 1" at sentence start. Choose one ("Sec. 6.5", "Fig. 4", "Table 4").
- Reference [11] prints "A. Bērzin, š, J. Helmig" with a stray comma, while Table 1 prints "Bērziņš" correctly. The bib key uses `B{\={e}}rzi{\c{n}}{\v{s}}`, which BibTeX splits badly. Use UTF-8 "Bērziņš" in braces.

---

## 3. Typed numbers (task 2)

The macro system covers most results. "Justified" means a fixed protocol parameter, a threshold set before the runs, a verified external fact, or a label. "Macro" means the number is data-derived or repeated and should come from `macros.tex`. I cannot verify that the table files `tab_*.tex` are regenerated by `aggregate.py` in every case: `aggregate.py` line 22 and line 119 write `tab_{name}.tex` and `tab_perproblem.tex`, so I assume yes. They carry no "generated" header, unlike `macros.tex`.

### 3.1 Should be macros (data-derived or already available as a macro)

| File:line | Text | Why |
|---|---|---|
| `sections/s6a_study.tex:9` | "does not carry over to **three** of these eight independent problems" | **Wrong number.** Three is the count where the reduced basis did win (`\TpLsClear`). It failed on five. Sec. 7 and Sec. 8 say five. Use `\TpN - \TpLsClear` as a macro `\TpNotClear`. |
| `s6a_study.tex:15` | "moved the verdict in **15** of `\ExpBTotal`" | `\ExpBChanged` (15) exists in `macros.tex` and is unused. |
| `s6a_study.tex:12, 14` | "the **28** budget-problem combinations" | `\FullCellsN` (28) exists, unused. |
| `s6a_study.tex:8` | "all **36** own-solver problems" | `\NOwnProblems`. |
| `s5_setup.tex:3` | "for **24** problems" (budgets 32 to 1024) | `\NMainProblems`. |
| `s6b_tool.tex:2, 6, 8` | "(**24** cells)", "the **48** cases", "of **24**" | `\SoneN`, `\BoneN`, `\BtwoOneN`. |
| `s6c_discussion.tex:7, 8` | "the **36** earlier problems", "treat **24** cells" | `\NOwnProblems`, `\SoneN`. |
| `s6c_discussion.tex:3`; `s6c_discussion.tex:18` | "**five** of the eight", "fails on **five** of eight" | derived (8 minus 3); the Sec. 6.1 error above shows why. |
| `s3_prelim.tex:19`, `s6c_discussion.tex:12` | "only **five** of our **44** problems have ten or more [inputs]" | data-derived count (from Table 2 range 3-32) typed twice. |
| `s1_intro.tex:12`, `s3_prelim.tex:19`, `s6c_discussion.tex:12,18`, `main.tex:15` (title) | "44-problem" / "44 problems" | `\NAllProblems` exists. Title is typed in `main.tex` and in `cover_letter.tex`. |
| `s6a_study.tex:5` | "the largest margin is a factor of **about three**" (networks) | data-derived and not in any table or figure. |
| `s6b_tool.tex:27` | "**1,503** rows, **five** inputs", "**9,568** rows, **four** inputs", "**1,052** rows" | dataset facts typed in prose; should come from the data loader. |
| `s5_setup.tex:24` (caption), `abstract.tex:1` | "8 problems", "16 cells" | duplicates of `\TpN`, `\SfourN` (abstract uses the macros, the table 3 caption does not). |

### 3.2 Justified as protocol constants, but duplicated (risk of drift)

- Tool defaults: rank 32 / 8, 3000 features, 300 runs, grid 0.05-15 sqrt(p), ridge 1e-16..1e-2, degree six, k = 4, tie band 0.1 decade, 25% basis margin, 1/8..1 learning-curve fractions, b < 0.1, 16N cap (`s4_method.tex:8, 11, 14, 17, 20, 23-25`). They are repeated in Secs. 4.2, 4.4, 4.5, Algorithm 1 and the supplement (`s_tool_supp.tex`). Suggest one generated block from the tool's default config.
- Experiment protocol: 4096 / 1000 / 500 inputs, seeds {0,1,2}, budgets (`s5_setup.tex:3`); 1500 epochs, 16 trials, depth 2-4, width 64-256, 200 L-BFGS (`s5_setup.tex:15, 18`; repeated in `s6c_discussion.tex:10`); 6000 steps (`s6a_study.tex:15`); 2000 resamples and 95% (`s5_setup.tex:34`); tie-band sensitivity 0.15 / 0.05 (`s6a_study.tex:5`); targets 10%, 1%, 0.1% (`s6a_study.tex:8`, `s6b_tool.tex:6`).
- Thresholds in Table 3 (1.5, 2, 75%, 70%, 25%, 4 of 16, 5 of 8): fixed by the plan. They also appear in Table 4 and in text; macros would keep them in step.
- `s2_related.tex:12`: "79% of 76 reviewed articles" is a figure quoted from McGreivy and Hakim [6]. Justified as a cited fact; I could not verify it against the source from the repo.
- `s3_prelim.tex:13`: "10^{+-0.1} approx 1.26" derived constant; fine.

### 3.3 Abstract numbers against macros and tables

All abstract numbers come from macros, and they match the text, Table 4 and Table 5 where I could check them:

- 8 problems = `\NTpProblems` (8); 44 = `\NAllProblems`.
- Factor 1.18 and 24 cells = `\SoneMax`, `\SoneN`; median 1.00 matches Table 4 (1.00 [1.00, 1.02]).
- 77% of 48 and 62% from 256 runs = `\BoneShare`, `\BoneN`, `\BoneShareTwofiftysix`. 37/48 = 77.1%; 15/24 = 62.5%, which the macro rounds down to 62% (round-half-even; many readers will expect 63%).
- 4 of 16 = `\SfourBetter`, `\SfourN`; I recomputed from Table 5 and found the same four cells (heatcomp_L2 at both N, lshape_L2 at both N).
- 3 of the 8 = `\TpLsClear`, `\TpN`.
- Also cross-checked: "tool better in 11 cells, network in 4, one tie" from Table 5; "median regret 1.04 over six cells" and "5 of 6 cells" from Table 7.

Problems with the abstract itself:

1. **Length: about 253 words** (my count of the PDF text between "Abstract" and "Keywords"; the raw `.tex` also gives 253 tokens). Limit is 250.
2. It contains about 15 numbers, not "the three most important". Pick three (for example regret 1.00 / 1.18, forecast 77% and 62%, 3 of 8 for the benchmark finding).
3. "a 44-problem study **explains** where each model family wins" overclaims. Sec. 6.2 says "we did not isolate the contribution of marginal-likelihood fitting".
4. "pre-registered limit" (see M5).
5. POD and GP are used without expansion ("POD basis"); "the benchmark" is not defined here (see 5).
6. Counts below ten are digits ("8 problems", "3 of the 8", "4 of 16" is fine as 16 > 9 but "4" is not).

### 3.4 Numbers agree? (task 6, cross-check list)

Agree: Fig. 1 error 2.8e-03 = Fig. 6 row 2; Fig. 6 heatmove_L1 8.0e-04 vs Table 5 9.0e-04 (single sample vs geometric mean; fine); Fig. 2(a) counts at N = 32 (5/14/5) and N = 1024 (13/3/8) = text; Fig. 3 medians 13 / 6.5 / 2.7 = text; Table 6 median 2.74 = text 2.7; timings 112/312 s and 146/429 s consistent between Sec. 6.3 and 6.4; Table 5 reproduces H4's 4 of 16 and 11/4; Table 7 regret column equals Tool/Oracle; airfoil pool 1052 = 0.7 x 1503; Table 4 vs Sec. 6.3 text (all H rows); Table 2 problem counts 2+2+2+2 = 8 and 9+9+4+4+2+8 = 36; cover letter "five of seven met, two not" equals H1a, H1b, H2, H3, H4 met and H1c, H5 not.

Disagree or unclear:

- `s6a_study.tex:9` "three of these eight" (should be five; see 3.1).
- Fig. 2(b) shows 36 problems; the 44-problem headline and text say "every problem".
- Fig. 4(b) legend N_1.
- Table 3 caption says 24 cells; H4 uses 16 (unexplained).
- Sec. 6.1 "the eight smooth problems we added later" and "the eight problems solved by scikit-fem" and (supplement S3) "eight new problems from four new families" (pilot test) are three different sets of eight. Easy to confuse. Name them.
- Sec. 5.2 says the best member of each group is chosen "on validation data"; Sec. 6.2 says the comparison uses the best network "by test error, an oracle that favours the networks". Both are in the paper, but Fig. 3's caption does not say it.
- The 16 vs 24 cell count in H4 vs H1/H2.
- Fig. 7 reports "Runs needed for error 0.001: about 235" for a case that already has 256 runs, while the cross-validated error at n = 192 is 1.42e-03. Plausible (the cross-validated error is estimated on 3/4 of the runs), but a reader will stop on it; add one sentence.

---

## 4. Structure against the required outline (task 3)

| Required piece | Status |
|---|---|
| Title | Present. Typed "44" (see 3.1). Colon title is fine. |
| Abstract (at most 250 words; problem, proposal, test, three numbers, one limitation) | Over limit (253); too many numbers; limitation present (good). |
| Introduction: application, gap, "Motivation and Contributions", Organization | Application is generic ("shape of a part"; one hour per run illustration) with **no reference** in the first paragraph for any claim ("thousands of runs", "a common remedy"). "Gap" present. Four contributions, each with a section pointer (good). Contribution 4 ("An honest record of what did not work") is a self-description, not a contribution. Organisation present. |
| Literature review by theme ending with "Motivations" (i)-(v) + comparison table | Present (Secs. 2.1-2.7, Table 1). Table 1 is weak (see 1.2). "We read only the abstract" and "mostly abstracts" are admissions a referee will quote. Motivations (i)-(v) present and each tied to the method. |
| Preliminary concepts: notation, equations, assumptions | Present (Eq. 1-2, A1-A4). No notation table. Terms "regret", "cell", "oracle", "decade" are defined later or not at all. |
| Proposed methodology: overview, schematic, algorithm box, one subsection per component, theory with proofs in supplement | Present: Fig. 1, Algorithm 1, Secs. 4.2-4.5, Propositions 1-2 with "standard" stated. Good. Algorithm and Sec. 4.5 duplicate the forecast description. |
| Experimental framework: setup, dataset table, metrics as equations, baselines, hypotheses and how tested | Setup, Table 2, baselines, Table 3 and Sec. 5.4 present. **Metrics as equations:** only Eq. (1) error and Eq. (3) group effect. Regret, forecast ratio (Sec. 5.2, prose) and NRMSE (never defined) are not equations. Dataset table omits sample sizes and the two real datasets. |
| Results: statistics per hypothesis | Present (Table 4 plus Secs. 6.1, 6.3). The 1% reach-target test equals the base rate (see 1.2). |
| Qualitative analysis | Present (Sec. 6.5), thin: no commentary tied to a specific number. |
| Ablation | Present (Table 6; duplicate row). |
| Computational complexity | **Missing as complexity.** Only wall-clock times on one machine (Sec. 6.4). No big-O in N, m, p for GP, KRR, polynomial and the learning curve, no memory figures, no scaling plot. |
| Comparative analysis | Present but short (Sec. 6.6) and internal only. It compares against the paper's own baselines, not against published methods or existing tools (the paper says it did not compare with pyMOR or UQLab). |
| Real-world validation | Present (two public scalar datasets, Table 7). They violate A2 (stated), so this is not field-data validation. |
| Case study | Present (Fig. 7), a single report, no discussion. |
| Discussion with numbered limitations | Present: "supports / does not support", eight numbered limitations. Good. One sentence is garbled: "Against a network tuned with twice the budget..., the tool was met on the criterion of H4" (`s6c_discussion.tex:2`). |
| Conclusion and Future Scope | Present with five next steps. **Source problem:** `sections/s7_conclusion.tex` is a 0-byte file, and `main.tex` still inputs it. The conclusion text lives at the end of `s6c_discussion.tex`; `s6_results.tex` is a three-line wrapper. A co-author editing "the conclusion" will edit an empty file. |
| Acknowledgments with AI-use disclosure | Present and clear. Contains a placeholder ("to be confirmed by the authors"). |
| Data and code availability | Present; archive DOI and copyright holder are placeholders. |

Further structure points:

- Section numbering: the Discussion is Sec. 7 and the Conclusion Sec. 8, outside "Results and Analysis" (Sec. 6). That is acceptable, but the instructions place "Discussion" as the last part of Results. State once that this is intentional.
- Sec. 6 opens with "All numbers in this section are written by `code/experiments/aggregate.py`". That is a provenance note, not a result; move it to Sec. 5 or the availability statement.
- Contribution 3 says the outcome "is shown to depend on training budget, tuning effort **and basis rank**". No experiment in the main text varies the basis rank (the pool only contains rank 8 and rank 32 members), and the supplement mentions rank only in the default-pool description. Remove "basis rank" or add the evidence.

### 4.1 "Counts below ten as words" (rule violations)

The rule is broken systematically, because the macros print digits. Examples (all in the PDF text):

- Abstract: "8 problems", "3 of the 8".
- Sec. 5.1: "grouped into 6 classes", "8 problems were added", "4 CPU cores", "Table 4 ... 3 of 8".
- Sec. 6.1: "clearly better in 5 problems", "the networks in 5", "counts are 13, 8 and 3", "(9 against 4 ...)".
- Sec. 6.3: "7 forecasts were too low ... 4 too high", "worse in 1", "worse in 9", "in 0 cells", "5 of 6 cells", "9 of 12".
- Sec. 6.3: "the 48 cases" is fine (above nine). Sec. 6.4 "4 cores". Supplement: "9 unit tests".
- The same paragraph mixes "eight scikit-fem problems" (typed words) with "8 problems" (macro) (Sec. 5.1, Sec. 6.1).

Fix: let `aggregate.py` emit a word form for integers below ten when used in prose (for example `\Wd{\TpN}` or a second macro set), keep digits inside tables and equations.

### 4.2 Consistency and terminology

- The same object has several names: "stand-in model" (title, abstract, intro), "surrogate" (keywords, Sec. 2, Table 1 context), "reduced-basis group", "reduced-basis Gaussian process", "POD-based member", "reduced model", "POD+GP" (all used for roughly the same family); "network", "direct network", "MLP", "neural network", "TunedMLP". Choose one name per object and define it once.
- "The benchmark" is used from the abstract onward ("the benchmark's own selection", "the benchmark finding", "five benchmark methods") but is never defined. A reader needs "the benchmark" = the 36-then-44-problem study and its five methods under equal tuning. In Sec. 2, "PDEBench" is also called a benchmark. Rename the first to "the baseline study" or "the five-method comparison".
- "cell" (problem x budget x seed-average), "case" (forecast case) and "combination" are used interchangeably with "problem" in places. "Class" (Table 2) vs "family" (Sec. 6.5, Sec. 7 limitation 1).
- "Decade" for a log10 unit and "regret" for a ratio are used without definition in the text before first use (the tie band says "0.1 decade"; abstract says "regret" nowhere, but Sec. 6.3 does). Define "decade" in Sec. 3.
- "Pre-registered" (abstract, contribution 2, Table 3, Table 4, Sec. 6.3, Sec. 7, cover letter): the study uses a self-hosted git history, and Limitation 8 and supplement S2 say "not an independent registry". Journals read "pre-registered" as a registry time stamp. Use "pre-specified (committed to the project repository)" in the abstract, tables and cover letter.
- British spelling throughout ("organisation", "regularisation", "colour", "optimiser"), but "hyper-parameter" (text) vs "hyperparameter" (reference titles) and "full-field" vs "full field". Fine if intended; keep one hyphenation.
- Abbreviations: POD is expanded in Sec. 1 but not in the abstract; GP in the abstract appears only as "Gaussian process" (fine) but "GP", "KRR", "ARD", "MLP", "TPE", "NRMSE" are introduced in different places. KRR is defined in Sec. 3 and used in the figures as "kernel ridge".

### 4.3 AI-sounding filler, repetition, hedging, jargon

The text is mostly clean. A search for delve, crucial, leverage, comprehensive, novel, paves, robust, notably, moreover, furthermore, holistic found none in the sections. Remaining issues:

- Hedging pile-ups: "can answer only roughly and must be validated, not assumed" (Sec. 2.7(v)); "is therefore largely an advantage of a smooth regressor whose regularisation is searched widely and finely, and not of the reduced basis; we did not isolate..." (Sec. 6.2) carries three qualifiers in one sentence; "Cell-wise values ... so seed variability understates ..." and the limitation list repeats the "seeds share the pool" caveat in Sec. 6.4 and Limitation 3.
- Self-description and appeal words: "An honest record of what did not work" (contribution 4); "far from chance" (Sec. 6.3); "hard to beat" (Sec. 6.6); "the tool of Section 4 is designed for exactly this case" (Sec. 6.1).
- Repeated phrasing: "twice the budget of any other method" appears five times (abstract, contribution 2, Sec. 5.3, Sec. 6.3, Sec. 7). "The pre-registered criterion was met with a confidence interval that includes the threshold" appears in Sec. 6.3 and Limitation 4. The sentence "the independent reviews were performed by AI agents" appears in Sec. 6.2, Limitation 8, the acknowledgments and the cover letter.
- Meta statements: "The wide-range control was added after an AI-agent review of an earlier draft showed ..." (Sec. 6.2). Honest, but it belongs in a methods or process note, not in the middle of the mechanism argument.

### 4.4 Eight concrete rewrites

1. **Sec. 6.1, `s6a_study.tex:9` (error).** Old: "The simple picture 'reduced basis wins at large budgets' therefore does not carry over to three of these eight independent problems". New: "The rule 'the reduced basis wins at large budgets' therefore fails on five of the eight independent problems."
2. **Abstract (length and numbers).** New draft, about 195 words with three headline numbers: "Engineers who rely on a slow simulation can afford only a few hundred runs. They must choose a fast stand-in model and decide whether more runs are worth the cost. We present SurroSelect, an open tool that picks a stand-in from a pool of classical models by cross-validation, reports which models are tied, checks whether the proper orthogonal decomposition (POD) basis limits accuracy, and forecasts the error for more runs. We tested it against criteria committed before the evaluation runs, on eight problems solved by the independent finite-element library scikit-fem, against a neural network tuned with twice the budget of any other method, and on two real datasets. A 44-problem study sets the context. The selected model was within a factor of 1.18 of the best pool member in all 24 cells (median 1.00). The error forecast for four times the budget was within a factor of two in 77% of 48 cases, but in only 62% when it started from 256 runs. The reduced-basis Gaussian process, which won the earlier study at large budgets, won on only three of the eight independent problems. All problems are simulated and fast, so the tool pays off only for much slower simulations, and the forecast is a rough extrapolation." (Replace "explains where each family wins" with a plain description; drop "exactly at the limit" or move it to the text.)
3. **Contribution 4.** Old: "An honest record of what did not work (Section 7) ...". New: "A full record of negative results and plan changes: a pilot diagnostic that was not confirmed, a control that had to be widened after review, and every deviation from the plan (Sec. S4)."
4. **Contribution 3, unsupported claim.** Old: "...the outcome of a comparison is shown to depend on training budget, tuning effort and basis rank." New: "...the outcome of a comparison depends on training budget and tuning effort." (Add the rank clause only if a result shows it.)
5. **Sec. 7 "What the evidence supports" (garbled).** Old: "Against a network tuned with twice the budget of any other method, the tool was met on the criterion of H4." New: "Against a network tuned with twice the budget of any other method, the tool met criterion H4: the network was better by more than 25% in four of 16 cells, exactly the allowed maximum."
6. **Sec. 6.2 (hedge pile-up).** Old: "The Gaussian-process advantage is therefore largely an advantage of a smooth regressor whose regularisation is searched widely and finely, and not of the reduced basis; we did not isolate the contribution of marginal-likelihood fitting, because its cost is not matched by the kernel-ridge search." New: "A wide, finely searched kernel ridge closes most of the gap to the Gaussian-process reduced model, and a Gaussian process on the full field is as accurate. So the advantage does not come from the reduced basis. A gap of about 2.7 times remains at 32 trials. We did not test whether marginal-likelihood fitting explains it."
7. **Sec. 6.2 process aside.** Old: "The wide-range control was added after an AI-agent review of an earlier draft showed that our first control could not reach the regularisation that near-interpolating fits need; this is a post hoc control (Supplement, ...)." New: "This control is post hoc (Sec. S2). We added it because the first kernel-ridge grid could not reach the small ridge values that near-interpolating fits need."
8. **Sec. 6.4 cost sentence.** Old: "...so for these problems the tool costs more than running the simulation 1024 times; its use is justified when one run takes minutes or hours." New: "At N = 1024 the tool needs 426 s. That equals 1024 runs of 0.42 s each. The tool therefore saves time only if one run takes much longer than 0.4 s. We did not test this case." (Use macros for 426 and the derived 0.42.)

Also for the Table 4 H2 row, add the base rate in the table ("accuracy at least 75%; majority-class rate 75%") so the reader sees the criterion does not discriminate.

---

## 5. References (task 4)

- Every `\cite` resolves; 35 of 39 entries are cited in the main text. **Four entries are unused**: `pedregosa2011` (scikit-learn), `paszke2019` (PyTorch), `virtanen2020` (SciPy), `quarteroni2016` (reduced-basis textbook). The first three should be cited where Sec. 5.1 lists the software versions (Python, NumPy, SciPy, scikit-learn, PyTorch, Optuna); NumPy has no entry at all. `quarteroni2016` is the obvious textbook reference for the POD discussion in Secs. 2.1 and 3. As they stand, they look like padding. Not cited in the supplement either (grep).
- Formatting: [32] prints "neurIPS 2022 Datasets and Benchmarks Track" (the BibTeX style lower-cased "NeurIPS"; protect with braces). [10], [11], [18], [20] print "arXiv:... (preprint) (2026)" with the year twice. [8], [25], [28] mix a conference venue with an arXiv number in `note`. [11] has a stray comma in the author name (2.4).
- Missing DOIs and pages: [8], [13], [21], [22], [35] have no DOI; [22], [23], [25], [28], [30] trigger "empty pages" warnings; [13] is an article with number but no DOI. DOI coverage is inconsistent (some entries have it, similar entries do not).
- Capitalisation of titles follows the style (sentence case), except in places where the bib contains braces for acronyms. "pyMOR - generic ..." renders fine; [30] "UQLab ... in Matlab" fine.
- Recent preprints: [10] arXiv:2604.00689, [18] arXiv:2604.20061, [20] arXiv:2510.23166 are dated 2025-2026. I cannot verify them from the repo; they are central (Westermann et al. is the "no universal winner" claim and a row in Table 1). Flag for the authors to re-check authors, titles and versions.
- Sec. 2: "we read only the abstract" of [11], "mostly abstracts" for Table 1, and "we did not compare their features" for [29], [30] are honest but weaken the review. The literature sections cite 29 works for related work, but about half are cited in one sentence each.
- Key claims in the introduction (first paragraph) have no citation: thousands of runs for optimisation, uncertainty quantification and calibration; surrogates as a "common remedy". Add one or two references each (for example [29], [30] and a survey).

---

## 6. Journal fit: what a methodology or software venue would ask for (task 5)

Evidence is from the repo only. I make no claims about any journal's scope or rules.

1. **No slow simulation.** All 44 problems are simulated, with solves of about 3-27 ms for the independent set and a median of 6.0 ms for the own set. The paper itself says the tool "costs more than the simulations it replaces" (Limitation 6) and "which we did not test". The motivating use case is therefore untested. A methods venue will ask for at least one expensive solver case, even a single published case with its run budget.
2. **Little independent data.** One finite-element library, four problem families, two levels each. Two real datasets are scalar and noisy, which violates assumption A2. There is no real field data and no public benchmark (PDEBench is named only as future work).
3. **No comparison with existing tools or generic baselines.** pyMOR and UQLab are cited and "not compared". There is no comparison against a generic model-selection procedure (plain cross-validated scikit-learn regressors, an AutoML search), which is the natural null for "choose a regressor by cross-validation". The strongest "baseline" is the paper's own benchmark under eight trials.
4. **Statistics rest on very few independent units.** Eight problems; 24 cells that share the pool, test set and nested training subsets. Limitation 3 admits the intervals are optimistic, but the tables still report 95% intervals and Holm-adjusted p-values without a problem-level analysis (for example intervals over the eight problems, or a mixed model).
5. **Forecast component is weak.** 62% within a factor two from 256 runs, a range that covers the truth in 12% of cases, no calibrated interval. It is one of four advertised features.
6. **Selection quality has no hard null for the tool's key claim.** H1c (against the benchmark's own selection) is not met. The default pool has no neural network, yet the main competitor is a neural network. The paper concedes this in Limitation 5 and Sec. 8.
7. **Software-paper elements missing from the main text.** Installation, dependencies, API, test count and licence are in the supplement (`s_tool_supp.tex`; nine unit tests; MIT licence). Missing: archive DOI (placeholder), version number and release tag, continuous-integration evidence, documentation location, test coverage, scaling limits (the paper only tests N up to 1024, m up to 2000 for full-field GP, p up to 32), memory use, and a statement of what happens outside assumptions A1-A4 (the tool "does not detect" non-exchangeable designs).
8. **Reproducibility claims need an archive.** "code/run_all.py reruns everything" is stated; no DOI, no container, no runtime or hardware budget for a full rerun. The supplement lists a bug found in the fresh-clone audit (hash-salted random search, deviation D5), so exact rerun is not bit-identical.
9. **Process.** The pre-registration is self-hosted; the supplement counts several stages as post hoc; reviews and drafting were done by AI agents (disclosed). A venue with a reproducibility or integrity checklist will want a named human who checked every claim; the acknowledgments still say "to be confirmed by the authors".
10. **Placeholders that block submission:** authors, affiliations, corresponding e-mail, journal name, funding, competing interests, archive DOI, copyright holder, cover-letter paragraph "Why this journal". The supplement header says "Preprint submitted to Elsevier" while the main paper says "journal to be chosen"; make them agree.
11. **Length.** 26 + 15 pages in preprint layout. Page limit unknown; likely to need cutting of Secs. 6.1-6.2 (the benchmark study) into the supplement if the venue wants a tool paper, or cutting the tool material if it wants a benchmark paper. The paper currently serves both audiences.

---

## 7. Objections (severity, location, evidence, fix)

### CRITICAL

None that invalidates a computed result. The items below are the ones I would not allow into a submission.

### MAJOR

**M1. Cross-document references print the other file's name.**
Location: 11 places in `main.pdf`, 2 in `supplement.pdf` (list in 2.1). Evidence: "section S7supplement.pdf", "proposition 1main.pdf". `check_build.sh` reports 0 leaks because it greps only for a backslash. Fix: see 2.1; add a check for `supplement.pdf|main.pdf` in the PDF text.

**M2. Sec. 6.1 contradicts the abstract.**
Location: `s6a_study.tex:9`. Evidence: "does not carry over to three of these eight"; abstract, Table 4, Sec. 7 and Sec. 8 give three where it held and five where it failed. Fix: rewrite 1 and derive the number from a macro.

**M3. Abstract over the word limit and not following the brief.**
Location: `abstract.tex`. Evidence: about 253 words; about 15 numbers; "explains where each model family wins" against Sec. 6.2. Fix: rewrite 2.

**M4. Unsupported claim in contribution 3.**
Location: `s1_intro.tex:12`. Evidence: "basis rank" dependence; no main-text result varies the rank. Fix: remove or add the evidence (rewrite 4).

**M5. "Pre-registered" used for a self-hosted git history.**
Location: abstract, `s1_intro.tex:11`, Tables 3-4 captions and text, Sec. 6.3, cover letter. Evidence: Limitation 8 and supplement S2 say "not an independent registry"; supplement S2 also says it shows "protocol-before-results in history, not protocol-before-first-run", and a smoke test preceded registration (contribution 2). Fix: "pre-specified (committed to the project repository)" in the abstract, tables and cover letter; keep the explanation in Sec. 5.4.

**M6. Figure 5 is never cited; its tick labels collide; its colours are close.**
Location: p. 18; `s6b_tool.tex:10-12`. Fix: cite it in the H4 paragraph ("Fig. 5 shows..."), rotate or abbreviate x labels, use two clearly different colours, and state the answer in the caption's first sentence.

**M7. Figure 2 reverses colour meaning between panels and has unreadable row labels.**
Location: p. 13; `code/visualization/fig_main_result.py` (tick font 4.6 pt). Fix: use one colour for "reduced basis better" and one for "network better" in both panels; enlarge labels to 6.5 pt or show only the top and bottom rows; state in the caption that (b) is the 36 own-solver problems.

**M8. Fonts below 6.5 pt in Figs. 1, 2(b), 6.**
Evidence: about 3-4 pt after scaling (script font sizes 4.6, 5, 5.5 pt, then scaled to 0.85-0.9 of text width; Fig. 1 labels about 5 pt). Fix: re-draw at final size with 6.5-8 pt text, drop the duplicate Fig. 6 row, put a shared colour bar per column type.

**M9. Supplement deviations table cut off at the page bottom; two nearly empty pages.**
Location: `supplement.pdf` pp. 5-7; `supplement.log` "Overfull \vbox (420.8pt too high)". Fix: `longtable`, wider Detail column, allow row breaks.

**M10. Metrics not given as equations; NRMSE undefined.**
Location: `s5_setup.tex:11`, Table 7. Fix: add equations for regret, forecast ratio, reach-target classification and NRMSE, and say what the NRMSE is normalised by.

**M11. No computational-complexity analysis.**
Location: Sec. 6.4. Evidence: only wall-clock seconds on one CPU. Fix: add a short table of asymptotic cost for each pool member and the learning curve (cubic in training size for exact GP, etc., as computed from the code), plus measured scaling in N.

**M12. H2 reach-target criterion does not discriminate.**
Location: Tables 3-4, `s6b_tool.tex:6`. Evidence: pass threshold 75%; the always-guess rate is 75% for the 1% target, as the text says. Fix: report the accuracy next to the base rate and say the 1% row is uninformative; or give an agreement statistic beyond the base rate.

**M13. Unexplained denominators and mixed cell counts.**
Location: Table 3 caption (24) vs H4 (16); Sec. 6.3. Fix: state once that the tuned network was run only at N = 256 and 1024 (and why), and caption Table 3 accordingly.

**M14. "The benchmark" undefined; three different sets of "eight problems"; inconsistent names for the same objects.**
Location: abstract onward; Sec. 6.1; supplement S3. Fix: see 4.2.

**M15. Typed numbers that should be macros** (list in 3.1). In particular `\ExpBChanged` and `\FullCellsN` exist and are unused; the single wrong number (M2) shows the risk. Fix: replace and add a lint step to `check_build.sh` that fails on a digit or number word in `sections/*.tex` outside an allow-list.

**M16. Counts below ten printed as digits** (list in 4.1). Fix: word-form macros.

**M17. Placeholders and unfinished front and back matter.**
Location: `main.tex` (authors, journal), acknowledgments, availability, cover letter. Fix: complete before any submission; give an archive DOI.

**M18. Empty `s7_conclusion.tex`, with the conclusion text inside `s6c_discussion.tex`.**
Fix: move the conclusion into `s7_conclusion.tex` or delete the file and the `\input`.

### MINOR

- **m1.** Double full stops after about 20 run-in headings (2.4).
- **m2.** Table 1 header collision; table is nearly all dashes and rests on abstracts (1.2). Either read the works fully or cut the table to the rows that carry information.
- **m3.** Table 6 duplicate rows; Table 4 row order (H5 first).
- **m4.** Fig. 4 legend "N_1"; Fig. 7 raw Markdown; Fig. 3 colours without meaning and an unexplained "GP, one length-scale" box.
- **m5.** Reference formatting: Bērziņš author string, "neurIPS", "(preprint) (2026)", missing DOIs, five "empty pages" warnings, four unused entries, no citations for scikit-learn, SciPy, PyTorch, NumPy (Sec. 5).
- **m6.** Cross-reference style mixed ("section" / "fig." / "Figure"); author's style is "Sec. S2", "Table S1".
- **m7.** Hyphen used as minus in "-0.03" (macro `\ExtMedianExt`).
- **m8.** `authoryear=false` option unused (warning in `main.log`).
- **m9.** First paragraph of the introduction has no references for its claims; illustration in parentheses ("As an illustration, not a result of this paper") is awkward.
- **m10.** 62.5% printed as 62% in the abstract. State the count (15 of 24) or round half up.
- **m11.** Sec. 6 opening provenance sentence belongs elsewhere (4).
- **m12.** Supplement header "Preprint submitted to Elsevier" vs main "journal to be chosen".
- **m13.** "Honest record" and similar self-assessing wording (4.3).
- **m14.** Fig. 7 "Runs needed ... about 235" with 256 runs in hand needs a one-line explanation.

---

## 8. Prioritised fix list

1. Fix the `\cref` / `xr-hyper` leak (M1) and extend `check_build.sh` so it catches it.
2. Correct "three of these eight" to five and derive derived counts from macros (M2, M15); add a lint for typed numbers.
3. Rewrite the abstract to at most 250 words with three headline numbers and without "explains" (M3). Replace "pre-registered" with "pre-specified" throughout (M5). Remove or support "basis rank" (M4).
4. Fix the supplement deviations table (M9) and the zero-overfull target (Table 1 header, path breaks in main and supplement).
5. Redraw figures: consistent colours, 6.5-8 pt fonts, no duplicated rows, no label collisions, cite Fig. 5, fix Fig. 4 legend, caption first sentences that state the answer (M6, M7, M8).
6. Add equations for regret, forecast ratio, NRMSE (M10); add a complexity paragraph or table (M11); report the base rate next to the reach-target accuracy (M12); explain 16 vs 24 cells (M13).
7. Word-form macros for counts below ten (M16); one name per object, define "the benchmark" and "decade" (M14).
8. References: cite software and the textbook, delete anything still unused, repair author and venue strings, add DOIs consistently (m5). Add references to the first paragraph of the introduction.
9. Move the conclusion into its own file and remove the empty one (M18).
10. Fill every placeholder and create the archive DOI (M17). Re-read Table 1 sources in full or shrink the table.
11. Decide the paper's audience (tool or benchmark), and move one of the two bodies of evidence to the supplement to bring the length down for a venue that sets a page limit. Add at least one expensive-solver case or state clearly in the title and abstract that the tool is validated only on fast solvers.
