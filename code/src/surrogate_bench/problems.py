"""Parametric PDE problem suite.

Every problem maps mu in R^p (nominal domain [0,1]^p; extrapolation uses mu outside it) to a
solution field sampled on a fixed output grid (m <= 256 values). All solvers are written with
numpy/scipy only. Physical parameter ranges are affine in mu so that mu in [-0.25, 1.25]^p stays valid.

Families (each with two difficulty levels -> 16 instances) + one DEV problem used only for debugging.
"""
from __future__ import annotations
import numpy as np, scipy.sparse as sp, scipy.sparse.linalg as spla
from dataclasses import dataclass
from typing import Callable
from scipy.linalg import solve_banded


def _aff(mu, lo, hi):
    return lo + (hi - lo) * mu


# ------------------------------------------------------------------ 2D helpers (FOM grid n x n interior nodes)
def _lap2d(n):
    h = 1.0 / (n + 1)
    T = sp.diags([-1.0, 2.0, -1.0], [-1, 0, 1], shape=(n, n)) / h**2
    I = sp.identity(n)
    return (sp.kron(I, T) + sp.kron(T, I)).tocsc()


def _grid2d(n):
    x = np.arange(1, n + 1) / (n + 1)
    X, Y = np.meshgrid(x, x, indexing="ij")
    return X, Y


def _sub2d(u, n, raw=False):   # n=32 interior nodes -> every other node, 16x16 output (raw: full field, for tests)
    return u.reshape(n, n) if raw else u.reshape(n, n)[1::2, 1::2].ravel()


# ------------------------------------------------------------------ F1 Darcy
def make_darcy(p, sigma, n=32, raw=False):
    X, Y = _grid2d(n); h = 1.0 / (n + 1)
    modes = sorted([(a, b) for a in range(0, 6) for b in range(0, 6) if a + b > 0], key=lambda t: (t[0] ** 2 + t[1] ** 2, t))[:p]
    phis = np.array([np.cos(np.pi * a * X) * np.cos(np.pi * b * Y) * 2.0 / (1 + a * a + b * b) ** 0.75 for a, b in modes])

    def solve(mu):
        la = sigma * np.tensordot(2 * np.asarray(mu) - 1, phis, axes=1)
        a = np.exp(la)
        ap = np.pad(a, 1, mode="edge")   # boundary coefficient = nearest interior value
        ae, aw = 2 * ap[2:, 1:-1] * a / (ap[2:, 1:-1] + a), 2 * ap[:-2, 1:-1] * a / (ap[:-2, 1:-1] + a)
        an, as_ = 2 * ap[1:-1, 2:] * a / (ap[1:-1, 2:] + a), 2 * ap[1:-1, :-2] * a / (ap[1:-1, :-2] + a)
        idx = np.arange(n * n).reshape(n, n)
        diag = (ae + aw + an + as_).ravel() / h**2
        data, ri, ci = [diag], [idx.ravel()], [idx.ravel()]
        data += [-ae[:-1, :].ravel() / h**2]; ri += [idx[:-1, :].ravel()]; ci += [idx[1:, :].ravel()]
        data += [-aw[1:, :].ravel() / h**2]; ri += [idx[1:, :].ravel()]; ci += [idx[:-1, :].ravel()]
        data += [-an[:, :-1].ravel() / h**2]; ri += [idx[:, :-1].ravel()]; ci += [idx[:, 1:].ravel()]
        data += [-as_[:, 1:].ravel() / h**2]; ri += [idx[:, 1:].ravel()]; ci += [idx[:, :-1].ravel()]
        A = sp.csc_matrix((np.concatenate(data), (np.concatenate(ri), np.concatenate(ci))), shape=(n * n, n * n))
        u = spla.spsolve(A, np.ones(n * n))
        return _sub2d(u, n, raw)
    return solve


# ------------------------------------------------------------------ F2 steady advection-diffusion (upwind)
def make_advdiff(eps_lo, eps_hi, n=32, raw=False):
    X, Y = _grid2d(n); h = 1.0 / (n + 1)
    L = _lap2d(n)
    Dx = sp.kron(sp.diags([-1.0, 1.0], [-1, 0], shape=(n, n)) / h, sp.identity(n)).tocsc()   # backward diff (b>0)
    Dy = sp.kron(sp.identity(n), sp.diags([-1.0, 1.0], [-1, 0], shape=(n, n)) / h).tocsc()

    def solve(mu):
        theta = _aff(mu[0], 0.1, np.pi / 2 - 0.1)
        eps = 10 ** _aff(mu[1], np.log10(eps_lo), np.log10(eps_hi))
        xs, ys = _aff(mu[2], 0.25, 0.75), _aff(mu[3], 0.25, 0.75)
        f = np.exp(-((X - xs) ** 2 + (Y - ys) ** 2) / (2 * 0.1**2)).ravel()
        A = (eps * L + np.cos(theta) * Dx + np.sin(theta) * Dy).tocsc()
        return _sub2d(spla.spsolve(A, f), n, raw)
    return solve


# ------------------------------------------------------------------ F3 transport (periodic, 4th-order FD + RK4)
def _periodic_gauss(x, x0, w):
    return sum(np.exp(-0.5 * ((x - x0 - k) / w) ** 2) for k in (-1, 0, 1))


def make_transport(w_lo, w_hi, N=512):
    x = np.arange(N) / N; h = 1.0 / N

    def ddx(u):
        return (8 * (np.roll(u, -1) - np.roll(u, 1)) - (np.roll(u, -2) - np.roll(u, 2))) / (12 * h)

    def solve(mu):
        c = _aff(mu[0], 0.2, 0.6); x1 = _aff(mu[1], 0.2, 0.5); w = _aff(mu[2], w_lo, w_hi); a2 = _aff(mu[3], 0.3, 1.0)
        u = _periodic_gauss(x, x1, w) + a2 * _periodic_gauss(x, x1 + 0.25, w)
        T = 1.0; nt = int(np.ceil(T * c / (0.5 * h))); dt = T / nt
        for _ in range(nt):
            k1 = -c * ddx(u); k2 = -c * ddx(u + 0.5 * dt * k1); k3 = -c * ddx(u + 0.5 * dt * k2); k4 = -c * ddx(u + dt * k3)
            u = u + dt / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
        return u[::4].copy()
    return solve


# ------------------------------------------------------------------ F4 viscous Burgers (pseudo-spectral IFRK4)
def make_burgers(nu_lo, nu_hi, N=512, T=0.5, dt=5e-4):
    x = np.arange(N) / N
    k = np.fft.rfftfreq(N, 1.0 / N) * 2 * np.pi
    dealias = (np.abs(np.fft.rfftfreq(N, 1.0 / N)) < N / 3).astype(float)

    def solve(mu):
        a = _aff(mu[0], 0.6, 1.0); phi = _aff(mu[1], 0.0, 0.5); b = _aff(mu[2], 0.0, 0.3)
        nu = 10 ** _aff(mu[3], np.log10(nu_lo), np.log10(nu_hi))
        u = a * np.sin(2 * np.pi * (x + phi)) + b * np.sin(4 * np.pi * x)
        uh = np.fft.rfft(u)
        E = np.exp(-nu * k**2 * dt / 2); E2 = E * E
        def Nl(vh):
            v = np.fft.irfft(vh * dealias, N)
            return -0.5j * k * np.fft.rfft(v * v)
        for _ in range(int(round(T / dt))):
            n1 = Nl(uh); n2 = Nl(E * (uh + 0.5 * dt * n1)); n3 = Nl(E * uh + 0.5 * dt * n2); n4 = Nl(E2 * uh + dt * E * n3)
            uh = E2 * uh + dt / 6 * (E2 * n1 + 2 * E * (n2 + n3) + n4)
        return np.fft.irfft(uh, N)[::4].copy()
    return solve


# ------------------------------------------------------------------ F5 Fisher-KPP front (Neumann, Strang splitting)
def make_fisher(T, N=256, dt=1e-3):
    x = (np.arange(N) + 0.5) / N; h = 1.0 / N

    def solve(mu):
        x0 = _aff(mu[0], 0.1, 0.3); r = _aff(mu[1], 5.0, 15.0); D = _aff(mu[2], 1e-3, 4e-3); delta = _aff(mu[3], 0.02, 0.05)
        u = 0.5 * (1 - np.tanh((x - x0) / delta))
        lam = D * dt / (2 * h**2)               # Crank-Nicolson half-system with Neumann ends (full step diffusion)
        ab = np.zeros((3, N)); ab[0, 1:] = -lam; ab[1, :] = 1 + 2 * lam; ab[2, :-1] = -lam
        ab[1, 0] = 1 + lam; ab[1, -1] = 1 + lam
        def react(u, tau):                       # exact logistic step
            e = np.exp(r * tau); return u * e / (1 - u + u * e)
        for _ in range(int(round(T / dt))):
            u = react(u, dt / 2)
            rhs = u.copy(); rhs[1:-1] += lam * (u[:-2] - 2 * u[1:-1] + u[2:]); rhs[0] += lam * (u[1] - u[0]); rhs[-1] += lam * (u[-2] - u[-1])
            u = solve_banded((1, 1), ab, rhs)
            u = react(u, dt / 2)
        return u[::2].copy()
    return solve


# ------------------------------------------------------------------ F6 2-D heat equation, moving Gaussian source
def make_heat2d(alpha, w_lo, w_hi, n=32, nt=40, T=1.0, raw=False):
    X, Y = _grid2d(n); L = _lap2d(n); dt = T / nt
    lu = spla.splu((sp.identity(n * n) + dt * alpha * L).tocsc())

    def solve(mu):
        x0, y0 = _aff(mu[0], 0.25, 0.75), _aff(mu[1], 0.25, 0.75); w = _aff(mu[2], w_lo, w_hi); A = _aff(mu[3], 0.5, 1.5)
        q = (A * np.exp(-((X - x0) ** 2 + (Y - y0) ** 2) / (2 * w**2))).ravel()
        u = np.zeros(n * n)
        for _ in range(nt):
            u = lu.solve(u + dt * q)
        return _sub2d(u, n, raw)
    return solve


# ------------------------------------------------------------------ F7 Bratu-type nonlinear elliptic (Newton)
def make_bratu(lam_lo, lam_hi, n=32, raw=False):
    X, Y = _grid2d(n); L = _lap2d(n)

    def solve(mu):
        lam = _aff(mu[0], lam_lo, lam_hi); k1, k2 = _aff(mu[1], -0.25, 0.25), _aff(mu[2], -0.25, 0.25)
        s = (1 + k1 * np.cos(np.pi * X) + k2 * np.cos(np.pi * Y)).ravel()
        u = np.zeros(n * n)
        for _ in range(50):
            F = L @ u - lam * s * np.exp(u)
            if np.linalg.norm(F, np.inf) < 1e-9 * (1 + np.linalg.norm(u, np.inf)): break
            J = (L - sp.diags(lam * s * np.exp(u))).tocsc()
            u = u - spla.spsolve(J, F)
        else:
            raise RuntimeError("Newton failed")
        return _sub2d(u, n, raw)
    return solve


# ------------------------------------------------------------------ F8 1-D wave equation (leapfrog)
def make_wave(w_lo, w_hi, N=512, T=0.5):
    x = np.arange(N) / N; h = 1.0 / N

    def solve(mu):
        c = _aff(mu[0], 0.4, 1.0); x0 = _aff(mu[1], 0.3, 0.5); w = _aff(mu[2], w_lo, w_hi); a2 = _aff(mu[3], 0.3, 1.0)
        g = _periodic_gauss(x, x0, w) + a2 * _periodic_gauss(x, x0 + 0.3, w)
        nt = int(np.ceil(T * c / (0.5 * h))); dt = T / nt; r2 = (c * dt / h) ** 2
        lap = lambda v: np.roll(v, -1) - 2 * v + np.roll(v, 1)
        up = g.copy(); u = g + 0.5 * r2 * lap(g)       # u_t(0)=0 start
        for _ in range(nt - 1):
            up, u = u, 2 * u - up + r2 * lap(u)
        return u[::4].copy()
    return solve


# ------------------------------------------------------------------ DEV problem (never part of evaluation)
def make_dev_heat1d(N=128):
    x = np.arange(N) / N
    def solve(mu):
        kappa = 10 ** _aff(mu[0], -3, -2)
        u = sum((2 * mu[j] - 1) / j * np.cos(2 * np.pi * j * x) for j in (1, 2, 3))
        uh = np.fft.rfft(u); k = np.fft.rfftfreq(N, 1.0 / N) * 2 * np.pi
        return np.fft.irfft(uh * np.exp(-kappa * k**2 * 0.5), N)
    return solve


@dataclass(frozen=True)
class Problem:
    name: str
    family: str
    level: int
    p: int
    m: int
    solve: Callable
    description: str


def build_suite() -> dict[str, Problem]:
    S = {}
    def add(fam, lvl, p, m, fn, desc): S[f"{fam}_L{lvl}"] = Problem(f"{fam}_L{lvl}", fam, lvl, p, m, fn, desc)
    add("darcy", 1, 4, 256, make_darcy(4, 1.0), "diffusion, 4 params, sigma=1.0")
    add("darcy", 2, 10, 256, make_darcy(10, 2.0), "diffusion, 10 params, sigma=2.0")
    add("advdiff", 1, 4, 256, make_advdiff(0.05, 0.2), "adv-diff, eps in [0.05,0.2]")
    add("advdiff", 2, 4, 256, make_advdiff(0.005, 0.02), "adv-diff, eps in [0.005,0.02] (layers)")
    add("transport", 1, 4, 128, make_transport(0.08, 0.12), "periodic transport, wide pulses")
    add("transport", 2, 4, 128, make_transport(0.03, 0.05), "periodic transport, narrow pulses")
    add("burgers", 1, 4, 128, make_burgers(0.05, 0.1), "Burgers nu in [0.05,0.1]")
    add("burgers", 2, 4, 128, make_burgers(0.005, 0.01), "Burgers nu in [0.005,0.01] (shocks)")
    add("fisher", 1, 4, 128, make_fisher(0.3), "Fisher-KPP T=0.3 (small front travel)")
    add("fisher", 2, 4, 128, make_fisher(1.2), "Fisher-KPP T=1.2 (large front travel)")
    add("heat2d", 1, 4, 256, make_heat2d(0.05, 0.15, 0.25), "heat eq, broad source")
    add("heat2d", 2, 4, 256, make_heat2d(0.005, 0.04, 0.08), "heat eq, narrow source, small diffusivity")
    add("bratu", 1, 3, 256, make_bratu(0.2, 1.2), "Bratu lambda in [0.2,1.2]")
    add("bratu", 2, 3, 256, make_bratu(1.0, 3.5), "Bratu lambda in [1.0,3.5] (strong nonlinearity)")
    add("wave", 1, 4, 128, make_wave(0.06, 0.10), "wave, wide pulses")
    add("wave", 2, 4, 128, make_wave(0.02, 0.04), "wave, narrow pulses")
    return S


def build_dev() -> Problem:
    return Problem("dev_heat1d", "dev", 0, 4, 128, make_dev_heat1d(), "DEV ONLY")
