#!/usr/bin/env python3
"""Stage 9 analysis (research_design/protocol_addendum_v3.4.md; forecasters and criteria fixed BEFORE any fit).
Reads results/raw_exp9L; development = leave-one-family-out over the 44-problem suite; held-out = frozen forecasters on the held-out problems -> results/s9/*.json, cases.csv, calibration_v1.json"""
import json, glob, pathlib, sys, numpy as np, pandas as pd
from sklearn.linear_model import Ridge
ROOT = pathlib.Path(__file__).resolve().parents[2]; R = ROOT / "results"; OUT = R / "s9"; OUT.mkdir(exist_ok=True)
LOG2 = np.log10(2.0); FEATS = ["log2h", "logN0", "b3", "b4", "curv", "nonmono", "loge4", "p", "logm", "floorratio"]


def power_law(n, e, use=3):                      # identical to surroselect.select._power_law, on log10 scale: log10 e = a - b log10 n
    n, e = np.asarray(n, float)[-use:], np.asarray(e, float)[-use:]; A = np.c_[np.ones(len(n)), -np.log10(n)]; coef, *_ = np.linalg.lstsq(A, np.log10(np.maximum(e, 1e-300)), rcond=None); return float(coef[0]), float(coef[1])


def load_cases():
    rows = []
    for f in sorted(glob.glob(str(R / "raw_exp9L/*__s*.json"))):
        m = json.load(open(f))
        for r in m["records"]:
            n, e = np.array(r["curve"]["n"], float), np.maximum(np.array(r["curve"]["error"], float), 1e-12); a, b = power_law(n, e); un, inv = np.unique(n, return_inverse=True); le = np.array([np.log10(e)[inv == k].mean() for k in range(len(un))]); ls = np.diff(le) / np.diff(np.log10(un)) if len(un) > 1 else np.zeros(1); fl = max(r["pod_floor_cv"], 1e-12)   # points with identical n (N0 = 64: the minimum training size of 12 is reached twice) are merged for slopes and curvature
            for h in (2, 4):
                act = r["actual"].get(str(h))
                if act is None or not np.isfinite(act) or act <= 0: continue
                N = h * r["N0"]; lf0 = a - b * np.log10(N); last_fit = a - b * np.log10(n[-1])
                rows.append(dict(split=m["split"], instance=m["instance"], family=m["family"], seed=m["seed"], N0=r["N0"], h=h, y=np.log10(act), lf0=lf0, loge4=np.log10(e[-1]), last_fit=last_fit, lastlogn=np.log10(n[-1]), logN=np.log10(N),
                                 log2h=np.log2(h), logN0=np.log10(r["N0"]), b3=-b, b4=(np.polyfit(np.log10(un), le, 1)[0] if len(un) > 1 else 0.0), curv=(ls[-1] - ls[0]), nonmono=float(np.any(np.diff(e) > 0)), p=m["p"], logm=np.log10(m["m"]),
                                 floorratio=float(np.clip(np.log10(max(r["best_cv_error"], 1e-12) / fl), -2, 6))))
    D = pd.DataFrame(rows); D["r"] = D.y - D.lf0; return D


class Ridge1:
    def fit(self, Z, t): self.mu, self.sd = Z.mean(0), Z.std(0) + 1e-9; self.m = Ridge(alpha=1.0).fit((Z - self.mu) / self.sd, t); return self
    def predict(self, Z): return self.m.predict((Z - self.mu) / self.sd)


def conf_q(res, alpha): n = len(res); k = int(np.ceil((n + 1) * (1 - alpha))); return float(np.sort(res)[min(k, n) - 1])


def crossfit(T, fn):
    """leave-one-family-out inside T: returns out-of-family predictions for every row of T"""
    out = np.zeros(len(T))
    for fam in T.family.unique():
        tr, te = T[T.family != fam], T[T.family == fam]
        if len(tr) == 0: continue
        out[(T.family == fam).values] = fn(tr, te)
    return out


def fit_forecasters(T):
    """fit all forecasters on training cases T; returns an object with predict(V) -> dict of (yhat, q80, q90) per forecaster"""
    P = {}; Z = T[FEATS].values
    mean_r = {h: T[T.h == h].r.mean() for h in (2, 4)}
    gfit = lambda tr, te: Ridge1().fit(tr[FEATS].values, tr.r.values).predict(te[FEATS].values)
    res_cf = T.r.values - crossfit(T, gfit)                                   # cross-fitted residuals of F3
    g = Ridge1().fit(Z, T.r.values); P["g"] = g
    P["q3"] = {a: conf_q(np.abs(res_cf), a) for a in (0.2, 0.1)}
    # F4: normalised conformal
    sfit = lambda tr, te: Ridge1().fit(tr[FEATS].values, np.log(np.abs(res_cf[tr.index.map(T.index.get_loc)]) + 1e-3)).predict(te[FEATS].values)
    s_cf = np.exp(crossfit(T, sfit)); sc_cf = np.abs(res_cf) / s_cf; P["s"] = Ridge1().fit(Z, np.log(np.abs(res_cf) + 1e-3)); P["q4"] = {a: conf_q(sc_cf, a) for a in (0.2, 0.1)}
    # F2: constant correction + constant width
    r2 = T.r.values - np.array([T[(T.family != fam) & (T.h == h)].r.mean() for fam, h in zip(T.family, T.h)]); P["q2"] = {a: conf_q(np.abs(r2), a) for a in (0.2, 0.1)}; P["mean_r"] = mean_r
    # F1: shrunk slope, lambda by leave-one-family-out
    P["bbar"] = {N0: T[T.N0 == N0].b3.mean() for N0 in T.N0.unique()}
    def f1(V, lam): sl = (1 - lam) * V.b3.values + lam * np.array([P["bbar"].get(n0, V.b3.mean()) for n0 in V.N0]); return V.last_fit.values + sl * (V.logN.values - V.lastlogn.values)
    best, bl = np.inf, 0.0
    for lam in (0, 0.25, 0.5, 0.75, 1.0):
        e = []
        for fam in T.family.unique():
            tr, te = T[T.family != fam], T[T.family == fam]; bb = {N0: tr[tr.N0 == N0].b3.mean() for N0 in tr.N0.unique()}
            sl = (1 - lam) * te.b3.values + lam * np.array([bb.get(n0, tr.b3.mean()) for n0 in te.N0]); e += list(np.abs(te.y.values - (te.last_fit.values + sl * (te.logN.values - te.lastlogn.values))))
        if np.median(e) < best: best, bl = np.median(e), lam
    P["lam"] = bl; P["f1"] = f1
    return P


def predict_all(P, V):
    out = {}; yh0 = V.lf0.values; g = P["g"].predict(V[FEATS].values); s = np.exp(P["s"].predict(V[FEATS].values))
    out["F0"] = (yh0, None, None); out["F5"] = (V.loge4.values, None, None)
    c2 = yh0 + np.array([P["mean_r"][h] for h in V.h]); out["F2"] = (c2, np.full(len(V), P["q2"][0.2]), np.full(len(V), P["q2"][0.1]))
    out["F1"] = (P["f1"](V, P["lam"]), None, None)
    c3 = yh0 + g; out["F3"] = (c3, np.full(len(V), P["q3"][0.2]), np.full(len(V), P["q3"][0.1])); out["F4"] = (c3, P["q4"][0.2] * s, P["q4"][0.1] * s)
    return out


def metrics(V, pred):
    res = {}
    for k, (yh, q80, q90) in pred.items():
        e = np.abs(V.y.values - yh); d = dict(share2=float((e <= LOG2).mean()), med_abs=float(np.median(e)), bias=float(np.median(V.y.values - yh)), n=int(len(V)))
        if q80 is not None: d.update(cov80=float((e <= q80).mean()), cov90=float((e <= q90).mean()), width80=float(np.median(2 * q80)), width90=float(np.median(2 * q90)))
        res[k] = d
    return res


def cluster_boot(V, pred, fn, B=2000, seed=0):
    rs = np.random.default_rng(seed); inst = V.instance.values; names = np.unique(inst); idx = {n: np.where(inst == n)[0] for n in names}; vals = []
    for _ in range(B):
        pick = rs.choice(names, len(names)); ii = np.concatenate([idx[n] for n in pick]); vals.append(fn(V.iloc[ii], {k: tuple(None if a is None else a[ii] for a in v) for k, v in pred.items()}))
    return [float(x) for x in np.nanpercentile(vals, [2.5, 97.5])]


def k5(V, pred, thr):
    yh, q80, _ = pred["F3"]; sel = (yh + q80) <= np.log10(thr); n = int(sel.sum()); return dict(n_confident=n, share_reached=(float((V.y.values[sel] <= np.log10(thr)).mean()) if n else None), evaluable=bool(n >= 10))


def main():
    D = load_cases()
    if D.empty: print("no data"); return
    dev, held = D[D.split == "dev"].reset_index(drop=True), D[D.split == "held"].reset_index(drop=True)
    # ---------------- development: leave-one-family-out
    parts = []; preds = {k: np.zeros(len(dev)) for k in ("F0", "F5", "F1", "F2", "F3", "F4")}; q = {k: np.zeros(len(dev)) for k in ("F2q80", "F2q90", "F3q80", "F3q90", "F4q80", "F4q90")}
    for fam in dev.family.unique():
        tr, te = dev[dev.family != fam].reset_index(drop=True), dev[dev.family == fam]; P = fit_forecasters(tr); pr = predict_all(P, te.reset_index(drop=True)); ii = te.index.values
        for k in preds: preds[k][ii] = pr[k][0]
        for k in ("F2", "F3", "F4"): q[k + "q80"][ii] = pr[k][1]; q[k + "q90"][ii] = pr[k][2]
    pd_ = {k: (preds[k], q.get(k + "q80"), q.get(k + "q90")) if k in ("F2", "F3", "F4") else (preds[k], None, None) for k in preds}
    lofo = metrics(dev, pd_); json.dump(dict(n_cases=len(dev), n_problems=int(dev.instance.nunique()), n_families=int(dev.family.nunique()), metrics=lofo), open(OUT / "lofo.json", "w"), indent=1)
    # ---------------- final: fit on all development cases, freeze, apply once to the held-out set
    P = fit_forecasters(dev); pr = predict_all(P, held); hm = metrics(held, pr)
    cal = dict(features=FEATS, g_mu=P["g"].mu.tolist(), g_sd=P["g"].sd.tolist(), g_coef=P["g"].m.coef_.tolist(), g_intercept=float(P["g"].m.intercept_), q3=P["q3"], q2=P["q2"], q4=P["q4"], mean_r=P["mean_r"], lam=P["lam"], n_dev_cases=len(dev), n_dev_problems=int(dev.instance.nunique()), version="1")
    json.dump(cal, open(OUT / "calibration_v1.json", "w"), indent=1)
    f0, f3, f2, f4 = (pr[k] for k in ("F0", "F3", "F2", "F4")); e0, e3, e2 = (np.abs(held.y.values - p[0]) for p in (f0, f3, f2))
    crit = dict(K1=dict(cov80=hm["F3"]["cov80"], met=bool(0.70 <= hm["F3"]["cov80"] <= 0.90), cov80_ci=cluster_boot(held, pr, lambda V, p: float((np.abs(V.y.values - p["F3"][0]) <= p["F3"][1]).mean()))),
                K2=dict(med_ratio=float(np.median(e3) / np.median(e0)), share_gain=float(hm["F3"]["share2"] - hm["F0"]["share2"]), met=bool(np.median(e3) <= 0.75 * np.median(e0) and hm["F3"]["share2"] - hm["F0"]["share2"] >= 0.10),
                        share_ci_f3=cluster_boot(held, pr, lambda V, p: float((np.abs(V.y.values - p["F3"][0]) <= LOG2).mean())), share_ci_f0=cluster_boot(held, pr, lambda V, p: float((np.abs(V.y.values - p["F0"][0]) <= LOG2).mean()))),
                K3=dict(share_f3=hm["F3"]["share2"], share_f2=hm["F2"]["share2"], width_f3=hm["F3"]["width80"], width_f4=hm["F4"]["width80"], width_f2=hm["F2"]["width80"], cov80_f4=hm["F4"]["cov80"], cov80_f2=hm["F2"]["cov80"]),
                K4=dict(width80=hm["F3"]["width80"], met=bool(hm["F3"]["width80"] <= 1.0)), K5={"one_pct": k5(held, pr, 0.01), "tenth_pct": k5(held, pr, 0.001)})
    crit["K3"]["met"] = bool(hm["F3"]["share2"] >= hm["F2"]["share2"] - 0.02 and min(hm["F3"]["width80"], hm["F4"]["width80"]) <= 0.9 * hm["F2"]["width80"])
    for t in crit["K5"].values(): t["met"] = bool(t["evaluable"] and t["share_reached"] is not None and t["share_reached"] >= 0.8)
    by = {}
    for (n0, h), g_ in held.groupby(["N0", "h"]): ii = g_.index.values; by[f"N0={n0},h={h}"] = metrics(g_, {k: tuple(None if a is None else a[ii] for a in v) for k, v in pr.items()})["F3"]
    json.dump(dict(n_cases=len(held), n_problems=int(held.instance.nunique()), metrics=hm, criteria=crit, F3_by_N0_h=by, lam=P["lam"]), open(OUT / "heldout.json", "w"), indent=1, default=float)
    held.assign(**{f"yhat_{k}": v[0] for k, v in pr.items()}, q80_F3=pr["F3"][1]).to_csv(OUT / "heldout_cases.csv", index=False); dev.assign(**{f"yhat_{k}": v[0] for k, v in pd_.items()}).to_csv(OUT / "dev_cases.csv", index=False)
    print("LOFO", json.dumps({k: {a: round(b, 3) for a, b in v.items()} for k, v in lofo.items()}, indent=0)); print("HELD", json.dumps(crit, indent=0, default=float)[:3000])


if __name__ == "__main__": main()
