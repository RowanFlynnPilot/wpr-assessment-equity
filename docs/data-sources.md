# Additional data sources for the assessment-equity study

Researched 2026-07-04 (web sweep + direct link verification). Every URL below
returned 200 on 2026-07-04 unless noted. Candidates are ordered by how much
they strengthen the study.

## Tier 1 — official cross-checks (add these)

### DOR Major Class Comparison (MCC), Marathon County
- **URL (verified):** https://www.revenue.wi.gov/SLFReportsassessor/MCCMARATHONF.PDF
- **What:** per-municipality, per-class (Residential/Commercial/Ag/other)
  assessed value vs DOR base (equalized) value with the ratio %, compliance
  status, and notice type — **seven year-rows, 2019–2025**, in one PDF.
- **Cadence:** annual Final edition (2025 Final published; note: munis that
  missed the 2025-10-06 filing deadline show no 2025 data).
- **Enables:** the single best independent cross-check of our per-muni median
  ratios, same vintage (2024 row for the 2024 study; 2025 row when V12 lands).
  Our Wausau 0.932 / Rib Mountain 0.618 medians should sit near MCC's
  Residential ratios; a big gap = investigate before publishing. Also gives
  ratios for small munis we pool but can't report standalone.

### DOR Summary of Aggregate Ratios
- **URLs (verified):**
  https://www.revenue.wi.gov/SLFReportscotvc/2024sumagg.xlsx ·
  https://www.revenue.wi.gov/SLFReportscotvc/2025sumagg.xlsx (PDF variants same
  dir, `<year>sumagg.PDF`)
- **What:** per-municipality total locally-assessed ÷ DOR base value, machine-
  readable, statewide.
- **Enables:** scriptable version of the MCC level check (aggregate, not
  class-split); trivially joinable by municipality name.

### DOR Town/Village/City (TVC) taxes
- **URLs (verified):** https://www.revenue.wi.gov/SLFReportscotvc/tvc24.xlsx ·
  https://www.revenue.wi.gov/SLFReportscotvc/tvc25.xlsx (series back to ~2001;
  published each June for the prior tax year)
- **What:** per-municipality levies, full-value gross/effective tax rates,
  % assessment level, and the levy decomposed school / tech college / county /
  local / TIF.
- **Enables:** the DOLLAR tax-shift translation at municipal level, and levy
  context for the widget. Caveat (DOR's own): rates are averages across
  overlapping districts — where a muni spans multiple school districts they
  are "not strictly comparable". For parcel-level dollars we already carry
  NETPRPTA, which is better.

### UChicago CMF report for Marathon County (independent comparator)
- **URL (verified):** https://s3.us-east-2.amazonaws.com/propertytaxdata.uchicago.edu/nationwide_reports/web/Marathon%20County_Wisconsin.html
  ("An Evaluation of Property Tax Regressivity in Marathon County, Wisconsin")
- **What:** the Center for Municipal Finance's own sales-ratio study of
  Marathon County — residential sales **2014–2023**, First American
  vendor-classified arm's-length sales (fully independent of RETR), same IAAO
  statistics with bootstrapped CIs.
- **Headline (from the report):** 67% of the lowest-value homes are
  over-assessed vs 45% of the highest-value homes; in 2023 the average
  bottom-decile home sold for $56,874.
- **Enables:** an independent-data, independent-team directional confirmation
  of our bottom-decile finding. **Flags:** vintage ends 2023 (never present as
  validation of our 2024/2025 numbers); CMF normalizes to the COUNTY median
  (we normalize to municipality medians — ours is the right design for
  Wisconsin's municipal assessment system, so expect level differences);
  headline metric is their regressivity index, not PRD/PRB.

## Tier 2 — enrichment and context

- **Municipal Assessment Report (MAR)** — per-muni, per-year assessment TYPE
  (full revaluation / interim market update / maintenance), the assessor's own
  estimated level of assessment, and Open Book / Board of Review dates.
  Explicitly non-confidential; e-filed to DOR annually (instructions:
  https://www.revenue.wi.gov/DORForms/mar-inst.pdf). A reval-year overlay is
  the right explainer for why median ratios differ so much across munis
  (e.g. Rib Mountain 0.618). Access: DOR reports portal / records request.
- **Statement of Assessment (SOA)** — per-muni class-level aggregates
  (parcel counts, acres, values), post-Board-of-Review; 2025 line summaries
  published 2026-05-28. Class-level totals only; cannot reproduce ratio stats.
- **cmfproperty R package** (https://cmf-uchicago.github.io/cmfproperty/) —
  CMF's open-source reference implementation of COD/PRD/PRB; takes just
  (sale year, price, assessed value). Optional credibility move: run it on our
  joined pairs and confirm our stdlib stats match the reference implementation.
- **Wisconsin Policy Forum** — citable context:
  2023 "Locally Assessed Property Values Fail to Keep Up with the Market"
  (42.5% of munis below an 80% ratio in 2022; only 39% did a full reval
  2011–2022) and April 2026 "Value Judgment" (Milwaukee County assessment
  practices). Both support the revaluation-staleness framing.
- **DOR equalization methodology** (https://www.revenue.wi.gov/DOR%20Publications/wieqval.pdf)
  — DOR runs its own RETR-based ratio studies (~240k sales/yr) and formally
  adopts the same IAAO bands we use (PRD 0.98–1.03, PRB ±0.05). Citable as
  "the state uses this same method".

## Appeals / Board of Review (story leads, not ratio data)

No central dataset exists. BOR records (PA-800 summaries, PR-302
determinations, objections PA-115A) are held by each **municipal clerk**,
retained ≥7 years, open to public inspection — per-muni records requests.
One central slice: sec. 70.85 appeals (properties ≤ $1M outside Milwaukee)
go to the DOR Equalization Supervisor — a records request to DOR could yield
a countywide appeal sample. DOR publishes an Open Book / BOR date calendar
per municipality (widget-friendly "how to appeal" context).

## Methodological flags (do NOT do these)

1. **Never use equalized values as the assessment side of a ratio.** They are
   municipality-level DOR estimates, not parcel assessments; against sales
   they measure DOR's level estimate, not assessor equity.
2. **Vintage offset in DOR's own ratios:** DOR's January-1-YEAR equalized
   value is derived from PRIOR-year sales. When cross-checking, match the MCC
   year-row to our study year, not to the equalization certification date.
3. **CMF numbers are 2014–2023 and county-median-normalized** — directional
   corroboration only.
4. **Known filter gap vs DOR practice:** DOR rejects sales where improvements
   changed between assessment date and sale (their reject code 75; adjudicated
   in their PAD system). RETR carries no such field, so our sample includes
   remodel-between-dates sales. List as a limitation; a records request for
   DOR's usable/reject determinations on Marathon 2024 sales could close it.

## Suggested build order

1. `analysis/crosscheck.py`: pull 2024/2025 sumagg.xlsx + parse MCC Residential
   rows → report our muni medians vs DOR's ratios side by side (assert
   within a tolerance, warn otherwise). Pure enrichment of the memo.
2. Dollar tax-shift section in the study: per-decile effective-tax-rate method
   (CMF's approach) using NETPRPTA we already fetch — produces "bottom-decile
   homes overpay ≈ $X/year" for memo + widget.
3. Reval-type overlay: MCC compliance status (already in the PDF) + MAR
   assessment types → a "last revalued" column in the muni table.
4. Memo caveats: cite CMF Marathon report + WPF 2023 as independent context.
