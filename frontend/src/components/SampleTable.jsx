// How the study sample was built — every filter step and every exclusion,
// counted. Collapsed by default; the transparency lives one click away.
export default function SampleTable({ sample, year }) {
  return (
    <section className="sample" aria-label="How the sample was built">
      <details>
        <summary>
          <h2>How we built the sample</h2>
          <span className="sample-n">
            {sample.waterfall[0].remaining.toLocaleString()} recorded transfers →{" "}
            {sample.final_n.toLocaleString()} studied sales
          </span>
        </summary>
        <div className="table-wrap">
          <table className="muni-table">
            <thead>
              <tr>
                <th>Filter step</th>
                <th className="num">Remaining</th>
              </tr>
            </thead>
            <tbody>
              {sample.waterfall.map((row) => (
                <tr key={row.step}>
                  <td>{row.step}</td>
                  <td className="num mono">{row.remaining.toLocaleString()}</td>
                </tr>
              ))}
              {sample.exclusions.map((row) => (
                <tr key={row.step} className="excl">
                  <td>excluded: {row.step}</td>
                  <td className="num mono">−{row.excluded.toLocaleString()}</td>
                </tr>
              ))}
              <tr className="total">
                <td>final study sample · {year}</td>
                <td className="num mono">{sample.final_n.toLocaleString()}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </details>
    </section>
  );
}
