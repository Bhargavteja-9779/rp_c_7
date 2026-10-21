import sys, pathlib, numpy as np, pytest
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))
from surrogate_bench import problems as P


def _common(u_raw, n, n_c=15):
    """Pick nodes shared with an n_c-interior-node grid (n = 2^k*(n_c+1)-1)."""
    r = (n + 1) // (n_c + 1)
    return u_raw[r - 1::r, r - 1::r][:n_c, :n_c]


def test_darcy_constant_coefficient_matches_poisson_series():
    n = 31; solve = P.make_darcy(4, 1e-12, n=n, raw=True)       # sigma ~ 0 -> a = 1
    u = solve(np.full(4, 0.5)); x = np.arange(1, n + 1) / (n + 1); X, Y = np.meshgrid(x, x, indexing="ij")
    ex = np.zeros_like(X)
    for m in range(1, 80, 2):
        for k in range(1, 80, 2):
            ex += 16 / (np.pi**4 * m * k * (m * m + k * k)) * np.sin(m * np.pi * X) * np.sin(k * np.pi * Y)
    assert np.linalg.norm(u - ex) / np.linalg.norm(ex) < 2e-3


def test_transport_matches_exact_translation():
    mu = np.array([0.5, 0.5, 0.5, 0.5]); u = P.make_transport(0.08, 0.12)(mu)
    c, x1, w, a2 = 0.4, 0.35, 0.10, 0.65; x = np.arange(128) / 128
    ex = P._periodic_gauss(x - c * 1.0, x1, w) + a2 * P._periodic_gauss(x - c * 1.0, x1 + 0.25, w)
    assert np.linalg.norm(u - ex) / np.linalg.norm(ex) < 1e-4


def test_wave_matches_dalembert():
    mu = np.array([0.5, 0.5, 0.5, 0.5]); u = P.make_wave(0.06, 0.10)(mu)
    c, x0, w, a2, T = 0.7, 0.4, 0.08, 0.65, 0.5; x = np.arange(128) / 128
    g = lambda s: P._periodic_gauss(s, x0, w) + a2 * P._periodic_gauss(s, x0 + 0.3, w)
    ex = 0.5 * (g(x - c * T) + g(x + c * T))
    assert np.linalg.norm(u - ex) / np.linalg.norm(ex) < 3e-3


def test_burgers_self_convergence_and_decay():
    mu = np.array([0.5, 0.3, 0.4, 0.5])
    fine = P.make_burgers(0.005, 0.01, N=1024, dt=2.5e-4)(mu); base = P.make_burgers(0.005, 0.01)(mu)
    fine = fine[::2]; assert np.linalg.norm(base - fine) / np.linalg.norm(fine) < 5e-3
    assert np.abs(base).max() < 1.0                         # max principle for viscous Burgers


def test_fisher_front_speed_and_bounds():
    mu = np.array([0.0, 0.5, 0.5, 0.5]); r, D = 10.0, 2.5e-3
    u = P.make_fisher(3.0, N=512)(mu)                        # output grid of 256 pts on [0,1]
    assert u.min() >= -1e-9 and u.max() <= 1 + 1e-9
    x = (np.arange(256) + 0.5) / 256 * 1.0
    pos = np.interp(0.5, u[::-1], x[::-1]) if False else x[np.argmin(np.abs(u - 0.5))]
    speed = (pos - 0.1) / 3.0
    assert abs(speed - 2 * np.sqrt(r * D)) / (2 * np.sqrt(r * D)) < 0.12


@pytest.mark.parametrize("maker,args", [("make_heat2d", (0.05, 0.15, 0.25)), ("make_bratu", (1.0, 3.5)), ("make_advdiff", (0.05, 0.2))])
def test_2d_grid_refinement_converges(maker, args):
    mu = np.array([0.4, 0.55, 0.6, 0.5])[: 3 if maker == "make_bratu" else 4]
    errs = []
    ref = _common(getattr(P, maker)(*args, n=127, raw=True)(mu), 127)
    for n in (15, 31, 63):
        u = _common(getattr(P, maker)(*args, n=n, raw=True)(mu), n)
        errs.append(np.linalg.norm(u - ref) / np.linalg.norm(ref))
    assert errs[0] > errs[1] > errs[2]
    assert errs[2] < 0.05


def test_extrapolated_parameters_remain_valid():
    rng = np.random.default_rng(1)
    for name, pr in P.build_suite().items():
        for _ in range(3):
            u = pr.solve(-0.25 + 1.5 * rng.random(pr.p)); assert np.isfinite(u).all() and u.shape == (pr.m,)


def test_deterministic():
    pr = P.build_suite()["burgers_L2"]; mu = np.array([.2, .3, .4, .5])
    assert np.array_equal(pr.solve(mu), pr.solve(mu))
