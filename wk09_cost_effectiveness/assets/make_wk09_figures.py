"""Teaching figures for the Week 9 "Cost-effectiveness" notebook.

Run:  python make_wk09_figures.py
Writes fig1_cost_curve.png, fig2_updating.png and fig3_last_vote.png
next to this script. All numbers are illustrative (made up).
"""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch

OUT = os.path.dirname(os.path.abspath(__file__))

RED, GRAY, BLUE = "#e74c3c", "#95a5a6", "#3498db"
RED_T, BLUE_T = "#fadbd8", "#d6eaf8"
DARK, GREEN = "#2c3e50", "#1e8449"
CAPTION = "#7f8c8d"

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.size": 12,
    "axes.titlesize": 14,
    "axes.titleweight": "bold",
    "figure.facecolor": "white",
    "savefig.facecolor": "white",
    "text.color": DARK,
    "axes.labelcolor": DARK,
    "xtick.color": DARK,
    "ytick.color": DARK,
    "hatch.linewidth": 2.0,
})


def save(fig, name):
    fig.savefig(os.path.join(OUT, name), dpi=200, bbox_inches="tight",
                facecolor="white")
    plt.close(fig)


def clean(ax):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)


# ----------------------------------------------------------------- Figure 1
def fig1():
    COST = 0.50
    YMAX = 300
    X0, X1 = -0.6, 2.6

    def price(e):
        return COST / (e / 100)

    fig, ax = plt.subplots(figsize=(11, 7))
    fig.subplots_adjust(left=0.09, right=0.98, top=0.92, bottom=0.17)
    ax.set_xlim(X0, X1)
    ax.set_ylim(0, YMAX)
    clean(ax)

    # zone where no money buys a vote
    ax.axvspan(X0, 0, color="#ecf0f1", zorder=0, lw=0)
    ax.axvline(0, color=GRAY, lw=1, zorder=1)
    ax.text(-0.30, 288, "Effect zero or\nbelow: no money\nbuys a vote.\n"
            "Tactic B's worst\ncase lands here:\nnever.",
            ha="center", va="top", fontsize=10.5, color=DARK,
            linespacing=1.3, zorder=6)

    # the curve (positive effects, price <= cap only)
    e = np.linspace(COST / YMAX * 100, X1, 400)
    ax.plot(e, price(e), color=DARK, lw=2.6, zorder=4)
    ax.text(2.55, 36, "Cost per additional vote", ha="right", va="bottom",
            fontsize=11.5, color=DARK, fontweight="bold")

    yA, yB = 8, 24            # heights of the effect bars above the x-axis
    xa = X0   # y-axis bar position (A)

    # ---- Tactic A (blue)
    lo, est, hi = 0.5, 1.0, 1.5
    for x in (lo, est, hi):
        ax.plot([x, x], [yA, price(x)], color=BLUE, ls="--", lw=1.5, zorder=3)
        ax.plot([X0, x], [price(x)] * 2, color=BLUE, ls="--", lw=1.5, zorder=3)
    ax.plot([lo, hi], [yA, yA], color=BLUE, lw=8, solid_capstyle="butt",
            zorder=5)
    ax.plot(est, yA, "o", color="white", mec=BLUE, mew=2.5, ms=10, zorder=6)
    ax.plot([xa, xa], [price(hi), price(lo)], color=BLUE, lw=8,
            solid_capstyle="butt", zorder=5, clip_on=False)
    ax.plot(xa, price(est), "o", color="white", mec=BLUE, mew=2.5, ms=10,
            zorder=6, clip_on=False)
    ax.text(hi + 0.06, yA, "Effect +0.5 to +1.5 points", color=BLUE,
            fontsize=12, fontweight="bold", va="center", ha="left")
    ax.text(0.95, 122, "Price \\$33 to \\$100.\n\\$50 is not in the middle",
            color=BLUE, fontsize=12, fontweight="bold", va="bottom",
            ha="left", linespacing=1.25, zorder=6)
    ax.text(lo + 0.04, price(lo) + 6, "$100", color=BLUE, fontsize=11.5,
            ha="left", va="bottom")
    ax.text(est + 0.04, price(est) + 6, "$50", color=BLUE, fontsize=11.5,
            ha="left", va="bottom")
    ax.text(hi + 0.04, price(hi) + 6, "$33", color=BLUE, fontsize=11.5,
            ha="left", va="bottom")

    # ---- Tactic B (red)
    blo, best, bhi = -0.2, 0.5, 1.2
    ax.plot([bhi, bhi], [yB, price(bhi)], color=RED, ls="--", lw=1.5,
            zorder=3)
    ax.plot([X0, bhi], [price(bhi)] * 2, color=RED, ls="--", lw=1.5, zorder=3)
    ax.plot([blo, bhi], [yB, yB], color=RED, lw=8, solid_capstyle="butt",
            zorder=5)
    ax.plot(best, yB, "o", color="white", mec=RED, mew=2.5, ms=10, zorder=6)
    ax.text(blo - 0.04, yB, "Tactic B", color=RED, fontsize=12,
            fontweight="bold", va="center", ha="right")
    ax.text(bhi + 0.05, price(bhi) + 8, "$42", color=RED, fontsize=11.5,
            ha="left", va="bottom")

    # key for the two tactics
    ax.text(2.58, 275,
            "Tactic A: +1.0 points, 95% interval +0.5 to +1.5 \u2192 price \\$33 to \\$100",
            color=BLUE, fontsize=11.5, fontweight="bold", ha="right",
            va="center")
    ax.text(2.58, 248,
            "Tactic B: +0.5 points, 95% interval \u22120.2 to +1.2 \u2192 price \\$42 to never",
            color=RED, fontsize=11.5, fontweight="bold", ha="right",
            va="center")

    ax.set_xticks([-0.5, 0, 0.5, 1.0, 1.5, 2.0, 2.5])
    ax.set_xticklabels(["\u22120.5", "0", "+0.5", "+1.0", "+1.5", "+2.0", "+2.5"])
    ax.set_yticks(range(0, 301, 50))
    ax.set_yticklabels([f"${v}" for v in range(0, 301, 50)])
    ax.tick_params(labelsize=12)
    ax.set_xlabel("Effect on turnout (percentage points)", fontsize=12.5,
                  labelpad=8)
    ax.set_ylabel("Cost per additional vote", fontsize=12.5, labelpad=8)
    ax.set_title("A small effect makes an expensive vote", pad=12)

    fig.text(0.5, 0.025,
             "Cost per vote = cost per person ÷ effect (as a proportion), "
             "with cost per person = $0.50. A bigger effect\nmeans a cheaper "
             "vote, so the top of the effect interval is the bottom of the "
             "price interval. Illustrative numbers.",
             ha="center", va="center", fontsize=10.5, color=CAPTION)
    save(fig, "fig1_cost_curve.png")


# ----------------------------------------------------------------- Figure 2
def fig2():
    def summ(est, se):
        return est, se, est - 1.96 * se, est + 1.96 * se

    def fmt(est, lo, hi):
        return f"{est:+.1f}  [{lo:.1f}, {hi:.1f}]".replace("-", "\u2212")

    believed = summ(2.0, 0.5)
    panels = [("A precise new study", summ(1.0, 0.25)),
              ("A noisy new study", summ(1.0, 1.0))]

    fig, axes = plt.subplots(1, 2, figsize=(11.5, 5.6), sharex=True,
                             sharey=True)
    fig.subplots_adjust(left=0.15, right=0.99, top=0.88, bottom=0.27,
                        wspace=0.06)
    ylabels = ["What you believed", "New study", "What you believe now"]
    cols = [GRAY, BLUE, GREEN]

    for ax, (title, new) in zip(axes, panels):
        p0, p1 = 1 / believed[1] ** 2, 1 / new[1] ** 2
        w_new = p1 / (p0 + p1)
        post_est = (1 - w_new) * believed[0] + w_new * new[0]
        post_se = 1 / np.sqrt(p0 + p1)
        post = (post_est, post_se, post_est - 1.96 * post_se,
                post_est + 1.96 * post_se)
        rows = [believed, new, post]
        for i, (r, col) in enumerate(zip(rows, cols)):
            y = 2 - i
            est, se, lo, hi = r
            ax.plot([lo, hi], [y, y], color=col, lw=9, solid_capstyle="butt",
                    zorder=3)
            ax.plot(est, y, "o", color="white", mec=DARK, mew=2, ms=10,
                    zorder=4)
            ax.text(3.0 + 0.1 if hi < 3.0 else hi + 0.1, y,
                    fmt(est, round(lo, 1), round(hi, 1)),
                    va="center", ha="left", fontsize=12, color=DARK)
        ax.axvline(0, color=GRAY, ls=":", lw=1.3, zorder=1)
        ax.set_xlim(-1.2, 4.7)
        ax.set_ylim(-0.6, 2.6)
        ax.set_xticks([-1, 0, 1, 2, 3])
        ax.spines["bottom"].set_bounds(-1.2, 3.4)
        ax.set_yticks([2, 1, 0])
        ax.set_yticklabels(ylabels, fontsize=12.5)
        for tl, col in zip(ax.get_yticklabels(), cols):
            tl.set_color(DARK)
        ax.tick_params(axis="y", length=0)
        ax.tick_params(axis="x", labelsize=12)
        clean(ax)
        ax.spines["left"].set_visible(False)
        ax.set_title(title, pad=10)
        ax.set_xlabel("Effect on turnout (percentage points)", fontsize=12,
                      labelpad=8)
        ax.text(1.1, -0.255, f"New study gets {w_new * 100:.0f}% of the weight",
                transform=ax.get_xaxis_transform(), ha="center", va="top", fontsize=13,
                fontweight="bold", color=BLUE)
        print(title, "weight", w_new, "est", post_est, "se", post_se,
              "ci", post[2], post[3])
    axes[1].tick_params(axis="y", labelleft=False)

    fig.text(0.5, 0.025,
             "Each belief is weighted by its precision, 1 ÷ SE². The updated "
             "interval is narrower than either one alone. Illustrative "
             "numbers.",
             ha="center", va="center", fontsize=10.5, color=CAPTION)
    save(fig, "fig2_updating.png")


# ----------------------------------------------------------------- Figure 3
def fig3():
    COST_ROUND = 10000
    votes = np.array([200, 100, 50, 25])
    cpv = COST_ROUND / votes
    left = np.concatenate([[0], np.cumsum(votes)[:-1]])
    total = votes.sum()
    avg = COST_ROUND * 4 / total
    NEXT = 120

    fig, ax = plt.subplots(figsize=(11, 6.6))
    fig.subplots_adjust(left=0.09, right=0.98, top=0.92, bottom=0.19)
    ax.set_xlim(0, 400)
    ax.set_ylim(0, 450)
    clean(ax)

    for i in range(4):
        keep = i < 2
        ax.bar(left[i], cpv[i], width=votes[i], align="edge",
               color=DARK if keep else "#ecf0f1",
               edgecolor="white" if keep else GRAY,
               hatch=None if keep else "//", lw=1.5, zorder=3)
        cx = left[i] + votes[i] / 2
        lab = f"Round {i + 1}:\n${cpv[i]:.0f}" if i >= 2 else \
            f"Round {i + 1}: ${cpv[i]:.0f}"
        if keep:
            ax.text(cx, cpv[i] / 2, lab, ha="center", va="center",
                    color="white", fontsize=12, fontweight="bold", zorder=6)
        else:
            ax.text(cx, cpv[i] + 8, lab, ha="center", va="bottom",
                    color=DARK, fontsize=12, fontweight="bold",
                    linespacing=1.2, zorder=6)

    ax.axhline(NEXT, color=BLUE, lw=2.6, zorder=4)
    ax.text(4, NEXT + 7, "Next-best tactic: $120 a vote", color=BLUE,
            fontsize=12.5, fontweight="bold", ha="left", va="bottom",
            zorder=6)
    ax.axhline(avg, color=DARK, lw=2, ls="--", zorder=4)
    ax.text(4, avg - 8, f"Average of all four rounds: ${avg:.0f}", color=DARK,
            fontsize=12.5, fontweight="bold", ha="left", va="top", zorder=6)

    ax.axvline(300, color=RED, lw=2, zorder=5)
    ax.text(292, 440,
            "Stop after round 2:\nround 3 costs \\$200 a vote,\nmore than \\$120",
            color=RED, fontsize=12.5, fontweight="bold", ha="right",
            va="top", linespacing=1.3, zorder=6)

    ax.set_xticks([0, 100, 200, 300, int(total)])
    ax.set_yticks(range(0, 451, 50))
    ax.set_yticklabels([f"${v}" for v in range(0, 451, 50)])
    ax.tick_params(labelsize=12)
    ax.set_xlabel("Additional votes, cheapest first", fontsize=12.5,
                  labelpad=8)
    ax.set_ylabel("Cost of each additional vote", fontsize=12.5, labelpad=8)
    ax.set_title("The average vote hides the last vote", pad=12)

    fig.text(0.5, 0.03,
             "Keep buying a tactic while its next vote is the cheapest you "
             "can buy. The average (\\$107) looks better than \\$120,\nbut the "
             "last rounds cost \\$200 and \\$400 a vote. Illustrative numbers.",
             ha="center", va="center", fontsize=10.5, color=CAPTION)
    save(fig, "fig3_last_vote.png")


if __name__ == "__main__":
    fig1()
    fig2()
    fig3()
