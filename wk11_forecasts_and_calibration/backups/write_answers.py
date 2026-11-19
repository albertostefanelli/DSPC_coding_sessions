"""Write wk11_answers.json (model answers and grading notes for the solutions notebook)."""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))

ex1 = """**Interpretation:** No. A 4% underdog should win about 4 times in 100, so one upset cannot show the forecast was wrong; the record is the test. In **997** Solid races the favorites lost only **1**, against about **4.9** expected. In the **214** Likely races the favorites' average chance was **87.0%**, but they won **95.3%**: **10** upsets against **27.9** expected. So the ratings were **underconfident**, too close to 50%, not overconfident. Too few upsets is still a calibration problem: "Likely" undersold the favorite, so the donor should trust FiveThirtyEight's favorites *more* than the labels suggest. Finally, if a Solid label steers money away from the underdog, the label helps make itself come true. Favorites then win more often partly *because* of the rating, so its record can look better than its forecasting skill.

*Grading notes:* full credit needs:
1. The table for all four ratings: races 66 / 96 / 214 / 997, actual upsets 26 / 26 / 10 / 1, expected upsets 29.5 / 31.4 / 27.9 / 4.9.
2. The point that one upset does not refute a probability, with reference to the record or to the expected count.
3. "Underconfident" for Likely, supported by 87.0% vs 95.3% or by 10 vs 27.9 upsets.
4. A sensible feedback argument: ratings move money and so outcomes, so a rating can help its own favorite win and flatter its record.

Common errors:
- Calling fewer upsets than expected "better" or "well calibrated".
- Calling the forecasts overconfident because of the Washington race.
- Computing expected upsets with the share won instead of the average chance.

Strong answers note that the Toss-up and Lean rows hold fewer races, and that races in one year can move together, so the record is smaller than its 1,373 rows suggest."""

ex2 = """**Interpretation:** In the **162** close races, the pundit called **67.9%** correctly, exactly as often as FiveThirtyEight's favorites won, because she picked the same favorites. But the Brier score also rewards honest uncertainty. FiveThirtyEight scored **0.2107**, always guessing the close races' base rate (**48.8%**) scored **0.2498**, and the pundit scored **0.321**, worse than guessing. Each of her forecasts is 0 or 1, so a correct call scores (1 − 1)² = 0 and a wrong call scores (1 − 0)² = 1. Her Brier score is therefore the share she got wrong: 52 of 162 = 0.321. She missed almost a third of these races at a cost of 1 each, while guessing the base rate (0.488) costs about 0.25 in every race, so she loses to the floor. She is **overconfident**: she says 100%, but her favorites won only 67.9% of the time, so her numbers are too far from 50%. FiveThirtyEight beat the floor by only about 0.04 in these races. Close races are hard to call, and most of FiveThirtyEight's edge in Part 1 came from easy races.

*Grading notes:* full credit needs:
1. The six numbers: 162 races, 67.9% correct, and Brier scores of 0.2107, 0.321 and 0.2498 (base rate 48.8%).
2. Why the same picks score worse: confident misses each cost 1, while FiveThirtyEight's hedged misses cost less, for example (0.6 − 0)² = 0.36. Hedging also costs a little on hits, for example (0.6 − 1)² = 0.16, but far less than it saves on misses.
3. Brier = share wrong for 0/1 forecasts.
4. "Overconfident", with the 100% vs 67.9% comparison.
5. A sensible reading of 0.2107 vs 0.2498: a modest edge, so close races are hard.

Common errors:
- Treating accuracy as the measure of forecast quality.
- Calling the pundit underconfident.
- Forgetting to square, or comparing the pundit with the full-sample base rate.

Strong answers note that the close races come from three elections that broke very differently (the Democrat won 49.1%, 16.3% and 75.0% of them in 2018, 2020 and 2022), so 0.2107 vs 0.2498 should not be oversold."""

ex3 = """**Interpretation:**
1. Moving one point of primary chance to Moreno gains 0.40 × 0.75 = 0.30 of the plan but gives up Sato's 0.70 × 1.00 = 0.70, so each point is worth **−0.40**. Endorsing Moreno can only lower the expected share of the plan. Moreno is four times as likely to win the *primary*, but a point of primary chance is worth more with Sato, who wins November more often and signs all of it. Board member 1 compares chances of winning one step, not what the group gets.
2. The November plan is worth 0.80 × 0.45 × 0.75 + 0.20 × 0.75 × 1.00 = 0.27 + 0.15 = **42.0%** of the plan, more than staying neutral (**38.0%**).
3. Endorsing Sato at d = 0 gives **30.0%**. Against the November plan it therefore starts 12 points behind instead of 8, and the break-even rises from **16** to **24** points of primary chance. The bar rises because the right comparison is the best alternative, not doing nothing. So endorsing Sato beats the November plan only if it lifts her primary chance from 20% to above 44%.

The 5 points are points of *November* chance and the break-even is in points of *primary* chance. They sit at different steps of the tree, so they are not the same kind of point. Each has to be multiplied through the tree before the two can be compared.

*Grading notes:* full credit needs:
1. −0.40 per point, with the reason that a point is worth more with the candidate who wins November more often and signs more.
2. The November plan at 42.0%.
3. The break-even of 24 points, compared with 16, explained by the higher alternative.
4. The units distinction between November and primary points.

Accept expressions in place of decimals, for example (42 − 30) ÷ 0.5. Common errors:
- Adding 0.05 to the primary chances instead of the November chances.
- Using Moreno's crossed share (50%) in the November plan; there is no endorsement, so she signs 75%.
- Saying endorsing Moreno is good because she is more likely to win.

Strong answers note that the 5 points and the crossed share are made-up inputs worth checking before the board decides."""

json.dump({"ex1": ex1, "ex2": ex2, "ex3": ex3}, open(os.path.join(HERE, "wk11_answers.json"), "w"), indent=1, ensure_ascii=False)
print("wrote wk11_answers.json")
