# Triage of Round 1 (scientific validity) review — reviewer: fresh-context AI agent (not a human)
Verdict received: **major revision** (arithmetic reproduced: 27/27 recomputed numbers match; inference problems). Each finding was checked against code/data before acting.

| ID | Finding | Verified? | Action |
|---|---|---|---|
| C1 | KRR control structurally handicapped (ridge floor, 8 draws); ML-II claim not isolated | **Yes** (I re-ran a wide-ridge KRR on bratu_L1/N=256: 7.9e-7 vs POD+GP 1.4e-6 and registered KRR 7.0e-4) | Pre-registered addendum v2.3 (48a0698) and ran Exp H (wide KRR, B=8/32). Result: median ratio 6.5x / 2.7x; verdict "mixed". "Explained by marginal likelihood" withdrawn everywhere; claim reworded to regressor/search quality; D1 rejection kept but scoped to the restricted control. POD+Poly observation added. |
| M1 | Exp G shown only for GP-clear cells; full table shows no-POD GP beating NNs on moving-feature cells | **Yes** (18 vs 12 clear wins at N=1024; NN-clear 9 -> 5) | Table 4b added (all 72 cells); claims about moving/discontinuous features tempered in 5.1, 6, 8. |
| M2 | NN under-trained; N=1024 step-count confound applies to headline counts; Exp F "ROBUST" overstated (L-BFGS capped at 400, no-op in 21%) | **Yes** | Confound stated up front in section 5 and Tables 1-2 captions; F verdict wording changed to "not overturned by the tested refits"; abstract qualified ("about three decades", "confounded"); 5.1 margin statement qualified. |
| M3 | Shared search draws; 3-vs-2 members; edge statistic uninformative (chance 0.85) | **Yes** (script itself notes 0.8-0.85) | Disclosed in 5/5.4/5.5/7; edge statistic withdrawn (row removed; addendum 2.3 item f). |
| M4 | A2 "7/7, p=1.7e-6" over-reads a near-tautological test | **Yes** | p-value no longer used; family structure (4 families) and control 0.997 stated; descriptive wording. |
| M5 | Mechanism cells oracle-selected, pooled, non-independent; iso/ARD >3x in 29% of cells; Exp B oracle classes | **Yes** | Disclosed in Table 4a/5 captions and 5.3; share >3x reported (29%). |
| m1 | NN-clear count unstable (6-8) | Yes | Stated "6-8 depending on band". |
| m2 | H2 baseline degenerate | Yes | Table 3 caption gives B0 comparison and baseline RMSEs; 5.2 reports B1log. |
| m3 | H4a generalisation one-directional | Yes | 5.5 reworded. |
| m4 | A2 control "1.00" actually 0.9967 | Yes | Shown as 0.997. |
| m5 | "15 families" wrong (19 labels); f1<-2 => p=3 true only in the 24 | Yes | Count now computed (19 labels, 36 instances); caveat added. |
| m6 | Config-draw halves not exchangeable | Yes | Caveat added. |
| m7 | S1 baseline not like-for-like | Yes | Caption: "uninformative". |
| m8 | P2 numbers differ by procedure | Yes | Both reported (10^4 pre-registered vs 10^6). |
| m9 | "nearly always toward NL" | Yes (15/15) | "always". |
| m10 | Power statement from AI audit not reproducible | Yes | Statement removed from text. |
