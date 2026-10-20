"""Pilot-data diagnostics computed from the first n0 training snapshots only (no test data, no model fits)."""
from __future__ import annotations
import numpy as np


def pilot_features(Y, r_list=(4, 8), max_r=16):
    """Y: (n0, m) pilot snapshots. Returns dict of features.
    cv_err[r]: leave-one-out relative POD reconstruction error with r modes (mean over snapshots).
    slope: least-squares slope of log10 singular values vs index over first 10 modes."""
    n0 = len(Y); cv = np.zeros((n0, max_r))
    for i in range(n0):
        tr = np.delete(Y, i, 0); mu = tr.mean(0); _, _, Vt = np.linalg.svd(tr - mu, full_matrices=False)
        y = Y[i] - mu; ny = np.linalg.norm(Y[i])
        for r in range(1, max_r + 1):
            V = Vt[: min(r, len(Vt))].T; cv[i, r - 1] = np.linalg.norm(y - V @ (V.T @ y)) / ny
    cvm = cv.mean(0)
    S = np.linalg.svd(Y - Y.mean(0), compute_uv=False); k = np.arange(1, min(10, len(S)) + 1)
    Sf = np.maximum(S[: len(k)], S[0] * 1e-12)          # floor: spectra below 1e-12 of the leading value are noise
    slope = np.polyfit(k, np.log10(Sf), 1)[0]
    out = {f"log_cv_err_r{r}": float(np.log10(cvm[r - 1] + 1e-16)) for r in r_list}
    out["slope"] = float(slope)
    tol = np.where(cvm <= 1e-2)[0]; out["r_tol1e-2"] = float(tol[0] + 1 if len(tol) else max_r + 1)
    return out
