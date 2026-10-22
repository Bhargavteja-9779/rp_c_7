"""Alternative explanation: NN baselines limited by the hyper-parameter search-space boundary? Share of selected NN configs at the edge of the space,
split by whether the cell is a clear LS win (ybar>0.1) or not. v1 + Exp A records."""
import json, glob, pathlib, math, numpy as np, pandas as pd
ROOT = pathlib.Path(__file__).resolve().parents[2]; RP = ROOT / "Reinforced_Research_Project"; LS, NL = ["pod_gp", "pod_poly", "pod_mlp"], ["mlp_direct", "bottleneck"]
rows = []; yb = {}
for d in (ROOT / "results/raw", RP / "results/raw_expA"):
    for f in sorted(glob.glob(str(d / "*__s*.json"))):
        if "errors" in f: continue
        m = json.load(open(f))
        for N in (32, 64, 128, 256, 512, 1024):
            rr = {r["method"]: r for r in m["records"] if r["N"] == N}; a = min(LS, key=lambda k: rr[k]["val_best"]); b = min(NL, key=lambda k: rr[k]["val_best"]); yb.setdefault((m["instance"], N), []).append(math.log10(rr[b]["test_err"] / rr[a]["test_err"]))
            for meth in ("pod_mlp", "mlp_direct", "bottleneck"):
                c = rr[meth]["best_cfg"]; rows.append(dict(instance=m["instance"], seed=m["seed"], N=N, method=meth, width=c["width"], depth=c["depth"], lr=c["lr"], wd=c["wd"], r=c.get("r"), k=c.get("k"), is_default=rr[meth]["trials"][0]["val"] == rr[meth]["val_best"]))
d = pd.DataFrame(rows); d["ybar"] = [np.mean(yb[(i, N)]) for i, N in zip(d.instance, d.N)]; d["ls_clear"] = d.ybar > 0.10
d["max_width"] = d.width == 256; d["max_depth"] = d.depth == 4; d["lr_high"] = d.lr > 6e-3; d["lr_low"] = d.lr < 1.7e-3; d["edge_any"] = d.max_width | d.max_depth | d.lr_high | d.lr_low
out = dict(n_selected_configs=int(len(d)), share_default_config_selected=float(d.is_default.mean()))
for tag, g in (("all", d), ("cells_where_LS_clearly_wins", d[d.ls_clear]), ("other_cells", d[~d.ls_clear])):
    out[tag] = dict(n=int(len(g)), width256=float(g.max_width.mean()), depth4=float(g.max_depth.mean()), lr_top_third=float(g.lr_high.mean()), lr_bottom_third=float(g.lr_low.mean()), any_edge=float(g.edge_any.mean()))
out["expected_share_if_uniform"] = dict(width256=1 / 3, depth4=1 / 3, lr_top_third="~0.33", any_edge="~0.8 (4 hyper-parameters)")
bm = d[d.method == "bottleneck"]; out["bottleneck_k_distribution"] = {int(k): float((bm.k == k).mean()) for k in sorted(bm.k.dropna().unique())}
(RP / "results/search_space_boundary.json").write_text(json.dumps(out, indent=1)); print(json.dumps(out, indent=1))
