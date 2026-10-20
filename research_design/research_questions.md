# Central problem, research questions, contribution

**Central problem.** Practitioners must choose a surrogate family for a parametric PDE *before* paying for the training-data budget. Theory (Kolmogorov n-width) says linear-subspace surrogates (POD + regression) win when solution manifolds are spectrally compact and nonlinear-output networks are needed otherwise, but no validated, cheap, *a-priori* decision rule exists, and published neural-vs-baseline comparisons are known to be sensitive to how hard the baselines are tuned (McGreivy & Hakim 2024).

**RQ1 (budget crossover).** How does the accuracy ratio between the best nonlinear-output surrogate (NL) and the best linear-subspace surrogate (LS) change with the number of training solves N, across qualitatively different parametric PDEs?
**RQ2 (a-priori diagnostic).** Do features computable from a 32-snapshot pilot (cross-validated POD reconstruction error, spectral slope) predict, out-of-sample across *unseen PDE families*, which family wins and by how much, beyond what N and parameter dimension predict?
**RQ3 (extrapolation).** Does parameter-space extrapolation penalise NL and LS differently? (exploratory)
**RQ4 (tuning asymmetry).** How much does asymmetric tuning effort (NL tuned with B=8 configurations, LS left at default) inflate the apparent NL win rate relative to symmetric tuning?
**RQ5 (cost, descriptive).** What are measured training/inference costs and, under explicit stylised full-order-model cost scenarios, the break-even number of queries?

**Contribution (claim limited to what experiments can show).** (i) A pre-registered, matched-tuning comparison of 5 surrogate methods (3 LS, 2 NL) on 16 PDE instances × 6 budgets × ≥3 seeds; (ii) an out-of-sample test of a pilot-based diagnostic; (iii) a paired quantification of tuning-asymmetry bias. **Not claimed:** a new architecture, state-of-the-art accuracy, a theory, or generality beyond this suite.
