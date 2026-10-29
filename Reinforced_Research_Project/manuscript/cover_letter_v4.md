[DATE]

To the Editor of [JOURNAL NAME — to be chosen by the authors after verifying the journal's current scope, article types, indexing, impact-factor/quartile status and author guidelines]

Dear Editor,

We submit "Do You Need a Neural Network? Choosing a Fast Stand-In for Slow Physics Simulations" for consideration as a [comparative study / research article — to match the journal's article type].

**What the paper does.** With a budget of 32 to 1,024 simulation runs, should one build a Gaussian-process stand-in on a reduced basis, or train a neural network? We compare five stand-in models under one tuning procedure on 36 simulated benchmark problems from six classes named after application areas, report how many runs each family needs to reach 10%, 1% and 0.1% error, and run follow-up experiments on why the winners win. The paper ends with a practical checklist.

**What the paper finds.** On smooth problems with few inputs the Gaussian-process stand-ins were far more accurate than lightly tuned networks; for coarse accuracy targets the two were about equal; some of the networks' apparent wins came from the limits of the reduced basis; and a good part of the Gaussian-process advantage reflects how widely and carefully its regularisation is searched. Results moved noticeably when the networks were trained longer. Most of our original hypotheses were not supported, including that a quick pilot statistic predicts the winner; these are reported in the supplement.

**What the paper is not.** It proposes no new method, uses no field or industrial data, and does not claim state-of-the-art accuracy. Its findings confirm and quantify earlier reports that Gaussian-process and kernel methods are hard to beat on smooth problems. The networks were only lightly tuned.

**Transparency.** Hypotheses, code and success criteria were committed to version control before each group of runs (our own history, not an independent registry); several follow-up experiments were designed after seeing earlier results, and one control was widened after an AI-agent review of our draft showed it was too narrow. All of this is documented in Supplement S1. The analysis, audits and drafting were carried out with an AI system (Claude) under our direction; no human independent review has yet been performed. Code and generated data are available in the repository; a permanent archive [DOI — to be created] will be provided before publication.

The manuscript has not been published or submitted elsewhere. [Suggested reviewers, competing interests, funding — to be completed by the authors.]

Sincerely,
[AUTHOR NAMES AND AFFILIATIONS — to be supplied]
