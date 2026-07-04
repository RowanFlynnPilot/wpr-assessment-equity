"""tax_shift_table: per-decile dollar shift vs the county-average effective
rate; iqr_trim passes extra tuple fields through intact."""

import pytest

from analysis.ratios import iqr_trim, tax_shift_table


def test_shift_is_zero_when_rates_are_flat():
    # Every home taxed at exactly 2% of price -> overall ETR 2%, zero shift.
    pt = [(price, price * 0.02) for price in (50_000, 100_000, 200_000, 400_000)]
    overall, rows = tax_shift_table(pt, n_deciles=2)
    assert overall == pytest.approx(0.02)
    for r in rows:
        assert r["median_shift"] == pytest.approx(0.0)
        assert r["median_etr"] == pytest.approx(0.02)


def test_regressive_taxes_shift_dollars_to_cheap_homes():
    # Cheap homes taxed at 3%, expensive at 1%: cheap deciles pay MORE than the
    # county-average rate would charge, expensive pay less.
    cheap = [(50_000, 1_500), (60_000, 1_800)]      # 3%
    dear = [(400_000, 4_000), (500_000, 5_000)]     # 1%
    overall, rows = tax_shift_table(cheap + dear, n_deciles=2)
    assert overall == pytest.approx(12_300 / 1_010_000)
    assert rows[0]["median_shift"] > 0
    assert rows[1]["median_shift"] < 0


def test_empty_input():
    overall, rows = tax_shift_table([])
    assert overall == 0.0
    assert rows == []


def test_iqr_trim_passes_triples_through():
    # 20 normal ratios + 1 wild outlier; the outlier's whole triple is dropped
    # and survivors keep their trailing tax field.
    recs = [(100_000 + i, 100_000, 1_500.0 + i) for i in range(20)]
    recs.append((900_000, 100_000, 9_999.0))  # ratio 9.0 — trimmed
    kept, n_trim = iqr_trim(recs)
    assert n_trim == 1
    assert all(len(r) == 3 for r in kept)
    assert (900_000, 100_000, 9_999.0) not in kept
