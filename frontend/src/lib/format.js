// Small formatting helpers. Pure functions, no state.

const USD = new Intl.NumberFormat("en-US", {
  style: "currency",
  currency: "USD",
  maximumFractionDigits: 0,
});

export function money(n) {
  return USD.format(n ?? 0);
}

// Compact dollars for axis ticks / dense labels: 226730 -> "$227k".
export function moneyCompact(n) {
  if (n >= 1_000_000) return `$${(n / 1_000_000).toFixed(1)}M`;
  if (n >= 1_000) return `$${Math.round(n / 1_000)}k`;
  return `$${n}`;
}

// A ratio (1.032) as a signed percent vs par: "+3.2%".
export function pctVsPar(ratio, digits = 1) {
  const n = ratio - 1;
  const sign = n > 0 ? "+" : n < 0 ? "−" : "";
  return `${sign}${(Math.abs(n) * 100).toFixed(digits)}%`;
}
