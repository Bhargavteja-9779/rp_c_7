"""Figure 2: Which family wins? (a) classes by training budget for the 24 main problems; (b) median signed effect by problem class (all 44 problems), diverging map centred at zero, blue = reduced basis better (same colour as in (a)). Per-problem values are in the Supplement table."""
import sys, pathlib, numpy as np, pandas as pd
sys.path.insert(0, str(pathlib.Path(__file__).parent)); from style import *
from matplotlib.colors import LinearSegmentedColormap
R = ROOT / "results"
pooled = pd.read_csv(R / "expA_primary/tables/pooled_cells.csv"); cls = lambda v: np.where(v > .1, "LS", np.where(v < -.1, "NL", "tie"))
frames = [pooled[["instance", "family", "N", "y"]], pd.read_csv(R / "expA_primary/tables/expA2_cells.csv")[["instance", "family", "N", "y"]], pd.read_csv(R / "expA_primary/tables/expA3_cells.csv")[["instance", "family", "N", "y"]]]
if (R / "s6/tp_cells.csv").exists(): frames.append(pd.read_csv(R / "s6/tp_cells.csv")[["instance", "family", "N", "y"]])
allc = pd.concat(frames)
G = dict(darcy="Flow through porous rock", darcyhd="Flow through porous rock", darcylin="Flow through porous rock", incl="Flow through porous rock", incl3="Flow through porous rock", advdiff="Pollutant or heat carried by a flow", transport="Pollutant or heat carried by a flow",
         heat2d="Heat conduction", heatmv3="Heat conduction", heatp="Heat conduction", diff1d="Heat conduction", nlheat="Heat conduction", bratu="Thermal runaway", fisher="Spreading fronts, reactions", reacdiff="Spreading fronts, reactions",
         burgers="Waves, shocks, acoustics", wave="Waves, shocks, acoustics", kdv="Waves, shocks, acoustics", helm="Waves, shocks, acoustics", lshape="Elastic L-plate†", heatcomp="Composite conduction†", heatmove="Transient heat, moving source†", convdiff="Convection–diffusion†")
allc["cls"] = allc.family.map(G); Ns = [64, 256, 1024]; M = allc[allc.N.isin(Ns)].groupby(["cls", "N"]).y.median().unstack().loc[:, Ns]; cnt = allc[allc.N == 1024].groupby("cls").instance.nunique(); M = M.sort_values(1024, ascending=False)
cmap = LinearSegmentedColormap.from_list("rb", [C["orange"], "#F7F7F7", C["blue"]])
fig = plt.figure(figsize=(TWO, 3.3)); gs = fig.add_gridspec(1, 2, width_ratios=[0.8, 1.2], wspace=1.15)
ax = fig.add_subplot(gs[0]); pooled["k"] = cls(pooled.y.values); cn = pooled.groupby("N").k.value_counts().unstack(fill_value=0).reindex(columns=["LS", "tie", "NL"]); x = np.arange(len(cn)); bot = np.zeros(len(cn))
for k, col, lab in (("LS", C["blue"], "reduced basis clearly better"), ("tie", "#BBBBBB", "tie (within 26%)"), ("NL", C["orange"], "network clearly better")):
    ax.bar(x, cn[k].values, bottom=bot, color=col, width=0.7, label=lab, linewidth=0); bot += cn[k].values
ax.set_xticks(x); ax.set_xticklabels([str(n) for n in cn.index]); ax.set_xlabel("training runs $N$"); ax.set_ylabel("problems (24 main problems)"); ax.legend(frameon=False, loc="upper center", bbox_to_anchor=(0.5, 1.34), fontsize=6.5); fig.text(0.01, 0.985, "(a)", fontsize=8, fontweight="bold")
ax2 = fig.add_subplot(gs[1]); im = ax2.imshow(M.values, aspect="auto", cmap=cmap, vmin=-3.3, vmax=3.3, interpolation="nearest")
ax2.set_xticks(range(3)); ax2.set_xticklabels([str(n) for n in Ns]); ax2.set_yticks(range(len(M))); ax2.set_yticklabels([f"{c} ({cnt.get(c, 0)})" for c in M.index], fontsize=6.5); ax2.set_xlabel("training runs $N$"); fig.text(0.31, 0.985, "(b)", fontsize=8, fontweight="bold")
for i in range(M.shape[0]):
    for j in range(3): ax2.text(j, i, f"{M.values[i, j]:.1f}".replace("-", "−"), ha="center", va="center", fontsize=6.5, color="black")
cb = fig.colorbar(im, ax=ax2, fraction=0.05, pad=0.04, location="top", aspect=30); cb.set_label(r"median $\bar y$ (blue: reduced basis better; orange: network better)", fontsize=6.5); cb.ax.tick_params(labelsize=6.5)
for s in ax2.spines.values(): s.set_visible(False)
save(fig, "fig_main_result")
