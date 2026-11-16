#!/usr/bin/env python3
"""POST HOC analysis of Stage 9 (not in addendum v3.4; labelled post hoc in the paper), added because the pre-specified calibrated forecaster F3 failed K2-K4: describe the error of the tool's RAW forecast F0 and give it an empirical interval.
Interval: +- q, q = the 80 % / 90 % quantile of |actual - forecast| (log10 scale) over the development cases of OTHER families (leave-one-family-out), then the frozen version (all development cases) on the held-out cases.
Also: how often a 'confident reach' statement (upper bound below the target) is right, and what share of true reaches it finds."""
import json, pathlib, sys, numpy as np, pandas as pd
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent)); import analyze_s9 as A
R = A.R; OUT = A.OUT; LOG2 = np.log10(2)


def main():
    D = A.load_cases(); dev, held = D[D.split == "dev"].reset_index(drop=True), D[D.split == "held"].reset_index(drop=True); res = {}
    ae = lambda X: np.abs(X.y.values - X.lf0.values)
    qs = lambda x: {a: float(np.quantile(x, 1 - a)) for a in (0.2, 0.1)}
    # LOFO coverage on development
    cov = {a: [] for a in (0.2, 0.1)}; wid = {a: [] for a in (0.2, 0.1)}
    for fam in dev.family.unique():
        tr, te = dev[dev.family != fam], dev[dev.family == fam]; q = qs(ae(tr))
        for a in cov: cov[a] += list(ae(te) <= q[a]); wid[a].append(2 * q[a])
    qd = qs(ae(dev)); qh = {a: float(np.mean(ae(held) <= qd[a])) for a in (0.2, 0.1)}
    res["development_lofo"] = dict(cov80=float(np.mean(cov[0.2])), cov90=float(np.mean(cov[0.1])), n=len(dev)); res["frozen_q"] = dict(q80=qd[0.2], q90=qd[0.1], width80_decades=2 * qd[0.2], width90_decades=2 * qd[0.1])
    res["heldout"] = dict(cov80=qh[0.2], cov90=qh[0.1], n=len(held))
    # problem-level bootstrap for held-out coverage
    rs = np.random.default_rng(0); inst = held.instance.values; names = np.unique(inst); idx = {n: np.where(inst == n)[0] for n in names}
    bc = [np.mean(np.concatenate([ae(held)[idx[n]] <= qd[0.2] for n in rs.choice(names, len(names))])) for _ in range(2000)]; res["heldout"]["cov80_ci_problem_level"] = [float(x) for x in np.percentile(bc, [2.5, 97.5])]
    # error quantiles of the raw forecast (all 54 problems) as multiplicative factors
    allae = ae(D); res["raw_forecast_factor_quantiles"] = {f"q{int(p*100)}": float(10 ** np.quantile(allae, p)) for p in (0.5, 0.8, 0.9)}; res["raw_forecast_share2"] = dict(dev=float((ae(dev) <= LOG2).mean()), held=float((ae(held) <= LOG2).mean()), all=float((allae <= LOG2).mean()))
    res["raw_forecast_bias_decades"] = dict(dev=float(np.median(dev.y - dev.lf0)), held=float(np.median(held.y - held.lf0)))
    # per-N0 quantile table
    res["by_N0"] = {int(n0): dict(share2=float((ae(g) <= LOG2).mean()), q80_factor=float(10 ** np.quantile(ae(g), 0.8)), n=int(len(g))) for n0, g in D.groupby("N0")}
    # decision value with the raw interval (frozen on development, applied to held-out and to all cases by LOFO)
    dec = {}
    for thr, nm in ((0.01, "one_pct"), (0.001, "tenth_pct")):
        lt = np.log10(thr); upper = held.lf0.values + qd[0.2]; conf = upper <= lt; reached = held.y.values <= lt; best = held.lf0.values <= lt
        dec[nm] = dict(n_confident=int(conf.sum()), precision=(float(reached[conf].mean()) if conf.sum() else None), n_reached=int(reached.sum()), recall=(float(conf[reached].mean()) if reached.sum() else None),
                       point_rule_precision=(float(reached[best].mean()) if best.sum() else None), point_rule_recall=(float(best[reached].mean()) if reached.sum() else None))
    res["decision_heldout"] = dec
    json.dump(res, open(OUT / "posthoc.json", "w"), indent=1, default=float); print(json.dumps(res, indent=1, default=float))


if __name__ == "__main__": main()
