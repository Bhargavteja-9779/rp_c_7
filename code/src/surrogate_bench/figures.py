"""Publication figures generated from results/tables/*.csv and results/statistics.json (no hand-drawn data)."""
from __future__ import annotations
import json, pathlib, numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

INK, GRID = "#0b0b0b", "#d9d8d4"
COL = dict(pod_gp="#2a78d6", pod_poly="#eb6834", pod_mlp="#1baf7a", mlp_direct="#eda100", bottleneck="#e87ba4")   # validated slots 1-5
MK = dict(pod_gp="o", pod_poly="s", pod_mlp="^", mlp_direct="D", bottleneck="v")
LS_ = dict(pod_gp="-", pod_poly="-", pod_mlp="-", mlp_direct="--", bottleneck="--")                                  # solid = LS, dashed = NL
LABEL = dict(pod_gp="POD+GP", pod_poly="POD+Poly", pod_mlp="POD+MLP", mlp_direct="MLP (direct)", bottleneck="Bottleneck MLP")
DIV = LinearSegmentedColormap.from_list("div", ["#eb6834", "#f2f1ee", "#2a78d6"])   # y>0 (LS better) blue, y<0 (NL better) orange
plt.rcParams.update({"font.size": 8, "axes.edgecolor": INK, "axes.labelcolor": INK, "text.color": INK, "xtick.color": INK, "ytick.color": INK,
                     "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.5,
                     "figure.dpi": 150, "savefig.dpi": 300, "legend.frameon": False, "font.family": "DejaVu Sans"})


def _save(fig, out, name):
    for ext in ("png", "pdf"): fig.savefig(out / f"{name}.{ext}", bbox_inches="tight")
    plt.close(fig)


def fig_learning_curves(T, out):
    lc = pd.read_csv(T / "learning_curves.csv"); insts = sorted(lc.instance.unique())
    fig, axes = plt.subplots(4, 4, figsize=(7.4, 7.6), sharex=True)
    for ax, inst in zip(axes.ravel(), insts):
        for m in COL:
            g = lc[(lc.instance == inst) & (lc.method == m)].sort_values("N")
            se = g["std"].fillna(0) / np.sqrt(g["count"]); ax.plot(g.N, g["mean"], LS_[m], marker=MK[m], ms=3, lw=1, color=COL[m], label=LABEL[m])
            ax.fill_between(g.N, np.maximum(g["mean"] - 1.96 * se, 1e-12), g["mean"] + 1.96 * se, color=COL[m], alpha=0.15, lw=0)
        ax.set_xscale("log", base=2); ax.set_yscale("log"); ax.set_title(inst, fontsize=7.5)
    for ax in axes[-1]: ax.set_xlabel("training solves N")
    for ax in axes[:, 0]: ax.set_ylabel("rel. $L_2$ error")
    h, l = axes[0, 0].get_legend_handles_labels(); fig.legend(h, l, ncol=5, loc="upper center", bbox_to_anchor=(0.5, 1.03), fontsize=7.5)
    fig.tight_layout(); _save(fig, out, "fig2_learning_curves")


def fig_heatmap(T, out):
    c = pd.read_csv(T / "cells.csv"); P = c.pivot(index="instance", columns="N", values="y"); v = np.nanmax(np.abs(P.values))
    fig, ax = plt.subplots(figsize=(4.2, 4.6)); im = ax.imshow(P.values, cmap=DIV, vmin=-v, vmax=v, aspect="auto"); ax.grid(False)
    ax.set_xticks(range(P.shape[1]), P.columns); ax.set_yticks(range(P.shape[0]), P.index); ax.set_xlabel("training solves N")
    for i in range(P.shape[0]):
        for j in range(P.shape[1]): ax.text(j, i, f"{P.values[i, j]:+.2f}", ha="center", va="center", fontsize=6, color=INK)
    cb = fig.colorbar(im, ax=ax); cb.set_label(r"$\bar y=\log_{10}(\mathrm{err}_{NL^*}/\mathrm{err}_{LS^*})$  (>0: LS better)")
    _save(fig, out, "fig3_family_ratio_heatmap")


def fig_lofo(T, out):
    d = pd.read_csv(T / "h2_lofo_predictions.csv"); fig, axes = plt.subplots(1, 2, figsize=(6.8, 3.2), sharex=True, sharey=True)
    for ax, k, t in zip(axes, ["B1", "M_spec"], ["Baseline: log$_2$N + p", "Pilot diagnostic: log$_2$N + CV-POD error + slope"]):
        ax.scatter(d.y, d[f"yhat_{k}"], s=10, c=d.N.map({64: "#c9d9f2", 128: "#8fb4e6", 256: "#5b93da", 512: "#2a78d6", 1024: "#164a8c"}), edgecolor="none")
        lim = [min(d.y.min(), d[f"yhat_{k}"].min()) - .1, max(d.y.max(), d[f"yhat_{k}"].max()) + .1]; ax.plot(lim, lim, color=INK, lw=0.6); ax.set_title(t, fontsize=7.5)
        ax.set_xlabel("observed $\\bar y$"); ax.axhline(0, color=GRID, lw=.6); ax.axvline(0, color=GRID, lw=.6)
    axes[0].set_ylabel("leave-one-family-out prediction"); fig.tight_layout(); _save(fig, out, "fig4_lofo_prediction")


def fig_tuning(S, out):
    cur = S["H4b_descriptive"]["nl_win_rate_by_budget"]; fig, ax = plt.subplots(figsize=(3.6, 3.0))
    xs = [1, 2, 4, 8]; ax.plot(xs, [cur[f"LS_b{b}_NL_b{b}"] for b in xs], "o-", color="#2a78d6", lw=1.2, label="symmetric (both tuned with b trials)")
    ax.plot([1, 8], [cur["LS_b1_NL_b8"]] * 2, "s--", color="#eb6834", lw=1.2, label="asymmetric (LS default, NL b=8)")
    ax.set_xscale("log", base=2); ax.set_xticks(xs, xs); ax.set_xlabel("hyper-parameter trials b"); ax.set_ylabel("fraction of cells won by NL"); ax.legend(fontsize=6.5, loc="best")
    fig.tight_layout(); _save(fig, out, "fig5_tuning_asymmetry")


def fig_extrap(T, out):
    c = pd.read_csv(T / "h3_inflation.csv"); fig, ax = plt.subplots(figsize=(3.4, 3.2))
    for r in c.itertuples(): ax.plot([0, 1], [r.infl_ls, r.infl_nl], color=GRID, lw=.8, marker="o", ms=3, mfc="#2a78d6" if False else "none")
    ax.plot([0, 1], [c.infl_ls.mean(), c.infl_nl.mean()], color="#2a78d6", lw=2, marker="o", label="mean")
    ax.set_xticks([0, 1], ["LS*", "NL*"]); ax.set_ylabel("$\\log_{10}$(err$_{ext}$/err$_{interp}$), N=256"); ax.legend(); fig.tight_layout(); _save(fig, out, "fig6_extrapolation")


def make_all(res_dir):
    res = pathlib.Path(res_dir); T = res / "tables"; out = res.parent / "figures" if res.name == "results" else res / "figures"; out.mkdir(parents=True, exist_ok=True)
    S = json.load(open(res / "statistics.json"))
    fig_learning_curves(T, out); fig_heatmap(T, out); fig_lofo(T, out); fig_tuning(S, out); fig_extrap(T, out); return out
