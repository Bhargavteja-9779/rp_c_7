# Journal comparison — observed submission-to-acceptance evidence

Generated 2026-10-20 by `journal_selection/tools/*.py` from `journal_selection/data/*.csv`. **All figures are OBSERVED history of recently published articles (received → accepted dates in public metadata). They are not publisher guarantees and are not JCR data.** Selection effects apply: only *accepted* papers are observed, so desk rejections, rejections and withdrawn papers are invisible, which biases observed times downward.

## A. Named candidate journals (Crossref-deposited dates, random samples of 2025-01 → 2026-09 articles)

| Journal | Crossref sampled | with both dates | median days | Q25–Q75 | share ≤72 d | Evidence status |
|---|---|---|---|---|---|---|
| Complex & Intelligent Systems (Springer) | 258 | 257 | 150 | 108–223 | 7% | observed (Crossref) |
| J King Saud Univ CIS (Springer) | 274 | 273 | 76 | 57–103 | 45% | observed (Crossref) |
| Results in Engineering (Elsevier) | 293 | 0 | – | – | – | **TIMELINE UNVERIFIED** (publisher does not deposit received/accepted dates in Crossref) |
| Alexandria Eng J (Elsevier) | 282 | 0 | – | – | – | **TIMELINE UNVERIFIED** (publisher does not deposit received/accepted dates in Crossref) |
| Ain Shams Eng J (Elsevier) | 265 | 0 | – | – | – | **TIMELINE UNVERIFIED** (publisher does not deposit received/accepted dates in Crossref) |
| Scientific Reports (Springer Nature) | 299 | 292 | 138 | 98–204 | 13% | observed (Crossref) |
| IEEE Access | 300 | 0 | – | – | – | **TIMELINE UNVERIFIED** (publisher does not deposit received/accepted dates in Crossref) |
| Expert Systems with Applications (Elsevier) | 295 | 0 | – | – | – | **TIMELINE UNVERIFIED** (publisher does not deposit received/accepted dates in Crossref) |
| Knowledge-Based Systems (Elsevier) | 290 | 0 | – | – | – | **TIMELINE UNVERIFIED** (publisher does not deposit received/accepted dates in Crossref) |
| Applied Soft Computing (Elsevier) | 292 | 0 | – | – | – | **TIMELINE UNVERIFIED** (publisher does not deposit received/accepted dates in Crossref) |
| Eng Appl of AI (Elsevier) | 296 | 0 | – | – | – | **TIMELINE UNVERIFIED** (publisher does not deposit received/accepted dates in Crossref) |
| Information Sciences (Elsevier) | 289 | 0 | – | – | – | **TIMELINE UNVERIFIED** (publisher does not deposit received/accepted dates in Crossref) |
| Journal of Big Data (Springer) | 250 | 248 | 236 | 166–367 | 1% | observed (Crossref) |
| Neural Computing & Applications (Springer) | 283 | 275 | 249 | 182–359 | 1% | observed (Crossref) |
| Computers in Biology and Medicine (Elsevier) | 290 | 0 | – | – | – | **TIMELINE UNVERIFIED** (publisher does not deposit received/accepted dates in Crossref) |
| Biomed Signal Process Control (Elsevier) | 292 | 0 | – | – | – | **TIMELINE UNVERIFIED** (publisher does not deposit received/accepted dates in Crossref) |
| Measurement (Elsevier) | 296 | 0 | – | – | – | **TIMELINE UNVERIFIED** (publisher does not deposit received/accepted dates in Crossref) |
| Int J Intelligent Systems (Wiley) | 204 | 204 | 188 | 126–268 | 8% | observed (Crossref) |
| Expert Systems (Wiley) | 234 | 215 | 170 | 105–282 | 12% | observed (Crossref) |
| Cognitive Computation (Springer) | 192 | 191 | 271 | 180–417 | 5% | observed (Crossref) |
| Applied Intelligence (Springer) | 282 | 108 | 237 | 186–319 | 2% | observed (Crossref) |
| Swarm & Evolutionary Computation (Elsevier) | 264 | 0 | – | – | – | **TIMELINE UNVERIFIED** (publisher does not deposit received/accepted dates in Crossref) |
| Pattern Recognition (Elsevier) | 283 | 0 | – | – | – | **TIMELINE UNVERIFIED** (publisher does not deposit received/accepted dates in Crossref) |
| Neurocomputing (Elsevier) | 294 | 0 | – | – | – | **TIMELINE UNVERIFIED** (publisher does not deposit received/accepted dates in Crossref) |
| Adv Eng Informatics (Elsevier) | 288 | 0 | – | – | – | **TIMELINE UNVERIFIED** (publisher does not deposit received/accepted dates in Crossref) |
| Eng Sci & Tech Int J (Elsevier) | 243 | 0 | – | – | – | **TIMELINE UNVERIFIED** (publisher does not deposit received/accepted dates in Crossref) |
| PeerJ Computer Science | 282 | 0 | – | – | – | **TIMELINE UNVERIFIED** (publisher does not deposit received/accepted dates in Crossref) |
| Artificial Intelligence Review (Springer) | 0 | 0 | – | – | – | **TIMELINE UNVERIFIED** (publisher does not deposit received/accepted dates in Crossref) |
| Computer Methods & Programs in Biomedicine (Elsevier) | 262 | 0 | – | – | – | **TIMELINE UNVERIFIED** (publisher does not deposit received/accepted dates in Crossref) |
| Journal of Computational Science (Elsevier) | 222 | 0 | – | – | – | **TIMELINE UNVERIFIED** (publisher does not deposit received/accepted dates in Crossref) |

Sample sizes are small and random; full-census recomputation for finalists is in section C.

## B. Elsevier / other titles indexed in PubMed (PubMed `History` received→accepted; ≤300 most recent 2025–2026 records each)

| PubMed journal | n | median days | Q75 | share ≤72 d |
|---|---|---|---|---|
| Comput Struct Biotechnol J | 298 | 92 | 118 | 32% |
| Comput Biol Chem | 294 | 100 | 143 | 28% |
| Comput Biol Med | 282 | 119 | 192 | 23% |
| Neuroimage | 296 | 150 | 206 | 8% |
| Comput Med Imaging Graph | 300 | 150 | 207 | 8% |
| Comput Methods Programs Biomed | 297 | 182 | 234 | 4% |
| Neural Netw | 299 | 218 | 284 | 0% |
| Med Image Anal | 296 | 228 | 312 | 0% |
| Artif Intell Med | 300 | 287 | 380 | 1% |

Note: *Journal of Biomedical Informatics* efetch failed (parse error) and is excluded; Expert Systems with Applications, Knowledge-Based Systems, Pattern Recognition, Applied Soft Computing, Neurocomputing etc. are not PubMed-indexed in a usable way → **TIMELINE UNVERIFIED**.

## C. Finalists — deterministic full harvest (all Crossref journal-article records in window; not a sample)

| Journal | window | records | with both dates | median | Q25 | Q75 | Q90 | max | share ≤72 d |
|---|---|---|---|---|---|---|---|---|---|
| Machine Learning for Computational Science and Engineering (Springer; ISSN 3005-1428 / 3005-1436) | 2023-01 → 2026-10 | 102 | 102 | 50 | 33 | 65 | 97 | 205 | 83.3% |
| Journal of King Saud University – Computer and Information Sciences (Springer; 1319-1578 / 2213-1248) | 2025-01 → 2026-10 | 1285 | 1280 | 74 | 56 | 99 | 128 | 266 | 48.1% |

## D. Landscape scan (2,423 non-MDPI journals from Crossref topical enumeration; two random samples of ≤100 each)

* Journals enumerated: 2423; journals with ≥30 dated articles: 828.
* Publishers that deposit dates: Springer (incl. BMC/Nature), Wiley, Taylor & Francis, ACM, IET, ASCE and several society publishers. **Elsevier, IEEE, PeerJ, OUP, CUP, SAGE do not deposit them** → their journals are TIMELINE UNVERIFIED unless PubMed covers them (section B).
* Journals with median ≤72 d and ≥40 dated articles: 56. Essentially all are in materials, chemistry, energy, civil engineering or are regional society journals — not computational/AI journals. The one computational/AI exception with strong evidence is **Machine Learning for Computational Science and Engineering**.

Domain-relevant, JCR-listed computational journals measured in the scan:

| Journal | n dated | median | Q75 | share ≤72 d |
|---|---|---|---|---|
| Archives of Computational Methods in Engineering | 174 | 116 | 196 | 18% |
| Computational Mechanics | 157 | 116 | 173 | 17% |
| Computational Geosciences | 125 | 191 | 285 | 9% |
| Machine Learning | 181 | 204 | 312 | 4% |
| Journal of Scientific Computing | 179 | 226 | 322 | 2% |
| Statistics and Computing | 173 | 241 | 321 | 2% |
| Neural Computing and Applications | 194 | 254 | 388 | 1% |
| Advances in Computational Mathematics | 128 | 323 | 428 | 0% |
