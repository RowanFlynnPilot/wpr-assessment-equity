"""IAAO ratio-study statistics. One responsibility: pure math on (assessed,
price) pairs. No I/O, no config, no network — fully unit-testable.

A "pair" everywhere below is (assessed_value, sale_price) — numbers. Assessed
values may be floats (the pooled analysis normalizes them by municipality
medians); the math is identical.
"""

import math
import random
import statistics
from collections.abc import Callable
from dataclasses import dataclass

Pair = tuple[float, float]

BOOTSTRAP_DRAWS = 1000
BOOTSTRAP_SEED = 20240101   # fixed: the memo and the feed must be reproducible


def bootstrap_ci(
    pairs: list[Pair], stat: Callable[[list[Pair]], float],
    draws: int = BOOTSTRAP_DRAWS, seed: int = BOOTSTRAP_SEED,
) -> tuple[float, float]:
    """Percentile-bootstrap 95% interval for any statistic on pairs — the
    standard way ratio studies state sampling uncertainty (the IAAO Standard
    recommends confidence intervals; CMF's reports bootstrap the same way).
    Deterministic for a given seed. Requires >= 5 pairs."""
    if len(pairs) < 5:
        raise ValueError(f"bootstrap needs >= 5 pairs, got {len(pairs)}")
    rng = random.Random(seed)
    n = len(pairs)
    values = sorted(stat([pairs[rng.randrange(n)] for _ in range(n)]) for _ in range(draws))
    lo = values[int(0.025 * (draws - 1))]
    hi = values[int(0.975 * (draws - 1))]
    return lo, hi


def ratio(assessed: float, price: float) -> float:
    if price <= 0:
        raise ValueError(f"sale price must be positive, got {price}")
    return assessed / price


def iqr_trim(pairs: list[Pair]) -> tuple[list[Pair], int]:
    """IAAO outlier trimming: drop pairs whose ratio lies outside
    [Q1 - 1.5*IQR, Q3 + 1.5*IQR]. Returns (kept, n_trimmed). Tuples may carry
    extra trailing fields (e.g. net tax); only [0]=assessed and [1]=price are
    read, and rows pass through intact."""
    if len(pairs) < 4:
        return pairs, 0
    rs = sorted(ratio(p[0], p[1]) for p in pairs)
    q1, _, q3 = statistics.quantiles(rs, n=4)
    lo, hi = q1 - 1.5 * (q3 - q1), q3 + 1.5 * (q3 - q1)
    kept = [p for p in pairs if lo <= ratio(p[0], p[1]) <= hi]
    return kept, len(pairs) - len(kept)


def median_ratio(pairs: list[Pair]) -> float:
    return statistics.median(ratio(a, p) for a, p in pairs)


def cod(pairs: list[Pair]) -> float:
    """Coefficient of dispersion: 100 * mean|r - median| / median."""
    med = median_ratio(pairs)
    rs = [ratio(a, p) for a, p in pairs]
    return 100.0 * (sum(abs(r - med) for r in rs) / len(rs)) / med


def prd(pairs: list[Pair]) -> float:
    """Price-related differential: mean ratio / sale-weighted mean ratio.
    > 1.03 indicates regressivity (IAAO band 0.98-1.03)."""
    rs = [ratio(a, p) for a, p in pairs]
    weighted = sum(a for a, _ in pairs) / sum(p for _, p in pairs)
    return statistics.fmean(rs) / weighted


@dataclass(frozen=True)
class PRB:
    coefficient: float   # % change in ratio per doubling of value (as fraction)
    std_error: float
    t_stat: float
    n: int

    @property
    def significant(self) -> bool:
        """|t| >= 1.96 — conventional 95% two-tailed threshold."""
        return abs(self.t_stat) >= 1.96


def prb(pairs: list[Pair]) -> PRB:
    """Price-related bias coefficient (IAAO). OLS of
        y_i = (r_i - med) / med
    on
        x_i = log2(0.5 * price_i + 0.5 * assessed_i / med)
    Slope reads as the fractional change in assessment ratio per doubling of
    value. Significantly negative => regressive."""
    if len(pairs) < 5:
        raise ValueError(f"PRB needs >= 5 pairs, got {len(pairs)}")
    med = median_ratio(pairs)
    xs, ys = [], []
    for a, p in pairs:
        value_proxy = 0.5 * p + 0.5 * a / med
        xs.append(math.log2(value_proxy))
        ys.append((ratio(a, p) - med) / med)

    n = len(xs)
    x_bar, y_bar = statistics.fmean(xs), statistics.fmean(ys)
    sxx = sum((x - x_bar) ** 2 for x in xs)
    if sxx == 0:
        raise ValueError("all sale values identical — PRB undefined")
    b = sum((x - x_bar) * (y - y_bar) for x, y in zip(xs, ys)) / sxx
    a0 = y_bar - b * x_bar
    sse = sum((y - (a0 + b * x)) ** 2 for x, y in zip(xs, ys))
    se = math.sqrt((sse / (n - 2)) / sxx)
    return PRB(coefficient=b, std_error=se, t_stat=b / se if se else float("inf"), n=n)


def tax_shift_table(
    price_tax: list[tuple[float, float]], n_deciles: int = 10,
) -> tuple[float, list[dict]]:
    """Dollar tax-shift illustration (the CMF method, medianized): for each
    sale-price decile, the median actual net tax, median effective tax rate
    (tax / price), and the median SHIFT — what the household paid minus what
    the county-average effective rate would charge on its sale price. Positive
    shift = paying more than a flat-rate county would ask. `price_tax` is
    (sale_price, net_tax) with tax > 0. Returns (overall_etr, rows)."""
    if not price_tax:
        return 0.0, []
    overall = sum(t for _, t in price_tax) / sum(p for p, _ in price_tax)
    rows = sorted(price_tax)
    out = []
    for d in range(n_deciles):
        chunk = rows[d * len(rows) // n_deciles:(d + 1) * len(rows) // n_deciles]
        if not chunk:
            continue
        out.append({
            "decile": d + 1,
            "n": len(chunk),
            "median_price": statistics.median(p for p, _ in chunk),
            "median_tax": statistics.median(t for _, t in chunk),
            "median_etr": statistics.median(t / p for p, t in chunk),
            "median_shift": statistics.median(t - overall * p for p, t in chunk),
        })
    return overall, out


def decile_table(
    pairs: list[Pair], norm: dict[str, float], munis: list[str],
    n_deciles: int = 10,
) -> list[dict]:
    """Median NORMALIZED ratio by sale-price decile. Each pair's ratio is divided
    by its municipality's median ratio (`norm`), so pooled deciles compare equity,
    not revaluation timing. `munis` aligns 1:1 with `pairs`."""
    rows = sorted(
        (p, ratio(a, p) / norm[m]) for (a, p), m in zip(pairs, munis)
    )
    out = []
    for d in range(n_deciles):
        chunk = rows[d * len(rows) // n_deciles:(d + 1) * len(rows) // n_deciles]
        if not chunk:
            continue
        out.append({
            "decile": d + 1,
            "n": len(chunk),
            "price_min": chunk[0][0],
            "price_max": chunk[-1][0],
            "median_price": statistics.median(p for p, _ in chunk),
            "median_norm_ratio": statistics.median(r for _, r in chunk),
        })
    return out
