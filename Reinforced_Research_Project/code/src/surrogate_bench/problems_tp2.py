"""Stage 7: eight further problems solved with scikit-fem (four families x two levels) plus one seconds-per-run problem (lshape_fine). mu in [0,1]^p; output = field at fixed probe points.
Families: helmholtz (Helmholtz, source position, wave number; L2 near resonance), reacdiff_fe (nonlinear reaction-diffusion, Newton), disc_elast (plane-stress elasticity on a disc with angular stiffness sectors), advdiff_cell (advection-diffusion in a cellular flow)."""
from __future__ import annotations
import numpy as np, scipy.sparse.linalg as spla


def _aff(x, lo, hi): return lo + (hi - lo) * x
def _logu(x, lo, hi): return lo * (hi / lo) ** x


def _probes(basis, n):
    g = (np.arange(n) + 0.5) / n; return basis.probes(np.array([[x, y] for y in g for x in g]).T)


def make_helmholtz(k2_lo, k2_hi, extra, refine=5, npr=16):
    from skfem import MeshTri, ElementTriP1, Basis, BilinearForm, asm
    from skfem.helpers import dot, grad
    mesh = MeshTri.init_sqsymmetric().refined(refine); basis = Basis(mesh, ElementTriP1())

    @BilinearForm
    def stiff(u, v, w): return dot(grad(u), grad(v))

    @BilinearForm
    def mass(u, v, w): return u * v
    K, Mm = asm(stiff, basis), asm(mass, basis); D = basis.get_dofs().all(); I = basis.complement_dofs(D); xy = mesh.p; P = _probes(basis, npr)

    def solve(mu):
        k2 = _aff(mu[0], k2_lo, k2_hi); sx = _aff(mu[1], 0.2, 0.8); sy = _aff(mu[2], 0.2, 0.8); sw = 0.08 if not extra else _aff(mu[3], 0.05, 0.14)
        s = 30.0 * np.exp(-((xy[0] - sx) ** 2 + (xy[1] - sy) ** 2) / (2 * sw**2)); A = (K - k2 * Mm)[I][:, I].tocsc()
        u = np.zeros(basis.N); u[I] = spla.spsolve(A, (Mm @ s)[I]); return P @ u
    solve.m = npr * npr; return solve


def make_reacdiff_fe(blocks, r_lo, r_hi, refine=4, npr=16, newton=12):
    from skfem import MeshTri, ElementTriP1, Basis, BilinearForm, LinearForm, asm
    from skfem.helpers import dot, grad
    mesh = MeshTri.init_sqsymmetric().refined(refine); basis = Basis(mesh, ElementTriP1())
    cent = mesh.p[:, mesh.t].mean(axis=1); nq = basis.X.shape[1]
    @BilinearForm
    def stiff(u, v, w): return w["ind"] * dot(grad(u), grad(v))
    @BilinearForm
    def mass(u, v, w): return u * v
    nb = int(np.sqrt(blocks)); bi = np.minimum((cent[0] * nb).astype(int), nb - 1); bj = np.minimum((cent[1] * nb).astype(int), nb - 1)
    Ks = [asm(stiff, basis, ind=np.repeat(((bi == i) & (bj == j)).astype(float)[:, None], nq, axis=1)) for i in range(nb) for j in range(nb)]; Mm = asm(mass, basis)
    @BilinearForm
    def m3(u, v, w): return 3.0 * w["u"] ** 2 * u * v                       # Jacobian of u^3
    @LinearForm
    def c3(v, w): return w["u"] ** 3 * v
    D = basis.get_dofs().all(); I = basis.complement_dofs(D); xy = mesh.p; P = _probes(basis, npr)

    def solve(mu):
        Ds = [_logu(mu[i], 0.3, 3.0) for i in range(blocks)]; r = _logu(mu[blocks], r_lo, r_hi); amp = _aff(mu[blocks + 1], 20.0, 80.0)
        K = sum(d * k for d, k in zip(Ds, Ks)); s = amp * np.exp(-((xy[0] - 0.5) ** 2 + (xy[1] - 0.5) ** 2) / (2 * 0.2**2)); f = Mm @ s; u = np.zeros(basis.N)
        for _ in range(newton):
            uq = basis.interpolate(u); J = K + r * asm(m3, basis, u=uq); res = K @ u + r * asm(c3, basis, u=uq) - f
            du = np.zeros(basis.N); du[I] = spla.spsolve(J[I][:, I].tocsc(), -res[I]); u = u + du
            if np.linalg.norm(du) < 1e-10 * (1 + np.linalg.norm(u)): break
        return P @ u
    solve.m = npr * npr; return solve


def make_disc_elast(nsec, c_lo, c_hi, refine=5):
    from skfem import MeshTri, ElementTriP1, ElementVector, Basis, FacetBasis, BilinearForm, LinearForm, asm
    from skfem.helpers import sym_grad, trace, ddot
    mesh = MeshTri.init_circle(refine); el = ElementVector(ElementTriP1()); basis = Basis(mesh, el); nu = 0.3; mu_l = 1 / (2 * (1 + nu)); lam = nu / (1 - nu**2)
    @BilinearForm
    def a(u, v, w): return w["ind"] * (2 * mu_l * ddot(sym_grad(u), sym_grad(v)) + lam * trace(sym_grad(u)) * trace(sym_grad(v)))
    cent = mesh.p[:, mesh.t].mean(axis=1); ang = (np.arctan2(cent[1], cent[0]) + np.pi) / (2 * np.pi); sec = np.minimum((ang * nsec).astype(int), nsec - 1); nq = basis.X.shape[1]
    Ks = [asm(a, basis, ind=np.repeat((sec == k).astype(float)[:, None], nq, axis=1)) for k in range(nsec)]
    ang_f = lambda x: np.abs(np.arctan2(x[1], x[0]))      # polar angle of a facet midpoint; mesh-independent regions: clamp |angle-pi|<0.35 (left arc), load |angle|<0.35 (right arc)
    bf = mesh.boundary_facets(); fixed = basis.get_dofs(bf[ang_f(mesh.p[:, mesh.facets[:, bf]].mean(axis=1)) > np.pi - 0.35]).all(); I = basis.complement_dofs(fixed); fb = FacetBasis(mesh, el, facets=bf[ang_f(mesh.p[:, mesh.facets[:, bf]].mean(axis=1)) < 0.35])
    @LinearForm
    def tx(v, w): return v.value[0]
    @LinearForm
    def ty(v, w): return v.value[1]
    fx, fy = asm(tx, fb), asm(ty, fb); rr = np.array([0.25, 0.5, 0.75, 0.9]); aa = 2 * np.pi * (np.arange(10) + 0.5) / 10; pts = np.vstack([np.array([[0.0], [0.0]]).T, np.array([[r * np.cos(a), r * np.sin(a)] for r in rr for a in aa])]).T; Pr = basis.probes(pts)   # 41 fixed physical points, same on every mesh
    def solve(mu):
        E = [_logu(mu[i], c_lo, c_hi) for i in range(nsec)]; th = _aff(mu[nsec], -np.pi / 2, np.pi / 2); K = sum(e * k for e, k in zip(E, Ks)); f = np.cos(th) * fx + np.sin(th) * fy
        u = np.zeros(basis.N); u[I] = spla.spsolve(K[I][:, I].tocsc(), f[I]); return Pr @ u
    solve.m = 2 * pts.shape[1]; return solve


def make_advdiff_cell(extra, e_lo, e_hi, refine=5, npr=16):
    from skfem import MeshTri, ElementTriP1, Basis, BilinearForm, asm
    from skfem.helpers import dot, grad
    mesh = MeshTri.init_sqsymmetric().refined(refine); basis = Basis(mesh, ElementTriP1())
    @BilinearForm
    def diff(u, v, w): return dot(grad(u), grad(v))
    @BilinearForm
    def conv(u, v, w): return (w["bx"] * grad(u)[0] + w["by"] * grad(u)[1]) * v
    @BilinearForm
    def mass(u, v, w): return u * v
    x = basis.global_coordinates()                                                  # quadrature-point coordinates, shape (2, nel, nq)
    bx = np.sin(np.pi * x[0]) * np.cos(np.pi * x[1]); by = -np.cos(np.pi * x[0]) * np.sin(np.pi * x[1])      # divergence-free cellular flow
    Kd = asm(diff, basis); Cc = asm(conv, basis, bx=bx, by=by); Mm = asm(mass, basis); D = basis.get_dofs().all(); I = basis.complement_dofs(D); xy = mesh.p; P = _probes(basis, npr)
    def solve(mu):
        eps = _logu(mu[0], e_lo, e_hi); beta = _aff(mu[1], 5.0, 20.0); sx = _aff(mu[2], 0.15, 0.45); sw = 0.08 if not extra else _aff(mu[3], 0.05, 0.12)
        s = 30.0 * np.exp(-((xy[0] - sx) ** 2 + (xy[1] - sx) ** 2) / (2 * sw**2)); A = eps * Kd + beta * Cc; u = np.zeros(basis.N); u[I] = spla.spsolve(A[I][:, I].tocsc(), (Mm @ s)[I]); return P @ u
    solve.m = npr * npr; return solve


def make_lshape_fine(refine=7):
    """Seconds-per-run case: the L-shaped plate of problems_tp.make_lshape (3 stiffness regions + load angle) on a fine mesh."""
    from .problems_tp import make_lshape
    return make_lshape(3, 1.0, 10.0, refine=refine)


def build_suite_tp2():
    from .problems import Problem
    S = {}
    def add(fam, lvl, p, fn, desc): S[f"{fam}_L{lvl}"] = Problem(f"{fam}_L{lvl}", fam, lvl, p, fn.m, fn, desc)
    add("helmholtz", 1, 3, make_helmholtz(2.0, 20.0, False), "scikit-fem Helmholtz, k^2 in [2,20], source position")
    add("helmholtz", 2, 4, make_helmholtz(30.0, 70.0, True), "scikit-fem Helmholtz, k^2 in [30,70] (several resonances), source position and width")
    add("reacdiff_fe", 1, 4, make_reacdiff_fe(1, 0.5, 5.0), "scikit-fem nonlinear reaction-diffusion (Newton), uniform D")
    add("reacdiff_fe", 2, 6, make_reacdiff_fe(4, 5.0, 100.0), "scikit-fem nonlinear reaction-diffusion (Newton), 2x2 blocks of D, strong reaction")
    add("disc_elast", 1, 5, make_disc_elast(4, 1.0, 10.0), "scikit-fem plane stress on a disc, 4 angular stiffness sectors + load angle")
    add("disc_elast", 2, 9, make_disc_elast(8, 0.2, 20.0), "scikit-fem plane stress on a disc, 8 angular stiffness sectors, high contrast")
    add("advdiff_cell", 1, 3, make_advdiff_cell(False, 0.03, 0.1), "scikit-fem advection-diffusion in a cellular flow")
    add("advdiff_cell", 2, 4, make_advdiff_cell(True, 0.012, 0.04), "scikit-fem advection-diffusion in a cellular flow, thin layers, source width")
    return S


def build_suite_fine():
    from .problems import Problem
    f = make_lshape_fine(); return {"lshape_fine_L1": Problem("lshape_fine_L1", "lshape_fine", 1, 4, f.m, f, "scikit-fem L-plate on a fine mesh (seconds per run)")}
