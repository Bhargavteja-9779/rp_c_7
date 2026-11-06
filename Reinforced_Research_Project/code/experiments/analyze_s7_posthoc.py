#!/usr/bin/env python3
"""POST HOC analyses of Stage 7, added after simulated review 04 (not in addendum v3.2; labelled post hoc in the paper). Reads stored outputs only.
1 B2 carry-forward baseline (predict 'reached' iff the cross-validated error at N0 = 256 is already below the target)   2 H1a/H1c without the two Helmholtz problems
3 per-job worst regret and the error levels on the Helmholtz problems   4 E7: tool time without the evaluation-only refit_all, best fixed member, direction of the forecast error   5 how often the network is selected and where it changes the result."""
import json, glob, pathlib, sys, numpy as np, pandas as pd
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent)); import analyze_s6 as A6
R = A6.R; OUT = R / "s7"; gm = lambda v: float(np.exp(np.mean(np.log(np.asarray(v, float)))))


def recs(dirs):
    out = []
    for d in dirs:
        for f in sorted(glob.glob(str(R / d / "*__s*.json"))):
            m = json.load(open(f))
            for r in m["records"]: out.append((m["instance"], m["seed"], r))
    return out


def carry_forward(dirs):
    by = {}
    for inst, seed, r in recs(dirs): by[(inst, seed, r["N"])] = r
    res = {}
    for thr, nm in ((0.01, "one_pct"), (0.001, "tenth_pct")):
        ok = []; act = []
        for (inst, seed, N), r in by.items():
            if N != 256 or (inst, seed, 1024) not in by: continue
            cv0 = r["cv_table"][0]["cv_error"]; actual = by[(inst, seed, 1024)]["test_err"][r["selected"]] <= thr; pred = cv0 <= thr; ok.append(pred == actual); act.append(actual)
        res[nm] = dict(n=len(ok), carry_forward_accuracy=float(np.mean(ok)), majority_baseline=float(max(np.mean(act), 1 - np.mean(act))))
    return res


def main():
    out = {}
    out["carry_forward_heldout"] = carry_forward(["raw_exp7C"]); out["carry_forward_pooled"] = carry_forward(["raw_exp6C", "raw_exp7C"])
    sc = pd.read_csv(OUT / "S1_cells.csv"); nh = sc[~sc.instance.str.startswith("helmholtz")]
    out["without_helmholtz"] = dict(n_cells=int(len(nh)), s1_median=float(nh.regret.median()), s1_max=float(nh.regret.max()), s1_share_le2=float((nh.regret <= 2).mean()), s3_median=float(nh.r_leg.median()), s3_better=int((nh.r_leg < 1 / 1.1).sum()), s3_worse=int((nh.r_leg > 1.1).sum()),
                                    s2_median=float(nh.r_gp.median()))
    h = sc[sc.instance.str.startswith("helmholtz")]; out["helmholtz_best_member_error"] = dict(L1=[float(x) for x in h[h.instance == "helmholtz_L1"].orc], L2=[float(x) for x in h[h.instance == "helmholtz_L2"].orc],
                                                                                         min_all=float(h.orc.min()), max_all=float(h.orc.max()), n_cells_best_error_ge_half=int((h.orc >= 0.5).sum()), n_cells=int(len(h)))
    C = pd.read_pickle(OUT / "C_records.pkl"); jr = (C.err_sel / C.err_oracle); out["worst_job_regret"] = dict(value=float(jr.max()), where=f"{C.loc[jr.idxmax(), 'instance']} N={int(C.loc[jr.idxmax(), 'N'])} seed {int(C.loc[jr.idxmax(), 'seed'])}", n_jobs_regret_gt2=int((jr > 2).sum()), n_jobs=int(len(jr)))
    # E7
    E = [json.load(open(f)) for f in sorted(glob.glob(str(R / "raw_exp7E/*__s*.json")))]; t_sim = E[0]["t_sim"]; cost = {}
    for k, N in ((0, 64), (1, 256)):
        t_cv = [sum(r["seconds"] for r in m["records"][k]["cv_table"]) + (m["records"][k]["seconds_total"] - m["records"][k]["seconds_fit"]) for m in E]
        t_all = [m["records"][k]["seconds_total"] for m in E]; err = gm([m["records"][k]["test_err"][m["records"][k]["selected"]] for m in E])
        cost[str(N)] = dict(tool_seconds_with_refit=float(np.median(t_all)), tool_seconds_without_refit=float(np.median(t_cv)), break_even_without_refit=float(N + np.median(t_cv) / t_sim), break_even_with_refit=float(N + np.median(t_all) / t_sim), error_at_N=err)
    fixed = {}
    for m in E:
        for k, v in m["records"][1]["test_err"].items(): fixed.setdefault(k, []).append(v)
    bf = min(fixed, key=lambda k: gm(fixed[k])); oracle_by_seed = [min(m["records"][1]["test_err"], key=m["records"][1]["test_err"].get) for m in E]
    out["e7"] = dict(cost=cost, best_fixed_member_256=bf, best_fixed_error_256=gm(fixed[bf]), oracle_by_seed_256=oracle_by_seed, tool_error_256=gm([m["records"][1]["test_err"][m["records"][1]["selected"]] for m in E]),
                     forecast_ratio_all_gt1=bool(all(m["records"][0]["pred_err_4N"]["256"][0] / m["records"][1]["test_err"][m["records"][0]["selected"]] > 1 for m in E if m["records"][0]["selected"] in m["records"][1]["test_err"])))
    # network in the pool: where selected, where the result changed
    N7 = recs(["raw_exp7N"]); out["network_pool"] = dict(n_jobs=len(N7), n_selected=int(sum(r["selected"] == "tuned_mlp" for _, _, r in N7)), cells_with_selection={i: int(sum(1 for ii, _, r in N7 if ii == i and r["selected"] == "tuned_mlp")) for i in sorted({i for i, _, _ in N7})})
    json.dump(out, open(OUT / "posthoc.json", "w"), indent=1, default=float); print(json.dumps(out, indent=1, default=float))


if __name__ == "__main__": main()
