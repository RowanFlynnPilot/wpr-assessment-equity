import { fixed, signedFixed } from "../lib/format.js";

// Per-municipality IAAO statistics. Municipality-level numbers are directly
// comparable to the IAAO reference bands; municipalities under the study's
// minimum sample are pooled into the county numbers but not shown standalone.
export default function MuniTable({ rows, reference, flaggedCount }) {
  return (
    <section className="munis" aria-label="Municipality statistics">
      <h2>Municipality by municipality</h2>
      <p className="section-hint">
        Wisconsin assesses at the municipal level, so each community is judged on its
        own numbers. COD measures uniformity (IAAO standard ≤{" "}
        {reference.cod_max_sfr.toFixed(0)} for single-family homes); PRD and PRB measure
        whether cheap and expensive homes are assessed at the same fraction of value.
        {flaggedCount > 0 &&
          ` ${flaggedCount} ${flaggedCount === 1 ? "community sits" : "communities sit"} outside the bands.`}
        {" "}Communities with fewer than {reference.muni_min_n} usable sales are counted
        in the county-wide numbers only.
      </p>
      <div className="table-wrap">
        <table className="muni-table">
          <thead>
            <tr>
              <th>Municipality</th>
              <th className="num">Sales</th>
              <th className="num">Median ratio</th>
              <th className="num">COD</th>
              <th className="num">PRD</th>
              <th className="num">PRB (t)</th>
              <th>Reading</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((m) => {
              const flag = !m.reading.startsWith("within");
              return (
                <tr key={m.name}>
                  <td>{m.name}</td>
                  <td className="num mono">{m.n}</td>
                  <td className="num mono">{m.median_ratio.toFixed(3)}</td>
                  <td className="num mono">{m.cod.toFixed(1)}</td>
                  <td className="num mono">{m.prd.toFixed(3)}</td>
                  <td className="num mono">
                    {signedFixed(m.prb)} ({fixed(m.prb_t)})
                  </td>
                  <td>
                    <span className={`reading-badge sm ${flag ? "flag" : "ok"}`}>
                      {flag ? m.reading.split(" — ")[0] : "within bands"}
                    </span>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </section>
  );
}
