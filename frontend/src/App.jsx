import { useEffect, useState } from "react";
import Masthead from "./components/Masthead.jsx";
import DecileChart from "./components/DecileChart.jsx";
import MuniTable from "./components/MuniTable.jsx";
import SampleTable from "./components/SampleTable.jsx";
import { pctVsPar, fixed, signedFixed } from "./lib/format.js";

// Is a verdict string inside the IAAO bands, or a flag (REGRESSIVE/PROGRESSIVE)?
const isFlag = (reading) => !reading.startsWith("within");

export default function App() {
  const [findings, setFindings] = useState(null);
  const [error, setError] = useState(false);

  useEffect(() => {
    fetch(`${import.meta.env.BASE_URL}findings.json`)
      .then((r) => {
        if (!r.ok) throw new Error(`feed ${r.status}`);
        return r.json();
      })
      .then(setFindings)
      .catch(() => setError(true));
  }, []);

  if (error) {
    return (
      <>
        <Masthead />
        <main className="page">
          <p className="empty">Couldn’t load the findings feed. Please try again later.</p>
        </main>
      </>
    );
  }
  if (!findings) {
    return (
      <>
        <Masthead />
        <main className="page">
          <p className="empty">Loading the study…</p>
        </main>
      </>
    );
  }

  const { county, study_year: year, pooled, reference, deciles } = findings;
  const flagged = findings.municipalities.filter((m) => isFlag(m.reading));

  // The decile furthest from its local norm — computed, so the banner can never
  // assert a superlative the data doesn't support.
  const maxDecile = deciles.reduce((a, b) =>
    Math.abs(b.median_norm_ratio - 1) > Math.abs(a.median_norm_ratio - 1) ? b : a
  );
  const maxSubject =
    maxDecile.decile === 1
      ? `the lowest-priced tenth of homes (under $${maxDecile.price_max.toLocaleString()})`
      : maxDecile.decile === deciles.length
        ? `the highest-priced tenth of homes ($${maxDecile.price_min.toLocaleString()}+)`
        : `homes between $${maxDecile.price_min.toLocaleString()} and $${maxDecile.price_max.toLocaleString()}`;

  return (
    <>
      <Masthead />
      <main className="page">
        <header className="masthead">
          <h1>Assessment Equity</h1>
          <p className="dek">
            Wisconsin homeowners pay property taxes on what the assessor says their home
            is worth — so when assessments drift from real sale prices unevenly, the tax
            burden shifts. We compared every qualifying {year} home sale in {county}{" "}
            County with that home's {year} assessment, using the same IAAO sales-ratio
            statistics assessors use to audit themselves.
          </p>
        </header>

        <section className="reading" aria-label="Overall reading">
          <span className={`reading-badge ${isFlag(pooled.reading) ? "flag" : "ok"}`}>
            {isFlag(pooled.reading) ? pooled.reading.split(" — ")[0] : "WITHIN IAAO EQUITY BANDS"}
          </span>
          <p className="reading-text">
            Across {pooled.n.toLocaleString()} qualifying sales county-wide, assessment
            equity sits {isFlag(pooled.reading) ? "outside" : "inside"} the industry's
            acceptable bands — and the price group furthest from its local norm is{" "}
            {maxSubject}, assessed {pctVsPar(maxDecile.median_norm_ratio)} vs the
            typical level in their own municipality.
          </p>
        </section>

        <section className="kpi" aria-label="County-wide statistics">
          <div className="kpi-grid">
            <article className="kpi-card">
              <div className="kpi-label">Sales studied</div>
              <div className="kpi-value">{pooled.n.toLocaleString()}</div>
              <div className="kpi-sub">{year} arm's-length single-family sales</div>
            </article>
            <article className="kpi-card">
              <div className="kpi-label">Uniformity · COD</div>
              <div className="kpi-value">{pooled.cod.toFixed(1)}</div>
              <div className="kpi-sub">IAAO standard: ≤ {reference.cod_max_sfr.toFixed(0)}</div>
            </article>
            <article className="kpi-card">
              <div className="kpi-label">Regressivity · PRD</div>
              <div className="kpi-value">{pooled.prd.toFixed(3)}</div>
              <div className="kpi-sub">
                acceptable {reference.prd_band[0].toFixed(2)}–{reference.prd_band[1].toFixed(2)}
              </div>
            </article>
            <article className="kpi-card">
              <div className="kpi-label">Price bias · PRB</div>
              <div className="kpi-value">{signedFixed(pooled.prb)}</div>
              <div className="kpi-sub">t = {fixed(pooled.prb_t)} · band ±0.05</div>
            </article>
          </div>
        </section>

        <DecileChart
          deciles={deciles}
          gapPct={findings.bottom_vs_top_pct}
          year={year}
        />

        {findings.tax_shift?.deciles?.length > 0 && (() => {
          const ts = findings.tax_shift.deciles;
          const top = ts[ts.length - 1];
          const maxOver = ts.reduce((a, b) => (b.median_shift > a.median_shift ? b : a));
          return (
            <p className="decile-gap">
              In dollars: the bottom deciles carried effective tax rates around{" "}
              <b>{(ts[0].median_etr * 100).toFixed(2)}%</b> of sale price versus{" "}
              <b>{(top.median_etr * 100).toFixed(2)}%</b> for the most expensive tenth.
              Against a county-average rate, the median home around{" "}
              ${maxOver.median_price.toLocaleString()} paid{" "}
              <b>${maxOver.median_shift.toLocaleString()} more</b> per year, while the
              median top-decile home paid{" "}
              <b>${Math.abs(top.median_shift).toLocaleString()} less</b> — an
              illustration that blends assessment inequity with municipal rate
              differences (details and caveats in the findings memo).
            </p>
          );
        })()}

        <MuniTable
          rows={findings.municipalities}
          reference={reference}
          flaggedCount={flagged.length}
        />

        <SampleTable sample={findings.sample} year={year} />

        <footer className="colophon">
          Method: IAAO sales-ratio study. {year} arm's-length, entire-parcel,
          fee-paying single-family sales of ${findings.min_sale_price.toLocaleString()}+
          are matched to the same year's assessment roll; extreme ratios are IQR-trimmed
          within each municipality, and county-wide statistics are computed on
          municipality-normalized ratios (each sale's ratio divided by its
          municipality's median), so they compare equity — not revaluation timing.
          Sources: Wisconsin DOR Real Estate Transfer Returns; Wisconsin Statewide
          Parcel Map (local assessor values). Aggregate statistics only. Generated{" "}
          {findings.generated}. A Wausau Pilot &amp; Review civic-data tool.
        </footer>
      </main>
    </>
  );
}
