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
import { money, moneyCompact, signedFixed } from "../lib/format.js";
import { CHART_AMBER, CHART_TEAL, GRID, AXIS, LABEL } from "../lib/palette.js";
import { ExtremeLabel, extremes } from "./DecileChart.jsx";

const signedMoney = (n) => (n > 0 ? "+" : n < 0 ? "−" : "") + money(Math.abs(n));

function ShiftTip({ active, payload }) {
  if (!active || !payload?.length) return null;
  const d = payload[0].payload;
  return (
    <div className="chart-tip">
      <div className="chart-tip-title">Decile {d.decile} · median home {money(d.median_price)}</div>
      <div className="chart-tip-row">
        Median net tax<b>{money(d.median_tax)}</b>
      </div>
      <div className="chart-tip-row">
        Effective rate<b>{(d.median_etr * 100).toFixed(2)}%</b>
      </div>
      <div className="chart-tip-row">
        vs county-average rate<b>{signedMoney(d.median_shift)}</b>
      </div>
      <div className="chart-tip-sub">{d.n} sales · positive = paid more than a flat county rate would charge</div>
    </div>
  );
}

// Same grammar as the decile chart, in dollars: each bar is the median shift —
// what the household paid minus what the county-average effective rate would
// charge on its sale price. Amber paid more, teal paid less.
export default function TaxShiftChart({ taxShift, year }) {
  const rows = taxShift?.deciles ?? [];
  if (rows.length < 2) return null;
  const data = rows.map((d) => ({ ...d, label: moneyCompact(d.median_price) }));
  const labelled = extremes(data.map((d) => d.median_shift));
  const overall = (taxShift.overall_etr * 100).toFixed(2);

  return (
    <>
      <figure className="chart chart-solo">
        <figcaption>
          Property-tax dollars vs a county-average rate ({overall}% of sale price), by
          sale-price decile · {year}
          <span className="chart-hint">
            {" "}
            · <span className="swatch swatch-amber" /> paid more ·{" "}
            <span className="swatch swatch-teal" /> paid less
          </span>
        </figcaption>
        <div className="chart-body">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data} margin={{ left: 8, right: 16, top: 18, bottom: 2 }} barCategoryGap="30%">
              <CartesianGrid vertical={false} stroke={GRID} />
              <XAxis dataKey="label" tick={{ fontSize: 11, fill: LABEL }} stroke={AXIS} tickLine={false} minTickGap={10} tickMargin={6} />
              <YAxis
                // 20% headroom past the extremes so their direct labels never
                // collide with the plot edge.
                domain={[(min) => Math.floor((min * 1.2) / 50) * 50, (max) => Math.ceil((max * 1.2) / 50) * 50]}
                tickFormatter={(v) => (v === 0 ? "$0" : signedMoney(v))}
                tick={{ fontSize: 11, fill: LABEL }}
                stroke={AXIS}
                tickLine={false}
                width={58}
              />
              <Tooltip content={<ShiftTip />} cursor={{ fill: "rgba(15,143,122,0.08)" }} />
              <ReferenceLine y={0} stroke={AXIS} />
              <Bar dataKey="median_shift" maxBarSize={24} isAnimationActive={false}>
                {data.map((d) => (
                  <Cell
                    key={d.decile}
                    fill={d.median_shift > 0 ? CHART_AMBER : CHART_TEAL}
                    radius={d.median_shift > 0 ? [4, 4, 0, 0] : [0, 0, 4, 4]}
                  />
                ))}
                <LabelList dataKey="median_shift" content={<ExtremeLabel labelled={labelled} format={signedMoney} />} />
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </figure>
      <details className="chart-table">
        <summary>View this chart as a table</summary>
        <div className="table-wrap">
          <table className="muni-table">
            <thead>
              <tr>
                <th>Decile</th>
                <th className="num">Median price</th>
                <th className="num">Sales</th>
                <th className="num">Median net tax</th>
                <th className="num">Effective rate</th>
                <th className="num">vs county-average rate</th>
              </tr>
            </thead>
            <tbody>
              {data.map((d) => (
                <tr key={d.decile}>
                  <td data-label="Decile">{d.decile}</td>
                  <td className="num mono" data-label="Median price">{money(d.median_price)}</td>
                  <td className="num mono" data-label="Sales">{d.n}</td>
                  <td className="num mono" data-label="Median net tax">{money(d.median_tax)}</td>
                  <td className="num mono" data-label="Effective rate">{signedFixed(d.median_etr * 100, 2).replace(/^\+/, "")}%</td>
                  <td className="num mono" data-label="vs county-average rate">{signedMoney(d.median_shift)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </details>
    </>
  );
}
