import json, numpy as np, warnings, subprocess, sys, pathlib, tempfile, json
warnings.filterwarnings("ignore")
from surroselect import SurrogateSelector, PodKRRWide, PodPoly, POD, rel_l2, make_report
from surroselect.models import _kern
from surroselect.select import _power_law


def _data(N=60, p=3, m=40, seed=0):
    rng = np.random.default_rng(seed); X = rng.random((N, p)); g = np.linspace(0, 1, m)
    f = lambda x: np.sin(2 * x[0] * g + x[1]) + x[2] * np.exp(-((g - 0.5) / 0.25) ** 2)
    return X, np.array([f(x) for x in X]), f, g


def test_krr_closed_form_loo_matches_brute_force():
    X, Y, *_ = _data(30); pod = POD(Y, 6); A = pod.encode(Y); kind, ell, lam = "rbf", 1.3, 1e-6; N = len(X)
    K = _kern(X, X, kind, ell); alpha = np.linalg.solve(K + lam * N * np.eye(N), A); H = K @ np.linalg.inv(K + lam * N * np.eye(N))
    loo = (A - K @ alpha) / (1 - np.diag(H))[:, None]; brute = []
    for i in range(N):
        idx = np.delete(np.arange(N), i); al = np.linalg.solve(K[np.ix_(idx, idx)] + lam * N * np.eye(N - 1), A[idx]); brute.append(A[i] - K[i, idx] @ al)
    # leave-one-out with a fixed (N-based) ridge differs slightly from the formula's (N-1) ridge; compare with the matching formula
    brute2 = []
    for i in range(N):
        idx = np.delete(np.arange(N), i); al = np.linalg.solve(K[np.ix_(idx, idx)] + lam * N * np.eye(N - 1), A[idx]); brute2.append(A[i] - K[i, idx] @ al)
    assert np.allclose(loo, np.array(brute2), rtol=1e-4, atol=1e-9)


def test_poly_recovers_polynomial_exactly():
    rng = np.random.default_rng(1); X = rng.random((80, 2)); g = np.linspace(0, 1, 20)
    Y = np.array([(1 + x[0] + 2 * x[1] ** 2) * np.cos(g) + x[0] * x[1] * g for x in X]); m = PodPoly(r=10).fit(X, Y)
    Xt = rng.random((50, 2)); Yt = np.array([(1 + x[0] + 2 * x[1] ** 2) * np.cos(g) + x[0] * x[1] * g for x in Xt]); assert rel_l2(Yt, m.predict(Xt)) < 1e-6


def test_selector_picks_accurate_model_and_reports_ties():
    X, Y, f, g = _data(100); s = SurrogateSelector(cv=3, random_state=0).fit(X, Y, refit_all=True)
    Xt = np.random.default_rng(5).random((100, 3)); Yt = np.array([f(x) for x in Xt])
    assert rel_l2(Yt, s.predict(Xt)) < 1e-3 and s.best_name_ in s.ties_ and s.cv_table_[0]["cv_error"] <= s.cv_table_[-1]["cv_error"]
    errs = {k: rel_l2(Yt, m.predict(s._scale(Xt))) for k, m in s.all_models_.items()}; assert errs[s.best_name_] <= 3 * min(errs.values())


def test_basis_limit_flag_fires_when_pod_truncation_dominates():
    rng = np.random.default_rng(2); N, m = 120, 200; X = rng.random((N, 2)); g = np.linspace(0, 1, m)
    Y = np.array([np.exp(-((g - (0.1 + 0.8 * x[0])) / 0.02) ** 2) for x in X])          # narrow travelling pulse: slow decay of POD modes
    s = SurrogateSelector(cv=3).fit(X, Y); fr = s.floor_report_; assert fr["pod_floor_cv"] > 1e-2 and fr["basis_limited"]


def test_power_law_and_runs_needed():
    n = np.array([16, 32, 64, 128.0]); e = 0.5 * n ** -1.5; a, b = _power_law(n, e); assert abs(b - 1.5) < 1e-8
    X, Y, *_ = _data(60); s = SurrogateSelector(cv=3).fit(X, Y); s.curve_ = dict(name=s.best_name_, n=list(n), error=list(e))
    need = s.runs_needed(1e-4, max_factor=1e6); assert abs(need - (0.5 / 1e-4) ** (1 / 1.5)) / need < 1e-6 and s.runs_needed(1e-4, max_factor=1) is None


def test_report_text():
    X, Y, *_ = _data(48); s = SurrogateSelector(cv=3).fit(X, Y); s.learning_curve(); txt = make_report(s, 0.01); assert "Selected" in txt and "Basis check" in txt


def test_cli_fit_predict_evaluate_roundtrip():
    X, Y, f, g = _data(60); Xt = np.random.default_rng(9).random((40, 3)); Yt = np.array([f(x) for x in Xt]); src = str(pathlib.Path(__file__).resolve().parents[1] / "src")
    env = {"PYTHONPATH": src, "PATH": "/usr/bin:/bin:/usr/local/bin"}; run = lambda *a: subprocess.run([sys.executable, "-m", "surroselect.cli", *a], capture_output=True, text=True, env=env)
    with tempfile.TemporaryDirectory() as d:
        d = pathlib.Path(d); np.savez(d / "train.npz", X=X, Y=Y); np.savez(d / "test.npz", X=Xt, Y=Yt); np.save(d / "xnew.npy", Xt)
        r = run("fit", str(d / "train.npz"), "--model", str(d / "m.pkl"), "--target", "0.01", "--no-curve", "--json", str(d / "fit.json")); assert r.returncode == 0 and "Selected" in r.stdout and (d / "m.pkl").exists()
        r = run("predict", str(d / "m.pkl"), str(d / "xnew.npy"), "--out", str(d / "yhat.npy")); assert r.returncode == 0; Yh = np.load(d / "yhat.npy"); assert Yh.shape == Yt.shape
        r = run("evaluate", str(d / "m.pkl"), str(d / "test.npz"), "--json", str(d / "ev.json")); assert r.returncode == 0
        err = json.load(open(d / "ev.json"))["mean_relative_l2_error"]; assert abs(err - rel_l2(Yt, Yh)) < 1e-12 and err < 1e-2
        r = run(str(d / "train.npz"), "--no-curve"); assert r.returncode == 0 and "Selected" in r.stdout                  # shortcut form


def test_krr_loo_is_stable_near_interpolation():
    """Regression test for a bug found in the smoke test: with a tiny ridge and short length-scale 1-H_ii is ~1e-11 and must not be clipped or computed by cancellation."""
    X, Y, *_ = _data(40); pod = POD(Y, 6); A = pod.encode(Y); kind, ell, lam = "matern52", 0.15, 1e-10; N = len(X)
    K = _kern(X, X, kind, ell); w, Q = np.linalg.eigh(K); w = np.maximum(w, 0); d = 1 / (w + lam * N); alpha = Q @ ((Q.T @ A) * d[:, None]); Hc = (Q**2) @ (lam * N * d)
    loo = (A - (A - lam * N * alpha)) / Hc[:, None]; brute = []
    for i in range(N):
        idx = np.delete(np.arange(N), i); al = np.linalg.solve(K[np.ix_(idx, idx)] + lam * N * np.eye(N - 1), A[idx]); brute.append(A[i] - K[i, idx] @ al)
    assert np.allclose(loo, np.array(brute), rtol=5e-2, atol=1e-8 * np.abs(A).max())


def test_nrmse_metric_option_and_default_unchanged():
    rng = np.random.default_rng(0); X = rng.random((60, 3)); Y = (100 + 5 * np.sin(3 * X[:, 0]) + 2 * X[:, 1] ** 2 - X[:, 2])[:, None]
    s = SurrogateSelector(cv=3, metric="nrmse").fit(X, Y); assert s.metric == "nrmse" and s.best_cv_error_ < 0.05 and s.floor_report_["pod_floor_cv"] < 1e-8
    from surroselect.models import nrmse; assert abs(nrmse(Y, Y, Y)) == 0 and abs(nrmse(Y, np.full_like(Y, Y.mean()), Y) - 1) < 1e-12
    assert SurrogateSelector(cv=3).metric == "rel_l2"
