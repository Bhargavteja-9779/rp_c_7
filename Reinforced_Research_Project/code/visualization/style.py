"""Shared figure style: size for final width, 6.5-8 pt fonts, one font family, colour-blind-safe (Okabe-Ito) palette, same colour for the same method everywhere."""
import pathlib, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
ROOT = pathlib.Path(__file__).resolve().parents[2]; FIG = ROOT / "paper/figures"; FIG.mkdir(parents=True, exist_ok=True)
ONE, TWO = 3.5, 7.2                                       # inches: one column, two columns
C = dict(blue="#0072B2", orange="#E69F00", green="#009E73", red="#D55E00", purple="#CC79A7", sky="#56B4E9", yellow="#F0E442", grey="#7F7F7F", black="#000000")
METHOD_COLOR = {"reduced": C["blue"], "network": C["orange"], "tie": "#BBBBBB", "tool": C["green"], "strong_nn": C["red"], "legacy": C["sky"], "gp": C["blue"], "krr": C["purple"], "poly": C["yellow"], "full": C["green"]}
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 7, "axes.labelsize": 7, "axes.titlesize": 7.5, "xtick.labelsize": 6.5, "ytick.labelsize": 6.5, "legend.fontsize": 6.5, "axes.linewidth": 0.5,
                     "axes.edgecolor": "#555555", "xtick.color": "#555555", "ytick.color": "#555555", "axes.spines.top": False, "axes.spines.right": False, "grid.color": "#DDDDDD", "grid.linewidth": 0.4,
                     "lines.linewidth": 1.0, "pdf.fonttype": 42, "figure.dpi": 150})


def save(fig, name):
    fig.savefig(FIG / f"{name}.pdf", bbox_inches="tight", pad_inches=0.02); fig.savefig(FIG / f"{name}.png", dpi=200, bbox_inches="tight", pad_inches=0.02); plt.close(fig)
