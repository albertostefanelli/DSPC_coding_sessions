"""Build three original, hypothetical Week 10 concept figure previews.

These figures are separate from the notebooks until the instructor approves them.
Run from the repository root with:
    MPLCONFIGDIR=/private/tmp/wk10_assessment/mpl \
        .private/validation_venv/bin/python \
        wk10_turnout_models/assets/build_concept_figures.py

All values are invented for explanation; none is an estimate from the session data.
Existing previews are backed up with a timestamp before they are regenerated.
"""

from datetime import datetime
from pathlib import Path
import shutil
from zoneinfo import ZoneInfo

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
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
        timestamp = datetime.now(ZoneInfo("America/New_York")).strftime(
            "%Y%m%d_%H%M%S_%f"
        )
        backup_dir = ASSET_DIR / "backups" / f"concept_previews_{timestamp}"
        backup_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(destination, backup_dir / filename)
    fig.savefig(destination, dpi=200, bbox_inches="tight", pad_inches=0.2)
    plt.close(fig)
    print(destination)


def figure_score():
    """Add the fitted-model pieces for one fictional voter, in points."""
    # The hypothetical formula is:
    # score = .20 + .15*voted_2018 + .25*voted_2020
    #              + .20*voted_2022 + .001*age
    # This fictional voter is age 40, with vote-history values 0, 1, and 1.
    contributions = np.array([20.0, 0.0, 25.0, 20.0, 4.0])
    cumulative = contributions.cumsum()
    assert np.isclose(cumulative[-1], 69.0)

    fig = plt.figure(figsize=(12.4, 7.3))
    heading(
        fig,
        "A turnout score adds up the model's pieces",
        "Hypothetical linear probability model | One fictional voter, age 40",
    )
    fig.text(0.055, 0.825,
             "Additions are in percentage points; the total is a probability.",
             fontsize=11.5, color=GRAY)
    ax = fig.add_axes([0.09, 0.31, 0.85, 0.45])
    for x, value in enumerate(contributions):
        bottom = 0 if x == 0 else cumulative[x - 1]
        color = BLUE if x < 4 else GOLD
        if value:
            ax.bar(x, value, bottom=bottom, width=0.66, color=color, zorder=3)
            ax.text(
                x, bottom + value / 2,
                f"{'+' if x else ''}{value:.0f}",
                ha="center", va="center", color=WHITE, fontweight="bold",
                fontsize=14 if value > 4 else 11,
            )
        else:
            ax.plot([x - 0.33, x + 0.33], [bottom, bottom], color=BLUE, lw=3)
            ax.text(x, bottom + 3.5, "+0", ha="center", fontsize=14,
                    fontweight="bold", color=BLUE)
        # The dashed connectors show the running total from one piece to the next.
        if x < len(contributions) - 1:
            ax.plot([x + 0.33, x + 0.67], [cumulative[x]] * 2,
                    color=GRAY, ls="--", lw=1.1, zorder=2)
    ax.bar(5.3, 69, width=0.76, color=NAVY, zorder=3)
    ax.text(5.3, 35, "69%", ha="center", va="center", fontsize=22,
            color=WHITE, fontweight="bold")
    ax.set_xticks([0, 1, 2, 3, 4, 5.3])
    ax.set_xticklabels([
        "Starting\npoint", "2018 vote\nNo = 0", "2020 vote\nYes = 1",
        "2022 vote\nYes = 1", "Age\n40 years", "Final\nscore",
    ], fontsize=11.5)
    ax.tick_params(axis="x", length=0, pad=10)
    ax.set_ylim(0, 80)
    ax.set_xlim(-0.65, 5.95)
    ax.set_yticks([0, 20, 40, 60, 80])
    ax.yaxis.set_major_formatter(PercentFormatter(100))
    ax.set_ylabel("Running turnout score", labelpad=10)
    ax.grid(axis="y", color=LINE, lw=0.7, zorder=0)
    ax.spines["left"].set_visible(False)
    ax.spines["bottom"].set_visible(False)
    ax.tick_params(axis="y", length=0)

    # Put the complete arithmetic below the plot, separate from the bar labels.
    fig.text(
        0.52, 0.175,
        "0.20 + (0.15 × 0) + (0.25 × 1) + (0.20 × 1) + (0.001 × 40) = 0.69",
        ha="center", fontsize=13.2, fontweight="bold",
        bbox={"boxstyle": "round,pad=0.75", "facecolor": BLUE_LIGHT,
              "edgecolor": "none"},
    )
    fig.text(0.52, 0.09, "The model predicts a 69% chance that this voter votes.",
             ha="center", fontsize=13.2, color=NAVY)
    fig.text(0.52, 0.035,
             "Invented coefficients and voter. This score does not estimate the effect of contacting the voter.",
             ha="center", fontsize=10.5, color=GRAY)
    save_preview(fig, "fig1_additive_turnout_score.png")


def confusion_panel(fig, rect, title, counts):
    """Draw predicted outcomes on rows and actual outcomes on columns."""
    ax = fig.add_axes(rect)
    ax.set(xlim=(0, 1), ylim=(0, 1))
    ax.axis("off")
    tp, fp, fn, tn = counts
    total = sum(counts)
    accuracy = (tp + tn) / total
    precision = tp / (tp + fp)
    recall = tp / (tp + fn)
    assert total == 100 and tp + fn == 60
    assert np.isclose(accuracy, 0.70)

    ax.text(0.60, 0.98, title, ha="center", va="top", fontsize=18,
            fontweight="bold")
    x0, cell_width, cell_height = 0.33, 0.31, 0.215
    ax.text(x0 + cell_width / 2, 0.86, "Actually\nvoted", ha="center",
            va="center", fontsize=12, fontweight="bold")
    ax.text(x0 + 1.5 * cell_width, 0.86, "Actually did\nnot vote",
            ha="center", va="center", fontsize=12, fontweight="bold")
    row_tops = [0.78, 0.565]
    ax.text(x0 - 0.035, row_tops[0] - cell_height / 2,
            'Predicted\n"will vote"', ha="right", va="center", fontsize=11.3)
    ax.text(x0 - 0.035, row_tops[1] - cell_height / 2,
            'Predicted\n"will not vote"', ha="right", va="center", fontsize=11.3)
    values = [[(tp, "True positive", True), (fp, "False positive", False)],
              [(fn, "False negative", False), (tn, "True negative", True)]]
    for row in range(2):
        for col in range(2):
            value, label, correct = values[row][col]
            x = x0 + col * cell_width
            y = row_tops[row] - cell_height
            ax.add_patch(Rectangle(
                (x, y), cell_width, cell_height,
                facecolor=BLUE_LIGHT if correct else GOLD_LIGHT,
                edgecolor=CREAM, linewidth=3,
            ))
            ax.text(x + cell_width / 2, y + cell_height * 0.62, str(value),
                    ha="center", va="center", fontsize=27, fontweight="bold",
                    color=BLUE if correct else GOLD)
            ax.text(x + cell_width / 2, y + cell_height * 0.23, label,
                    ha="center", va="center", fontsize=9.8)
    ax.text(0.60, 0.275, f"Accuracy: {tp + tn}/100 = {accuracy:.0%}",
            ha="center", fontsize=14, fontweight="bold")
    ax.text(0.60, 0.175,
            f"Precision: {tp}/{tp + fp} = {precision:.1%}",
            ha="center", fontsize=13)
    ax.text(0.60, 0.085, f"Recall: {tp}/{tp + fn} = {recall:.1%}",
            ha="center", fontsize=13)
    return precision, recall


def figure_mistakes():
    """Hold total accuracy fixed while changing false positives/negatives."""
    fig = plt.figure(figsize=(12.8, 8.2))
    heading(fig, "Same accuracy. Different mistakes.",
            "Hypothetical predictions for the same 100 people: 60 voted and 40 did not.")
    fig.text(0.055, 0.815,
             'The free answer: say "will vote" for everyone → 60% accuracy.',
             fontsize=12.5, fontweight="bold", color=BLUE)
    precision_a, recall_a = confusion_panel(
        fig, [0.035, 0.25, 0.44, 0.53], "Model A", (54, 24, 6, 16)
    )
    precision_b, recall_b = confusion_panel(
        fig, [0.525, 0.25, 0.44, 0.53], "Model B", (42, 12, 18, 28)
    )
    assert recall_a > recall_b and precision_b > precision_a

    fig.text(0.295, 0.18, "Model A identifies more of the people\nwho actually voted.",
             ha="center", va="center", fontsize=12.5, linespacing=1.45)
    fig.text(0.785, 0.18, "Model B's predicted voters have\na higher actual turnout rate.",
             ha="center", va="center", fontsize=12.5, linespacing=1.45)
    fig.text(0.52, 0.075,
             "Accuracy counts both kinds of mistake equally.\nPrecision and recall answer different questions.",
             ha="center", va="center", fontsize=12, fontweight="bold",
             linespacing=1.4)
    fig.text(0.52, 0.025, "Blue cells: correct predictions. Gold cells: incorrect predictions. All counts are invented.",
             ha="center", fontsize=10.4, color=GRAY)
    save_preview(fig, "fig2_same_accuracy_different_mistakes.png")


def dot_group(fig, rect, voted, color):
    """Show a hundred people; filled color means the person voted."""
    ax = fig.add_axes(rect)
    x = np.tile(np.arange(10), 10)
    y = np.repeat(np.arange(10)[::-1], 10)
    colors = [color if i < voted else LINE for i in range(100)]
    ax.scatter(x, y, c=colors, s=27, edgecolors="none")
    ax.set(xlim=(-0.6, 9.6), ylim=(-0.6, 9.6), aspect="equal")
    ax.axis("off")


def figure_calibration():
    """Compare two hypothetical 100-person groups with average score .60."""
    fig = plt.figure(figsize=(12.4, 7.8))
    heading(fig, "Calibration asks whether scores mean what they say",
            "Two hypothetical groups, each with 100 people and an average turnout score of 60%.")
    ax = fig.add_axes([0.075, 0.20, 0.455, 0.61])
    ax.plot([0, 1], [0, 1], ls="--", lw=1.6, color=GRAY, zorder=1)
    ax.text(0.12, 0.89, "On this line, the average score\nmatches observed turnout.",
            fontsize=10.5, color=GRAY, ha="left", va="top")
    ax.scatter([0.6], [0.6], color=BLUE, s=150, zorder=4,
               edgecolor=CREAM, linewidth=1.8)
    ax.scatter([0.6], [0.4], color=GOLD, s=150, zorder=4,
               edgecolor=CREAM, linewidth=1.8)
    ax.axvline(0.6, color=LINE, lw=1, zorder=0)
    ax.annotate("A", (0.6, 0.6), xytext=(-19, 9), textcoords="offset points",
                color=BLUE, fontsize=15, fontweight="bold")
    ax.annotate("B", (0.6, 0.4), xytext=(-19, -18), textcoords="offset points",
                color=GOLD, fontsize=15, fontweight="bold")
    ax.annotate("", xy=(0.69, 0.6), xytext=(0.69, 0.4),
                arrowprops={"arrowstyle": "<->", "color": GOLD, "lw": 1.8})
    ax.text(0.735, 0.50, "20-point\noverprediction", fontsize=10.4,
            va="center", ha="left", color=GOLD, fontweight="bold")
    ax.set(xlim=(0, 1), ylim=(0, 1), aspect="equal",
           xlabel="Average score in the group", ylabel="Share of the group who voted")
    ax.set_xticks(np.linspace(0, 1, 6))
    ax.set_yticks(np.linspace(0, 1, 6))
    ax.xaxis.set_major_formatter(PercentFormatter(1))
    ax.yaxis.set_major_formatter(PercentFormatter(1))
    ax.tick_params(length=0, pad=7, labelsize=10.5)
    ax.set_axisbelow(True)
    ax.grid(color=LINE, lw=0.6, alpha=0.6)

    # The right-hand dot arrays make the percentages tangible, without new theory.
    fig.text(0.61, 0.78, "A  |  60 of 100 voted", color=BLUE,
             fontsize=14, fontweight="bold")
    fig.text(0.61, 0.735, "The score matches turnout in this group.",
             fontsize=10.8)
    dot_group(fig, [0.635, 0.50, 0.255, 0.215], 60, BLUE)
    fig.text(0.61, 0.435, "B  |  40 of 100 voted", color=GOLD,
             fontsize=14, fontweight="bold")
    fig.text(0.61, 0.39, "The score is higher than actual turnout.",
             fontsize=10.8)
    dot_group(fig, [0.635, 0.155, 0.255, 0.215], 40, GOLD)
    fig.text(0.77, 0.125, "Colored dot = voted; gray dot = did not vote.",
             ha="center", fontsize=9.3, color=GRAY)
    fig.text(0.51, 0.065,
             "Each plotted dot uses the group's average score, not the middle of a score range.",
             ha="center", fontsize=11.5, fontweight="bold")
    fig.text(0.51, 0.025,
             "These are invented groups. Checking one group does not establish calibration for the whole model.",
             ha="center", fontsize=10.4, color=GRAY)
    save_preview(fig, "fig3_what_calibration_means.png")


if __name__ == "__main__":
    figure_score()
    figure_mistakes()
    figure_calibration()
