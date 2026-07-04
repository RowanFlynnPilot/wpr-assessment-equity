# Assessment equity in Marathon County — 2024 sales ratio study

*Generated 2026-07-04 by `wpr-assessment-equity`. Aggregate statistics only — see CLAUDE.md for methodology and privacy policy.*

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

| Municipality | n | median ratio | COD | PRD | PRB (t) | reading |
|---|---|---|---|---|---|---|
| CITY OF WAUSAU | 504 | 0.932 | 11.0 | 1.000 | +0.002 (0.3) | within IAAO equity bands |
| VILLAGE OF WESTON | 153 | 0.889 | 9.8 | 1.005 | +0.023 (1.2) | within IAAO equity bands |
| VILLAGE OF RIB MOUNTAIN | 93 | 0.618 | 13.9 | 1.020 | -0.030 (-1.3) | within IAAO equity bands |
| VILLAGE OF KRONENWETTER | 82 | 0.682 | 11.6 | 1.010 | -0.009 (-0.3) | within IAAO equity bands |
| VILLAGE OF ROTHSCHILD | 80 | 0.885 | 11.4 | 1.012 | +0.023 (0.8) | within IAAO equity bands |
| CITY OF MOSINEE | 50 | 0.703 | 16.0 | 1.032 | -0.048 (-1.1) | REGRESSIVE — lower-priced homes carry proportionally higher assessments |
| VILLAGE OF SPENCER | 37 | 0.762 | 9.7 | 1.009 | +0.006 (0.2) | within IAAO equity bands |
| CITY OF SCHOFIELD | 30 | 0.889 | 12.0 | 0.984 | +0.056 (1.8) | within IAAO equity bands |

## County pooled (municipality-normalized)

Each sale's ratio is divided by its municipality's median ratio before pooling, so this compares equity, not revaluation timing.

- n = 1,409
- COD = 13.6
- PRD = 1.015
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

Bottom-decile homes are assessed at a ratio **+7.6%** relative to top-decile homes.

## Caveats

- Single-family, arm's-length, entire-parcel, fee-paying sales >= $10,000 only; 2024 sales against the 2024 assessment roll.
- Small municipalities appear only in the pooled analysis.
- This memo is an internal finding, not a publication. Editorial decisions (including whether any illustrative property is ever named) rest with the editor per docs/editorial-memo-draft.md.