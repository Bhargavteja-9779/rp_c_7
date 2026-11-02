"""Minimal demo: a synthetic 'simulation' (a smooth field depending on 3 inputs); run SurroSelect and print the report."""
import numpy as np, warnings
warnings.filterwarnings("ignore")
from surroselect import SurrogateSelector, make_report

rng = np.random.default_rng(0); g = np.linspace(0, 1, 100)
simulate = lambda x: np.sin(3 * x[0] * g + x[1]) + x[2] * np.exp(-((g - 0.5) / 0.2) ** 2)      # stands in for a slow solver
X = rng.random((96, 3)); Y = np.array([simulate(x) for x in X])                                  # 96 "simulation runs"
sel = SurrogateSelector(cv=4, verbose=False).fit(X, Y); sel.learning_curve()
print(make_report(sel, target=1e-3))
Xt = rng.random((50, 3)); Yt = np.array([simulate(x) for x in Xt]); print("test error of the selected model:", float(np.mean(np.linalg.norm(Yt - sel.predict(Xt), axis=1) / np.linalg.norm(Yt, axis=1))))
