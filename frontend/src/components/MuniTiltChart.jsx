import { range } from "../lib/format.js";

// "VILLAGE OF RIB MOUNTAIN" -> { name: "Rib Mountain", type: "Village" }: the
// feed carries the parcel layer's all-caps PLACENAME; the chart reads better
// (and fits phones) with the place first and the type as a small suffix.
function friendly(placename) {
  const m = placename.match(/^(CITY|VILLAGE|TOWN) OF (.+)$/i);
  const title = (s) => s.toLowerCase().replace(/\b\w/g, (c) => c.toUpperCase());
  return m ? { name: title(m[2]), type: title(m[1]) } : { name: title(placename), type: "" };
}

// Per-community PRD ("the tilt test") as a dot with its 95% interval, drawn
// over the IAAO acceptable band. A forest plot, in HTML: each row's band,
// midline, whisker and dot are positioned by percentage of a shared scale, so
// the chart stays crisp at any width and the text is real text. The
// municipality table right below is its table twin.
export default function MuniTiltChart({ rows, reference }) {
  const [lo, hi] = reference.prd_band;
  const usable = rows.filter((m) => m.prd_ci);
  if (usable.length < 2) return null;

  const xs = usable.flatMap((m) => [m.prd_ci[0], m.prd_ci[1]]);
  const min = Math.min(0.96, ...xs) - 0.005;
  const max = Math.max(1.05, ...xs) + 0.005;
  const pct = (v) => ((v - min) / (max - min)) * 100;
  const ticks = [];
  for (let t = Math.ceil(min * 50) / 50; t <= max; t += 0.02) ticks.push(+t.toFixed(2));

  return (
    <figure className="chart tilt" aria-label="Regressivity by community">
      <figcaption>
        The tilt test by community · PRD with 95% confidence interval
        <span className="chart-hint">
          {" "}· shaded band = IAAO acceptable range {lo.toFixed(2)}–{hi.toFixed(2)} · right of it
          = cheaper homes over-assessed
        </span>
      </figcaption>
      <div className="tilt-ticks" aria-hidden="true">
        <span className="tilt-name" />
        <span className="tilt-track">
          {ticks.map((t) => (
            <span key={t} className="tilt-tick" style={{ left: `${pct(t)}%` }}>
              {t.toFixed(2)}
            </span>
          ))}
        </span>
        <span className="tilt-val" />
      </div>
      <ol className="tilt-rows">
        {usable.map((m) => {
          const flag = !m.reading.startsWith("within");
          const f = friendly(m.name);
          return (
            <li className="tilt-row" key={m.name}>
              <span className="tilt-name" title={m.name}>
                {f.name}
                {f.type && <small>{f.type}</small>}
              </span>
              <span
                className="tilt-track"
                role="img"
                aria-label={`${m.name}: PRD ${m.prd.toFixed(3)}, 95% CI ${range(m.prd_ci, 3)}`}
                title={`PRD ${m.prd.toFixed(3)} · 95% CI ${range(m.prd_ci, 3)} · n=${m.n}`}
              >
                <span className="tilt-band" style={{ left: `${pct(lo)}%`, width: `${pct(hi) - pct(lo)}%` }} />
                <span className="tilt-mid" style={{ left: `${pct(1)}%` }} />
                <span
                  className="tilt-whisker"
                  style={{ left: `${pct(m.prd_ci[0])}%`, width: `${pct(m.prd_ci[1]) - pct(m.prd_ci[0])}%` }}
                />
                <span className={`tilt-dot${flag ? " flag" : ""}`} style={{ left: `${pct(m.prd)}%` }} />
              </span>
              <span className="tilt-val mono">
                {m.prd.toFixed(3)}
                <span className="ci">{range(m.prd_ci, 3)}</span>
              </span>
            </li>
          );
        })}
      </ol>
      <p className="tilt-foot">
        A dot inside the band, or an interval that reaches into it, is consistent with
        fair treatment of cheap and expensive homes. Wide intervals belong to small
        communities — read those loosely. Full statistics in the table below.
      </p>
    </figure>
  );
}
