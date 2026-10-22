"""Exp F (pre-registered in protocol_addendum_v2.2.md): is the neural error floor an optimisation/precision artefact?
Refit each STORED best configuration of the three NN methods in float64 with FULL-BATCH Adam (6000 steps, cosine) [variant f64_adam], and then
polish with L-BFGS (strong-Wolfe, float64, full batch) [variant f64_lbfgs]. Same training subset and seed as the recorded run. Resumable."""
import sys, json, os, pathlib, time, numpy as np
for v in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS"): os.environ[v] = "1"
ROOT = pathlib.Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT / "src")); ORIG = ROOT.parents[1] / "results/raw"; NEW = ROOT.parent / "results/raw_expA"; OUT = ROOT.parent / "results/raw_expF"
from multiprocessing import Pool
INSTANCES = ["bratu_L1", "bratu_L2", "burgers_L1", "nlheat_L1", "nlheat_L2", "darcy_L1", "heat2d_L1", "transport_L2", "fisher_L2", "heat2d_L2"]
NS, METHODS, EPOCHS, LBFGS_ITERS = (256, 1024), ("pod_mlp", "mlp_direct", "bottleneck"), 6000, 400


def build_and_train(method, X, Y, cfg, seed):
    import torch
    from surrogate_bench import methods as M
    torch.manual_seed(seed); dt = torch.float64; Xt = torch.tensor(M._x(X), dtype=dt)
    if method == "pod_mlp":
        pod = M.POD(Y, cfg["r"]); A = pod.encode(Y); s = float(np.sqrt((pod.S[0] ** 2) / len(Y))); T = torch.tensor(A / s, dtype=dt); net = M._mlp(X.shape[1], pod.r, cfg["width"], cfg["depth"], cfg["act"])
        dec = lambda out: pod.decode(out * s)
    elif method == "mlp_direct":
        mean = Y.mean(0); s = float((Y - mean).std() + 1e-12); T = torch.tensor((Y - mean) / s, dtype=dt); net = M._mlp(X.shape[1], Y.shape[1], cfg["width"], cfg["depth"], cfg["act"]); dec = lambda out: out * s + mean
    else:
        mean = Y.mean(0); s = float((Y - mean).std() + 1e-12); T = torch.tensor((Y - mean) / s, dtype=dt); w, d = cfg["width"], max(1, cfg["depth"] - 1)
        net = torch.nn.Sequential(M._mlp(X.shape[1], cfg["k"], w, d, cfg["act"]), M._mlp(cfg["k"], Y.shape[1], w, d, cfg["act"])); dec = lambda out: out * s + mean
    net = net.double(); opt = torch.optim.Adam(net.parameters(), lr=cfg["lr"], weight_decay=cfg["wd"]); sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, EPOCHS)
    for _ in range(EPOCHS):
        opt.zero_grad(); loss = ((net(Xt) - T) ** 2).mean(); loss.backward(); opt.step(); sched.step()
    with torch.no_grad(): l_adam = float(((net(Xt) - T) ** 2).mean())
    pred_adam = lambda Xn: dec(net(torch.tensor(M._x(Xn), dtype=dt)).detach().numpy())
    import copy; net_a = copy.deepcopy(net)
    lb = torch.optim.LBFGS(net.parameters(), lr=1.0, max_iter=LBFGS_ITERS, history_size=60, line_search_fn="strong_wolfe", tolerance_grad=1e-14, tolerance_change=1e-16)
    def closure():
        lb.zero_grad(); l = ((net(Xt) - T) ** 2).mean(); l.backward(); return l
    try: lb.step(closure)
    except Exception: pass
    with torch.no_grad(): l_lb = float(((net(Xt) - T) ** 2).mean())
    pred_lb = lambda Xn: dec(net(torch.tensor(M._x(Xn), dtype=dt)).detach().numpy())
    net_a.eval()
    pa = lambda Xn: dec(net_a(torch.tensor(M._x(Xn), dtype=dt)).detach().numpy())
    return pa, l_adam, pred_lb, l_lb


def job(a):
    inst, seed = a; import torch; torch.set_num_threads(1)
    from surrogate_bench import methods as M
    from surrogate_bench.problems import build_suite
    from surrogate_bench.data import build_dataset, POOL
    f = OUT / f"{inst}__s{seed}.json"
    if f.exists(): return f"skip {f.name}"
    src = (ORIG if (ORIG / f"{inst}__s{seed}.json").exists() else NEW) / f"{inst}__s{seed}.json"; rec = json.load(open(src))["records"]
    P = build_suite()[inst]; d = build_dataset(P, str(ROOT / "data_cache")); perm = np.random.default_rng(1000 + seed).permutation(POOL); out = []; t0 = time.time()
    for r in rec:
        if r["N"] in NS and r["method"] in METHODS:
            idx = perm[:r["N"]]; pa, la, pl, ll = build_and_train(r["method"], d["mu_train"][idx], d["u_train"][idx], r["best_cfg"], seed * 100 + 99)
            ea = float(M.rel_l2(d["u_test"], pa(d["mu_test"])).mean()); el = float(M.rel_l2(d["u_test"], pl(d["mu_test"])).mean())
            out.append(dict(instance=inst, seed=seed, N=r["N"], method=r["method"], err_1500=r["test_err"], err_f64_adam=ea, err_f64_lbfgs=el, train_loss_adam=la, train_loss_lbfgs=ll))
    OUT.mkdir(parents=True, exist_ok=True); tmp = f.with_suffix(".tmp"); tmp.write_text(json.dumps(out)); tmp.rename(f); return f"done {f.name} {time.time()-t0:.0f}s"


if __name__ == "__main__":
    with Pool(4) as p:
        for m in p.imap_unordered(job, [(i, s) for s in (0, 1, 2) for i in INSTANCES]): print(m, flush=True)
