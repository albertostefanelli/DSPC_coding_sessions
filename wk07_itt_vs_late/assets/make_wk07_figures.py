"""Teaching figures for the Week 7 ITT vs LATE notebook.

Run:  python make_wk07_figures.py
Writes fig1_who_ends_up_where.png, fig2_three_comparisons.png and
fig3_why_divide.png next to this script.
"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyBboxPatch, FancyArrowPatch
from matplotlib.colors import to_rgba

OUT = os.path.dirname(os.path.abspath(__file__))

RED, GRAY, BLUE = "#e74c3c", "#95a5a6", "#3498db"
RED_T, BLUE_T = "#fadbd8", "#d6eaf8"
DARK, GREEN = "#2c3e50", "#1e8449"
FADE = 0.25

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.size": 12,
    "axes.titlesize": 14,
    "axes.titleweight": "bold",
    "figure.facecolor": "white",
    "savefig.facecolor": "white",
    "text.color": DARK,
    "hatch.linewidth": 2.0,
})


def save(fig, name):
    fig.savefig(os.path.join(OUT, name), dpi=200, bbox_inches="tight",
                facecolor="white")
    plt.close(fig)


# ----------------------------------------------------------------- Figure 1
def fig1():
    fig, ax = plt.subplots(figsize=(11, 6.5))
    fig.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
    ax.set_xlim(0, 11)
    ax.set_ylim(0.1, 6.5)
    ax.axis("off")

    def box(cx, cy, w, h, fc, ec, text, tc=DARK, fs=12, weight="normal"):
        ax.add_patch(Rectangle((cx - w / 2, cy - h / 2), w, h, fc=fc, ec=ec,
                               lw=1.2, zorder=2))
        ax.text(cx, cy, text, ha="center", va="center", fontsize=fs,
                color=tc, fontweight=weight, zorder=3, linespacing=1.3)

    def line(xs, ys):
        ax.plot(xs, ys, color="black", lw=1.2, zorder=1, solid_capstyle="butt")

    def arrow(x, y0, y1):
        ax.add_patch(FancyArrowPatch((x, y0), (x, y1), arrowstyle="-|>",
                                     mutation_scale=14, color="black",
                                     lw=1.2, shrinkA=0, shrinkB=0, zorder=1))

    # top box and split
    box(5.5, 6.0, 3.4, 0.8, "white", "black",
        "13,383 registered voters\nwith a turnout record")
    line([5.5, 5.5], [5.6, 5.0])
    line([2.75, 8.25], [5.0, 5.0])
    arrow(2.75, 5.0, 4.45)
    arrow(8.25, 5.0, 4.45)
    ax.text(5.65, 5.3, "Random assignment (a coin flip, done by the researchers)",
            ha="left", va="center", fontsize=11, style="italic")

    # level 2
    box(2.75, 4.0, 3.6, 0.9, RED_T, RED, "Assigned a visit\n2,650 people")
    box(8.25, 4.0, 3.6, 0.9, BLUE_T, BLUE, "Control: no visit\n10,733 people")

    # left: stem, label, split
    line([2.75, 2.75], [3.55, 2.3])
    ax.text(2.75, 2.95,
            "Decided by the canvassers' luck\nat the door, NOT by a coin flip",
            ha="center", va="center", fontsize=11, style="italic", zorder=3,
            linespacing=1.3,
            bbox=dict(fc="white", ec="none", pad=3))
    line([1.4, 4.1], [2.3, 2.3])
    arrow(1.4, 2.3, 1.85)
    arrow(4.1, 2.3, 1.85)
    box(1.4, 1.25, 2.5, 1.2, RED, "black",
        "Someone in the household\nanswered the door\n869 people (32.8%)",
        tc="white", fs=11)
    box(4.1, 1.25, 2.5, 1.2, GRAY, "black",
        "Nobody was reached\n1,781 people (67.2%)", fs=11)

    # right: one blue box with dashed divider
    x0, x1 = 5.65, 10.85
    w = x1 - x0
    xd = x0 + 0.328 * w
    ax.add_patch(Rectangle((x0, 0.65), w, 1.2, fc=to_rgba(BLUE, 0.55),
                           ec="black", lw=1.2, zorder=2))
    ax.plot([xd, xd], [0.65, 1.85], color="black", lw=1.4, ls=(0, (4, 3)),
            zorder=3)
    arrow(8.25, 3.55, 1.85)
    ax.text((x0 + xd) / 2, 1.25, "Would have\nanswered\n(≈32.8%)",
            ha="center", va="center", fontsize=11, zorder=3, linespacing=1.3)
    ax.text((xd + x1) / 2, 1.25, "Would not have\nbeen reached\n(≈67.2%)",
            ha="center", va="center", fontsize=11, zorder=3, linespacing=1.3)
    ax.text(8.25, 0.35, "Nobody visited them, so we cannot tell who is who.",
            ha="center", va="center", fontsize=10.5, style="italic")
    save(fig, "fig1_who_ends_up_where.png")


# ----------------------------------------------------------------- Figure 2
H_C = 0.328          # share contacted / would-be-reached
H_N = 1 - H_C        # share not reached
LX, RX, CW = 0.3, 6.2, 3.5   # left col x, right col x, column width


def block(ax, x, y, h, color, on, hatch=False, lw_on=3.0):
    a = 1.0 if on else FADE
    ec = to_rgba("black", a)
    lw = lw_on if on else 1.2
    if hatch:
        ax.add_patch(Rectangle((x, y), CW, h, fc=to_rgba(color, a),
                               ec=to_rgba("white", a), hatch="//", lw=0,
                               zorder=2))
        ax.add_patch(Rectangle((x, y), CW, h, fill=False, ec=ec, lw=lw,
                               zorder=4 if on else 3))
    else:
        ax.add_patch(Rectangle((x, y), CW, h, fc=to_rgba(color, a), ec=ec,
                               lw=lw, zorder=4 if on else 2))


def col_outline(ax, x):
    ax.add_patch(Rectangle((x, 0), CW, 1, fill=False, ec="black", lw=3.2,
                           zorder=6))


def panel(ax, title, red_on, gray_on, ctrl_bottom_on, ctrl_top_on,
          left_col, right_col, arrow_y, gap, sub, sub_color):
    ax.set_xlim(-0.1, 10.1)
    ax.set_ylim(-0.5, 1.12)
    ax.axis("off")
    ax.set_title(title, pad=10, fontsize=14, fontweight="bold")

    # left column (assigned)
    block(ax, LX, 0, H_N, GRAY, gray_on, lw_on=1.2 if left_col else 3.0)
    block(ax, LX, H_N, H_C, RED, red_on, lw_on=1.2 if left_col else 3.0)
    # right column (control)
    block(ax, RX, 0, H_N, BLUE, ctrl_bottom_on, lw_on=1.2)
    block(ax, RX, H_N, H_C, BLUE, ctrl_top_on, hatch=True,
          lw_on=1.2 if right_col else 3.0)
    if left_col:
        col_outline(ax, LX)
    if right_col:
        col_outline(ax, RX)

    # headers
    ax.text(LX + CW / 2, 1.04, "Assigned a visit", ha="center", va="bottom",
            fontsize=10.5, fontweight="bold")
    ax.text(RX + CW / 2, 1.04, "Control", ha="center", va="bottom",
            fontsize=10.5, fontweight="bold")

    # block labels
    def lab(x, y, t, on, tc=DARK, bbox=None, weight="normal"):
        ax.text(x + CW / 2, y, t, ha="center", va="center", fontsize=8.5,
                color=to_rgba(tc, 1.0 if on else 0.45), zorder=7,
                linespacing=1.25, bbox=bbox, fontweight=weight)

    lab(LX, H_N / 2, "Not reached\n43.5%", gray_on)
    lab(LX, H_N + H_C / 2, "Contacted\n57.7%", red_on, tc="white",
        weight="bold")
    lab(RX, H_N / 2, "Would not be\nreached", ctrl_bottom_on)
    lab(RX, H_N + H_C / 2, "Would be reached\n45.6% (worked out)",
        ctrl_top_on,
        bbox=dict(fc=to_rgba("white", 0.88 if ctrl_top_on else 0.5),
                  ec="none", pad=2))
    # outside label for whole control column
    ax.text(RX + CW / 2, -0.06, "All control: 44.2%", ha="center", va="top",
            fontsize=9, fontweight="bold" if right_col else "normal",
            color=to_rgba(DARK, 1.0 if right_col else 0.45))
    if left_col:
        ax.text(LX + CW / 2, -0.06, "All assigned: 48.1%", ha="center",
                va="top", fontsize=9, fontweight="bold")

    # two-headed arrow with the gap on it
    ax.add_patch(FancyArrowPatch((LX + CW + 0.08, arrow_y),
                                 (RX - 0.08, arrow_y), arrowstyle="<|-|>",
                                 mutation_scale=14, color=DARK, lw=2.0,
                                 zorder=8, shrinkA=0, shrinkB=0))
    ax.text((LX + CW + RX) / 2, arrow_y + 0.05, gap, ha="center",
            va="bottom", fontsize=10, fontweight="bold", zorder=8)

    ax.text(5.0, -0.22, sub, ha="center", va="top", fontsize=9.5,
            color=sub_color, linespacing=1.3)


def fig2():
    fig, axes = plt.subplots(1, 3, figsize=(11, 4.4))
    fig.subplots_adjust(left=0.01, right=0.99, top=0.88, bottom=0.08,
                        wspace=0.02)
    mid_red = H_N + H_C / 2
    panel(axes[0], "A. Naive comparison: +13.5 pp",
          red_on=True, gray_on=False, ctrl_bottom_on=True, ctrl_top_on=True,
          left_col=False, right_col=True, arrow_y=mid_red, gap="+13.5 pp",
          sub="Unfair: contacted people were picked\nafter the coin flip.",
          sub_color=RED)
    panel(axes[1], "B. ITT: +3.95 pp",
          red_on=True, gray_on=True, ctrl_bottom_on=True, ctrl_top_on=True,
          left_col=True, right_col=True, arrow_y=0.5, gap="+3.95 pp",
          sub="Fair: compares the two groups\nthe coin flip created.",
          sub_color=GREEN)
    panel(axes[2], "C. LATE: +12.0 pp",
          red_on=True, gray_on=False, ctrl_bottom_on=False, ctrl_top_on=True,
          left_col=False, right_col=False, arrow_y=mid_red, gap="+12.0 pp",
          sub="Fair, with assumptions: compares\ncontacted people with their "
              "look-alikes in control.",
          sub_color=GREEN)
    fig.text(0.5, 0.01,
             "Block heights show the share of people (32.8% / 67.2%). "
             "Percentages inside blocks are turnout.",
             ha="center", va="bottom", fontsize=10, color="#7f8c8d")
    save(fig, "fig2_three_comparisons.png")


# ----------------------------------------------------------------- Figure 3
def fig3():
    fig, ax = plt.subplots(figsize=(11, 3.8))
    fig.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
    ax.set_xlim(-0.05, 10.05)
    ax.set_ylim(0, 3.8)
    ax.axis("off")
    y0, h = 1.9, 1.1
    ax.add_patch(Rectangle((0, y0), 3.28, h, fc=RED, ec="black", lw=1.2))
    ax.add_patch(Rectangle((3.28, y0), 6.72, h, fc=GRAY, ec="black", lw=1.2))
    ax.text(1.64, y0 + h / 2,
            "869 people in reached households\nvisit effect: +12.0 pp each "
            "(the LATE)", ha="center", va="center", fontsize=10.5,
            color="white", fontweight="bold", linespacing=1.4)
    ax.text(3.28 + 3.36, y0 + h / 2,
            "1,781 people never reached\nvisit effect: 0 pp (no visit "
            "happened)", ha="center", va="center", fontsize=11,
            linespacing=1.4)
    ax.text(5.0, y0 + h + 0.25, "The 2,650 people assigned a visit",
            ha="center", va="bottom", fontsize=14, fontweight="bold")
    ax.add_patch(FancyBboxPatch((0.35, 0.15), 9.3, 1.25,
                                boxstyle="round,pad=0.02,rounding_size=0.15",
                                fc="#f4f6f7", ec=DARK, lw=1.2))
    ax.text(5.0, 0.775,
            "Average effect over everyone assigned (the ITT) = "
            "0.328 × 12.0 pp + 0.672 × 0 pp = 3.95 pp\n"
            "So to get back the effect on reached households: "
            "LATE = ITT ÷ 0.328 = 12.0 pp",
            ha="center", va="center", fontsize=11, linespacing=1.9)
    save(fig, "fig3_why_divide.png")


if __name__ == "__main__":
    fig1()
    fig2()
    fig3()
    print("done")
