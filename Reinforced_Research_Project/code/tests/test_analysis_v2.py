import sys, pathlib, numpy as np, pandas as pd
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))
from surrogate_bench import analysis_v2 as V

def test_perm_spearman_exact_extremes():
    x = np.arange(8.0); assert abs(V.perm_spearman_neg(x, -x)["p"] - 1 / 40320) < 1e-12 and V.perm_spearman_neg(x, x)["p"] == 1.0
def test_primary_tests_detect_planted_signal_and_null():
    fz = dict(R2=dict(mu=[8.0, -1.0], sd=[1.4, 1.0], beta=[0.2, -0.9], ym=0.5), B0=dict(mu=[8.0], sd=[1.4], beta=[0.2], ym=0.5))
    rng = np.random.default_rng(0); rows = []
    for i in range(8):
        f1 = rng.normal(-1, 1)
        for N in (64, 128, 256, 512, 1024): rows.append(dict(instance=f"i{i}", N=N, log_cv_err_r4=f1, y=0.5 + 0.2 * (np.log2(N) - 8) / 1.4 - 0.9 * (f1 + 1) + 0.05 * rng.normal()))
    P1, P2 = V.primary_tests(pd.DataFrame(rows), fz, n_boot=2000); assert P1["rho"] < -0.9 and P1["p"] < 0.01 and P2["p"] < 0.05 and P2["mean_sq_error_gain"] > 0
    rows = [dict(r, y=0.5 + 0.1 * rng.normal()) for r in rows]; P1, P2 = V.primary_tests(pd.DataFrame(rows), fz, n_boot=2000); assert P2["mean_sq_error_gain"] < 0.2


def test_expA2_binomial_logic(tmp_path):
    import json, scipy.stats as ss
    assert ss.binomtest(3, 7, 0.10, alternative="greater").pvalue < 0.05 and ss.binomtest(2, 7, 0.10, alternative="greater").pvalue > 0.05


def test_expB_shift_sign_convention(tmp_path):
    import json, pandas as pd
    # synthetic: NL improves by 0.3 decades with longer training -> shift_toward_NL must be +0.3 (B2 compares this with 0.5)
    rows = [dict(instance="i", seed=0, N=256, method=m, epochs=6000, err_6000=e6, err_1500=e1) for m, e6, e1 in (("pod_mlp", 1e-2, 1e-2), ("mlp_direct", 5e-3, 1e-2), ("bottleneck", 5e-3, 1e-2))]
    (tmp_path / "i__s0.json").write_text(json.dumps(rows))
    df = pd.DataFrame([dict(instance="i", seed=0, N=256, method=m, err=e) for m, e in (("pod_gp", 1e-3), ("pod_poly", 1e-1), ("pod_mlp", 1e-2), ("mlp_direct", 1e-2), ("bottleneck", 1e-2))])
    out, c = V.expB(str(tmp_path), df); assert abs(out["median_shift_toward_NL"] - np.log10(2)) < 1e-9 and out["B2_pass"] is True
