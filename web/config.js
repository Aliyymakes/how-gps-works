// Every placeholder number for the first screen lives here (design.md 2b).
// All of these are provisional until Icarus confirms them.

// Where the phone really is. Jakarta.
export const receiver = { lat_deg: -6.2, lon_deg: 106.8 }; // placeholder, provisional

// Four satellites spread around the sky. Elevation stays between 15 and 65 degrees.
export const satellites = [ // placeholder, provisional
  { id: "1", azimuth_deg: 30, elevation_deg: 60 },
  { id: "2", azimuth_deg: 120, elevation_deg: 35 },
  { id: "3", azimuth_deg: 210, elevation_deg: 20 },
  { id: "4", azimuth_deg: 300, elevation_deg: 45 },
];

// Ground map: it shows a square from -half to +half metres, east and north.
export const mapHalfWidthM = 1000; // placeholder, provisional
export const lineSamples = 40; // points per distance line, placeholder

// Clock error slider, stored in seconds. 0 to 3 microseconds in steps of 0.05 microseconds.
export const clockSlider = { min_s: 0, max_s: 3e-6, step_s: 5e-8 }; // placeholder, provisional

// Error colour thresholds in metres: below ok is "ok", below warn is "warn", else "bad".
export const errorLimits = { ok_m: 10, warn_m: 100 }; // placeholder, provisional
