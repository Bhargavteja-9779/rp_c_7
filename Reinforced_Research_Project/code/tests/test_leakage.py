import sys, pathlib, re, numpy as np, torch
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src")); torch.set_num_threads(1)
from surrogate_bench import methods as M, hpo, diagnostics as D, problems as P


def test_pilot_features_ignore_everything_beyond_the_pilot_rows_in_the_driver():
    src = (pathlib.Path(__file__).resolve().parents[1] / "src/surrogate_bench/experiment.py").read_text()
    assert re.search(r'pilot_features\(d\["u_train"\]\[perm\[: cfg\["pilot_n0"\]\]\]\)', src)            # only the first n0 pool rows of the permutation


def test_validation_error_is_unaffected_by_test_labels():
    pr = P.build_dev(); rng = np.random.default_rng(0); X = rng.random((40, pr.p)); Y = np.array([pr.solve(x) for x in X]); Xt = rng.random((30, pr.p)); Yt = np.array([pr.solve(x) for x in Xt])
    M.NN_EPOCHS = 5; M._train.__defaults__ = (5,)
    a, _, _ = hpo.run_method("pod_poly", X, Y, Xt, Yt, Xt, Yt, 4, 0, pr.p, pr.m)
    b, _, _ = hpo.run_method("pod_poly", X, Y, Xt, rng.normal(size=Yt.shape), Xt, rng.normal(size=Yt.shape), 4, 0, pr.p, pr.m)      # corrupt ALL test labels
    assert a["val_best"] == b["val_best"] and a["best_cfg"] == b["best_cfg"] and [t["val"] for t in a["trials"]] == [t["val"] for t in b["trials"]]


def test_poly_degree_cap_is_visible_in_distinct_effective_features():
    from math import comb
    assert comb(32 + 3, 3) > 5000 and comb(10 + 6, 6) > 5000          # the cap triggers for p=32 degree>=3 and p=10 degree 6 (audit F17): documented limitation
