"""merge_monthly: order-preserving concat of monthly pulls, dedupe on Document
Number (window-edge overlaps only — recorded-date windows are disjoint)."""

from analysis.retr import merge_monthly


def _row(doc: str, **extra) -> dict:
    return {"Document Number": doc, **extra}


def test_disjoint_months_pass_through_in_order():
    jan = [_row("100"), _row("101")]
    feb = [_row("200")]
    rows, dupes = merge_monthly([jan, feb])
    assert [r["Document Number"] for r in rows] == ["100", "101", "200"]
    assert dupes == 0


def test_window_edge_duplicate_dropped_keeping_first():
    jan = [_row("100", month="jan")]
    feb = [_row("100", month="feb"), _row("200")]
    rows, dupes = merge_monthly([jan, feb])
    assert [r["Document Number"] for r in rows] == ["100", "200"]
    assert rows[0]["month"] == "jan"
    assert dupes == 1


def test_document_number_whitespace_normalized():
    rows, dupes = merge_monthly([[_row("100 ")], [_row(" 100")]])
    assert len(rows) == 1
    assert dupes == 1
