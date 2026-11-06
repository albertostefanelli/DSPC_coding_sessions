"""Build the Week 9 student and solutions notebooks.

Run:  python3 build_wk09.py [--figures-approved] [--force]

Refuses to overwrite a notebook that changed since the last build (hand edits):
sync those edits into this script first, or pass --force after backing up.
Hashes of the last build are kept in last_build_hashes.json next to this script.
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WEEK = os.path.dirname(HERE)
STUDENT = os.path.join(WEEK, "wk09_codingsession.ipynb")
SOLUTIONS = os.path.join(WEEK, "wk09_codingsession_solutions.ipynb")
STAMP = os.path.join(HERE, "last_build_hashes.json")
FIGURES = "--figures-approved" in sys.argv
FORCE = "--force" in sys.argv

REPO = "https://raw.githubusercontent.com/albertostefanelli/DSPC_coding_sessions/"
ASSETS = REPO + "refs/heads/master/wk09_cost_effectiveness/assets/"
COLAB = "https://colab.research.google.com/github/albertostefanelli/DSPC_coding_sessions/blob/master/wk09_cost_effectiveness/"
NOTES = "https://github.com/albertostefanelli/DSPC_coding_sessions/blob/master/wk09_cost_effectiveness/data/README.md"


def md(cid, text):
    # Colab and Jupyter read $...$ in markdown as LaTeX math, so escape every dollar sign.
    return {"cell_type": "markdown", "id": cid, "metadata": {},
            "source": text.strip("\n").replace("$", "\\$")}


def code(cid, text):
    return {"cell_type": "code", "id": cid, "metadata": {}, "execution_count": None,
            "outputs": [], "source": text.strip("\n")}


# ---------------------------------------------------------------- Part 1
PART1 = [
md("part1-story", """
## 1. Which tactic buys the most votes per dollar?

A campaign has a fixed budget and several ways to spend it: mail, phone calls, texts, knocking on doors. It is tempting to fund the tactic with the biggest effect on turnout. But a tactic that works well on each person can still be a bad deal if each person is expensive to reach. To compare tactics we need one number that combines effect and cost: what one more vote costs. This session builds that number, then asks how sure we can be about it, how to update it, and why cheap votes run out.
"""),
md("part1-cost-per-vote", """
### Cost per additional vote

An **additional vote** is one more vote than you would have had without the campaign. The **cost per additional vote** is what it costs to produce one:

**cost per additional vote = cost per person ÷ effect (as a proportion)**

> A mailer costs $0.50 per person and raises turnout by 1 percentage point. Mail 1,000 people: you pay 1,000 × $0.50 = $500. One point is 1 in every 100 people, so you get 1,000 × 0.01 = 10 additional votes, at $500 ÷ 10 = $50 each. The 1,000 cancels, so you can work per person: $0.50 ÷ 0.01 = $50.

**Watch the units.** Effects are reported in **percentage points** (pp). Divide by 100 before you use them: +1 pp is 0.01. Dividing by 1 instead gives $0.50, a vote 100 times too cheap.

Cost per vote also tells you what a budget buys: **additional votes = budget ÷ cost per vote**, so $10,000 buys 200 votes at $50. Rank tactics by cost per vote, not by effect size or by cost per contact.
"""),
md("part1-same-people", """
### Match the cost to the effect

Canvassers knock on many doors, but only some open. The **contact rate** is the share of the people you try to reach that you actually reach. Suppose a conversation costs $2, canvassers reach 25% of the people on their list, and the experiment finds +1 point among *everyone on the list*.

That +1 point is the intent-to-treat effect (**ITT**) from Week 7: the effect per person you tried to reach, averaged over everyone on the list, including people who never opened the door. The price is per conversation, and only 25% of the list gets one, so the cost per person on the list is $2 × 0.25 = $0.50, and a vote costs $0.50 ÷ 0.01 = **$50**. You can also work per conversation. The effect on the people you reached is the local average treatment effect (**LATE**), 1 ÷ 0.25 = 4 points, and $2 ÷ 0.04 = **$50** again.

The mistake is to mix the two: $2 per conversation ÷ 0.01 per person on the list = $200, four times too much. **Before you divide, check that the cost and the effect describe the same people.**
"""),
md("part1-net-votes", """
### An additional voter is not a net vote

Campaigns win by getting more votes than the other side. A **net vote** is one vote added to your margin. Turnout contact brings out people who would have stayed home, and they do not all vote for you. If 100 new voters break 70–30, your margin grows by 70 − 30 = 40 net votes. At $50 per additional voter, those 100 voters cost $5,000, so each net vote costs $5,000 ÷ 40 = $125, or in one step $50 ÷ (0.70 − 0.30). If new voters split 50–50, turnout buys no net votes at all. That is why targeting matters.

**Persuasion counts twice.** Persuasion changes the minds of people who were going to vote anyway. Each voter you switch from the other candidate leaves their column (−1) and joins yours (+1): two net votes. So 20 switched voters are worth as much as 100 new voters who break 70–30.
"""),
md("part1-interval", """
### Price the interval, not just the point

Every effect estimate comes with a 95% confidence interval, so every cost per vote has one too. To find it, price each end of the effect's interval. If the mailer's effect is +1 point with an interval from +0.5 to +1.5, the best case is $0.50 ÷ 0.015 = **$33** and the worst case is $0.50 ÷ 0.005 = **$100**. A bigger effect means a cheaper vote, so the top of the effect's interval gives the bottom of the price's.

Notice that $50 is not in the middle of $33 and $100. Dividing by a small number gives a very large result, so the worst case sits much further away than the best case. A second tactic at the same price might have an effect of +0.5 with an interval from −0.2 to +1.2. Its interval reaches zero, and at zero effect no amount of money buys a vote, so its worst-case price is **never**. Tactics with similar point estimates can have very different worst cases (Part 2 shows two cities like this).
"""),
md("fig1", """
![A curve of cost per vote against the effect on turnout. One effect interval maps to a lopsided price interval; another reaches zero, where the price is never.](""" + ASSETS + """fig1_cost_curve.png)

*Figure 1. Tactic A's effect interval (blue) becomes a lopsided price interval on the side axis, $33 to $100. Tactic B's (red) reaches zero, so its price has no top: never.*
"""),
md("part1-updating", """
### Updating with new evidence

**Bayesian updating** combines what you believed before a new study (the **prior**) with what the study says, to get what you believe now (the **updated belief**, or *posterior*). The updated belief is a weighted average of the two, and each one's weight is its **precision**:

**precision = 1 ÷ SE²**

The **standard error (SE)** measures an estimate's uncertainty: a 95% interval is estimate ± 1.96 × SE, so SE = half the interval's width ÷ 1.96. A small SE means a narrow interval and a big weight.

> You believed the effect was +2.0 points, SE 0.5 (precision 1 ÷ 0.25 = 4). A new study finds +1.0, SE 0.25 (precision 1 ÷ 0.0625 = 16). Each weight is a precision's share of the total, 4 + 16 = 20: 20% and 80%. The updated belief is 0.2 × 2.0 + 0.8 × 1.0 = **+1.2**. Precisions add, so the updated SE is 1 ÷ √20 = 0.22 and the interval is about [+0.8, +1.6].

The updated interval is narrower than either: two pieces of evidence beat one. A noisy new study (SE 1.0, precision 1) would get only 20% of the weight, landing you at +1.8. **You move toward whichever belief is narrower.** The rule assumes both measure the same true effect, which may fail if the new study had different voters or elections. Then price the vote with the updated belief: $0.50 ÷ 0.012 = $42.
"""),
md("fig2", """
![Two panels of interval bars: a precise new study pulls the updated belief close to it; a noisy one leaves it close to the prior.](""" + ASSETS + """fig2_updating.png)

*Figure 2. The same prior meets two different new studies. The precise study pulls the updated belief most of the way; the noisy one barely moves it.*
"""),
md("part1-last-vote", """
### The average vote and the last vote

An experiment usually measures what one contact does, and nothing guarantees that the third mailer to a home does what the first did. **Diminishing returns** means each additional dollar buys less than the one before.

Suppose four rounds on the same list each cost $10,000 and bring 200, 100, 50 and 25 additional votes: $50, $100, $200 and $400 a vote. **The average vote** is total cost ÷ total votes, $40,000 ÷ 375 = $107. **The last vote** is what the last round costs per vote, $400. If another tactic buys votes at $120, the average makes all four rounds look like a bargain, yet rounds 3 and 4 cost more than $120. Keep buying a tactic while its next vote is the cheapest you can buy, then switch. That is why the best plan is usually a mix.
"""),
md("fig3", """
![A staircase of four bars, the cost per vote of each round, against a flat line for the next-best tactic and a dashed line for the average.](""" + ASSETS + """fig3_last_vote.png)

*Figure 3. The first two rounds are cheaper than the next-best tactic, the last two are not. The average of all four rounds hides that.*
"""),
md("part1-checklist", """
> **Before you quote a cost per vote, ask:**
> - **Units:** did you divide the effect by 100?
> - **Same people:** are the cost and the effect both per person on the list, or both per contact?
> - **Which vote:** an additional voter, or a net vote for your side?
> - **How sure:** what do the two ends of the interval cost?
> - **Which estimate:** if studies disagree, how much weight does each deserve?
> - **Which dollar:** what does the *last* vote cost, not the average one?
>
> And a vote is only worth buying in a race that could be close.
"""),
]
if not FIGURES:
    PART1 = [c for c in PART1 if c["id"] not in ("fig1", "fig2", "fig3")]

# ---------------------------------------------------------------- Part 2 data
DATA_MD = md("part2-data", """
## 2. The data

### Six canvassing experiments

Before local elections in November 2001, groups in Bridgeport, Columbus, Detroit, Minneapolis, Raleigh and St. Paul knocked on doors to encourage people to vote, without backing any candidate. In each city, researchers randomly split a list of registered voters into a treatment group, which canvassers tried to visit, and a control group, then checked who voted. Canvassers reached only some of their list, so the study reports both the ITT and the LATE.

Each row is one **city**; the last row, `All sites`, is the study's estimate for all six cities together.

| Column | What it records |
|---|---|
| `city` | City, or `All sites` |
| `people` | Registered voters in the experiment |
| `itt_pp` | Effect on turnout per person on the list (ITT), in points |
| `itt_se_pp` | Standard error of `itt_pp`, in points |
| `contact_rate` | Share of the treatment group that canvassers actually reached |
| `late_pp` | Effect on turnout per person reached (LATE), in points |

**The price.** The researchers costed canvassing at $10 an hour for a canvasser who has about eight conversations an hour, so **$1.25 per conversation**. These are 2001 wages, and they leave out the fixed costs of running an organization.

**Source:** Green, Gerber and Nickerson (2003), "Getting Out the Vote in Local Elections," *Journal of Politics* 65(4), Table 2; replication data in the ISPS Data Archive, [doi:10.60600/YU/B9TZNZ](https://doi.org/10.60600/YU/B9TZNZ), CC0. The [data notes](""" + NOTES + """) record how the file was built.
""")

SETUP = code("setup", """
# Import the tools we need: pandas for tables, numpy for numbers, matplotlib for plots.
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Read the six canvassing experiments straight from the course repository (you need to be online).
# Source: Green, Gerber & Nickerson (2003), Journal of Politics 65(4), Table 2;
# replication data: ISPS Data Archive, doi:10.60600/YU/B9TZNZ (CC0).
# Python joins the two quoted strings inside the parentheses into one address.
cities = pd.read_csv(
    'https://raw.githubusercontent.com/albertostefanelli/DSPC_coding_sessions/'
    'master/wk09_cost_effectiveness/data/six_city_canvassing.csv'
)

# The researchers' price: $10 an hour, about 8 conversations an hour.
cost_per_conversation = 10 / 8

cities
""")

# ---------------------------------------------------------------- Part 2 demo
PART2 = [
md("s2a", """
### 2a. What does a vote from canvassing cost?

The effect `itt_pp` is per person on the list, but the $1.25 is per conversation. Following Part 1, we first turn the price into a cost per person on the list, then divide. As a check we also work per conversation with the LATE, and we show what the mixed-up division would give.
"""),
code("s2a-code1", """
# You pay only for conversations, and only contact_rate of the people on the list are reached,
# so the cost per person on the list is the price of a conversation x the contact rate.
cities['cost_per_person'] = cost_per_conversation * cities['contact_rate']

# Right way 1: cost per person on the list / effect per person on the list (ITT, as a proportion).
cities['cost_per_vote'] = cities['cost_per_person'] / (cities['itt_pp'] / 100)

# Right way 2: cost per conversation / effect per person reached (LATE, as a proportion).
cities['cost_per_vote_late'] = cost_per_conversation / (cities['late_pp'] / 100)

# Mixed up: cost per conversation / effect per person on the list. Wrong: different people.
cities['cost_per_vote_mixed'] = cost_per_conversation / (cities['itt_pp'] / 100)

cities[['city', 'itt_pp', 'contact_rate', 'cost_per_person',
        'cost_per_vote', 'cost_per_vote_late', 'cost_per_vote_mixed']].round(2)
"""),
md("s2a-read1", """
For all six cities together, both right ways give about **$17.6** a vote. The mixed-up division gives **$59.5**, more than three times too much. City by city, the two right ways agree closely except in Raleigh, where the effects are so close to zero that rounding them to one decimal matters. The authors' own rougher figure is $15; the data notes explain the gap. Votes look cheapest in Bridgeport and St. Paul (about **$8.7–8.8**) and most expensive in Raleigh (about **$558**).

These are additional voters, not net votes. If the new voters broke 70–30 for your candidate, a net vote would cost more:
"""),
code("s2a-code2", """
# Keep only the All sites row, then take its single value out with .iloc[0].
all_sites = cities[cities['city'] == 'All sites']
cost_per_vote_all = all_sites['cost_per_vote'].iloc[0]

# Each additional voter who breaks 70-30 adds 0.70 - 0.30 = 0.40 to your margin.
net_share = 0.70 - 0.30
cost_per_net_vote = cost_per_vote_all / net_share

# Inside {}, :.2f means two decimal places.
print(f'Cost per additional vote: ${cost_per_vote_all:.2f}')
print(f'Cost per net vote, 70-30: ${cost_per_net_vote:.2f}')
"""),
md("s2b", """
### 2b. How sure are we about each price?

Each city's effect has a standard error, so each price has an interval. We build the effect's 95% interval and price both ends, as in Part 1. Where the interval reaches zero, the worst case is "never".
"""),
code("s2b-code1", """
# 95% interval for each effect: estimate +/- 1.96 standard errors.
cities['itt_low'] = cities['itt_pp'] - 1.96 * cities['itt_se_pp']
cities['itt_high'] = cities['itt_pp'] + 1.96 * cities['itt_se_pp']

# Best case: the high end of the effect gives the lowest price.
cities['best_case'] = cities['cost_per_person'] / (cities['itt_high'] / 100)

# Worst case: the low end of the effect, but only if it is above zero.
# np.where(condition, a, b) takes a where the condition is True and b where it is False.
# np.nan means "no number"; here it stands for "never".
cities['worst_case'] = np.where(cities['itt_low'] > 0,
                                cities['cost_per_person'] / (cities['itt_low'] / 100),
                                np.nan)

cities[['city', 'itt_low', 'itt_pp', 'itt_high',
        'best_case', 'cost_per_vote', 'worst_case']].round(1)
"""),
code("s2b-code2", """
# Each city's effect with its 95% interval. plt.subplots makes an empty chart (ax) to draw on;
# xerr is the distance from the estimate to each end of the interval.
fig, ax = plt.subplots(figsize=(8, 4))
ax.errorbar(cities['itt_pp'], cities['city'], xerr=1.96 * cities['itt_se_pp'],
            fmt='o', color='#2c3e50', ecolor='#3498db', elinewidth=3, capsize=4)
ax.axvline(0, color='#e74c3c', linestyle='--')     # zero effect: no votes bought
ax.invert_yaxis()                                   # first city at the top
ax.set_xlabel('Effect on turnout per person on the list (points)')
ax.set_title('Four of the six city intervals reach zero (bottom row: all six combined)')
plt.tight_layout()
plt.show()
"""),
md("s2b-read", """
Bridgeport and St. Paul have the same price at their point estimates, about **$8.7–8.8** a vote. Their worst cases differ: **$33** in Bridgeport and **$83** in St. Paul, whose estimate is noisier. In Columbus, Detroit, Minneapolis and Raleigh the interval reaches zero, so the worst case is "never" (shown as `NaN`). Combining all six cities gives a narrower interval, from +0.9 to +3.3, and a finite worst case of **$40**. This is the reason to combine evidence.
"""),
md("s2c", """
### 2c. Combining the evidence by precision

The precision rule from Part 1 works for any number of estimates: each one's weight is its precision's share of the total. Here we combine the five cities other than Raleigh, which sets up Exercise 2. Like Part 1, this treats every city as measuring the same effect.
"""),
code("s2c-code", """
# Keep the five cities other than Raleigh (and drop the All sites row).
# & means "and"; .copy() makes a separate table we can add columns to.
others = cities[(cities['city'] != 'Raleigh') & (cities['city'] != 'All sites')].copy()

# Precision = 1 / SE squared; weight = each precision's share of the total.
others['precision'] = 1 / others['itt_se_pp']**2
others['weight'] = others['precision'] / others['precision'].sum()
print(others[['city', 'itt_pp', 'itt_se_pp', 'precision', 'weight']].round(2))

# The weighted average, and its SE: precisions add, so SE = 1 / square root of the total.
# In the print, :+.2f shows the sign and two decimals; :.1f shows one decimal.
five_city_estimate = (others['weight'] * others['itt_pp']).sum()
five_city_se = 1 / np.sqrt(others['precision'].sum())
print(f'Five-city estimate: {five_city_estimate:+.2f} points (SE {five_city_se:.2f}), '
      f'95% interval {five_city_estimate - 1.96*five_city_se:+.1f} to {five_city_estimate + 1.96*five_city_se:+.1f}')
"""),
md("s2c-read", """
Columbus has the smallest SE, so it gets the largest weight (about **a third**); St. Paul, the noisiest, gets the smallest (under **10%**). Together, the five cities say about **+2.5 points** per person on the list (SE **0.65**), with an interval that stays well above zero.
"""),
]

# ---------------------------------------------------------------- Part 3
PART3_INTRO_STUDENT = md("part3", """
## 3. Three short exercises

Each exercise needs a few lines of code and **three to five short sentences of interpretation**, one for each part of the question. Say what the result means for a campaign decision, not just what the number is.

The quotes and the later mailer rounds in Exercise 3 are made up; the data are not. Cells marked **YOUR CODE** contain only comments; replace them with your calculations.
""")

MAILER_MD = md("mailers", """
### The data for Exercises 1 and 3: the Michigan mailer experiment

Before Michigan's August 2006 primary, researchers took 180,002 households of registered voters who had voted in November 2004. About 11 days before the election, they randomly sent one of four mailers to about 20,000 households each, and nothing to the rest (the control group):

- **Civic Duty:** a reminder that voting is a citizen's duty.
- **Hawthorne:** the same, plus "YOU ARE BEING STUDIED!": researchers would check public records to see who voted.
- **Self:** the household's own recent voting record, with a promise to mail an updated record after the election.
- **Neighbors:** the household's voting record *and* its neighbors', with the same promise.

Each row is one **group**.

| Column | What it records |
|---|---|
| `mailer` | `Control`, `Civic Duty`, `Hawthorne`, `Self` or `Neighbors` |
| `households` | Households in the group (each mailed household got one mailer) |
| `people` | Registered voters living in those households |
| `voted` | How many of them voted in the primary |

The researchers report that each mailer cost **30 cents** to print and mail.

**Source:** Gerber, Green and Larimer (2008), "Social Pressure and Voter Turnout," *American Political Science Review* 102(1); replication data in the ISPS Data Archive, [doi:10.60600/YU/CGMWNW](https://doi.org/10.60600/YU/CGMWNW), CC0. See the [data notes](""" + NOTES + """).
""")

MAILER_CODE = code("mailers-code", """
# Read the mailer experiment from the course repository.
# Source: Gerber, Green & Larimer (2008), APSR 102(1); replication data:
# ISPS Data Archive, doi:10.60600/YU/CGMWNW (CC0). One row per group.
mailers = pd.read_csv(
    'https://raw.githubusercontent.com/albertostefanelli/DSPC_coding_sessions/'
    'master/wk09_cost_effectiveness/data/ggl_2008_mailers.csv'
)

mailers
""")

EX1_MD = md("ex1", """
### Exercise 1. Is the $1.93 a typo?

**Data:** `mailers`. Each mailer costs `cost_per_mailer = 0.30` dollars per household.

The researchers write that the Neighbors mailer produced additional votes at **$1.93** each. A staffer disagrees: *"A Neighbors mailer costs 30 cents and raises turnout by 8.1 points. $0.30 ÷ 0.081 = $3.70 a vote. The paper is off by almost half."*

**Calculate:** run the supplied code, which adds each group's `turnout` and each mailer's `effect_pp` (its turnout minus the control group's, in points). Then, for each mailer, compute the cost of mailing the whole group (`total_cost` = households × $0.30), the `additional_votes` (people × effect as a proportion) and `cost_per_vote`. Ignore the `inf` in the Control row. Add the staffer's number as `staffer_cost_per_vote` (cost per mailer ÷ effect as a proportion) and print the people per household.

**Interpret:** who is right about the Neighbors mailer, and what exactly went wrong in the other calculation? Rank the four mailers by effect and by cost per vote. Why are the two rankings the same here, and in what situation would they differ?
""")

EX1_CODE = code("ex1-code", """
# Supplied code: turnout in each group, and each group's effect compared with the control group.
cost_per_mailer = 0.30
mailers['turnout'] = mailers['voted'] / mailers['people']
control_turnout = mailers['turnout'].iloc[0]          # the first row is the control group
mailers['effect_pp'] = 100 * (mailers['turnout'] - control_turnout)
print(mailers[['mailer', 'turnout', 'effect_pp']].round(3))

# YOUR CODE: add total_cost, additional_votes and cost_per_vote for each group,
# then staffer_cost_per_vote (cost per mailer / effect as a proportion)
# and people_per_household (people / households).
# Print the four mailer rows rounded to 2 decimals; mailers[mailers['mailer'] != 'Control']
# keeps every row except the control group.
""")

EX2_MD = md("ex2", """
### Exercise 2. Raleigh found nothing. Stop canvassing there?

**Data:** the numbers you need are typed into the code cell. Raleigh's own experiment found **+0.1 points** (SE **1.4**). The five other cities, combined in Part 2c, found **+2.48** (SE **0.65**). In Raleigh, canvassers reached 44.6% of the people on their list, so at $1.25 a conversation a person on the list costs $1.25 × 0.446.

A Raleigh organizer writes: *"Our own experiment found +0.1 points. Whatever happened elsewhere, canvassing does not work here. Move the money to something else."*

**Calculate:** Raleigh's 95% interval. Then update the five-city estimate (the prior) with Raleigh's result (the new study): both precisions, both weights, `updated_estimate`, `updated_se` and the updated 95% interval. Finally, the cost per vote in Raleigh at three effects: Raleigh's own estimate, the five-city estimate and `updated_estimate`.

**Interpret:** does Raleigh's result show that canvassing does not work there? Why does the updated belief land much closer to the five-city estimate than to Raleigh's? The update assumes every city has the same true effect; what would make you doubt that for Raleigh, and how would it change your advice to the organizer?
""")

EX2_CODE = code("ex2-code", """
# Inputs: Raleigh's own result, the five-city estimate from Part 2c, and Raleigh's cost per person.
# a, b = 1, 2 stores two numbers at once: a gets 1 and b gets 2.
raleigh_estimate, raleigh_se = 0.1, 1.4
five_city_estimate, five_city_se = 2.48, 0.65
raleigh_cost_per_person = 1.25 * 0.446

# YOUR CODE: Raleigh's 95% interval (estimate +/- 1.96 x SE).
# Precisions (1 / SE**2) and weights (each precision / their sum) for the five cities and Raleigh.
# updated_estimate, updated_se (1 / square root of the summed precisions) and the 95% interval.
# The cost per vote in Raleigh at raleigh_estimate, five_city_estimate and updated_estimate.
# Print everything with clear labels.
""")

EX3_MD = md("ex3", """
### Exercise 3. One more round of mail?

**Data:** typed into the code cell. A campaign has about $18,000, enough for three rounds of mail to a list the size of the Hawthorne group (20,002 households, 38,204 voters) at $0.30 per household. Round 1 works like the real Hawthorne mailer, **+2.57 points**; assume each later round is half as effective as the one before. The next-best use of the money is canvassing at about **$17.60** per additional vote (Part 2a).

The mail vendor says: *"Three rounds of our mailer average about $10 a vote, well under canvassing's $17.60. Put the money into three rounds."*

**Calculate:** for each round, its cost, its additional votes and its cost per vote, in a column `cost_per_vote`. Then `average_cost`, the total cost of all three rounds ÷ their total votes. Last, suppose new mail voters break 55–45 for your candidate, while canvassing goes to neighborhoods where new voters break 70–30: compute each round's cost per net vote and canvassing's.

**Interpret:** is the vendor's average right, and is it the right number for this decision? How many rounds would you send, and where should the rest of the money go? Does your answer change once you count net votes, and why?
""")

EX3_CODE = code("ex3-code", """
# Supplied code: the three rounds. Round 1 is the real Hawthorne effect; rounds 2 and 3 are assumed.
# pd.DataFrame({...}) builds a table from columns: each name is followed by its list of values.
rounds = pd.DataFrame({'round': [1, 2, 3],
                       'effect_pp': [2.57, 2.57 / 2, 2.57 / 4]})
# The size of the list and the prices (several values stored at once, in order).
households, voters, cost_per_mailer = 20002, 38204, 0.30
canvass_cost_per_vote = 17.60

# YOUR CODE: add columns cost (households x cost per mailer), additional_votes
# (voters x effect as a proportion) and cost_per_vote, and print rounds.
# average_cost = total cost of the three rounds / total additional votes.
# Cost per net vote: each round's cost_per_vote / (0.55 - 0.45),
# and canvassing's canvass_cost_per_vote / (0.70 - 0.30).
""")

STUB = "**Your interpretation:** Write three to five short sentences. Answer each part of the question and quote the numbers you use."


def student_cells():
    return ([md("title", "# Coding Session 09: What does one more vote cost?")]
            + PART1 + [DATA_MD, SETUP] + PART2
            + [PART3_INTRO_STUDENT, MAILER_MD, MAILER_CODE,
               EX1_MD, EX1_CODE, md("ex1-interp", STUB),
               EX2_MD, EX2_CODE, md("ex2-interp", STUB),
               EX3_MD, EX3_CODE, md("ex3-interp", STUB)])


# ---------------------------------------------------------------- Solutions
SOL_TITLE = md("title", """
# Coding Session 09: Solutions
## What does one more vote cost?

This notebook has the same Part 1 and setup as the student notebook, so it runs on its own. Part 2 is condensed into one cell that rebuilds every object the exercises use. Each exercise is followed by worked code and a model interpretation.

**Open in Colab:** [Student notebook](""" + COLAB + """wk09_codingsession.ipynb) · [Solutions notebook](""" + COLAB + """wk09_codingsession_solutions.ipynb).
""")

SOL_SETUP_MD = md("sol-setup", """
## Setup: rebuild the objects from Part 2

This cell repeats the demonstration in Part 2 without the printouts: the cost per vote in each city and the five-city estimate.
""")

SOL_SETUP_CODE = code("sol-setup-code", """
# Part 2a and 2c in brief: cost per vote in each city and the five-city estimate.
cities['cost_per_person'] = cost_per_conversation * cities['contact_rate']
cities['cost_per_vote'] = cities['cost_per_person'] / (cities['itt_pp'] / 100)

others = cities[(cities['city'] != 'Raleigh') & (cities['city'] != 'All sites')].copy()
others['precision'] = 1 / others['itt_se_pp']**2
five_city_estimate = (others['precision'] * others['itt_pp']).sum() / others['precision'].sum()
five_city_se = 1 / np.sqrt(others['precision'].sum())

# .iloc[-1] is the last row, All sites.
print(f'All sites: ${cities["cost_per_vote"].iloc[-1]:.2f} a vote; '
      f'five cities {five_city_estimate:+.2f} (SE {five_city_se:.2f})')
""")

SOL_PART3 = md("part3", """
## 3. Exercises with solutions

The quotes in the exercises and the later mailer rounds in Exercise 3 are made up; the data are not. Model answers are a little longer than we expect from students.
""")

EX1_SOL = code("ex1-sol", """
# Turnout and effect of each mailer, as in the supplied code.
cost_per_mailer = 0.30
mailers['turnout'] = mailers['voted'] / mailers['people']
control_turnout = mailers['turnout'].iloc[0]
mailers['effect_pp'] = 100 * (mailers['turnout'] - control_turnout)

# Cost of mailing the whole group, votes it produced, and the cost of each vote.
mailers['total_cost'] = mailers['households'] * cost_per_mailer
mailers['additional_votes'] = mailers['people'] * mailers['effect_pp'] / 100
mailers['cost_per_vote'] = mailers['total_cost'] / mailers['additional_votes']

# The staffer divides a cost per household by an effect per person.
mailers['staffer_cost_per_vote'] = cost_per_mailer / (mailers['effect_pp'] / 100)
mailers['people_per_household'] = mailers['people'] / mailers['households']

print(mailers[mailers['mailer'] != 'Control'][['mailer', 'effect_pp', 'total_cost', 'additional_votes', 'cost_per_vote',
                        'staffer_cost_per_vote', 'people_per_household']].round(2))
""")

EX2_SOL = code("ex2-sol", """
# Inputs, as in the exercise.
raleigh_estimate, raleigh_se = 0.1, 1.4
five_city_estimate, five_city_se = 2.48, 0.65
raleigh_cost_per_person = 1.25 * 0.446

print(f'Raleigh 95% interval: {raleigh_estimate - 1.96*raleigh_se:+.2f} to {raleigh_estimate + 1.96*raleigh_se:+.2f}')

prior_precision = 1 / five_city_se**2
new_precision = 1 / raleigh_se**2
prior_weight = prior_precision / (prior_precision + new_precision)
new_weight = new_precision / (prior_precision + new_precision)
print(f'Precision: five cities {prior_precision:.2f}, Raleigh {new_precision:.2f}')
# :.1% shows a share as a percentage with one decimal.
print(f'Weight:    five cities {prior_weight:.1%}, Raleigh {new_weight:.1%}')

updated_estimate = prior_weight * five_city_estimate + new_weight * raleigh_estimate
updated_se = 1 / np.sqrt(prior_precision + new_precision)
print(f'Updated: {updated_estimate:+.2f} (SE {updated_se:.2f}), 95% interval '
      f'{updated_estimate - 1.96*updated_se:+.2f} to {updated_estimate + 1.96*updated_se:+.2f}')

# Re-price a Raleigh vote at each effect. :,.2f adds a thousands comma.
print(f'Cost per vote, Raleigh alone: ${raleigh_cost_per_person / (raleigh_estimate / 100):,.2f}')
print(f'Cost per vote, five cities:   ${raleigh_cost_per_person / (five_city_estimate / 100):,.2f}')
print(f'Cost per vote, updated:       ${raleigh_cost_per_person / (updated_estimate / 100):,.2f}')
""")

EX3_SOL = code("ex3-sol", """
# The three rounds, their costs and votes, and the net-vote comparison.
rounds = pd.DataFrame({'round': [1, 2, 3],
                       'effect_pp': [2.57, 2.57 / 2, 2.57 / 4]})
households, voters, cost_per_mailer = 20002, 38204, 0.30
canvass_cost_per_vote = 17.60

rounds['cost'] = households * cost_per_mailer
rounds['additional_votes'] = voters * rounds['effect_pp'] / 100
rounds['cost_per_vote'] = rounds['cost'] / rounds['additional_votes']
rounds['cost_per_net_vote'] = rounds['cost_per_vote'] / (0.55 - 0.45)
print(rounds.round(2))

average_cost = rounds['cost'].sum() / rounds['additional_votes'].sum()
print(f'Average cost per vote, three rounds: ${average_cost:.2f}')
print(f'Canvassing: ${canvass_cost_per_vote:.2f} per vote, '
      f'${canvass_cost_per_vote / (0.70 - 0.30):.2f} per net vote')
""")

ANSWERS_FILE = os.path.join(HERE, "wk09_answers.json")


def solution_cells(answers):
    return ([SOL_TITLE] + PART1 + [DATA_MD, SETUP, SOL_SETUP_MD, SOL_SETUP_CODE, SOL_PART3,
             MAILER_MD, MAILER_CODE,
             EX1_MD, EX1_SOL, md("ex1-ans", answers["ex1"]),
             EX2_MD, EX2_SOL, md("ex2-ans", answers["ex2"]),
             EX3_MD, EX3_SOL, md("ex3-ans", answers["ex3"])])


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


def write(cells, path, stamps):
    if os.path.exists(path) and not FORCE:
        name = os.path.basename(path)
        if name not in stamps:
            sys.exit(f"STOP: {path} exists but was not written by this builder. Back it up and use --force.")
        if sha(path) != stamps[name]:
            sys.exit(f"STOP: {path} changed since the last build (manual edits?). Sync them into the builder first.")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(notebook(cells), f, indent=1, ensure_ascii=False)
        f.write("\n")
    stamps[os.path.basename(path)] = sha(path)


if __name__ == "__main__":
    import copy
    stamps = json.load(open(STAMP)) if os.path.exists(STAMP) else {}
    answers = json.load(open(ANSWERS_FILE))
    write(copy.deepcopy(student_cells()), STUDENT, stamps)
    write(copy.deepcopy(solution_cells(answers)), SOLUTIONS, stamps)
    json.dump(stamps, open(STAMP, "w"), indent=1)
    print("wrote", STUDENT, "and", SOLUTIONS, "| figures included:", FIGURES)
