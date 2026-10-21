"""Phase-1 forensic check. Does NOT import surrogate_bench.analysis or surrogate_bench.stats: re-derives the key statistics from raw JSON with
independent code, and checks internal consistency of the raw outputs. Exit 1 on any failure."""
import json, glob, pathlib, sys, math, numpy as np
from scipy import stats as sps
ROOT = pathlib.Path(__file__).resolve().parents[2]; RAW = ROOT / "results/raw"; S = json.load(open(ROOT / "results/statistics.json")); out = []; bad = 0
def chk(name, ok, detail=""):
    global bad; bad += (not ok); out.append(f"| {'PASS' if ok else '**FAIL**'} | {name} | {detail} |")
LS, NL = ["pod_gp", "pod_poly", "pod_mlp"], ["mlp_direct", "bottleneck"]
files = sorted(glob.glob(str(RAW / "*__s*.json"))); files = [f for f in files if not f.endswith("errors.json")]
D = {}
for f in files:
    m = json.load(open(f)); D[(m["instance"], m["seed"])] = m
chk("48 job files, 16 instances x 3 seeds", len(D) == 48 and len({k[0] for k in D}) == 16 and {k[1] for k in D} == {0, 1, 2})
# --- internal consistency of every record
n_rec = n_bad_val = n_bad_cfg = n_bad_trials = n_bad_npz = 0
for (inst, s), m in D.items():
    z = np.load(RAW / f"{inst}__s{s}__errors.npz")
    for r in m["records"]:
        n_rec += 1; tr = r["trials"]
        n_bad_trials += len(tr) != 8 or [t["trial"] for t in tr] != list(range(8))
        best = min(tr, key=lambda t: t["val"]); n_bad_val += not math.isclose(best["val"], r["val_best"], rel_tol=1e-12); n_bad_cfg += best["cfg"] != r["best_cfg"]
        e = z[f"{r['N']}__{r['method']}__interp"].astype(np.float64); n_bad_npz += not math.isclose(e.mean(), r["test_err"], rel_tol=1e-4)
chk("1440 records; each has 8 trials numbered 0..7", n_rec == 1440 and n_bad_trials == 0, f"records={n_rec}, bad={n_bad_trials}")
chk("val_best == min trial validation error in every record", n_bad_val == 0, f"mismatches={n_bad_val}")
chk("best_cfg == config of the min-validation trial", n_bad_cfg == 0, f"mismatches={n_bad_cfg}")
chk("recorded test_err == mean of per-sample errors in .npz (float32 tol 1e-4)", n_bad_npz == 0, f"mismatches={n_bad_npz}")
# --- independent y / cells
cell = {}
for (inst, s), m in D.items():
    for N in sorted({r["N"] for r in m["records"]}):
        rr = {r["method"]: r for r in m["records"] if r["N"] == N}
        a = min(LS, key=lambda k: rr[k]["val_best"]); b = min(NL, key=lambda k: rr[k]["val_best"])
        cell.setdefault((inst, N), []).append(math.log10(rr[b]["test_err"] / rr[a]["test_err"]))
ybar = {k: float(np.mean(v)) for k, v in cell.items()}; insts = sorted({k[0] for k in ybar}); Ns = [32, 64, 128, 256, 512, 1024]
# H1a
y32 = np.array([ybar[(i, 32)] for i in insts]); w = sps.wilcoxon(y32, alternative="greater")
chk("H1a recomputed (median, p) equals statistics.json", math.isclose(np.median(y32), S["H1a"]["median"], rel_tol=1e-9) and math.isclose(w.pvalue, S["H1a"]["p"], rel_tol=1e-9), f"median={np.median(y32):.4f} p={w.pvalue:.4f}")
# H1b
k = sum(sps.spearmanr(np.log2(Ns), [ybar[(i, N)] for N in Ns]).statistic < 0 for i in insts)
chk("H1b recomputed (k of 16) equals statistics.json", k == S["H1b"]["k"], f"k={k}")
# H4a independent
def trial_y(b_ls, b_nl):
    cells = {}
    for (inst, s), m in D.items():
        for N in Ns:
            rr = {r["method"]: r for r in m["records"] if r["N"] == N}
            pick = lambda meth, b: min(rr[meth]["trials"][:b], key=lambda t: t["val"])
            ls = {k_: pick(k_, b_ls) for k_ in LS}; nl = {k_: pick(k_, b_nl) for k_ in NL}
            a = min(ls, key=lambda k_: ls[k_]["val"]); b = min(nl, key=lambda k_: nl[k_]["val"])
            cells.setdefault((inst, N), []).append(math.log10(nl[b]["test"] / ls[a]["test"]))
    return {k_: np.mean(v) for k_, v in cells.items()}
sym, asym = trial_y(8, 8), trial_y(1, 8); keys = sorted(sym)
b_ = sum((asym[k_] < 0) and not (sym[k_] < 0) for k_ in keys); c_ = sum((not asym[k_] < 0) and (sym[k_] < 0) for k_ in keys)
chk("H4a discordant counts recomputed (b, c) equal statistics.json", (b_, c_) == (S["H4a"]["b"], S["H4a"]["c"]), f"b={b_} c={c_}")
chk("H4a McNemar p recomputed", math.isclose(sps.binomtest(b_, b_ + c_, .5, alternative="greater").pvalue, S["H4a"]["p"], rel_tol=1e-9))
# --- independent LOFO ridge for H2 (own implementation)
feat = {}
for (inst, s), m in D.items(): feat.setdefault(inst, []).append(m["pilot_features"])
fam = {i: i.rsplit("_L", 1)[0] for i in insts}; P = {}
for (inst, s), m in D.items(): P[inst] = m["records"][0]["p"]
rows = [(i, N) for i in insts for N in (64, 128, 256, 512, 1024)]
y = np.array([ybar[r] for r in rows]); lg = np.array([math.log2(r[1]) for r in rows]); g = np.array([fam[r[0]] for r in rows])
cv4 = np.array([np.mean([f["log_cv_err_r4"] for f in feat[r[0]]]) for r in rows]); sl = np.array([np.mean([f["slope"] for f in feat[r[0]]]) for r in rows]); pp = np.array([P[r[0]] for r in rows], float)
def lofo(X):
    res = np.zeros(len(y))
    for f_ in np.unique(g):
        te = g == f_; tr = ~te; mu, sd = X[tr].mean(0), X[tr].std(0) + 1e-12; Z = (X[tr] - mu) / sd; ym = y[tr].mean()
        beta = np.linalg.solve(Z.T @ Z + 1e-3 * tr.sum() * np.eye(X.shape[1]), Z.T @ (y[tr] - ym)); res[te] = y[te] - (((X[te] - mu) / sd) @ beta + ym)
    return np.sqrt(np.mean(res ** 2))
r_b0, r_b1, r_ms = lofo(lg[:, None]), lofo(np.c_[lg, pp]), lofo(np.c_[lg, cv4, sl])
chk("H2 LOFO RMSEs recomputed equal statistics.json (B0,B1,M_spec)", all(math.isclose(a, S["H2"]["rmse"][k_], rel_tol=1e-6) for a, k_ in ((r_b0, "B0"), (r_b1, "B1"), (r_ms, "M_spec"))), f"{r_b0:.3f} {r_b1:.3f} {r_ms:.3f}")
# --- pilot features recomputed from the data cache (independent SVD code)
cache_ok = True; checked = 0
try:
    for inst in ("darcy_L1", "wave_L2"):
        z = np.load(ROOT / "code/data_cache" / f"{inst}.npz"); perm = np.random.default_rng(1000 + 1).permutation(4096)[:32]; Y = z["u_train"][perm]
        errs = []
        for i in range(32):
            tr = np.delete(Y, i, 0); mu = tr.mean(0); V = np.linalg.svd(tr - mu, full_matrices=False)[2][:4].T; yv = Y[i] - mu
            errs.append(np.linalg.norm(yv - V @ (V.T @ yv)) / np.linalg.norm(Y[i]))
        mine = math.log10(np.mean(errs) + 1e-16); stored = D[(inst, 1)]["pilot_features"]["log_cv_err_r4"]; checked += 1
        cache_ok &= math.isclose(mine, stored, rel_tol=1e-6, abs_tol=1e-9)
    chk("pilot feature log_cv_err_r4 recomputed from data cache (2 instances, seed 1)", cache_ok and checked == 2)
except FileNotFoundError:
    chk("pilot feature recomputation (data cache missing)", False, "run build_dataset first")
(ROOT / "Reinforced_Research_Project/audit/independent_recompute_report.md").write_text("# Independent recomputation of key results (no shared analysis code)\n\n| Status | Check | Detail |\n|---|---|---|\n" + "\n".join(out) + "\n")
print("\n".join(out)); sys.exit(1 if bad else 0)
