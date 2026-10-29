"""Analysis-only: smallest training budget N (among the N levels run) at which each family's validation-selected model reaches a target mean relative error.
Seed-geometric-mean error per (instance, N). Instances run at N in {32..1024} (24) or {64,256,1024} (12): resolution is coarser for the latter."""
import sys, json, pathlib, numpy as np, pandas as pd
ROOT = pathlib.Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT / "code/src"))
from surrogate_bench import analysis as A
d = [A.load(p)[0] for p in (ROOT.parent / "results/raw", ROOT / "results/raw_expA", ROOT / "results/raw_expA2", ROOT / "results/raw_expA3")]
df = pd.concat(d, ignore_index=True); y = A.family_y(df); y["l_ls"] = np.log10(y.err_ls); y["l_nl"] = np.log10(y.err_nl)
g = y.groupby(["instance", "family", "p", "N"], as_index=False)[["l_ls", "l_nl"]].mean()
rows = []
for (inst, fam, p), s in g.groupby(["instance", "family", "p"]):
    s = s.sort_values("N"); r = dict(instance=inst, family=fam, p=int(p))
    for t in (1e-1, 1e-2, 1e-3):
        for k, col in (("ls", "l_ls"), ("nl", "l_nl")):
            ok = s[s[col] <= np.log10(t)]; r[f"{k}_{t:g}"] = int(ok.N.min()) if len(ok) else None
    r["err_ls_256"] = float(10 ** s[s.N == 256].l_ls.iloc[0]); r["err_nl_256"] = float(10 ** s[s.N == 256].l_nl.iloc[0]); r["err_ls_1024"] = float(10 ** s[s.N == 1024].l_ls.iloc[0]); r["err_nl_1024"] = float(10 ** s[s.N == 1024].l_nl.iloc[0]); rows.append(r)
t = pd.DataFrame(rows); t.to_csv(ROOT / "results/budget_to_accuracy.csv", index=False)
summ = {f"{k}_{th}": int(t[f"{k}_{th}"].notna().sum()) for th in ("0.1", "0.01", "0.001") for k in ("ls", "nl")}; summ["n_instances"] = int(len(t))
# fit time (CPU seconds, tuning+final fit) at N=1024 by method, seed-median over instances
df["t_total"] = df.t_fit + df.t_hpo; tm = df[df.N == 1024].groupby("method").t_total.median().to_dict(); summ["median_cpu_seconds_N1024"] = {k: float(v) for k, v in tm.items()}
tm256 = df[df.N == 256].groupby("method").t_total.median().to_dict(); summ["median_cpu_seconds_N256"] = {k: float(v) for k, v in tm256.items()}
(ROOT / "results/budget_to_accuracy.json").write_text(json.dumps(summ, indent=1)); print(json.dumps(summ, indent=1))
