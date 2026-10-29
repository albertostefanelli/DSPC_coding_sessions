"""Teaching figures for the Week 8 "Can we trust polls?" notebook.

Run:  python make_wk08_figures.py
Writes fig1_noise_vs_bias.png, fig2_share_vs_lead.png and
fig3_what_weighting_fixes.png next to this script.
"""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrowPatch
from matplotlib.colors import to_rgba

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


# ----------------------------------------------------------------- Figure 1
def fig1():
    rng = np.random.default_rng(8)
    TRUE = 0.48
    N_POLLS = 200
    sizes = [500, 5000]
    rows = [("Unbiased pollster", 0.48, BLUE, BLUE_T),
            ("Biased pollster", 0.51, RED, RED_T)]
    notes = {
        (0, 0): "Noisy but centered",
        (0, 1): "Tight and centered: right answer",
        (1, 0): "Noisy and off-center",
        (1, 1): "Tight but off-center:\na more precise wrong answer",
    }
    bins = np.arange(40, 56.01, 0.5)

    fig, axes = plt.subplots(2, 2, figsize=(11, 6.5), sharex=True)
    fig.subplots_adjust(left=0.10, right=0.99, top=0.93, bottom=0.14,
                        wspace=0.08, hspace=0.14)

    for r, (rlabel, p, col, tint) in enumerate(rows):
        for c, n in enumerate(sizes):
            ax = axes[r, c]
            polls = 100 * rng.binomial(n, p, N_POLLS) / n
            counts, _ = np.histogram(polls, bins=bins)
            ymax = counts.max()
            ax.hist(polls, bins=bins, color=col, alpha=0.85, ec="white",
                    lw=0.8, zorder=3)
            ax.set_ylim(0, ymax * 2.65)
            ax.set_xlim(40, 56)

            # spread band around the centre of the cloud
            half = 196 * np.sqrt(TRUE * (1 - TRUE) / n)  # in points
            ctr = polls.mean()
            ax.axvspan(ctr - half, ctr + half, color=tint, alpha=0.75,
                       zorder=1, lw=0, ymax=0.80)
            yb = ymax * 1.28
            ax.add_patch(FancyArrowPatch((ctr - half, yb), (ctr + half, yb),
                                         arrowstyle="<|-|>", mutation_scale=11,
                                         color=DARK, lw=1.4, shrinkA=0,
                                         shrinkB=0, zorder=5))
            ax.text(ctr, yb + ymax * 0.07,
                    f"±{half:.1f} points", ha="center",
                    va="bottom", fontsize=11, zorder=5,
                    bbox=dict(fc="white", ec="none", pad=1.5, alpha=0.8))

            # truth line
            ax.axvline(48, color=DARK, lw=2.2, zorder=4, ymax=0.80)
            ax.text(47.8, ymax * 1.95, "True share: 48%", ha="right",
                    va="top", fontsize=11, fontweight="bold", color=DARK,
                    zorder=6)

            # panel annotation
            ax.text(40.3, ymax * 2.63, notes[(r, c)], ha="left", va="top",
                    fontsize=11.5, fontweight="bold", color=col if r else DARK,
                    linespacing=1.3, zorder=6)

            ax.set_yticks([])
            for s in ("top", "right", "left"):
                ax.spines[s].set_visible(False)
            if r == 0:
                ax.set_title(f"Small polls (n = 500)" if n == 500
                             else "Large polls (n = 5,000)", pad=8)
            if r == 1:
                ax.set_xticks(range(40, 57, 4))
                ax.tick_params(axis="x", labelsize=12)
            else:
                ax.tick_params(axis="x", length=0)
            if c == 0:
                ax.text(-0.04, 0.5, rlabel, transform=ax.transAxes,
                        rotation=90, ha="right", va="center", fontsize=13,
                        fontweight="bold")

    fig.text(0.545, 0.058, "Democratic share in each simulated poll (%)",
             ha="center", va="center", fontsize=12.5)
    fig.text(0.545, 0.0,
             "Each panel: 200 simulated polls (taller bar = more polls). "
             "Bracket: where 95% of polls land.",
             ha="center", va="bottom", fontsize=10.5, color=CAPTION)
    save(fig, "fig1_noise_vs_bias.png")


# ----------------------------------------------------------------- Figure 2
def fig2():
    fig = plt.figure(figsize=(11, 4.6))
    gs = fig.add_gridspec(1, 2, width_ratios=[1, 2.3], left=0.03, right=0.985,
                          top=0.88, bottom=0.26, wspace=0.12)
    axA = fig.add_subplot(gs[0])
    axB = fig.add_subplot(gs[1])

    # ---- Panel A: one share
    centre, moe = 46.2, 3.1
    axA.errorbar([centre], [1], xerr=[moe], fmt="o", color=BLUE, ms=11,
                 lw=4, capsize=9, capthick=3, zorder=3)
    axA.text(centre, 1.28, "Dem share 46%,\nmargin of error ±3", ha="center",
             va="bottom", fontsize=12, fontweight="bold", linespacing=1.3)
    axA.set_xlim(38, 54)
    axA.set_ylim(-0.7, 3.0)
    axA.set_yticks([])
    axA.set_xticks([40, 44, 48, 52])
    axA.set_xticklabels(["40%", "44%", "48%", "52%"])
    axA.tick_params(axis="x", labelsize=12)
    axA.set_title("A candidate's share", pad=12)
    for s in ("top", "right", "left"):
        axA.spines[s].set_visible(False)

    # ---- Panel B: the lead
    rows = [("Phone poll\n(n = 1,001)", -3.9, 6.1, GRAY, "Statistical tie"),
            ("Online poll\n(n = 1,002)", 7.6, 6.0, BLUE,
             "Dem lead, but could be +2"),
            ("University poll\n(n ≈ 1,200)", 1.0, 5.7, GRAY,
             "Statistical tie")]
    axB.axvline(0, color=DARK, lw=3, ls=(0, (4, 3)), zorder=1)
    axB.text(0, 2.8, "Tie", ha="center", va="center", fontsize=12,
             fontweight="bold", bbox=dict(fc="white", ec="none", pad=2))

    def lead_txt(v):
        v1 = f"{abs(v):.1f}"
        return f"Dem +{v1}" if v > 0 else f"Rep +{v1}"

    for i, (name, est, m, col, lab) in enumerate(rows):
        y = 2 - i
        axB.errorbar([est], [y], xerr=[m], fmt="o", color=col, ms=12, lw=5,
                     capsize=9, capthick=3, zorder=3)
        axB.text(est, y + 0.2, lab, ha="center", va="bottom", fontsize=12,
                 fontweight="bold", color=DARK if col == BLUE else "#6c7a7b",
                 bbox=dict(fc="white", ec="none", pad=1.5))
        axB.text(est, y - 0.2, f"{lead_txt(est)}, ±{m:.1f}", ha="center",
                 va="top", fontsize=11, color=CAPTION,
                 bbox=dict(fc="white", ec="none", pad=1.5))
    axB.set_xlim(-12, 16)
    axB.set_ylim(-0.7, 3.0)
    axB.set_yticks([2, 1, 0])
    axB.set_yticklabels([r[0] for r in rows], fontsize=12)
    ticks = [-10, -5, 0, 5, 10, 15]
    axB.set_xticks(ticks)
    axB.set_xticklabels(["Rep +10", "Rep +5", "Tie", "Dem +5", "Dem +10",
                         "Dem +15"], fontsize=12)
    axB.tick_params(axis="y", length=0)
    axB.set_title("A lead", pad=12)
    for s in ("top", "right", "left"):
        axB.spines[s].set_visible(False)
    axB.text(0.5, -0.24,
             "Same sample size, about twice the uncertainty: one person "
             "switching sides moves the lead by two.",
             transform=axB.transAxes, ha="center", va="top", fontsize=11,
             style="italic", color=CAPTION)
    axB.text(0.5, -0.35, "Bars show the 95% margin of error.",
             transform=axB.transAxes, ha="center", va="top", fontsize=11,
             style="italic", color=CAPTION)
    save(fig, "fig2_share_vs_lead.png")


# ----------------------------------------------------------------- Figure 3
def fig3():
    fig = plt.figure(figsize=(11, 6.5))
    gs = fig.add_gridspec(2, 1, height_ratios=[1.0, 1.15], left=0.02,
                          right=0.98, top=0.93, bottom=0.04, hspace=0.22)
    axA = fig.add_subplot(gs[0])
    axB = fig.add_subplot(gs[1])

    # ---- Panel A: age mix
    groups = ["18–29", "30–44", "45–64", "65+"]
    sample = [6.0, 17.0, 35.9, 41.2]
    district = [18.0, 25.0, 32.1, 24.9]
    cols = [RED, "#f1948a", "#85c1e9", BLUE]
    tcols = ["white", DARK, DARK, "white"]
    weights = [3.00, 1.47, 0.90, 0.60]  # as given in the notebook

    axA.set_xlim(-17, 100)
    axA.set_ylim(-0.75, 2.3)
    axA.axis("off")
    axA.set_title("What weighting fixes: the age mix", pad=6)
    yS, yD, bh = 1.45, 0.0, 0.62

    def bar(y, vals, label):
        left = 0
        centres = []
        for g, v, col, tc in zip(groups, vals, cols, tcols):
            axA.add_patch(Rectangle((left, y - bh / 2), v, bh, fc=col,
                                    ec="white", lw=2, zorder=2))
            axA.text(left + v / 2, y, f"{v:.1f}%", ha="center",
                     va="center", fontsize=12, fontweight="bold", color=tc,
                     zorder=3)
            if y == yS:
                axA.text(left + v / 2, y + bh / 2 + 0.07, g, ha="center",
                         va="bottom", fontsize=12, fontweight="bold")
            centres.append(left + v / 2)
            left += v
        axA.text(-1.2, y, label, ha="right", va="center", fontsize=12,
                 fontweight="bold", linespacing=1.3)
        return centres

    cS = bar(yS, sample, "Phone poll\nsample")
    cD = bar(yD, district, "District\n(voter file)")

    for xs, xd, w in zip(cS, cD, weights):
        axA.add_patch(FancyArrowPatch((xs, yS - bh / 2 - 0.03),
                                      (xd, yD + bh / 2 + 0.03),
                                      arrowstyle="-|>", mutation_scale=13,
                                      color=DARK, lw=1.4, shrinkA=0,
                                      shrinkB=0, zorder=1))
        xm, ym = (xs + xd) / 2, (yS + yD) / 2
        axA.text(xm, ym, f"×{w:.2f}", ha="center", va="center", fontsize=12.5,
                 fontweight="bold", zorder=4,
                 bbox=dict(fc="white", ec=DARK, boxstyle="round,pad=0.25",
                           lw=1.0))
    axA.text(50, -0.58, "weight = district share ÷ sample share",
             ha="center", va="center", fontsize=12, style="italic",
             color=DARK)

    # ---- Panel B: dot grid
    ncol, nrow = 20, 9
    axB.set_xlim(-0.8, 50)
    axB.set_ylim(-3.0, nrow + 0.3)
    axB.axis("off")
    axB.set_title("What weighting cannot fix: who answers within a group",
                  pad=6)
    k = 0
    for r in range(nrow):
        for c in range(ncol):
            y = nrow - 1 - r
            if k < 60:
                axB.scatter(c, y, s=150, color=RED, ec=RED, lw=1.5, zorder=3)
            else:
                axB.scatter(c, y, s=150, facecolors="none",
                            edgecolors=to_rgba(GRAY, 0.55), lw=1.5, zorder=3)
            k += 1
    axB.text(21.2, 7.0, "60 answered", ha="left", va="center", fontsize=13,
             fontweight="bold", color=RED)
    axB.text(21.2, 6.1, "each now counts ×3\n(often the politically engaged)",
             ha="left", va="top", fontsize=12, linespacing=1.4)
    axB.text(21.2, 2.8, "120 never answered", ha="left", va="center",
             fontsize=13, fontweight="bold", color="#7f8c8d")
    axB.text(21.2, 1.9, "still missing\n(often the less engaged)", ha="left", va="top",
             fontsize=12, linespacing=1.4, color="#7f8c8d")
    axB.text(-0.5, -1.3,
             "Each circle is one young voter that a fair poll of 1,000 "
             "would include (180 in all).",
             ha="left", va="center", fontsize=11, color=CAPTION)
    axB.text(-0.5, -2.4,
             "Weighting makes the 60 three times louder. It does not find "
             "the missing 120.",
             ha="left", va="center", fontsize=12.5, style="italic",
             color=DARK)
    save(fig, "fig3_what_weighting_fixes.png")


if __name__ == "__main__":
    fig1()
    fig2()
    fig3()
    print("done")
