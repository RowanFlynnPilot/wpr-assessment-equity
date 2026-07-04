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

import csv
import sys
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

def backfill() -> None:
    """One full-year TAP pull. Completeness tripwire: the CSV must contain
    recorded dates in BOTH January and December of the study year — if TAP ever
    caps a full-year result set, this fails loudly and the fix is a deliberate
    design change (quarterly windows merged on Document Number), not a retry."""
    if not config.SIBLING_SCRAPER_REPO.is_dir():
        raise FileNotFoundError(
            f"sibling checkout not found at {config.SIBLING_SCRAPER_REPO} — "
            f"clone RowanFlynnPilot/wpr-property-transactions next to this repo")
    sys.path.insert(0, str(config.SIBLING_SCRAPER_REPO))
    from scraper.tap import download_report  # noqa: E402  (sibling import)

    config.RAW_DIR.mkdir(exist_ok=True)
    y = config.STUDY_YEAR
    csv_path = download_report(config.COUNTY, date(y, 1, 1), date(y, 12, 31),
                               config.RAW_DIR)
    Path(csv_path).replace(config.RETR_RAW_CSV)

    months = set()
    with open(config.RETR_RAW_CSV, newline="", encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            mm, _, yyyy = r["Recorded Date"].strip().partition("-")
            if yyyy.endswith(str(y)):
                months.add(int(mm))
    if not {1, 12} <= months:
        raise RuntimeError(
            f"backfill CSV covers months {sorted(months)} — missing the window "
            f"edges. TAP likely capped the result set; redesign as quarterly "
            f"windows merged on Document Number.")
    print(f"Backfill complete: {config.RETR_RAW_CSV} (months {sorted(months)})")


if __name__ == "__main__":
    backfill()
