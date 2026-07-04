"""Orchestration. One responsibility: run the study and write the findings memo.

    python -m analysis.study      -> output/findings-<year>.md

Everything written here is AGGREGATE-ONLY: statistics by municipality and
price decile. No names, addresses, or parcel numbers.
"""

import statistics
from collections import defaultdict
from datetime import date

from . import config, parcels, ratios
from .join import join
from .retr import load_study_population


def _pairs_by_muni(matches) -> dict[str, list[tuple[int, int]]]:
    by_muni: dict[str, list[tuple[int, int]]] = defaultdict(list)
    for m in matches:
        assessed = int(float(m.parcel["CNTASSDVALUE"]))
        by_muni[m.parcel["PLACENAME"].strip()].append((assessed, m.sale["_price"]))
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


def run() -> None:
    sales, waterfall = load_study_population(config.RETR_RAW_CSV)
    index = parcels.load()
    matches, join_excl = join(sales, index)

    by_muni = _pairs_by_muni(matches)

    # Per-municipality trimming + medians (the normalization denominators).
    trimmed: dict[str, list[tuple[int, int]]] = {}
    n_trimmed_total = 0
    muni_median: dict[str, float] = {}
    for muni, pairs in by_muni.items():
        kept, n_trim = ratios.iqr_trim(pairs)
        trimmed[muni] = kept
        n_trimmed_total += n_trim
        if kept:
            muni_median[muni] = ratios.median_ratio(kept)

    # Pooled, municipality-normalized sample.
    pooled_pairs, pooled_munis = [], []
    for muni, pairs in trimmed.items():
        if muni in muni_median:
            pooled_pairs.extend(pairs)
            pooled_munis.extend([muni] * len(pairs))
    norm_pooled = [(a / muni_median[m], p)
                   for (a, p), m in zip(pooled_pairs, pooled_munis)]

    lines: list[str] = []
    w = lines.append
    w(f"# Assessment equity in {config.COUNTY} County — {config.STUDY_YEAR} sales ratio study")
    w("")
    w(f"*Generated {date.today().isoformat()} by `wpr-assessment-equity`. "
      f"Aggregate statistics only — see CLAUDE.md for methodology and privacy policy.*")
    w("")
    w("## Sample construction")
    w("")
    w("| Filter step | remaining |")
    w("|---|---|")
    for name, n in waterfall:
        w(f"| {name} | {n:,} |")
    for name, n in join_excl.items():
        w(f"| excluded: {name} | −{n:,} |")
    w(f"| excluded: IQR ratio trimming (within municipality) | −{n_trimmed_total:,} |")
    w(f"| **final study sample** | **{sum(len(v) for v in trimmed.values()):,}** |")
    w("")

    w("## Municipality-level statistics (IAAO)")
    w("")
    w(f"Municipalities with fewer than {config.MUNI_MIN_N} trimmed sales are pooled "
      f"but not reported standalone. COD reference for single-family residential: "
      f"<= {config.IAAO_COD_MAX_SFR:.0f}. PRD band {config.IAAO_PRD_BAND[0]}–"
      f"{config.IAAO_PRD_BAND[1]}. PRB band ±0.05.")
    w("")
    w("| Municipality | n | median ratio | COD | PRD | PRB (t) | reading |")
    w("|---|---|---|---|---|---|---|")
    for muni in sorted(trimmed, key=lambda m: -len(trimmed[m])):
        pairs = trimmed[muni]
        if len(pairs) < config.MUNI_MIN_N:
            continue
        p_v = ratios.prd(pairs)
        b_v = ratios.prb(pairs)
        w(f"| {muni} | {len(pairs)} | {ratios.median_ratio(pairs):.3f} "
          f"| {ratios.cod(pairs):.1f} | {p_v:.3f} "
          f"| {b_v.coefficient:+.3f} ({b_v.t_stat:.1f}) | {_verdict(p_v, b_v)} |")
    w("")

    w("## County pooled (municipality-normalized)")
    w("")
    w("Each sale's ratio is divided by its municipality's median ratio before "
      "pooling, so this compares equity, not revaluation timing.")
    w("")
    prd_v = ratios.prd(norm_pooled)
    prb_v = ratios.prb(norm_pooled)
    w(f"- n = {len(norm_pooled):,}")
    w(f"- COD = {ratios.cod(norm_pooled):.1f}")
    w(f"- PRD = {prd_v:.3f}")
    w(f"- PRB = {prb_v.coefficient:+.3f} (SE {prb_v.std_error:.3f}, t {prb_v.t_stat:.1f})")
    w(f"- **Reading: {_verdict(prd_v, prb_v)}**")
    w("")

    w("## Median normalized ratio by sale-price decile")
    w("")
    w("| decile | n | price range | median price | median normalized ratio |")
    w("|---|---|---|---|---|")
    table = ratios.decile_table(pooled_pairs, muni_median, pooled_munis,
                                config.N_DECILES)
    for row in table:
        w(f"| {row['decile']} | {row['n']} "
          f"| ${row['price_min']:,}–${row['price_max']:,} "
          f"| ${int(row['median_price']):,} | {row['median_norm_ratio']:.3f} |")
    if table:
        gap = (table[0]["median_norm_ratio"] / table[-1]["median_norm_ratio"] - 1) * 100
        w("")
        w(f"Bottom-decile homes are assessed at a ratio **{gap:+.1f}%** relative to "
          f"top-decile homes.")
    w("")
    w("## Caveats")
    w("")
    w(f"- Single-family, arm's-length, entire-parcel, fee-paying sales "
      f">= ${config.MIN_SALE_PRICE:,} only; {config.STUDY_YEAR} sales against the "
      f"{config.STUDY_YEAR} assessment roll.")
    w("- Small municipalities appear only in the pooled analysis.")
    w("- This memo is an internal finding, not a publication. Editorial decisions "
      "(including whether any illustrative property is ever named) rest with the "
      "editor per docs/editorial-memo-draft.md.")

    config.OUTPUT_DIR.mkdir(exist_ok=True)
    config.FINDINGS_MD.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {config.FINDINGS_MD}")


if __name__ == "__main__":
    run()
