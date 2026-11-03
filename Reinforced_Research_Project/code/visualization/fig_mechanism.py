"""Figure 4: Where does the Gaussian-process advantage come from? Error ratio of each alternative to the Gaussian-process reduced model in cells where it clearly beats the best network."""
import sys, pathlib, numpy as np, pandas as pd
sys.path.insert(0, str(pathlib.Path(__file__).parent)); from style import *
T = ROOT / "results/expA_primary/tables"; dc = pd.read_csv(T / "expD_cells.csv"); e = pd.read_csv(T / "expE_cells.csv"); g = pd.read_csv(T / "expG_cells.csv")
series = [("kernel ridge,\nnarrow range", dc[(dc.y_gp > 0.1) & dc.N.isin([64, 256, 1024])].ratio_krr_gp.values, C["purple"]), ("kernel ridge,\nwide, 8 trials", pd.read_csv(T / "expH8_cells.csv").query("y_ard > 0.1").ratio.values, C["purple"]),
          ("kernel ridge,\nwide, 32 trials", pd.read_csv(T / "expH32_cells.csv").query("y_ard > 0.1").ratio.values, C["purple"]), ("GP, one\nlength-scale", (e[e.y_ard > .1].err_iso / e[e.y_ard > .1].err_ard).values, C["blue"]),
          ("GP on full field\n(no POD)", g[g.y_gp > .1].ratio_full_over_pod.values, C["green"])]
fig, ax = plt.subplots(figsize=(TWO * 0.8, 2.5)); bp = ax.boxplot([s[1] for s in series], showfliers=False, widths=0.5, patch_artist=True, medianprops=dict(color="black", lw=1))
for patch, s in zip(bp["boxes"], series): patch.set_facecolor(s[2]); patch.set_alpha(0.35); patch.set_linewidth(0.5)
for i, s in enumerate(series, 1): ax.scatter(np.random.default_rng(i).normal(i, 0.06, len(s[1])), s[1], s=5, color=s[2], alpha=0.7, linewidths=0)
ax.set_yscale("log"); ax.axhline(3, ls="--", c="#555555", lw=0.6); ax.axhline(1, c="#555555", lw=0.6); ax.set_xticks(range(1, 6)); ax.set_xticklabels([s[0] for s in series]); ax.set_ylabel("error ratio to the GP reduced model\n(above 1: alternative is worse)")
ax.text(5.45, 3.2, "factor 3", fontsize=6, ha="right", color="#555555"); save(fig, "fig_mechanism")
