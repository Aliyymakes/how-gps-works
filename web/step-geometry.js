// Rung 2: geometry (design.md 2a). It draws and takes input; every number comes from Python.
// The only arithmetic here: Math.hypot for the position error, the slider-to-angle blend,
// and the sky drawing scale.
import { whenPythonReady } from "./startup.js";
import { say } from "./say.js";
import { formatMetres } from "./format.js";

// Every tunable number for this step. All of these are provisional until Icarus confirms them.
export const geometryConfig = {
  receiver: { lat_deg: -6.2, lon_deg: 106.8 }, // placeholder, provisional (Jakarta, as on the first screen)
  // Four satellites spread around the sky: one nearly overhead, three low and 120 degrees apart.
  // Elevation stays between 15 and 80 degrees.
  spread: [ // placeholder, provisional
    { id: "1", azimuth_deg: 30, elevation_deg: 80 },
    { id: "2", azimuth_deg: 90, elevation_deg: 20 },
    { id: "3", azimuth_deg: 210, elevation_deg: 20 },
    { id: "4", azimuth_deg: 330, elevation_deg: 20 },
  ],
  // The same four satellites bunched into one patch of sky, all within about 10 degrees.
  bunched: [ // placeholder, provisional
    { id: "1", azimuth_deg: 40, elevation_deg: 44 },
    { id: "2", azimuth_deg: 44, elevation_deg: 48 },
    { id: "3", azimuth_deg: 48, elevation_deg: 52 },
    { id: "4", azimuth_deg: 50, elevation_deg: 46 },
  ],
  clock_error_s: 1e-6, // placeholder, provisional: the phone's clock is 1 microsecond ahead
  noise_m: 3, // placeholder, provisional: measurement noise, standard deviation in metres
  seed: 1, // placeholder, provisional: the same seed every run, so only the layout changes
  slider_steps: 100, // placeholder, provisional: 0 = spread, 100 = bunched
  error_limits: { ok_m: 10, warn_m: 100 }, // placeholder, provisional: below ok is "ok", below warn is "warn", else "bad"
};

const SVG = "http://www.w3.org/2000/svg";
const SKY_SIZE = 240; // the sky SVG viewBox is 240 by 240
const SKY_RADIUS = 110; // horizon circle radius in that box
const SKY_LABEL = "Sky diagram. The edge is the horizon and the centre is straight overhead. Four dots are the satellites.";
const LEVEL_WORDS = { ok: "Good fix", warn: "Fix is off", bad: "Fix is far off" };

// Layout for this section only. Colours, fonts and radii come from theme.css.
const STYLE = `
.geo { display: grid; grid-template-columns: minmax(0, 1fr); gap: var(--s-5); }
.geo-grid { display: grid; grid-template-columns: minmax(0, 1fr); gap: var(--s-5); }
@media (min-width: 760px) { .geo-grid { grid-template-columns: 1fr 1fr; align-items: start; } }
.geo-stack { display: grid; grid-template-columns: minmax(0, 1fr); gap: var(--s-4); }
.geo-sky { width: 100%; max-width: 320px; aspect-ratio: 1; display: block; margin: 0 auto; }
.geo-sky .sky-sat { transition: none; }
.geo-sky text { fill: var(--text-muted); font: 500 var(--text-xs) var(--font-mono); }
.geo-note { font-size: var(--text-sm); color: var(--text-muted); min-height: 1.5em; }
.geo-note:empty { min-height: 0; }
.geo-note[data-id="msg-slider"]:empty { min-height: 1.5em; }
.geo h3.label { margin-bottom: var(--s-3); }
.geo-highlight { border-color: var(--accent); padding: var(--s-4); }
.geo-readout { padding: var(--s-4); display: grid; grid-template-columns: minmax(0, 1fr); gap: var(--s-2); }
.geo-big { font-size: var(--text-xl); }
.geo .badge[hidden] { display: none; }
.geo .hint { font-size: var(--text-sm); font-weight: 500; color: var(--text); }
.geo .slider-head { flex-wrap: wrap; column-gap: var(--s-3); }
.geo-closing { max-width: 60ch; }
.geo .btn { touch-action: manipulation; }
.geo input[type="range"] { touch-action: pan-y; }
.geo .btn:disabled, .geo input[type="range"]:disabled { opacity: 0.4; cursor: not-allowed; }
.geo .btn:disabled:hover { border-color: var(--line-strong); }
`;

const PAGE = `
<div class="geo">
  <header class="geo-stack" style="gap: var(--s-2)">
    <h2>Does it matter where the satellites are?</h2>
    <p class="muted">Same four satellites, same clock error, same noise. Only the layout changes.</p>
  </header>
  <div class="geo-grid">
    <section class="card" aria-labelledby="geo-sky-title">
      <h3 class="label" id="geo-sky-title">Sky, seen from below</h3>
      <svg class="geo-sky" data-id="sky" viewBox="0 0 ${SKY_SIZE} ${SKY_SIZE}" role="img"
           aria-label="${SKY_LABEL}"></svg>
      <p class="geo-note" style="margin-top: var(--s-3)">Edge is the horizon, centre is straight overhead.</p>
    </section>
    <section class="card geo-stack" aria-label="Controls and results">
      <p class="geo-note" data-id="status" role="status" aria-live="polite">Loading the maths…</p>
      <p class="hint" data-id="hint" hidden>Drag this slider to push the four satellites into one patch of sky.</p>
      <div class="slider inset geo-highlight">
        <div class="slider-head">
          <label for="geo-bunch">Bunch the satellites</label>
          <span class="num" data-id="slider-value">0 % bunched</span>
        </div>
        <input id="geo-bunch" data-id="slider" type="range" value="0" disabled>
        <p class="geo-note" data-id="msg-slider" role="status" aria-live="polite"></p>
      </div>
      <div class="inset geo-readout">
        <span class="label">DOP</span>
        <span class="num geo-big" data-id="dop">–</span>
        <p class="geo-note" style="min-height: 0">DOP (dilution of precision): how much the satellites' layout multiplies measurement errors. Lower is better.</p>
        <p class="geo-note" data-id="msg-dop" role="status" aria-live="polite"></p>
      </div>
      <div class="inset geo-readout">
        <span class="label">Position off by</span>
        <span class="num geo-big" data-id="error">–</span>
        <div><span class="badge is-ok" data-id="badge" hidden></span></div>
        <p class="geo-note" data-id="msg-error" role="status" aria-live="polite"></p>
      </div>
      <div>
        <button class="btn" data-id="reset" type="button" disabled>Reset</button>
        <p class="geo-note" style="margin-top: var(--s-2)" data-id="msg-reset" role="status" aria-live="polite"></p>
      </div>
    </section>
  </div>
  <p class="geo-closing">Spread out, the same errors barely move the fix. Bunched, they multiply. But all of this error began with time, so next: how does the phone measure it at all?</p>
</div>`;

export function mountGeometryStep(container) {
  if (!document.getElementById("geo-style")) {
    const style = document.createElement("style");
    style.id = "geo-style";
    style.textContent = STYLE;
    document.head.append(style);
  }
  container.innerHTML = PAGE;
  const $ = (id) => container.querySelector(`[data-id="${id}"]`);
  const el = {
    status: $("status"), hint: $("hint"), sky: $("sky"), slider: $("slider"), sliderValue: $("slider-value"),
    msgSlider: $("msg-slider"), dop: $("dop"), msgDop: $("msg-dop"),
    error: $("error"), badge: $("badge"), msgError: $("msg-error"), reset: $("reset"), msgReset: $("msg-reset"),
  };
  const { receiver, spread, bunched } = geometryConfig;

  let callPython = null; // set when the bridge has loaded
  let receiverPoint = null; // true receiver position, from Python
  let running = false;
  let rerun = false;
  let hintDone = false; // once the user has touched the slider, the hint stays hidden

  el.slider.min = 0;
  el.slider.max = geometryConfig.slider_steps;
  el.slider.step = 1;
  el.slider.value = 0;
  buildSky();
  showSlider();
  el.slider.addEventListener("input", () => { el.hint.hidden = true; hintDone = true; el.msgReset.textContent = ""; showSlider(); update(); });
  el.reset.addEventListener("click", () => {
    el.slider.value = 0;
    showSlider();
    update();
    say(el.msgReset, "Back to the start: satellites spread out.");
  });
  start();

  // ---------- start up ----------

  function start() {
    whenPythonReady(el.status, async (call) => {
      callPython = call;
      try {
        receiverPoint = await callPython("coords.latlon_to_xyz", [receiver.lat_deg, receiver.lon_deg]);
        if (receiverPoint.error) throw new Error(receiverPoint.error);
      } catch (error) {
        console.error(error);
        el.status.textContent = "The calculation engine loaded but could not place the phone, so the controls stay off.";
        return;
      }
      el.slider.disabled = false;
      el.reset.disabled = false;
      el.hint.hidden = hintDone;
      if (!hintDone) el.hint.classList.add("is-shown"); // index.html's .hint rule fades it in only with this class
      update();
    });
  }

  // ---------- the slider and the sky (drawing only) ----------

  function bunchAmount() { return Number(el.slider.value) / geometryConfig.slider_steps; }

  // Blend each satellite's angles between the spread set and the bunched set.
  function currentSky() {
    const t = bunchAmount();
    return spread.map((from, i) => ({
      id: from.id,
      azimuth_deg: from.azimuth_deg + (bunched[i].azimuth_deg - from.azimuth_deg) * t,
      elevation_deg: from.elevation_deg + (bunched[i].elevation_deg - from.elevation_deg) * t,
    }));
  }

  function showSlider() {
    el.sliderValue.textContent = `${Math.round(bunchAmount() * 100)}\u00a0% bunched`;
    el.slider.setAttribute("aria-valuetext", el.sliderValue.textContent);
    el.sky.setAttribute("aria-label", `${SKY_LABEL} ${el.sliderValue.textContent}.`);
    drawSky(currentSky()); // instant, no easing: the sky follows the slider every frame
  }

  function buildSky() {
    const mid = SKY_SIZE / 2;
    for (const fraction of [1, 2 / 3, 1 / 3]) { // horizon, then rings at 30 and 60 degrees up
      const ring = document.createElementNS(SVG, "circle");
      ring.setAttribute("class", "sky-ring");
      ring.setAttribute("cx", mid); ring.setAttribute("cy", mid); ring.setAttribute("r", SKY_RADIUS * fraction);
      el.sky.append(ring);
    }
    for (const sat of spread) {
      const group = document.createElementNS(SVG, "g");
      group.dataset.id = sat.id;
      group.innerHTML = '<circle class="sky-sat" r="7"></circle><text text-anchor="middle" dy="-12"></text>';
      group.querySelector("text").textContent = sat.id;
      el.sky.append(group);
    }
  }

  // Overhead (90 degrees) is the middle, the horizon (0 degrees) is the edge. Azimuth 0 is north, at the top.
  function drawSky(sats) {
    const mid = SKY_SIZE / 2;
    for (const sat of sats) {
      const away = (90 - sat.elevation_deg) / 90 * SKY_RADIUS;
      const angle = sat.azimuth_deg * Math.PI / 180;
      const group = el.sky.querySelector(`g[data-id="${sat.id}"]`);
      group.setAttribute("transform", `translate(${mid + away * Math.sin(angle)} ${mid - away * Math.cos(angle)})`);
    }
  }

  // ---------- one run: ask Python, then draw ----------

  // Python calls are async. If one is running, remember that a newer run is wanted and do it once after.
  async function update() {
    if (!callPython) return;
    if (running) { rerun = true; return; }
    running = true;
    try {
      do {
        rerun = false;
        await runOnce();
      } while (rerun);
    } finally {
      running = false;
    }
  }

  async function runOnce() {
    el.msgDop.textContent = el.msgError.textContent = "";
    const position = Number(el.slider.value); // the slider position this run is about
    const sky = currentSky(); // the layout this run is about, even if the slider moves meanwhile
    try {
      const sats = [];
      for (const sat of sky) {
        const point = await callPython("coords.satellite_from_sky", [receiver.lat_deg, receiver.lon_deg, sat.azimuth_deg, sat.elevation_deg]);
        if (failed(point)) return;
        sats.push({ id: sat.id, ...point });
      }
      const dop = await callPython("geometry.dop", [receiverPoint, sats]);
      if (failed(dop)) return;
      const ranges = await callPython("scenario.make_pseudoranges", [receiverPoint, sats, geometryConfig.clock_error_s, geometryConfig.noise_m, geometryConfig.seed]);
      if (failed(ranges)) return;
      // Clock solved, as a real phone does: the clock error is removed, and what remains is the
      // noise multiplied by the layout. That is exactly what DOP describes.
      const solution = await callPython("solver.solve_position", [sats, ranges, true]);
      if (failed(solution)) return;
      const point = { x_m: solution.x_m, y_m: solution.y_m, z_m: solution.z_m };
      const local = await callPython("mapview.to_local", [receiver.lat_deg, receiver.lon_deg, point]);
      if (failed(local)) return;
      const errorM = Math.hypot(local.east_m, local.north_m, local.up_m);
      requestAnimationFrame(() => showResult(dop.pdop, errorM, position));
    } catch (error) {
      console.error(error);
      say(el.msgSlider, "Something went wrong in the calculation, so the numbers below may be out of date.");
    }
  }

  function failed(result) {
    if (!result || !result.error) return false;
    say(el.msgSlider, result.error); // Python's own plain sentence
    return true;
  }

  // ---------- show numbers ----------

  function errorLevel(errorM) {
    if (errorM < geometryConfig.error_limits.ok_m) return "ok";
    if (errorM < geometryConfig.error_limits.warn_m) return "warn";
    return "bad";
  }

  function stateSentence(level, position) {
    if (position === 0) return "Spread across the sky: small measurement errors stay small.";
    if (level === "ok") return "Still a good fix, but DOP is climbing. Keep dragging.";
    if (level === "warn") return "The same small measurement errors now move the fix by tens of metres.";
    return "Bunched together: the same small measurement errors now throw the fix far off.";
  }

  function showResult(pdop, errorM, position) {
    const level = errorLevel(errorM);
    const dopText = new Intl.NumberFormat("en", { maximumFractionDigits: 1 }).format(pdop);
    const sentence = stateSentence(level, position);
    if (el.msgSlider.textContent !== sentence) say(el.msgSlider, sentence); // only when the words change
    const percent = Math.round(position / geometryConfig.slider_steps * 100);
    el.sky.setAttribute("aria-label", `Sky diagram. Satellites ${percent} % bunched. DOP ${dopText}.`);
    el.dop.textContent = dopText;
    el.error.textContent = formatMetres(errorM);
    el.badge.hidden = false;
    el.badge.className = `badge is-${level}`;
    el.badge.textContent = LEVEL_WORDS[level];
  }
}
