import sys, pathlib, numpy as np
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))
from surrogate_bench import problems as P

def _star(n):
    x = np.arange(1, n + 1) / (n + 1); X, Y = np.meshgrid(x, x, indexing="ij"); return np.sin(np.pi * X) * np.sin(np.pi * Y)

def test_helm_manufactured_solution():
    n, k2 = 63, 5.0; ust = _star(n); f = (2 * np.pi**2 - k2) * ust
    L = P._lap2d(n); import scipy.sparse as sp, scipy.sparse.linalg as spla
    u = spla.spsolve((L - k2 * sp.identity(n * n)).tocsc(), f.ravel()).reshape(n, n); assert np.linalg.norm(u - ust) / np.linalg.norm(ust) < 3e-3

def test_reacdiff_manufactured_solution():
    n, c = 63, 4.0; ust = _star(n); f = 2 * np.pi**2 * ust + c * ust**3
    # mu giving c=4 : c_lo=1,c_hi=7 -> mu0=0.5 ; A,w irrelevant (overridden)
    u = P.make_reacdiff(1.0, 7.0, n=n, raw=True, f_override=f)(np.array([0.5, 0.5, 0.5]))
    assert np.linalg.norm(u - ust) / np.linalg.norm(ust) < 3e-3

def test_diff1d_constant_coefficient_exact():
    sol = P.make_diff1d(4, 1e-12); u = sol(np.full(4, 0.5)); n = 128; x = np.arange(1, n + 1) / (n + 1)
    assert np.linalg.norm(u - 0.5 * x * (1 - x)) / np.linalg.norm(0.5 * x * (1 - x)) < 1e-6

def test_heatp_refinement_and_steady_limit():
    mu = np.array([0.5, 0.5, 0.5]); ref = P.make_heatp(0.05, 0.2, n=127, raw=True)(mu); errs = []
    for n in (15, 31, 63):
        u = P.make_heatp(0.05, 0.2, n=n, raw=True)(mu); r = (n + 1) // 16; errs.append(np.linalg.norm(u[r - 1::r, r - 1::r][:15, :15] - ref[8 - 1::8, 8 - 1::8][:15, :15]) / np.linalg.norm(ref[7::8, 7::8][:15, :15]))
    assert errs[0] > errs[1] > errs[2] and errs[2] < 0.05

def test_v21_suite_valid_incl_extrapolation():
    S = P.build_suite_v21(); rng = np.random.default_rng(0); assert len(S) == 8 and len(P.build_suite()) == 32
    for name, pr in S.items():
        for box in (rng.random(pr.p), -0.25 + 1.5 * rng.random(pr.p)):
            u = pr.solve(box); assert np.isfinite(u).all() and u.shape == (pr.m,), name
