import sys, pathlib, numpy as np, pytest, torch
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))
torch.set_num_threads(1)
from surrogate_bench import methods as M, hpo, diagnostics as D, problems as P

@pytest.fixture(scope="module")
def dev():
    pr = P.build_dev(); rng = np.random.default_rng(0)
    X = rng.random((60, pr.p)); Y = np.array([pr.solve(x) for x in X])
    Xt = rng.random((40, pr.p)); Yt = np.array([pr.solve(x) for x in Xt])
    return pr, X, Y, Xt, Yt

@pytest.mark.parametrize("name", M.ALL_METHODS)
def test_fit_predict_shape_finite_deterministic(dev, name):
    pr, X, Y, Xt, Yt = dev; M.NN_EPOCHS = 30; M._train.__defaults__ = (30,)
    cfg = M.REGISTRY[name].sample_config(np.random.default_rng(0), len(X), pr.p, pr.m, 0)
    a = M.REGISTRY[name]().fit(X, Y, cfg, 3).predict(Xt); b = M.REGISTRY[name]().fit(X, Y, cfg, 3).predict(Xt)
    assert a.shape == Yt.shape and np.isfinite(a).all()
    assert np.allclose(a, b, atol=1e-9)

def test_pod_gp_beats_mean_predictor_on_smooth_problem(dev):
    pr, X, Y, Xt, Yt = dev
    cfg = M.PodGP.sample_config(np.random.default_rng(0), len(X), pr.p, pr.m, 0)
    e = M.rel_l2(Yt, M.PodGP().fit(X, Y, cfg, 0).predict(Xt)).mean()
    base = M.rel_l2(Yt, np.tile(Y.mean(0), (len(Yt), 1))).mean()
    assert e < 0.1 * base

def test_pod_is_exact_for_low_rank_data():
    rng = np.random.default_rng(0); Y = rng.normal(size=(30, 3)) @ rng.normal(size=(3, 50)); pod = M.POD(Y, 3)
    assert np.linalg.norm(pod.decode(pod.encode(Y)) - Y) < 1e-9

def test_hpo_selects_by_validation_not_test(dev):
    pr, X, Y, Xt, Yt = dev; M.NN_EPOCHS = 10; M._train.__defaults__ = (10,)
    r, _, _ = hpo.run_method("pod_poly", X, Y, Xt, Yt, Xt, Yt, 6, 0, pr.p, pr.m)
    chosen = min(r["trials"], key=lambda t: t["val"])
    assert r["best_cfg"] == chosen["cfg"] and len(r["trials"]) == 6 and r["trials"][0]["trial"] == 0

def test_hpo_trial0_is_default(dev):
    pr, X, Y, *_ = dev
    for n in M.ALL_METHODS:
        c0 = M.REGISTRY[n].sample_config(np.random.default_rng(1), 60, pr.p, pr.m, 0)
        c0b = M.REGISTRY[n].sample_config(np.random.default_rng(99), 60, pr.p, pr.m, 0)
        assert c0 == c0b                               # default independent of the RNG

def test_pilot_features_rank_two_data():
    rng = np.random.default_rng(0); Y = rng.normal(size=(32, 2)) @ rng.normal(size=(2, 64))
    f = D.pilot_features(Y)
    assert f["log_cv_err_r4"] < -8 and f["slope"] < -1 and f["r_tol1e-2"] <= 2

def test_pilot_features_use_only_given_snapshots():
    rng = np.random.default_rng(0); Y = rng.normal(size=(32, 40)); f1 = D.pilot_features(Y); f2 = D.pilot_features(Y.copy())
    assert f1 == f2

def test_no_train_test_parameter_overlap():
    from surrogate_bench.data import draw_params
    for name in ("darcy_L2", "burgers_L2", "wave_L1"):
        pr = P.build_suite()[name]; tr, te, ex = draw_params(pr)
        assert not set(map(tuple, np.round(tr, 12))) & set(map(tuple, np.round(te, 12)))
        assert np.all(~np.all((ex >= 0) & (ex <= 1), axis=1))     # extrapolation set lies outside the unit box


def test_hpo_sampling_is_reproducible_across_processes():
    """Regression test for a bug found in the fresh-clone audit: config sampling must not depend on PYTHONHASHSEED."""
    import subprocess, os, json
    code = ("import sys,json,numpy as np; sys.path.insert(0,%r); from surrogate_bench import hpo,methods as M; import zlib;"
            "r=np.random.default_rng(3*7919+zlib.crc32(b'pod_poly')%%10007); print(json.dumps([M.PodPoly.sample_config(r,64,4,128,b) for b in range(4)]))") % str(pathlib.Path(__file__).resolve().parents[1] / "src")
    outs = [subprocess.check_output([sys.executable, "-c", code], env={**os.environ, "PYTHONHASHSEED": h}, text=True) for h in ("1", "2", "3")]
    assert outs[0] == outs[1] == outs[2]
    src = (pathlib.Path(__file__).resolve().parents[1] / "src/surrogate_bench/hpo.py").read_text()
    assert "hash(method)" not in src


def test_nn_logs_loss_curve_and_krr_works(dev):
    pr, X, Y, Xt, Yt = dev; M.NN_EPOCHS = 30; M._train.__defaults__ = (30,)
    cfg = M.REGISTRY["mlp_direct"].sample_config(np.random.default_rng(0), len(X), pr.p, pr.m, 0)
    mdl = M.REGISTRY["mlp_direct"]().fit(X, Y, cfg, 0); assert len(mdl.curve) >= 10 and mdl.curve[-1][0] == 30 and mdl.final_loss == mdl.curve[-1][1]
    k = M.REGISTRY["pod_krr"]; c = k.sample_config(np.random.default_rng(0), len(X), pr.p, pr.m, 0); e = M.rel_l2(Yt, k().fit(X, Y, c, 0).predict(Xt)).mean()
    assert np.isfinite(e) and e < 0.5 * M.rel_l2(Yt, np.tile(Y.mean(0), (len(Yt), 1))).mean()
    r, _, _ = hpo.run_method("pod_krr", X, Y, Xt, Yt, Xt, Yt, 3, 0, pr.p, pr.m); assert r["loss_curve"] is None and len(r["trials"]) == 3


def test_gp_iso_runs_and_uses_single_lengthscale(dev):
    pr, X, Y, Xt, Yt = dev; cfg = M.PodGP.sample_config(np.random.default_rng(0), len(X), pr.p, pr.m, 0)
    m_iso = M.REGISTRY["pod_gp_iso"]().fit(X, Y, cfg, 0); e = M.rel_l2(Yt, m_iso.predict(Xt)).mean()
    assert np.isfinite(e) and e < 0.2 * M.rel_l2(Yt, np.tile(Y.mean(0), (len(Yt), 1))).mean()
    assert np.ndim(m_iso.gps[0][1].kernel_.k1.k2.length_scale) == 0
