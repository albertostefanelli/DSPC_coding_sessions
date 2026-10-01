# Week 5 canvassing pilot teaching data

The notebook loads `canvassing_pilot.csv` directly from the pinned course
URL below. It is Josh Kalla's Week 5 teaching file from
`data_science_campaigns_26`.
It is course case data; the supplied materials do not identify a published
study or a real-world sampling provenance. Do not present it as an
independently verified empirical campaign result.

- Source: [pinned course CSV](https://raw.githubusercontent.com/joshuakalla/data_science_campaigns_26/df35e89ef09877aee3f2de4ce49a1ec654520e7f/weeks/wk05_power_and_nulls/data/canvassing_pilot.csv)
- Source revision: `df35e89ef09877aee3f2de4ce49a1ec654520e7f`
- SHA-256: `a197dcb38573328eea9a30b0e04116fa6a92f0bacb90bacc06ad1dd60cc381a9`
- Rows: 400 households; 200 assigned to treatment and 200 to control.
- Missing values: none.

| Variable | Meaning |
|---|---|
| `household_id` | Unique household record ID (1–400). |
| `treatment` | 1 = assigned a canvass attempt; 0 = control. |
| `turned_out` | Binary turnout outcome supplied by the case, 1 = voted and 0 = did not. |

The case simplifies turnout to one binary outcome per household record.
There are no separate resident-level outcomes or completed-contact indicators.
The simulation follows this simplified unit and assumes independent records.

The file reproduces the case totals: 84 of 200 controls (42.0%) and 87 of 200
treatment records (43.5%) voted, for a difference of +1.5 percentage points.
Its regression p-value is about 0.76; the simulated RI tail fraction
is about 0.84. These are different procedures, not different datasets.

The notebook generates new binary outcomes for power calculations, explicitly
assuming 42% control turnout and a +2 percentage-point assignment effect.
Those simulated outcomes are not additional observations in this CSV.

The notebook uses `pd.read_csv(data_url)` and requires an internet
connection. No local dataset copy or path selection is needed.
