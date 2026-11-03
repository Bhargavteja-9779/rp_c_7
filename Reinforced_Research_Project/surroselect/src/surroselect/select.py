"""Cross-validated, tie-aware model selection, a budget-to-accuracy (learning-curve) predictor and a basis-limit check."""
from __future__ import annotations
import time, copy, numpy as np
from .models import rel_l2, POD, default_candidates, get_metric

TIE_BAND_DECADES = 0.1          # errors within a factor 10**0.1 (about 26%) of the best count as tied


def _power_law(ns, es, use=3):
    """Fit log10 e = a - b log10 n on the last `use` points; returns (a, b)."""
    ns, es = np.asarray(ns, float)[-use:], np.asarray(es, float)[-use:]; A = np.c_[np.ones(len(ns)), -np.log10(ns)]; coef, *_ = np.linalg.lstsq(A, np.log10(es), rcond=None); return float(coef[0]), float(coef[1])


class SurrogateSelector:
    """Fit the candidate stand-in models, choose by k-fold cross-validated mean relative L2 error, and report ties, the POD floor and a learning curve.

    Parameters: candidates (list of model objects with fit/predict, default pool if None); cv (folds); tie_band (decades); random_state."""
    def __init__(self, candidates=None, cv=4, tie_band=TIE_BAND_DECADES, random_state=0, verbose=False, metric="rel_l2"):
        self.candidates, self.cv, self.tie_band, self.random_state, self.verbose, self.metric = candidates, cv, tie_band, random_state, verbose, metric; self._m = get_metric(metric)

    # ------------------------------------------------------------------ helpers
    def _scale(self, X): return (np.asarray(X, float) - self.lo_) / self.span_
    def _folds(self, N):
        rs = np.random.default_rng(self.random_state); perm = rs.permutation(N); return [(np.setdiff1d(perm, f, assume_unique=True), f) for f in np.array_split(perm, self.cv)]

    # ------------------------------------------------------------------ main entry
    def fit(self, X, Y, refit_all=False):
        X = np.asarray(X, float); Y = np.asarray(Y, float); N, p = X.shape; self.lo_ = X.min(0); self.span_ = np.where(X.max(0) - X.min(0) > 0, X.max(0) - X.min(0), 1.0); Xs = self._scale(X)
        cands = self.candidates if self.candidates is not None else default_candidates(Y.shape[1], N); self.pool_ = cands; folds = self._folds(N); self.folds_ = folds; rows = []
        for c in cands:
            errs, t0 = [], time.time()
            try:
                for tr, va in folds: errs.append(self._m(Y[va], copy.deepcopy(c).fit(Xs[tr], Y[tr]).predict(Xs[va]), Y[tr]))
                err = float(np.mean(errs)); msg = ""
            except Exception as e: err, msg = float("inf"), repr(e)[:120]
            rows.append(dict(name=c.name, cv_error=err, fold_errors=errs, seconds=time.time() - t0, message=msg))
            if self.verbose: print(f"  {c.name:28s} CV error {err:.3e}  ({rows[-1]['seconds']:.1f}s)")
        self.cv_table_ = sorted(rows, key=lambda r: r["cv_error"]); best = self.cv_table_[0]; self.best_name_ = best["name"]; self.best_cv_error_ = best["cv_error"]
        self.ties_ = [r["name"] for r in self.cv_table_ if r["cv_error"] <= best["cv_error"] * 10**self.tie_band]
        idx = {c.name: c for c in cands}; self.model_ = copy.deepcopy(idx[self.best_name_]).fit(Xs, Y); self.n_train_, self.p_, self.m_ = N, p, Y.shape[1]
        self.all_models_ = {c.name: copy.deepcopy(c).fit(Xs, Y) for c in cands if np.isfinite(next(r["cv_error"] for r in rows if r["name"] == c.name))} if refit_all else None
        self._X, self._Y = Xs, Y; self.floor_report_ = self._floor(Xs, Y, folds); return self

    def predict(self, X): return self.model_.predict(self._scale(X))

    # ------------------------------------------------------------------ basis-limit check
    def _floor(self, Xs, Y, folds, r=32):
        fl = [POD(Y[tr], r).projection_error(Y[va], None if self.metric == "rel_l2" else self._m, Y[tr]) for tr, va in folds]; floor = float(np.mean(fl))
        pod_rows = [r_ for r_ in self.cv_table_ if r_["name"].startswith(("pod_", )) and np.isfinite(r_["cv_error"])]
        best_pod = pod_rows[0] if pod_rows else None
        full = [r_ for r_ in self.cv_table_ if r_["name"].startswith("gp_full") and np.isfinite(r_["cv_error"])]
        limited = bool(best_pod is not None and best_pod["cv_error"] <= 1.25 * floor)
        return dict(rank=r, pod_floor_cv=floor, best_pod_model=(best_pod or {}).get("name"), best_pod_cv_error=(best_pod or {}).get("cv_error"), basis_limited=limited,
                    best_full_field_cv_error=(full[0]["cv_error"] if full else None),
                    advice=("The best POD-based model is within 25% of the best error any 32-mode POD basis can reach: the basis, not the regressor, limits accuracy. "
                            "Use a full-field model, a larger basis, or a nonlinear (autoencoder) output map." if limited else "The POD basis is not the limiting factor at this training size."))

    # ------------------------------------------------------------------ budget-to-accuracy
    def learning_curve(self, name=None, fractions=(0.125, 0.25, 0.5, 1.0), min_n=12):
        """Cross-validated error of one candidate (default: the selected one) when trained on growing fractions of the training folds."""
        name = name or self.best_name_; c = next(c for c in self.pool_ if c.name == name); ns, es = [], []
        for f in fractions:
            e, n_used = [], []
            for tr, va in self.folds_:
                k = max(min_n, int(np.ceil(f * len(tr)))); sub = tr[:k]; n_used.append(len(sub)); e.append(self._m(self._Y[va], copy.deepcopy(c).fit(self._X[sub], self._Y[sub]).predict(self._X[va]), self._Y[sub]))
            ns.append(float(np.mean(n_used))); es.append(float(np.mean(e)))
        self.curve_ = dict(name=name, n=ns, error=es); return self.curve_

    def predict_error(self, n, use=3):
        """Predict the (test) error of the selected model trained on n runs, by extrapolating the learning curve; returns (central, low, high) using the last 3 / all 4 points."""
        cv = getattr(self, "curve_", None) or self.learning_curve(); out = []
        for u in (use, len(cv["n"])):
            a, b = _power_law(cv["n"], cv["error"], u); out.append(10 ** (a - b * np.log10(n)))
        c = out[0]; return c, min(out), max(out)

    def runs_needed(self, target, use=3, max_factor=16):
        """Smallest number of runs at which the extrapolated error reaches `target`; None if the curve is flat (exponent < 0.1) or the answer is more than max_factor x the current budget."""
        cv = getattr(self, "curve_", None) or self.learning_curve(); a, b = _power_law(cv["n"], cv["error"], use)
        if b < 0.1: return None
        n = 10 ** ((a - np.log10(target)) / b); return float(n) if n <= max_factor * self.n_train_ else None
