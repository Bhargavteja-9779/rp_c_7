"""Figure 5: Tool versus a strongly tuned network on the eight independent problems (test error, seed geometric means; bars: min-max over seeds)."""
import sys, pathlib, numpy as np, pandas as pd
sys.path.insert(0, str(pathlib.Path(__file__).parent)); from style import *
S = ROOT / "results/s6"; C_ = pd.read_pickle(S / "C_records.pkl"); Sd = pd.read_pickle(S / "S_records.pkl") if (S / "S_records.pkl").exists() else None
inst = sorted(C_.instance.unique()); fig, axs = plt.subplots(1, 2, figsize=(TWO, 2.8), sharey=True)
for ax, N in zip(axs, (256, 1024)):
    x = np.arange(len(inst))
    for off, key, lab, col, df in ((-0.27, "err_sel", "SurroSelect", C["green"], C_), (-0.09, "err_leg_gp", "always POD+GP", C["blue"], C_), (0.09, "err_leg_sel", "benchmark selection", C["sky"], C_), (0.27, "err_strong", "tuned network", C["red"], Sd)):
        if df is None: continue
        g = df[df.N == N].groupby("instance")[key]; gm = np.exp(np.log(g.apply(list)).apply(np.mean)) if False else g.apply(lambda v: np.exp(np.mean(np.log(v)))); lo = g.min(); hi = g.max()
        ax.errorbar(x + off, gm.reindex(inst), yerr=[(gm - lo).reindex(inst).values, (hi - gm).reindex(inst).values], fmt="o", ms=3, color=col, elinewidth=0.6, capsize=0, label=lab)
    ax.set_yscale("log"); ax.set_xticks(x); ax.set_xticklabels([i.replace("_", "\n") for i in inst], fontsize=5.5); ax.set_title(f"$N={N}$", fontsize=7.5); ax.grid(axis="y")
axs[0].set_ylabel("test error (mean relative $L_2$)"); axs[1].legend(frameon=False, fontsize=6, loc="upper right"); save(fig, "fig_strong_nn")
