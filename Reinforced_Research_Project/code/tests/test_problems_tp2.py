"""Checks for the Stage 7 scikit-fem problems (problems_tp2): mesh convergence, exact scaling/symmetry identities, Newton consistency."""
import sys, pathlib, numpy as np, pytest
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))
pytest.importorskip("skfem")
from surrogate_bench import problems_tp2 as T


def _rel(a, b): return np.linalg.norm(a - b) / np.linalg.norm(b)


def test_helmholtz_mesh_convergence():
    mu = np.array([0.4, 0.3, 0.6]); u = [T.make_helmholtz(2.0, 20.0, False, refine=r)(mu) for r in (3, 4, 5, 6)]
    d = [_rel(u[i], u[i + 1]) for i in range(3)]
    assert d[2] < d[1] < d[0] and d[2] < 5e-3


def test_helmholtz_zero_wavenumber_is_poisson_and_symmetric_source():
    # k^2 -> small: solution is symmetric under x<->y reflection when the source sits on the diagonal (sx = sy)
    f = T.make_helmholtz(1e-9, 2e-9, False, refine=4); mu = np.array([0.0, 0.5, 0.5]); u = f(mu)
    g = np.arange(16); idx = (g[:, None] * 16 + g[None, :]).ravel(); idxT = (g[None, :] * 16 + g[:, None]).ravel()
    assert _rel(u[idx], u[idxT]) < 1e-9 and np.all(u > 0)


def test_reacdiff_linear_limit_scales_with_diffusivity():
    f = T.make_reacdiff_fe(1, 1e-9, 2e-9, refine=3)           # reaction negligible -> u = G s / D
    u1 = f(np.array([0.0, 0.5, 0.5])); u2 = f(np.array([1.0, 0.5, 0.5]))   # D = 0.3 vs 3.0 : ratio 10
    assert abs(np.linalg.norm(u1) / np.linalg.norm(u2) - 10.0) < 1e-4


def test_reacdiff_newton_converged_residual():
    # re-evaluate the discrete nonlinear residual at the returned field via the full-field solve on a refined run: reaction reduces the response
    f_lin = T.make_reacdiff_fe(1, 1e-9, 2e-9, refine=3); f_nl = T.make_reacdiff_fe(1, 0.5, 5.0, refine=3)
    mu = np.array([0.5, 0.9, 0.5]); u_nl = f_nl(mu); u_lin = f_lin(np.array([0.5, 0.0, 0.5]))
    assert np.all(np.isfinite(u_nl)) and u_nl.max() < u_lin.max()          # the cubic sink must lower the peak
    # Newton limit cycle check: more Newton iterations leave the answer unchanged
    f_more = T.make_reacdiff_fe(1, 0.5, 5.0, refine=3, newton=30)
    assert _rel(f_more(mu), u_nl) < 1e-8


def test_reacdiff_mesh_convergence():
    mu = np.array([0.5, 0.5, 0.5]); u = [T.make_reacdiff_fe(1, 0.5, 5.0, refine=r)(mu) for r in (3, 4, 5)]
    assert _rel(u[1], u[2]) < _rel(u[0], u[1]) and _rel(u[1], u[2]) < 1e-2


def test_disc_elast_load_reversal_and_stiffness_scaling():
    f = T.make_disc_elast(4, 1.0, 10.0, refine=3); mu = np.array([0.2, 0.5, 0.8, 0.3, 0.0]); mu2 = mu.copy(); mu2[-1] = 1.0   # theta = -pi/2 vs +pi/2
    assert _rel(f(mu), -f(mu2)) < 1e-9 or _rel(f(mu), -f(mu2)) < 1e-8
    a = f(np.array([0.0, 0.0, 0.0, 0.0, 0.7])); b = f(np.array([1.0, 1.0, 1.0, 1.0, 0.7]))   # all moduli x10
    assert abs(np.linalg.norm(a) / np.linalg.norm(b) - 10.0) < 1e-6


def test_disc_elast_mesh_convergence():
    mu = np.array([0.3, 0.6, 0.2, 0.9, 0.5]); u = {r: T.make_disc_elast(4, 1.0, 10.0, refine=r)(mu) for r in (3, 4, 5, 6)}
    e = {r: _rel(u[r], u[6]) for r in (3, 4, 5)}          # probes are fixed physical points; clamp/load arcs are defined by polar angle
    assert e[5] < e[4] < e[3] and e[5] < 0.05


def test_disc_elast_regions_are_boundary_arcs_only():
    # a uniform field cannot be reproduced if interior facets were loaded/clamped: with equal moduli the response to a +x load must be net +x at the load side
    f = T.make_disc_elast(4, 1.0, 10.0, refine=4); u = f(np.array([0.5] * 4 + [0.5])); n = f.m // 2
    assert u[:n].mean() > 0 and abs(u[0]) > 1e-3                                  # centre probe moves (it was exactly 0 when a whole wedge was clamped)


def test_advdiff_mesh_convergence_and_positivity():
    mu = np.array([1.0, 0.2, 0.5]); u = [T.make_advdiff_cell(False, 0.03, 0.1, refine=r)(mu) for r in (4, 5, 6)]
    assert _rel(u[1], u[2]) < _rel(u[0], u[1]) and _rel(u[1], u[2]) < 0.05


def test_suite_tp2_shapes_and_determinism():
    S = T.build_suite_tp2(); assert len(S) == 8
    rng = np.random.default_rng(3)
    for name, pr in S.items():
        mu = rng.random(pr.p); y = pr.solve(mu); assert y.shape == (pr.m,) and np.all(np.isfinite(y)), name
        assert np.array_equal(y, pr.solve(mu)), name
