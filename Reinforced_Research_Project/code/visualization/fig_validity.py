"""Figure 3: Is the learning-curve forecast usable? Forecast versus actual test error at 4x the budget (N0 = 64 and 256), 48 cases, with the factor-2 band."""
import sys, pathlib, numpy as np, pandas as pd
sys.path.insert(0, str(pathlib.Path(__file__).parent)); from style import *
B = pd.read_csv(ROOT / "results/s6/B1_cases.csv"); fig, ax = plt.subplots(1, 2, figsize=(TWO, 2.7), gridspec_kw=dict(width_ratios=[1.25, 1], wspace=0.32))
a = ax[0]; lo, hi = 10 ** np.floor(np.log10(min(B.actual.min(), B.pred.min()))), 10 ** np.ceil(np.log10(max(B.actual.max(), B.pred.max()))); xs = np.array([lo, hi])
a.fill_between(xs, xs / 2, xs * 2, color="#DDDDDD", lw=0, label="factor 2"); a.plot(xs, xs, c="#555555", lw=0.6)
for N0, col, mk in ((64, C["blue"], "o"), (256, C["orange"], "s")):
    s = B[B.N0 == N0]; a.scatter(s.actual, s.pred, s=9, color=col, marker=mk, linewidths=0, alpha=0.85, label=f"$N_0={N0}$ (forecast for ${4*N0}$ runs)")
a.set_xscale("log"); a.set_yscale("log"); a.set_xlim(lo, hi); a.set_ylim(lo, hi); a.set_xlabel("actual test error at $4N_0$ runs"); a.set_ylabel("forecast from $N_0$ runs"); a.legend(frameon=False, loc="upper left", fontsize=6); a.set_title("(a)", loc="left", fontsize=8, fontweight="bold")
b = ax[1]; lr = np.log10(B.pred / B.actual); b.axvspan(-np.log10(2), np.log10(2), color="#DDDDDD", lw=0); b.axvline(0, c="#555555", lw=0.6)
for N0, col in ((64, C["blue"]), (256, C["orange"])): b.hist(lr[B.N0 == N0], bins=np.linspace(-2, 2, 21), color=col, alpha=0.65, label=f"$N_0={N0}$")
b.set_xlabel(r"$\log_{10}$(forecast / actual)"); b.set_ylabel("cases"); b.legend(frameon=False, fontsize=6); b.set_title("(b)", loc="left", fontsize=8, fontweight="bold"); save(fig, "fig_validity")
