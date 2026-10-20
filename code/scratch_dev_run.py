import sys, time, numpy as np; sys.path.insert(0, "src")
from surrogate_bench.problems import build_dev
from surrogate_bench.data import build_dataset
from surrogate_bench.hpo import run_method
P = build_dev(); d = build_dataset(P, "/tmp/claude-0/-home-user-rp-c-7/d247ddca-2eb6-5163-bca0-57b556b9e2f0/scratchpad/devcache", dev=True)
for N in (32, 256):
    for m in ("pod_gp", "pod_poly", "pod_mlp", "mlp_direct", "bottleneck"):
        t = time.time(); r, _, _ = run_method(m, d["mu_train"][:N], d["u_train"][:N], d["mu_test"], d["u_test"], d["mu_ext"], d["u_ext"], 3, 0, P.p, P.m)
        print(f"DEV N={N:4d} {m:11s} test={r['test_err']:.2e} ext={r['ext_err']:.2e} val={r['val_best']:.2e} total={time.time()-t:5.1f}s fit={r['t_fit']:.1f}s")
