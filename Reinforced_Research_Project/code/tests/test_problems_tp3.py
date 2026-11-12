"""Checks for the Stage 8 expensive problem (problems_tp3): beam theory, load reversal, exact stiffness scaling, band sensitivity, mesh convergence."""
import sys, pathlib, numpy as np, pytest
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))
pytest.importorskip("skfem")
from surrogate_bench import problems_tp3 as T


def _rel(a, b): return np.linalg.norm(a - b) / np.linalg.norm(b)


def test_cantilever_matches_euler_bernoulli_beam():
    f = T.make_bracket3d(32, 8, 4); u = f(np.array([0.0, 0.0, 0.0, 0.5, 0.0]))        # E = 1 everywhere, nu = 0.3, load in +y
    n = f.m // 3; idx = 1 * 6 + 5; x = (5.5 / 6) * 3.8 + 0.1; F = 0.5; I = 0.5 * 1.0**3 / 12; eb = F * x**2 * (3 * 4.0 - x) / (6 * 1.0 * I)
    assert u[1 * n + idx] > 0 and abs(u[1 * n + idx] / eb - 1) < 0.2                   # a stocky beam (L/h = 4): shear and end effects of order 10 %


def test_load_reversal_scaling_and_band_sensitivity():
    f = T.make_bracket3d(16, 4, 2); mu = np.array([0.2, 0.7, 0.4, 0.3, 0.0]); mu_r = mu.copy(); mu_r[-1] = 1.0                 # theta = 0 versus pi
    assert _rel(f(mu), -f(mu_r)) < 1e-9
    a = f(np.array([0.0, 0.0, 0.0, 0.3, 0.6])); b = f(np.array([1.0, 1.0, 1.0, 0.3, 0.6])); assert abs(np.linalg.norm(a) / np.linalg.norm(b) - 10.0) < 1e-6     # all moduli x10
    base = np.array([0.5, 0.5, 0.5, 0.3, 0.2])
    for k in range(3): m = base.copy(); m[k] = 0.0; assert _rel(f(m), f(base)) > 1e-3


def test_mesh_convergence_of_probe_values():
    mu = np.array([0.3, 0.6, 0.2, 0.5, 0.4]); u = [T.make_bracket3d(*d)(mu) for d in ((16, 4, 2), (24, 6, 3), (32, 8, 4))]
    assert _rel(u[1], u[2]) < _rel(u[0], u[1])
