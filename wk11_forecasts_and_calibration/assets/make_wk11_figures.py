"""Build two hypothetical Week 11 concept figure previews.

These are hypothetical illustrations kept separate from the notebooks until the
instructor approves them. Run with:
    python3 make_wk11_figures.py

All values are invented for explanation; none comes from real forecasts.
Existing previews are backed up with a timestamp before they are regenerated.
"""

from datetime import datetime
from pathlib import Path
import shutil

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.ticker import PercentFormatter
import numpy as np


ASSET_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = ASSET_DIR / "previews"
CREAM = "#FBF9F3"
NAVY = "#20364B"
BLUE = "#317CA6"
BLUE_LIGHT = "#E2EFF5"
GOLD = "#B78420"
GOLD_LIGHT = "#F6EACA"
GRAY = "#687782"
LINE = "#D6DCE0"
WHITE = "#FFFFFF"

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 12,
    "text.color": NAVY,
    "axes.labelcolor": NAVY,
    "xtick.color": GRAY,
    "ytick.color": GRAY,
    "figure.facecolor": CREAM,
    "axes.facecolor": CREAM,
    "savefig.facecolor": CREAM,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.edgecolor": LINE,
    "axes.titleweight": "bold",
})


def heading(fig, title, subtitle):
    """Use the same title placement and visual hierarchy in every figure."""
    fig.text(0.055, 0.94, title, fontsize=21, fontweight="bold", va="top")
    fig.text(0.055, 0.875, subtitle, fontsize=11.5, color=GRAY, va="top")


def save_preview(fig, filename):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    destination = OUTPUT_DIR / filename
    if destination.exists():
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        backup_dir = ASSET_DIR / "backups" / f"concept_previews_{timestamp}"
        backup_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(destination, backup_dir / filename)
    fig.savefig(destination, dpi=200, bbox_inches="tight", pad_inches=0.2)
    plt.close(fig)
    print(destination)


# --------------------------------------------------------------------------
# Figure 1
# --------------------------------------------------------------------------
def curve(x, k):
    return 1 / (1 + ((1 - x) / x) ** k)


def fig_over_underconfident():
    k_over, k_under = 0.292, 2.81
    fig = plt.figure(figsize=(8.4, 7.4))
    heading(fig, "Overconfident or underconfident?",
            "Hypothetical illustration")
    ax = fig.add_axes([0.12, 0.09, 0.84, 0.72])
    # Stop short of 0% and 100%: the overconfident curve turns steeply at the very ends.
    x = np.linspace(0.03, 0.97, 600)
    ax.plot([0, 1], [0, 1], color=GRAY, ls="--", lw=1.8)
    ax.plot(x, curve(x, k_over), color=GOLD, lw=3)
    ax.plot(x, curve(x, k_under), color=BLUE, lw=3)

    ax.axvline(0.8, color=NAVY, ls=":", lw=1.4)
    points = [(0.8, 0.8, "80 of 100", GRAY),
              (0.8, curve(0.8, k_over), "60 of 100", GOLD),
              (0.8, curve(0.8, k_under), "98 of 100", BLUE)]
    expected = [80, 60, 98]
    for (px, py, label, color), want in zip(points, expected):
        assert round(py * 100) == want, (label, py)
        ax.scatter([px], [py], s=70, color=color, edgecolor=CREAM,
                   linewidth=1.5, zorder=5)
    ax.text(0.815, 0.98 - 0.035, "98 of 100", color=BLUE, fontsize=11,
            fontweight="bold", va="center")
    ax.text(0.815, 0.80 - 0.04, "80 of 100", color=GRAY, fontsize=11,
            fontweight="bold", va="center")
    ax.text(0.815, 0.60 - 0.04, "60 of 100", color=GOLD, fontsize=11,
            fontweight="bold", va="center")

    # Direct curve labels
    # Placed just left of the blue curve's upper part (the curve reaches 86% near x = 0.65).
    ax.text(0.60, 0.86, "Underconfident:\nnumbers too close\nto 50%",
            color=BLUE, fontsize=11.5, fontweight="bold", va="center", ha="right")
    ax.text(0.505, 0.37, "Overconfident:\nnumbers too far\nfrom 50%",
            color=GOLD, fontsize=11.5, fontweight="bold", va="center")
    ax.text(0.03, 0.555, "Dashed line, calibrated:\nsaid 80%, happened 80%",
            color=GRAY, fontsize=10.5, fontweight="bold", va="center")

    ax.set(xlim=(0, 1), ylim=(0, 1.0))
    ax.set_aspect("equal")
    ax.xaxis.set_major_formatter(PercentFormatter(1, decimals=0))
    ax.yaxis.set_major_formatter(PercentFormatter(1, decimals=0))
    ax.set_xlabel("What the forecaster said (chance)", fontsize=12.5,
                  labelpad=8)
    ax.set_ylabel("How often it happened", fontsize=12.5, labelpad=8)
    ax.grid(color=LINE, lw=0.7, alpha=0.7)
    ax.set_axisbelow(True)
    save_preview(fig, "fig1_over_underconfident.png")


# --------------------------------------------------------------------------
# Figure 2
# --------------------------------------------------------------------------
def draw_dot(ax, x, y, won):
    face, edge_color = (BLUE, BLUE) if won else (GOLD_LIGHT, GOLD)
    ax.scatter([x], [y], s=210, color=face, edgecolor=edge_color,
               linewidth=1.8, zorder=4)


def dot_stack(ax, x, outcomes):
    """Stack dots at one forecast value; no jitter. Wins sit at the bottom."""
    for i, won in enumerate(sorted(outcomes, reverse=True)):
        draw_dot(ax, x, 0.55 + i * 0.5, won)


def style_panel(ax, title):
    ax.set(xlim=(0, 1), ylim=(0, 5.6))
    ax.set_yticks([])
    ax.spines["left"].set_visible(False)
    ax.xaxis.set_major_formatter(PercentFormatter(1, decimals=0))
    ax.set_xticks(np.arange(0, 1.01, 0.1))
    ax.grid(axis="x", color=LINE, lw=0.7)
    ax.set_axisbelow(True)
    ax.set_title(title, loc="left", fontsize=14, pad=8)
    ax.set_xlabel("Forecast chance of winning", fontsize=11.5)


def fig_calibrated_not_enough():
    fig = plt.figure(figsize=(11, 8.6))
    heading(fig, "Calibrated is not enough", "Hypothetical illustration")
    axA = fig.add_axes([0.05, 0.50, 0.58, 0.28])
    axB = fig.add_axes([0.05, 0.08, 0.58, 0.28])
    for ax, t in [(axA, "Forecaster A: every race gets 50%"),
                  (axB, "Forecaster B: 10% or 90%")]:
        style_panel(ax, t)

    # Forecaster A: 20 dots at 50%, drawn as two side-by-side stacks of 10.
    # Won and lost alternate in a checkerboard, so neither outcome sits to one side of 50%.
    for i in range(20):
        col, row = divmod(i, 10)
        won = (row % 2 == 0) if col == 0 else (row % 2 == 1)
        draw_dot(axA, 0.5 + (-0.012 if col == 0 else 0.012),
                 0.55 + row * 0.5, won)
    dot_stack(axB, 0.1, [True] * 1 + [False] * 9)
    dot_stack(axB, 0.9, [True] * 9 + [False] * 1)

    def note(ax, text):
        ax.text(1.04, 0.5, text, transform=ax.transAxes, fontsize=12,
                va="center", ha="left", wrap=True,
                bbox=dict(boxstyle="round,pad=0.6", fc=WHITE, ec=LINE))

    note(axA, "10 of 20 won.\nWinners and losers\nboth got 50%.\nCalibrated, but it\n"
              "never says which\nrace is likely.")
    note(axB, "Said 10%: 1 of 10 won.\nSaid 90%: 9 of 10 won.\n"
              "Winners got 82% on\naverage, losers 18%.\n"
              "Calibrated, and it\nseparates likely winners\n"
              "from likely losers.")

    handles = [
        Line2D([], [], marker="o", ls="", markersize=11, color=BLUE,
               label="Won"),
        Line2D([], [], marker="o", ls="", markersize=11,
               markerfacecolor=GOLD_LIGHT, markeredgecolor=GOLD,
               markeredgewidth=1.8, label="Lost"),
    ]
    fig.legend(handles=handles, loc="upper right",
               bbox_to_anchor=(0.97, 0.93), frameon=False, ncol=2,
               fontsize=12)
    save_preview(fig, "fig2_calibrated_not_enough.png")


if __name__ == "__main__":
    fig_over_underconfident()
    fig_calibrated_not_enough()
