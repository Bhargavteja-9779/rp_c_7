[Date]

The Editor-in-Chief
*Engineering with Computers* (provisional target; to be confirmed against the journal's current scope and guidelines)

**Manuscript:** Linear-subspace or neural? A pre-registered, matched-tuning comparison of surrogate families for parametric PDEs

Dear Editor,

We submit the above manuscript for consideration as a research article.

**Problem.** Surrogate models for parametric PDEs are routinely built by first choosing between linear-subspace approaches (POD with a regressor) and neural networks that map parameters to fields. The choice is made before the simulation budget is spent, and published comparisons are known to depend on how carefully each competitor is tuned.

**What we did.** In a study whose protocol and analysis code were committed to version control before any comparative result existed, we compared five surrogates under identical hyper-parameter budgets on 16 simulated parametric-PDE instances at six training budgets and three seeds, and tested four pre-specified hypotheses with Holm correction. Post-hoc analyses are labelled as exploratory.

**Principal findings.** No family was uniformly better. Gaussian-process regression of POD coefficients was up to about three orders of magnitude more accurate on smooth problems, with an advantage that grew with the number of training solves, while neural networks were modestly better on transport- and front-dominated instances. Two pre-registered expectations were not supported, and a pre-registered pilot-data selection rule was not confirmed; we report these negative results in full. Giving the neural family a larger tuning budget than the linear family inflated its apparent advantage in the pre-registered test, although the effect was concentrated in five of sixteen instances.

**Fit with the journal.** The work concerns the construction and evaluation of surrogate models for simulation-based engineering. We believe the careful comparison protocol, the openly reported negative results and the released code will be useful to readers who must choose and validate surrogate models. We do not claim a new method or state-of-the-art accuracy, and the conclusions are limited to a suite of simulated, low-dimensional problems.

**Declarations (to be confirmed by the authors before submission).** [The manuscript is original, has not been published and is not under consideration elsewhere.] [All authors approved the submission.] [Conflict-of-interest, funding and ethics statements.] [Disclosure that the study design, code and first draft were produced with an autonomous AI assistant, with the human authors taking responsibility for the content, in line with the journal's AI policy.] [Data/code deposit DOI.]

Sincerely,

[Corresponding author name, affiliation, e-mail — to be supplied]
