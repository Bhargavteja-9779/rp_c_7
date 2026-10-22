"""Alternative-explanation test: is the LS/NL outcome an artifact of the mean-relative-error metric? Winners are still chosen by validation
(mean) error; the outcome y is recomputed with the median and the 95th-percentile per-sample error of the selected models. v1 + Exp A raw data."""
import json, glob, pathlib, math, numpy as np, pandas as pd
ROOT = pathlib.Path(__file__).resolve().parents[2]; RP = ROOT / "Reinforced_Research_Project"; LS, NL = ["pod_gp", "pod_poly", "pod_mlp"], ["mlp_direct", "bottleneck"]; TIE = 0.10
rows = []
for d in (ROOT / "results/raw", RP / "results/raw_expA"):
    for f in sorted(glob.glob(str(d / "*__s*.json"))):
        if "errors" in f: continue
        m = json.load(open(f))
        for N in (32, 64, 128, 256, 512, 1024):
            rr = {r["method"]: r for r in m["records"] if r["N"] == N}; a = min(LS, key=lambda k: rr[k]["val_best"]); b = min(NL, key=lambda k: rr[k]["val_best"])
            rows.append(dict(instance=m["instance"], seed=m["seed"], N=N, y_mean=math.log10(rr[b]["test_err"] / rr[a]["test_err"]), y_med=math.log10(rr[b]["test_med"] / rr[a]["test_med"]), y_p95=math.log10(rr[b]["test_p95"] / rr[a]["test_p95"])))
d = pd.DataFrame(rows); c = d.groupby(["instance", "N"], as_index=False)[["y_mean", "y_med", "y_p95"]].mean()
cls = lambda s: np.where(s > TIE, 1, np.where(s < -TIE, -1, 0)); out = dict(n_cells=int(len(c)))
for k in ("y_med", "y_p95"):
    out[k] = dict(agree_class_with_mean=float((cls(c[k]) == cls(c.y_mean)).mean()), spearman_with_mean=float(c[["y_mean", k]].corr(method="spearman").iloc[0, 1]),
                  n_sign_flips_among_clear_mean_cells=int(((np.sign(c[k]) != np.sign(c.y_mean)) & (c.y_mean.abs() > TIE)).sum()), n_clear_mean_cells=int((c.y_mean.abs() > TIE).sum()),
                  mean_shift_vs_mean_metric=float((c[k] - c.y_mean).mean()), by_N_clear_LS_NL_tie={int(N): [int((g[k] > TIE).sum()), int((g[k] < -TIE).sum()), int((g[k].abs() <= TIE).sum())] for N, g in c.groupby("N")})
out["mean_metric_by_N_clear_LS_NL_tie"] = {int(N): [int((g.y_mean > TIE).sum()), int((g.y_mean < -TIE).sum()), int((g.y_mean.abs() <= TIE).sum())] for N, g in c.groupby("N")}
(RP / "results/metric_sensitivity.json").write_text(json.dumps(out, indent=1)); print(json.dumps(out, indent=1))
