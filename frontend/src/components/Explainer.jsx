import { pctVsPar } from "../lib/format.js";

// Plain-English on-ramp: what an assessment is, why it decides your tax bill,
// and how comparing sales to assessments reveals unfairness. Sits before any
// statistics so a reader who stops here still understands the story. The
// glossary below it defines each statistic USING the study's own numbers, so
// the definitions stay current with every data release.
export function HowItWorks({ county, year }) {
  return (
    <section className="explain" aria-label="How this works">
      <h2>How this works — the 90-second version</h2>
      <div className="explain-cards">
        <div className="explain-card">
          <span className="explain-step">1</span>
          <h3>Your assessment is your slice of the pie</h3>
          <p>
            Your city, school district, and county decide the total property-tax levy.
            Your <b>assessment</b> — the assessor's estimate of your home's value —
            only decides your <i>share</i> of it. Assessed too high relative to your
            neighbors, and you quietly pay part of their bill.
          </p>
        </div>
        <div className="explain-card">
          <span className="explain-step">2</span>
          <h3>Home sales are the answer key</h3>
          <p>
            When a home sells, the market states its real value. Divide the assessment
            by the sale price and you get that home's <b>assessment ratio</b>: a house
            that sold for $200,000 while assessed at $180,000 has a ratio of 0.90. We
            computed this ratio for every qualifying {year} sale in {county} County.
          </p>
        </div>
        <div className="explain-card">
          <span className="explain-step">3</span>
          <h3>Fair means the same ratio for everyone</h3>
          <p>
            The exact ratio doesn't matter — municipalities revalue on different
            schedules, so levels differ by design. What matters is that cheap and
            expensive homes in the <i>same community</i> get the <b>same</b> ratio.
            When cheaper homes consistently score higher ratios, the tax load tilts
            onto the people least able to carry it. Assessors call that{" "}
            <b>regressive</b>, and their own industry group (the IAAO) publishes
            yardsticks for it — the ones we use below.
          </p>
        </div>
      </div>
    </section>
  );
}

// The statistics, defined with the study's own numbers filled in.
export function Definitions({ pooled, reference }) {
  const [prdLo, prdHi] = reference.prd_band;
  return (
    <section className="gloss" aria-label="Definitions">
      <details>
        <summary>
          <h2>The four yardsticks, defined</h2>
          <span className="gloss-hint">plain-English definitions of every statistic on this page</span>
        </summary>
        <dl className="gloss-list">
          <div className="gloss-item">
            <dt>Median ratio <span className="gloss-val">ours: {pooled.n.toLocaleString()} sales, by municipality above</span></dt>
            <dd>
              Line all the ratios up and take the middle one — the community's overall
              assessment <i>level</i>. A median of 0.93 means the typical home is
              assessed at 93% of what homes actually sell for. A low level isn't unfair
              by itself; it mostly reflects how long since the last revaluation.
            </dd>
          </div>
          <div className="gloss-item">
            <dt>COD — uniformity <span className="gloss-val">ours: {pooled.cod.toFixed(1)} · IAAO says ≤ {reference.cod_max_sfr.toFixed(0)}</span></dt>
            <dd>
              The Coefficient of Dispersion asks: how far does a typical home's ratio
              stray from the middle? A COD of {pooled.cod.toFixed(0)} means roughly{" "}
              {pooled.cod.toFixed(0)}% — think of it as the size of the assessment
              lottery. Zero would mean every home assessed at exactly the same share
              of its value.
            </dd>
          </div>
          <div className="gloss-item">
            <dt>PRD — the tilt test <span className="gloss-val">ours: {pooled.prd.toFixed(3)} · acceptable {prdLo.toFixed(2)}–{prdHi.toFixed(2)}</span></dt>
            <dd>
              The Price-Related Differential compares the plain average ratio with a
              dollar-weighted one. If expensive homes are getting a break, the
              dollar-weighted average sags and the PRD rises above 1. Above{" "}
              {prdHi.toFixed(2)} is the industry's line for a regressive tilt.
            </dd>
          </div>
          <div className="gloss-item">
            <dt>PRB — the slope test <span className="gloss-val">ours: {(pooled.prb >= 0 ? "+" : "−") + Math.abs(pooled.prb).toFixed(3)} · acceptable ±0.05</span></dt>
            <dd>
              The Price-Related Bias measures how the assessment level changes as home
              value doubles. A PRB of −0.05 would mean each doubling of value shaves
              about 5% off the assessment level — a systematic discount for expensive
              homes. Between −0.05 and +0.05, with no strong statistical signal, counts
              as fair.
            </dd>
          </div>
          <div className="gloss-item">
            <dt>Normalized ratio <span className="gloss-val">used in the chart above</span></dt>
            <dd>
              Each home's ratio divided by the <i>typical</i> ratio in its own city,
              village, or town. 1.00 means "assessed exactly like the typical home in
              your community"; {pctVsPar(1.08)} means 8% above it. Comparing within
              communities is what makes different revaluation schedules cancel out.
            </dd>
          </div>
          <div className="gloss-item">
            <dt>Decile</dt>
            <dd>
              Sort every sale by price and cut the list into ten equal groups. Decile 1
              is the cheapest tenth of homes sold; decile 10 the most expensive tenth.
            </dd>
          </div>
        </dl>
      </details>
    </section>
  );
}
