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

// The money chart: median municipality-normalized assessment ratio by
// sale-price decile. 1.00 = assessed exactly at the municipality's typical
// level; above the line = over-assessed relative to neighbors. The bottom
// decile is highlighted — it's where the deviation concentrates.
export default function DecileChart({ deciles, gapPct, year }) {
  const data = deciles.map((d) => ({ ...d, label: moneyCompact(d.median_price) }));
  const maxAbove = Math.max(...deciles.map((d) => d.median_norm_ratio));

  return (
    <section className="decile" aria-label="Assessment ratio by price decile">
      <h2>Who gets assessed above the local norm?</h2>
      <figure className="chart chart-solo">
        <figcaption>
          Median normalized assessment ratio by sale-price decile · {year}
          <span className="chart-hint"> · 1.00 = the municipality's typical level</span>
        </figcaption>
        <div className="chart-body">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data} margin={{ left: 8, right: 16, top: 20 }}>
              <CartesianGrid vertical={false} stroke={GRID} />
              <XAxis
                dataKey="label"
                tick={{ fontSize: 11 }}
                stroke={AXIS}
                interval={0}
                tickMargin={6}
              />
              <YAxis
                domain={[0.9, Math.max(1.1, Math.ceil(maxAbove * 20) / 20)]}
                tickFormatter={(v) => v.toFixed(2)}
                tick={{ fontSize: 11 }}
                stroke={AXIS}
                width={44}
              />
              <Tooltip content={<DecileTip />} cursor={{ fill: "rgba(58,134,124,0.08)" }} />
              <ReferenceLine y={1} stroke={LABEL} strokeDasharray="4 3" />
              <Bar dataKey="median_norm_ratio" radius={[3, 3, 0, 0]} isAnimationActive={false}>
                {data.map((d) => (
                  <Cell key={d.decile} fill={d.decile === 1 ? AMBER : TEAL} />
                ))}
                <LabelList
                  dataKey="median_norm_ratio"
                  position="top"
                  formatter={(v) => v.toFixed(2)}
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
          relative to top-decile homes. Deciles are labeled by their median sale price.
        </p>
      )}
    </section>
  );
}
