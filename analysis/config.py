"""Study configuration. One responsibility: every parameter and threshold, in
one place, with the reason it exists.
"""

import os
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# ---- Scope -------------------------------------------------------------------
COUNTY = "Marathon"                 # RETR county name (TAP filter value)
COUNTY_UPPER = "MARATHON"           # parcel layer CONAME value
# Sales year AND required assessment roll year. The default is the current
# study; regenerate an earlier year with the env var instead of editing this
# file (PowerShell: `$env:WPR_STUDY_YEAR=2024; python -m analysis.study`), so
# a temporary flip can never be committed by accident.
STUDY_YEAR = int(os.environ.get("WPR_STUDY_YEAR", "2025"))

# ---- Sibling repo (browser automation lives there; we do not fork it) ---------
SIBLING_SCRAPER_REPO = REPO_ROOT.parent / "wpr-property-transactions"

# ---- Parcel layer (Wisconsin Statewide Parcel Map REST endpoint) ---------------
# Renamed with the V12 release (layer 0 = V1200_WisconsinParcels_2026, 2025 tax
# roll); the pre-V12 path "Wisconsin_Statewide_Parcels" now returns "Invalid
# URL" for every query. Verified 2026-09-05: same 47-field schema, all fields
# below present, 82,172 of 83,708 Marathon parcels on the 2025 roll.
PARCEL_ENDPOINT = (
    "https://services3.arcgis.com/n6uYoouQZW75n5WI/arcgis/rest/services/"
    "Wisconsin_Statewide_Parcels_DB/FeatureServer/0/query"
)
PARCEL_FIELDS = (
    "PARCELID,PLACENAME,PROPCLASS,AUXCLASS,TAXROLLYEAR,"
    "CNTASSDVALUE,LNDVALUE,IMPVALUE,NETPRPTA,ASSDACRES"
)
PARCEL_PAGE_SIZE = 2000             # endpoint maxRecordCount

# ---- File layout ---------------------------------------------------------------
RAW_DIR = REPO_ROOT / "raw"                          # gitignored; never committed
RETR_RAW_CSV = RAW_DIR / f"retr_{STUDY_YEAR}.csv"    # names/addresses/parcels
PARCEL_CSV = RAW_DIR / f"parcels_{COUNTY.lower()}_{STUDY_YEAR}.csv"
OUTPUT_DIR = REPO_ROOT / "output"                    # aggregate-only, committable
FINDINGS_MD = OUTPUT_DIR / f"findings-{STUDY_YEAR}.md"
FINDINGS_JSON = OUTPUT_DIR / f"findings-{STUDY_YEAR}.json"   # widget feed, per year
INDEX_JSON = OUTPUT_DIR / "index.json"               # {years, latest}: widget entry
CROSSCHECK_JSON = OUTPUT_DIR / f"crosscheck-{STUDY_YEAR}.json"  # DOR ratios per muni

# ---- Filter waterfall parameters ------------------------------------------------
MIN_SALE_PRICE = 10_000     # ratio-study floor (NOT the $1,000 editorial floor)
ACRE_TOLERANCE = 1.5        # RETR acres > parcel ASSDACRES * this + 0.5 => multi-
ACRE_SLACK = 0.5            # parcel sale fingerprint; excluded and counted
ACRE_FLOOR = 2.0            # fingerprint only fires above this: June-2025 evidence
                            # showed preparers enter "1" as default acreage on small
                            # city lots (34 of 35 flagged cases were retr=1.00 vs
                            # 0.1-0.3 acre lots — entry noise, not multi-parcel
                            # sales; the one genuine case was 65 acres vs 5)

# ---- Loud preconditions ----------------------------------------------------------
VINTAGE_MIN_SHARE = 0.95    # share of residential parcels whose TAXROLLYEAR must
                            # equal STUDY_YEAR. V11 serves 2024 -> fails until V12.
JOIN_RATE_MIN = 0.95        # spike measured 0.990 on June 2025 x V11
TAP_RESULT_CAP = 1000       # TAP caps any single search at 1000 returns (sibling
                            # spike-confirmed) and truncation is NOT date-ordered:
                            # a 2026-07-04 full-year pull returned exactly 1000
                            # rows spread across all 12 months. Backfill therefore
                            # pulls monthly and fails loudly if any window reaches
                            # this cap.

# ---- Analysis grouping ------------------------------------------------------------
MUNI_MIN_N = 30             # minimum trimmed sample for standalone muni statistics
N_DECILES = 10

# ---- IAAO reference bands (reported alongside results; not pass/fail gates) -------
IAAO_COD_MAX_SFR = 15.0     # single-family residential uniformity ceiling
IAAO_PRD_BAND = (0.98, 1.03)
IAAO_PRB_BAND = (-0.05, 0.05)
