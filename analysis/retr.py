"""Sales side. Two responsibilities kept in one thin module: (1) backfill the
study year's raw RETR CSV using the SIBLING repo's browser automation; (2) turn
that raw CSV into the study population via the documented filter waterfall.

    python -m analysis.retr        # backfill -> raw/retr_<year>.csv

The sibling repo (`wpr-property-transactions`) owns the one correct path into
DOR TAP. We import its `tap.download_report` and nothing else — this repo
parses the raw CSV itself because the study needs columns the transactions
feed discards (relationship, exemption, part-of-parcel, acres).

The raw CSV contains names, addresses, and parcel numbers. It lives in raw/
(gitignored) and is NEVER committed. Everything published from this repo is
aggregate-only.
"""

import calendar
import csv
import sys
import tempfile
import time
from datetime import date
from pathlib import Path

from . import config

# ---- Filter waterfall (order matters; every step is counted) --------------------

WATERFALL = [
    ("conveyance is Sale",
     lambda r: r["Conveyance Type"].strip() == "Sale"),
    ("arm's length (no grantor/grantee relationship)",
     lambda r: r["Grantor/Grantee Relationship"].strip() == "No relationship"),
    ("no fee exemption claimed",
     lambda r: r["Fee Exemption"].strip() == ""),
    ("entire parcel transferred",
     lambda r: r["Part of Parcel Transferred"].strip().startswith("1.")),
    ("single family use",
     lambda r: r["Property Use Type"].strip().startswith("Single family")),
    (f"sale price >= ${config.MIN_SALE_PRICE:,}",
     lambda r: r["_price"] >= config.MIN_SALE_PRICE),
    (f"recorded in {config.STUDY_YEAR}",
     lambda r: r["Recorded Date"].strip().endswith(str(config.STUDY_YEAR))),
]


def _money(raw: str) -> int:
    s = (raw or "").replace("$", "").replace(",", "").strip()
    return int(round(float(s))) if s else 0


def _acres(raw: str) -> float:
    s = (raw or "").replace(",", "").strip()
    return float(s) if s else 0.0


def load_study_population(csv_path: Path) -> tuple[list[dict], list[tuple[str, int]]]:
    """Raw CSV -> (study rows, waterfall counts). Rows keep raw columns plus
    parsed `_price` and `_acres`."""
    with open(csv_path, newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        raise RuntimeError(f"{csv_path} is empty — backfill failed silently?")
    for r in rows:
        r["_price"] = _money(r["Sale Price"])
        r["_acres"] = _acres(r["Acres"])

    counts: list[tuple[str, int]] = [("raw RETR rows", len(rows))]
    kept = rows
    for name, keep in WATERFALL:
        kept = [r for r in kept if keep(r)]
        counts.append((name, len(kept)))
    return kept, counts


# ---- Backfill --------------------------------------------------------------------

_PULL_ATTEMPTS = 3          # same transient-flake retry the sibling's history.py
                            # uses on this exact browser flow


def merge_monthly(monthly: list[list[dict]]) -> tuple[list[dict], int]:
    """Concatenate monthly pulls in order, deduping on Document Number (the
    recorded-date windows are disjoint, so a duplicate can only be a window-edge
    overlap). Returns (rows, n_duplicates_dropped). Pure; unit-tested."""
    seen: set[str] = set()
    rows: list[dict] = []
    dupes = 0
    for pull in monthly:
        for r in pull:
            doc = r["Document Number"].strip()
            if doc in seen:
                dupes += 1
                continue
            seen.add(doc)
            rows.append(r)
    return rows, dupes


def _pull(download_report, county: str, d_from: date, d_to: date,
          tmp_dir: Path) -> Path:
    for attempt in range(1, _PULL_ATTEMPTS + 1):
        try:
            return download_report(county, d_from, d_to, tmp_dir)
        except Exception as exc:
            if attempt == _PULL_ATTEMPTS:
                raise
            print(f"  {d_from:%Y-%m} attempt {attempt} failed ({exc}); retrying")
            time.sleep(5)


def backfill() -> None:
    """Twelve monthly TAP pulls merged on Document Number. TAP caps any single
    search at TAP_RESULT_CAP returns and the truncation is NOT date-ordered
    (a full-year pull returns a 1000-row sample spread across all 12 months),
    so wide windows silently sample the year. Marathon runs ~300-500 recorded
    conveyances a month — comfortably under the cap. Tripwires: every monthly
    pull must be non-empty AND below the cap."""
    if not config.SIBLING_SCRAPER_REPO.is_dir():
        raise FileNotFoundError(
            f"sibling checkout not found at {config.SIBLING_SCRAPER_REPO} — "
            f"clone RowanFlynnPilot/wpr-property-transactions next to this repo")
    sys.path.insert(0, str(config.SIBLING_SCRAPER_REPO))
    from scraper.tap import download_report  # noqa: E402  (sibling import)

    config.RAW_DIR.mkdir(exist_ok=True)
    y = config.STUDY_YEAR
    monthly: list[list[dict]] = []
    fieldnames: list[str] | None = None
    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        for m in range(1, 13):
            last = calendar.monthrange(y, m)[1]
            csv_path = _pull(download_report, config.COUNTY,
                             date(y, m, 1), date(y, m, last), tmp_dir)
            with open(csv_path, newline="", encoding="utf-8-sig") as f:
                reader = csv.DictReader(f)
                rows = list(reader)
            if fieldnames is None:
                fieldnames = list(rows[0].keys()) if rows else None
            elif rows and list(rows[0].keys()) != fieldnames:
                raise RuntimeError(f"{y}-{m:02d} pull has a different header — "
                                   f"TAP report layout changed mid-backfill")
            if not rows:
                raise RuntimeError(
                    f"{y}-{m:02d} pull returned zero rows — implausible for "
                    f"{config.COUNTY}; TAP flow or window is broken")
            if len(rows) >= config.TAP_RESULT_CAP:
                raise RuntimeError(
                    f"{y}-{m:02d} pull returned {len(rows)} rows — at the TAP "
                    f"result cap; the month was silently truncated. The window "
                    f"must shrink (a design change), not be retried.")
            print(f"  {y}-{m:02d}: {len(rows)} rows")
            monthly.append(rows)

    merged, dupes = merge_monthly(monthly)
    with open(config.RETR_RAW_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(merged)
    print(f"Backfill complete: {config.RETR_RAW_CSV} "
          f"({len(merged)} rows from 12 monthly pulls, {dupes} duplicates dropped)")


if __name__ == "__main__":
    backfill()
