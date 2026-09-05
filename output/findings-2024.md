# Assessment equity in Marathon County — 2024 sales ratio study

*Generated 2026-09-05 by `wpr-assessment-equity`. Aggregate statistics only — see CLAUDE.md for methodology and privacy policy.*

## Sample construction

| Filter step | remaining |
|---|---|
| raw RETR rows | 4,959 |
| conveyance is Sale | 2,643 |
| arm's length (no grantor/grantee relationship) | 2,479 |
| no fee exemption claimed | 2,379 |
| entire parcel transferred | 2,291 |
| single family use | 1,891 |
| sale price >= $10,000 | 1,874 |
| recorded in 2024 | 1,874 |
| excluded: no parcel match | −32 |
| excluded: parcel not pure class 1 | −243 |
| excluded: acreage mismatch (multi-parcel fingerprint) | −18 |
| excluded: IQR ratio trimming (within municipality) | −172 |
| **final study sample** | **1,409** |

## Municipality-level statistics (IAAO)

Municipalities with fewer than 30 trimmed sales are pooled but not reported standalone. COD reference for single-family residential: <= 15. PRD band 0.98–1.03. PRB band ±0.05.

| Municipality | n | median ratio | COD (95% CI) | PRD (95% CI) | PRB (t) | eff. tax rate | reading |
|---|---|---|---|---|---|---|---|
| CITY OF WAUSAU | 504 | 0.932 | 11.0 (10.2–11.8) | 1.000 (0.991–1.008) | +0.002 (0.3) | 1.69% | within IAAO equity bands |
| VILLAGE OF WESTON | 153 | 0.889 | 9.8 (8.3–11.1) | 1.005 (0.999–1.012) | +0.023 (1.2) | 1.34% | within IAAO equity bands |
| VILLAGE OF RIB MOUNTAIN | 93 | 0.618 | 13.9 (11.4–16.0) | 1.020 (0.997–1.045) | -0.030 (-1.3) | 1.08% | within IAAO equity bands |
| VILLAGE OF KRONENWETTER | 82 | 0.682 | 11.6 (9.5–13.6) | 1.010 (0.999–1.022) | -0.009 (-0.3) | 1.08% | within IAAO equity bands |
| VILLAGE OF ROTHSCHILD | 80 | 0.885 | 11.4 (9.2–13.4) | 1.012 (0.993–1.034) | +0.023 (0.8) | 1.25% | within IAAO equity bands |
| CITY OF MOSINEE | 50 | 0.703 | 16.0 (12.1–19.4) | 1.032 (1.010–1.055) | -0.048 (-1.1) | 1.30% | REGRESSIVE — lower-priced homes carry proportionally higher assessments · COD above 15 |
| VILLAGE OF SPENCER | 37 | 0.762 | 9.7 (7.0–11.8) | 1.009 (0.994–1.021) | +0.006 (0.2) | 1.38% | within IAAO equity bands |
| CITY OF SCHOFIELD | 30 | 0.889 | 12.0 (9.1–14.7) | 0.984 (0.968–1.002) | +0.056 (1.8) | 1.23% | within IAAO equity bands |

95% CIs are percentile bootstraps (1,000 resamples, fixed seed). Eff. tax rate = median net tax ÷ sale price.

## County pooled (municipality-normalized)

Each sale's ratio is divided by its municipality's median ratio before pooling, so this compares equity, not revaluation timing.

- n = 1,409
- COD = 13.6 (95% CI 12.7–14.5)
- PRD = 1.015 (95% CI 1.006–1.023)
- PRB = -0.011 (SE 0.007, t -1.6)
- **Reading: within IAAO equity bands**

## Median normalized ratio by sale-price decile

| decile | n | price range | median price | median normalized ratio |
|---|---|---|---|---|
| 1 | 140 | $10,000–$110,000 | $70,000 | 1.080 |
| 2 | 141 | $110,000–$150,000 | $131,000 | 1.012 |
| 3 | 141 | $150,000–$177,000 | $164,000 | 0.998 |
| 4 | 141 | $177,500–$205,000 | $190,000 | 0.995 |
| 5 | 141 | $205,000–$234,500 | $220,000 | 0.987 |
| 6 | 141 | $234,900–$262,000 | $248,000 | 0.990 |
| 7 | 141 | $262,500–$299,900 | $276,000 | 0.986 |
| 8 | 141 | $299,900–$340,000 | $315,000 | 1.005 |
| 9 | 141 | $340,000–$425,000 | $375,000 | 1.006 |
| 10 | 141 | $426,000–$1,200,000 | $525,000 | 1.004 |

Bottom-decile homes are assessed at a ratio **+7.6%** relative to top-decile homes. Bottom-decile median normalized ratio 1.080 (95% CI 1.039–1.143).

## Property-tax dollars (tax-shift illustration)

Actual net property tax (parcel `NETPRPTA`) on 1,409 of the study sales. "Shift" is what the household paid minus what the county-average effective rate (1.33% of sale price) would charge — positive means paying more than a flat-rate county would ask.

| decile | n | median price | median net tax | median eff. rate | median shift |
|---|---|---|---|---|---|
| 1 | 140 | $70,000 | $911 | 1.47% | +$47 |
| 2 | 141 | $131,000 | $1,889 | 1.46% | +$148 |
| 3 | 141 | $164,000 | $2,341 | 1.46% | +$203 |
| 4 | 141 | $190,000 | $2,698 | 1.43% | +$195 |
| 5 | 141 | $220,000 | $2,920 | 1.34% | +$23 |
| 6 | 141 | $248,000 | $3,229 | 1.29% | −$115 |
| 7 | 141 | $276,000 | $3,548 | 1.27% | −$191 |
| 8 | 141 | $315,000 | $3,845 | 1.22% | −$359 |
| 9 | 141 | $375,000 | $4,710 | 1.26% | −$287 |
| 10 | 141 | $525,000 | $7,106 | 1.26% | −$323 |

## Caveats

- Single-family, arm's-length, entire-parcel, fee-paying sales >= $10,000 only; 2024 sales against the 2024 assessment roll.
- Small municipalities appear only in the pooled analysis.
- The tax-shift table is an illustration, not a simulation: NETPRPTA is net of credits, and it holds levies fixed (a re-assessment would also shift rates). Sales with no reported net tax are excluded from it. Its gradient blends assessment inequity WITH municipal rate geography — lower-priced homes concentrating in higher-rate municipalities also steepens it.
- Independent context: the UChicago Center for Municipal Finance's own Marathon County study (First American sales, 2014–2023) found 67% of the lowest-value homes over-assessed vs 45% of the highest-value homes — same direction as this study, different data and method (county-median normalization). Wisconsin Policy Forum (2023) documents the statewide revaluation-staleness backdrop. See docs/data-sources.md.
- This memo is an internal finding, not a publication. Editorial decisions (including whether any illustrative property is ever named) rest with the editor per docs/editorial-memo-draft.md.