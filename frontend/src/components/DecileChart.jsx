import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Cell,
  ReferenceLine,
  LabelList,
} from "recharts";
import { money, moneyCompact, pctVsPar } from "../lib/format.js";
import { TEAL, AMBER, GRID, AXIS, LABEL } from "../lib/palette.js";

function DecileTip({ active, payload }) {
  if (!active || !payload?.length) return null;
  const d = payload[0].payload;
  return (
    <div className="chart-tip">
      <div className="chart-tip-title">
        Decile {d.decile} · {moneyCompact(d.price_min)}–{moneyCompact(d.price_max)}
      </div>
      <div className="chart-tip-row">
        Median price<b>{money(d.median_price)}</b>
      </div>
      <div className="chart-tip-row">
        Normalized ratio<b>{d.median_norm_ratio.toFixed(3)}</b>
      </div>
      <div className="chart-tip-sub">
        {d.n} sales · assessed {pctVsPar(d.median_norm_ratio)} vs the local typical level
      </div>
    </div>
  );
}

// The money chart, drawn honestly: each bar is the decile's DEVIATION from the
// municipality-typical assessment level (median normalized ratio − 1), so bar
// length encodes exactly the thing the story is about. Amber = assessed above
// the local norm, teal = below. A zero-based ratio axis would hide the effect;
// a truncated ratio axis would exaggerate it — deviation bars do neither.
export default function DecileChart({ deciles, gapPct, year }) {
  const data = deciles.map((d) => ({
    ...d,
    deviation: +(d.median_norm_ratio - 1).toFixed(3),
    label: moneyCompact(d.median_price),
  }));

  return (
    <section className="decile" aria-label="Assessment ratio by price decile">
      <h2>Who gets assessed above the local norm?</h2>
      <p className="section-hint">
        How to read this: every {year} sale is sorted by price and split into ten
        equal groups, cheapest on the left. Each bar shows how far that group's
        typical assessment sits from the <b>norm in its own community</b> — 0% means
        assessed exactly like the typical local home, bars above the line mean
        assessed high (and therefore taxed high) relative to the neighbors.
      </p>
      <figure className="chart chart-solo">
        <figcaption>
          Deviation from the municipality's typical assessment level, by sale-price
          decile · {year}
          <span className="chart-hint">
            {" "}
            · <span className="swatch swatch-amber" /> above the local norm ·{" "}
            <span className="swatch swatch-teal" /> below
          </span>
        </figcaption>
        <div className="chart-body">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data} margin={{ left: 8, right: 16, top: 18, bottom: 2 }}>
              <CartesianGrid vertical={false} stroke={GRID} />
              <XAxis
                dataKey="label"
                tick={{ fontSize: 11 }}
                stroke={AXIS}
                minTickGap={10}
                tickMargin={6}
              />
              <YAxis
                tickFormatter={(v) => pctVsPar(1 + v, 0)}
                tick={{ fontSize: 11 }}
                stroke={AXIS}
                width={44}
              />
              <Tooltip content={<DecileTip />} cursor={{ fill: "rgba(58,134,124,0.08)" }} />
              <ReferenceLine y={0} stroke={LABEL} />
              <Bar dataKey="deviation" radius={[3, 3, 0, 0]} isAnimationActive={false}>
                {data.map((d) => (
                  <Cell key={d.decile} fill={d.deviation > 0 ? AMBER : TEAL} />
                ))}
                <LabelList
                  dataKey="deviation"
                  position="top"
                  formatter={(v) => pctVsPar(1 + v)}
                  style={{ fontSize: 11, fill: LABEL }}
                />
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </figure>
      {gapPct != null && (
        <p className="decile-gap">
          Bottom-decile homes are assessed at a ratio <b>{gapPct > 0 ? "+" : ""}{gapPct}%</b>{" "}
          relative to top-decile homes. Deciles are labeled by their median sale price;
          deviations are measured within each home's own municipality, so revaluation
          timing can't produce them.
        </p>
      )}
    </section>
  );
}
