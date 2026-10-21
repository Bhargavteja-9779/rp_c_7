import sys, pathlib, numpy as np
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))
from surrogate_bench import stats as S


def _synthetic(signal, seed, n_fam=8, per=10):
    rng = np.random.default_rng(seed); g = np.repeat(np.arange(n_fam), per)
    logN = np.tile(np.arange(per) % 5, n_fam).astype(float); p = np.repeat(rng.integers(3, 11, n_fam), per).astype(float)
    f = rng.normal(size=len(g)) + np.repeat(rng.normal(size=n_fam), per)           # a feature with family structure
    y = 0.3 * logN + 0.1 * p + signal * f + 0.15 * rng.normal(size=len(g))
    return g, logN, p, f, y


def test_h2_machinery_detects_planted_signal():
    wins = 0
    for s in range(10):
        g, logN, p, f, y = _synthetic(0.8, s)
        rb = S.lofo_residuals(np.c_[logN, p], y, g); rn = S.lofo_residuals(np.c_[logN, p, f], y, g)
        wins += S.cluster_bootstrap_rmse_diff(rb, rn, g, n_boot=1000, seed=s)["p"] < 0.05
    assert wins >= 8


def test_h2_machinery_controls_false_positives_under_null():
    fp = 0
    for s in range(60):
        g, logN, p, f, y = _synthetic(0.0, s)
        rb = S.lofo_residuals(np.c_[logN, p], y, g); rn = S.lofo_residuals(np.c_[logN, p, f], y, g)
        fp += S.cluster_bootstrap_rmse_diff(rb, rn, g, n_boot=500, seed=s)["p"] < 0.05
    assert fp / 60 < 0.12                                                          # nominal 0.05 (+ MC noise)


def test_holm_matches_hand_calculation():
    r = S.holm({"a": 0.01, "b": 0.02, "c": 0.04, "d": 0.30})
    assert np.isclose(r["a"][0], 0.04) and np.isclose(r["b"][0], 0.06) and np.isclose(r["c"][0], 0.08) and np.isclose(r["d"][0], 0.30)
    assert r["a"][1] and not r["b"][1]


def test_mcnemar_and_sign_tests_exact_values():
    assert np.isclose(S.mcnemar_exact_greater(8, 2)["p"], 0.0546875)             # P(X>=8 | n=10, .5)
    assert np.isclose(S.sign_test_greater(12, 16)["p"], 0.0384, atol=1e-3)


def test_wilcoxon_detects_shift_and_not_null():
    rng = np.random.default_rng(0)
    assert S.wilcoxon_greater(rng.normal(0.8, 0.5, 16))["p"] < 0.01
    ps = [S.wilcoxon_greater(rng.normal(0, 1, 16))["p"] for _ in range(300)]
    assert 0.02 < np.mean(np.array(ps) < 0.05) < 0.09
