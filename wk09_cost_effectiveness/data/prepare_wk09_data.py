"""Build the two small CSV files used by the Week 9 coding session.

Run:  python prepare_wk09_data.py
Writes six_city_canvassing.csv and ggl_2008_mailers.csv next to this script.
Needs pandas and an internet connection (downloads about 21 MB from the
Yale ISPS Data Archive, CC0 1.0). See README.md for the sources.
"""
import os
import numpy as np
import pandas as pd

OUT = os.path.dirname(os.path.abspath(__file__))
DATAVERSE = "https://dataverse.yale.edu/api/access/datafile/"

# 1. Six-city canvassing table -------------------------------------------------
# Transcribed from Table 2 of Green, Gerber & Nickerson (2003), Journal of
# Politics 65(4), p. 1092: post-treatment difference in 2001 turnout (ITT, SE),
# percentage of the treatment group actually contacted, and the effect of
# actual contact (LATE). "All sites" is the paper's pooled row.
six = pd.DataFrame({
    "city": ["Bridgeport", "Columbus", "Detroit", "Minneapolis", "Raleigh",
             "St. Paul", "All sites"],
    "people": [1806, 2478, 4954, 2827, 4660, 2208, 18933],
    "itt_pp": [4.0, 1.4, 2.4, 1.9, 0.1, 4.6, 2.1],
    "itt_se_pp": [1.5, 1.1, 1.4, 1.6, 1.4, 2.1, 0.6],
    "contact_rate": [0.281, 0.143, 0.309, 0.185, 0.446, 0.321, 0.296],
    "late_pp": [14.4, 9.7, 7.8, 10.1, 0.2, 14.4, 7.1],
})

# Check the transcription against the replication file (dataset version 2.0,
# file id 27228). Within-city ITT with walk-list (turf) fixed effects, as in
# the paper; differences of a few tenths are expected after the 2020 edits.
raw = pd.read_csv(DATAVERSE + "27228", sep="\t")
for city, d in raw.groupby("city"):
    d = d.copy()
    for col in ["voted01", "treatmen"]:
        d[col + "_dm"] = d[col] - d.groupby("turf")[col].transform("mean")
    itt = (d["voted01_dm"] * d["treatmen_dm"]).sum() / (d["treatmen_dm"] ** 2).sum()
    contact = d.loc[d["treatmen"] == 1, "contact"].mean()
    print(f"check {city:12s} ITT {100*itt:5.2f} pp  contacted {100*contact:5.1f}%")
six.to_csv(os.path.join(OUT, "six_city_canvassing.csv"), index=False)

# 2. Gerber, Green & Larimer (2008) mailer table -------------------------------
# Individual-level file, dataset version 2.0, file id 42238. Household is the
# unit of assignment; treatment 0 = control, 1 = Hawthorne, 2 = Civic Duty,
# 3 = Neighbors, 4 = Self (authors' R file).
ind = pd.read_csv(DATAVERSE + "42238", sep="\t",
                  usecols=["treatment", "voted", "hh_id"])
names = {0: "Control", 2: "Civic Duty", 1: "Hawthorne", 4: "Self", 3: "Neighbors"}
ggl = (ind.groupby("treatment")
          .agg(households=("hh_id", "nunique"), people=("voted", "size"),
               voted=("voted", "sum"))
          .loc[list(names)]                       # paper's column order
          .reset_index())
ggl.insert(0, "mailer", ggl["treatment"].map(names))
ggl = ggl.drop(columns="treatment")
print(ggl)
ggl.to_csv(os.path.join(OUT, "ggl_2008_mailers.csv"), index=False)
