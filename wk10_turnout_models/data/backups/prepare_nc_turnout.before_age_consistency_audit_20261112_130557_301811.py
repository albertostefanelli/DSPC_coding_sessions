"""Prepare a fixed, de-identified North Carolina turnout teaching extract.

This supporting script does the large-file preparation once. Students only read
the resulting small CSV. No names, addresses, telephone numbers, or public voter
identifiers are written to the teaching extract or printed by this script.

Run from the repository root with the validation environment:
    .private/validation_venv/bin/python wk10_turnout_models/data/prepare_nc_turnout.py

Downloads remain compressed in /private/tmp/wk10_nc_raw. ZIP members are read in
chunks; the very large uncompressed statewide files are never written to disk.
The current registry and history change weekly. The source manifest records the
exact download timestamps, HTTP metadata, byte sizes, and SHA-256 checksums.
"""

from __future__ import annotations

import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import urllib.request
import zipfile
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd


BASE_URL = "https://s3.amazonaws.com/dl.ncsbe.gov/"
SOURCES = {
    "snapshot": BASE_URL + "data/Snapshots/VR_Snapshot_20240101.zip",
    "history": BASE_URL + "data/ncvhis_Statewide.zip",
    "current_registry": BASE_URL + "data/ncvoter_Statewide.zip",
}
ELECTIONS = {
    2018: "11/06/2018",
    2020: "11/03/2020",
    2022: "11/08/2022",
    2024: "11/05/2024",
}
REGISTERED_STATUSES = {"ACTIVE", "INACTIVE", "TEMPORARY"}
CHUNK_SIZE = 150_000
SAMPLE_SIZE = 50_000
SAMPLE_SEED = 202410


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def sha256_file(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def backup_existing(path):
    """Preserve any previous output, including possible manual changes."""
    if path.exists():
        stamp = datetime.now(ZoneInfo("America/New_York")).strftime("%Y%m%d_%H%M%S_%f")
        backup_dir = path.parent / "backups"
        backup_dir.mkdir(exist_ok=True)
        shutil.copy2(path, backup_dir / f"{path.stem}.before_prepare_{stamp}{path.suffix}")


def download_source(name, url, raw_dir, old_manifest):
    """Reuse only a previously recorded, checksum-verified compressed source."""
    path = raw_dir / url.rsplit("/", 1)[-1]
    old = old_manifest.get(name)
    if path.exists() and old and old.get("url") == url:
        if path.stat().st_size == old["bytes"] and sha256_file(path) == old["sha256"]:
            print(f"Using verified cached source: {name}", flush=True)
            return name, old

    partial = path.with_suffix(path.suffix + ".part")
    request_started = utc_now()
    request = urllib.request.Request(url, headers={"User-Agent": "NC-turnout-teaching-preparation/1.0"})
    with urllib.request.urlopen(request, timeout=120) as response, partial.open("wb") as out:
        headers = {key: response.headers.get(key) for key in ["ETag", "Last-Modified", "Content-Length"]}
        digest = hashlib.sha256()
        size = 0
        last_report = 0
        while True:
            block = response.read(8 * 1024 * 1024)
            if not block:
                break
            out.write(block)
            digest.update(block)
            size += len(block)
            if size - last_report >= 250 * 1024 * 1024:
                print(f"Downloaded {name}: {size / 1_000_000:.0f} MB", flush=True)
                last_report = size
    if headers["Content-Length"] and size != int(headers["Content-Length"]):
        raise ValueError(f"Incomplete source download: {name}")
    backup_existing(path)
    partial.replace(path)
    result = {
        "url": url,
        "local_compressed_filename": path.name,
        "download_started_utc": request_started,
        "download_completed_utc": utc_now(),
        "bytes": size,
        "sha256": digest.hexdigest(),
        "http_headers": headers,
    }
    print(f"Source ready: {name} ({size / 1_000_000:.1f} MB)", flush=True)
    return name, result


def source_details(path):
    """Inspect ZIP metadata and the column header, without displaying records."""
    with zipfile.ZipFile(path) as archive:
        members = [info for info in archive.infolist() if not info.is_dir() and info.filename.lower().endswith((".txt", ".csv"))]
        if len(members) != 1:
            raise ValueError(f"Expected exactly one data member in {path.name}; found {len(members)}")
        info = members[0]
        with archive.open(info) as stream:
            prefix = stream.read(4)
        # Snapshot files declare UTF-16 with a byte-order mark. The required
        # fields in the other files are ASCII; a byte-preserving single-byte
        # decoder avoids failures on accents in unused names or precincts.
        encoding = "utf-16" if prefix.startswith((b"\xff\xfe", b"\xfe\xff")) else "latin-1"
        with archive.open(info) as stream:
            columns = list(pd.read_csv(stream, sep="\t", encoding=encoding, nrows=0).columns)
        return {
            "member": info.filename,
            "uncompressed_bytes": info.file_size,
            "compressed_bytes": info.compress_size,
            "zip_crc32": f"{info.CRC:08x}",
            "encoding": encoding,
            "columns": columns,
        }


@contextmanager
def source_chunks(path, details, columns):
    """Select only the necessary fields while streaming each compressed member."""
    lookup = {name.strip().lower(): name for name in details["columns"]}
    missing = set(columns) - set(lookup)
    if missing:
        raise ValueError(f"Required columns missing from {path.name}: {sorted(missing)}")
    with zipfile.ZipFile(path) as archive, archive.open(details["member"]) as stream:
        reader = pd.read_csv(
            stream, sep="\t", encoding=details["encoding"],
            usecols=[lookup[name] for name in columns], dtype=str,
            keep_default_na=False, chunksize=CHUNK_SIZE,
        )
        def normalized_chunks():
            for chunk in reader:
                chunk.columns = [name.strip().lower() for name in chunk.columns]
                for name in chunk.columns:
                    chunk[name] = chunk[name].str.strip()
                yield chunk
        yield normalized_chunks()


def select_snapshot_sample(path, details):
    """Uniform random priorities select records before any history is read.

    Every eligible row receives one independent random number. The 50,000
    smallest numbers form a simple random sample, regardless of chunking. IDs
    repeated among eligible registrations are excluded, rather than resolving
    competing eligible records using later turnout. A removed historical
    registration sharing an ID with one eligible row does not exclude a person.
    """
    rng = np.random.default_rng(SAMPLE_SEED)
    sample = pd.DataFrame()
    all_ids = set()
    duplicate_ids = set()
    eligible_ids = set()
    duplicate_eligible_ids = set()
    counts = Counter()
    status_counts = Counter()
    with source_chunks(path, details, ["ncid", "age", "registr_dt", "voter_status_desc"]) as chunks:
        for number, chunk in enumerate(chunks, 1):
            counts["all_snapshot_rows"] += len(chunk)
            status = chunk["voter_status_desc"].str.upper()
            status_counts.update(status)
            for ncid in chunk["ncid"]:
                if not ncid:
                    counts["blank_ncid_rows"] += 1
                elif ncid in all_ids:
                    counts["repeated_ncid_rows"] += 1
                    duplicate_ids.add(ncid)
                else:
                    all_ids.add(ncid)

            registered = status.isin(REGISTERED_STATUSES)
            age = pd.to_numeric(chunk["age"], errors="coerce")
            counts["registered_status_rows"] += int(registered.sum())
            counts["registered_missing_or_nonnumeric_age"] += int((registered & age.isna()).sum())
            counts["registered_age_under_18"] += int((registered & (age < 18)).sum())
            counts["registered_age_above_110"] += int((registered & (age > 110)).sum())
            valid_age = age.between(18, 110) & (age % 1 == 0)
            eligible = registered & valid_age & chunk["ncid"].ne("")
            candidates = chunk.loc[eligible, ["ncid", "registr_dt"]].copy()
            for ncid in candidates["ncid"]:
                if ncid in eligible_ids:
                    counts["repeated_eligible_ncid_rows"] += 1
                    duplicate_eligible_ids.add(ncid)
                else:
                    eligible_ids.add(ncid)
            candidates["age_2024"] = age[eligible].astype(int)
            candidates["sample_priority"] = rng.random(len(candidates))
            counts["eligible_rows_before_ncid_uniqueness_audit"] += len(candidates)
            sample = pd.concat([sample, candidates], ignore_index=True)
            if len(sample) > SAMPLE_SIZE:
                sample = sample.nsmallest(SAMPLE_SIZE, "sample_priority").reset_index(drop=True)
            if number % 10 == 0:
                print(f"Snapshot rows checked: {counts['all_snapshot_rows']:,}", flush=True)

    counts["unique_nonblank_snapshot_ncids"] = len(all_ids)
    counts["duplicated_snapshot_ncids"] = len(duplicate_ids)
    counts["unique_eligible_snapshot_ncids"] = len(eligible_ids)
    counts["duplicated_eligible_snapshot_ncids"] = len(duplicate_eligible_ids)
    counts["random_sample_before_uniqueness_exclusion"] = len(sample)
    counts["sample_rows_with_ncid_repeated_anywhere_in_snapshot"] = int(sample["ncid"].isin(duplicate_ids).sum())
    ambiguous = sample["ncid"].isin(duplicate_eligible_ids)
    counts["sample_rows_excluded_duplicate_eligible_snapshot_ncid"] = int(ambiguous.sum())
    sample = sample.loc[~ambiguous].sort_values("sample_priority").reset_index(drop=True)
    if not sample["ncid"].is_unique:
        raise AssertionError("Snapshot sample NCIDs are not unique")
    registration = pd.to_datetime(sample["registr_dt"], format="%Y-%m-%d", errors="coerce")
    sample["registration_year"] = registration.dt.year.astype("Int64")
    counts["sample_missing_or_unparseable_registration_date"] = int(registration.isna().sum())
    counts["sample_registration_date_after_snapshot"] = int((registration > pd.Timestamp("2024-01-01")).sum())
    print(f"Random snapshot sample ready: {len(sample):,} records", flush=True)
    return sample, {"counts": dict(counts), "snapshot_status_counts": dict(status_counts)}


def audit_registry(sample, path, details):
    """Confirm ID persistence, including removed and other non-active records.

    This does not require that a person still be actively registered. A missing
    ID is an unknown linkage, not an observed nonvote. NCID identifies the
    person, so repeated registry rows with the same ID still prove persistence;
    we do not use a current demographic row or choose a current county.
    """
    selected_ids = set(sample["ncid"])
    matches = Counter()
    statuses = Counter()
    total_rows = 0
    with source_chunks(path, details, ["ncid", "voter_status_desc"]) as chunks:
        for chunk in chunks:
            total_rows += len(chunk)
            present = chunk[chunk["ncid"].isin(selected_ids)]
            matches.update(present["ncid"])
            statuses.update(present["voter_status_desc"].str.upper())
    match_count = sample["ncid"].map(matches).fillna(0).astype(int)
    report = {
        "all_current_registry_rows_scanned": total_rows,
        "sample_unique_registry_match": int((match_count == 1).sum()),
        "sample_no_registry_match": int((match_count == 0).sum()),
        "sample_multiple_registry_matches": int((match_count > 1).sum()),
        "matched_current_status_counts_including_removed": dict(statuses),
    }
    kept = sample.loc[match_count >= 1].copy()
    print(f"Registry linkage: {len(kept):,} IDs present; {len(sample) - len(kept):,} absent and excluded", flush=True)
    return kept, report


def attach_history(sample, path, details):
    """A 1 means an official participation record exists for that election.

    A 0 means no such record was found for a retained NCID present in the registry.
    It does not prove eligibility, residence in NC, or nonvoting elsewhere.
    Repeated rows for a person/election are counted once, never as extra votes.
    """
    selected_ids = set(sample["ncid"])
    any_history = set()
    voters = {year: set() for year in ELECTIONS}
    selected_target_rows = Counter()
    all_dates = Counter()
    total_rows = 0
    with source_chunks(path, details, ["ncid", "election_lbl"]) as chunks:
        for number, chunk in enumerate(chunks, 1):
            total_rows += len(chunk)
            all_dates.update(chunk["election_lbl"])
            selected = chunk[chunk["ncid"].isin(selected_ids)]
            any_history.update(selected["ncid"])
            for year, label in ELECTIONS.items():
                election_ids = selected.loc[selected["election_lbl"] == label, "ncid"]
                selected_target_rows[year] += len(election_ids)
                voters[year].update(election_ids)
            if number % 30 == 0:
                print(f"History rows checked: {total_rows:,}", flush=True)
    election_report = {}
    for year, label in ELECTIONS.items():
        if all_dates[label] == 0:
            raise AssertionError(f"Required election not present in history source: {year}")
        sample[f"voted_{year}"] = sample["ncid"].isin(voters[year]).astype(int)
        election_report[str(year)] = {
            "election_date_label": label,
            "statewide_history_rows_for_election": all_dates[label],
            "sample_participation_rows_before_deduplication": selected_target_rows[year],
            "sample_unique_participants": len(voters[year]),
            "sample_duplicate_person_election_rows": selected_target_rows[year] - len(voters[year]),
            "sample_recorded_turnout_share": float(sample[f"voted_{year}"].mean()),
        }
    report = {
        "all_history_rows_scanned": total_rows,
        "election_coverage": election_report,
        "sample_with_any_history_in_current_history_file": len(any_history),
        "sample_no_history_but_current_registry_id_present": len(sample) - len(any_history),
        "sample_no_recorded_turnout_in_four_selected_elections": int((sample[[f"voted_{year}" for year in ELECTIONS]].sum(axis=1) == 0).sum()),
        "history_election_labels_and_row_counts": dict(sorted(all_dates.items())),
    }
    return sample, report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-dir", type=Path, default=Path("/private/tmp/wk10_nc_raw"))
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument("--inspect-only", action="store_true", help="Download and inspect headers; do not select or export records.")
    args = parser.parse_args()
    args.raw_dir.mkdir(parents=True, exist_ok=True)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = args.raw_dir / "source_manifest.json"
    old_manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else {}
    started = utc_now()
    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = [pool.submit(download_source, name, url, args.raw_dir, old_manifest) for name, url in SOURCES.items()]
        manifest = dict(future.result() for future in futures)
    backup_existing(manifest_path)
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
    paths = {name: args.raw_dir / entry["local_compressed_filename"] for name, entry in manifest.items()}
    details = {name: source_details(path) for name, path in paths.items()}
    for name, entry in details.items():
        print(f"Inspected {name}: {len(entry['columns'])} columns; {entry['encoding']}; {entry['uncompressed_bytes'] / 1e9:.2f} GB uncompressed", flush=True)
    if args.inspect_only:
        return

    sample, snapshot_report = select_snapshot_sample(paths["snapshot"], details["snapshot"])
    sample, registry_report = audit_registry(sample, paths["current_registry"], details["current_registry"])
    sample, history_report = attach_history(sample, paths["history"], details["history"])
    public_columns = ["age_2024", "registration_year"] + [f"voted_{year}" for year in ELECTIONS]
    teaching = sample[public_columns].reset_index(drop=True)
    teaching.insert(0, "row_id", np.arange(1, len(teaching) + 1))
    assert 0 < len(teaching) <= SAMPLE_SIZE
    assert teaching["row_id"].is_unique
    assert teaching["age_2024"].between(18, 110).all()
    assert teaching[[f"voted_{year}" for year in ELECTIONS]].isin([0, 1]).all().all()
    assert set(teaching.columns) == set(["row_id"] + public_columns)

    output_path = args.output_dir / "nc_turnout_2024_teaching.csv"
    backup_existing(output_path)
    teaching.to_csv(output_path, index=False, lineterminator="\n")
    report = {
        "preparation_started_utc": started,
        "preparation_completed_utc": utc_now(),
        "script_sha256": sha256_file(Path(__file__).resolve()),
        "python_packages": {"pandas": pd.__version__, "numpy": np.__version__},
        "sources": manifest,
        "source_layouts": details,
        "selection": {
            "snapshot_date": "2024-01-01",
            "registered_statuses": sorted(REGISTERED_STATUSES),
            "minimum_age": 18,
            "maximum_age": 110,
            "requested_sample_size": SAMPLE_SIZE,
            "random_seed": SAMPLE_SEED,
            "method": "Independent uniform random priorities over eligible snapshot rows; keep 50,000 smallest before reading history. Exclude sampled IDs repeated among eligible snapshot rows, then IDs absent from the current registry. Repeats involving removed snapshot rows do not disqualify a unique eligible record. No replacement or outcome-based resampling.",
            "snapshot_audit": snapshot_report,
            "registry_linkage_audit": registry_report,
        },
        "history_audit": history_report,
        "output": {
            "filename": output_path.name,
            "rows": len(teaching),
            "columns": list(teaching.columns),
            "bytes": output_path.stat().st_size,
            "sha256": sha256_file(output_path),
            "missing_values": {key: int(value) for key, value in teaching.isna().sum().items()},
        },
        "column_definitions": {
            "row_id": "New sequential teaching-row identifier; not an NCSBE identifier and not a lookup key to a public voter record.",
            "age_2024": "Age reported in the January 1, 2024 registration snapshot; use as a dated approximate age predictor, not exact age on Election Day.",
            "registration_year": "Year of registr_dt in the January 2024 administrative record, when parseable; not necessarily first eligibility or first-ever registration. Blank means unavailable or masked.",
            "voted_2018, voted_2020, voted_2022, voted_2024": "1 if the current statewide history contains that general-election participation record for the matched NCID; 0 if none was found. Repeated person/election rows count once.",
        },
        "limitations": [
            "The population is January 2024 registered adults with ages 18-110, a unique eligible snapshot record, and a retained administrative ID, not all North Carolina residents or everyone eligible to vote in November 2024. Later registrants are excluded.",
            "Registry linkage uses a later administrative file and therefore excludes absent IDs after sampling; this can introduce attrition bias. Removed records are retained when their ID is present; selection does not require current active status.",
            "No history row means no participation recorded in this North Carolina history file. Earlier zeros may reflect youth, later registration, moving from another state, or administrative incompleteness rather than a decision to abstain.",
            "Current-registry ID presence verifies identity persistence, not perfect historical-record completeness. Administrative corrections or missing history can still affect outcomes.",
            "The record does not identify who received campaign contact. Predictions describe recorded turnout under the campaigns that actually occurred, not experimentally identified turnout without contact or the effect of a new contact.",
            "A random held-out set tests predictions for other retained cohort members in 2024. It does not demonstrate accuracy for a different election or a newly registered population.",
            "The official history file covers only the most recent ten years and changes weekly. A future rerun against newly downloaded sources need not reproduce this fixed teaching extract.",
            "No 2026 outcome is used because election histories may still be incomplete shortly after that election.",
        ],
        "official_documentation": {
            "registration": "https://www.ncsbe.gov/results-data/voter-registration-data",
            "history": "https://www.ncsbe.gov/results-data/voter-history-data",
            "snapshot_layout": BASE_URL + "data/Snapshots/layout_VR_Snapshot.txt",
            "registry_layout": BASE_URL + "data/layout_ncvoter.txt",
            "history_layout": BASE_URL + "data/layout_ncvhis.txt",
            "data_guidance": "https://www.ncsbe.gov/about-elections/county-boards-elections/county-resources/county-board-kit/how-work-our-data",
        },
    }
    report_path = args.output_dir / "nc_turnout_2024_preparation_report.json"
    backup_existing(report_path)
    report_path.write_text(json.dumps(report, indent=2) + "\n")
    print(f"Exported {len(teaching):,} anonymous rows; CSV SHA-256: {report['output']['sha256']}", flush=True)
    print(json.dumps(history_report["election_coverage"], indent=2), flush=True)


if __name__ == "__main__":
    main()
