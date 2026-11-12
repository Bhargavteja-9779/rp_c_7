"""Stage 8: a genuinely expensive problem solved with scikit-fem: linear elasticity of a three-dimensional cantilever with three stiffness bands (tetrahedral mesh, tens of seconds per run).
mu in [0,1]^5: three band moduli (log-uniform 1..10), Poisson ratio in [0.2, 0.4], tip-load angle in [0, pi] (in the y-z plane). Output: displacement (3 components) at a fixed grid of interior points."""
from __future__ import annotations
import numpy as np, scipy.sparse.linalg as spla


def _aff(x, lo, hi): return lo + (hi - lo) * x
def _logu(x, lo, hi): return lo * (hi / lo) ** x


def make_bracket3d(nx=40, ny=16, nz=8, nbands=3):
    from skfem import MeshTet, ElementTetP1, ElementVector, Basis, FacetBasis, BilinearForm, LinearForm, asm
    from skfem.helpers import sym_grad, trace, ddot
    Lx, Ly, Lz = 4.0, 1.0, 0.5
    mesh = MeshTet.init_tensor(np.linspace(0, Lx, nx + 1), np.linspace(0, Ly, ny + 1), np.linspace(0, Lz, nz + 1)); el = ElementVector(ElementTetP1()); basis = Basis(mesh, el)
    @BilinearForm
    def amu(u, v, w): return w["ind"] * 2 * ddot(sym_grad(u), sym_grad(v))
    @BilinearForm
    def alam(u, v, w): return w["ind"] * trace(sym_grad(u)) * trace(sym_grad(v))
    cent = mesh.p[:, mesh.t].mean(axis=1); band = np.minimum((cent[0] / Lx * nbands).astype(int), nbands - 1); nq = basis.X.shape[1]
    Km, Kl = [], []
    for b in range(nbands):
        ind = np.repeat((band == b).astype(float)[:, None], nq, axis=1); Km.append(asm(amu, basis, ind=ind)); Kl.append(asm(alam, basis, ind=ind))
    fixed = basis.get_dofs(lambda x: np.isclose(x[0], 0.0)).all(); I = basis.complement_dofs(fixed)
    fb = FacetBasis(mesh, el, facets=mesh.facets_satisfying(lambda x: np.isclose(x[0], Lx)))
    @LinearForm
    def ty(v, w): return v.value[1]
    @LinearForm
    def tz(v, w): return v.value[2]
    fy, fz = asm(ty, fb), asm(tz, fb)
    gx, gy, gz = (np.arange(6) + 0.5) / 6 * (Lx - 0.2) + 0.1, (np.arange(3) + 0.5) / 3 * Ly, (np.arange(2) + 0.5) / 2 * Lz
    pts = np.array([[x, y, z] for z in gz for y in gy for x in gx]).T; P = basis.probes(pts)

    def solve(mu):
        E = [_logu(mu[i], 1.0, 10.0) for i in range(nbands)]; nu = _aff(mu[nbands], 0.2, 0.4); th = _aff(mu[nbands + 1], 0.0, np.pi)
        mu_l = 1.0 / (2 * (1 + nu)); lam = nu / ((1 + nu) * (1 - 2 * nu)); K = sum(E[b] * (mu_l * Km[b] + lam * Kl[b]) for b in range(nbands)); f = np.cos(th) * fy + np.sin(th) * fz
        u = np.zeros(basis.N); u[I] = spla.spsolve(K[I][:, I].tocsc(), f[I]); return P @ u
    solve.m = 3 * pts.shape[1]; solve.mesh = mesh; return solve
