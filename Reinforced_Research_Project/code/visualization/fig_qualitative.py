"""Figure 6: Qualitative examples chosen by a fixed rule (written before looking): for the first problem of each family in suite order (lshape_L1, heatcomp_L1, heatmove_L1, convdiff_L1) at N=256, seed 0, the FIRST test sample in dataset order; plus two failure cases: the cell (problem, N=256) with the largest selection regret, and the cell with the largest error of the selected model. Columns: true field, selected model, absolute error. Outputs are shown on their probe grids (L-plate: displacement magnitude at probe nodes is not a regular grid and is shown as a profile)."""
import sys, pathlib, json, warnings, numpy as np, pandas as pd
warnings.filterwarnings("ignore")
sys.path.insert(0, str(pathlib.Path(__file__).parent)); from style import *
sys.path.insert(0, str(ROOT / "code/src")); sys.path.insert(0, str(ROOT / "surroselect/src"))
from surroselect import make_candidate
from surrogate_bench.problems import build_suite
from surrogate_bench.data import build_dataset, POOL
C_ = pd.read_pickle(ROOT / "results/s6/C_records.pkl"); S = build_suite(); seed, N = 0, 256
cell = C_[C_.N == N].groupby("instance").apply(lambda g: pd.Series(dict(regret=np.exp(np.mean(np.log(g.err_sel / g.err_oracle))), err=np.exp(np.mean(np.log(g.err_sel)))))); fail1, fail2 = cell.regret.idxmax(), cell.err.idxmax()
rows = [("lshape_L1", "rule"), ("heatcomp_L1", "rule"), ("heatmove_L1", "rule"), ("convdiff_L1", "rule")]
for nm, why in ((fail1, "largest regret"), (fail2, "largest error")):
    if nm in [r[0] for r in rows]: print("failure case already shown:", nm, why)
    else: rows.append((nm, why))
fig, axs = plt.subplots(len(rows), 3, figsize=(TWO, 1.25 * len(rows)))
for i, (name, why) in enumerate(rows):
    r = C_[(C_.instance == name) & (C_.N == N) & (C_.seed == seed)].iloc[0]; P = S[name]; d = build_dataset(P, str(ROOT / "code/data_cache")); idx = np.random.default_rng(1000 + seed).permutation(POOL)[:N]
    X, Y = d["mu_train"][idx], d["u_train"][idx]; lo, sp = X.min(0), X.max(0) - X.min(0); m = make_candidate(r.selected).fit((X - lo) / sp, Y); yt = d["u_test"][0]; yh = m.predict((d["mu_test"][:1] - lo) / sp)[0]
    side = int(round(np.sqrt(len(yt)))) if int(round(np.sqrt(len(yt)))) ** 2 == len(yt) else None
    for j, (f, lab, cm) in enumerate(((yt, "true", "viridis"), (yh, "selected model", "viridis"), (np.abs(yh - yt), "absolute error", "magma"))):
        a = axs[i, j]
        if side: a.imshow(f.reshape(side, side), origin="lower", cmap=cm, vmin=0 if j else None); a.set_xticks([]); a.set_yticks([])
        else: a.plot(yt if j == 0 else (yh if j == 1 else np.abs(yh - yt)), lw=0.7, color=C["blue"]); a.set_xticks([]); a.tick_params(labelsize=6.5)
        if i == 0: a.set_title(lab, fontsize=7.5)
        if j == 0: a.set_ylabel(f"{name}\n({why})", fontsize=6.5, rotation=0, ha="right", va="center", labelpad=2)
    axs[i, 2].text(1.04, 0.5, f"{r.selected}\nerror {np.linalg.norm(yh - yt) / np.linalg.norm(yt):.1e}", transform=axs[i, 2].transAxes, fontsize=6.5, va="center")
save(fig, "fig_qualitative")
