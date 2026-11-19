"""Build the Week 11 student and solutions notebooks.

Run:  python3 build_wk11.py [--no-figures] [--force]

Refuses to overwrite a notebook that changed since the last build (hand edits):
sync those edits into this script first, or pass --force after backing up.
Hashes of the last build are kept in last_build_hashes.json next to this script.
Figures 1 and 2 were approved by the instructor on 2026-11-18 and are included by default;
--no-figures leaves them out. Any new figure must be approved before it is added here.
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WEEK = os.path.dirname(HERE)
STUDENT = os.path.join(WEEK, "wk11_codingsession.ipynb")
SOLUTIONS = os.path.join(WEEK, "wk11_codingsession_solutions.ipynb")
STAMP = os.path.join(HERE, "last_build_hashes.json")
ANSWERS_FILE = os.path.join(HERE, "wk11_answers.json")
FIGURES = "--no-figures" not in sys.argv   # Figures 1-2 approved 2026-11-18
FORCE = "--force" in sys.argv

REPO = "https://raw.githubusercontent.com/albertostefanelli/DSPC_coding_sessions/"
ASSETS = REPO + "refs/heads/master/wk11_forecasts_and_calibration/assets/previews/"
COLAB = "https://colab.research.google.com/github/albertostefanelli/DSPC_coding_sessions/blob/master/wk11_forecasts_and_calibration/"
NOTES = "https://github.com/albertostefanelli/DSPC_coding_sessions/blob/master/wk11_forecasts_and_calibration/data/README.md"
SOURCE = "https://github.com/fivethirtyeight/checking-our-work-data"


def md(cid, text):
    # Colab and Jupyter read $...$ in markdown as LaTeX math, so escape every dollar sign.
    return {"cell_type": "markdown", "id": cid, "metadata": {},
            "source": text.strip("\n").replace("$", "\\$")}


def code(cid, text):
    return {"cell_type": "code", "id": cid, "metadata": {}, "execution_count": None,
            "outputs": [], "source": text.strip("\n")}


STUB = """
**Your interpretation:** Write three to five short sentences. Answer each part of the question and quote the numbers you use.
"""

# ---------------------------------------------------------------- Intro
INTRO = md("intro", """
A **forecast** in this session is a probability. A 70% chance of winning is not a promise: it says that in races like this one, the candidate should win about 7 times in 10.

**Part 1** tests a real forecaster's record. **Part 2** uses probabilities to make a campaign decision. Each step introduces an idea, shows it in code, and interprets the result. Examples labeled **hypothetical** use made-up numbers. Three short exercises at the end practice the main ideas.
""")

# ---------------------------------------------------------------- Part 1
P1_RECORD = md("p1-record", """
## Part 1. Testing a forecaster

### 1. A probability is a claim you test with a record

A forecaster gives a candidate a 70% chance, and the candidate loses. Was the forecaster wrong? Not necessarily: a 70% candidate should lose about 3 times in 10. **One race can never confirm or refute a probability.** What we can test is a **record** of many forecasts. If a forecaster said 70% in 100 races, about 70 of its candidates should have won.

We will test **FiveThirtyEight**, a well-known election forecaster, in **1,373** races: House and Senate in 2018, 2020 and 2022, and governor in 2018 and 2022 (88% are House races). Each row is one race with at least two candidates, exactly one of them a Democrat.

| Column | Meaning |
|---|---|
| `year`, `office` | 2018, 2020 or 2022; `House`, `Senate` or `Governor`. |
| `state`, `district` | Where the race was held (`district` is 0 for statewide races). |
| `special` | `True` for a special Senate election. |
| `candidate` | The Democratic candidate. |
| `dem_prob` | FiveThirtyEight's Election-Day chance that the Democrat would win, from 0 to 1. |
| `dem_won` | 1 if the Democrat won, 0 if not. |

We use the middle of FiveThirtyEight's three model versions, called "Classic", in every year, so a number you find online may differ.

**Source:** FiveThirtyEight, "How Good Are FiveThirtyEight Forecasts?" data, [github.com/fivethirtyeight/checking-our-work-data](""" + SOURCE + """), CC BY 4.0. The [data notes](""" + NOTES + """) record how the file was built. In Colab, save your own copy and run the cells in order; the data load from the internet.
""")

SETUP = code("setup", """
# pandas works with tables, numpy with numbers, and matplotlib draws charts.
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Load FiveThirtyEight's final forecasts from the course repository (you need to be online).
# Source: FiveThirtyEight "checking our work" data,
# github.com/fivethirtyeight/checking-our-work-data (CC BY 4.0).
# Python joins the two quoted strings inside the parentheses into one address.
races = pd.read_csv(
    'https://raw.githubusercontent.com/albertostefanelli/DSPC_coding_sessions/'
    'master/wk11_forecasts_and_calibration/data/fivethirtyeight_final_forecasts_2018_2022.csv'
)

print('Races:', len(races))
races.head()
""")

P1_UPSET_CODE = code("p1-upset-code", """
# One race: Iowa's 2nd District in 2020.
# A condition inside races[...] keeps only the rows where it is True; & means "and".
races[(races['year'] == 2020) & (races['state'] == 'IA') & (races['district'] == 2)]
""")

P1_UPSET_RESULT = md("p1-upset-result", """
FiveThirtyEight gave the Democrat, Rita Hart, a **94%** chance, and she lost. A 94% favorite should still lose about 6 times in 100, so this race alone cannot show that the forecast was wrong. We need to know how often its favorites lost **across many races**. The record must also be long: a presidential forecaster gets one national race every four years, far too few to show whether it is any good.
""")

P1_CALIBRATION = md("p1-calibration", """
### 2. Calibration: do the numbers mean what they say?

A forecaster is **calibrated** if, among all the events it called X% likely, about X% happen. To check, group the forecasts into ranges (0–10%, 10–20%, and so on) and compare each range's **average forecast** with the **share that happened**. On a calibration plot, calibrated points lie on the diagonal.

When the points miss, the direction matters. Of all the events a forecaster calls 80% likely, about 80 in 100 should happen.

- If only 60 happen, the forecaster is **overconfident**: its numbers are too far from 50%.
- If 98 happen, it is **underconfident**: its numbers are too close to 50%.
""")

FIG1 = md("fig1", """
![A calibration plot with three curves: the diagonal for a calibrated forecaster, a flatter curve for an overconfident one, and a steeper curve for an underconfident one.](""" + ASSETS + """fig1_over_underconfident.png)

*Figure 1. Of the events called 80% likely, about 80 in 100 happen for a calibrated forecaster, 60 for an overconfident one, and 98 for an underconfident one. Hypothetical illustration.*
""")

P1_CALIBRATION_2 = md("p1-calibration-2", """
In Week 10 we called a point below the diagonal **overprediction** and a point above it **underprediction**. An overconfident forecaster overpredicts its favorites (right side) and underpredicts its underdogs (left side). An underconfident forecaster does the reverse.

The code builds the calibration table. A **positive gap** means the forecast was higher than what happened.
""")

P1_CAL_CODE = code("p1-cal-code", """
# Put each forecast into one of ten ranges. include_lowest=True keeps exact zeros.
# Each range includes its upper edge, so a forecast of exactly 1 lands in the last range.
ranges = [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1]
races['forecast_range'] = pd.cut(races['dem_prob'], ranges, include_lowest=True)

# groupby splits the races by range; mean() averages each selected column.
# The mean of dem_prob is the average forecast. The mean of dem_won (0 or 1) is the share who won.
# observed=True leaves out empty ranges.
calibration = races.groupby('forecast_range', observed=True)[['dem_prob', 'dem_won']].mean()
# size() counts the races in each range.
calibration['races'] = races.groupby('forecast_range', observed=True).size()
# Gap in percentage points: positive means the forecast was higher than what happened.
calibration['gap_pp'] = 100 * (calibration['dem_prob'] - calibration['dem_won'])

# Every race must be in exactly one range.
assert calibration['races'].sum() == len(races)
calibration[['races', 'dem_prob', 'dem_won', 'gap_pp']].round(3)
""")

P1_PLOT_CODE = code("p1-plot-code", """
# Each dot is one range of forecasts. Bigger dots stand for more races.
fig, ax = plt.subplots(figsize=(6, 5))
ax.plot([0, 1], [0, 1], '--', color='gray', label='Forecast equals what happened')
ax.scatter(calibration['dem_prob'], calibration['dem_won'],
           s=30 + 180 * calibration['races'] / calibration['races'].max(),
           color='#2463a6', edgecolor='white')
ax.set(xlabel='Average forecast (chance the Democrat wins)',
       ylabel='Share of Democrats who won',
       xlim=(0, 1), ylim=(0, 1), title='FiveThirtyEight final forecasts, 2018-2022')
ax.legend(loc='upper left')
plt.tight_layout()
plt.show()
""")

P1_POOL_MD = md("p1-pool-md", """
The two end ranges hold over 500 races each and sit almost on the diagonal. The middle ranges hold only 30 to 58 races each, so any one of them can miss by chance (the 0.6–0.7 range sits below the diagonal while its neighbors sit above it). To see the pattern, look from the **favorite's** side: for each race, take the chance FiveThirtyEight gave whichever candidate it favored, and pool the races where that chance was between 50% and 90%.
""")

P1_POOL_CODE = code("p1-pool-code", """
# The favorite is the Democrat when dem_prob is at least 0.5; otherwise it is the Republican.
# np.where(condition, value_if_true, value_if_false) picks one of two values for each race.
races['fav_prob'] = np.where(races['dem_prob'] >= 0.5, races['dem_prob'], 1 - races['dem_prob'])
races['fav_won'] = np.where(races['dem_prob'] >= 0.5, races['dem_won'], 1 - races['dem_won'])

# Pool the races where the favorite was given more than 50% and at most 90%.
middle = races[(races['fav_prob'] > 0.5) & (races['fav_prob'] <= 0.9)]
print('Races:', len(middle),
      "| favorite's average chance:", round(middle['fav_prob'].mean(), 3),
      '| share the favorite won:', round(middle['fav_won'].mean(), 3))

# The same comparison in each election year.
middle.groupby('year')[['fav_prob', 'fav_won']].mean().round(3)
""")

P1_POOL_RESULT = md("p1-pool-result", """
In these **302** races, FiveThirtyEight gave the favorite **72.3%** on average, and the favorite won **80.5%** of the time. The same is true in each year: 73.3% vs 84.2% in 2018, 72.4% vs 78.5% in 2020, and 70.9% vs 77.9% in 2022. Favorites won more often than forecast, so underdogs won less often: FiveThirtyEight's forecasts were **underconfident**, too close to 50%. This describes groups of races, not every single forecast.
""")

P1_DISCRIMINATION = md("p1-discrimination", """
### 3. Calibrated is not enough

The **base rate** is how often this kind of event happens; here the Democrat won about half the races. A lazy forecaster could give every Democrat that same chance. Its average forecast would equal the share who won, so it would be perfectly calibrated. It would also be useless, because it never says *which* races the Democrat is likely to win.

What it lacks is **discrimination**: separating the more likely events from the less likely ones. A useful forecaster is calibrated *and* gives high numbers to races that end up won and low numbers to races that end up lost. The code below computes the base rate and compares FiveThirtyEight's average forecast in races the Democrat won and lost.
""")

FIG2 = md("fig2", """
![Two dot plots of twenty races. Forecaster A puts every race at 50%. Forecaster B puts ten races at 10% and ten at 90%, with the winners mostly at 90%.](""" + ASSETS + """fig2_calibrated_not_enough.png)

*Figure 2. Both forecasters are calibrated, but only Forecaster B separates likely winners from likely losers. Hypothetical illustration.*
""")

P1_DISC_CODE = code("p1-disc-code", """
# The base rate: the share of all races the Democrat won.
base_rate = races['dem_won'].mean()
print('Base rate (% of races the Democrat won):', round(100 * base_rate, 1))

# Average forecast, separately for races the Democrat lost (0) and won (1).
races.groupby('dem_won')['dem_prob'].mean().round(3)
""")

P1_DISC_RESULT = md("p1-disc-result", """
The Democrat won **51.0%** of the races, so the lazy forecaster gives winners and losers the same 0.510. FiveThirtyEight gave the Democrats who went on to win **0.924** on average, and those who lost **0.087**. It separated winners from losers very well, helped by the many races that were easy to call.
""")

P1_BRIER = md("p1-brier", """
### 4. The Brier score

The **Brier score** is the average of (forecast − outcome)², where the outcome is 1 if the event happened and 0 if it did not. Lower is better, and 0 is perfect. Squaring makes big misses count much more than small ones, so **a confident forecast that turns out wrong is penalized heavily**.

> **Hypothetical example.** A forecaster calls four races.
>
> | Race | Forecast | Happened? | (forecast − outcome)² |
> |---|---|---|---|
> | 1 | 0.7 | Yes (1) | (0.7 − 1)² = 0.09 |
> | 2 | 0.9 | No (0) | (0.9 − 0)² = 0.81 |
> | 3 | 0.2 | No (0) | (0.2 − 0)² = 0.04 |
> | 4 | 0.6 | Yes (1) | (0.6 − 1)² = 0.16 |
>
> Brier score = (0.09 + 0.81 + 0.04 + 0.16) ÷ 4 = **0.275**. The one confident miss, race 2, contributes most of it.

Compare a Brier score with always guessing the **base rate**. In the example 2 of 4 events happened, so guessing 0.5 scores (0.5)² = 0.25 in every race: a Brier score of **0.25**, the **floor to beat**. Because of one confident miss, our forecaster's 0.275 is *worse* than the floor.

The code scores FiveThirtyEight and the lazy base-rate forecaster on all races, then both again on the harder races alone.
""")

P1_BRIER_CODE = code("p1-brier-code", """
# (forecast - outcome) ** 2 for every race; .mean() averages over all races.
brier_538 = ((races['dem_prob'] - races['dem_won']) ** 2).mean()
# The lazy forecaster says base_rate in every race.
brier_base = ((base_rate - races['dem_won']) ** 2).mean()
print('All races   | Brier, FiveThirtyEight:', round(brier_538, 4),
      '| Brier, always guess base rate:', round(brier_base, 4))

# The harder races: FiveThirtyEight gave the Democrat between 5% and 95%.
hard_races = races[races['dem_prob'].between(0.05, 0.95)]
hard_base_rate = hard_races['dem_won'].mean()   # the floor uses these races' own base rate
print('Harder races:', len(hard_races), 'of', len(races))
print('Harder races | Brier, FiveThirtyEight:', round(((hard_races['dem_prob'] - hard_races['dem_won']) ** 2).mean(), 4),
      '| Brier, always guess base rate:', round(((hard_base_rate - hard_races['dem_won']) ** 2).mean(), 4))
""")

P1_BRIER_RESULT = md("p1-brier-result", """
FiveThirtyEight scores **0.0338**, far below the **0.2499** of always guessing the base rate (almost exactly 0.25, because Democrats won about half the races). But here the floor is a low bar. About three races in four were easy calls, below 5% or above 95%. They add very little error, and because there are so many of them they pull the average down. In the **376** harder races, FiveThirtyEight scores **0.1205** against a floor of **0.2488** for those races: still better, but much less impressive.
""")

P1_RATINGS = md("p1-ratings", """
### 5. Race ratings are forecasts too

Many campaigns never see a probability. They see a **race rating** such as Solid, Likely, Lean or Toss-up, from analysts like the Cook Political Report, and use it to decide where to spend. A rating is a forecast in words, so we can test it the same way: in races labeled Likely, how often did the favorite win?

FiveThirtyEight turned its own probabilities into labels, using the favorite's chance of winning:

| Label | Favorite's chance of winning |
|---|---|
| Toss-up | under 60% |
| Lean | 60% to under 75% |
| Likely | 75% to under 95% |
| Solid | 95% or more |

Unlike a weather forecast, a rating can affect what it predicts. If donors read that a race is Solid and give elsewhere, the underdog becomes even less likely to win. **A rating can change the race it forecasts.**

The code labels each race from `fav_prob` (Section 2), then splits the Toss-ups by year.
""")

P1_RATINGS_CODE = code("p1-ratings-code", """
# pd.cut with labels= gives each range a name. The edges are FiveThirtyEight's cutoffs.
# No race sits exactly on a cutoff, so the default ranges (which include their upper edge)
# match the table above.
rating_edges = [0.5, 0.6, 0.75, 0.95, 1]
races['rating'] = pd.cut(races['fav_prob'], rating_edges, include_lowest=True,
                         labels=['Toss-up', 'Lean', 'Likely', 'Solid'])
assert races['rating'].notna().all()   # every race got a label

# value_counts counts the races with each label; sort=False keeps the labels in order.
races['rating'].value_counts(sort=False)
""")

P1_TOSSUP_CODE = code("p1-tossup-code", """
# Toss-up races only, split by election year.
tossups = races[races['rating'] == 'Toss-up']
# For each year: how many Toss-ups the Democrat won (the sum of the 0/1 column dem_won),
# the number of Toss-ups, and the average chance FiveThirtyEight gave the Democrat.
by_year = pd.DataFrame({'dem_wins': tossups.groupby('year')['dem_won'].sum()})
by_year['races'] = tossups.groupby('year').size()
by_year['avg_dem_prob'] = tossups.groupby('year')['dem_prob'].mean()
by_year.round(3)
""")

P1_TOSSUP_RESULT = md("p1-tossup-result", """
Only **66** races are Toss-ups, and Democrats won **36** of them, close to a coin flip. But the years look nothing alike: Democrats won **14 of 24** in 2018, **2 of 19** in 2020 and **20 of 23** in 2022, with an average forecast near 50% each year. If each Toss-up were a separate coin flip, 2 of 19 would almost never happen. Races in the same year can move together, because whatever shifts an election can shift many close races at once. So 1,373 races are fewer independent tests than they seem: judge a forecaster across several elections.
""")

P1_BOX = md("p1-box", """
> **Before you trust a forecast, ask:**
> - **Record:** many forecasts across several elections, or one race?
> - **Calibration:** does each range's share that happened match its average forecast, and how many races are in it?
> - **Pattern or noise:** a consistent over- or underconfidence, or one small range missing by chance?
> - **Floor:** does the Brier score beat guessing the base rate, and is that a low bar?
> - **Ratings:** is a label a forecast with a record behind it, and could it have changed the race?
""")

# ---------------------------------------------------------------- Part 2
P2_SCENARIO = md("p2-scenario", """
## Part 2. From probabilities to a decision

People act on forecasts. In this part a group uses probabilities to decide whether to endorse. The scenario and every number in it are **hypothetical**.

A transit group wants the next county executive to sign a bus-lane plan, which the executive can do alone. The seat is open: one party holds a primary, and its nominee faces the other party in November. The group can endorse in the primary and send its volunteers, or stay neutral. Its analyst gives these numbers:

| Candidate | Wins the primary | Wins November, if nominated | Signs how much of the plan |
|---|---|---|---|
| Ortiz (front-runner) | 70% | 50% | 30% |
| Hale (insurgent) | 30% | 60% | 100% |

Ortiz will fund one bus corridor, worth 30% of the plan; Hale promises all of it; the other party would sign none. Hale's campaign tells the group: *"The analyst gives us a 60% chance in November and Ortiz only 50%. We're the stronger candidate."*
""")

P2_EV = md("p2-ev", """
### 6. Conditional probability and expected value

Hale's 60% is a **conditional probability**: his chance of winning in November *if* he first wins the primary. To take office he has to win both, so multiply: 30% × 60% = 18%. Quoting the 60% without the 30% it depends on makes Hale look stronger than he is.

The group does not care who wins for its own sake; it wants the plan signed. So multiply each outcome's chance by the share of the plan it delivers, and add up. The result is an **expected value**: each outcome weighted by how likely it is.
""")

P2_EV_CODE = code("p2-ev-code", """
# Chance of winning the primary
p_ortiz = 0.70
p_hale = 0.30

# Chance of winning November, if nominated (conditional chances)
nov_ortiz = 0.50
nov_hale = 0.60

# Share of the plan each one would sign
signs_ortiz = 0.30
signs_hale = 1.00

# Chance of taking office = chance of winning the primary x chance of winning November if nominated.
office_ortiz = p_ortiz * nov_ortiz
office_hale = p_hale * nov_hale
office_other = 1 - office_ortiz - office_hale   # whatever is left: the other party wins

print('Ortiz takes office (%):     ', round(100 * office_ortiz, 1))
print('Hale takes office (%):      ', round(100 * office_hale, 1))
print('Other party takes office (%):', round(100 * office_other, 1))

# Expected value of staying neutral: chance x share signed for every outcome, added up.
# The other party signs nothing, so its term is 0.
neutral = office_ortiz * signs_ortiz + office_hale * signs_hale + office_other * 0
print('Stay neutral, expected share of the plan (%):', round(100 * neutral, 1))

# What would Ortiz have to sign to be worth as much as Hale? office_ortiz x v = office_hale x signs_hale
print('Share Ortiz would need to sign to match Hale (%):',
      round(100 * office_hale * signs_hale / office_ortiz, 1))
""")

P2_EV_RESULT = md("p2-ev-result", """
| Outcome | Chance | Share of the plan signed | Chance × share |
|---|---|---|---|
| Ortiz takes office | 35% | 30% | 10.5% |
| Hale takes office | 18% | 100% | 18.0% |
| Other party takes office | 47% | 0% | 0% |
| **Total** | 100% | | **28.5%** |

Staying neutral is worth an expected **28.5%** of the plan. Ortiz is almost twice as likely to take office, but Hale delivers far more. To match Hale, Ortiz would have to sign **51.4%** of the plan; she has committed to 30%.
""")

P2_ENDORSE = md("p2-endorse", """
### 7. What an endorsement does

An endorsement does not pick the winner. All it can do is move some primary chance from Ortiz to Hale; call it **d points**, so 70% becomes 70 − d and 30% becomes 30 + d. These are points of *chance of winning the primary*, not vote share. Two questions decide whether endorsing Hale pays.

1. **What does it cost before it moves anyone?** Endorsing Hale **crosses** Ortiz: you backed her opponent. Suppose that if she wins anyway, she funds 20% of the plan instead of 30% (we made this number up). At d = 0, all endorsing does is cut what Ortiz would sign.
2. **What is each moved point worth?** A point that moves to Hale gains 60% × 100% = 0.60 points of the plan. Taking it from a crossed Ortiz loses 50% × 20% = 0.10. Net: 0.50 per point.

The **break-even** is the d at which endorsing is worth exactly as much as staying neutral: how far behind endorsing starts, divided by what each point is worth.
""")

P2_ENDORSE_CODE = code("p2-endorse-code", """
# What Ortiz signs if you endorse Hale (we made this number up).
signs_ortiz_crossed = 0.20

# Endorse Hale, but move no one (d = 0): the primary stays 70-30.
endorse = p_ortiz * nov_ortiz * signs_ortiz_crossed + p_hale * nov_hale * signs_hale
behind = (neutral - endorse) * 100        # in percentage points of the plan
print('Endorse Hale, d = 0 (%):           ', round(100 * endorse, 1))
print('Behind staying neutral by (points):', round(behind, 1))

# Move one point of primary chance from Ortiz to Hale:
# Hale gains nov_hale x signs_hale, and a crossed Ortiz loses nov_ortiz x signs_ortiz_crossed.
per_point = nov_hale * signs_hale - nov_ortiz * signs_ortiz_crossed
print('One moved point is worth:', round(per_point, 3))

# Break-even: how many points must move to make up the gap?
break_even = behind / per_point
print('Break-even:', round(break_even, 1), 'points of primary chance')
""")

P2_MOVES_CODE = code("p2-moves-code", """
# What endorsing Hale is worth for a few values of d (one row per value).
# Each moved point adds per_point to what you get at d = 0.
moves = pd.DataFrame({'points_moved': [0, 4, 7, 10]})
moves['endorse_hale'] = 100 * endorse + per_point * moves['points_moved']
moves['stay_neutral'] = 100 * neutral
moves.round(1)
""")

P2_ENDORSE_RESULT = md("p2-endorse-result", """
Endorsing Hale starts **3.5** points behind staying neutral (25.0% vs 28.5% of the plan), and each moved point is worth **0.5**. It pays only if the endorsement moves Hale's chance of winning the primary by more than **7 points**, from 30% to above 37%. No forecast can tell you whether it will. That needs evidence on what endorsements actually do.
""")

P2_SENSITIVITY = md("p2-sensitivity", """
### 8. How solid is 7 points?

Every input is a guess: four probabilities, two shares, and one number we made up. Before acting on a break-even, **change one input at a time** and see how far it moves. Each row in the code changes one input and keeps the rest:

- **Ortiz primary 80%:** the forecast is off by 10 points.
- **Crossed Ortiz signs 10%:** crossing her costs more than we assumed.
- **Hale November 55% if endorsed:** the other party attacks Hale as the transit group's candidate (made up).
""")

P2_SENS_CODE = code("p2-sens-code", """
# One row per version of the inputs. Each row changes one input; the others stay as before.
checks = pd.DataFrame({
    'change': ['none', 'Ortiz primary 80%', 'crossed Ortiz signs 10%', 'Hale November 55% if endorsed'],
    'p_ortiz': [0.70, 0.80, 0.70, 0.70],
    'crossed_share': [0.20, 0.20, 0.10, 0.20],
    'nov_hale_endorsed': [0.60, 0.60, 0.60, 0.55],
})
checks['p_hale'] = 1 - checks['p_ortiz']

# The same formulas as before, applied to every row at once (in % of the plan).
# Staying neutral uses the original November chances and shares.
checks['neutral'] = 100 * (checks['p_ortiz'] * nov_ortiz * signs_ortiz
                           + checks['p_hale'] * nov_hale * signs_hale)
# Endorsing Hale at d = 0: Ortiz is crossed, and Hale's November chance may fall.
checks['endorse'] = 100 * (checks['p_ortiz'] * nov_ortiz * checks['crossed_share']
                           + checks['p_hale'] * checks['nov_hale_endorsed'] * signs_hale)
checks['behind'] = checks['neutral'] - checks['endorse']
checks['per_point'] = checks['nov_hale_endorsed'] * signs_hale - nov_ortiz * checks['crossed_share']
checks['break_even'] = checks['behind'] / checks['per_point']
# round() with a dictionary rounds each column to its own number of decimals.
checks[['change', 'neutral', 'endorse', 'behind', 'per_point', 'break_even']].round(
    {'neutral': 1, 'endorse': 1, 'behind': 1, 'per_point': 2, 'break_even': 1})
""")

P2_SENS_RESULT = md("p2-sens-result", """
The made-up input matters more than the forecast. A 10-point forecast error moves the break-even from **7.0** to **8.0**; a bigger cost of crossing Ortiz moves it to **12.7**. Pin down that cost before you worry about the forecast.

In the last row two things get worse at once. You start further behind (**5.0** points instead of 3.5), because Hale wins November less often, and each moved point is worth less (**0.45** instead of 0.5), because it goes to a weaker nominee. The break-even rises to **11.1**.

Two more cautions. Compare endorsing with your **best alternative**, such as saving the volunteers for November, not with doing nothing: if the alternative is worth more than staying neutral, endorsing starts further behind it, and the break-even rises. And keep the precision honest. Even the one decimal in this table claims more than we know; a break-even built from a handful of guesses is "about 11".
""")

P2_BOX = md("p2-box", """
> **Before you quote a break-even, ask:**
> - **Conditional:** is each chance for the whole path, or one step? Multiply first.
> - **Expected value:** did you count every outcome, including those worth nothing?
> - **Units:** are the moved points primary *chance*, not vote share?
> - **One at a time:** which input moves the answer most: a forecast, or a made-up number?
> - **Alternative and precision:** are you comparing with your best alternative, and are you reporting more digits than your guesses support?
""")

# ---------------------------------------------------------------- Part 3
PART3_INTRO = md("part3", """
## Part 3. Three short exercises

Each exercise needs a few lines of code and **three to five sentences** of interpretation that quote your numbers. Exercises 1 and 2 use `races` from Part 1, including the `fav_prob`, `fav_won` and `rating` columns from Section 5; Exercise 3 stands on its own. The quoted claims and the Exercise 3 scenario are hypothetical; the forecasts are real.
""")

EX1_MD = md("ex1", """
### Exercise 1. Was "Solid Republican" wrong?

In 2022, FiveThirtyEight gave Marie Gluesenkamp Perez, the Democrat in Washington's 3rd District, a **4%** chance (Classic version), which put the race in its **Solid** category. She won. A donor writes:

> *"FiveThirtyEight called that seat Solid Republican and got it badly wrong. Their ratings can't be trusted."*

The ratings use the favorite's chance of winning: **Toss-up** under 60%, **Lean** 60% to under 75%, **Likely** 75% to under 95%, **Solid** 95% or more. An **upset** is a race the favorite lost.

**Calculate:** for each rating, the number of races, the favorite's average chance (`fav_prob`) and the share the favorite won (`fav_won`). Add the **actual upsets** and the **expected upsets** the forecasts imply: races × (1 − average chance). For example, 100 races at an average chance of 90% imply 10 upsets.

**Coding guide.** Group by `rating` as in Section 2: `.mean()` gives the averages and `.size()` counts the races. A favorite that won a share s of n races lost n × (1 − s) of them.

**Interpret:** does the Washington result show that FiveThirtyEight was wrong? Using the **Likely** row, were the ratings overconfident, underconfident or about right? Can too few upsets also be a problem? Finally, if a Solid label leads donors to give up on the underdog, how could that make a rating's record look better than its forecasting skill?
""")

EX1_CODE = code("ex1-code", """
# For each rating: the number of races, the favorite's average chance, and the share the favorite won.
# Add actual upsets (races the favorite lost) and expected upsets: races x (1 - average chance).
# Print the table rounded to 3 decimals.
""")

EX2_MD = md("ex2", """
### Exercise 2. The pundit who never hedges

A cable-news pundit names a winner in every race and says she is 100% sure. Looking back at the close races, she says:

> *"I picked the same winner as FiveThirtyEight in every close race, so I was right exactly as often. And I don't hedge. My forecasts are just as good as theirs."*

Use the **close races**, where FiveThirtyEight gave the Democrat between 25% and 75%: `close = races[races['dem_prob'].between(0.25, 0.75)].copy()` (`.copy()` makes a separate table you can add columns to).

**Coding guide.** `(close['dem_prob'] > 0.5).astype(int)` is the pundit's forecast for the Democrat: 1 means "the Democrat wins for sure", 0 means "the Republican wins for sure" (`astype(int)` turns True/False into 1/0). The mean of `(forecast == outcome)` is the share called correctly. The Brier formula works for forecasts of 0 or 1 too.

**Calculate:** the number of close races, the share the pundit called correctly, and the Brier scores of FiveThirtyEight, the pundit, and always guessing the close races' base rate (the share of close races the Democrat won).

**Interpret:** with the same picks, why is her Brier score worse than FiveThirtyEight's, and even worse than guessing the base rate? Why does it equal the share of races she called wrong? Is she overconfident or underconfident? What does FiveThirtyEight's score, compared with the base rate, say about how hard close races are to call?
""")

EX2_CODE = code("ex2-code", """
# Keep the close races (Democrat given between 25% and 75%).
# The pundit's forecast for the Democrat: 1 if FiveThirtyEight favored the Democrat, otherwise 0.
# Report: the number of close races, the share the pundit called correctly, and the Brier scores
# of FiveThirtyEight, the pundit, and always guessing the close races' base rate.
""")

EX3_MD = md("ex3", """
### Exercise 3. Endorse the front-runner, or wait for November?

Another hypothetical group wants the next mayor to sign a clean-water plan. Its analyst gives these numbers:

| Candidate | Wins the primary | Wins November, if nominated | Signs how much of the plan |
|---|---|---|---|
| Moreno (front-runner) | 80% | 40% | 75% (50% if the group endorses Sato) |
| Sato (insurgent) | 20% | 70% | 100% |

Sato has committed in writing to sign the whole plan, whatever the group does. The supplied code computes staying neutral, endorsing Sato at d = 0, the value of a point moved to Sato, and the break-even. Two board members disagree:

> *Board member 1: "Moreno is four times as likely to win the primary. Endorse her. Backing the likely winner can't hurt."*
>
> *Board member 2: "Stay neutral and save our volunteers for November. They would add 5 points to the November chance of whoever is nominated, and that beats endorsing Sato."*

The volunteers can be used only once, in the primary or in November. The 5 points are made up.

**Calculate:**
1. The value of one point of primary chance moved from Sato to Moreno, if the group endorses Moreno (this does not change what Sato signs).
2. The expected share of the plan under the **November plan**: stay neutral, and add 0.05 to both November chances.
3. The break-even for endorsing Sato when the comparison is the November plan, not staying neutral.

**Interpret:** answer board member 1 using your first number. Why does the break-even for endorsing Sato rise against the November plan? Board member 2's 5 points and the break-even are both "points": are they the same kind of point?
""")

EX3_SUPPLIED = code("ex3-supplied", """
# Inputs (hypothetical)
p_moreno = 0.80              # chance of winning the primary
p_sato = 0.20
nov_moreno = 0.40            # chance of winning November, if nominated
nov_sato = 0.70
signs_moreno = 0.75          # share of the plan each one signs
signs_sato = 1.00
signs_moreno_crossed = 0.50  # what Moreno signs if the group endorses Sato

# Supplied: staying neutral, endorsing Sato at d = 0, one point moved to Sato, and the break-even.
stay_neutral = p_moreno * nov_moreno * signs_moreno + p_sato * nov_sato * signs_sato
endorse_sato = p_moreno * nov_moreno * signs_moreno_crossed + p_sato * nov_sato * signs_sato
point_to_sato = nov_sato * signs_sato - nov_moreno * signs_moreno_crossed
break_even_vs_neutral = (stay_neutral - endorse_sato) * 100 / point_to_sato

print('Stay neutral (%):         ', round(100 * stay_neutral, 1))
print('Endorse Sato, d = 0 (%):  ', round(100 * endorse_sato, 1))
print('One point moved to Sato:  ', round(point_to_sato, 3))
print('Break-even vs neutral:    ', round(break_even_vs_neutral, 1), 'points of primary chance')
""")

EX3_CODE = code("ex3-code", """
# (1) The value of one point of primary chance moved from Sato to Moreno, if the group endorses Moreno.
# (2) The expected share of the plan under the November plan (add 0.05 to both November chances).
# (3) The break-even for endorsing Sato compared with the November plan.
""")

FINISH = md("finish", """
**Before finishing:** Restart the session, run all cells in order, and check your three answers. Be ready to explain in one sentence each: calibrated; overconfident versus underconfident; why a calibrated forecaster can be useless; the Brier floor; why one upset does not refute a forecast; why Hale's 60% is not his chance of taking office; expected value; and how to find a break-even.
""")


def figure_cells(cells):
    # Figure cells are dropped only when the builder runs with --no-figures.
    return [c for c in cells if FIGURES or c["id"] not in ("fig1", "fig2")]


# Parts 1 and 2 are shared by both notebooks, so edits here appear in both.
PARTS_1_2 = [
    P1_RECORD, SETUP, P1_UPSET_CODE, P1_UPSET_RESULT,
    P1_CALIBRATION, FIG1, P1_CALIBRATION_2, P1_CAL_CODE, P1_PLOT_CODE,
    P1_POOL_MD, P1_POOL_CODE, P1_POOL_RESULT,
    P1_DISCRIMINATION, FIG2, P1_DISC_CODE, P1_DISC_RESULT,
    P1_BRIER, P1_BRIER_CODE, P1_BRIER_RESULT,
    P1_RATINGS, P1_RATINGS_CODE, P1_TOSSUP_CODE, P1_TOSSUP_RESULT, P1_BOX,
    P2_SCENARIO, P2_EV, P2_EV_CODE, P2_EV_RESULT,
    P2_ENDORSE, P2_ENDORSE_CODE, P2_MOVES_CODE, P2_ENDORSE_RESULT,
    P2_SENSITIVITY, P2_SENS_CODE, P2_SENS_RESULT, P2_BOX,
]


def student_cells():
    return figure_cells(
        [md("title", "# Coding Session 11: Can we trust a forecast?"), INTRO]
        + PARTS_1_2
        + [PART3_INTRO,
           EX1_MD, EX1_CODE, md("ex1-interp", STUB),
           EX2_MD, EX2_CODE, md("ex2-interp", STUB),
           EX3_MD, EX3_SUPPLIED, EX3_CODE, md("ex3-interp", STUB),
           FINISH])


# ---------------------------------------------------------------- Solutions
SOL_TITLE = md("title", """
# Coding Session 11: Solutions
## Can we trust a forecast?

This notebook repeats Parts 1 and 2 of the student notebook unchanged, so it runs on its own and builds every object the exercises use. Each exercise is followed by worked code and a model interpretation with grading notes.

**Open in Colab:** [Student notebook](""" + COLAB + """wk11_codingsession.ipynb) · [Solutions notebook](""" + COLAB + """wk11_codingsession_solutions.ipynb).
""")

SOL_PART3 = md("part3", """
## Part 3. Exercises with solutions

The quoted claims and the Exercise 3 scenario are hypothetical; the forecasts are real. Model answers are longer than we expect from students, who should aim for three to five sentences.
""")

EX1_SOL = code("ex1-sol", """
# Averages by rating: the favorite's average chance and the share the favorite won.
by_rating = races.groupby('rating', observed=True)[['fav_prob', 'fav_won']].mean()
by_rating['races'] = races.groupby('rating', observed=True).size()

# Upsets: races the favorite lost, and the number the forecasts imply.
by_rating['actual_upsets'] = by_rating['races'] * (1 - by_rating['fav_won'])
by_rating['expected_upsets'] = by_rating['races'] * (1 - by_rating['fav_prob'])

assert by_rating['races'].sum() == len(races)
by_rating[['races', 'fav_prob', 'fav_won', 'actual_upsets', 'expected_upsets']].round(3)
""")

EX2_SOL = code("ex2-sol", """
# The close races: FiveThirtyEight gave the Democrat between 25% and 75%.
close = races[races['dem_prob'].between(0.25, 0.75)].copy()
# The pundit says 100% for FiveThirtyEight's favorite: 1 if the Democrat was favored, else 0.
close['pundit'] = (close['dem_prob'] > 0.5).astype(int)
close_base_rate = close['dem_won'].mean()

print('Close races:', len(close))
print('Share the pundit called correctly (%):', round(100 * (close['pundit'] == close['dem_won']).mean(), 1))
print('Base rate of the close races (%):     ', round(100 * close_base_rate, 1))
print('Brier, FiveThirtyEight:  ', round(((close['dem_prob'] - close['dem_won']) ** 2).mean(), 4))
print('Brier, pundit:           ', round(((close['pundit'] - close['dem_won']) ** 2).mean(), 4))
print('Brier, always base rate: ', round(((close_base_rate - close['dem_won']) ** 2).mean(), 4))

# Not required: the close races came from three elections that broke very differently.
print(close.groupby('year')['dem_won'].agg(['size', 'mean']).round(3))
""")

EX3_SOL = code("ex3-sol", """
# (1) Endorse Moreno: a point moves from Sato to Moreno. Sato's share is unchanged (written commitment).
point_to_moreno = nov_moreno * signs_moreno - nov_sato * signs_sato
print('One point moved to Moreno:', round(point_to_moreno, 3))

# (2) The November plan: stay neutral, and both November chances rise by 0.05.
november_plan = (p_moreno * (nov_moreno + 0.05) * signs_moreno
                 + p_sato * (nov_sato + 0.05) * signs_sato)
print('November plan (%):', round(100 * november_plan, 1))

# (3) Break-even for endorsing Sato against the November plan (same value per point as before).
break_even_vs_november = (november_plan - endorse_sato) * 100 / point_to_sato
print('Break-even vs November plan:', round(break_even_vs_november, 1), 'points of primary chance')
""")


def solution_cells(answers):
    return figure_cells(
        [SOL_TITLE, INTRO] + PARTS_1_2
        + [SOL_PART3,
           EX1_MD, EX1_SOL, md("ex1-ans", answers["ex1"]),
           EX2_MD, EX2_SOL, md("ex2-ans", answers["ex2"]),
           EX3_MD, EX3_SUPPLIED, EX3_SOL, md("ex3-ans", answers["ex3"])])


# ---------------------------------------------------------------- write
def notebook(cells):
    ids = [c["id"] for c in cells]
    assert len(ids) == len(set(ids)), "duplicate cell ids"
    for c in cells:  # nbformat stores source as a list of lines
        c["source"] = c["source"].splitlines(keepends=True)
    return {"cells": cells, "nbformat": 4, "nbformat_minor": 5,
            "metadata": {"colab": {"private_outputs": True, "provenance": []},
                         "kernelspec": {"display_name": "Python 3", "language": "python",
                                        "name": "python3"},
                         "language_info": {"name": "python"}}}


def sha(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def check(path, stamps):
    # Stop before writing anything if either notebook was edited by hand since the last build.
    if os.path.exists(path) and not FORCE:
        name = os.path.basename(path)
        if name not in stamps:
            sys.exit(f"STOP: {path} exists but was not written by this builder. Back it up and use --force.")
        if sha(path) != stamps[name]:
            sys.exit(f"STOP: {path} changed since the last build (manual edits?). Sync them into the builder first.")


def write(cells, path, stamps):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(notebook(cells), f, indent=1, ensure_ascii=False)
        f.write("\n")
    stamps[os.path.basename(path)] = sha(path)


if __name__ == "__main__":
    import copy
    stamps = json.load(open(STAMP)) if os.path.exists(STAMP) else {}
    answers = json.load(open(ANSWERS_FILE))
    check(STUDENT, stamps)
    check(SOLUTIONS, stamps)
    write(copy.deepcopy(student_cells()), STUDENT, stamps)
    write(copy.deepcopy(solution_cells(answers)), SOLUTIONS, stamps)
    json.dump(stamps, open(STAMP, "w"), indent=1)
    print("wrote", STUDENT, "and", SOLUTIONS, "| figures included:", FIGURES)
