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

// "11.3–13.1" — a [lo, hi] interval at a fixed precision.
export function range(ci, digits = 1) {
  if (!Array.isArray(ci) || ci.length !== 2) return "";
  return `${fixed(ci[0], digits)}–${fixed(ci[1], digits)}`;
}

// Fixed-point with a typographic minus (−, not the ASCII hyphen toFixed emits).
export function fixed(n, digits = 1) {
  return (n < 0 ? "−" : "") + Math.abs(n).toFixed(digits);
}

// Fixed-point with an explicit sign: "+0.002" / "−0.011".
export function signedFixed(n, digits = 3) {
  return (n > 0 ? "+" : n < 0 ? "−" : "") + Math.abs(n).toFixed(digits);
}
