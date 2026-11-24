// Every placeholder number for the first screen lives here (design.md 2b).
// All of these are provisional until Icarus confirms them.

// Where the phone really is. Jakarta.
export const receiver = { lat_deg: -6.2, lon_deg: 106.8 }; // placeholder, provisional

// Four satellites spread around the sky. Elevation stays between 15 and 65 degrees.
// Chosen so no two distance lines are parallel and PDOP stays under 4 (decisions.md, #43).
export const satellites = [ // placeholder, provisional
  { id: "1", azimuth_deg: 10, elevation_deg: 60 },
  { id: "2", azimuth_deg: 100, elevation_deg: 35 },
  { id: "3", azimuth_deg: 235, elevation_deg: 20 },
  { id: "4", azimuth_deg: 325, elevation_deg: 20 },
];

// Ground map: it shows a square from -half to +half metres, east and north.
export const mapHalfWidthM = 1000; // placeholder, provisional
export const lineSamples = 40; // points per distance line, placeholder

// Clock error slider, stored in seconds. 0 to 3 microseconds in steps of 0.05 microseconds.
export const clockSlider = { min_s: 0, max_s: 3e-6, step_s: 5e-8 }; // placeholder, provisional

// Error colour thresholds in metres: below ok is "ok", below warn is "warn", else "bad".
export const errorLimits = { ok_m: 10, warn_m: 100 }; // placeholder, provisional

// Rung 4 (relativity) section. The satellites and receiver above are reused.
export const relativitySlider = { min_h: 0, max_h: 24, step_h: 1, start_h: 24 }; // placeholder, provisional: hours of drift. Starts at one day so the effect is already showing.
// The two maps in this section show a square 40 km wide (-20000 to +20000 m). With the clock trusted at 24 h all four
// distance lines stay on a map this wide; on a 20 km wide map two would leave it.
export const relativityMapHalfWidthM = 20000; // placeholder, provisional
// Zero, so at 0 hours both ways of solving agree and show 0 m. A 1 microsecond phone clock error would put
// about 500 m on the "trusted clock" result before any drift happens.
export const relativityPhoneClockErrorS = 0; // placeholder, provisional: the phone's own clock error
