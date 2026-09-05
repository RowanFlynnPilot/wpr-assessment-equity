# CLAUDE.md — wpr-assessment-equity

Project context and working agreement for Claude Code. Read this first.

## What this is

A Wausau Pilot & Review (WPR) **sales ratio study**: are cheaper homes in Marathon
County assessed at a higher fraction of their market value than expensive ones?
This is the standard vertical-equity method (IAAO ratio study statistics; the same
family of analysis behind the Chicago/Detroit/Philadelphia regressivity findings
and the UChicago Center for Municipal Finance national study).

**Analysis-first.** The primary deliverable is `output/findings-<year>.md` — a
findings memo for the editor. `frontend/` presents the same findings as a
WPR-branded widget (see Decisions log); it reads ONLY the aggregate feed files
the pipeline writes to `output/` — `index.json` (years present, latest),
`findings-<year>.json` (per study year), and the optional
`crosscheck-<year>.json` (DOR's published level per municipality) — and
deploys to GitHub Pages on push (`.github/workflows/deploy.yml`). With two or
more years in the index the widget offers a year switch and a
"what changed" comparison.

## Publishing workflow (the standard process)

Nothing goes live without a human push — the pipeline never publishes on its
own. When a study run produces new findings:

1. **Notify.** Whoever ran the study (usually a working session in this repo)
   surfaces the regenerated `output/findings-<year>.md`, `findings-<year>.json`,
   `index.json` and (after `python -m analysis.crosscheck`)
   `crosscheck-<year>.json` to Rowan with the headline numbers. Nothing is
   committed yet.
2. **Review & update.** Rowan reads the memo. When satisfied, commit and push
   those output files (plus any config change). That push IS the sign-off.
3. **Live shortly.** The push triggers `deploy.yml` (it watches
   `output/*.json` and `frontend/**`), which rebuilds the widget and
   republishes Pages in ~2 minutes at
   https://rowanflynnpilot.github.io/wpr-assessment-equity/ — the WordPress
   iframe (once embedded) picks it up with no WordPress change.

First-deploy note: if the initial Actions run fails with a Pages-not-enabled
error, set Settings → Pages → Source = "GitHub Actions" once and re-run.

## Decisions log

- **Study window: calendar-2025 sales × 2025 assessment roll.** Confirmed by Rowan
  2026-07-04. The purpose of the 2025 run is to validate the method so the 2026
  study runs on rails.
- **Analysis first, widget maybe.** Confirmed by Rowan 2026-07-04.
- **Findings widget greenlit.** Rowan 2026-07-04 (same day, after the 2024
  findings landed): build `frontend/` in the WPR brand system (Oswald /
  Merriweather / typewriter roundel, matching wausaupilotandreview.com and the
  restyled transactions widget). The widget consumes `output/findings.json`
  (aggregate-only).
- **Publication approved.** Rowan 2026-07-04: GitHub Pages deploy via
  `.github/workflows/deploy.yml` (same pattern as the transactions widget).
  The standard update process is documented below ("Publishing workflow").
  Whether/where the widget is embedded on wausaupilotandreview.com remains
  Rowan's manual step.
- **This repo reuses the RETR scraper from `wpr-property-transactions`** (sibling
  checkout) for browser automation only. It does NOT fork the Playwright logic.
- **2025 study run (V12 live).** 2026-09-05: the parcel service was renamed
  with the V12 release (see Assessments below); after the config fix the 2025
  study ran with the vintage gate at 100%. Its outputs await Rowan's review
  per the Publishing workflow — the widget keeps 2024 live until that push.

## The two sources (and why)

### Sales: Wisconsin DOR RETR, via the sibling repo's `scraper.tap`

`wpr-property-transactions` already owns the one correct path into the DOR TAP
(GenTax) RETR Advanced Search. This repo imports `tap.download_report(county,
date_from, date_to, dest_dir)` from a **sibling checkout** at
`../wpr-property-transactions` and runs it as **twelve monthly windows per
study year, merged on Document Number** (see Backfill below). TAP caps any
single search at 1,000 returns and the truncation is NOT date-ordered — a
full-year pull (2026-07-04) returned exactly 1,000 rows spread across all 12
months, passing a naive window-edge check. Quarterly windows are also over the
cap (~1,250 rows/quarter at Marathon's ~5,000 recorded conveyances a year).

We parse the raw 78-column CSV **ourselves** (`analysis/retr.py`), not through the
sibling's `parse.py`, because the study needs columns the transactions feed
deliberately discards: `Grantor/Grantee Relationship`, `Fee Exemption`,
`Part of Parcel Transferred`, `Primary Residence of Grantee?`, `Acres`.
The boundary: sibling repo = browser flow; this repo = everything after the CSV.

### Assessments: Wisconsin Statewide Parcel Map REST endpoint

`https://services3.arcgis.com/n6uYoouQZW75n5WI/arcgis/rest/services/Wisconsin_Statewide_Parcels_DB/FeatureServer/0`

(Renamed with the V12 release — layer 0 is `V1200_WisconsinParcels_2026`,
carrying the 2025 tax roll. The pre-V12 path `Wisconsin_Statewide_Parcels`
now answers "Invalid URL" to every query. If the fetch ever fails that way
again, list the org's services directory — `.../rest/services?f=json` — and
look for the parcel service's new name; the 47-field schema has been stable
across releases.)

Attribute-only paginated queries (`returnGeometry=false`, 2000/page), filtered by
`CONAME`. Carries per-parcel `CNTASSDVALUE` / `LNDVALUE` / `IMPVALUE` (local
assessor values), `PROPCLASS`, `PLACENAME` (municipality), `TAXROLLYEAR`,
`ASSDACRES`, and `NETPRPTA` (actual net property tax — used for the tax-shift
illustration). Chosen over county GIS exports and file-geodatabase downloads
because it is statewide-consistent (add-a-county = config change), attribute-only
(no GIS stack), and scriptable. There are **no fallback sources**.

## The two traps (encoded as rules, not prose)

1. **Wisconsin assesses at the MUNICIPAL level and levels drift between
   revaluations** (state law only requires each major class within 10% of full
   value once every five years). Raw ratios are therefore NOT comparable across
   municipalities — a naive cross-muni comparison measures revaluation timing,
   not equity. Rule: vertical-equity statistics are computed (a) within a single
   municipality where n >= MUNI_MIN_N, and (b) county-pooled only on
   **municipality-median-normalized** ratios (each sale's ratio divided by its
   municipality's median ratio).

2. **Vintage matching.** Ratios pair a sale with the assessment for the SAME
   assessment year. The statewide parcel release lags: V11 (published 2025)
   carries the 2024 tax roll; V12 (2025 roll) was scheduled for 2026-06-30.
   Rule: `analysis/parcels.py` asserts that >= VINTAGE_MIN_SHARE of fetched
   residential parcels have `TAXROLLYEAR == STUDY_YEAR` and **fails loudly**
   otherwise. Until the endpoint serves V12, the production run correctly
   refuses to run. Do not add a bypass flag.

## Join contract (spike-validated 2026-07-04)

- RETR `Parcel Number` for Marathon: `NNN-NNNN-NNN-NNNN` (14 digits + dashes).
- Parcel layer `PARCELID`: same 14 digits, bare.
- Normalization: strip all non-digit characters, compare as strings.
- Spike result on June-2025 RETR (488 rows; 199 study-population sales) against
  the live endpoint (82,881 Marathon parcels, V11): **join rate 99.0%**. The two
  misses were genuine absences (parcels created after V11 collection), not format
  failures. `JOIN_RATE_MIN = 0.95` is asserted in the pipeline.

## Filter waterfall (ordered; every exclusion is counted and reported)

1. `Conveyance Type == "Sale"`
2. `Grantor/Grantee Relationship == "No relationship"` (arm's-length; same field
   DOR uses to cull its own equalization ratio studies)
3. `Fee Exemption` empty (exempt conveyances are presumptively non-market)
4. `Part of Parcel Transferred` starts with `"1."` (entire parcel only)
5. `Property Use Type` starts with `"Single family"` (v1 scope; Multi-family etc.
   are future work)
6. `Sale Price >= MIN_SALE_PRICE` (10,000 — a ratio-study floor, deliberately
   higher than the transactions column's $1,000 editorial floor)
7. Parcel joins to index (join rate asserted >= JOIN_RATE_MIN)
8. Parcel `PROPCLASS == "1"` exactly (pure residential; mixed like `"1,4"` are
   excluded — a comma-list class means part of the assessment is use-value ag,
   which corrupts the ratio)
9. Acreage sanity: if both sides carry acres AND the conveyed acreage exceeds
   `ACRE_FLOOR` (2.0), RETR conveyed acres must not grossly exceed the matched
   parcel's `ASSDACRES` (multi-parcel conveyances appear in the CSV as ONE row
   with one parcel number — verified in spike: zero duplicated document numbers
   in a full month — so a big acreage mismatch is the fingerprint of a
   multi-parcel sale priced against one parcel's assessment). The floor exists
   because of a June-2025 evidence finding: preparers enter "1" as a default
   acreage on small city lots — 34 of 35 initially-flagged cases were
   `retr=1.00` vs 0.1–0.3-acre lots (entry noise); the single genuine case was
   65 conveyed acres against a 5-acre parcel. Without the floor this filter
   silently ate 20% of the sample, biased toward city lots.
10. IAAO IQR trimming of extreme ratios, applied within each analysis group

## Statistics (`analysis/ratios.py`, stdlib only — no pandas/numpy)

For ratios r_i = assessed / sale price:

- **Median ratio** — level of assessment
- **COD** = 100 × mean(|r_i − median|) / median — uniformity; IAAO standard for
  single-family residential is <= 15 (<= 10 in homogeneous new areas)
- **PRD** = mean(r) / (Σ assessed / Σ price) — acceptable band 0.98–1.03;
  above 1.03 indicates regressivity
- **PRB** — OLS slope of (r_i − med)/med on log2(0.5·SP_i + 0.5·AV_i/med),
  with SE and t; acceptable band −0.05 to +0.05; significantly negative
  indicates regressivity (assessments fall ~|PRB|% per doubling of value)
- **Decile table** — median normalized ratio by sale-price decile (the money chart)

These four are the defensible, assessor-recognized standard. Report all of them;
do not invent bespoke statistics.

Reported alongside them (all standard practice, none bespoke):

- **95% confidence intervals** — percentile bootstrap, 1,000 resamples, fixed
  seed (`ratios.bootstrap_ci`), on COD and PRD (county and per municipality)
  and on the bottom-decile normalized ratio. The IAAO Standard recommends
  stating sampling uncertainty; CMF's reports bootstrap the same way.
- **Uniformity flag** — `uniformity_ok = COD <= IAAO_COD_MAX_SFR`, carried
  beside (never folded into) the equity verdict, so a loose roll is visible
  even when the price tilt is inside the bands.
- **Effective tax rate** — median `NETPRPTA / sale price` per municipality and
  per decile (the dollar tax-shift illustration).
- **DOR cross-check** — `python -m analysis.crosscheck` compares our
  municipality medians with DOR's Summary of Aggregate Ratios, flags residuals
  from the shared drift, and writes `output/crosscheck-<year>.json`.

## Privacy & editorial policy

- The raw RETR CSV (names, addresses, parcel numbers) lives in `raw/` which is
  **gitignored and never committed**, same posture as the transactions repo.
- Everything this repo *outputs* is **aggregate-only**: statistics by
  municipality and price decile. No addresses, names, or parcel numbers appear
  in `output/`.
- Whether the eventual *story* names illustrative properties is an editorial
  decision for the editor, not this pipeline. `docs/editorial-memo-draft.md` is
  the pending memo covering the new use of raw RETR data. Do not build any
  per-property output before that sign-off.

## Engineering principles

Same as every WPR repo: don't overengineer; one correct path, no fallbacks; one
way to do things; throw errors — fail fast when preconditions aren't met; no
backups — trust the primary mechanism; separation of concerns — one
responsibility per module; surgical changes only; evidence-based debugging;
fix root causes.

Concretely here: stdlib only (csv, json, urllib, statistics, math). The only
third-party dependency (Playwright) belongs to the sibling repo and is used
only during backfill.

## Dev environment

- Windows / PowerShell 5.1: separate commands with `;` — never `&&`.
- Python 3.14 at `C:\Users\rpfly\Projects\`. Sibling checkout expected at
  `C:\Users\rpfly\Projects\wpr-property-transactions`.
- Backfill (once per study year, ~30 min, needs Playwright from the sibling):
  `python -m analysis.retr` — twelve monthly STUDY_YEAR windows merged on
  Document Number; asserts every monthly pull is non-empty AND below
  TAP_RESULT_CAP (if a month ever reaches the cap, the window must shrink —
  a design change, not a retry).
- Parcel fetch (idempotent, ~42 REST pages): `python -m analysis.parcels`
- Study: `python -m analysis.study` → `output/findings-<year>.md` (editor memo)
  + `output/findings-<year>.json` (widget feed; both rendered from one computed
  dict) + `output/index.json` (rebuilt from the feed files present)
- Cross-check (network; after the study): `python -m analysis.crosscheck` →
  prints the DOR comparison and writes `output/crosscheck-<year>.json`
- Tests: `python -m pytest tests/ -q` (pure-function tests; no network)
- Widget: `cd frontend ; npm install ; npm run dev` (Vite serves at
  `/wpr-assessment-equity/`; `vite.config.js` publicDir points at `output/` so
  the feed is served without a copy step). `npm run build` → `frontend/dist/`
  (gitignored; no deploy workflow — publishing is an editorial decision).
