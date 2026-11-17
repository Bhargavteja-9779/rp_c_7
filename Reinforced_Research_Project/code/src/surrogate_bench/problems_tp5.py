"""Stage 11: two further frequency-response families with damping (complex linear systems), unseen when the pole-deflation method was designed.
mdk_chain: a chain of 20 masses and springs (fixed at one end, force at the free end), Rayleigh damping, an added mass and a spring stiffness as inputs; output = displacement of all masses (real and imaginary parts).
disc_acoustic: Helmholtz equation in a circular cavity with impedance wall, source position in polar coordinates; output = real and imaginary parts at 41 fixed points. mu in [0,1]^p."""
from __future__ import annotations
import numpy as np, scipy.sparse as sp, scipy.sparse.linalg as spla


def _aff(x, lo, hi): return lo + (hi - lo) * x
def _logu(x, lo, hi): return lo * (hi / lo) ** x


def make_mdk_chain(w_lo, w_hi, a_lo, a_hi, n=20):
    # K0: wall spring on mass 0 (stiffness 1) and springs between neighbours (stiffness 1); the free end is mass n-1
    K0 = np.zeros((n, n)); K0[0, 0] += 1.0
    for i in range(n - 1): K0[i, i] += 1.0; K0[i + 1, i + 1] += 1.0; K0[i, i + 1] -= 1.0; K0[i + 1, i] -= 1.0
    mid = n // 2 - 1; e = np.zeros((n, n)); e[mid, mid] += 1.0; e[mid + 1, mid + 1] += 1.0; e[mid, mid + 1] -= 1.0; e[mid + 1, mid] -= 1.0          # the spring between masses mid and mid+1
    f = np.zeros(n); f[-1] = 1.0

    def full(mu):
        w = max(_aff(mu[0], w_lo, w_hi), 0.02); al = _logu(mu[1], a_lo, a_hi); madd = max(_aff(mu[2], 0.0, 1.0), 0.0); km = _logu(mu[3], 0.3, 3.0)
        K = K0 + (km - 1.0) * e; M = np.eye(n); M[mid, mid] += madd; C = al * M; A = K - w**2 * M + 1j * w * C
        return np.linalg.solve(A, f.astype(complex)), f, w, al, M, K

    def solve(mu): u = full(mu)[0]; return np.concatenate([u.real, u.imag])
    solve.full = full; solve.m = 2 * n; solve.K0, solve.n = K0, n; return solve


def make_disc_acoustic(k_lo, k_hi, b_lo, b_hi, refine=5):
    from skfem import MeshTri, ElementTriP1, Basis, FacetBasis, BilinearForm, asm
    from skfem.helpers import dot, grad
    mesh = MeshTri.init_circle(refine); basis = Basis(mesh, ElementTriP1()); fb = FacetBasis(mesh, ElementTriP1())
    @BilinearForm
    def stiff(u, v, w): return dot(grad(u), grad(v))
    @BilinearForm
    def mass(u, v, w): return u * v
    K, Mm, Bd = asm(stiff, basis), asm(mass, basis), asm(mass, fb); xy = mesh.p
    rr = np.array([0.25, 0.5, 0.75, 0.9]); aa = 2 * np.pi * (np.arange(10) + 0.5) / 10; pts = np.vstack([np.array([[0.0], [0.0]]).T, np.array([[r * np.cos(a), r * np.sin(a)] for r in rr for a in aa])]); P = basis.probes(pts.T)

    def full(mu):
        k = _aff(mu[0], k_lo, k_hi); beta = max(_aff(mu[1], b_lo, b_hi), 0.0); r = min(max(_aff(mu[2], 0.2, 0.6), 0.0), 0.9); th = _aff(mu[3], 0.0, 2 * np.pi)
        sx, sy = r * np.cos(th), r * np.sin(th); s = np.exp(-((xy[0] - sx) ** 2 + (xy[1] - sy) ** 2) / (2 * 0.08**2)); A = (K - k**2 * Mm + 1j * k * beta * Bd).tocsc(); f = Mm @ s
        return spla.spsolve(A, f.astype(complex)), f, k, beta

    def solve(mu): u, *_ = full(mu); rr_ = P @ u; return np.concatenate([rr_.real, rr_.imag])
    solve.full = full; solve.m = 2 * pts.shape[0]; solve.K, solve.M, solve.B = K, Mm, Bd; return solve


def build_suite_frf2():
    from .problems import Problem
    S = {}
    def add(fam, lvl, p, fn, desc): S[f"{fam}_L{lvl}"] = Problem(f"{fam}_L{lvl}", fam, lvl, p, fn.m, fn, desc)
    add("mdk_chain", 1, 4, make_mdk_chain(0.05, 0.12, 0.002, 0.02), "mass-spring chain (20 masses), Rayleigh damping, added mass and spring stiffness, first resonance in range")
    add("mdk_chain", 2, 4, make_mdk_chain(0.05, 0.60, 0.001, 0.01), "mass-spring chain (20 masses), light damping, four resonances in range")
    add("disc_acoustic", 1, 4, make_disc_acoustic(1.4, 2.3, 0.01, 0.08), "scikit-fem damped Helmholtz in a circular cavity (impedance wall), first mode pair in range, polar source position")
    add("disc_acoustic", 2, 4, make_disc_acoustic(1.4, 4.2, 0.005, 0.04), "scikit-fem damped Helmholtz in a circular cavity, light impedance, three mode groups in range, polar source position")
    return S
