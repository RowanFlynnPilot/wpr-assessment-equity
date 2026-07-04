"""Orchestration. One responsibility: run the study and write the findings.

    python -m analysis.study      -> output/findings-<year>.md  (editor memo)
                                     output/findings.json       (widget feed)

Both artifacts are rendered from ONE computed findings dict, so they can never
disagree. Everything written here is AGGREGATE-ONLY: statistics by municipality
and price decile. No names, addresses, or parcel numbers.
"""

import json
import statistics
from collections import defaultdict
from datetime import date

from . import config, parcels, ratios
from .join import join
from .retr import load_study_population


def _records_by_muni(matches) -> dict[str, list[tuple[int, int, float]]]:
    """(assessed, price, net_tax) per municipality. net_tax = NETPRPTA (actual
    net property tax on the parcel), 0.0 when the layer carries none."""
    by_muni: dict[str, list[tuple[int, int, float]]] = defaultdict(list)
    for m in matches:
        assessed = int(float(m.parcel["CNTASSDVALUE"]))
        raw_tax = (m.parcel.get("NETPRPTA") or "").strip()
        try:
            tax = float(raw_tax)
        except ValueError:
            tax = 0.0
        by_muni[m.parcel["PLACENAME"].strip()].append((assessed, m.sale["_price"], tax))
    return by_muni


def _verdict(prd_v: float, prb_v: ratios.PRB) -> str:
    lo, hi = config.IAAO_PRD_BAND
    regressive = prd_v > hi or (prb_v.coefficient < config.IAAO_PRB_BAND[0]
                                and prb_v.significant)
    progressive = prd_v < lo or (prb_v.coefficient > config.IAAO_PRB_BAND[1]
                                 and prb_v.significant)
    if regressive:
        return "REGRESSIVE — lower-priced homes carry proportionally higher assessments"
    if progressive:
        return "PROGRESSIVE — higher-priced homes carry proportionally higher assessments"
    return "within IAAO equity bands"


def compute() -> dict:
    """Run the pipeline and return the findings as one aggregate-only dict —
    the single source both renderers read."""
    sales, waterfall = load_study_population(config.RETR_RAW_CSV)
    index = parcels.load()
    matches, join_excl = join(sales, index)

    by_muni = _records_by_muni(matches)

    # Per-municipality trimming + medians (the normalization denominators).
    # trimmed holds (assessed, price, tax) triples; stats read (assessed, price).
    trimmed: dict[str, list[tuple[int, int, float]]] = {}
    n_trimmed_total = 0
    muni_median: dict[str, float] = {}
    for muni, recs in by_muni.items():
        kept, n_trim = ratios.iqr_trim(recs)
        trimmed[muni] = kept
        n_trimmed_total += n_trim
        if kept:
            muni_median[muni] = ratios.median_ratio([(a, p) for a, p, _ in kept])

    # Pooled, municipality-normalized sample.
    pooled_pairs, pooled_munis, pooled_tax = [], [], []
    for muni, recs in trimmed.items():
        if muni in muni_median:
            pooled_pairs.extend((a, p) for a, p, _ in recs)
            pooled_tax.extend((p, t) for _, p, t in recs if t > 0)
            pooled_munis.extend([muni] * len(recs))
    norm_pooled = [(a / muni_median[m], p)
                   for (a, p), m in zip(pooled_pairs, pooled_munis)]

    muni_rows = []
    for muni in sorted(trimmed, key=lambda m: -len(trimmed[m])):
        pairs = [(a, p) for a, p, _ in trimmed[muni]]
        if len(pairs) < config.MUNI_MIN_N:
            continue
        p_v = ratios.prd(pairs)
        b_v = ratios.prb(pairs)
        muni_rows.append({
            "name": muni,
            "n": len(pairs),
            "median_ratio": round(ratios.median_ratio(pairs), 3),
            "cod": round(ratios.cod(pairs), 1),
            "prd": round(p_v, 3),
            "prb": round(b_v.coefficient, 3),
            "prb_t": round(b_v.t_stat, 1),
            "reading": _verdict(p_v, b_v),
        })

    prd_v = ratios.prd(norm_pooled)
    prb_v = ratios.prb(norm_pooled)
    deciles = [
        {**row,
         "median_price": int(row["median_price"]),
         "median_norm_ratio": round(row["median_norm_ratio"], 3)}
        for row in ratios.decile_table(pooled_pairs, muni_median, pooled_munis,
                                       config.N_DECILES)
    ]
    gap = ((deciles[0]["median_norm_ratio"] / deciles[-1]["median_norm_ratio"] - 1) * 100
           if deciles else None)

    # Dollar tax-shift illustration (NETPRPTA = actual net property tax).
    overall_etr, shift_rows = ratios.tax_shift_table(pooled_tax, config.N_DECILES)
    tax_shift = {
        "n": len(pooled_tax),
        "overall_etr": round(overall_etr, 5),
        "deciles": [
            {"decile": r["decile"], "n": r["n"],
             "median_price": int(r["median_price"]),
             "median_tax": int(round(r["median_tax"])),
             "median_etr": round(r["median_etr"], 5),
             "median_shift": int(round(r["median_shift"]))}
            for r in shift_rows
        ],
    }

    return {
        "generated": date.today().isoformat(),
        "county": config.COUNTY,
        "study_year": config.STUDY_YEAR,
        "min_sale_price": config.MIN_SALE_PRICE,
        "reference": {
            "cod_max_sfr": config.IAAO_COD_MAX_SFR,
            "prd_band": list(config.IAAO_PRD_BAND),
            "prb_band": list(config.IAAO_PRB_BAND),
            "muni_min_n": config.MUNI_MIN_N,
        },
        "sample": {
            "waterfall": [{"step": name, "remaining": n} for name, n in waterfall],
            "exclusions": (
                [{"step": name, "excluded": n} for name, n in join_excl.items()]
                + [{"step": "IQR ratio trimming (within municipality)",
                    "excluded": n_trimmed_total}]
            ),
            "final_n": sum(len(v) for v in trimmed.values()),
        },
        "municipalities": muni_rows,
        "pooled": {
            "n": len(norm_pooled),
            "cod": round(ratios.cod(norm_pooled), 1),
            "prd": round(prd_v, 3),
            "prb": round(prb_v.coefficient, 3),
            "prb_se": round(prb_v.std_error, 3),
            "prb_t": round(prb_v.t_stat, 1),
            "reading": _verdict(prd_v, prb_v),
        },
        "deciles": deciles,
        "bottom_vs_top_pct": round(gap, 1) if gap is not None else None,
        "tax_shift": tax_shift,
    }


def render_md(f: dict) -> str:
    lines: list[str] = []
    w = lines.append
    w(f"# Assessment equity in {f['county']} County — {f['study_year']} sales ratio study")
    w("")
    w(f"*Generated {f['generated']} by `wpr-assessment-equity`. "
      f"Aggregate statistics only — see CLAUDE.md for methodology and privacy policy.*")
    w("")
    w("## Sample construction")
    w("")
    w("| Filter step | remaining |")
    w("|---|---|")
    for row in f["sample"]["waterfall"]:
        w(f"| {row['step']} | {row['remaining']:,} |")
    for row in f["sample"]["exclusions"]:
        w(f"| excluded: {row['step']} | −{row['excluded']:,} |")
    w(f"| **final study sample** | **{f['sample']['final_n']:,}** |")
    w("")

    ref = f["reference"]
    w("## Municipality-level statistics (IAAO)")
    w("")
    w(f"Municipalities with fewer than {ref['muni_min_n']} trimmed sales are pooled "
      f"but not reported standalone. COD reference for single-family residential: "
      f"<= {ref['cod_max_sfr']:.0f}. PRD band {ref['prd_band'][0]}–"
      f"{ref['prd_band'][1]}. PRB band ±0.05.")
    w("")
    w("| Municipality | n | median ratio | COD | PRD | PRB (t) | reading |")
    w("|---|---|---|---|---|---|---|")
    for m in f["municipalities"]:
        w(f"| {m['name']} | {m['n']} | {m['median_ratio']:.3f} "
          f"| {m['cod']:.1f} | {m['prd']:.3f} "
          f"| {m['prb']:+.3f} ({m['prb_t']:.1f}) | {m['reading']} |")
    w("")

    p = f["pooled"]
    w("## County pooled (municipality-normalized)")
    w("")
    w("Each sale's ratio is divided by its municipality's median ratio before "
      "pooling, so this compares equity, not revaluation timing.")
    w("")
    w(f"- n = {p['n']:,}")
    w(f"- COD = {p['cod']:.1f}")
    w(f"- PRD = {p['prd']:.3f}")
    w(f"- PRB = {p['prb']:+.3f} (SE {p['prb_se']:.3f}, t {p['prb_t']:.1f})")
    w(f"- **Reading: {p['reading']}**")
    w("")

    w("## Median normalized ratio by sale-price decile")
    w("")
    w("| decile | n | price range | median price | median normalized ratio |")
    w("|---|---|---|---|---|")
    for row in f["deciles"]:
        w(f"| {row['decile']} | {row['n']} "
          f"| ${row['price_min']:,}–${row['price_max']:,} "
          f"| ${row['median_price']:,} | {row['median_norm_ratio']:.3f} |")
    if f["bottom_vs_top_pct"] is not None:
        w("")
        w(f"Bottom-decile homes are assessed at a ratio **{f['bottom_vs_top_pct']:+.1f}%** "
          f"relative to top-decile homes.")
    w("")

    ts = f.get("tax_shift") or {}
    if ts.get("deciles"):
        w("## Property-tax dollars (tax-shift illustration)")
        w("")
        w(f"Actual net property tax (parcel `NETPRPTA`) on {ts['n']:,} of the study "
          f"sales. \"Shift\" is what the household paid minus what the county-average "
          f"effective rate ({ts['overall_etr'] * 100:.2f}% of sale price) would "
          f"charge — positive means paying more than a flat-rate county would ask.")
        w("")
        w("| decile | n | median price | median net tax | median eff. rate | median shift |")
        w("|---|---|---|---|---|---|")
        for r in ts["deciles"]:
            w(f"| {r['decile']} | {r['n']} | ${r['median_price']:,} "
              f"| ${r['median_tax']:,} | {r['median_etr'] * 100:.2f}% "
              f"| {'+' if r['median_shift'] >= 0 else '−'}${abs(r['median_shift']):,} |")
        w("")

    w("## Caveats")
    w("")
    w(f"- Single-family, arm's-length, entire-parcel, fee-paying sales "
      f">= ${f['min_sale_price']:,} only; {f['study_year']} sales against the "
      f"{f['study_year']} assessment roll.")
    w("- Small municipalities appear only in the pooled analysis.")
    w("- The tax-shift table is an illustration, not a simulation: NETPRPTA is net "
      "of credits, and it holds levies fixed (a re-assessment would also shift "
      "rates). Sales with no reported net tax are excluded from it. Its gradient "
      "blends assessment inequity WITH municipal rate geography — lower-priced "
      "homes concentrating in higher-rate municipalities also steepens it.")
    w("- Independent context: the UChicago Center for Municipal Finance's own "
      "Marathon County study (First American sales, 2014–2023) found 67% of the "
      "lowest-value homes over-assessed vs 45% of the highest-value homes — same "
      "direction as this study, different data and method (county-median "
      "normalization). Wisconsin Policy Forum (2023) documents the statewide "
      "revaluation-staleness backdrop. See docs/data-sources.md.")
    w("- This memo is an internal finding, not a publication. Editorial decisions "
      "(including whether any illustrative property is ever named) rest with the "
      "editor per docs/editorial-memo-draft.md.")
    return "\n".join(lines)


def run() -> None:
    findings = compute()
    config.OUTPUT_DIR.mkdir(exist_ok=True)
    config.FINDINGS_MD.write_text(render_md(findings), encoding="utf-8")
    config.FINDINGS_JSON.write_text(json.dumps(findings, indent=1), encoding="utf-8")
    print(f"Wrote {config.FINDINGS_MD}")
    print(f"Wrote {config.FINDINGS_JSON}")


if __name__ == "__main__":
    run()
