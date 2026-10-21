"""POST-HOC EXPLORATORY analyses (run after confirmatory results; see research_design/deviations.md D4).
E1 long-training NN check; E2 pilot-size sensitivity + B1 fold diagnosis; E3 one-feature deployable rule."""
import sys, json, pathlib, time, os, numpy as np, pandas as pd
ROOT = pathlib.Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT / "src"))
RES = ROOT.parent / "results"; OUT = RES / "exploratory"; OUT.mkdir(exist_ok=True)
from multiprocessing import Pool


def _e1(args):
    for v in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS"): os.environ[v] = "1"
    import torch; torch.set_num_threads(1)
    from surrogate_bench import methods as M
    from surrogate_bench.problems import build_suite
    from surrogate_bench.data import build_dataset, POOL
    inst, N, meth, cfg, seed, epochs = args
    M.NN_EPOCHS = epochs; M._train.__defaults__ = (epochs,)
    P = build_suite()[inst]; d = build_dataset(P, str(ROOT / "data_cache"))
    idx = np.random.default_rng(1000 + seed).permutation(POOL)[:N]
    t = time.time(); mdl = M.REGISTRY[meth]().fit(d["mu_train"][idx], d["u_train"][idx], cfg, seed * 100 + 99)
    return dict(instance=inst, N=N, method=meth, epochs=epochs, err=float(M.rel_l2(d["u_test"], mdl.predict(d["mu_test"])).mean()), seconds=time.time() - t)


def e1():
    import glob
    jobs = []
    insts = ["bratu_L1", "darcy_L1", "heat2d_L1", "burgers_L1", "transport_L2", "fisher_L2"]
    for inst in insts:
        m = json.load(open(RES / "raw" / f"{inst}__s0.json"))
        for r in m["records"]:
            if r["N"] in (256, 1024) and r["method"] in ("pod_mlp", "mlp_direct", "bottleneck"):
                jobs.append((inst, r["N"], r["method"], r["best_cfg"], 0, 6000))
    with Pool(4) as p: out = p.map(_e1, jobs, chunksize=1)
    df = pd.DataFrame(out); raw = pd.read_csv(RES / "raw_results.csv"); raw = raw[raw.seed == 0]
    df = df.merge(raw[["instance", "N", "method", "err"]].rename(columns={"err": "err_1500ep"}), on=["instance", "N", "method"])
    gp = raw[raw.method == "pod_gp"][["instance", "N", "err"]].rename(columns={"err": "err_pod_gp"}); df = df.merge(gp, on=["instance", "N"])
    df["ratio_6000_vs_1500"] = df.err / df.err_1500ep; df.to_csv(OUT / "e1_long_training.csv", index=False)
    print(df.round(5).to_string())


def e2_e3():
    from surrogate_bench import analysis as A, stats as S
    from surrogate_bench.diagnostics import pilot_features
    from surrogate_bench.data import build_dataset, POOL
    from surrogate_bench.problems import build_suite
    df, ft, seeds = A.load(str(RES / "raw")); y = A.family_y(df); cells0 = A.cell_table(y, ft)
    # ---- E2a pilot-size sensitivity (features recomputed from cached training data; n0 <= 64 so pilot is inside every N >= 64 training set)
    suite = build_suite(); rows = []
    for n0 in (16, 24, 32, 48, 64):
        f = []
        for inst in df.instance.unique():
            d = build_dataset(suite[inst], str(ROOT / "data_cache"))
            for s in seeds:
                perm = np.random.default_rng(1000 + s).permutation(POOL); ff = pilot_features(d["u_train"][perm[:n0]]); f.append(dict(instance=inst, seed=s, **ff))
        ftn = pd.DataFrame(f); cells = A.cell_table(y, ftn); h, _ = A.h2(cells, extra_models=False, n_boot=4000)
        rows.append(dict(n0=n0, rmse_B0=h["rmse"]["B0"], rmse_B1=h["rmse"]["B1"], rmse_Mspec=h["rmse"]["M_spec"],
                         delta_vs_B0=h["M_spec_vs_B0"]["delta"], ci_lo_B0=h["M_spec_vs_B0"]["ci95"][0], ci_hi_B0=h["M_spec_vs_B0"]["ci95"][1], p_B0=h["M_spec_vs_B0"]["p"],
                         delta_vs_B1=h["primary_M_spec_vs_B1"]["delta"], p_B1=h["primary_M_spec_vs_B1"]["p"]))
    pd.DataFrame(rows).to_csv(OUT / "e2_pilot_size_sensitivity.csv", index=False); print(pd.DataFrame(rows).round(3).to_string())
    # ---- E2b why B1 is poor: per-held-out-family squared residuals
    d = cells0[cells0.N.isin(A.N_H2)].sort_values(["instance", "N"]).reset_index(drop=True); yv, g = d.y.values, d.family.values
    lg = np.log2(d.N.values); folds = {}
    for k, X in dict(B0=np.c_[lg], B1=np.c_[lg, d.p.values], M_spec=np.c_[lg, d.log_cv_err_r4.values, d.slope.values]).items():
        r = S.lofo_residuals(X, yv, g); folds[k] = {fam: float(np.sqrt(np.mean(r[g == fam] ** 2))) for fam in np.unique(g)}
    pd.DataFrame(folds).round(3).to_csv(OUT / "e2_lofo_rmse_by_heldout_family.csv"); print(pd.DataFrame(folds).round(3))
    # ---- E3 rank association and a deployable one-feature rule (LOFO threshold), at N=1024 and N=256
    out = []
    for N in (64, 256, 1024):
        c = cells0[cells0.N == N].reset_index(drop=True)
        for feat in ("log_cv_err_r4", "slope", "log_cv_err_r8"):
            rho = S.spearman(c[feat].values, c.y.values)
            # LOFO threshold: choose t on training families that maximises accuracy of sign(y>0) = (feat < t) ; predict held-out
            correct = 0
            for fam in c.family.unique():
                tr, te = c[c.family != fam], c[c.family == fam]
                cand = np.sort(tr[feat].values); best = max(((np.mean((tr[feat].values < t) == (tr.y.values > 0)), t) for t in cand))
                correct += np.sum((te[feat].values < best[1]) == (te.y.values > 0))
            out.append(dict(N=N, feature=feat, spearman_with_y=rho, lofo_threshold_accuracy=correct / len(c), majority_baseline=max(np.mean(c.y > 0), np.mean(c.y <= 0)), n=len(c)))
    pd.DataFrame(out).to_csv(OUT / "e3_one_feature_rule.csv", index=False); print(pd.DataFrame(out).round(3).to_string())


if __name__ == "__main__":
    which = sys.argv[1]
    {"e1": e1, "e23": e2_e3}[which]()
