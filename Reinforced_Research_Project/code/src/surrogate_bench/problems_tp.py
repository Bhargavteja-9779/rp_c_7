"""Third-party-solver test problems (Stage 6): finite-element models built with the independent scikit-fem library (not our own discretisations).
All parameters mu are in [0,1]^p; the output is the field sampled at fixed probe points (so m is small and identical for all samples).
Four families x two levels: lshape (linear elasticity on an L-shaped plate), heatcomp (composite conduction), heatmove (transient heat, moving source),
convdiff (steady convection-diffusion)."""
from __future__ import annotations
import numpy as np, scipy.sparse as sp, scipy.sparse.linalg as spla


def _aff(x, lo, hi): return lo + (hi - lo) * x
def _logu(x, lo, hi): return lo * (hi / lo) ** x


# ------------------------------------------------------------------------------------------------ L-shaped plate, plane-stress elasticity
def make_lshape(n_blocks, c_lo, c_hi, refine=3):
    from skfem import MeshTri, ElementTriP1, ElementVector, Basis, FacetBasis, BilinearForm, LinearForm, asm
    from skfem.helpers import sym_grad, trace, ddot
    mesh = MeshTri.init_lshaped().refined(refine); el = ElementVector(ElementTriP1()); basis = Basis(mesh, el)
    nu = 0.3; mu_l = 1 / (2 * (1 + nu)); lam = nu / (1 - nu**2)

    @BilinearForm
    def a(u, v, w): return w["ind"] * (2 * mu_l * ddot(sym_grad(u), sym_grad(v)) + lam * trace(sym_grad(u)) * trace(sym_grad(v)))
    cent = mesh.p[:, mesh.t].mean(axis=1); nq = basis.X.shape[1]
    if n_blocks == 3: groups = [(cent[0] < 0) & (cent[1] > 0), (cent[0] < 0) & (cent[1] < 0), (cent[0] > 0) & (cent[1] < 0)]
    else:   # each arm split in two halves along its length
        groups = [(cent[0] < 0) & (cent[1] > 0.5), (cent[0] < 0) & (cent[1] > 0) & (cent[1] <= 0.5), (cent[0] < 0) & (cent[1] < 0), (cent[0] > 0) & (cent[1] < 0) & (cent[0] <= 0.5), (cent[0] > 0.5) & (cent[1] < 0) & (cent[1] > -0.5), (cent[0] > 0.5) & (cent[1] <= -0.5)]
        groups = groups[:n_blocks]
    assert sum(g.sum() for g in groups) == mesh.t.shape[1]
    Ks = [asm(a, basis, ind=np.repeat(g.astype(float)[:, None], nq, axis=1)) for g in groups]
    fixed = basis.get_dofs(lambda x: np.isclose(x[1], 1.0) & (x[0] <= 0)).all(); I = basis.complement_dofs(fixed)
    fb = FacetBasis(mesh, el, facets=mesh.facets_satisfying(lambda x: np.isclose(x[0], 1.0)))

    @LinearForm
    def tx(v, w): return v.value[0]

    @LinearForm
    def ty(v, w): return v.value[1]
    fx, fy = asm(tx, fb), asm(ty, fb)
    probe_mesh = MeshTri.init_lshaped().refined(2); pidx = np.array([np.argmin(np.sum((mesh.p - q[:, None]) ** 2, axis=0)) for q in probe_mesh.p.T])
    dof_idx = np.concatenate([basis.nodal_dofs[0][pidx], basis.nodal_dofs[1][pidx]])

    def solve(mu):
        E = [_logu(mu[i], c_lo, c_hi) for i in range(n_blocks)]; th = _aff(mu[n_blocks], 0.0, np.pi)
        K = sum(e * k for e, k in zip(E, Ks)); f = np.cos(th) * fx + np.sin(th) * fy
        u = np.zeros(basis.N); u[I] = spla.spsolve(K[I][:, I].tocsc(), f[I]); return u[dof_idx]
    solve.m = len(dof_idx); return solve


# ------------------------------------------------------------------------------------------------ composite steady conduction
def make_heatcomp(nb, c_lo, c_hi, refine=4, npr=16):
    from skfem import MeshTri, ElementTriP1, Basis, BilinearForm, LinearForm, asm
    from skfem.helpers import dot, grad
    mesh = MeshTri.init_sqsymmetric().refined(refine); basis = Basis(mesh, ElementTriP1())

    @BilinearForm
    def a(u, v, w): return w["ind"] * dot(grad(u), grad(v))

    @LinearForm
    def l(v, w): return v.value
    cent = mesh.p[:, mesh.t].mean(axis=1); nq = basis.X.shape[1]
    bi = np.minimum((cent[0] * nb).astype(int), nb - 1); bj = np.minimum((cent[1] * nb).astype(int), nb - 1)
    Ks = [asm(a, basis, ind=np.repeat(((bi == i) & (bj == j)).astype(float)[:, None], nq, axis=1)) for i in range(nb) for j in range(nb)]
    f = asm(l, basis); D = basis.get_dofs().all(); I = basis.complement_dofs(D)
    g = (np.arange(npr) + 0.5) / npr; P = basis.probes(np.array([[x, y] for y in g for x in g]).T)

    def solve(mu):
        k = [_logu(mu[i], c_lo, c_hi) for i in range(nb * nb)]; K = sum(e * K_ for e, K_ in zip(k, Ks))
        u = np.zeros(basis.N); u[I] = spla.spsolve(K[I][:, I].tocsc(), f[I]); return P @ u
    solve.m = npr * npr; return solve


# ------------------------------------------------------------------------------------------------ transient heat, moving Gaussian source
def make_heatmove(extra, kappa, w_lo, w_hi, refine=4, nsteps=30, T=0.6, npr=8):
    from skfem import MeshTri, ElementTriP1, Basis, BilinearForm, asm
    from skfem.helpers import dot, grad
    mesh = MeshTri.init_sqsymmetric().refined(refine); basis = Basis(mesh, ElementTriP1())

    @BilinearForm
    def stiff(u, v, w): return dot(grad(u), grad(v))

    @BilinearForm
    def mass(u, v, w): return u * v
    K, Mm = asm(stiff, basis), asm(mass, basis); D = basis.get_dofs().all(); I = basis.complement_dofs(D); dt = T / nsteps
    xy = mesh.p; g = (np.arange(npr) + 0.5) / npr; P = basis.probes(np.array([[x, y] for y in g for x in g]).T)
    save = {int(round(nsteps * f)) for f in (1 / 3, 2 / 3, 1.0)}
    cache = {}

    def solve(mu):
        alpha = _aff(mu[0], 0.0, np.pi / 2); v = _aff(mu[1], 0.5, 1.2); w = _aff(mu[2], w_lo, w_hi)
        amp = 40.0 if not extra else _aff(mu[3], 20.0, 60.0); kap = kappa if not extra else _logu(mu[4], kappa / 2, kappa * 2)
        key = round(kap, 12)
        if key not in cache:
            if len(cache) > 20: cache.clear()
            cache[key] = spla.splu((Mm[I][:, I] / dt + kap * K[I][:, I]).tocsc())
        lu = cache[key]; u = np.zeros(basis.N); out = []
        for s in range(1, nsteps + 1):
            t = s * dt; c = np.array([0.2, 0.2]) + v * t * np.array([np.cos(alpha), np.sin(alpha)]) * 0.9
            src = amp * np.exp(-((xy[0] - c[0]) ** 2 + (xy[1] - c[1]) ** 2) / (2 * w**2))
            rhs = (Mm @ (u / dt + src))[I]; u[I] = lu.solve(rhs)
            if s in save: out.append(P @ u)
        return np.concatenate(out)
    solve.m = 3 * npr * npr; return solve


# ------------------------------------------------------------------------------------------------ steady convection-diffusion
def make_convdiff(extra, e_lo, e_hi, refine=5, npr=16):
    from skfem import MeshTri, ElementTriP1, Basis, BilinearForm, LinearForm, asm
    from skfem.helpers import dot, grad
    mesh = MeshTri.init_sqsymmetric().refined(refine); basis = Basis(mesh, ElementTriP1())

    @BilinearForm
    def diff(u, v, w): return dot(grad(u), grad(v))

    @BilinearForm
    def cx(u, v, w): return grad(u)[0] * v

    @BilinearForm
    def cy(u, v, w): return grad(u)[1] * v

    @BilinearForm
    def mass(u, v, w): return u * v
    Kd, Cx, Cy, Mm = asm(diff, basis), asm(cx, basis), asm(cy, basis), asm(mass, basis)
    D = basis.get_dofs().all(); I = basis.complement_dofs(D); xy = mesh.p; g = (np.arange(npr) + 0.5) / npr
    P = basis.probes(np.array([[x, y] for y in g for x in g]).T)

    def solve(mu):
        eps = _logu(mu[0], e_lo, e_hi); th = _aff(mu[1], 0.0, np.pi / 2); sx = _aff(mu[2], 0.15, 0.45)
        sw = 0.08 if not extra else _aff(mu[3], 0.05, 0.12)
        s = 30.0 * np.exp(-((xy[0] - sx) ** 2 + (xy[1] - sx) ** 2) / (2 * sw**2)); A = (eps * Kd + np.cos(th) * Cx + np.sin(th) * Cy)
        u = np.zeros(basis.N); u[I] = spla.spsolve(A[I][:, I].tocsc(), (Mm @ s)[I]); return P @ u
    solve.m = npr * npr; return solve


def build_suite_tp():
    from .problems import Problem
    S = {}
    def add(fam, lvl, p, fn, desc):
        S[f"{fam}_L{lvl}"] = Problem(f"{fam}_L{lvl}", fam, lvl, p, fn.m, fn, desc)
    add("lshape", 1, 4, make_lshape(3, 1.0, 10.0), "scikit-fem plane-stress L-plate, 3 stiffness regions + load angle")
    add("lshape", 2, 7, make_lshape(6, 0.2, 20.0), "scikit-fem plane-stress L-plate, 6 stiffness regions + load angle, high contrast")
    add("heatcomp", 1, 4, make_heatcomp(2, 0.2, 5.0), "scikit-fem composite conduction 2x2 blocks")
    add("heatcomp", 2, 9, make_heatcomp(3, 0.05, 20.0), "scikit-fem composite conduction 3x3 blocks, high contrast")
    add("heatmove", 1, 3, make_heatmove(False, 0.02, 0.08, 0.16), "scikit-fem transient heat, moving source (angle, speed, width)")
    add("heatmove", 2, 5, make_heatmove(True, 0.01, 0.05, 0.10), "scikit-fem transient heat, moving narrow source, + amplitude, diffusivity")
    add("convdiff", 1, 3, make_convdiff(False, 0.03, 0.1), "scikit-fem convection-diffusion (eps, direction, source position)")
    add("convdiff", 2, 4, make_convdiff(True, 0.012, 0.04), "scikit-fem convection-diffusion, thin layers, + source width")
    return S
