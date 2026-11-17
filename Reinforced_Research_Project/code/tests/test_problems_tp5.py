"""Checks for the Stage 11 frequency-response problems (problems_tp5): eigenfrequencies against theory, passivity, reciprocity, convergence."""
import sys, pathlib, numpy as np, pytest
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))
pytest.importorskip("skfem")
from surrogate_bench import problems_tp5 as T


def _rel(a, b): return np.linalg.norm(a - b) / np.linalg.norm(b)


def test_chain_resonances_match_the_fixed_free_chain_formula():
    n = 20; theory = [2 * np.sin((2 * j - 1) * np.pi / (2 * (2 * n + 1))) for j in range(1, 5)]; c = T.make_mdk_chain(0.02, 0.6, 0.0005, 0.0005, n=n); mu3 = np.log(1 / 0.3) / np.log(10)      # uniform chain: added mass 0, spring stiffness 1
    ws = np.linspace(0, 1, 4000); amp = np.array([np.linalg.norm(c(np.array([x, 0.0, 0.0, mu3]))) for x in ws]); w = 0.02 + 0.58 * ws
    from scipy.signal import find_peaks
    pk, _ = find_peaks(amp, prominence=0.05 * amp.max()); assert len(pk) >= 4 and all(abs(w[pk[i]] - theory[i]) < 0.01 * theory[i] for i in range(4))


def test_disc_resonances_at_bessel_derivative_zeros():
    d = T.make_disc_acoustic(1.4, 4.2, 0.001, 0.001); xs = np.linspace(0, 1, 1200); amp = np.array([np.linalg.norm(d(np.array([x, 0.5, 0.5, 0.3]))) for x in xs]); k = 1.4 + 2.8 * xs
    from scipy.signal import find_peaks
    pk, _ = find_peaks(amp, prominence=0.1 * amp.max()); expected = [1.8412, 3.0542, 3.8317]; assert len(pk) >= 3 and all(abs(k[pk[i]] - expected[i]) < 0.02 * expected[i] for i in range(3))      # zeros of J1', J2', J0'


def test_passivity_and_reciprocity():
    rs = np.random.default_rng(0)
    c = T.make_mdk_chain(0.05, 0.6, 0.001, 0.01)
    for _ in range(5): u, f, w, al, M, K = c.full(rs.random(4)); assert np.vdot(u, f).imag > 0                       # Im(u^H f) = w u^H C u >= 0
    mu = rs.random(4); u, f, w, al, M, K = c.full(mu); n = c.n; A = K - w**2 * M + 1j * w * al * M; G = np.linalg.inv(A); assert np.allclose(G, G.T, atol=1e-9 * abs(G).max())      # symmetric transfer matrix = reciprocity
    d = T.make_disc_acoustic(1.4, 4.2, 0.005, 0.04, refine=4)
    for _ in range(4): u, f, k, beta = d.full(rs.random(4)); assert np.vdot(u, f).imag > 0


def test_disc_mesh_convergence():
    mu = np.array([0.4, 0.3, 0.5, 0.2]); u = [T.make_disc_acoustic(1.4, 2.3, 0.01, 0.08, refine=r)(mu) for r in (3, 4, 5, 6)]
    e = [_rel(u[i], u[3]) for i in range(3)]; assert e[2] < e[1] < e[0] and e[2] < 0.05


def test_suite_shapes_finite_deterministic_and_extrapolation_safe():
    S = T.build_suite_frf2(); assert len(S) == 4; rs = np.random.default_rng(1)
    for n, P in S.items():
        mu = rs.random(P.p); y = P.solve(mu); assert y.shape == (P.m,) and np.all(np.isfinite(y)) and np.array_equal(y, P.solve(mu)), n
        Xe = -0.25 + 1.5 * rs.random((50, P.p)); assert np.isfinite(np.array([P.solve(x) for x in Xe])).all(), n                       # extrapolation draws are finite
