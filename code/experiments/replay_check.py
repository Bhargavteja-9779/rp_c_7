"""Replay check: refit the stored best configuration of selected recorded runs (same seed, same training subset) and compare the
test error with the value recorded in results/raw/*.json. Deterministic methods should match to ~1e-9; NNs to float tolerance on the same hardware."""
import sys, json, pathlib, numpy as np, os
os.environ.setdefault("OMP_NUM_THREADS", "1")
ROOT = pathlib.Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT / "src"))
import torch; torch.set_num_threads(1)
from surrogate_bench import methods as M
from surrogate_bench.problems import build_suite
from surrogate_bench.data import build_dataset, POOL
M.NN_EPOCHS = 1500; M._train.__defaults__ = (1500,)
rows = []
for inst, seed, N in (("darcy_L1", 0, 64), ("transport_L2", 1, 128), ("heat2d_L2", 2, 64), ("bratu_L1", 0, 256)):
    P = build_suite()[inst]; d = build_dataset(P, str(ROOT / "data_cache")); rec = json.load(open(ROOT.parent / "results/raw" / f"{inst}__s{seed}.json"))["records"]
    idx = np.random.default_rng(1000 + seed).permutation(POOL)[:N]
    for r in rec:
        if r["N"] != N: continue
        mdl = M.REGISTRY[r["method"]]().fit(d["mu_train"][idx], d["u_train"][idx], r["best_cfg"], seed * 100 + 99)
        e = float(M.rel_l2(d["u_test"], mdl.predict(d["mu_test"])).mean()); rel = abs(e - r["test_err"]) / r["test_err"]
        rows.append((inst, seed, N, r["method"], r["test_err"], e, rel)); print(f"{inst:12s} s{seed} N={N:4d} {r['method']:11s} recorded={r['test_err']:.6e} replay={e:.6e} rel.diff={rel:.2e}", flush=True)
bad = [x for x in rows if x[6] > 1e-6]; print(f"\n{len(rows)} replays; {len(rows)-len(bad)} match within 1e-6 relative; max rel diff = {max(x[6] for x in rows):.2e}")
json.dump([dict(instance=a, seed=b, N=c, method=d_, recorded=e_, replay=f_, rel_diff=g) for a, b, c, d_, e_, f_, g in rows], open(ROOT.parent / "results/exploratory/replay_check.json", "w"), indent=1)
