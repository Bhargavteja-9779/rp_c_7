"""Figure 2: Which family wins? (a) classes by training budget for the 24 main problems; (b) signed effect per problem (44 problems) at three budgets, diverging map centred at zero."""
import sys, pathlib, json, numpy as np, pandas as pd
sys.path.insert(0, str(pathlib.Path(__file__).parent)); from style import *
R = ROOT / "results"
pooled = pd.read_csv(R / "expA_primary/tables/pooled_cells.csv"); cls = lambda v: np.where(v > .1, "LS", np.where(v < -.1, "NL", "tie"))
frames = [pooled[["instance", "N", "y"]], pd.read_csv(R / "expA_primary/tables/expA2_cells.csv")[["instance", "N", "y"]], pd.read_csv(R / "expA_primary/tables/expA3_cells.csv")[["instance", "N", "y"]]]
tp = R / "s6/tp_cells.csv"
if tp.exists(): frames.append(pd.read_csv(tp)[["instance", "N", "y"]])
allc = pd.concat(frames); Ns = [64, 256, 1024]
M = allc[allc.N.isin(Ns)].pivot(index="instance", columns="N", values="y").dropna(); M = M.sort_values(1024, ascending=False)
fig = plt.figure(figsize=(TWO, 4.3)); gs = fig.add_gridspec(1, 2, width_ratios=[1, 1.15], wspace=0.28)
ax = fig.add_subplot(gs[0]); pooled["k"] = cls(pooled.y.values); cnt = pooled.groupby("N").k.value_counts().unstack(fill_value=0).reindex(columns=["LS", "tie", "NL"]); x = np.arange(len(cnt)); bot = np.zeros(len(cnt))
for k, col, lab in (("LS", METHOD_COLOR["reduced"], "reduced basis clearly better"), ("tie", METHOD_COLOR["tie"], "tie (within 26%)"), ("NL", METHOD_COLOR["network"], "network clearly better")):
    ax.bar(x, cnt[k].values, bottom=bot, color=col, width=0.7, label=lab, linewidth=0); bot += cnt[k].values
ax.set_xticks(x); ax.set_xticklabels([str(n) for n in cnt.index]); ax.set_xlabel("training runs $N$"); ax.set_ylabel("problems (24 main problems)"); ax.legend(frameon=False, loc="upper center", bbox_to_anchor=(0.5, 1.2), ncol=1, fontsize=6.2); ax.text(-0.16, 1.2, "(a)", transform=ax.transAxes, fontsize=8, fontweight="bold")
ax2 = fig.add_subplot(gs[1]); vmax = 3.3; im = ax2.imshow(M.values, aspect="auto", cmap="RdBu_r", vmin=-vmax, vmax=vmax, interpolation="nearest")
ax2.set_xticks(range(len(Ns))); ax2.set_xticklabels([str(n) for n in Ns]); ax2.set_yticks(range(len(M))); ax2.set_yticklabels(M.index, fontsize=4.6); ax2.set_xlabel("training runs $N$"); ax2.text(-0.30, 1.02, "(b)", transform=ax2.transAxes, fontsize=8, fontweight="bold")
cb = fig.colorbar(im, ax=ax2, fraction=0.035, pad=0.12, location="bottom", aspect=35); cb.set_label(r"$\bar y=\log_{10}(\mathrm{err}_{\rm network}/\mathrm{err}_{\rm reduced})$; red: reduced basis better, blue: network better", fontsize=6.2); cb.ax.tick_params(labelsize=6)
for s in ax2.spines.values(): s.set_visible(False)
save(fig, "fig_main_result")
