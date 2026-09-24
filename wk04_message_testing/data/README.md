# Week 4 datasets

Both datasets used here are unchanged copies of those used in Coding Session 03.

## Robocall experiment

`kling_stratmann_subset.csv` has 539,567 voter records and eight columns.
Kling and Stratmann studied partisan get-out-the-vote calls before the November
2014 US general election in Georgia, Nebraska, New Mexico, Ohio, Pennsylvania,
and Virginia. The question is whether assignment to different numbers of calls
changes turnout. The outcome records participation, not candidate choice.

The researchers selected landline numbers and included registered voters in the
corresponding households. Households were assigned within states to no calls,
one call, three calls, or six calls. The CSV has one row per voter, not per
household. There are 135,331 control voters, 135,920 one-call voters, 134,826
three-call voters, and 133,490 six-call voters.

| Column | Coding and units |
|---|---|
| `group` | `Control (No Call)`, `T1: 1 Call`, `T3: 3 Calls`, or `T6: 6 Calls`; assigned arm. |
| `treatment` | 1 = assigned any calls; 0 = control. This is not confirmed contact. |
| `voted` | 1 = voted in November 2014; 0 = did not vote. |
| `gen2012` | 1 = voted in the 2012 general election; 0 = did not vote. |
| `svh` | 1 = single-voter household; 0 = another household type. This does not identify households. |
| `age` | Recorded age in years; 21,446 missing values. |
| `male` | Recorded male indicator, 1/0; 22,418 missing values. |
| `income` | Supplied numeric income measure; 21,064 missing values. Exact definition, currency, and reference period have not been verified from the source codebook. Unused in this session. |

There are no missing values in `group`, `treatment`, `voted`, `gen2012`, or `svh`.
A mean of `voted` is a turnout proportion; multiply it by 100 for a percentage.
Multiply a difference in turnout proportions by 100 for percentage points.

**Assignment limitation:** neither state nor household identifiers are present.
Individual row shuffles cannot reproduce the experiment's household assignment
within states. Restricting to single-voter households would still leave the
state information missing. A permutation of this extract must not be presented
as a replication of the study's randomization inference.

Sources:

- [Published study](https://doi.org/10.1017/XPS.2022.16), published online August
  18, 2022; *Journal of Experimental Political Science* 10(2), 2023, 188–200.
- [Original replication archive](https://doi.org/10.7910/DVN/DMJ7EA), cited by
  the published article as Harvard Dataverse V1 (2022).
- [Authors' working paper](https://www.ifo.de/DocDL/cesifo1_wp6195.pdf), November
  2016; documents the sample, household calls, and assignment within states.

**Version check, September 23, 2026:** the published article and its archive
reference were checked. The Dataverse landing page failed to load and the public
version-history API returned HTTP 403. Later corrected or revised releases
therefore could not be verified. The existing extract has no recorded source
release or preparation script; its exact match to V1 is unverified. Its total
and arm counts agree with the authors' reported sample. The CSV remains unchanged.

SHA-256: `ce400ea2345f1b9b70fbd5ed126c61ac0da67adac4a17a153110642efb3a9be5`.

## Pons (2018): French presidential campaign teaching extract

`pons_2018_teaching.csv` is an unchanged copy of the Coding Session 03 exercise
dataset. Week 4 uses it for subgroup comparisons.
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
estimates in the paper. Any further randomization inference must preserve
assignment within blocks, conditional on the areas and treatment counts retained
in the extract, including blocks with incomplete election-result coverage.
Week 4 calculates descriptive subgroup contrasts and does not repeat the
Week 3 permutation exercise.


## Version and preparation check: September 24, 2026

The journal article is from June 2018. The [original replication archive](https://www.openicpsr.org/openicpsr/project/113130/version/V1/view)
currently lists V1, published October 12, 2019, as its only published version.
No newer release or correction is listed there. The journal's replication link
points to that archive. The source data were not replaced.

Coding Session 03's preparation notes record a September 17, 2026 download of
the [journal-hosted replication ZIP](https://www.aeaweb.org/content/file?id=7262).
The input was `AER-2016-0524.R2_PUBLISH/Data/Analysis/analysis.dta`, with SHA-256
`83c1641bab30bd501b69219278dc349bde1e39b3f779ea100ccc2b757bd49fe6`.
The filtering and variable transformations are documented in the tables above
and implemented in [Week 3's preparation script](../../wk03_rcts_and_ate/data/prepare_pons_data.py).
The historical download checksum is recorded provenance, not a fresh comparison
of that source file with the archive. This revision copies the prepared Week 3
CSV byte for byte, without re-extracting, sampling, filtering, or recoding it.

Week 4 CSV SHA-256:
`d9902caab0eb255c9e0cf57e2f40da05f08abf0e5c02c99eff2dad97ae07c921`.

The exercise compares `hollande_share` across treatment and control separately
within Municipality (1,350 treated, 334 control) and Precinct (1,373 treated,
340 control). It retains all 3,397 areas. The municipality-minus-precinct effect
difference is descriptive; the notebooks do not claim a significant interaction
or interpret area type itself as randomized. Considering both available outcomes
in both area types would create four within-subgroup comparisons.

## File locations and loading

The two datasets used by the notebooks are:

- `data/kling_stratmann_subset.csv`, identical to Coding Session 03's copy.
- `data/pons_2018_teaching.csv`, identical to Coding Session 03's copy.

Each week keeps its own copy. The existing `nyvoterfile_2021.csv` is retained as
a legacy file and is not loaded by either revised notebook.

Both loading cells use one direct `pd.read_csv('data/<filename>')` call, followed
by `.head()` and `.shape()` for inspection, as in the lab's setup. Open the
notebook from the Week 4 folder. From the repository root, prefix either path
with `wk04_message_testing/`.

In Colab, create a runtime folder named `data` and upload both supplied CSVs
before running the loading cells. The same calls then read those uploaded
files. Both local paths were executed; live Colab execution was not tested.
There are no file-search loops, existence checks, path fallbacks, or automatic
download helpers in either notebook.

## Multiple-comparisons simulations

The teaching simulations use the lab's `np.random.binomial()`, mean differences,
array slices, `np.percentile()`, and nested loops. They create temporary outcomes
in memory, not a substitute empirical dataset. There is no permutation p-value
for the robocall extract, which lacks the required state and household IDs.

The reference cutoff is the 95th percentile of absolute differences from 1,000
no-effect two-group experiments (seed 2026), each with 1,000 independent 0/1
controls and 1,000 independent 0/1 treated outcomes, all with success probability
0.49. Unlike the lab's permutation-derived cutoff, this one comes directly from
the stated binomial model. We do not reuse an invalid voter-level shuffle.

The walkthrough then generates 1,000 independent no-effect experiments
(seed 42), each with 4,000 outcomes: one shared control and three treatment arms,
all of size 1,000. It applies the same cutoff to one fixed arm and to a search
across all three, counting each affected experiment once.

The exercise adapts that loop to two disjoint subgroups, each with its own
1,000 controls and 1,000 treated outcomes (seed 42, 1,000 experiments). Both
comparisons have the same probability and group size as the cutoff model.
Neither simulation reproduces the actual robocall household assignment or Pons's
area vote shares and blocked assignment. Their numerical cutoffs and error rates
are not applied to the real-data estimates.

Instructional and exercise code uses only functions and methods found in the
Week 4 lab or live coding. The coloured-box helper matches the existing lab and
Coding Session 03 presentation code.
