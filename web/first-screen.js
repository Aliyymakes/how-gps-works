// The first screen (design.md 2b). It draws and takes input; every number comes from Python.
// The only arithmetic here: Math.hypot for the position error, and the map's metres-to-pixels scaling.
import { trackPointerLight, loadSavedTheme } from "./theme.js";
import * as config from "./config.js";

const SVG = "http://www.w3.org/2000/svg";
const MAP_SIZE = 400; // the SVG viewBox is 400 by 400
const $ = (id) => document.getElementById(id);

const el = {
  status: $("status"), slider: $("clock"), sliderValue: $("clock-value"),
  errorValue: $("error-value"), badge: $("error-badge"), solve: $("solve"), reset: $("reset"),
  switches: $("switches"), lines: $("map-lines"), dot: $("map-dot"), caption: $("map-caption"),
  msgSlider: $("msg-slider"), msgReadout: $("msg-readout"), msgSolve: $("msg-solve"), msgSwitch: $("msg-switch"),
};

let callPython = null; // set when the bridge has loaded
let receiverPoint = null; // true receiver position, from Python
let allSatellites = []; // from Python, with ids from config.js
const state = { clockErrorS: 0, mode: "trusted", on: config.satellites.map(() => true) };
let running = false;
let rerun = false;

loadSavedTheme();
trackPointerLight();
setupControls();
drawTrueMark();
start();

// ---------- start up ----------

async function start() {
  let bridge;
  try {
    bridge = await import("./bridge.js"); // may be missing: a failure here must not break the page
    await bridge.loadMechanism((text) => { el.status.textContent = text; });
  } catch (error) {
    console.error(error);
    el.status.textContent = "The calculation engine could not load, so the controls stay off. Reload the page to try again.";
    return;
  }
  callPython = bridge.callPython;
  try {
    await buildScene();
  } catch (error) {
    console.error(error);
    el.status.textContent = "The calculation engine loaded but could not set up the satellites, so the controls stay off.";
    return;
  }
  el.status.textContent = "";
  setControlsDisabled(false);
  update("start");
}

async function buildScene() {
  const { lat_deg, lon_deg } = config.receiver;
  receiverPoint = await callPython("coords.latlon_to_xyz", [lat_deg, lon_deg]);
  if (receiverPoint.error) throw new Error(receiverPoint.error);
  allSatellites = [];
  for (const sat of config.satellites) {
    const point = await callPython("coords.satellite_from_sky", [lat_deg, lon_deg, sat.azimuth_deg, sat.elevation_deg]);
    if (point.error) throw new Error(point.error);
    allSatellites.push({ id: sat.id, ...point });
  }
}

// ---------- controls ----------

function setupControls() {
  const { min_s, max_s, step_s } = config.clockSlider;
  // The slider counts steps (whole numbers), so there are no floating point surprises.
  el.slider.min = 0;
  el.slider.max = Math.round((max_s - min_s) / step_s);
  el.slider.step = 1;
  el.slider.value = 0;
  showClockValue();

  config.satellites.forEach((sat, index) => {
    const label = document.createElement("label");
    label.className = "toggle";
    label.innerHTML = '<input type="checkbox" checked disabled><span class="toggle-track"></span>';
    label.append(`Satellite ${sat.id}`);
    label.querySelector("input").addEventListener("change", (event) => {
      state.on[index] = event.target.checked;
      update("switch");
    });
    el.switches.append(label);
  });

  el.slider.addEventListener("input", () => {
    state.clockErrorS = Number(el.slider.value) * config.clockSlider.step_s + config.clockSlider.min_s;
    state.mode = "trusted"; // moving the slider again goes back to trusting the clock
    showClockValue();
    update("slider");
  });
  el.solve.addEventListener("click", () => {
    state.mode = "solved";
    update("solve");
  });
  el.reset.addEventListener("click", resetAll);
  setControlsDisabled(true);
}

function setControlsDisabled(disabled) {
  el.slider.disabled = disabled;
  el.solve.disabled = disabled;
  el.reset.disabled = disabled;
  el.switches.querySelectorAll("input").forEach((box) => { box.disabled = disabled; });
}

function resetAll() {
  state.clockErrorS = 0;
  state.mode = "trusted";
  state.on = config.satellites.map(() => true);
  el.slider.value = 0;
  el.switches.querySelectorAll("input").forEach((box) => { box.checked = true; });
  showClockValue();
  update("reset");
}

function showClockValue() {
  el.sliderValue.textContent = formatMicroseconds(state.clockErrorS);
  el.slider.setAttribute("aria-valuetext", el.sliderValue.textContent);
}

// ---------- one run: ask Python, then draw ----------

// Python calls are async. If one is running, remember that a newer run is wanted and do it once after.
async function update(cause) {
  if (!callPython) return;
  if (running) { rerun = true; return; }
  running = true;
  try {
    do {
      rerun = false;
      try {
        await runOnce(cause);
      } catch (error) {
        console.error(error);
        el.msgSolve.textContent = "Something went wrong in the calculation. Press Reset to start again.";
      }
    } while (rerun);
  } finally {
    running = false;
  }
}

async function runOnce(cause) {
  const solveClock = state.mode === "solved";
  const sats = allSatellites.filter((_, i) => state.on[i]);
  const slot = { slider: el.msgSlider, solve: el.msgSolve, switch: el.msgSwitch }[cause] || el.msgSolve;
  clearMessages();

  if (solveClock && sats.length < 4) {
    // Do not call the solver: it cannot work, and the page says why. There is no fix to show.
    el.msgSwitch.textContent = "Four things are unknown (east, north, up and the clock), but three satellites give only three measurements.";
    hideSwitchedOffLines(sats);
    showNoFix();
    return;
  }

  const ranges = await callPython("scenario.make_pseudoranges", [receiverPoint, sats, state.clockErrorS]);
  if (failed(ranges, slot)) return;
  const solution = await callPython("solver.solve_position", [sats, ranges, solveClock]);
  if (failed(solution, slot)) return;
  const { lat_deg, lon_deg } = config.receiver;
  const point = { x_m: solution.x_m, y_m: solution.y_m, z_m: solution.z_m };
  const local = await callPython("mapview.to_local", [lat_deg, lon_deg, point]);
  if (failed(local, slot)) return;
  const assumedClockS = solveClock ? solution.clock_error_s : 0;
  const lines = await callPython("mapview.distance_lines", [lat_deg, lon_deg, sats, ranges, assumedClockS, config.mapHalfWidthM, config.lineSamples]);
  if (failed(lines, slot)) return;

  const errorM = Math.hypot(local.east_m, local.north_m, local.up_m);
  requestAnimationFrame(() => draw(lines, local, errorM));
  showWords(solution, errorM, solveClock);
}

function failed(result, slot) {
  if (!result || !result.error) return false;
  slot.textContent = result.error; // Python's own plain sentence
  showNoFix();
  return true;
}

function clearMessages() {
  for (const node of [el.msgSlider, el.msgReadout, el.msgSolve, el.msgSwitch]) node.textContent = "";
}

// ---------- words ----------

function showWords(solution, errorM, solveClock) {
  if (solveClock) {
    el.msgSolve.textContent = describeClock(solution.clock_error_s);
  } else {
    el.msgReadout.textContent = errorLevel(errorM) === "ok"
      ? "The distance lines meet at the dot."
      : "The phone trusts its clock, so the distance lines miss each other.";
  }
  if (solution.converged === false) el.msgReadout.textContent = "The solver did not settle on an answer.";
}

function describeClock(clockErrorS) {
  const shown = formatMicroseconds(Math.abs(clockErrorS));
  if (shown.startsWith("0.00")) return "The phone found its clock is right.";
  return `The phone found its clock is ${shown} ${clockErrorS > 0 ? "fast" : "slow"}.`;
}

function formatMicroseconds(seconds) {
  return `${(seconds * 1e6).toFixed(2)} µs`;
}

// ---------- drawing ----------

function errorLevel(errorM) {
  if (errorM < config.errorLimits.ok_m) return "ok";
  if (errorM < config.errorLimits.warn_m) return "warn";
  return "bad";
}

const levelWords = { ok: "Good fix", warn: "Fix is off", bad: "Fix is far off" };

function toPixelX(east_m) { return (east_m + config.mapHalfWidthM) * MAP_SIZE / (2 * config.mapHalfWidthM); }
function toPixelY(north_m) { return (config.mapHalfWidthM - north_m) * MAP_SIZE / (2 * config.mapHalfWidthM); }

function draw(lines, local, errorM) {
  drawLines(lines);
  const level = errorLevel(errorM);
  const x = toPixelX(local.east_m);
  const y = toPixelY(local.north_m);
  const inside = x >= 0 && x <= MAP_SIZE && y >= 0 && y <= MAP_SIZE;
  el.dot.style.display = inside ? "" : "none";
  el.dot.firstElementChild.setAttribute("cx", x);
  el.dot.firstElementChild.setAttribute("cy", y);
  el.dot.setAttribute("class", `is-${level}`);
  el.errorValue.textContent = `${new Intl.NumberFormat("en", { maximumFractionDigits: 1 }).format(errorM)} m`;
  el.badge.hidden = false;
  el.badge.className = `badge is-${level}`;
  el.badge.textContent = levelWords[level];
  el.caption.textContent = inside
    ? `The map is about ${config.mapHalfWidthM * 2 / 1000} km wide. North is up.`
    : "The phone's position is off the edge of this map.";
}

// When the page refuses to solve: no metres value, no badge, no dot (issue #40).
// Done in the next frame so it lands after any drawing an earlier run has already queued.
function showNoFix() {
  requestAnimationFrame(() => {
    el.dot.style.display = "none";
    el.errorValue.textContent = "–";
    el.badge.hidden = true;
  });
}

function drawLines(lines) {
  const known = new Map([...el.lines.children].map((node) => [node.dataset.id, node]));
  const wanted = new Set(lines.map((line) => line.id));
  for (const line of lines) {
    let node = known.get(line.id);
    if (!node) {
      node = document.createElementNS(SVG, "polyline");
      node.dataset.id = line.id;
      node.setAttribute("class", "map-line");
      el.lines.append(node);
    }
    node.setAttribute("points", line.points.map(([e, n]) => `${toPixelX(e)},${toPixelY(n)}`).join(" "));
    node.classList.toggle("is-hidden", !line.inside);
  }
  // A switched-off satellite is not in the list: fade its line out.
  for (const [id, node] of known) if (!wanted.has(id)) node.classList.add("is-hidden");
}

// Fade out the lines of satellites that are switched off, keeping the rest as they were.
function hideSwitchedOffLines(sats) {
  const onIds = new Set(sats.map((sat) => sat.id));
  for (const node of el.lines.children) if (!onIds.has(node.dataset.id)) node.classList.add("is-hidden");
}

// The true position is always the middle of the map.
function drawTrueMark() {
  const middle = MAP_SIZE / 2;
  const group = $("map-true");
  for (const [x1, y1, x2, y2] of [[middle - 8, middle, middle + 8, middle], [middle, middle - 8, middle, middle + 8]]) {
    const line = document.createElementNS(SVG, "line");
    for (const [name, value] of Object.entries({ x1, y1, x2, y2 })) line.setAttribute(name, value);
    group.append(line);
  }
}
