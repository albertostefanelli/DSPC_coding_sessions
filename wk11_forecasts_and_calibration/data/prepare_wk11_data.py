"""Build the Week 11 teaching extract of FiveThirtyEight's final election forecasts.

Run:  python3 prepare_wk11_data.py

What it does
1. Downloads FiveThirtyEight's "checking our work" files for House, Senate and
   governor races from a pinned GitHub commit (CC BY 4.0), into a temporary folder.
2. Keeps one forecast per race: the "classic" model version, the forecast dated
   Election Day, and the Democrat's row, in races with exactly one Democrat and
   at least two candidates (2018, 2020 and 2022).
3. Checks the 2018 rows against FiveThirtyEight's separate 2018 forecast file,
   and checks the rating cutoffs (60 / 75 / 95 percent) published in that file.
4. Writes fivethirtyeight_final_forecasts_2018_2022.csv next to this script and
   prints the SHA-256 of every input and of the output (recorded in README.md).

Only the Python standard library and pandas are needed.
"""
import hashlib
import os
import tempfile
import urllib.request

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
OUTPUT = os.path.join(HERE, "fivethirtyeight_final_forecasts_2018_2022.csv")

# Pinned commits, so a re-run downloads exactly the same bytes.
COW = ("https://raw.githubusercontent.com/fivethirtyeight/checking-our-work-data/"
       "f6d5b2e1d6da2889345d381c41431f9a4ee208dd/")
REVIEW_2018 = ("https://raw.githubusercontent.com/fivethirtyeight/data/"
               "4c1ff5e3aef1816ae04af63218015066e186c147/forecast-review/forecast_results_2018.csv")
SOURCES = {
    "House": COW + "us_house_elections.csv",
    "Senate": COW + "us_senate_elections.csv",
    "Governor": COW + "governors_elections.csv",
}
YEARS = [2018, 2020, 2022]
VERSION = "classic"


def download(url, folder):
    path = os.path.join(folder, url.rsplit("/", 1)[-1])
    urllib.request.urlretrieve(url, path)
    with open(path, "rb") as f:
        digest = hashlib.sha256(f.read()).hexdigest()
    print(f"downloaded {url.rsplit('/', 1)[-1]:32s} sha256 {digest}")
    return path


def load_office(office, path):
    rows = pd.read_csv(path, low_memory=False)
    # House rows have a district; statewide races (Senate, governor) get district 0.
    if "district" not in rows:
        rows["district"] = 0
    # Senate and governor rows mark special elections; the House file has no such column.
    # The Senate file writes the flag as false / true / 1 / blank, so normalize it.
    if "special" not in rows:
        rows["special"] = False
    rows["special"] = rows["special"].astype(str).str.lower().isin(["true", "1"])
    rows["office"] = office
    return rows


def build(folder):
    frames = [load_office(office, download(url, folder)) for office, url in SOURCES.items()]
    rows = pd.concat(frames, ignore_index=True)

    # Race-level forecasts only (state "US" rows are chamber-control forecasts).
    rows = rows[rows["year"].isin(YEARS) & (rows["state"] != "US")]
    key = ["year", "office", "state", "district", "special"]

    # The forecast dated Election Day is the last forecast for every race in these years.
    last = rows.groupby(key)["forecast_date"].transform("max")
    assert (last == rows["election_date"]).all(), "a race has a forecast after Election Day"
    rows = rows[(rows["forecast_date"] == rows["election_date"]) & (rows["forecast_type"] == VERSION)]
    races_total = rows.groupby(key).ngroups

    # One row per race: the Democrat, in races with exactly one Democrat and at least two candidates.
    candidates = rows.groupby(key)["candidate"].transform("size")
    democrats = rows["party"].eq("D").groupby([rows[k] for k in key]).transform("sum")
    keep = rows[(rows["party"] == "D") & (democrats == 1) & (candidates >= 2)].copy()

    # Why races are dropped (one row per race).
    per_race = pd.DataFrame({"candidates": candidates, "democrats": democrats}).groupby(
        [rows[k] for k in key]).first()
    print("dropped: uncontested with a lone Democrat",
          int(((per_race["candidates"] == 1) & (per_race["democrats"] == 1)).sum()),
          "| no Democrat", int((per_race["democrats"] == 0).sum()),
          "| two or more Democrats", int((per_race["democrats"] >= 2).sum()))

    out = pd.DataFrame({
        "year": keep["year"].astype(int),
        "office": keep["office"],
        "state": keep["state"],
        "district": keep["district"].fillna(0).astype(int),
        "special": keep["special"],
        "candidate": keep["candidate"],
        "dem_prob": keep["probwin"].astype(float),
        "dem_won": keep["probwin_outcome"].astype(int),
    })
    order = {"House": 0, "Senate": 1, "Governor": 2}
    out = (out.assign(_o=out["office"].map(order))
              .sort_values(["year", "_o", "state", "district", "special"])
              .drop(columns="_o").reset_index(drop=True))
    assert not out.duplicated(key).any()
    print(f"races with an Election-Day {VERSION} forecast: {races_total}; kept: {len(out)}; "
          f"dropped: {races_total - len(out)} (uncontested, no Democrat, or two or more Democrats)")
    return out


def check_against_2018_review(out, folder):
    review = pd.read_csv(download(REVIEW_2018, folder))
    review = review[review["version"] == VERSION].copy()

    # Rebuild the review file's race labels: AL-1 (House), AZ-S1 / MN-S2 (Senate, S2 = special), AK-G1 (governor).
    ours = out[out["year"] == 2018].copy()
    ours["race"] = ours["state"] + "-" + ours.apply(
        lambda r: str(r["district"]) if r["office"] == "House"
        else ("S2" if r["special"] else "S1") if r["office"] == "Senate" else "G1", axis=1)
    both = ours.merge(review, on="race", how="left")
    assert both["Democrat_WinProbability"].notna().all(), "a 2018 race is missing from the review file"

    # Known definitional difference: in Maine's 2018 Senate race the review file puts the
    # independent Angus King on the Democratic side; this extract keeps the Democratic
    # Party's own candidate, Zak Ringelstein. Every other race must agree.
    maine = both["race"] == "ME-S1"
    assert both.loc[maine, "candidate"].eq("Zak Ringelstein").all()
    both = both[~maine]
    gap = (both["dem_prob"] - both["Democrat_WinProbability"]).abs().max()
    print(f"2018 check: {len(both)} races agree with the review file (Maine Senate set aside); "
          f"largest probability difference {gap:.5f}")
    assert gap < 0.001
    assert (both["dem_won"] == both["Democrat_Won"]).all(), "an outcome differs from the review file"

    # FiveThirtyEight's own rating labels, read from the favorite's chance of winning.
    review["favorite"] = review[["Democrat_WinProbability", "Republican_WinProbability"]].max(axis=1)
    review["label"] = review["category"].str.replace(r" [DR]$", "", regex=True).str.replace("Safe", "Solid")
    review.loc[review["label"].str.startswith("Tossup"), "label"] = "Toss-up"
    ranges = review.groupby("label")["favorite"].agg(["min", "max", "size"]).sort_values("min")
    print("2018 rating labels by the favorite's chance:\n" + ranges.round(4).to_string())
    assert ranges.loc["Toss-up", "max"] < 0.60 <= ranges.loc["Lean", "min"]
    assert ranges.loc["Lean", "max"] < 0.75 <= ranges.loc["Likely", "min"]
    assert ranges.loc["Likely", "max"] < 0.95 <= ranges.loc["Solid", "min"]


if __name__ == "__main__":
    with tempfile.TemporaryDirectory() as folder:
        extract = build(folder)
        check_against_2018_review(extract, folder)

    # No race sits exactly on a rating cutoff, so the notebook's default right-closed bins are safe.
    favorite = extract["dem_prob"].where(extract["dem_prob"] >= 0.5, 1 - extract["dem_prob"])
    assert not favorite.isin([0.5, 0.6, 0.75, 0.95]).any()

    print(extract.groupby(["office", "year"]).size().to_string())
    extract.to_csv(OUTPUT, index=False)
    with open(OUTPUT, "rb") as f:
        print("wrote", os.path.basename(OUTPUT), len(extract), "rows; sha256", hashlib.sha256(f.read()).hexdigest())
