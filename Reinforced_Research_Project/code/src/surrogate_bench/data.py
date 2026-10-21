"""Dataset pools: i.i.d. parameter draws + FOM solves, cached on disk. Parameter draws depend only on the
problem name (fixed global seeds), never on any method result."""
from __future__ import annotations
import hashlib, time, numpy as np, pathlib
from multiprocessing import Pool
from .problems import Problem

POOL, N_TEST, N_EXT = 4096, 1000, 500


def _rng(name, stream):
    h = int(hashlib.sha256(f"{name}|{stream}".encode()).hexdigest()[:8], 16)
    return np.random.default_rng(h)


def draw_params(problem: Problem):
    p = problem.p
    tr = _rng(problem.name, "train").random((POOL, p))
    te = _rng(problem.name, "test").random((N_TEST, p))
    r = _rng(problem.name, "ext"); ex = []
    while len(ex) < N_EXT:
        c = -0.25 + 1.5 * r.random(p)
        if not np.all((c >= 0) & (c <= 1)): ex.append(c)
    return tr, te, np.array(ex)


def _solve_chunk(args):
    name, mus, dev = args
    from .problems import build_suite, build_dev
    P = build_dev() if dev else build_suite()[name]
    return np.array([P.solve(m) for m in mus])


def build_dataset(problem: Problem, cache_dir, dev=False, workers=4):
    cache = pathlib.Path(cache_dir) / f"{problem.name}.npz"
    if cache.exists():
        z = np.load(cache); return {k: z[k] for k in z.files}
    tr, te, ex = draw_params(problem)
    allmu = np.vstack([tr, te, ex]); chunks = np.array_split(allmu, workers * 8)
    t0 = time.time()
    with Pool(workers) as pool: out = pool.map(_solve_chunk, [(problem.name, c, dev) for c in chunks])
    wall = time.time() - t0
    U = np.vstack(out)
    # single-process timing of the FOM on 40 samples -> per-solve cost used in the cost analysis
    t1 = time.time(); [problem.solve(m) for m in tr[:40]]; per_solve = (time.time() - t1) / 40
    d = dict(mu_train=tr, u_train=U[:POOL], mu_test=te, u_test=U[POOL:POOL + N_TEST], mu_ext=ex, u_ext=U[POOL + N_TEST:],
             fom_seconds_per_solve=np.array(per_solve), gen_wall_seconds=np.array(wall))
    pathlib.Path(cache_dir).mkdir(parents=True, exist_ok=True); np.savez_compressed(cache, **d)
    return d
