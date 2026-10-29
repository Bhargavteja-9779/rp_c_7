"""Analysis-only numbers used in the v4 text (previously computed ad hoc): (1) rank-32 POD projection floor vs POD+GP at N=1024 (seed 0 subset);
(2) Exp D ratio restricted to the N in {64,256,1024} cells (comparable to Exp E/H); (3) budget-to-accuracy counts excluding the 8 A2 candidates; (4) share of p<=4 problems where the reduced basis is clear at N=1024."""
import sys, json, glob, pathlib, numpy as np, pandas as pd
ROOT = pathlib.Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT / "code/src"))
from surrogate_bench import methods as M
from surrogate_bench.problems import build_suite
from surrogate_bench.data import build_dataset, POOL
out = {"pod_floor": {}}
for name in ["heat2d_L2", "incl_L1", "incl_L2", "transport_L2"]:
    P = build_suite()[name]; d = build_dataset(P, str(ROOT / "code/data_cache")); perm = np.random.default_rng(1000).permutation(POOL)[:1024]
    pod = M.POD(d["u_train"][perm], 32); U = d["u_test"]; Uh = pod.decode(pod.encode(U)); floor = float(np.mean(np.linalg.norm(U - Uh, axis=1) / np.linalg.norm(U, axis=1)))
    f = glob.glob(str(ROOT / f"results/raw_expA/{name}__s0.json")) or glob.glob(str(ROOT.parent / f"results/raw/{name}__s0.json")); recs = json.load(open(f[0]))["records"]
    r = {x["method"]: x["test_err"] for x in recs if x["N"] == 1024}; out["pod_floor"][name] = dict(r32_projection_error=floor, pod_gp=r["pod_gp"], mlp_direct=r["mlp_direct"], bottleneck=r["bottleneck"])
dc = pd.read_csv(ROOT / "results/expA_primary/tables/expD_cells.csv"); s = dc[(dc.y_gp > 0.1) & dc.N.isin([64, 256, 1024])]
out["expD_on_comparable_cells"] = dict(n=int(len(s)), median_ratio_krr_over_gp=float(s.ratio_krr_gp.median()), share_le3=float((s.ratio_krr_gp <= 3).mean()))
bt = pd.read_csv(ROOT / "results/budget_to_accuracy.csv"); main = bt[~bt.instance.str.match(r"^(reacdiff|helm|heatp|diff1d)")]
out["budget_excl_A2_candidates"] = dict(n=int(len(main)), **{f"{k}_{t}": int(main[f"{k}_{t}"].notna().sum()) for t in ("0.1", "0.01", "0.001") for k in ("ls", "nl")})
c = pd.concat([pd.read_csv(ROOT / "results/expA_primary/tables/pooled_cells.csv")[["instance", "p", "N", "y"]], pd.read_csv(ROOT / "results/expA_primary/tables/expA2_cells.csv")[["instance", "p", "N", "y"]], pd.read_csv(ROOT / "results/expA_primary/tables/expA3_cells.csv")[["instance", "p", "N", "y"]]])
m24 = bt[~bt.instance.str.match(r"^(reacdiff|helm|heatp|diff1d|darcylin|heatmv3|incl3)")]
out["budget_main24"] = dict(n=int(len(m24)), **{f"{k}_{t}": int(m24[f"{k}_{t}"].notna().sum()) for t in ("0.1", "0.01", "0.001") for k in ("ls", "nl")})
lo = c[(c.N == 1024) & (c.p <= 4)]; out["p_le4_n1024"] = dict(n=int(len(lo)), ls_clear=int((lo.y > .1).sum()), tie=int((lo.y.abs() <= .1).sum()), nl_clear=int((lo.y < -.1).sum()))
lo2 = lo[~lo.instance.str.match(r"^(reacdiff|helm|heatp|diff1d)")]; out["p_le4_excl_a2"] = dict(n=int(len(lo2)), ls_clear=int((lo2.y > .1).sum()), tie=int((lo2.y.abs() <= .1).sum()), nl_clear=int((lo2.y < -.1).sum()))
hi = c[(c.N == 1024) & (c.p >= 10)]; out["p_ge10_n1024"] = {r.instance: round(r.y, 2) for r in hi.itertuples()}
(ROOT / "results/pod_floor_check_and_extras.json").write_text(json.dumps(out, indent=1)); print(json.dumps(out, indent=1))
