# wpr-assessment-equity

Sales ratio study for **Marathon County, WI**: are cheaper homes assessed at a
higher fraction of market value than expensive ones? IAAO-standard vertical
equity statistics (median ratio, COD, PRD, PRB) on arm's-length single-family
sales, published by Wausau Pilot & Review as an internal findings memo first.

**Sources:** Wisconsin DOR RETR sales (via the sibling
[`wpr-property-transactions`](../wpr-property-transactions) scraper) × Wisconsin
Statewide Parcel Map assessed values (REST endpoint). Join key: normalized
14-digit parcel ID — spike-validated at 99.0%.

See **CLAUDE.md** for the full working agreement: methodology rules (municipal
normalization, vintage gate), the filter waterfall, join contract, privacy
policy, and engineering principles.

## Quick start (PowerShell)

```powershell
# one-time: sibling checkout provides the browser automation
cd C:\Users\rpfly\Projects ; git clone https://github.com/RowanFlynnPilot/wpr-property-transactions.git

cd C:\Users\rpfly\Projects\wpr-assessment-equity

# 1. backfill the study year's raw RETR CSV (Playwright, ~minutes)
python -m analysis.retr

# 2. fetch the county parcel index (~83k rows, ~42 REST pages)
python -m analysis.parcels

# 3. run the study -> output/findings-2025.md
#    (fails loudly until the endpoint serves the 2025 roll — see CLAUDE.md)
python -m analysis.study

# tests
python -m pytest tests\ -q
```

## Status

Pipeline complete and spike-validated (2026-07-04). **Blocked, correctly, on the
V12 statewide parcel release** (2025 tax roll; scheduled 2026-06-30): the
vintage gate in `analysis/parcels.py` refuses to compute ratios against the
2024 roll. Editorial memo (`docs/editorial-memo-draft.md`) pending sign-off.
