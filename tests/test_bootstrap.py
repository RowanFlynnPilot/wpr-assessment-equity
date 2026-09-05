"""bootstrap_ci: deterministic percentile intervals that bracket the truth."""

import random

import pytest

from analysis import ratios


def _sample(n=300, seed=7):
    # Ratios ~ 0.9 with modest spread, prices spread across 50k-500k.
    rng = random.Random(seed)
    out = []
    for _ in range(n):
        price = rng.uniform(50_000, 500_000)
        out.append((price * rng.gauss(0.9, 0.08), price))
    return out


def test_deterministic_for_fixed_seed():
    pairs = _sample()
    a = ratios.bootstrap_ci(pairs, ratios.cod, draws=200)
    b = ratios.bootstrap_ci(pairs, ratios.cod, draws=200)
    assert a == b


def test_interval_brackets_point_estimate_and_is_ordered():
    pairs = _sample()
    lo, hi = ratios.bootstrap_ci(pairs, ratios.median_ratio, draws=300)
    assert lo < hi
    assert lo <= ratios.median_ratio(pairs) <= hi
    # The true median ratio is 0.9 by construction; a 95% CI on n=300 should
    # comfortably contain it.
    assert lo < 0.9 < hi


def test_narrower_with_more_data():
    small = _sample(n=40, seed=3)
    big = _sample(n=800, seed=3)
    lo_s, hi_s = ratios.bootstrap_ci(small, ratios.cod, draws=300)
    lo_b, hi_b = ratios.bootstrap_ci(big, ratios.cod, draws=300)
    assert (hi_b - lo_b) < (hi_s - lo_s)


def test_too_few_pairs_rejected():
    with pytest.raises(ValueError):
        ratios.bootstrap_ci([(90, 100)] * 4, ratios.cod)
