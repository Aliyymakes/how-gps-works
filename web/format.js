// One rule for every metres readout: one decimal place below 100 m, whole metres from 100 m up,
// always with a thousands separator. The space before "m" cannot break across lines.
export function formatMetres(m) {
  const digits = new Intl.NumberFormat("en", { maximumFractionDigits: m < 100 ? 1 : 0 }).format(m);
  return `${digits} m`;
}
