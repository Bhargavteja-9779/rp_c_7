"""Candidate stand-in models. All map inputs X (N, p) to output fields Y (N, m) and share fit/predict. Self-contained (numpy, scipy, scikit-learn)."""
from __future__ import annotations
import warnings, numpy as np
from scipy.spatial.distance import cdist
from sklearn.exceptions import ConvergenceWarning
from sklearn.gaussian_process import GaussianProcessRegressor as GPR
from sklearn.gaussian_process.kernels import RBF, Matern, WhiteKernel, ConstantKernel as C


warnings.filterwarnings("ignore", category=ConvergenceWarning)    # the GP optimiser often stops at a parameter bound; this is expected and harmless here


def rel_l2(Y, Yh):
    """Mean relative L2 error over samples."""
    return float(np.mean(np.linalg.norm(Y - Yh, axis=1) / (np.linalg.norm(Y, axis=1) + 1e-300)))


class POD:
    """Proper orthogonal decomposition of the centred snapshots."""
    def __init__(self, Y, r):
        self.mean = Y.mean(0); U, s, Vt = np.linalg.svd(Y - self.mean, full_matrices=False); self.r = int(min(r, len(s))); self.V = Vt[: self.r].T; self.s = s
    def encode(self, Y): return (Y - self.mean) @ self.V
    def decode(self, A): return A @ self.V.T + self.mean
    def projection_error(self, Y): return rel_l2(Y, self.decode(self.encode(Y)))


class _Base:
    needs_scaled_inputs = True
    def _prep(self, X): return np.asarray(X, float)


def _kern(A, B, kind, ell):
    d = cdist(A / ell, B / ell)
    if kind == "rbf": return np.exp(-0.5 * d**2)
    s5 = np.sqrt(5) * d; return (1 + s5 + s5**2 / 3) * np.exp(-s5)


class PodGP(_Base):
    """POD + anisotropic (ARD) Gaussian process on the leading modes (marginal-likelihood fitted); the other modes share the 4th mode's kernel."""
    def __init__(self, kernel="matern52", r=32, n_gp_modes=4, n_opt=300, seed=0): self.kernel, self.r, self.n_gp_modes, self.n_opt, self.seed = kernel, r, n_gp_modes, n_opt, seed
    @property
    def name(self): return f"pod_gp[{self.kernel},r={self.r}]"
    def fit(self, X, Y):
        X = self._prep(X); p = X.shape[1]; self.pod = POD(Y, self.r); A = self.pod.encode(Y); self.sd = A.std(0) + 1e-12; Z = A / self.sd
        rs = np.random.default_rng(self.seed); sub = rs.permutation(len(X))[: self.n_opt]; self.gps = []; k_last = None
        for j in range(self.pod.r):
            if j < self.n_gp_modes:
                base = C(1.0, (1e-3, 1e3)) * (Matern(np.ones(p), (1e-2, 1e3), nu=2.5) if self.kernel == "matern52" else RBF(np.ones(p), (1e-2, 1e3))) + WhiteKernel(1e-6, (1e-10, 1e-1))
                g = GPR(base, normalize_y=False, n_restarts_optimizer=0, random_state=self.seed).fit(X[sub], Z[sub, j]); k_last = g.kernel_
                self.gps.append(GPR(k_last, optimizer=None).fit(X, Z[:, j]))
            else: self.gps.append(GPR(k_last, optimizer=None).fit(X, Z[:, j]))
        return self
    def predict(self, X):
        X = self._prep(X); A = np.column_stack([g.predict(X) for g in self.gps]) * self.sd; return self.pod.decode(A)


class GPFull(_Base):
    """Gaussian process on the full output field (no POD): one shared ARD kernel fitted on at most n_opt points, all outputs jointly."""
    def __init__(self, kernel="matern52", n_opt=300, seed=0): self.kernel, self.n_opt, self.seed = kernel, n_opt, seed
    @property
    def name(self): return f"gp_full[{self.kernel}]"
    def fit(self, X, Y):
        X = self._prep(X); p = X.shape[1]; self.mean = Y.mean(0); self.s = float((Y - self.mean).std() + 1e-12); T = (Y - self.mean) / self.s
        sub = np.random.default_rng(self.seed).permutation(len(X))[: self.n_opt]
        base = C(1.0, (1e-3, 1e3)) * (Matern(np.ones(p), (1e-2, 1e3), nu=2.5) if self.kernel == "matern52" else RBF(np.ones(p), (1e-2, 1e3))) + WhiteKernel(1e-6, (1e-10, 1e-1))
        g = GPR(base, normalize_y=False, n_restarts_optimizer=0, random_state=self.seed).fit(X[sub], T[sub]); self.gp = GPR(g.kernel_, optimizer=None).fit(X, T); return self
    def predict(self, X): return self.gp.predict(self._prep(X)) * self.s + self.mean


class PodKRRWide(_Base):
    """POD + kernel ridge; (kernel, length-scale, ridge) chosen over a WIDE grid by closed-form leave-one-out error (no marginal likelihood)."""
    ELLS = np.logspace(np.log10(0.1), np.log10(30.0), 14); LAMS = np.logspace(-16, -2, 15)
    def __init__(self, r=32): self.r = r
    name = "pod_krr_wide"
    def fit(self, X, Y):
        X = self._prep(X); N, p = X.shape; self.pod = POD(Y, self.r); A = self.pod.encode(Y); best = (np.inf, None)
        for kind in ("matern52", "rbf"):
            for e in self.ELLS:
                ell = e * np.sqrt(p); K = _kern(X, X, kind, ell); w, Q = np.linalg.eigh(0.5 * (K + K.T)); w = np.maximum(w, 0.0); QtA = Q.T @ A; Q2 = Q**2
                for lam in self.LAMS:
                    d = 1.0 / (w + lam * N); Hdiag = Q2 @ (w * d); alpha = Q @ (QtA * d[:, None])
                    fit_ = A - lam * N * alpha; resid = (A - fit_) / np.maximum(1 - Hdiag, 1e-12)[:, None]; score = float(np.mean(np.sum(resid**2, axis=1)))
                    if score < best[0]: best = (score, (kind, ell, lam, alpha))
        self.kind, self.ell, self.lam, self.alpha = best[1]; self.X = X; self.loo_score = best[0]; return self
    def predict(self, X): return self.pod.decode(_kern(self._prep(X), self.X, self.kind, self.ell) @ self.alpha)


class PodPoly(_Base):
    """POD + ridge polynomial of total degree <= deg (<= max_feat features); (degree, ridge) chosen by closed-form leave-one-out error."""
    LAMS = np.logspace(-12, 1, 14)
    def __init__(self, r=32, max_deg=6, max_feat=3000): self.r, self.max_deg, self.max_feat = r, max_deg, max_feat
    name = "pod_poly"
    def fit(self, X, Y):
        from sklearn.preprocessing import PolynomialFeatures
        X = self._prep(X); N, p = X.shape; self.pod = POD(Y, self.r); A = self.pod.encode(Y); best = (np.inf, None); Xc = 2 * X - 1
        for deg in range(1, self.max_deg + 1):
            pf = PolynomialFeatures(deg, include_bias=True); F = pf.fit_transform(Xc[:2])
            if F.shape[1] > self.max_feat: break
            F = pf.transform(Xc); U, s, Vt = np.linalg.svd(F, full_matrices=False); UtA = U.T @ A; U2 = U**2
            for lam in self.LAMS:
                d = s**2 / (s**2 + lam * N); Hdiag = U2 @ d; fit_ = U @ (d[:, None] * UtA); resid = (A - fit_) / np.maximum(1 - Hdiag, 1e-12)[:, None]; score = float(np.mean(np.sum(resid**2, axis=1)))
                if score < best[0]: best = (score, (deg, lam, pf, Vt.T @ ((s / (s**2 + lam * N))[:, None] * UtA)))
        self.deg, self.lam, self.pf, self.coef = best[1]; self.loo_score = best[0]; return self
    def predict(self, X): return self.pod.decode(self.pf.transform(2 * self._prep(X) - 1) @ self.coef)


def default_candidates(m, N):
    """The default candidate pool (fast, no neural networks). Full-field GP only when the output is not huge."""
    c = [PodGP("matern52", 32), PodGP("rbf", 32), PodGP("matern52", 8), PodKRRWide(32), PodPoly(32)]
    if m <= 2000: c += [GPFull("matern52"), GPFull("rbf")]
    return c
