"""Surrogate families. All map mu in [~-0.25,1.25]^p to a field in R^m.

LS (linear-subspace output):   pod_gp, pod_poly, pod_mlp
NL (nonlinear/direct output):  mlp_direct, bottleneck
Every method exposes: sample_config(rng, N, p, m, trial), fit(Xtr, Ytr, cfg, seed), predict(X).
Trial 0 is the method's fixed default (used for the tuning-budget analysis).
"""
from __future__ import annotations
import numpy as np, torch, warnings
from sklearn.gaussian_process import GaussianProcessRegressor as GPR
from sklearn.gaussian_process.kernels import Matern, RBF, ConstantKernel as C, WhiteKernel
from sklearn.preprocessing import PolynomialFeatures, StandardScaler
from sklearn.linear_model import Ridge
from sklearn.exceptions import ConvergenceWarning

warnings.filterwarnings("ignore", category=ConvergenceWarning)
warnings.filterwarnings("ignore", message=".*lbfgs.*")
LS_METHODS = ("pod_gp", "pod_poly", "pod_mlp"); NL_METHODS = ("mlp_direct", "bottleneck")
ALL_METHODS = LS_METHODS + NL_METHODS
NN_EPOCHS = 1500


def _x(X): return 2 * np.asarray(X) - 1                          # [0,1] -> [-1,1]
def _logu(rng, lo, hi): return float(10 ** rng.uniform(np.log10(lo), np.log10(hi)))


class POD:
    def __init__(self, Y, r):
        self.mean = Y.mean(0); U, S, Vt = np.linalg.svd(Y - self.mean, full_matrices=False)
        self.r = int(min(r, len(S))); self.V = Vt[: self.r].T; self.S = S
    def encode(self, Y): return (Y - self.mean) @ self.V
    def decode(self, A): return A @ self.V.T + self.mean


# ----------------------------------------------------------------------------- POD + GP
class PodGP:
    name = "pod_gp"; K_OPT = 4; N_OPT = 300
    @staticmethod
    def sample_config(rng, N, p, m, trial):
        if trial == 0: return dict(kernel="matern52", r=16)
        return dict(kernel=str(rng.choice(["matern52", "rbf"])), r=int(rng.choice([4, 8, 16, 32])))
    def fit(self, X, Y, cfg, seed):
        X = _x(X); self.pod = POD(Y, cfg["r"]); A = self.pod.encode(Y); r = self.pod.r; p = X.shape[1]
        rs = np.random.default_rng(seed); sub = rs.permutation(len(X))[: self.N_OPT]
        self.gps = []
        mk = lambda: C(1.0, (1e-3, 1e3)) * (Matern(np.ones(p), (1e-2, 1e3), nu=2.5) if cfg["kernel"] == "matern52" else RBF(np.ones(p), (1e-2, 1e3))) + WhiteKernel(1e-6, (1e-10, 1e-1))
        last = None
        for j in range(min(self.K_OPT, r)):
            g = GPR(mk(), normalize_y=True, n_restarts_optimizer=0, random_state=seed).fit(X[sub], A[sub, j])
            last = g.kernel_; gf = GPR(last, optimizer=None, normalize_y=True).fit(X, A[:, j]); self.gps.append(([j], gf))
        if r > self.K_OPT:
            gf = GPR(last, optimizer=None, normalize_y=True).fit(X, A[:, self.K_OPT:]); self.gps.append((list(range(self.K_OPT, r)), gf))
        return self
    def predict(self, X):
        X = _x(X); A = np.zeros((len(X), self.pod.r))
        for idx, g in self.gps: A[:, idx] = g.predict(X).reshape(len(X), -1)
        return self.pod.decode(A)


# ----------------------------------------------------------------------------- POD + polynomial ridge
class PodPoly:
    name = "pod_poly"
    @staticmethod
    def sample_config(rng, N, p, m, trial):
        if trial == 0: return dict(degree=3, alpha=1e-6, r=16)
        return dict(degree=int(rng.integers(1, 7)), alpha=_logu(rng, 1e-10, 1e-1), r=int(rng.choice([4, 8, 16, 32])))
    def fit(self, X, Y, cfg, seed):
        X = _x(X); p = X.shape[1]; deg = cfg["degree"]
        from math import comb
        while comb(p + deg, deg) > 5000 and deg > 1: deg -= 1       # cap feature count (documented)
        self.poly = PolynomialFeatures(deg, include_bias=False); F = self.poly.fit_transform(X)
        self.sc = StandardScaler().fit(F); F = self.sc.transform(F)
        self.pod = POD(Y, cfg["r"]); self.reg = Ridge(alpha=cfg["alpha"] * len(X), solver="auto").fit(F, self.pod.encode(Y))
        return self
    def predict(self, X): return self.pod.decode(self.reg.predict(self.sc.transform(self.poly.transform(_x(X)))))


# ----------------------------------------------------------------------------- neural nets
def _mlp(din, dout, width, depth, act):
    A = dict(tanh=torch.nn.Tanh, silu=torch.nn.SiLU)[act]; L = []; d = din
    for _ in range(depth): L += [torch.nn.Linear(d, width), A()]; d = width
    L.append(torch.nn.Linear(d, dout)); return torch.nn.Sequential(*L)


def _train(net, X, T, cfg, seed, epochs=NN_EPOCHS):
    torch.manual_seed(seed)
    opt = torch.optim.Adam(net.parameters(), lr=cfg["lr"], weight_decay=cfg["wd"])
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, epochs)
    n = len(X); bs = n if n <= 512 else 512; g = torch.Generator().manual_seed(seed)
    for _ in range(epochs):
        perm = torch.randperm(n, generator=g)
        for i in range(0, n, bs):
            b = perm[i:i + bs]; opt.zero_grad(); loss = ((net(X[b]) - T[b]) ** 2).mean(); loss.backward(); opt.step()
        sched.step()
    return net


def _nn_cfg(rng, trial, extra=None):
    if trial == 0: c = dict(width=128, depth=3, act="silu", lr=3e-3, wd=1e-6)
    else: c = dict(width=int(rng.choice([64, 128, 256])), depth=int(rng.choice([2, 3, 4])), act=str(rng.choice(["tanh", "silu"])), lr=_logu(rng, 1e-3, 1e-2), wd=_logu(rng, 1e-8, 1e-4))
    return c


class PodMLP:
    name = "pod_mlp"
    @staticmethod
    def sample_config(rng, N, p, m, trial):
        c = _nn_cfg(rng, trial); c["r"] = 16 if trial == 0 else int(rng.choice([4, 8, 16, 32])); return c
    def fit(self, X, Y, cfg, seed):
        self.pod = POD(Y, cfg["r"]); A = self.pod.encode(Y); self.s = float(np.sqrt((self.pod.S[0] ** 2) / len(Y)))
        Xt = torch.tensor(_x(X), dtype=torch.float32); T = torch.tensor(A / self.s, dtype=torch.float32)
        torch.manual_seed(seed); self.net = _mlp(X.shape[1], self.pod.r, cfg["width"], cfg["depth"], cfg["act"])
        _train(self.net, Xt, T, cfg, seed); return self
    def predict(self, X):
        with torch.no_grad(): A = self.net(torch.tensor(_x(X), dtype=torch.float32)).numpy().astype(np.float64) * self.s
        return self.pod.decode(A)


class MLPDirect:
    name = "mlp_direct"
    @staticmethod
    def sample_config(rng, N, p, m, trial): return _nn_cfg(rng, trial)
    def fit(self, X, Y, cfg, seed):
        self.mean = Y.mean(0); self.s = float((Y - self.mean).std() + 1e-12)
        Xt = torch.tensor(_x(X), dtype=torch.float32); T = torch.tensor((Y - self.mean) / self.s, dtype=torch.float32)
        torch.manual_seed(seed); self.net = _mlp(X.shape[1], Y.shape[1], cfg["width"], cfg["depth"], cfg["act"])
        _train(self.net, Xt, T, cfg, seed); return self
    def predict(self, X):
        with torch.no_grad(): return self.net(torch.tensor(_x(X), dtype=torch.float32)).numpy().astype(np.float64) * self.s + self.mean


class Bottleneck:
    name = "bottleneck"
    @staticmethod
    def sample_config(rng, N, p, m, trial):
        c = _nn_cfg(rng, trial); c["k"] = 8 if trial == 0 else int(rng.choice([2, 4, 8, 16])); return c
    def fit(self, X, Y, cfg, seed):
        self.mean = Y.mean(0); self.s = float((Y - self.mean).std() + 1e-12)
        Xt = torch.tensor(_x(X), dtype=torch.float32); T = torch.tensor((Y - self.mean) / self.s, dtype=torch.float32)
        torch.manual_seed(seed); w, d = cfg["width"], max(1, cfg["depth"] - 1)
        self.net = torch.nn.Sequential(_mlp(X.shape[1], cfg["k"], w, d, cfg["act"]), _mlp(cfg["k"], Y.shape[1], w, d, cfg["act"]))
        _train(self.net, Xt, T, cfg, seed); return self
    def predict(self, X):
        with torch.no_grad(): return self.net(torch.tensor(_x(X), dtype=torch.float32)).numpy().astype(np.float64) * self.s + self.mean


REGISTRY = dict(pod_gp=PodGP, pod_poly=PodPoly, pod_mlp=PodMLP, mlp_direct=MLPDirect, bottleneck=Bottleneck)


def rel_l2(U, Uh): return np.linalg.norm(U - Uh, axis=1) / np.linalg.norm(U, axis=1)
