import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))
import numpy as np, pytest
pytest.importorskip("skfem")
from surrogate_bench.problems_tp import make_heatcomp, make_lshape, make_heatmove, make_convdiff


def _series_T(x, y, terms=41):
    s = 0.0
    for m in range(1, terms, 2):
        for n in range(1, terms, 2):
            s += 16 / (np.pi**4 * m * n * (m * m + n * n)) * np.sin(m * np.pi * x) * np.sin(n * np.pi * y)
    return s


def test_heatcomp_matches_series_solution():
    f = make_heatcomp(2, 0.2, 5.0, refine=5); x = np.log(1 / 0.2) / np.log(5.0 / 0.2)       # uniform conductivity k = 1
    u = f(np.full(4, x)); g = (np.arange(16) + 0.5) / 16; ref = np.array([_series_T(a, b) for b in g for a in g])
    assert np.linalg.norm(u - ref) / np.linalg.norm(ref) < 5e-3


def test_heatcomp_scales_inversely_with_conductivity():
    f = make_heatcomp(2, 0.2, 5.0); lo = lambda k: np.log(k / 0.2) / np.log(5.0 / 0.2)
    u1 = f(np.full(4, lo(1.0))); u2 = f(np.full(4, lo(2.0))); assert np.allclose(u1, 2 * u2, rtol=1e-8)


def test_lshape_linear_scaling_and_load_reversal():
    f = make_lshape(3, 1.0, 10.0); lo = lambda E: np.log(E) / np.log(10.0)
    a = f(np.array([lo(2.0)] * 3 + [0.3])); b = f(np.array([lo(4.0)] * 3 + [0.3])); assert np.allclose(a, 2 * b, rtol=1e-8)
    p, q = f(np.array([0.5, 0.5, 0.5, 0.0])), f(np.array([0.5, 0.5, 0.5, 1.0])); assert np.allclose(p, -q, atol=1e-10 * np.abs(p).max())


def test_lshape_mesh_convergence():
    mu = np.array([0.2, 0.6, 0.4, 0.3]); a, b = make_lshape(3, 1.0, 10.0, refine=3)(mu), make_lshape(3, 1.0, 10.0, refine=4)(mu)
    assert np.linalg.norm(a - b) / np.linalg.norm(b) < 0.08


def test_heatmove_time_and_space_convergence():
    mu = np.array([0.4, 0.5, 0.5]); a = make_heatmove(False, 0.02, 0.08, 0.16)(mu)
    assert np.linalg.norm(a - make_heatmove(False, 0.02, 0.08, 0.16, nsteps=120)(mu)) / np.linalg.norm(a) < 0.06
    assert np.linalg.norm(a - make_heatmove(False, 0.02, 0.08, 0.16, refine=5)(mu)) / np.linalg.norm(a) < 0.03


def test_convdiff_mesh_convergence_and_near_positivity():
    mu = np.array([0.5, 0.4, 0.5]); a, b = make_convdiff(False, 0.03, 0.1, refine=5)(mu), make_convdiff(False, 0.03, 0.1, refine=6)(mu)
    assert np.linalg.norm(a - b) / np.linalg.norm(b) < 0.03 and a.min() > -0.05 * a.max()
