"""parse_sumagg: stdlib xlsx parsing against a synthetic workbook shaped like
DOR's Summary of Aggregate Ratios (header located by content; county filter;
T/V/C -> PLACENAME-style names)."""

import zipfile

import pytest

from analysis.crosscheck import parse_sumagg

_SHEET_NS = 'xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"'

HEADERS = ["TAX YEAR", "AUTH", "CO-MUNI CODE", "MUNICIPALITY\nTYPE",
           "MUNICIPALITY NAME", "COUNTY NAME", "MFG ADMIN", "EQ ADMIN",
           "AGGREGATE\nRATIO"]
ROWS = [
    ["2024", "0001", "37251", "C", "WAUSAU", "MARATHON COUNTY", "79", "80", "0.941"],
    ["2024", "0002", "37191", "V", "WESTON", "MARATHON COUNTY", "79", "80", "0.902"],
    ["2024", "0003", "37010", "T", "BERGEN", "MARATHON COUNTY", "79", "80", "0.731"],
    ["2024", "0004", "01002", "T", "ADAMS", "ADAMS COUNTY", "79", "80", "0.990"],
]


def _write_sumagg(path, headers=HEADERS, rows=ROWS):
    strings, index = [], {}

    def sref(s):
        if s not in index:
            index[s] = len(strings)
            strings.append(s)
        return index[s]

    def cell(v):
        try:
            float(v)
            return f"<c><v>{v}</v></c>"
        except ValueError:
            return f'<c t="s"><v>{sref(v)}</v></c>'

    body = "".join(
        "<row>" + "".join(cell(v) for v in row) + "</row>"
        for row in [headers, *rows]
    )
    sheet = f'<?xml version="1.0"?><worksheet {_SHEET_NS}><sheetData>{body}</sheetData></worksheet>'
    sst = (f'<?xml version="1.0"?><sst {_SHEET_NS}>'
           + "".join(f"<si><t>{s}</t></si>" for s in strings) + "</sst>")
    with zipfile.ZipFile(path, "w") as z:
        z.writestr("xl/worksheets/sheet1.xml", sheet)
        z.writestr("xl/sharedStrings.xml", sst)


def test_parses_one_county_with_placename_keys(tmp_path):
    f = tmp_path / "sumagg.xlsx"
    _write_sumagg(f)
    out = parse_sumagg(f, "Marathon")
    assert out == {
        "CITY OF WAUSAU": 0.941,
        "VILLAGE OF WESTON": 0.902,
        "TOWN OF BERGEN": 0.731,
    }


def test_tolerates_dor_header_typo(tmp_path):
    # The 2025 edition shipped "MINUCIPALITY NAME"; column lookup is by
    # content, so the typo must not break the parse.
    f = tmp_path / "sumagg.xlsx"
    typo = [h.replace("MUNICIPALITY NAME", "MINUCIPALITY NAME") for h in HEADERS]
    _write_sumagg(f, headers=typo)
    assert parse_sumagg(f, "Marathon")["CITY OF WAUSAU"] == 0.941


def test_missing_county_fails_loudly(tmp_path):
    f = tmp_path / "sumagg.xlsx"
    _write_sumagg(f)
    with pytest.raises(RuntimeError, match="no DANE COUNTY rows"):
        parse_sumagg(f, "Dane")


def test_changed_header_fails_loudly(tmp_path):
    f = tmp_path / "sumagg.xlsx"
    _write_sumagg(f, headers=["SOMETHING", "ELSE"], rows=[])
    with pytest.raises(RuntimeError, match="header changed"):
        parse_sumagg(f, "Marathon")
