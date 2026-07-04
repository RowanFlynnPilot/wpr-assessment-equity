"""Join contract. One responsibility: match a RETR sale to its parcel record.

Spike-validated 2026-07-04: RETR Marathon parcels are `NNN-NNNN-NNN-NNNN`
(14 digits + dashes); the statewide layer's PARCELID is the same 14 digits bare.
Normalization is therefore digit-extraction, nothing cleverer. June-2025 join
rate against the live endpoint: 99.0% (197/199).
"""

import re
from dataclasses import dataclass

from . import config

_DIGITS = re.compile(r"\D")


def normalize_parcel_id(raw: str) -> str:
    """'004-3006-032-0999' -> '00430060320999'. Strips tabs/spaces/dashes; the
    empty string means no parcel id."""
    return _DIGITS.sub("", raw or "")


@dataclass(frozen=True)
class Match:
    sale: dict      # the raw RETR row
    parcel: dict    # the parcel index row


def acreage_plausible(retr_acres: float, parcel_acres_raw: str) -> bool:
    """False when the conveyance's total acres grossly exceed the matched
    parcel's assessed acres — the fingerprint of a multi-parcel sale carrying a
    single parcel number (the RETR CSV emits one row per document; verified:
    zero duplicated document numbers in a full month). When either side is
    missing, the check cannot fire and the pair passes.

    ACRE_FLOOR guards a data-entry artifact found in the June-2025 evidence:
    preparers enter "1" as a default acreage on small city lots (34 of 35
    flagged cases), so sub-floor conveyance acreage is noise and never fires."""
    if retr_acres <= config.ACRE_FLOOR:
        return True
    try:
        parcel_acres = float(parcel_acres_raw)
    except (TypeError, ValueError):
        return True
    if parcel_acres <= 0:
        return True
    return retr_acres <= parcel_acres * config.ACRE_TOLERANCE + config.ACRE_SLACK


def join(sales: list[dict], index: dict[str, dict]) -> tuple[list[Match], dict[str, int]]:
    """Match sales to parcels. Returns (matches, exclusion counts). Asserts the
    join rate — a collapse below JOIN_RATE_MIN means the ID contract broke, and
    the study must stop, not limp."""
    matched, no_parcel, not_class1, bad_acres = [], 0, 0, 0
    for s in sales:
        pid = normalize_parcel_id(s["Parcel Number"])
        parcel = index.get(pid)
        if parcel is None:
            no_parcel += 1
            continue
        if (parcel["PROPCLASS"] or "").strip() != "1":
            not_class1 += 1
            continue
        if not acreage_plausible(s["_acres"], parcel["ASSDACRES"]):
            bad_acres += 1
            continue
        matched.append(Match(sale=s, parcel=parcel))

    attempted = len(sales)
    if attempted:
        rate = (attempted - no_parcel) / attempted
        if rate < config.JOIN_RATE_MIN:
            raise RuntimeError(
                f"join rate {rate:.1%} < {config.JOIN_RATE_MIN:.0%} — the parcel "
                f"ID contract is broken (format change or wrong county). Stop and "
                f"diagnose; do not analyze a biased subsample.")
    return matched, {
        "no parcel match": no_parcel,
        "parcel not pure class 1": not_class1,
        "acreage mismatch (multi-parcel fingerprint)": bad_acres,
    }
