import { Component, useEffect, useState } from "react";
import Masthead from "./components/Masthead.jsx";
import { HowItWorks, Definitions } from "./components/Explainer.jsx";
import DecileChart from "./components/DecileChart.jsx";
import MuniTable from "./components/MuniTable.jsx";
import SampleTable from "./components/SampleTable.jsx";
import YearOverYear from "./components/YearOverYear.jsx";
import { pctVsPar, fixed, signedFixed, range } from "./lib/format.js";

// Is a verdict string inside the IAAO bands, or a flag (REGRESSIVE/PROGRESSIVE)?
const isFlag = (reading) => !reading.startsWith("within");

const BASE = import.meta.env.BASE_URL;
// Oldest feed contract this build understands (analysis/study.py FEED_SCHEMA).
const MIN_SCHEMA = 2;

// no-cache = always revalidate with the server (ETag), so a fresh deploy's
// index.json is picked up immediately instead of after Pages' cache window.
async function getJSON(path, { optional = false } = {}) {
  const r = await fetch(`${BASE}${path}`, { cache: "no-cache" });
  if (!r.ok) {
    if (optional) return null;
    throw new Error(`${path}: ${r.status}`);
  }
  return r.json();
}

// The feed is generated code, but a truncated, half-written, or out-of-date
// file must fail with a readable message rather than a blank page.
function validate(f) {
  const need = ["study_year", "county", "reference", "sample", "municipalities", "pooled", "deciles"];
  const missing = need.filter((k) => f?.[k] == null);
  if (missing.length) throw new Error(`findings feed is missing: ${missing.join(", ")}`);
  if (!Array.isArray(f.deciles) || f.deciles.length < 2) throw new Error("findings feed has no deciles");
  if ((f.schema ?? 0) < MIN_SCHEMA) throw new Error(`findings feed schema ${f.schema ?? "none"} is older than ${MIN_SCHEMA}`);
  return f;
}

// A render-time crash (an unexpected null deep in a feed) would otherwise
// unmount the whole page. Catch it and show the same friendly message.
class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { error: null };
  }
  static getDerivedStateFromError(error) {
    return { error };
  }
  render() {
    if (this.state.error) {
      return (
        <p className="empty">
          Couldn’t display the study right now.{" "}
          <span className="empty-detail">({String(this.state.error.message || this.state.error)})</span>
        </p>
      );
    }
    return this.props.children;
  }
}

function Shell({ children }) {
  return (
    <>
      <Masthead />
      <main className="page">{children}</main>
    </>
  );
}

export default function App() {
  const [index, setIndex] = useState(null);
  const [year, setYear] = useState(null);
  const [data, setData] = useState(null); // { findings, previous, crosscheck }
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Entry: index.json names the years; the latest is the default view.
  useEffect(() => {
    getJSON("index.json")
      .then((ix) => {
        if (!ix?.years?.length) throw new Error("index.json lists no years");
        setIndex(ix);
        setYear(ix.latest);
      })
      .catch((e) => setError(e.message));
  }, []);

  // Per year: the findings, the prior year (for what-changed), and the optional
  // DOR cross-check. A year switch holds the previous render dimmed — no flash.
  useEffect(() => {
    if (!index || year == null) return;
    let alive = true;
    setLoading(true);
    const years = index.years;
    const prevYear = years[years.indexOf(year) - 1];
    // The prior year and the cross-check are enrichments: if either is missing
    // or malformed the page still renders, without that section.
    const soft = (p) => p.catch(() => null);
    Promise.all([
      getJSON(`findings-${year}.json`).then(validate),
      prevYear ? soft(getJSON(`findings-${prevYear}.json`, { optional: true }).then((f) => f && validate(f))) : null,
      soft(getJSON(`crosscheck-${year}.json`, { optional: true }).then((c) => (c?.municipalities ? c : null))),
    ])
      .then(([findings, previous, crosscheck]) => {
        if (!alive) return;
        setData({ findings, previous, crosscheck });
        setLoading(false);
      })
      .catch((e) => alive && setError(e.message));
    return () => {
      alive = false;
    };
  }, [index, year]);

  if (error) {
    return (
      <Shell>
        <p className="empty">
          Couldn’t load the study right now. <span className="empty-detail">({error})</span>
        </p>
      </Shell>
    );
  }
  if (!data) {
    return (
      <Shell>
        <p className="empty">Loading the study…</p>
      </Shell>
    );
  }

  const { findings, previous, crosscheck } = data;
  const { county, study_year: shownYear, pooled, reference, deciles } = findings;
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
  const bottomCI = findings.bottom_decile_ci;

  return (
    <Shell>
      <ErrorBoundary>
      <div className={loading ? "study is-loading" : "study"} aria-busy={loading}>
        <header className="masthead">
          <div className="masthead-top">
            <h1>Assessment Equity</h1>
            {index.years.length > 1 && (
              <div className="seg" role="group" aria-label="Study year">
                {index.years.map((y) => (
                  <button
                    key={y}
                    type="button"
                    className={y === year ? "active" : ""}
                    aria-pressed={y === year}
                    onClick={() => setYear(y)}
                  >
                    {y}
                  </button>
                ))}
              </div>
            )}
          </div>
          <p className="dek">
            Wisconsin homeowners pay property taxes on what the assessor says their home
            is worth — so when assessments drift from real sale prices unevenly, the tax
            burden shifts. We compared every qualifying {shownYear} home sale in {county}{" "}
            County with that home's {shownYear} assessment, using the same IAAO
            sales-ratio statistics assessors use to audit themselves.
          </p>
        </header>

        <HowItWorks county={county} year={shownYear} />

        <section className="reading" aria-label="Overall reading">
          <div className="reading-hero">
            <span className="reading-hero-num">{pctVsPar(maxDecile.median_norm_ratio)}</span>
            <span className="reading-hero-label">
              {maxDecile.decile === 1 ? "cheapest tenth of homes" : `decile ${maxDecile.decile}`}
              <br />
              vs the local norm
              {maxDecile.decile === 1 && bottomCI && (
                <>
                  <br />
                  <span className="ci">95% CI {pctVsPar(bottomCI[0])} to {pctVsPar(bottomCI[1])}</span>
                </>
              )}
            </span>
          </div>
          <div className="reading-body">
            <span className={`reading-badge ${isFlag(pooled.reading) ? "flag" : "ok"}`}>
              {isFlag(pooled.reading) ? pooled.reading.split(" — ")[0] : "WITHIN IAAO EQUITY BANDS"}
            </span>
            {pooled.uniformity_ok === false && (
              <span className="reading-badge warn">COD ABOVE STANDARD</span>
            )}
            <p className="reading-text">
              Across {pooled.n.toLocaleString()} qualifying {shownYear} sales county-wide,
              assessment equity sits {isFlag(pooled.reading) ? "outside" : "inside"} the
              industry's acceptable bands — and the price group furthest from its local
              norm is {maxSubject}, assessed {pctVsPar(maxDecile.median_norm_ratio)} vs the
              typical level in their own municipality.
            </p>
          </div>
        </section>

        <section className="kpi" aria-label="County-wide statistics">
          <div className="kpi-grid">
            <article className="kpi-card">
              <div className="kpi-label">Sales studied</div>
              <div className="kpi-value">{pooled.n.toLocaleString()}</div>
              <div className="kpi-sub">{shownYear} arm's-length single-family sales</div>
              <div className="kpi-plain">every qualifying open-market home sale, matched to its assessment</div>
            </article>
            <article className={`kpi-card${pooled.uniformity_ok === false ? " kpi-warn" : ""}`}>
              <div className="kpi-label">Uniformity · COD</div>
              <div className="kpi-value">{pooled.cod.toFixed(1)}</div>
              <div className="kpi-sub">
                IAAO standard: ≤ {reference.cod_max_sfr.toFixed(0)}
                {pooled.cod_ci && <span className="ci"> · 95% CI {range(pooled.cod_ci, 1)}</span>}
              </div>
              <div className="kpi-plain">the size of the assessment lottery — a typical home's ratio sits ~{pooled.cod.toFixed(0)}% from the middle</div>
            </article>
            <article className="kpi-card">
              <div className="kpi-label">Regressivity · PRD</div>
              <div className="kpi-value">{pooled.prd.toFixed(3)}</div>
              <div className="kpi-sub">
                acceptable {reference.prd_band[0].toFixed(2)}–{reference.prd_band[1].toFixed(2)}
                {pooled.prd_ci && <span className="ci"> · 95% CI {range(pooled.prd_ci, 3)}</span>}
              </div>
              <div className="kpi-plain">above {reference.prd_band[1].toFixed(2)} would mean cheaper homes carry more than their share</div>
            </article>
            <article className="kpi-card">
              <div className="kpi-label">Price bias · PRB</div>
              <div className="kpi-value">{signedFixed(pooled.prb)}</div>
              <div className="kpi-sub">t = {fixed(pooled.prb_t)} · band ±0.05</div>
              <div className="kpi-plain">how the assessment level shifts each time home value doubles</div>
            </article>
          </div>
        </section>

        {previous && <YearOverYear current={findings} previous={previous} />}

        <Definitions pooled={pooled} reference={reference} />

        <DecileChart
          deciles={deciles}
          gapPct={findings.bottom_vs_top_pct}
          bottomCI={bottomCI}
          year={shownYear}
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
          crosscheck={crosscheck}
        />

        <SampleTable sample={findings.sample} year={shownYear} />

        <footer className="colophon">
          Method: IAAO sales-ratio study. {shownYear} arm's-length, entire-parcel,
          fee-paying single-family sales of ${findings.min_sale_price.toLocaleString()}+
          are matched to the same year's assessment roll; extreme ratios are IQR-trimmed
          within each municipality, and county-wide statistics are computed on
          municipality-normalized ratios (each sale's ratio divided by its
          municipality's median), so they compare equity — not revaluation timing.
          Confidence intervals are percentile bootstraps (1,000 resamples). Sources:
          Wisconsin DOR Real Estate Transfer Returns; Wisconsin Statewide Parcel Map
          (local assessor values); DOR Summary of Aggregate Ratios for the cross-check.
          Aggregate statistics only. Generated {findings.generated}. A Wausau Pilot &amp;
          Review civic-data tool.
        </footer>
      </div>
      </ErrorBoundary>
    </Shell>
  );
}
