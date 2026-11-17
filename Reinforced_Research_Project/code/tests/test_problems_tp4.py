"""Checks for the Stage 10 frequency-response problems (problems_tp4): resonance locations against theory, passivity, reciprocity, mesh convergence."""
import sys, pathlib, numpy as np, pytest
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))
pytest.importorskip("skfem")
from surrogate_bench import problems_tp4 as T


def _rel(a, b): return np.linalg.norm(a - b) / np.linalg.norm(b)


def test_square_cavity_resonance_at_pi():
    f = T.make_acoustic("square", 2.6, 4.7, 0.001, 0.001, refine=5); xs = np.linspace(0, 1, 800); amp = [np.linalg.norm(f(np.array([x, 0.5, 0.3, 0.4]))) for x in xs]
    k_peak = 2.6 + 2.1 * xs[int(np.argmax(amp))]; assert abs(k_peak - np.pi) < 0.02 * np.pi and max(amp) / min(amp) > 50      # first (degenerate) Neumann-type eigenvalue of the unit square, k = pi


def test_beam_first_resonance_matches_euler_bernoulli():
    f = T.make_beam_frf(2.0, 6.0, 0.03, 0.3); ws = np.linspace(0, 1, 800); amp = [np.linalg.norm(f(np.array([x, 0.0, 0.0, 1.0]))) for x in ws]
    assert abs((2 + 4 * ws[int(np.argmax(amp))]) - 3.516) < 0.02 * 3.516                    # cantilever, (beta_1 L)^2 = 3.516 for EI = rho A = L = 1 (damping shifts the peak slightly)


def test_passivity_dissipation_is_nonnegative():
    a = T.make_acoustic("square", 2.6, 3.8, 0.01, 0.08, refine=4); rs = np.random.default_rng(0)
    for _ in range(5): u, f, k, beta = a.full(rs.random(4)); assert np.vdot(u, f).imag > 0                       # Im(u^H f) = k beta |u|^2_boundary >= 0
    b = T.make_beam_frf(2.0, 30.0, 0.01, 0.1)
    for _ in range(5): u, f, w, dm = b.full(rs.random(4)); assert np.vdot(u[b.I], f).imag > 0                      # Im(u^H f) = w u^H C u >= 0


def test_beam_reciprocity():
    b = T.make_beam_frf(2.0, 30.0, 0.01, 0.1); xa, xb = 0.5, 0.9; mua = np.array([0.4, 0.3, 0.2, (xa - 0.3) / 0.7]); mub = mua.copy(); mub[3] = (xb - 0.3) / 0.7
    ua, *_ = b.full(mua); ub, *_ = b.full(mub); ra, rb = b.load(xa), b.load(xb); assert abs(rb @ ua - ra @ ub) < 1e-8 * abs(rb @ ua)      # response at b to a load at a equals response at a to a load at b


def test_mesh_convergence():
    mu = np.array([0.4, 0.3, 0.6, 0.5]); u = [T.make_acoustic("square", 2.6, 3.8, 0.01, 0.08, refine=r)(mu) for r in (3, 4, 5)]; assert _rel(u[1], u[2]) < _rel(u[0], u[1]) and _rel(u[1], u[2]) < 0.02
    v = [T.make_beam_frf(2.0, 6.0, 0.03, 0.3, nel=n)(mu) for n in (10, 20, 40)]; assert _rel(v[1], v[2]) < _rel(v[0], v[1]) and _rel(v[1], v[2]) < 1e-3


def test_suite_shapes_finite_and_deterministic():
    S = T.build_suite_frf(); assert len(S) == 4; rs = np.random.default_rng(1)
    for n, P in S.items(): mu = rs.random(P.p); y = P.solve(mu); assert y.shape == (P.m,) and np.all(np.isfinite(y)) and np.array_equal(y, P.solve(mu)), n
