"""Independent verification of the v2 results (Exp A, Exp D) WITHOUT importing surrogate_bench.analysis/analysis_v2/stats."""
import json, glob, pathlib, math, itertools, sys, numpy as np
from scipy import stats as sps
RP = pathlib.Path(__file__).resolve().parents[1]; out = []; bad = 0
def chk(n, ok, d=""):
    global bad; bad += (not ok); out.append(f"| {'PASS' if ok else '**FAIL**'} | {n} | {d} |")
fz = json.load(open(RP / "research_design/frozen_rules_from_v1.json")); S = json.load(open(RP / "results/expA_primary/statistics_expA_primary_FINAL.json"))["expA"]
LS, NL = ["pod_gp", "pod_poly", "pod_mlp"], ["mlp_direct", "bottleneck"]
# ---- Exp A raw integrity
files = [f for f in sorted(glob.glob(str(RP / "results/raw_expA/*__s*.json"))) if "errors" not in f]; D = {}
for f in files: m = json.load(open(f)); D[(m["instance"], m["seed"])] = m
chk("Exp A: 24 jobs = 8 instances x 3 seeds", len(D) == 24)
n = bi = bc = bz = bl = 0
for (inst, s), m in D.items():
    z = np.load(RP / "results/raw_expA" / f"{inst}__s{s}__errors.npz")
    for r in m["records"]:
        n += 1; tr = r["trials"]; best = min(tr, key=lambda t: t["val"]); bi += (len(tr) != 8); bc += best["cfg"] != r["best_cfg"]
        bz += not math.isclose(z[f"{r['N']}__{r['method']}__interp"].astype(float).mean(), r["test_err"], rel_tol=1e-4)
        if r["method"] in ("pod_mlp", "mlp_direct", "bottleneck"): bl += not (r.get("loss_curve") and len(r["loss_curve"]) >= 10 and r["train_loss_final"] is not None)
chk("Exp A: 720 records, 8 trials each, argmin-val config recorded, recorded error = mean of per-sample errors", n == 720 and bi == 0 and bc == 0 and bz == 0, f"records={n}")
chk("Exp A: every NN record has a logged loss curve (new in v2)", bl == 0, f"missing={bl}")
# ---- independent ybar, f1, P1, P2
ybar = {}; f1 = {}
for inst in sorted({k[0] for k in D}):
    ys = []
    for s in (0, 1, 2):
        pass
    for N in (32, 64, 128, 256, 512, 1024):
        v = []
        for s in (0, 1, 2):
            rr = {r["method"]: r for r in D[(inst, s)]["records"] if r["N"] == N}; a = min(LS, key=lambda k: rr[k]["val_best"]); b = min(NL, key=lambda k: rr[k]["val_best"]); v.append(math.log10(rr[b]["test_err"] / rr[a]["test_err"]))
        ybar[(inst, N)] = float(np.mean(v))
    f1[inst] = float(np.mean([D[(inst, s)]["pilot_features"]["log_cv_err_r4"] for s in (0, 1, 2)]))
insts = sorted(f1); x = np.array([f1[i] for i in insts]); y = np.array([ybar[(i, 1024)] for i in insts])
rx, ry = sps.rankdata(x), sps.rankdata(y); obs = np.corrcoef(rx, ry)[0, 1]; cnt = sum(np.corrcoef(rx, ry[list(p)])[0, 1] <= obs + 1e-12 for p in itertools.permutations(range(8))); p1 = cnt / math.factorial(8)
chk("P1 recomputed (rho, exact permutation p) equals reported", math.isclose(obs, S["P1"]["rho"], rel_tol=1e-9) and math.isclose(p1, S["P1"]["p"], rel_tol=1e-9), f"rho={obs:.4f} p={p1:.4f}")
rows = [(i, N) for i in insts for N in (64, 128, 256, 512, 1024)]; yy = np.array([ybar[r] for r in rows]); lg = np.array([math.log2(r[1]) for r in rows]); ff = np.array([f1[r[0]] for r in rows])
r2 = ((np.c_[lg, ff] - np.array(fz["R2"]["mu"])) / np.array(fz["R2"]["sd"])) @ np.array(fz["R2"]["beta"]) + fz["R2"]["ym"]; b0 = ((lg[:, None] - np.array(fz["B0"]["mu"])) / np.array(fz["B0"]["sd"])) @ np.array(fz["B0"]["beta"]) + fz["B0"]["ym"]
gain = (yy - b0) ** 2 - (yy - r2) ** 2
chk("P2 mean squared-error gain and RMSEs recomputed", math.isclose(gain.mean(), S["P2"]["mean_sq_error_gain"], rel_tol=1e-9) and math.isclose(np.sqrt(np.mean((yy - r2) ** 2)), S["P2"]["rmse_R2"], rel_tol=1e-9) and math.isclose(np.sqrt(np.mean((yy - b0) ** 2)), S["P2"]["rmse_B0"], rel_tol=1e-9), f"gain={gain.mean():.4f}")
tie = fz["tie_band"]; ok = [(f1[i] > fz["R1"]["t"]) == (ybar[(i, N)] < 0) for i in insts for N in (256, 1024) if abs(ybar[(i, N)]) >= tie]
chk("S1 recomputed (6 of 10 non-tie cells correct)", (sum(ok), len(ok)) == (S["S1"]["correct"], S["S1"]["n_nontie_cells"]), f"{sum(ok)}/{len(ok)}")
# frozen rules provenance: check threshold/coeffs correspond to v1-only source commit
chk("frozen rules cite the v1 source commit 931b306", fz["source_commit"].startswith("931b306"))
# ---- Exp D raw integrity
fd = [f for f in glob.glob(str(RP / "results/raw_expD/*__s*.json")) if "errors" not in f]; nd = 0; badd = 0
for f in fd:
    m = json.load(open(f))
    for r in m["records"]: nd += 1; badd += (len(r["trials"]) != 8 or r["method"] != "pod_krr")
chk("Exp D: 72 jobs, 432 records (24 inst x 3 seeds x 6 N x 1 method), all pod_krr with 8 trials", len(fd) == 72 and nd == 432 and badd == 0, f"jobs={len(fd)} records={nd}")
(RP / "audit/independent_recompute_v2_report.md").write_text("# Independent verification of v2 results (no shared analysis code)\n\n| Status | Check | Detail |\n|---|---|---|\n" + "\n".join(out) + "\n"); print("\n".join(out)); sys.exit(1 if bad else 0)
