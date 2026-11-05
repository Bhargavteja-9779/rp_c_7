#!/usr/bin/env python3
"""Stage 7 analysis (research_design/protocol_addendum_v3.2.md; criteria fixed BEFORE the runs).
1. the 8 new problems alone (held-out confirmation): the Stage 6 analysis code, unchanged, pointed at raw_exp7T/7C/7S -> results/s7
2. pooled over the 16 third-party problems (descriptive)                                                              -> results/s7_pooled
3. W1/W2 (tool + network, N7), S5 (stronger network, SP), E1 + cost numbers (expensive solver, E7)                         -> results/s7/{W.json,S5.json,E7.json}"""
import json, glob, pathlib, sys, numpy as np, pandas as pd
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent)); import analyze_s6 as A6
R = A6.R; OUT = R / "s7"; OUT.mkdir(exist_ok=True); wilson = A6.wilson
gm = lambda v: float(np.exp(np.mean(np.log(np.asarray(v, float)))))


def recs(dirpath):
    out = []
    for f in sorted(glob.glob(str(pathlib.Path(dirpath) / "*__s*.json"))):
        m = json.load(open(f))
        for r in m["records"]: out.append((m["instance"], m["seed"], r))
    return out


def cellgm(rows, key):                                  # {(instance, N): geometric mean over seeds of key(record)}
    d = {}
    for inst, seed, r in rows: d.setdefault((inst, r["N"]), []).append(key(r))
    return {k: gm(v) for k, v in d.items()}


def part_w():
    N7 = recs(R / "raw_exp7N")
    if not N7: return None
    sel = cellgm(N7, lambda r: r["test_err"][r["selected"]]); orc = cellgm(N7, lambda r: min(r["test_err"].values())); net = cellgm(N7, lambda r: r["test_err"].get("tuned_mlp", np.inf))
    sel_net = cellgm(N7, lambda r: 1.0 if r["selected"] == "tuned_mlp" else 1e-9)
    reg = {k: sel[k] / orc[k] for k in sel}; C7 = cellgm(recs(R / "raw_exp7C"), lambda r: r["test_err"][r["selected"]]); S7 = cellgm(recs(R / "raw_exp7S"), lambda r: r["test_err"])
    W1 = dict(n_cells=len(reg), median_regret=float(np.median(list(reg.values()))), max_regret=float(max(reg.values())), share_le2=float(np.mean(np.array(list(reg.values())) <= 2)), wilson_le2=wilson(int(sum(v <= 2 for v in reg.values())), len(reg)))
    W1["criterion_met"] = bool(W1["median_regret"] <= 1.5 and W1["share_le2"] >= .75)
    ok = {k: sel[k] <= 1.1 * min(C7[k], S7[k]) for k in sel if k in C7 and k in S7}; W2 = dict(n_cells=len(ok), n_ok=int(sum(ok.values())), criterion_met=bool(sum(ok.values()) >= 6), wilson=wilson(int(sum(ok.values())), len(ok)))
    n_sel_net = int(sum(1 for _, _, r in N7 if r["selected"] == "tuned_mlp")); n_net_best = int(sum(1 for _, _, r in N7 if min(r["test_err"], key=r["test_err"].get) == "tuned_mlp"))
    per_cell = {f"{k[0]}": dict(tool_plus_net=sel[k], tool_alone=C7.get(k), net_alone=S7.get(k), net_in_N7_refit=net[k], oracle=orc[k]) for k in sel}
    sec = [r["seconds_fit"] for _, _, r in N7]; out = dict(W1=W1, W2=W2, n_jobs_selecting_network=n_sel_net, n_jobs_network_is_oracle=n_net_best, n_jobs=len(N7), median_fit_seconds=float(np.median(sec)), per_cell=per_cell)
    json.dump(out, open(OUT / "W.json", "w"), indent=1, default=float); return out


def part_s5():
    SP = recs(R / "raw_exp7SP")
    if not SP: return None
    tool = {**cellgm(recs(R / "raw_exp6C"), lambda r: r["test_err"][r["selected"]]), **cellgm(recs(R / "raw_exp7C"), lambda r: r["test_err"][r["selected"]])}
    S = {**cellgm(recs(R / "raw_exp6S"), lambda r: r["test_err"]), **cellgm(recs(R / "raw_exp7S"), lambda r: r["test_err"])}; SPc = cellgm(SP, lambda r: r["test_err"])
    ks = sorted(k for k in SPc if k in tool and k in S)
    win = lambda e: int(sum(tool[k] / e[k] > 1.25 for k in ks)); ratio = [SPc[k] / S[k] for k in ks]
    out = dict(n_cells=len(ks), n_better_than_tool_by_25pct_standard=win(S), n_better_than_tool_by_25pct_stronger=win(SPc), median_ratio_stronger_over_standard=float(np.median(ratio)), n_stronger_better_than_standard=int(sum(r < 1 for r in ratio)),
               n_stronger_better_by_10pct_than_standard=int(sum(r < 1 / 1.1 for r in ratio)), median_ratio_tool_over_stronger=float(np.median([tool[k] / SPc[k] for k in ks])), median_ratio_tool_over_standard=float(np.median([tool[k] / S[k] for k in ks])),
               stronger_wins=sorted(k[0] for k in ks if tool[k] / SPc[k] > 1.25), standard_wins=sorted(k[0] for k in ks if tool[k] / S[k] > 1.25), median_seconds_stronger=float(np.median([r["seconds"] for _, _, r in SP])),
               per_problem={k[0]: dict(tool=tool[k], standard=S[k], stronger=SPc[k]) for k in ks})
    json.dump(out, open(OUT / "S5.json", "w"), indent=1, default=float); return out


def part_e1():
    fs = sorted(glob.glob(str(R / "raw_exp7E/*__s*.json")))
    if not fs: return None
    J = [json.load(open(f)) for f in fs]; t_sim = J[0]["t_sim"]; rows = []
    for m in J:
        r64, r256 = m["records"]; sel = lambda r: r["test_err"][r["selected"]]; orc = lambda r: min(r["test_err"].values()); name = r64["selected"]; pred = r64["pred_err_4N"]["256"][0]; act = r256["test_err"].get(name, np.nan)
        rows.append(dict(seed=m["seed"], regret64=sel(r64) / orc(r64), regret256=sel(r256) / orc(r256), err_sel64=sel(r64), err_sel256=sel(r256), err_gp64=r64["test_err"]["pod_gp[matern52,r=32]"], err_gp256=r256["test_err"]["pod_gp[matern52,r=32]"],
                         err_net256=r256["network"]["test_err"], sec_net256=r256["network"]["seconds"], sel64=r64["selected"], sel256=r256["selected"], fc_pred=pred, fc_actual=act, fc_ratio=pred / act, fc_ok=abs(np.log10(pred / act)) <= np.log10(2),
                         tool_sec64=r64["seconds_total"], tool_sec256=r256["seconds_total"], basis_limited256=r256["floor"]["basis_limited"], rn1=r256.get("runs_needed_1pct")))
    D = pd.DataFrame(rows)
    E1 = dict(regret64_mean=float(D.regret64.mean()), regret256_mean=float(D.regret256.mean()), regret_ok=bool(gm(D.regret64) <= 2 and gm(D.regret256) <= 2), n_forecast_ok=int(D.fc_ok.sum()), n_seeds=len(D), forecast_ok=bool(D.fc_ok.sum() >= 2))
    E1["criterion_met"] = bool(E1["regret_ok"] and E1["forecast_ok"])
    cost = {}
    for N, col in ((64, "tool_sec64"), (256, "tool_sec256")):
        tt = float(D[col].median()); cost[N] = dict(sim_hours=N * t_sim / 3600, tool_seconds=tt, break_even_queries=(N * t_sim + tt) / t_sim, solver_hours_for_1e4_queries=1e4 * t_sim / 3600, surrogate_hours_for_1e4_queries=(N * t_sim + tt) / 3600)
    out = dict(t_sim_seconds=t_sim, E1=E1, cost=cost, geo_err_tool=dict(N64=gm(D.err_sel64), N256=gm(D.err_sel256)), geo_err_gp=dict(N64=gm(D.err_gp64), N256=gm(D.err_gp256)), geo_err_net256=gm(D.err_net256), median_network_seconds=float(D.sec_net256.median()), per_seed=D.to_dict("records"))
    json.dump(out, open(OUT / "E7.json", "w"), indent=1, default=float); return out


if __name__ == "__main__":
    A6.configure([R / "raw_exp7T"], [R / "raw_exp7C"], [R / "raw_exp7S"], R / "s7"); A6.main()
    A6.configure([R / "raw_exp6T", R / "raw_exp7T"], [R / "raw_exp6C", R / "raw_exp7C"], [R / "raw_exp6S", R / "raw_exp7S"], R / "s7_pooled"); A6.main()
    for f in (part_w, part_s5, part_e1): print(f.__name__, json.dumps(f(), indent=1, default=float)[:1500] if True else "")
