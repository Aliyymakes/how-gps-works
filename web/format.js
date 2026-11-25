// One rule for every metres readout: one decimal place below 100 m, whole metres from 100 m up,
// always with a thousands separator. The space before "m" cannot break across lines.
export function formatMetres(m) {
  const digits = new Intl.NumberFormat("en", { maximumFractionDigits: m < 100 ? 1 : 0 }).format(m);
  return `${digits} m`;
}

// Rough distances for numbers that must never look exact (gotchas: "about 11 km"). Under 1000 m the metres
// rule above; from 1 km one decimal ("2.8 km"); from 10 km whole kilometres ("11 km"). The word "about" goes in the label.
export function formatRoughDistance(m) {
  if (m < 1000) return formatMetres(m);
  const km = m / 1000;
  return `${new Intl.NumberFormat("en", { maximumFractionDigits: km < 10 ? 1 : 0 }).format(km)} km`;
}

// Clock digits written "HH:00:00.000 000". Whole hours come from the slider; the six decimals are millionths of a
// second. The ground row has none; the satellite row shows the gap in whole microseconds (for example "000 038").
export function formatClockDigits(hours, gapMicroseconds) {
  const start = `${String(hours).padStart(2, "0")}:00:00.`;
  const gap = String(gapMicroseconds).padStart(6, "0");
  return { ground: `${start}000 000`, satellite: `${start}${gap.slice(0, 3)} ${gap.slice(3)}` };
}
