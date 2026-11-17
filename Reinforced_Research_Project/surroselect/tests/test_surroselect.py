import pytest, json, numpy as np, warnings, subprocess, sys, pathlib, tempfile, json
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


def test_scalar_output_predictions_have_shape_n_by_one():
    """Regression test (review 03): a GP on a single output returned a 1-D array that broadcast against (n,1) targets and gave garbage NRMSE."""
    rng = np.random.default_rng(0); X = rng.random((40, 3)); Y = (50 + np.sin(3 * X[:, 0]) + X[:, 1])[:, None]
    from surroselect import GPFull, PodGP, nrmse
    for m in (GPFull("rbf"), PodGP("rbf", 4)):
        m.fit(X, Y); P = m.predict(X[:7]); assert P.shape == (7, 1) and nrmse(Y[:7], P, Y) < 0.1


def test_cli_with_network_adds_a_tuned_mlp_to_the_pool(tmp_path, monkeypatch):
    pytest.importorskip("torch"); pytest.importorskip("optuna")
    from surroselect import nn as _nn, cli
    orig = _nn.TunedMLP; monkeypatch.setattr(_nn, "TunedMLP", lambda **k: orig(search_epochs=60, final_factor=2, lbfgs_iters=5, **k))
    rs = np.random.default_rng(0); X = rs.random((40, 2)); t = np.linspace(0, 1, 20); Y = np.sin(3 * X[:, :1] * t) + X[:, 1:] * t
    np.savez(tmp_path / "d.npz", X=X, Y=Y); out = tmp_path / "r.json"
    assert cli.main(["fit", str(tmp_path / "d.npz"), "--with-network", "--network-trials", "2", "--no-curve", "--json", str(out)]) == 0
    import json; names = [r["name"] for r in json.load(open(out))["cv_table"]]; assert "tuned_mlp" in names


def test_no_usable_model_warning_fires_on_unlearnable_data_and_not_on_smooth_data():
    from surroselect import SurrogateSelector, make_report
    X, Y, f, g = _data(60); ok = SurrogateSelector(cv=4).fit(X, Y); assert ok.usable_ and "no usable model" not in make_report(ok)
    rs = np.random.default_rng(5); Xr = rs.random((60, 3)); Yr = rs.standard_normal((60, 40))           # outputs unrelated to the inputs
    bad = SurrogateSelector(cv=4).fit(Xr, Yr); assert (not bad.usable_) and "WARNING: no usable model" in make_report(bad)
    assert SurrogateSelector(cv=4, usable_threshold=10.0).fit(Xr, Yr).usable_            # the threshold is an option


def test_cost_benefit_arithmetic_and_report_paragraph():
    from surroselect import cost_benefit, SurrogateSelector, make_report
    c = cost_benefit(solver_seconds=2.0, n_train=100, tool_seconds=50.0, n_queries=1000, predict_seconds=0.0)
    assert c["surrogate_fixed_seconds"] == 250.0 and c["break_even_queries"] == 125.0 and c["direct_seconds"] == 2000.0 and c["surrogate_total_seconds"] == 250.0
    assert cost_benefit(1.0, 10, predict_seconds=2.0)["break_even_queries"] is None                  # a stand-in slower than the solver never pays back
    X, Y, f, g = _data(60); sel = SurrogateSelector(cv=4).fit(X, Y); assert "Cost." in make_report(sel, solver_seconds=30.0, n_queries=5000, tool_seconds=10.0)
    try: cost_benefit(0.0, 5); raise AssertionError
    except ValueError: pass


def test_input_validation_gives_clear_errors_and_cli_status():
    from surroselect import SurrogateSelector
    X, Y, f, g = _data(40)
    for bad, msg in ((dict(X=X, Y=Y[:, 0]), "2-D"), (dict(X=X[:30], Y=Y), "runs"), (dict(X=X, Y=np.where(np.arange(len(Y))[:, None] == 3, np.nan, Y)), "NaN"), (dict(X=X[:5], Y=Y[:5]), "too few")):
        try: SurrogateSelector(cv=4).fit(bad["X"], bad["Y"]); raise AssertionError("no error for " + msg)
        except ValueError as e: assert msg in str(e), str(e)
    try: SurrogateSelector(cv=1).fit(X, Y); raise AssertionError
    except ValueError: pass
    from surroselect import cli
    with tempfile.TemporaryDirectory() as d:
        np.savez(pathlib.Path(d) / "bad.npz", A=X); assert cli.main(["fit", str(pathlib.Path(d) / "bad.npz")]) == 2


def test_report_notes_non_monotone_learning_curve():
    from surroselect import SurrogateSelector, make_report
    X, Y, f, g = _data(60); sel = SurrogateSelector(cv=4).fit(X, Y); sel.curve_ = dict(name=sel.best_name_, n=[10.0, 20.0, 40.0, 80.0], error=[0.2, 0.9, 0.03, 0.004])
    assert "not monotone" in make_report(sel); sel.curve_ = dict(name=sel.best_name_, n=[10.0, 20.0, 40.0, 80.0], error=[0.2, 0.1, 0.03, 0.004]); assert "not monotone" not in make_report(sel)


def test_forecast_interval_and_confident_runs_needed():
    from surroselect import SurrogateSelector, make_report
    X, Y, f, g = _data(60); sel = SurrogateSelector(cv=4).fit(X, Y); sel.curve_ = dict(name=sel.best_name_, n=[10.0, 20.0, 40.0, 80.0], error=[0.2, 0.1, 0.05, 0.025])     # exact power law, exponent 1
    lo, c, hi = sel.forecast_interval(160); assert abs(c - 0.0125) < 1e-9 and abs(np.log10(hi / c) - 0.5794) < 1e-9 and abs(np.log10(c / lo) - 0.5794) < 1e-9
    n_pt, n_conf = sel.runs_needed(0.001, max_factor=1e9), sel.runs_needed_confident(0.001, max_factor=1e9); assert abs(n_pt - 2000) < 1e-6 and abs(n_conf / n_pt - 10 ** 0.5794) < 1e-6                   # e = 2/n: 2000 runs; the confident statement needs more
    assert sel.runs_needed_confident(1e-9) is None                     # more than 16x the budget
    try: sel.forecast_interval(10, level=0.5); raise AssertionError
    except ValueError: pass
    assert "empirical 80% interval" in make_report(sel, target=0.01)


def _rational_data(N, seed):
    r = np.random.default_rng(seed); V = np.linalg.qr(np.random.default_rng(0).standard_normal((60, 8)))[0]; X = r.random((N, 3)); q = (X[:, 0] - 0.55) ** 2 + 0.02 + 0.3 * X[:, 1] * X[:, 0]
    C = np.stack([(1 + X[:, 0] * (k + 1) + X[:, 1] ** 2 * (k % 3) + 0.5 * X[:, 2] * np.cos(k)) / q for k in range(8)], 1); return X, C @ V.T


def test_pod_rational_recovers_a_rational_response_with_a_pole_in_the_cube():
    from surroselect import PodRational, PodPoly, rel_l2, make_candidate
    Xt, Yt = _rational_data(150, 1); X, Y = _rational_data(200, 2); m = PodRational().fit(X, Y); e = rel_l2(Yt, m.predict(Xt))
    assert e < 1e-3 and rel_l2(Yt, PodPoly(32).fit(X, Y).predict(Xt)) > 100 * e                     # exact structure is found; a polynomial cannot do it
    assert make_candidate("pod_rational").name == "pod_rational"


def test_pod_rational_is_deterministic_picklable_and_degrades_gracefully():
    import pickle
    from surroselect import PodRational
    X, Y = _rational_data(60, 3); m1, m2 = PodRational().fit(X, Y), PodRational().fit(X, Y); assert np.array_equal(m1.predict(X[:5]), m2.predict(X[:5])); assert np.array_equal(pickle.loads(pickle.dumps(m1)).predict(X[:5]), m1.predict(X[:5]))
    Xs, Ys, f, g = _data(60); ms = PodRational().fit(Xs, Ys); assert np.isfinite(ms.predict(Xs)).all()                  # smooth data: runs, errors are finite (the selector will simply not choose it)


def test_selector_chooses_the_rational_member_when_it_is_far_better():
    from surroselect import SurrogateSelector
    from surroselect import default_candidates
    X, Y = _rational_data(200, 4); assert "pod_rational" not in [c.name for c in default_candidates(Y.shape[1], len(X), 3)]; sel = SurrogateSelector(candidates=default_candidates(Y.shape[1], len(X), 3, with_rational=True), cv=4).fit(X, Y); assert sel.best_name_ == "pod_rational", sel.cv_table_[:3]
