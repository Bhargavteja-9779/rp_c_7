"""Statistical routines for the pre-registered analyses (pure functions, unit-tested on synthetic data)."""
from __future__ import annotations
import numpy as np
from scipy import stats


def holm(pvals: dict[str, float], alpha=0.05):
    """Holm-Bonferroni. Returns {name: (adjusted_p, reject)}."""
    names = sorted(pvals, key=lambda k: pvals[k]); m = len(names); out = {}; run = 0.0
    for i, k in enumerate(names):
        run = max(run, min(1.0, (m - i) * pvals[k])); out[k] = (run, run < alpha)
    return out


def wilcoxon_greater(x):
    x = np.asarray(x, float); r = stats.wilcoxon(x, alternative="greater", method="auto")
    return dict(n=int(len(x)), median=float(np.median(x)), statistic=float(r.statistic), p=float(r.pvalue))


def wilcoxon_two_sided(x):
    x = np.asarray(x, float); r = stats.wilcoxon(x, alternative="two-sided", method="auto")
    return dict(n=int(len(x)), median=float(np.median(x)), statistic=float(r.statistic), p=float(r.pvalue))


def sign_test_greater(k, n):
    r = stats.binomtest(int(k), int(n), 0.5, alternative="greater")
    ci = r.proportion_ci(0.95, method="wilson")
    return dict(k=int(k), n=int(n), p=float(r.pvalue), prop=float(k / n) if n else float("nan"), ci95=[float(ci.low), float(ci.high)])


def mcnemar_exact_greater(b, c):
    """b: cells flipping in the hypothesised direction, c: opposite direction."""
    if b + c == 0: return dict(b=int(b), c=int(c), p=1.0)
    return dict(b=int(b), c=int(c), p=float(stats.binomtest(int(b), int(b + c), 0.5, alternative="greater").pvalue))


def ridge_fit(X, y, lam):
    mu, sd = X.mean(0), X.std(0) + 1e-12; Z = (X - mu) / sd; ym = y.mean()
    beta = np.linalg.solve(Z.T @ Z + lam * np.eye(Z.shape[1]), Z.T @ (y - ym)); return dict(mu=mu, sd=sd, beta=beta, ym=ym)


def ridge_predict(m, X): return ((X - m["mu"]) / m["sd"]) @ m["beta"] + m["ym"]


def lofo_residuals(X, y, groups, lam_per_row=1e-3):
    """Leave-one-group-out ridge residuals. X: (n, d) design WITHOUT intercept."""
    res = np.zeros(len(y))
    for g in np.unique(groups):
        te = groups == g; tr = ~te
        m = ridge_fit(X[tr], y[tr], lam_per_row * tr.sum()); res[te] = y[te] - ridge_predict(m, X[te])
    return res


def cluster_bootstrap_rmse_diff(res_base, res_new, groups, n_boot=10000, seed=0):
    """Delta = RMSE(base) - RMSE(new); resample whole groups (families) with replacement. One-sided p for Delta<=0."""
    rng = np.random.default_rng(seed); G = np.unique(groups); idx = {g: np.where(groups == g)[0] for g in G}
    obs = float(np.sqrt(np.mean(res_base**2)) - np.sqrt(np.mean(res_new**2))); d = np.empty(n_boot)
    for b in range(n_boot):
        pick = np.concatenate([idx[g] for g in rng.choice(G, len(G), replace=True)])
        d[b] = np.sqrt(np.mean(res_base[pick] ** 2)) - np.sqrt(np.mean(res_new[pick] ** 2))
    return dict(delta=obs, ci95=[float(np.percentile(d, 2.5)), float(np.percentile(d, 97.5))], p=float((np.sum(d <= 0) + 1) / (n_boot + 1)),
                rmse_base=float(np.sqrt(np.mean(res_base**2))), rmse_new=float(np.sqrt(np.mean(res_new**2))))


def sign_accuracy(y, yhat):
    acc = float(np.mean(np.sign(y) == np.sign(yhat))); maj = float(max(np.mean(y > 0), np.mean(y <= 0))); return dict(accuracy=acc, majority_baseline=maj)


def kendall_tau(a, b):
    t = stats.kendalltau(a, b); return float(t.statistic) if not np.isnan(t.statistic) else float("nan")


def spearman(a, b):
    if len(set(np.round(a, 12))) < 2 or len(set(np.round(b, 12))) < 2: return float("nan")
    return float(stats.spearmanr(a, b).statistic)
