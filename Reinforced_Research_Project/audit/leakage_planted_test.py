"""Leakage audit script: (1) exact overlap and nearest-neighbour distances between train pool, test and extrapolation parameters for all problems; (2) a PLANTED leak: 20 test samples are copied into the training set; the overlap check must flag it and the leaked error must be far below the clean error."""
import sys, json, pathlib, numpy as np
ROOT = pathlib.Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT / "code/src")); sys.path.insert(0, str(ROOT / "surroselect/src"))
from scipy.spatial import cKDTree
from surrogate_bench.problems import build_suite
from surrogate_bench.data import draw_params, build_dataset, POOL
S = build_suite(); out = {"per_problem": {}}
def overlap(A, B): d, _ = cKDTree(A).query(B); return float(d.min()), int((d == 0).sum())
for name, P in S.items():
    tr, te, ex = draw_params(P); d_te = overlap(tr, te); d_ex = overlap(tr, ex); d_tr = cKDTree(tr).query(tr, k=2)[0][:, 1].min()
    out["per_problem"][name] = dict(min_dist_train_test=d_te[0], exact_matches_train_test=d_te[1], min_dist_train_ext=d_ex[0], exact_matches_train_ext=d_ex[1], min_pairwise_train=float(d_tr), p=P.p)
out["max_exact_matches"] = max(v["exact_matches_train_test"] + v["exact_matches_train_ext"] for v in out["per_problem"].values())
# planted leak on one problem
import warnings; warnings.filterwarnings("ignore")
from surroselect import PodGP, rel_l2
P = S["heatcomp_L1"]; d = build_dataset(P, str(ROOT / "code/data_cache")); rng = np.random.default_rng(0); N = 64
idx = rng.permutation(POOL)[:N]; X, Y = d["mu_train"][idx], d["u_train"][idx]; Xt, Yt = d["mu_test"], d["u_test"]
clean = rel_l2(Yt, PodGP("rbf", 16).fit(X, Y).predict(Xt))
leak = rng.permutation(len(Xt))[:20]; Xl, Yl = np.vstack([X, Xt[leak]]), np.vstack([Y, Yt[leak]])
m = PodGP("rbf", 16).fit(Xl, Yl); leaked_err_on_leaked = rel_l2(Yt[leak], m.predict(Xt[leak])); clean_err_on_rest = rel_l2(np.delete(Yt, leak, 0), m.predict(np.delete(Xt, leak, 0)))
flag_leak = overlap(Xl, Xt)[1]; flag_clean = overlap(X, Xt)[1]
out["planted"] = dict(problem="heatcomp_L1", N=N, error_clean_model_on_test=clean, error_on_leaked_samples=leaked_err_on_leaked, error_on_non_leaked_samples=clean_err_on_rest, exact_matches_flagged_with_leak=flag_leak, exact_matches_flagged_without_leak=flag_clean,
                      audit_detects_leak=bool(flag_leak >= 20 and flag_clean == 0), leaked_error_much_lower=bool(leaked_err_on_leaked < 0.2 * clean))
(ROOT / "results/leakage_planted_test.json").write_text(json.dumps(out, indent=1)); print(json.dumps(out["planted"], indent=1), "max exact matches over all problems:", out["max_exact_matches"])
