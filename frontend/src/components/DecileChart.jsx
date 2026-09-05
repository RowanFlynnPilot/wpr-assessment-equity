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
import { CHART_AMBER, CHART_TEAL, GRID, AXIS, LABEL } from "../lib/palette.js";

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

// Direct labels only on the two extremes (the story's bars); the axis, the
// tooltip, and the table twin carry the rest.
function ExtremeLabel({ x, y, width, height, value, index, labelled }) {
  if (!labelled.has(index)) return null;
  const up = value >= 0;
  return (
    <text
      x={x + width / 2}
      y={up ? y - 6 : y + height + 14}
      textAnchor="middle"
      fontSize={11}
      fontFamily="'Oswald', Helvetica, Arial, sans-serif"
      fill={LABEL}
    >
      {pctVsPar(1 + value)}
    </text>
  );
}

// The money chart, drawn honestly: each bar is the decile's DEVIATION from the
// municipality-typical assessment level (median normalized ratio − 1), so bar
// length encodes exactly the thing the story is about. Amber = assessed above
// the local norm, teal = below. A zero-based ratio axis would hide the effect;
// a truncated ratio axis would exaggerate it — deviation bars do neither.
export default function DecileChart({ deciles, gapPct, bottomCI, year }) {
  const data = deciles.map((d) => ({
    ...d,
    deviation: +(d.median_norm_ratio - 1).toFixed(3),
    label: moneyCompact(d.median_price),
  }));
  const iMax = data.reduce((best, d, i) => (d.deviation > data[best].deviation ? i : best), 0);
  const iMin = data.reduce((best, d, i) => (d.deviation < data[best].deviation ? i : best), 0);
  const labelled = new Set([iMax, iMin]);

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
            <BarChart data={data} margin={{ left: 8, right: 16, top: 18, bottom: 2 }} barCategoryGap="30%">
              <CartesianGrid vertical={false} stroke={GRID} />
              <XAxis
                dataKey="label"
                tick={{ fontSize: 11, fill: LABEL }}
                stroke={AXIS}
                tickLine={false}
                minTickGap={10}
                tickMargin={6}
              />
              <YAxis
                tickFormatter={(v) => pctVsPar(1 + v, 0)}
                tick={{ fontSize: 11, fill: LABEL }}
                stroke={AXIS}
                tickLine={false}
                width={44}
              />
              <Tooltip content={<DecileTip />} cursor={{ fill: "rgba(15,143,122,0.08)" }} />
              <ReferenceLine y={0} stroke={AXIS} />
              <Bar dataKey="deviation" maxBarSize={24} isAnimationActive={false}>
                {data.map((d) => (
                  <Cell
                    key={d.decile}
                    fill={d.deviation > 0 ? CHART_AMBER : CHART_TEAL}
                    radius={d.deviation > 0 ? [4, 4, 0, 0] : [0, 0, 4, 4]}
                  />
                ))}
                <LabelList dataKey="deviation" content={<ExtremeLabel labelled={labelled} />} />
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </figure>
      {gapPct != null && (
        <p className="decile-gap">
          Bottom-decile homes are assessed at a ratio <b>{gapPct > 0 ? "+" : ""}{gapPct}%</b>{" "}
          relative to top-decile homes
          {bottomCI && (
            <>
              {" "}(bottom-decile deviation {pctVsPar(deciles[0].median_norm_ratio)}, 95% CI{" "}
              {pctVsPar(bottomCI[0])} to {pctVsPar(bottomCI[1])})
            </>
          )}
          . Deciles are labeled by their median sale price; deviations are measured
          within each home's own municipality, so revaluation timing can't produce them.
        </p>
      )}
      <details className="chart-table">
        <summary>View this chart as a table</summary>
        <div className="table-wrap">
          <table className="muni-table">
            <thead>
              <tr>
                <th>Decile</th>
                <th>Price range</th>
                <th className="num">Median price</th>
                <th className="num">Sales</th>
                <th className="num">Normalized ratio</th>
                <th className="num">vs local norm</th>
              </tr>
            </thead>
            <tbody>
              {data.map((d) => (
                <tr key={d.decile}>
                  <td data-label="Decile">{d.decile}</td>
                  <td data-label="Price range">{money(d.price_min)}–{money(d.price_max)}</td>
                  <td className="num mono" data-label="Median price">{money(d.median_price)}</td>
                  <td className="num mono" data-label="Sales">{d.n}</td>
                  <td className="num mono" data-label="Normalized ratio">{d.median_norm_ratio.toFixed(3)}</td>
                  <td className="num mono" data-label="vs local norm">{pctVsPar(d.median_norm_ratio)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </details>
    </section>
  );
}
