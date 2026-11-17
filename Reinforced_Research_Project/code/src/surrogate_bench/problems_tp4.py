"""Stage 10: frequency-response problems with damping (complex linear systems), solved with scikit-fem. Output = real and imaginary parts of the response at fixed points (m = 2 x points).
acoustic_cavity: Helmholtz equation in a cavity with impedance (Robin) walls, -lap u - k^2 u = f, du/dn = -i k beta u; inputs wave number, impedance, source position.
beam_frf: Euler-Bernoulli cantilever (Hermite elements) with Rayleigh damping and a tip mass, (K - w^2 M + i w C) u = f; inputs frequency, mass damping, tip mass, load position.
mu in [0,1]^p."""
from __future__ import annotations
import numpy as np, scipy.sparse as sp, scipy.sparse.linalg as spla


def _aff(x, lo, hi): return lo + (hi - lo) * x
def _logu(x, lo, hi): return lo * (hi / lo) ** x


def make_acoustic(shape, k_lo, k_hi, b_lo, b_hi, refine=5, npr=8):
    from skfem import MeshTri, ElementTriP1, Basis, FacetBasis, BilinearForm, asm
    from skfem.helpers import dot, grad
    mesh = (MeshTri.init_sqsymmetric() if shape == "square" else MeshTri.init_lshaped()).refined(refine); basis = Basis(mesh, ElementTriP1()); fb = FacetBasis(mesh, ElementTriP1())
    if shape != "square": mesh = mesh.scaled(0.5).translated((0.5, 0.5)); basis = Basis(mesh, ElementTriP1()); fb = FacetBasis(mesh, ElementTriP1())      # L-shape of side 1 inside the unit square: [0,1]^2 minus the upper-right quadrant
    @BilinearForm
    def stiff(u, v, w): return dot(grad(u), grad(v))
    @BilinearForm
    def mass(u, v, w): return u * v
    @BilinearForm
    def bmass(u, v, w): return u * v
    K, Mm, Bd = asm(stiff, basis), asm(mass, basis), asm(bmass, fb); xy = mesh.p
    g = (np.arange(npr) + 0.5) / npr; pts = np.array([[x, y] for y in g for x in g]); inside = np.array([mesh.p[0].min() - 1e-9 <= q[0] <= mesh.p[0].max() + 1e-9 and mesh.p[1].min() - 1e-9 <= q[1] <= mesh.p[1].max() + 1e-9 for q in pts])
    if shape != "square": inside &= ~((pts[:, 0] > 0.5 - 1e-9) & (pts[:, 1] > 0.5 - 1e-9))                  # drop probes in the removed quadrant
    pts = pts[inside]; P = basis.probes(pts.T)

    def full(mu):
        k = _aff(mu[0], k_lo, k_hi); beta = _aff(mu[1], b_lo, b_hi); sx = _aff(mu[2], 0.15, 0.45); sy = _aff(mu[3], 0.15, 0.45)
        s = np.exp(-((xy[0] - sx) ** 2 + (xy[1] - sy) ** 2) / (2 * 0.06**2)); A = (K - k**2 * Mm + 1j * k * beta * Bd).tocsc(); f = Mm @ s
        return spla.spsolve(A, f.astype(complex)), f, k, beta

    def solve(mu): u, *_ = full(mu); r = P @ u; return np.concatenate([r.real, r.imag])
    solve.full = full; solve.m = 2 * len(pts); solve.K, solve.M, solve.B = K, Mm, Bd; return solve


def make_beam_frf(w_lo, w_hi, dm_lo, dm_hi, nel=80, npts=40):
    from skfem import MeshLine, ElementLineHermite, Basis, BilinearForm, asm
    from skfem.helpers import dd
    mesh = MeshLine(np.linspace(0, 1, nel + 1)); basis = Basis(mesh, ElementLineHermite())
    @BilinearForm
    def stiff(u, v, w): return u.hess[0][0] * v.hess[0][0]
    @BilinearForm
    def mass(u, v, w): return u * v
    K, Mm = asm(stiff, basis), asm(mass, basis); fixed = basis.get_dofs(lambda x: np.isclose(x[0], 0.0)).all(); I = basis.complement_dofs(fixed)
    tip = basis.get_dofs(lambda x: np.isclose(x[0], 1.0)).nodal["u"]; tipdof = int(np.atleast_1d(tip)[0])
    xs = np.linspace(0.05, 1.0, npts); P = basis.probes(xs[None, :])
    def load(xf): return np.asarray(basis.probes(np.array([[xf]])).todense()).ravel()

    def full(mu):
        w = _aff(mu[0], w_lo, w_hi); dm = _logu(mu[1], dm_lo, dm_hi); mt = _aff(mu[2], 0.0, 0.5); xf = _aff(mu[3], 0.3, 1.0); Mt = Mm.tolil(); Mt[tipdof, tipdof] += mt; Mt = Mt.tocsr()
        Cd = dm * Mt + 2e-4 * K; A = (K - w**2 * Mt + 1j * w * Cd)[I][:, I].tocsc(); f = load(xf)[I]; u = np.zeros(basis.N, complex); u[I] = spla.spsolve(A, f.astype(complex)); return u, f, w, dm
    def solve(mu): u, *_ = full(mu); r = P @ u; return np.concatenate([r.real, r.imag])
    solve.full = full; solve.m = 2 * npts; solve.K, solve.M, solve.basis, solve.I, solve.tipdof, solve.load = K, Mm, basis, I, tipdof, load; return solve


def build_suite_frf():
    from .problems import Problem
    S = {}
    def add(fam, lvl, p, fn, desc): S[f"{fam}_L{lvl}"] = Problem(f"{fam}_L{lvl}", fam, lvl, p, fn.m, fn, desc)
    add("acoustic_cavity", 1, 4, make_acoustic("square", 2.6, 3.8, 0.01, 0.08), "scikit-fem damped Helmholtz (impedance walls) in a square cavity, the first resonance group in range, source position")
    add("acoustic_cavity", 2, 4, make_acoustic("lshape", 2.2, 4.4, 0.005, 0.04), "scikit-fem damped Helmholtz (light impedance) in an L-shaped cavity, a resonance in range, source position")
    add("beam_frf", 1, 4, make_beam_frf(2.0, 6.0, 0.03, 0.3), "scikit-fem cantilever frequency response (Hermite beam, Rayleigh damping, tip mass, load position), first resonance in range")
    add("beam_frf", 2, 4, make_beam_frf(2.0, 30.0, 0.01, 0.1), "scikit-fem cantilever frequency response, first two resonances in range, light damping")
    return S
