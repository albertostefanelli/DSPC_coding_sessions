# Week 3 datasets

Both datasets used by the Week 3 notebooks are stored in this folder.

## Kling and Stratmann: robocall walkthrough

`kling_stratmann_subset.csv` contains 539,567 voter records and eight columns.
It is an unchanged copy of the existing course extract of the 2014 robocall
experiment. Weeks 4 and 10 have their own copies in their respective `data`
folders; the original Week 9 copy is retained.

The Week 3 notebooks load the [Week 3 CSV](https://raw.githubusercontent.com/albertostefanelli/DSPC_coding_sessions/master/wk03_rcts_and_ate/data/kling_stratmann_subset.csv).
Source: Kling, Daniel T., and Thomas Stratmann (2023),
[Large-Scale Evidence for the Effectiveness of Partisan GOTV Robo Calls](https://doi.org/10.1017/XPS.2022.16).
The notebooks describe each column.

## Pons (2018): French presidential campaign teaching extract

`pons_2018_teaching.csv` supplies the independent Pons exercise in both Week 3 notebooks.
It contains actual experimental data, with shortened variable names, from:

Pons, Vincent. 2018. “Will a Five-Minute Discussion Change Your Mind? A Countrywide
Experiment on Voter Choice in France.” *American Economic Review* 108(6): 1322–1363.
[Article](https://doi.org/10.1257/aer.20160524) ·
[Replication archive, version 1](https://doi.org/10.3886/E113130V1) ·
[Journal-hosted ZIP](https://www.aeaweb.org/content/file?id=7262).

## Study and sample

The study randomized areas within local blocks during François Hollande's 2012
presidential campaign. In a full block of five areas, four entered the treatment
pool and one entered control. The campaign then allocated a subset of treatment
areas to canvassers according to its coverage targets. Treatment assignment is
therefore distinct from allocation and from actual conversations with voters.

The original analysis file contains 17,242 areas. The author's main analysis
restricts to `territory_in == 1`: territories whose activists' reports or
post-election survey responses indicated use of the campaign's allocation lists.
This gives 4,674 areas. Requiring `merge_results12 == 1`, as in the first-round
main specifications in `DoFiles/Analysis.do`, gives the **3,397 rows** used here.
The 1,277 excluded areas lack matched 2012 election results. No additional
sampling or imputation is performed.

One row is one unit of randomization and observation: either a precinct or a
whole municipality. The extract contains **1,713 precincts**, **1,684 municipalities**,
**2,723 treatment areas**, and **674 controls**, covering 733 block identifiers.
There are no missing values in the eight retained columns, and `area_id` is unique.

Both outcomes refer to the **first round of the presidential election, April 22,
2012**. Turnout and candidate share have different denominators. Values are
proportions, despite the percent signs in the original Stata variable labels.

## Variables and original names

| Teaching column | Source / transformation | Meaning |
|---|---|---|
| `area_id` | `P_` + `municipality_code` + `_` + `precinct_code` for precincts; `M_` + `municipality_code` for municipalities | Unique geographic key created for this extract. |
| `area_type` | `level_randomization`: 1 → `Precinct`; 0 → `Municipality` | Unit represented by the row. |
| `municipality` | `municipality` | Municipality name; repeated when multiple precincts are present. |
| `block` | `stratum_identifier` | Local randomization block identifier. |
| `treatment` | `treatment` | 1 = randomized treatment pool; 0 = randomized control. |
| `registered` | `nb_registered_pr12t1_an` | Registered voters in the area for the first round. |
| `turnout` | `prop_turnout_pr12t1_an` | Ballots cast / registered voters. |
| `hollande_share` | `prop_hollande_pr12t1_an` | Hollande votes / valid candidate votes, excluding blank and invalid ballots. |

The two ratios follow the formulas in `DoFiles/Databases_preparation.do`.
Identifiers, assignment, and voter counts are written as integers where appropriate;
outcome proportions retain the numerical values in the source file.

## Interpreting the classroom calculations

The notebooks use equal weight for each area. Group means are averages of area
proportions, not voter-weighted national totals. The exercise estimates an
unadjusted assignment difference; it does not estimate an effect per voter reached.
The published analysis includes randomization-block effects and separate estimates
for assignment and allocation. Classroom results need not equal the headline
estimates in the paper. The permutation exercise shuffles assignment within each
block, conditional on the areas and treatment counts retained in this teaching
extract. This preserves block membership and counts, including in blocks with
incomplete election-result coverage. It is a conditional teaching test, not a
reconstruction of every stage of the original assignment and allocation procedure.

## Rebuilding the extract

Downloaded September 17, 2026, from the journal-hosted public replication ZIP.
The source is `AER-2016-0524.R2_PUBLISH/Data/Analysis/analysis.dta`.

Source file SHA-256:
`83c1641bab30bd501b69219278dc349bde1e39b3f779ea100ccc2b757bd49fe6`.

The preparation script is for course maintainers; students only need the CSV:

```bash
python prepare_pons_data.py /path/to/AER-2016-0524.R2_PUBLISH/Data/Analysis/analysis.dta
```

It writes `pons_2018_teaching.csv` beside the script. In local Jupyter, run the
notebooks from the Week 3 folder. In Colab, create a runtime folder named `data`
and upload this CSV there before running the second data-loading cell.

`nyvoterfile_2021.csv` is retained as a legacy file and is not used by these notebooks.
