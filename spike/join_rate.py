"""SPIKE: end-to-end mechanics check on any raw RETR CSV, deliberately WITHOUT
the vintage gate. This validates the waterfall, join contract, and statistics
code paths — its ratio numbers are NOT findings when the parcel vintage doesn't
match the sales year.

    python -m spike.join_rate raw/some_month.csv

Recorded result (2026-07-04, June-2025 RETR × live V11 endpoint):
    488 raw rows -> 199 study population -> join rate 99.0% (2 genuine absences,
    zero format failures) -> 192 usable ratios, median 0.751 (vintage-mismatched
    2024 roll ÷ 2025 prices — mechanics only, not a finding).
"""

import sys
from pathlib import Path

from analysis import ratios
from analysis.join import join
from analysis.retr import load_study_population


def run(csv_path: Path) -> None:
    sales, waterfall = load_study_population(csv_path)
    print("waterfall:")
    for name, n in waterfall:
        print(f"  {name}: {n}")

    # Parcel index WITHOUT the vintage gate (spike-only): read the fetched CSV
    # through the same loader internals.
    import csv as _csv
    from analysis.config import PARCEL_CSV
    from analysis.join import normalize_parcel_id
    if not PARCEL_CSV.exists():
        raise FileNotFoundError("run `python -m analysis.parcels` first")
    index = {}
    with open(PARCEL_CSV, newline="", encoding="utf-8") as f:
        for row in _csv.DictReader(f):
            pid = normalize_parcel_id(row["PARCELID"] or "")
            if pid:
                index[pid] = row
    print(f"parcel index: {len(index)}")

    matches, excl = join(sales, index)
    print(f"joined: {len(matches)}  exclusions: {excl}")

    pairs = [(int(float(m.parcel["CNTASSDVALUE"])), m.sale["_price"])
             for m in matches if m.parcel["CNTASSDVALUE"]]
    kept, n_trim = ratios.iqr_trim(pairs)
    print(f"ratios: n={len(kept)} (trimmed {n_trim}), "
          f"median={ratios.median_ratio(kept):.3f}, COD={ratios.cod(kept):.1f}, "
          f"PRD={ratios.prd(kept):.3f}")
    b = ratios.prb(kept)
    print(f"PRB={b.coefficient:+.3f} (t={b.t_stat:.1f}) "
          f"[NOT a finding if vintage-mismatched]")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: python -m spike.join_rate <raw_retr.csv>")
    run(Path(sys.argv[1]))
