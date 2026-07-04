"""Known-value tests for the IAAO statistics. Pure functions, no I/O."""

import math

import pytest

from analysis import ratios


def test_median_ratio():
    pairs = [(90, 100), (100, 100), (110, 100)]
    assert ratios.median_ratio(pairs) == 1.0


def test_ratio_rejects_zero_price():
    with pytest.raises(ValueError):
        ratios.ratio(100, 0)


def test_cod_hand_computed():
    # ratios 0.8, 1.0, 1.2 -> median 1.0, mean|dev| = 0.4/3, COD = 13.333
    pairs = [(80, 100), (100, 100), (120, 100)]
    assert math.isclose(ratios.cod(pairs), 100 * (0.4 / 3), rel_tol=1e-9)


def test_prd_neutral_when_uniform():
    pairs = [(50, 100), (500, 1000), (5000, 10000)]
    assert math.isclose(ratios.prd(pairs), 1.0, rel_tol=1e-9)


def test_prd_flags_regressive():
    # cheap home over-assessed (1.2), expensive under-assessed (0.8)
    pairs = [(120_000, 100_000), (400_000, 500_000)]
    assert ratios.prd(pairs) > 1.03


def test_prb_negative_for_regressive_pattern():
    # ratio falls smoothly as price rises across two orders of magnitude
    pairs = [(int(p * (1.3 - 0.05 * i)), p)
             for i, p in enumerate([50, 75, 100, 150, 220, 330, 500, 750][:8])]
    pairs = [(a * 1000, p * 1000) for a, p in pairs]
    result = ratios.prb(pairs)
    assert result.coefficient < 0
    assert result.n == 8


def test_prb_near_zero_when_equitable():
    pairs = [(int(p * 0.95), p) for p in
             [80_000, 120_000, 160_000, 240_000, 350_000, 500_000]]
    result = ratios.prb(pairs)
    assert abs(result.coefficient) < 1e-9


def test_iqr_trim_drops_extreme_ratio():
    pairs = [(95, 100)] * 10 + [(1000, 100)]  # one 10.0 ratio among 0.95s
    kept, n = ratios.iqr_trim(pairs)
    assert n == 1
    assert all(a == 95 for a, _ in kept)


def test_iqr_trim_small_sample_untouched():
    pairs = [(95, 100), (1000, 100)]
    kept, n = ratios.iqr_trim(pairs)
    assert n == 0 and len(kept) == 2


def test_decile_table_normalization():
    # Two munis at different assessment LEVELS but identical equity: normalized
    # deciles must be flat at 1.0 — the whole point of the normalization rule.
    pairs, munis = [], []
    for i in range(20):
        price = 100_000 + i * 20_000
        pairs.append((int(price * 0.9), price)); munis.append("A")
        pairs.append((int(price * 0.5), price)); munis.append("B")
    norm = {"A": 0.9, "B": 0.5}
    table = ratios.decile_table(pairs, norm, munis, n_deciles=4)
    assert len(table) == 4
    for row in table:
        assert math.isclose(row["median_norm_ratio"], 1.0, rel_tol=1e-6)
