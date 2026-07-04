"""Cross-check our per-municipality median ratios against DOR's own published
Summary of Aggregate Ratios (assessed value ÷ DOR base value, per municipality).

    python -m analysis.crosscheck     # run AFTER the study inputs exist

Downloads raw/sumagg_<STUDY_YEAR>.xlsx (idempotent) from the DOR report
directory, recomputes the study's municipality medians through the exact same
pipeline (`study.compute()`), and prints them side by side. This is a level
sanity check, not a gate: DOR's ratio is an ALL-CLASS aggregate of totals,
ours is a residential-only median of sales — agreement should be rough
(within ~0.05 for residential-dominated cities/villages), and a large gap
means investigate before publishing.

A SYSTEMATIC negative delta is expected, not alarming — three mechanisms all
push DOR's figure above ours: (1) our sales are dated through the year while
assessments value January 1, so a rising market drags our ratios down;
(2) DOR's base value for year Y derives from year Y-1 sales (their documented
one-year offset), overstating their ratio in a rising market; (3) DOR's ratio
is all-class and commercial assesses closer to full value than residential
(WPF 2023). The check therefore flags each municipality's RESIDUAL — its
delta minus the county's median delta — which isolates idiosyncratic gaps
from the shared drift.

Stdlib xlsx parsing (zipfile + ElementTree): sumagg is a flat one-sheet table
(TAX YEAR | AUTH | CO-MUNI CODE | TYPE | MUNICIPALITY NAME | COUNTY NAME |
MFG ADMIN | EQ ADMIN | AGGREGATE RATIO) — verified against the 2024 edition.
"""

import statistics
import sys
import urllib.request
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

from . import config, study

SUMAGG_URL = ("https://www.revenue.wi.gov/SLFReportscotvc/"
              f"{config.STUDY_YEAR}sumagg.xlsx")
SUMAGG_XLSX = config.RAW_DIR / f"sumagg_{config.STUDY_YEAR}.xlsx"

_NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
_MUNI_TYPE = {"T": "TOWN OF", "V": "VILLAGE OF", "C": "CITY OF"}
WARN_RESIDUAL = 0.05   # |delta − county median delta| above this gets a flag


def parse_sumagg(path: Path, county_name: str) -> dict[str, float]:
    """sumagg workbook -> {PLACENAME-style name: aggregate ratio} for one
    county. Header row is located by content, so column reordering fails
    loudly instead of silently misreading."""
    z = zipfile.ZipFile(path)
    shared = []
    if "xl/sharedStrings.xml" in z.namelist():
        root = ET.fromstring(z.read("xl/sharedStrings.xml"))
        for si in root.findall("m:si", _NS):
            shared.append("".join(t.text or "" for t in si.iter("{%s}t" % _NS["m"])))

    def val(cell):
        v = cell.find("m:v", _NS)
        if v is None:
            return ""
        return shared[int(v.text)] if cell.get("t") == "s" else (v.text or "")

    rows = [[val(c) for c in r.findall("m:c", _NS)]
            for r in ET.fromstring(z.read("xl/worksheets/sheet1.xml")).findall(".//m:row", _NS)]
    if not rows:
        raise RuntimeError(f"{path} has no rows")
    header = [h.replace("\n", " ").strip().upper() for h in rows[0]]
    try:
        i_type = header.index("MUNICIPALITY TYPE")
        i_name = header.index("MUNICIPALITY NAME")
        i_county = header.index("COUNTY NAME")
        i_ratio = header.index("AGGREGATE RATIO")
    except ValueError as e:
        raise RuntimeError(f"sumagg header changed: {header}") from e

    out: dict[str, float] = {}
    want = f"{county_name.upper()} COUNTY"
    for r in rows[1:]:
        if len(r) <= i_ratio or r[i_county].strip().upper() != want:
            continue
        prefix = _MUNI_TYPE.get(r[i_type].strip().upper())
        if prefix is None:
            raise RuntimeError(f"unknown municipality type {r[i_type]!r} in {path}")
        out[f"{prefix} {r[i_name].strip().upper()}"] = float(r[i_ratio])
    if not out:
        raise RuntimeError(f"no {want} rows in {path} — county filter broken?")
    return out


def run() -> None:
    if not SUMAGG_XLSX.exists():
        config.RAW_DIR.mkdir(exist_ok=True)
        print(f"downloading {SUMAGG_URL}")
        with urllib.request.urlopen(SUMAGG_URL) as resp:
            SUMAGG_XLSX.write_bytes(resp.read())
    dor = parse_sumagg(SUMAGG_XLSX, config.COUNTY)

    findings = study.compute()
    rows = []
    for m in findings["municipalities"]:
        d = dor.get(m["name"].upper())
        rows.append((m, d, m["median_ratio"] - d if d is not None else None))
    deltas = [delta for _, _, delta in rows if delta is not None]
    shared = statistics.median(deltas) if deltas else 0.0

    print(f"\nDOR Summary of Aggregate Ratios ({config.STUDY_YEAR}) vs study medians")
    print("DOR ratio is ALL-CLASS aggregate against DOR base value; ours is a "
          "residential-only median against same-year sales. A shared negative "
          "drift is expected (see module docstring); the residual column is "
          "the anomaly signal.\n")
    print(f"{'municipality':<28} {'n':>5} {'study median':>13} {'DOR aggregate':>14} "
          f"{'delta':>8} {'residual':>9}")
    flagged = 0
    for m, d, delta in rows:
        if delta is None:
            print(f"{m['name']:<28} {m['n']:>5} {m['median_ratio']:>13.3f} {'NOT IN DOR':>14}")
            flagged += 1
            continue
        residual = delta - shared
        flag = "  <-- investigate" if abs(residual) > WARN_RESIDUAL else ""
        if flag:
            flagged += 1
        print(f"{m['name']:<28} {m['n']:>5} {m['median_ratio']:>13.3f} {d:>14.3f} "
              f"{delta:>+8.3f} {residual:>+9.3f}{flag}")
    print(f"\nshared drift (county median delta): {shared:+.3f}")
    print(f"{flagged} of {len(rows)} flagged (|residual| > {WARN_RESIDUAL} or missing).")


if __name__ == "__main__":
    sys.exit(run())
