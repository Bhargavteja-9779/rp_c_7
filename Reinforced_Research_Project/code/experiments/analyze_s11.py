#!/usr/bin/env python3
"""Stage 11 analysis (research_design/protocol_addendum_v3.6.md; criteria fixed BEFORE the runs): old pool (7 members) vs new pool (+ PoleDeflated), plain and pole-deflated tuned networks, no-harm on 52 earlier problems -> results/s11/*.json"""
import json, glob, pathlib, numpy as np, pandas as pd
ROOT = pathlib.Path(__file__).resolve().parents[2]; R = ROOT / "results"; OUT = R / "s11"; OUT.mkdir(exist_ok=True)
NEWM = "deflated[pod_gp[rbf,r=32]]"; gm = lambda v: float(np.exp(np.mean(np.log(np.maximum(np.asarray(v, float), 1e-300)))))
RNG = np.random.default_rng(0)


def load(dirname):
    rows = []
    for f in sorted(glob.glob(str(R / dirname / "*__s*.json"))):
        m = json.load(open(f))
        for r in m["records"]:
            cv = {t["name"]: t["cv_error"] for t in r["cv_table"] if np.isfinite(t["cv_error"])}; old = {k: v for k, v in cv.items() if k != NEWM}; te = r["test_err"]; sn, so = r["selected"], min(old, key=old.get)
            rows.append(dict(instance=m["instance"], seed=m["seed"], N=r["N"], sel_new=sn, sel_old=so, err_new=te[sn], err_old=te[so], err_oracle=min(te.values()), err_def=te.get(NEWM, np.nan), seconds_def=next((t["seconds"] for t in r["cv_table"] if t["name"] == NEWM), np.nan), seconds_all=sum(t["seconds"] for t in r["cv_table"])))
    return pd.DataFrame(rows)


def cells(D): return D.groupby(["instance", "N"]).apply(lambda g: pd.Series(dict(new=gm(g.err_new), old=gm(g.err_old), orc=gm(g.err_oracle), dfl=gm(g.err_def.dropna()) if g.err_def.notna().any() else np.nan, n_sel_def=int((g.sel_new == NEWM).sum())))).reset_index()


def netcells(dirname, col):
    rows = []
    for f in sorted(glob.glob(str(R / dirname / "*__s*.json"))):
        m = json.load(open(f)); rows += [dict(instance=m["instance"], seed=m["seed"], N=r["N"], e=r["test_err"], chosen=r.get("chosen")) for r in m["records"]]
    return pd.DataFrame(rows).groupby(["instance", "N"]).agg(e=("e", gm), n_defl=("chosen", lambda x: int(sum(v == "deflated" for v in x)))).rename(columns={"e": col, "n_defl": col + "_n_defl"}).reset_index() if rows else None


def ci(x, f=np.median, B=2000): x = np.asarray(x, float); return [float(v) for v in np.percentile([f(RNG.choice(x, len(x))) for _ in range(B)], [2.5, 97.5])]


def main():
    out = {}; F = load("raw_exp11F")
    if len(F):
        C = cells(F); C["ratio"] = C.new / C.old; C["regret"] = C.new / C.orc; big = C[C.N >= 256]
        out["D1"] = dict(n_cells=len(big), n_half=int((big.ratio <= 0.5).sum()), met=bool((big.ratio <= 0.5).sum() >= 4)); out["D2"] = dict(n_cells=len(C), n_worse10=int((C.ratio > 1.1).sum()), met=bool((C.ratio > 1.1).sum() <= 1))
        out["D3"] = dict(median_regret=float(C.regret.median()), share_le2=float((C.regret <= 2).mean()), met=bool(C.regret.median() <= 1.5 and (C.regret <= 2).mean() >= 0.75))
        out["D4"] = dict(n_cells=len(big), usable_new=int((big.new <= 0.25).sum()), usable_old=int((big.old <= 0.25).sum()), met=bool((big.new <= 0.25).sum() >= 6 and (big.new <= 0.25).sum() - (big.old <= 0.25).sum() >= 2))
        S, Dn = netcells("raw_exp11S", "net"), netcells("raw_exp11D", "dnet")
        if S is not None and Dn is not None:
            Q = big.merge(S, on=["instance", "N"]).merge(Dn, on=["instance", "N"]); out["D5"] = dict(n_cells=len(Q), dnet_better25=int((Q.dnet < Q.net / 1.25).sum()), dnet_worse25=int((Q.dnet > 1.25 * Q.net).sum()), met=bool((Q.dnet < Q.net / 1.25).sum() >= 3 and (Q.dnet > 1.25 * Q.net).sum() <= 2))
            out["D6"] = dict(n_cells=len(Q), usable_best=int((np.minimum.reduce([Q.new, Q.net, Q.dnet]) <= 0.25).sum()), usable_old_tools=int((np.minimum(Q.old, Q.net) <= 0.25).sum()), met=bool((np.minimum.reduce([Q.new, Q.net, Q.dnet]) <= 0.25).sum() >= 6))
            out["D7"] = dict(n_cells=len(Q), net_better25=int((Q.net < Q.new / 1.25).sum()), met=bool((Q.net < Q.new / 1.25).sum() <= 3)); Q.to_csv(OUT / "F_cells_with_nets.csv", index=False)
        out["D9_F"] = dict(per_cell={f"{r.instance}@{int(r.N)}": dict(new=r.new, old=r.old, orc=r.orc, dfl=r.dfl, sel_def=int(r.n_sel_def)) for r in C.itertuples()}, median_def_seconds_share=float((F.seconds_def / F.seconds_all).median()), median_def_seconds_N1024=float(F[F.N == 1024].seconds_def.median()))
        C.to_csv(OUT / "F_cells.csv", index=False)
    H = load("raw_exp11H")
    if len(H):
        C = cells(H); C["ratio"] = C.new / C.old; out["D8"] = dict(n_problems=len(C), median_ratio=float(C.ratio.median()), median_ci=ci(C.ratio), n_worse10=int((C.ratio > 1.1).sum()), met=bool(C.ratio.median() <= 1.03 and (C.ratio > 1.1).sum() <= 5))
        out["D9_H"] = dict(n_better25=int((C.ratio < 0.8).sum()), better_instances=sorted(C[C.ratio < 0.8].instance), worse_instances=sorted(C[C.ratio > 1.1].instance), selected_instances=sorted(C[C.n_sel_def > 0].instance)); C.to_csv(OUT / "H_cells.csv", index=False)
    json.dump(out, open(OUT / "criteria.json", "w"), indent=1, default=float); print(json.dumps({k: v for k, v in out.items() if k != "D9_F"}, indent=1, default=float))


if __name__ == "__main__": main()
