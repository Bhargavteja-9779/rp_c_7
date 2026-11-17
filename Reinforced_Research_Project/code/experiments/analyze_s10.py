#!/usr/bin/env python3
"""Stage 10 analysis (research_design/protocol_addendum_v3.5.md; criteria fixed BEFORE the runs): old pool (7 members) versus new pool (8 members incl. pod_rational) on the 4 frequency-response problems (F),
tuned network (S), and the no-harm check on 52 earlier problems (H) -> results/s10/*.json"""
import json, glob, pathlib, numpy as np, pandas as pd
ROOT = pathlib.Path(__file__).resolve().parents[2]; R = ROOT / "results"; OUT = R / "s10"; OUT.mkdir(exist_ok=True)
gm = lambda v: float(np.exp(np.mean(np.log(np.maximum(np.asarray(v, float), 1e-300)))))
RNG = np.random.default_rng(0)


def load(dirname):
    rows = []
    for f in sorted(glob.glob(str(R / dirname / "*__s*.json"))):
        m = json.load(open(f))
        for r in m["records"]:
            cv = {t["name"]: t["cv_error"] for t in r["cv_table"] if np.isfinite(t["cv_error"])}; old = {k: v for k, v in cv.items() if k != "pod_rational"}; te = r["test_err"]
            sel_new, sel_old = r["selected"], min(old, key=old.get); rows.append(dict(instance=m["instance"], seed=m["seed"], N=r["N"], sel_new=sel_new, sel_old=sel_old, err_new=te[sel_new], err_old=te[sel_old], err_oracle=min(te.values()), err_rat=te.get("pod_rational", np.nan),
                                                                                 cv_rat=cv.get("pod_rational", np.nan), seconds_rat=next((t["seconds"] for t in r["cv_table"] if t["name"] == "pod_rational"), np.nan), seconds_all=sum(t["seconds"] for t in r["cv_table"])))
    return pd.DataFrame(rows)


def cells(D): return D.groupby(["instance", "N"]).apply(lambda g: pd.Series(dict(new=gm(g.err_new), old=gm(g.err_old), orc=gm(g.err_oracle), rat=gm(g.err_rat.dropna()) if g.err_rat.notna().any() else np.nan, n_sel_rat=int((g.sel_new == "pod_rational").sum())))).reset_index()


def ci(x, f=np.median, B=2000): x = np.asarray(x, float); return [float(v) for v in np.percentile([f(RNG.choice(x, len(x))) for _ in range(B)], [2.5, 97.5])]


def main():
    out = {}; F = load("raw_exp10F")
    if len(F):
        C = cells(F); C["ratio"] = C.new / C.old; C["regret"] = C.new / C.orc; n = len(C)
        out["R1"] = dict(n_cells=n, n_half=int((C.ratio <= 0.5).sum()), met=bool((C.ratio <= 0.5).sum() >= 6)); out["R2"] = dict(n_worse10=int((C.ratio > 1.1).sum()), met=bool((C.ratio > 1.1).sum() <= 1))
        out["R3"] = dict(median_regret=float(C.regret.median()), share_le2=float((C.regret <= 2).mean()), met=bool(C.regret.median() <= 1.5 and (C.regret <= 2).mean() >= 0.75))
        big = C[C.N >= 256]; out["R5"] = dict(n_cells=len(big), usable_new=int((big.new <= 0.25).sum()), usable_old=int((big.old <= 0.25).sum()), met=bool((big.new <= 0.25).sum() >= 6 and (big.new <= 0.25).sum() - (big.old <= 0.25).sum() >= 2))
        S = []
        for f in sorted(glob.glob(str(R / "raw_exp10S/*__s*.json"))):
            m = json.load(open(f)); S += [dict(instance=m["instance"], seed=m["seed"], N=r["N"], err_net=r["test_err"]) for r in m["records"]]
        if S:
            Sd = pd.DataFrame(S).groupby(["instance", "N"]).err_net.apply(gm).rename("net").reset_index(); Q = C.merge(Sd, on=["instance", "N"]); nb = int((Q.net < Q.new / 1.25).sum()); out["R4"] = dict(n_cells=len(Q), net_better25=nb, met=bool(nb <= 3))
            Q.to_csv(OUT / "F_cells_with_net.csv", index=False)
        out["R7_F"] = dict(per_cell={f"{r.instance}@{int(r.N)}": dict(new=r.new, old=r.old, orc=r.orc, rat=r.rat, sel_rat=int(r.n_sel_rat)) for r in C.itertuples()}, median_ratio=float(C.ratio.median()), best_ratio=float(C.ratio.min()), worst_ratio=float(C.ratio.max()))
        C.to_csv(OUT / "F_cells.csv", index=False); out["R8_F"] = dict(median_rat_seconds_share=float((F.seconds_rat / F.seconds_all).median()), median_rat_seconds_N1024=float(F[F.N == 1024].seconds_rat.median()))
    H = load("raw_exp10H")
    if len(H):
        C = cells(H); C["ratio"] = C.new / C.old; n = len(C); out["R6"] = dict(n_problems=n, median_ratio=float(C.ratio.median()), median_ci=ci(C.ratio), n_worse10=int((C.ratio > 1.1).sum()), met=bool(C.ratio.median() <= 1.03 and (C.ratio > 1.1).sum() <= 5))
        out["R7_H"] = dict(n_better25=int((C.ratio < 0.8).sum()), better_instances=sorted(C[C.ratio < 0.8].instance), worse_instances=sorted(C[C.ratio > 1.1].instance), n_cells_rat_selected=int((C.n_sel_rat > 0).sum()), selected_instances=sorted(C[C.n_sel_rat > 0].instance)); C.to_csv(OUT / "H_cells.csv", index=False)
    json.dump(out, open(OUT / "criteria.json", "w"), indent=1, default=float); print(json.dumps({k: v for k, v in out.items() if k != "R7_F"}, indent=1, default=float))


if __name__ == "__main__": main()
