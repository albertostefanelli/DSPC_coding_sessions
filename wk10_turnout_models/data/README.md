# North Carolina turnout teaching data

**Release status:** Published fixed teaching data with user approval. The cloud CSV is pinned to a specific Git commit so classroom results do not change when a source download changes.

`nc_turnout_2024_teaching.csv` contains **47,463 real administrative records** from the North Carolina State Board of Elections (NCSBE), reduced to the seven columns below. It is not simulated and is not a contact experiment. This is the fixed file used by both Week 10 notebooks.

[Fixed cloud CSV](https://raw.githubusercontent.com/albertostefanelli/DSPC_coding_sessions/0346cd0991e445edcbd7f7a10cba2194186961d6/wk10_turnout_models/data/nc_turnout_2024_teaching.csv) · [Preparation script](prepare_nc_turnout.py) · [Full machine-readable audit](nc_turnout_2024_preparation_report.json)

## Official sources

NCSBE publishes [historical registration snapshots](https://www.ncsbe.gov/results-data/voter-registration-data), [statewide voter history](https://www.ncsbe.gov/results-data/voter-history-data), and [data-use guidance](https://www.ncsbe.gov/about-elections/county-boards-elections/county-resources/county-board-kit/how-work-our-data). The snapshot layout is documented [here](https://s3.amazonaws.com/dl.ncsbe.gov/data/Snapshots/layout_VR_Snapshot.txt), the current registry [here](https://s3.amazonaws.com/dl.ncsbe.gov/data/layout_ncvoter.txt), and history [here](https://s3.amazonaws.com/dl.ncsbe.gov/data/layout_ncvhis.txt).

| Input | Official download | SHA-256 of the compressed source |
|---|---|---|
| snapshot | [VR_Snapshot_20240101.zip](https://s3.amazonaws.com/dl.ncsbe.gov/data/Snapshots/VR_Snapshot_20240101.zip) | 447925db866050238498ab3fd7e67d084ef8224257960005d47e2ca3b168c76c |
| history | [ncvhis_Statewide.zip](https://s3.amazonaws.com/dl.ncsbe.gov/data/ncvhis_Statewide.zip) | 59470bf35cbca1331e1b620e4c03707e59fbd958fba85b3903e5070bcc8e4837 |
| current registry | [ncvoter_Statewide.zip](https://s3.amazonaws.com/dl.ncsbe.gov/data/ncvoter_Statewide.zip) | 0a7f828a851fa81eceae913d17d88494246e64d606430ecf91c83fbcbe923770 |

Retrieved during 2026-11-12T18:06:17.593962+00:00–2026-11-12T18:10:44.667905+00:00 (UTC). Exact HTTP Last-Modified/ETag values, file sizes, encodings, source-member names, and package versions are in the audit. The historical snapshot is dated **January 1, 2024**. Current registration and participation files are the specific weekly versions captured in the audit; these URLs change over time.

## Population and preparation

The starting population is the snapshot's **ACTIVE, INACTIVE, and TEMPORARY** registrants with a numeric integer age from **18 through 110**, with a usable official identifier. This is not everyone eligible to vote in November 2024: it excludes people who registered later and those younger than 18 at the snapshot date. The age upper bound is an explicit preparation rule, not a model result.

The preparation script scans only needed fields from the compressed files. It draws a seeded sample before attaching any turnout outcomes. The audit's exact selection rule is:

> Independent uniform random priorities over eligible snapshot rows; keep 50,000 smallest before reading history. Exclude sampled IDs repeated among eligible snapshot rows, then IDs absent from the current registry. Repeats involving removed snapshot rows do not disqualify a unique eligible record. No replacement or outcome-based resampling.

The target sample is 50,000; the final file contains **47,463** records after the recorded linkage and quality checks. The random seed is `202410`. The full selection and exclusion counts are retained in the audit, including the handling of repeated identifiers and removed historical registrations.

The later registry is used only to check identifier persistence, not to choose people currently marked active or to supply predictors. Removed records are retained when the linkage rule is satisfied. Sampled records with unresolved identifiers are excluded and reported, not recoded as nonvoters. This later check can still create attrition: findings concern the retained cohort, not the whole January population.

Participation is attached from the **statewide** history file by the official identifier. County files are unsuitable for this historical join because they follow current registration county. Repeated records for one person and one election count once. The extract deliberately retains people with no voting history: **4,877** have no recorded participation in any of its four elections.

Public identifiers are used transiently for matching and removed before export. Names, addresses and phone numbers are not read into the processing tables. The teaching file contains no public voter IDs or contact details.

The descriptive registration year is missing for **25** retained records whose recorded year (1900) precedes the earliest birth year consistent with the snapshot age. The rule is `registration_year < 2024 - age_2024 - 1`. These people remain in the file, and all model predictors and outcomes are complete. The dated snapshot age is retained rather than replaced with a later age; the audit also records the small number of disagreements with later birth-year records.

## Columns

| Column | Definition |
|---|---|
| `row_id` | New sequential teaching identifier, unrelated to the official ID; not a voter lookup key. |
| `age_2024` | Age in the January 1, 2024 snapshot; a dated age measure, not exact age on Election Day. |
| `registration_year` | Year of the snapshot's administrative registration date. It need not be the person's first registration or first eligibility. Blank values, if present, mean unavailable. Used descriptively, not as a model predictor. |
| `voted_2018` | Recorded participation in the November 6, 2018 general election. |
| `voted_2020` | Recorded participation in the November 3, 2020 general election. |
| `voted_2022` | Recorded participation in the November 8, 2022 general election. |
| `voted_2024` | Recorded participation in the November 5, 2024 general election; the modeled outcome. |

Every `voted_` column is 1 when participation is recorded and 0 when no corresponding record is found for a retained identifier. **Zero does not prove nonvoting everywhere.** It may also reflect youth, later registration, interstate moves, or an incomplete administrative record. A unique registry match establishes a usable identifier, not perfect history completeness.

| General election | Recorded participants in the retained sample | Recorded turnout |
|---|---:|---:|
| 2018 | 23,222 | 48.93% |
| 2020 | 35,662 | 75.14% |
| 2022 | 25,328 | 53.36% |
| 2024 | 35,892 | 75.62% |

These percentages describe the retained January 2024 cohort. They are **not statewide turnout estimates** for the earlier elections. The dataset supplies no candidate choices, support scores, or randomized contact indicator. Its predictions therefore describe participation under the campaigning that actually occurred, not a measured no-contact counterfactual.

## Reproduction and stable classroom use

Run `python prepare_nc_turnout.py --raw-dir /path/to/compressed/source/cache` in an environment with pandas and NumPy. The script streams ZIP members and does not write enormous uncompressed voter files. It needs several gigabytes for compressed inputs and working memory. Students do not run this script; they use one `pd.read_csv` call to the fixed cloud CSV.

The current state downloads change weekly and retain only a rolling history window. Re-running with newly downloaded inputs is a new data version, not guaranteed reproduction of this release. Retaining the source files with the listed hashes reproduces the extraction; the checked-in teaching CSV and audit preserve the classroom release without including full state records in the repository.

Output SHA-256: `8f6716a353ccb1dcba2ddbcd2951a6eee773f7196a4ac43e1dcc137e6c3e53c1`. Exact columns, missing-value counts and row totals are in the audit. The notebooks fit on 70% of this fixed file (`random_state=10`) and evaluate the remaining 30%. They use only 2018/2020/2022 participation and January 2024 age to predict 2024. No 2026 outcome is used.

## Legacy data

`kling_stratmann_subset.csv` is preserved unchanged for archival continuity. It is no longer used by the revised Week 10 notebooks. Its earlier description is in the timestamped backups and the Week 4 data notes.
