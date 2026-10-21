"""Exp B: stronger-NN challenge. Refit each STORED best configuration of the three NN-based methods with 6000 epochs (4x) at N in {256,1024}
for all 24 instances x seeds {0,1,2}; same training subset and seed as the recorded run. Resumable; writes results/raw_expB/*.json."""
import sys, json, os, pathlib, time, numpy as np
for v in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS"): os.environ[v] = "1"
ROOT = pathlib.Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT / "src")); ORIG = ROOT.parents[1] / "results/raw"; NEW = ROOT.parent / "results/raw_expA"; OUT = ROOT.parent / "results/raw_expB"
from multiprocessing import Pool
EPOCHS, NS, METHODS = 6000, (256, 1024), ("pod_mlp", "mlp_direct", "bottleneck")
def job(a):
    inst, seed = a; import torch; torch.set_num_threads(1)
    from surrogate_bench import methods as M
    from surrogate_bench.problems import build_suite
    from surrogate_bench.data import build_dataset, POOL
    f = OUT / f"{inst}__s{seed}.json"
    if f.exists(): return f"skip {f.name}"
    src = (ORIG if (ORIG / f"{inst}__s{seed}.json").exists() else NEW) / f"{inst}__s{seed}.json"; rec = json.load(open(src))["records"]
    M.NN_EPOCHS = EPOCHS; M._train.__defaults__ = (EPOCHS,); P = build_suite()[inst]; d = build_dataset(P, str(ROOT / "data_cache"))
    perm = np.random.default_rng(1000 + seed).permutation(POOL); out = []; t0 = time.time()
    for r in rec:
        if r["N"] in NS and r["method"] in METHODS:
            idx = perm[:r["N"]]; mdl = M.REGISTRY[r["method"]]().fit(d["mu_train"][idx], d["u_train"][idx], r["best_cfg"], seed * 100 + 99)
            out.append(dict(instance=inst, seed=seed, N=r["N"], method=r["method"], epochs=EPOCHS, err_6000=float(M.rel_l2(d["u_test"], mdl.predict(d["mu_test"])).mean()),
                            err_1500=r["test_err"], final_train_loss_6000=mdl.final_loss, loss_curve_6000=mdl.curve))
    OUT.mkdir(parents=True, exist_ok=True); tmp = f.with_suffix(".tmp"); tmp.write_text(json.dumps(out)); tmp.rename(f); return f"done {f.name} {time.time()-t0:.0f}s"
if __name__ == "__main__":
    insts = ["darcy_L1","darcy_L2","advdiff_L1","advdiff_L2","transport_L1","transport_L2","burgers_L1","burgers_L2","fisher_L1","fisher_L2","heat2d_L1","heat2d_L2","bratu_L1","bratu_L2","wave_L1","wave_L2","darcyhd_L1","darcyhd_L2","incl_L1","incl_L2","kdv_L1","kdv_L2","nlheat_L1","nlheat_L2"]
    with Pool(4) as p:
        for m in p.imap_unordered(job, [(i, s) for s in (0, 1, 2) for i in insts]): print(m, flush=True)
