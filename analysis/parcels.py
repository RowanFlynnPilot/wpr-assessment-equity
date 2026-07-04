"""Assessment side. One responsibility: county parcel index from the Wisconsin
Statewide Parcel Map REST endpoint.

    python -m analysis.parcels     # fetch -> raw/parcels_<county>_<year>.csv

`fetch` pages the endpoint (attributes only, no geometry) and writes one CSV.
`load` reads that CSV into {normalized_parcel_id: row} and enforces the VINTAGE
GATE: if fewer than VINTAGE_MIN_SHARE of residential parcels carry
TAXROLLYEAR == STUDY_YEAR, the study refuses to run — that is the release lag
(V11 = 2024 roll) and the correct behavior is to wait for the V12 release, not
to compute vintage-mismatched ratios.
"""

import csv
import json
import urllib.parse
import urllib.request

from . import config
from .join import normalize_parcel_id

_COLUMNS = config.PARCEL_FIELDS.split(",")


def fetch() -> None:
    config.RAW_DIR.mkdir(exist_ok=True)
    offset, written = 0, 0
    with open(config.PARCEL_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=_COLUMNS)
        w.writeheader()
        while True:
            q = urllib.parse.urlencode({
                "where": f"CONAME='{config.COUNTY_UPPER}'",
                "outFields": config.PARCEL_FIELDS,
                "returnGeometry": "false",
                "resultOffset": offset,
                "resultRecordCount": config.PARCEL_PAGE_SIZE,
                "f": "json",
            })
            with urllib.request.urlopen(f"{config.PARCEL_ENDPOINT}?{q}", timeout=120) as r:
                d = json.load(r)
            if "error" in d:
                raise RuntimeError(f"parcel endpoint error at offset {offset}: {d['error']}")
            feats = d.get("features", [])
            if not feats:
                break
            for feat in feats:
                w.writerow({k: feat["attributes"].get(k) for k in _COLUMNS})
            written += len(feats)
            offset += len(feats)
            print(f"  fetched {written} parcels...", flush=True)
            if not d.get("exceededTransferLimit") and len(feats) < config.PARCEL_PAGE_SIZE:
                break
    if written < 1000:
        raise RuntimeError(f"only {written} parcels fetched for {config.COUNTY_UPPER} — "
                           "endpoint or filter is broken")
    print(f"Wrote {written} parcels to {config.PARCEL_CSV}")


def load() -> dict[str, dict]:
    """raw CSV -> {normalized PARCELID: row}. Enforces the vintage gate."""
    if not config.PARCEL_CSV.exists():
        raise FileNotFoundError(
            f"{config.PARCEL_CSV} missing — run `python -m analysis.parcels` first")
    index: dict[str, dict] = {}
    with open(config.PARCEL_CSV, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            pid = normalize_parcel_id(row["PARCELID"] or "")
            if pid:
                index[pid] = row

    residential = [r for r in index.values() if (r["PROPCLASS"] or "") == "1"]
    if not residential:
        raise RuntimeError("no PROPCLASS==1 parcels in index — fetch is broken")
    on_vintage = sum(1 for r in residential
                     if str(r["TAXROLLYEAR"]).strip() == str(config.STUDY_YEAR))
    share = on_vintage / len(residential)
    if share < config.VINTAGE_MIN_SHARE:
        raise RuntimeError(
            f"VINTAGE GATE: only {share:.1%} of residential parcels carry the "
            f"{config.STUDY_YEAR} tax roll (need >= {config.VINTAGE_MIN_SHARE:.0%}). "
            f"The endpoint is still serving an older release (V11 = 2024 roll; "
            f"V12 with the 2025 roll was scheduled for 2026-06-30). Re-run "
            f"`python -m analysis.parcels` once V12 is live. Do NOT bypass this: "
            f"ratios against the wrong assessment year are noise, not findings.")
    print(f"Parcel index: {len(index)} parcels, vintage {config.STUDY_YEAR} "
          f"({share:.1%} of residential on-vintage)")
    return index


if __name__ == "__main__":
    fetch()
