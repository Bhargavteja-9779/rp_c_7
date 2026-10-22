"""v2 figures, generated from results tables (no hand-drawn data)."""
from __future__ import annotations
import json, pathlib, numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from .figures import INK, GRID, COL, _save   # reuse style + validated palette
BLUE, ORANGE, GREY = "#2a78d6", "#eb6834", "#b9b8b2"
plt.rcParams.update({"font.size": 8, "axes.edgecolor": INK, "axes.labelcolor": INK, "text.color": INK, "xtick.color": INK, "ytick.color": INK, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.5, "savefig.dpi": 300, "legend.frameon": False, "font.family": "DejaVu Sans"})
TIE = 0.10


def fig_outcomes_by_N(cells, out, name="figv2_outcomes_by_N"):
    """Stacked counts of clear-LS / tie / clear-NL cells by N (tie band +-0.10 decades)."""
    Ns = sorted(cells.N.unique()); fig, ax = plt.subplots(figsize=(4.4, 3.0)); bot = np.zeros(len(Ns))
    for lab, col, f in (("LS clearly better (ȳ > 0.1)", BLUE, lambda g: (g.y > TIE).sum()), ("tie (|ȳ| ≤ 0.1)", GREY, lambda g: (g.y.abs() <= TIE).sum()), ("NL clearly better (ȳ < −0.1)", ORANGE, lambda g: (g.y < -TIE).sum())):
        v = np.array([f(cells[cells.N == N]) for N in Ns]); ax.bar(range(len(Ns)), v, bottom=bot, color=col, label=lab, width=0.7, edgecolor="white", linewidth=1); bot += v
    ax.set_xticks(range(len(Ns)), Ns); ax.set_xlabel("training solves N"); ax.set_ylabel("instances"); ax.legend(fontsize=6.5, loc="upper center", bbox_to_anchor=(0.5, 1.28), ncol=1); fig.tight_layout(); _save(fig, out, name)


def fig_diag_scatter(cells, out, frozen_t=None, name="figv2_diagnostic_vs_outcome", new_instances=()):
    """f1 (pilot LOO POD error) vs ȳ at N=1024 for all instances; new-family instances are marked."""
    g = cells[cells.N == 1024]; fig, ax = plt.subplots(figsize=(4.6, 3.4))
    old = g[~g.instance.isin(new_instances)]; new = g[g.instance.isin(new_instances)]
    ax.scatter(old.log_cv_err_r4, old.y, s=22, color=BLUE, label="original 16 instances", edgecolor="white", linewidth=.5, zorder=3)
    ax.scatter(new.log_cv_err_r4, new.y, s=34, marker="D", color=ORANGE, label="new independent instances (Exp A)", edgecolor="white", linewidth=.5, zorder=4)
    ax.axhspan(-TIE, TIE, color=GRID, alpha=0.5, lw=0, zorder=1); ax.axhline(0, color=INK, lw=0.6, zorder=2)
    if frozen_t is not None: ax.axvline(frozen_t, color=INK, ls="--", lw=0.8, label=f"frozen threshold t = {frozen_t:.2f}")
    ax.set_xlabel("pilot diagnostic f1 = log₁₀ LOO POD error (r = 4)"); ax.set_ylabel("ȳ at N = 1024  (> 0: LS better)"); ax.legend(fontsize=6.3, loc="upper right"); fig.tight_layout(); _save(fig, out, name)


def fig_mechanism(tD, out, tE=None, name="figv2_mechanism"):
    """Error ratios (log scale) in cells where POD+GP clearly beats the best NN."""
    sel = tD[(tD.y_gp > TIE)]; data = [sel.ratio_krr_gp.values]; labels = ["matched-search KRR\n/ POD+GP (ARD)"]
    if tE is not None:
        s2 = tE[tE.y_ard > TIE]; data += [(s2.err_iso / s2.err_ard).values, (s2.err_krr / s2.err_iso).values]; labels += ["GP isotropic\n/ GP ARD", "KRR / GP isotropic"]
    fig, ax = plt.subplots(figsize=(1.6 + 1.3 * len(data), 3.1)); parts = ax.boxplot(data, widths=0.5, showfliers=False, patch_artist=True, medianprops=dict(color=INK))
    for b in parts["boxes"]: b.set(facecolor="#dfe9f7", edgecolor=INK, linewidth=0.8)
    for i, d in enumerate(data, 1): ax.scatter(np.random.default_rng(i).normal(i, 0.07, len(d)), d, s=6, color=BLUE, alpha=0.5, zorder=3, edgecolor="none")
    ax.set_yscale("log"); ax.axhline(1, color=INK, lw=0.6); ax.axhline(3, color=INK, lw=0.6, ls="--"); ax.set_xticks(range(1, len(data) + 1), labels, fontsize=7); ax.set_ylabel("test-error ratio (>1: numerator worse)"); fig.tight_layout(); _save(fig, out, name)


def fig_strong_nn(tB, out, name="figv2_strong_nn_shift"):
    """Shift in ȳ when NN training is 4x longer (6000 vs 1500 epochs); positive = LS advantage grew."""
    g = tB.sort_values("y1500"); fig, ax = plt.subplots(figsize=(4.8, 3.2))
    for i, (_, r) in enumerate(g.iterrows()): ax.plot([i, i], [r.y1500, r.y6000], color=GRID, lw=1, zorder=1)
    ax.scatter(range(len(g)), g.y1500, s=14, color=BLUE, label="1500 epochs", zorder=3, edgecolor="none"); ax.scatter(range(len(g)), g.y6000, s=14, color=ORANGE, marker="D", label="6000 epochs", zorder=3, edgecolor="none")
    ax.axhspan(-TIE, TIE, color=GRID, alpha=0.4, lw=0); ax.axhline(0, color=INK, lw=0.6); ax.set_xlabel("(instance, N) cells, sorted by ȳ at 1500 epochs"); ax.set_ylabel("ȳ (oracle-best of each family)"); ax.legend(fontsize=6.5); fig.tight_layout(); _save(fig, out, name)
