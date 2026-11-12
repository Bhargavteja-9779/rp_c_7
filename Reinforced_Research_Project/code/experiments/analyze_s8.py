#!/usr/bin/env python3
"""Stage 8 analysis (protocol_addendum_v3.3.md; criteria fixed BEFORE the runs): E8 on the expensive 3D problem and the warning check U on the stored results of Stages 6 and 7 -> results/s8/*.json"""
import json, glob, pathlib, numpy as np
ROOT = pathlib.Path(__file__).resolve().parents[2]; R = ROOT / "results"; OUT = R / "s8"; OUT.mkdir(exist_ok=True)
gm = lambda v: float(np.exp(np.mean(np.log(np.asarray(v, float)))))


def e8():
    J = [json.load(open(f)) for f in sorted(glob.glob(str(R / "raw_exp8E/*__s*.json")))]
    if not J: return None
    t_sim = J[0]["t_sim"]; rows = []
    for m in J:
        r64, r256 = m["records"]; sel = lambda r: r["test_err"][r["selected"]]; orc = lambda r: min(r["test_err"].values()); name = r64["selected"]; pred = r64["pred_err_4N"]["256"][0]; act = r256["test_err"].get(name, np.nan)
        cvt = lambda r: sum(x["seconds"] for x in r["cv_table"]) + (r["seconds_total"] - r["seconds_fit"])
        rows.append(dict(seed=m["seed"], regret64=sel(r64) / orc(r64), regret256=sel(r256) / orc(r256), err64=sel(r64), err256=sel(r256), usable64=r64["usable"], usable256=r256["usable"], cv64=r64["best_cv_error"], cv256=r256["best_cv_error"],
                         err_gp256=r256["test_err"]["pod_gp[matern52,r=32]"], err_net256=r256["network"]["test_err"], net_better25=bool(r256["network"]["test_err"] < sel(r256) / 1.25), sec_net=r256["network"]["seconds"], sel64=r64["selected"], sel256=r256["selected"],
                         fc_pred=pred, fc_actual=act, fc_ratio=pred / act, fc_ok=bool(abs(np.log10(pred / act)) <= np.log10(2)), tool64=r64["seconds_total"], tool256=r256["seconds_total"], tool64_norefit=cvt(r64), tool256_norefit=cvt(r256), basis_limited256=r256["floor"]["basis_limited"]))
    D = rows; g = lambda k: [r[k] for r in D]
    c1 = bool(gm(g("regret64")) <= 2 and gm(g("regret256")) <= 2); c2 = bool(all(r["usable64"] and r["usable256"] for r in D) and gm(g("err64")) <= 0.25 and gm(g("err256")) <= 0.25 and max(g("err64") + g("err256")) <= 0.25 + 1e-12)
    c3 = bool(sum(g("fc_ok")) >= 2); c4 = bool(sum(g("net_better25")) <= 1)
    cost = {}
    for N, a, b in ((64, "tool64", "tool64_norefit"), (256, "tool256", "tool256_norefit")):
        for tag, k in (("with_refit", a), ("without_refit", b)):
            tt = float(np.median(g(k))); cost[f"{N}_{tag}"] = dict(tool_seconds=tt, break_even=(N * t_sim + tt) / t_sim, hours_surrogate_1e4=(N * t_sim + tt) / 3600)
    out = dict(t_sim_seconds=t_sim, E8_1=dict(met=c1, regret64=gm(g("regret64")), regret256=gm(g("regret256"))), E8_2=dict(met=c2, n_fits_warning=int(sum(not (r["usable64"] and r["usable256"]) for r in D)), err64=gm(g("err64")), err256=gm(g("err256"))),
               E8_3=dict(met=c3, n_ok=int(sum(g("fc_ok"))), n=len(D), ratios=g("fc_ratio")), E8_4=dict(met=c4, n_net_better=int(sum(g("net_better25"))), err_net256=gm(g("err_net256")), err_tool256=gm(g("err256")), err_gp256=gm(g("err_gp256"))),
               cost=cost, hours_solver_1e4=1e4 * t_sim / 3600, median_network_seconds=float(np.median(g("sec_net"))), selected=sorted(set(g("sel64") + g("sel256"))), per_seed=rows)
    json.dump(out, open(OUT / "E8.json", "w"), indent=1, default=float); return out


def u_check():
    rows = []
    for d in ("raw_exp6C", "raw_exp7C"):
        for f in sorted(glob.glob(str(R / d / "*__s*.json"))):
            m = json.load(open(f))
            for r in m["records"]:
                cv = {t["name"]: t["cv_error"] for t in r["cv_table"]}; best_cv = min(v for v in cv.values() if np.isfinite(v)); rows.append(dict(instance=m["instance"], seed=m["seed"], N=r["N"], warn=bool(best_cv > 0.25), unusable=bool(r["test_err"][r["selected"]] > 0.25), best_cv=best_cv, test_sel=r["test_err"][r["selected"]]))
    tp = sum(r["warn"] and r["unusable"] for r in rows); fn = sum((not r["warn"]) and r["unusable"] for r in rows); fp = sum(r["warn"] and not r["unusable"] for r in rows); tn = sum((not r["warn"]) and not r["unusable"] for r in rows)
    sens = tp / (tp + fn) if tp + fn else None; spec = tn / (tn + fp) if tn + fp else None
    out = dict(n_jobs=len(rows), tp=tp, fn=fn, fp=fp, tn=tn, sensitivity=sens, specificity=spec, criterion_met=bool(sens is not None and spec is not None and sens >= 0.9 and spec >= 0.9),
               warned_instances=sorted({r["instance"] for r in rows if r["warn"]}), unusable_instances=sorted({r["instance"] for r in rows if r["unusable"]}), design_informed=True)
    json.dump(out, open(OUT / "U.json", "w"), indent=1, default=float); return out


if __name__ == "__main__":
    print(json.dumps(u_check(), indent=1, default=float)); e = e8(); print(json.dumps({k: v for k, v in (e or {}).items() if k != "per_seed"}, indent=1, default=float))
