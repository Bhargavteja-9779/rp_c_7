import sys, pathlib, numpy as np, pytest
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))
from surrogate_bench import problems as P


def _common(u_raw, n, n_c=15):
    r = (n + 1) // (n_c + 1); return u_raw[r - 1::r, r - 1::r][:n_c, :n_c]


def test_kdv_single_soliton_matches_exact_solution():
    solve = P.make_kdv(False); mu = np.array([0.5, 0.5, 0.0, 0.0])     # b=0 -> pure soliton
    c, x0, L, T = 1.4, 6.0, 20.0, 3.0; u = solve(mu); x = (np.arange(256) * L / 256)[::2]
    d = (x - x0 - c * T + L / 2) % L - L / 2; ex = 0.5 * c / np.cosh(0.5 * np.sqrt(c) * d) ** 2
    assert np.linalg.norm(u - ex) / np.linalg.norm(ex) < 5e-3


def test_kdv_conserves_mass_and_converges_in_time_step():
    for two in (False, True):
        mu = np.array([0.4, 0.6, 0.3, 0.7]); u = P.make_kdv(two)(mu); u2 = P.make_kdv(two, dt=0.002)(mu)
        assert np.linalg.norm(u - u2) / np.linalg.norm(u2) < 1e-3
        u0 = P.make_kdv(two, T=0.0)(mu) if False else None
    m_end = P.make_kdv(True)(np.array([.5, .5, .5, .5])).sum(); m_0 = P.make_kdv(True, T=0.004)(np.array([.5, .5, .5, .5])).sum()
    assert abs(m_end - m_0) / abs(m_0) < 1e-6                                   # integral of u is conserved


@pytest.mark.parametrize("maker,args,mu", [("make_incl", (3.0, 10.0), [0.4, 0.55, 0.5, 0.5]), ("make_nlheat", (1.0, 8.0), [0.6, 0.5, 0.5])])
def test_2d_refinement_converges(maker, args, mu):
    mu = np.array(mu); ref = _common(getattr(P, maker)(*args, n=127, raw=True)(mu), 127); errs = []
    for n in (15, 31, 63):
        errs.append(np.linalg.norm(_common(getattr(P, maker)(*args, n=n, raw=True)(mu), n) - ref) / np.linalg.norm(ref))
    assert errs[0] > errs[1] > errs[2] and errs[2] < 0.06


def test_incl_reduces_to_constant_coefficient_for_unit_contrast():
    n = 31; u = P.make_incl(1.0, 1.0 + 1e-12, n=n, raw=True)(np.array([.5, .5, .5, .5])); ref = P.make_darcy(4, 1e-12, n=n, raw=True)(np.full(4, .5))
    assert np.linalg.norm(u - ref) / np.linalg.norm(ref) < 1e-6


def test_nlheat_linear_limit_and_nonlinear_effect():
    n = 31; lin = P.make_nlheat(1e-9, 2e-9, n=n, raw=True)(np.array([.5, .5, .5])); non = P.make_nlheat(8.0, 9.0, n=n, raw=True)(np.array([.5, .5, .5]))
    assert non.max() < lin.max()                                                # k(u)>1 lowers the temperature
    L = P._lap2d(n); f = lin.ravel(); res = L @ f                                # linear limit satisfies -lap u = f (f>0 smooth)
    assert np.all(res > -1e-8) and 0.2 < lin.max() < 5.0


def test_v2_suite_valid_incl_extrapolation_and_dimensions():
    S = P.build_suite_v2(); rng = np.random.default_rng(0); assert len(S) == 8 and S["darcyhd_L2"].p == 32
    for name, pr in S.items():
        for box in (rng.random(pr.p), -0.25 + 1.5 * rng.random(pr.p)):
            u = pr.solve(box); assert np.isfinite(u).all() and u.shape == (pr.m,), name
    assert len(P.build_suite()) == 24
