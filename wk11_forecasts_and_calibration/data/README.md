# W11 data sources

Coding Session 11 uses one file, built by [`prepare_wk11_data.py`](prepare_wk11_data.py) from FiveThirtyEight's public forecast archive. Run `python3 prepare_wk11_data.py` in this folder to rebuild it. The script downloads the pinned source files and prints their SHA-256 values and its checks.

## `fivethirtyeight_final_forecasts_2018_2022.csv`

- **Source:** FiveThirtyEight, *How Good Are FiveThirtyEight Forecasts?* ("checking our work") data.
  - Repository: [github.com/fivethirtyeight/checking-our-work-data](https://github.com/fivethirtyeight/checking-our-work-data), pinned to commit [`f6d5b2e1d6da2889345d381c41431f9a4ee208dd`](https://github.com/fivethirtyeight/checking-our-work-data/tree/f6d5b2e1d6da2889345d381c41431f9a4ee208dd).
  - Files: `us_house_elections.csv`, `us_senate_elections.csv`, `governors_elections.csv`.
  - Retrieved 2026-11-18.
- **License:** Creative Commons Attribution 4.0 International (CC BY 4.0), per the repository's `LICENSE` file. Data © FiveThirtyEight / ABC News.
  - This file is a filtered and renamed extract; the changes are listed below.
  - The FiveThirtyEight website now redirects to ABC News; the GitHub repositories still serve the files.
- **One row per race:** a 2018, 2020 or 2022 general election for the U.S. House, the U.S. Senate or governor, with FiveThirtyEight's final forecast for the Democratic candidate.
  - **1,373 races:** House 403 / 403 / 398, Senate 32 / 32 / 33, governor 36 / 0 / 36 (the source has no 2020 governor races).
- **Columns:**

| Column | Meaning |
|---|---|
| `year` | Election year. |
| `office` | `House`, `Senate` or `Governor`. |
| `state` | Two-letter state code. |
| `district` | House district number (at-large seats are 1); 0 for statewide races. |
| `special` | `True` for a special election (Senate only, in this file). |
| `candidate` | The Democratic candidate. |
| `dem_prob` | FiveThirtyEight's Election-Day chance that this Democrat would win (0 to 1). Source column `probwin`. |
| `dem_won` | 1 if the Democrat won, 0 if not. Source column `probwin_outcome`. |

### Preparation steps

These are the steps in `prepare_wk11_data.py`.

1. Keep years 2018, 2020 and 2022. Drop rows with state `US`, which are chamber-control forecasts.
2. Keep the **"classic"** model version only, so all three years use the same version. FiveThirtyEight published three versions ("lite", "classic", "deluxe"), so numbers quoted elsewhere may come from a different version and differ from this file.
   - Washington's 3rd District, 2022: classic 4.0%, deluxe 2.2%.
   - Iowa's 2nd District, 2020: classic 94.0%, deluxe 87.8%.
3. Keep the forecast dated Election Day. For every race in these years it is also the last forecast. The script checks this.
4. Keep the Democratic candidate's row, in races with **exactly one Democrat and at least two candidates**. Of the 1,477 races, **104** are dropped:
   - 39 uncontested races with a lone Democrat;
   - 33 races with no Democrat (for example top-two Republican-vs-Republican races, Vermont's 2018 Senate race with Bernie Sanders, Utah's 2022 Senate race with Evan McMullin);
   - 32 races with two or more Democrats (for example California and Washington top-two races and Louisiana's open ballot).
5. Rename the columns as in the table above. Statewide races get `district` 0, and the Senate file's mixed special-election flags (`false`, `true`, `1`, blank) become `True`/`False`.

Two rules worth knowing:
- **Independents.** Races won by an independent stay in the file as a Democratic loss when a Democrat also ran (Maine's 2018 Senate race: Angus King won; the Democrat in the file is Zak Ringelstein).
- **Unresolved races.** North Carolina's 9th District in 2018 has no certified result and is not in the source.

### Checks (printed by the script)

- **2018 forecasts.** The 2018 rows agree with FiveThirtyEight's separate 2018 forecast file ([fivethirtyeight/data `forecast-review/forecast_results_2018.csv`](https://github.com/fivethirtyeight/data/blob/4c1ff5e3aef1816ae04af63218015066e186c147/forecast-review/forecast_results_2018.csv), commit `4c1ff5e`, CC BY 4.0) to within 0.0003, with identical outcomes.
  - The one exception is Maine's 2018 Senate race: that file puts the independent Angus King on the Democratic side.
- **Rating labels.** The same 2018 file labels races by the favorite's chance of winning. Its labels split exactly at **60%, 75% and 95%**:

| Label | Favorite's chance |
|---|---|
| Toss-up | under 60% |
| Lean | 60% to under 75% |
| Likely | 75% to under 95% |
| Solid | 95% or more |

  - The notebook applies these cutoffs to all three years.
  - No race in the extract sits exactly on a cutoff, so `pd.cut`'s default right-closed bins give the same result.
- **Key numbers used in the notebook:**
  - share of races the Democrat won: 0.510;
  - Brier score of the forecasts: 0.0338;
  - Brier score of always guessing the share won: 0.2499.

### Hashes

| File | SHA-256 |
|---|---|
| `us_house_elections.csv` | `d63d5d49275480e4df8f1d349c6fd9f3c55beac1eaad61238e9bc27ef7bf5ac0` |
| `us_senate_elections.csv` | `981e5e0560bec7ce9ac10e49cb88eb8417755e23620696fd77cf361eb725771d` |
| `governors_elections.csv` | `213b13c16b80517315688c99abf3d3efa01285eec27ab37c6bd7e0cf0e9725d5` |
| `forecast_results_2018.csv` | `f06b04061ecf9af5996c433b9b9de3be2045ef615e53bfdf794ebae587e136a8` |
| **Output** `fivethirtyeight_final_forecasts_2018_2022.csv` | `1ff315c4a9f79f073febe045383518d2631499330ad0b71e6123e6b0c8bc7c85` |

## Hypothetical numbers

The endorsement scenario in Part 2 and Exercise 3 (candidates, primary and November chances, shares of the plan, and what crossing a candidate costs) is **made up** for teaching. It is labeled hypothetical in the notebook.

## Removed files

`analyst_record.csv`, the course's simulated teaching record used by the September version of this session, was removed in the November 2026 redesign. A copy is kept outside the published folders.
