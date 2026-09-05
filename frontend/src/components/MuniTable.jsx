import { fixed, signedFixed, range } from "../lib/format.js";

// Per-municipality IAAO statistics. Municipality-level numbers are directly
// comparable to the IAAO reference bands; municipalities under the study's
// minimum sample are pooled into the county numbers but not shown standalone.
// The optional cross-check feed adds DOR's own published level per community.
// Below 760px each row becomes a labelled card (data-label on every cell).
export default function MuniTable({ rows, reference, flaggedCount, crosscheck }) {
  const dor = crosscheck
    ? Object.fromEntries(crosscheck.municipalities.map((m) => [m.name, m]))
    : null;
  const loose = rows.filter((m) => m.uniformity_ok === false).length;

  return (
    <section className="munis" aria-label="Municipality statistics">
      <h2>Municipality by municipality</h2>
      <p className="section-hint">
        Wisconsin assesses at the municipal level, so each community is judged on its
        own numbers. COD measures uniformity (IAAO standard ≤{" "}
        {reference.cod_max_sfr.toFixed(0)} for single-family homes); PRD and PRB measure
        whether cheap and expensive homes are assessed at the same fraction of value.
        {flaggedCount > 0 &&
          ` ${flaggedCount} ${flaggedCount === 1 ? "community sits" : "communities sit"} outside the equity bands.`}
        {loose > 0 &&
          ` ${loose} ${loose === 1 ? "community's assessments are" : "communities' assessments are"} looser than the uniformity standard.`}
        {" "}Communities with fewer than {reference.muni_min_n} usable sales are counted
        in the county-wide numbers only.
        {dor && (
          <>
            {" "}<b>DOR level</b> is the state's own published assessed-to-market ratio for
            the whole municipality (all property classes) — an independent check on the
            median ratio next to it.
          </>
        )}
      </p>
      <div className="table-wrap muni-wrap">
        <table className="muni-table">
          <thead>
            <tr>
              <th>Municipality</th>
              <th className="num">Sales</th>
              <th className="num">Median ratio</th>
              {dor && <th className="num">DOR level</th>}
              <th className="num">COD</th>
              <th className="num">PRD</th>
              <th className="num">PRB (t)</th>
              <th className="num">Eff. tax rate</th>
              <th>Reading</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((m) => {
              const flag = !m.reading.startsWith("within");
              const d = dor?.[m.name];
              return (
                <tr key={m.name}>
                  <td data-label="Municipality" className="muni-name">{m.name}</td>
                  <td className="num mono" data-label="Sales">{m.n}</td>
                  <td className="num mono" data-label="Median ratio">{m.median_ratio.toFixed(3)}</td>
                  {dor && (
                    <td className="num mono" data-label="DOR level">
                      {d?.dor_ratio != null ? d.dor_ratio.toFixed(3) : "—"}
                    </td>
                  )}
                  <td className="num mono" data-label="COD">
                    {m.cod.toFixed(1)}
                    {m.cod_ci && <span className="ci">{range(m.cod_ci, 1)}</span>}
                  </td>
                  <td className="num mono" data-label="PRD">
                    {m.prd.toFixed(3)}
                    {m.prd_ci && <span className="ci">{range(m.prd_ci, 3)}</span>}
                  </td>
                  <td className="num mono" data-label="PRB (t)">
                    {signedFixed(m.prb)} ({fixed(m.prb_t)})
                  </td>
                  <td className="num mono" data-label="Eff. tax rate">
                    {m.median_etr != null ? `${(m.median_etr * 100).toFixed(2)}%` : "—"}
                  </td>
                  <td data-label="Reading" className="reading-cell">
                    <span className={`reading-badge sm ${flag ? "flag" : "ok"}`}>
                      {flag ? m.reading.split(" — ")[0] : "within bands"}
                    </span>
                    {m.uniformity_ok === false && (
                      <span className="reading-badge sm warn">COD above {reference.cod_max_sfr.toFixed(0)}</span>
                    )}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
      <p className="table-foot">
        Small figures under COD and PRD are 95% confidence intervals (bootstrap). Eff. tax
        rate = median net property tax ÷ sale price.
      </p>
    </section>
  );
}
