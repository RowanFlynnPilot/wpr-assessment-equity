import { fixed, signedFixed, pctVsPar } from "../lib/format.js";

// What changed since the prior study year. Every cell is a delta of a number
// the reader has already met above, so this section adds no new concepts —
// only direction. Municipal level jumps (≥ 0.10 in median ratio) are called out
// because they are almost always revaluations, the thing that most confuses a
// year-to-year comparison if left unexplained.
const LEVEL_JUMP = 0.1;

function Delta({ value, digits = 1, suffix = "", goodWhenDown = true }) {
  if (value == null || Number.isNaN(value)) return <span className="delta flat">—</span>;
  const dir = value > 0 ? "up" : value < 0 ? "down" : "flat";
  const good = dir === "flat" ? "flat" : (dir === "down") === goodWhenDown ? "good" : "bad";
  const glyph = dir === "up" ? "▲" : dir === "down" ? "▼" : "■";
  return (
    <span className={`delta ${good}`}>
      {glyph} {signedFixed(value, digits)}{suffix}
    </span>
  );
}

export default function YearOverYear({ current, previous }) {
  const cy = current.study_year;
  const py = previous.study_year;
  const cur = current.pooled;
  const prev = previous.pooled;
  const curBottom = (current.deciles[0].median_norm_ratio - 1) * 100;
  const prevBottom = (previous.deciles[0].median_norm_ratio - 1) * 100;

  const prevByName = Object.fromEntries(previous.municipalities.map((m) => [m.name, m]));
  const jumps = current.municipalities
    .filter((m) => prevByName[m.name])
    .map((m) => ({ name: m.name, from: prevByName[m.name].median_ratio, to: m.median_ratio }))
    .filter((j) => Math.abs(j.to - j.from) >= LEVEL_JUMP)
    .sort((a, b) => Math.abs(b.to - b.from) - Math.abs(a.to - a.from));

  const rows = [
    {
      label: "Cheapest tenth vs local norm",
      prev: pctVsPar(previous.deciles[0].median_norm_ratio),
      cur: pctVsPar(current.deciles[0].median_norm_ratio),
      delta: <Delta value={curBottom - prevBottom} suffix=" pts" />,
      note: "the headline inequity figure — lower is fairer",
    },
    {
      label: "Bottom vs top decile gap",
      prev: `${previous.bottom_vs_top_pct > 0 ? "+" : ""}${previous.bottom_vs_top_pct}%`,
      cur: `${current.bottom_vs_top_pct > 0 ? "+" : ""}${current.bottom_vs_top_pct}%`,
      delta: <Delta value={current.bottom_vs_top_pct - previous.bottom_vs_top_pct} suffix=" pts" />,
      note: "how far apart the cheapest and priciest tenths sit",
    },
    {
      label: "Uniformity · COD",
      prev: fixed(prev.cod, 1),
      cur: fixed(cur.cod, 1),
      delta: <Delta value={cur.cod - prev.cod} />,
      note: "lower is more consistent",
    },
    {
      label: "Regressivity · PRD",
      prev: fixed(prev.prd, 3),
      cur: fixed(cur.prd, 3),
      delta: <Delta value={cur.prd - prev.prd} digits={3} />,
      note: "closer to 1.000 is fairer",
    },
    {
      label: "Sales studied",
      prev: prev.n.toLocaleString(),
      cur: cur.n.toLocaleString(),
      delta: <Delta value={cur.n - prev.n} digits={0} goodWhenDown={false} />,
      note: "",
    },
  ];

  return (
    <section className="yoy" aria-label={`What changed since ${py}`}>
      <h2>What changed since {py}</h2>
      <div className="table-wrap">
        <table className="muni-table yoy-table">
          <thead>
            <tr>
              <th>Measure</th>
              <th className="num">{py}</th>
              <th className="num">{cy}</th>
              <th className="num">Change</th>
              <th>Reading</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((r) => (
              <tr key={r.label}>
                <td data-label="Measure">{r.label}</td>
                <td className="num mono" data-label={String(py)}>{r.prev}</td>
                <td className="num mono" data-label={String(cy)}>{r.cur}</td>
                <td className="num mono" data-label="Change">{r.delta}</td>
                <td className="yoy-note" data-label="Reading">{r.note}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {jumps.length > 0 && (
        <p className="section-hint yoy-jumps">
          Level changes to know about: {jumps.map((j, i) => (
            <span key={j.name}>
              {i > 0 && "; "}
              <b>{j.name}</b> moved from {j.from.toFixed(3)} to {j.to.toFixed(3)}
            </span>
          ))}. A jump that size is a revaluation — it resets the community's overall
          assessment level, which is why the equity statistics above compare each home
          only to its own municipality's norm.
        </p>
      )}
    </section>
  );
}
