# Assessment equity in Marathon County — 2025 sales ratio study

*Generated 2026-09-05 by `wpr-assessment-equity`. Aggregate statistics only — see CLAUDE.md for methodology and privacy policy.*

## Sample construction

| Filter step | remaining |
|---|---|
| raw RETR rows | 5,227 |
| conveyance is Sale | 2,605 |
| arm's length (no grantor/grantee relationship) | 2,449 |
| no fee exemption claimed | 2,329 |
| entire parcel transferred | 2,270 |
| single family use | 1,907 |
| sale price >= $10,000 | 1,902 |
| recorded in 2025 | 1,902 |
| excluded: no parcel match | −37 |
| excluded: parcel not pure class 1 | −243 |
| excluded: acreage mismatch (multi-parcel fingerprint) | −19 |
| excluded: IQR ratio trimming (within municipality) | −150 |
| **final study sample** | **1,453** |

## Municipality-level statistics (IAAO)

Municipalities with fewer than 30 trimmed sales are pooled but not reported standalone. COD reference for single-family residential: <= 15. PRD band 0.98–1.03. PRB band ±0.05.

| Municipality | n | median ratio | COD (95% CI) | PRD (95% CI) | PRB (t) | eff. tax rate | reading |
|---|---|---|---|---|---|---|---|
| CITY OF WAUSAU | 508 | 0.866 | 12.2 (11.3–13.1) | 1.009 (1.002–1.017) | -0.006 (-0.6) | 1.55% | within IAAO equity bands |
| VILLAGE OF WESTON | 145 | 0.834 | 11.3 (9.8–12.9) | 1.014 (1.006–1.022) | -0.022 (-1.3) | 1.25% | within IAAO equity bands |
| VILLAGE OF RIB MOUNTAIN | 95 | 0.926 | 9.5 (7.9–11.1) | 1.010 (0.998–1.023) | -0.003 (-0.2) | 1.07% | within IAAO equity bands |
| VILLAGE OF KRONENWETTER | 91 | 0.635 | 10.1 (8.3–12.0) | 1.002 (0.993–1.011) | +0.040 (1.5) | 1.04% | within IAAO equity bands |
| VILLAGE OF ROTHSCHILD | 75 | 0.828 | 10.1 (8.3–11.7) | 1.010 (1.001–1.021) | -0.019 (-0.7) | 1.26% | within IAAO equity bands |
| CITY OF MOSINEE | 71 | 0.650 | 17.5 (13.9–20.7) | 1.010 (0.990–1.035) | +0.006 (0.2) | 1.26% | within IAAO equity bands · COD above 15 |
| CITY OF SCHOFIELD | 33 | 0.833 | 12.8 (9.4–15.2) | 1.009 (0.987–1.031) | -0.002 (-0.1) | 1.32% | within IAAO equity bands |
| VILLAGE OF SPENCER | 33 | 0.776 | 13.0 (9.8–16.1) | 1.018 (0.996–1.045) | -0.064 (-1.7) | 1.52% | within IAAO equity bands |

95% CIs are percentile bootstraps (1,000 resamples, fixed seed). Eff. tax rate = median net tax ÷ sale price.

## County pooled (municipality-normalized)

Each sale's ratio is divided by its municipality's median ratio before pooling, so this compares equity, not revaluation timing.

- n = 1,453
- COD = 14.1 (95% CI 13.2–15.1)
- PRD = 1.019 (95% CI 1.011–1.027)
- PRB = -0.013 (SE 0.007, t -1.8)
- **Reading: within IAAO equity bands**

## Median normalized ratio by sale-price decile

| decile | n | price range | median price | median normalized ratio |
|---|---|---|---|---|
| 1 | 145 | $14,000–$125,000 | $85,000 | 1.121 |
| 2 | 145 | $125,000–$160,000 | $145,000 | 1.038 |
| 3 | 145 | $160,000–$190,000 | $175,000 | 1.000 |
| 4 | 146 | $190,000–$217,000 | $201,250 | 0.965 |
| 5 | 145 | $217,000–$241,900 | $230,000 | 0.981 |
| 6 | 145 | $242,000–$275,000 | $256,000 | 0.971 |
| 7 | 146 | $275,000–$315,000 | $292,000 | 1.000 |
| 8 | 145 | $315,000–$357,900 | $334,900 | 0.995 |
| 9 | 145 | $357,900–$439,000 | $382,500 | 1.000 |
| 10 | 146 | $439,900–$1,475,000 | $530,000 | 0.965 |

Bottom-decile homes are assessed at a ratio **+16.2%** relative to top-decile homes. Bottom-decile median normalized ratio 1.121 (95% CI 1.067–1.225).

## Property-tax dollars (tax-shift illustration)

Actual net property tax (parcel `NETPRPTA`) on 1,453 of the study sales. "Shift" is what the household paid minus what the county-average effective rate (1.25% of sale price) would charge — positive means paying more than a flat-rate county would ask.

| decile | n | median price | median net tax | median eff. rate | median shift |
|---|---|---|---|---|---|
| 1 | 145 | $85,000 | $1,226 | 1.47% | +$108 |
| 2 | 145 | $145,000 | $2,089 | 1.47% | +$320 |
| 3 | 145 | $175,000 | $2,426 | 1.37% | +$206 |
| 4 | 146 | $201,250 | $2,639 | 1.30% | +$99 |
| 5 | 145 | $230,000 | $2,903 | 1.28% | +$61 |
| 6 | 145 | $256,000 | $3,122 | 1.20% | −$118 |
| 7 | 146 | $292,000 | $3,695 | 1.25% | −$4 |
| 8 | 145 | $334,900 | $3,784 | 1.13% | −$401 |
| 9 | 145 | $382,500 | $4,724 | 1.24% | −$51 |
| 10 | 146 | $530,000 | $6,230 | 1.14% | −$694 |

## Caveats

- Single-family, arm's-length, entire-parcel, fee-paying sales >= $10,000 only; 2025 sales against the 2025 assessment roll.
- Small municipalities appear only in the pooled analysis.
- The tax-shift table is an illustration, not a simulation: NETPRPTA is net of credits, and it holds levies fixed (a re-assessment would also shift rates). Sales with no reported net tax are excluded from it. Its gradient blends assessment inequity WITH municipal rate geography — lower-priced homes concentrating in higher-rate municipalities also steepens it.
- Independent context: the UChicago Center for Municipal Finance's own Marathon County study (First American sales, 2014–2023) found 67% of the lowest-value homes over-assessed vs 45% of the highest-value homes — same direction as this study, different data and method (county-median normalization). Wisconsin Policy Forum (2023) documents the statewide revaluation-staleness backdrop. See docs/data-sources.md.
- This memo is an internal finding, not a publication. Editorial decisions (including whether any illustrative property is ever named) rest with the editor per docs/editorial-memo-draft.md.