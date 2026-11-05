"""Figure 1: SurroSelect pipeline schematic with real example fields (first test sample of heatcomp_L1, seed 0, N=256: true field, selected model, absolute error). Selected model read from results/raw_exp6C."""
import sys, pathlib, json, warnings, numpy as np
warnings.filterwarnings("ignore")
sys.path.insert(0, str(pathlib.Path(__file__).parent)); from style import *
sys.path.insert(0, str(ROOT / "code/src")); sys.path.insert(0, str(ROOT / "surroselect/src"))
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from surroselect import make_candidate, rel_l2
from surrogate_bench.problems import build_suite
from surrogate_bench.data import build_dataset, POOL
name, seed, N = "heatcomp_L1", 0, 256
rec = [r for r in json.load(open(ROOT / f"results/raw_exp6C/{name}__s{seed}.json"))["records"] if r["N"] == N][0]; sel = rec["selected"]
P = build_suite()[name]; d = build_dataset(P, str(ROOT / "code/data_cache")); idx = np.random.default_rng(1000 + seed).permutation(POOL)[:N]; X, Y = d["mu_train"][idx], d["u_train"][idx]
lo, sp = X.min(0), X.max(0) - X.min(0); m = make_candidate(sel).fit((X - lo) / sp, Y); yt = d["u_test"][0]; yh = m.predict(((d["mu_test"][0:1]) - lo) / sp)[0]; n = int(np.sqrt(len(yt)))
fig = plt.figure(figsize=(TWO, 2.6)); ax = fig.add_axes([0, 0.06, 1, 0.94]); ax.set_xlim(0, 10); ax.set_ylim(0, 3.6); ax.axis("off")
def box(x, y, w, h, text, fc="#F4F4F4", ec="#555555", fs=7):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.08", fc=fc, ec=ec, lw=0.6)); ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs, wrap=True)
def arrow(x0, y0, x1, y1): ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1), arrowstyle="-|>", mutation_scale=7, lw=0.7, color="#555555"))
box(0.1, 1.3, 1.55, 1.0, "$N$ simulation runs\ninputs $\\mu_i$, fields $u_i$", fc="#EAF3FA"); box(2.15, 1.3, 2.0, 1.0, "pool of stand-ins\nPOD+GP, POD+KRR, POD+poly,\nGP on full field", fc="#EAF3FA", fs=6.5)
box(4.65, 2.45, 1.9, 0.9, "$k$-fold cross-validation\n+ tie band", fc="#EAF6EF"); box(4.65, 1.3, 1.9, 0.9, "basis check\nmodel error vs POD floor", fc="#EAF6EF"); box(4.65, 0.15, 1.9, 0.9, "learning curve\nforecast of runs needed", fc="#EAF6EF")
box(7.05, 1.3, 1.1, 1.0, "report:\nselected model,\nties, flags,\nforecast", fc="#FDF1E3", fs=6.5)
arrow(1.65, 1.8, 2.15, 1.8); arrow(4.15, 1.9, 4.65, 2.8); arrow(4.15, 1.8, 4.65, 1.75); arrow(4.15, 1.7, 4.65, 0.6); arrow(6.55, 2.9, 7.05, 2.0); arrow(6.55, 1.75, 7.05, 1.8); arrow(6.55, 0.6, 7.05, 1.6)
vmax = max(yt.max(), yh.max())
for i, (f, lab, cm, vm) in enumerate(((yt, "true field", "viridis", vmax), (yh, "selected model", "viridis", vmax), (np.abs(yh - yt), "absolute error", "magma", None))):
    a = fig.add_axes([8.45 / 10 + 0.0, 0, 0, 0]); a.remove()
    sub = fig.add_axes([0.845, 0.77 - 0.25 * i, 0.15, 0.2]); sub.imshow(f.reshape(n, n), origin="lower", cmap=cm, vmin=0, vmax=vm); sub.set_xticks([]); sub.set_yticks([]); sub.set_title(lab, fontsize=6.5, pad=1)
    for s in sub.spines.values(): s.set_linewidth(0.4)
arrow(8.2, 1.8, 8.45, 1.8)
fig.text(0.80, 0.0, f"{name}, N={N}, seed 0\nselected: {sel}\nrelative error of this sample: {np.linalg.norm(yh-yt)/np.linalg.norm(yt):.1e}", fontsize=6.5, va="top")
save(fig, "fig_framework")
