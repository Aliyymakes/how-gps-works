// Rung 4: relativity (design.md 2a, 2b). One slider drives two cards: (a) the satellite clocks pull ahead,
// (b) the position does not drift. Every number comes from Python (relativity.drift_over_time and the first
// screen's own chain of calls); the only fixed numbers are the 45, 7 and 38 µs a day from docs/facts.md rows 25 to 27.
import * as config from "./config.js";
import { whenPythonReady } from "./startup.js";
import { say } from "./say.js";
import { formatMetres, formatRoughDistance, formatClockDigits } from "./format.js";

const SVG = "http://www.w3.org/2000/svg";
const MAP_SIZE = 200; // each small map's viewBox is 200 by 200

// Layout for this section only. Colours, fonts and radii come from theme.css.
const STYLE = `
.rel { display: grid; grid-template-columns: minmax(0, 1fr); gap: var(--s-4); }
.rel-stack { grid-template-columns: minmax(0, 1fr); }
.rel-note { font-size: var(--text-sm); color: var(--text-muted); min-height: 1.5em; }
.rel-note:empty { min-height: 0; }
.rel-card { display: grid; grid-template-columns: minmax(0, 1fr); gap: var(--s-4); }
.rel-highlight { border-color: var(--accent); padding: var(--s-4); }
.rel-readout { padding: var(--s-4); display: grid; gap: var(--s-2); grid-template-columns: minmax(0, 1fr); }
.rel-sketch { width: 100%; max-width: 360px; height: auto; display: block; }
.rel-clocks { display: grid; grid-template-columns: minmax(0, 1fr); gap: var(--s-3); }
.rel-digits { font-size: var(--text-lg); color: var(--text-muted); overflow-wrap: anywhere; }
.rel-digits .diff { color: var(--text); }
.rel-pair { display: grid; grid-template-columns: minmax(0, 1fr); gap: var(--s-4); }
@media (min-width: 560px) { .rel-pair { grid-template-columns: 1fr 1fr; } }
.rel-why { margin: 0; padding: 0; list-style: none; display: grid; gap: var(--s-2); font-size: var(--text-sm); }
.rel-maps { max-width: 640px; display: grid; grid-template-columns: minmax(0, 1fr); gap: var(--s-4); }
@media (min-width: 340px) { .rel-maps { grid-template-columns: minmax(0, 1fr) minmax(0, 1fr); } }
.rel-map { display: grid; grid-template-columns: minmax(0, 1fr); gap: var(--s-2); align-content: start; }
.rel-map-title { font-size: var(--text-sm); font-weight: 600; margin: 0; }
.rel-off { font-size: var(--text-lg); overflow-wrap: anywhere; }
.rel-map .rel-off { font-size: var(--text-md); white-space: nowrap; }
.rel .hint { font-size: var(--text-sm); font-weight: 500; color: var(--text); }
.rel .slider-head { flex-wrap: nowrap; column-gap: var(--s-3); }
.rel .slider-head .num { white-space: nowrap; }
.rel-control { position: sticky; top: var(--s-2); z-index: 5; background: var(--surface); }
.rel-control, .rel input, .rel button { scroll-margin-top: 140px; }
@media (max-width: 559px) { .rel-control { padding: var(--s-3); gap: var(--s-2); } .rel-control .rel-highlight { padding: var(--s-3); } }
@media (max-width: 419px) { .rel-map .rel-off { font-size: var(--text-sm); } }
.rel [data-id="sentence"] { color: var(--text); font-size: var(--text-md); }
.rel .badge[hidden] { display: none; }
.rel .btn { touch-action: manipulation; }
.rel input[type="range"] { touch-action: pan-y; }
.rel .btn:disabled, .rel input[type="range"]:disabled { opacity: 0.4; cursor: not-allowed; }
.rel .btn:disabled:hover { border-color: var(--line-strong); }
`;

const LEVEL_WORDS = { ok: "Good fix", warn: "Fix is off", bad: "Fix is far off" };

function errorLevel(errorM) {
  if (errorM < config.errorLimits.ok_m) return "ok";
  if (errorM < config.errorLimits.warn_m) return "warn";
  return "bad";
}

// One small ground map, like the first screen's: frame, cross at the true place, distance lines, dot.
function mapMarkup(name, title, label) {
  return `
      <div class="rel-map">
        <p class="rel-map-title">${title}</p>
        <svg class="map" data-id="map-${name}" viewBox="0 0 ${MAP_SIZE} ${MAP_SIZE}" role="img" aria-label="${label}">
          <rect class="map-frame" x="0.5" y="0.5" width="${MAP_SIZE - 1}" height="${MAP_SIZE - 1}"/>
          <path class="map-true" d="M92 100h16M100 92v16"/>
          <g data-id="lines-${name}"></g>
          <g data-id="dot-${name}" class="is-ok" style="display: none"><circle class="map-dot" r="6"/></g>
        </svg>
        <span class="num rel-off" data-id="${name}">–</span>
        <div><span class="badge is-ok" data-id="${name}-badge" hidden></span></div>
        <p class="rel-note" data-id="caption-${name}" role="status" aria-live="polite"></p>
      </div>`;
}

// Draft sentences: every visible sentence below is for Icarus to approve.
const PAGE = `
<div class="rel">
  <header class="rel-stack" style="display: grid; gap: var(--s-2)">
    <h2 id="rel-title">Do the satellites' own clocks matter?</h2>
    <p class="rel-note" data-id="status" role="status" aria-live="polite">Loading the maths…</p>
  </header>
  <section class="card rel-card rel-control" aria-label="Control">
    <p class="hint" data-id="hint" hidden>Drag this back to 0 and the two clocks agree. Drag it forward and watch the gap grow.</p>
    <div class="slider inset rel-highlight">
      <div class="slider-head">
        <label for="rel-hours">Time since the satellite clocks were last corrected</label>
        <span class="num" data-id="slider-value">24 h</span>
      </div>
      <input id="rel-hours" data-id="slider" type="range" disabled>
    </div>
  </section>

  <section class="card rel-card" aria-labelledby="rel-a-title">
    <div style="display: grid; gap: var(--s-2)">
      <span class="label">First</span>
      <h3 id="rel-a-title">Satellite clocks run fast.</h3>
    </div>
    <p class="looking"><b>What you're looking at:</b> two clocks that started together. One stayed on the ground. One is on a GPS satellite.</p>
    <svg class="figure rel-sketch" viewBox="0 0 320 130" role="img" aria-label="Sketch: a clock on the ground and a clock on a satellite. The satellite's clock is ahead.">
      <path class="dim" d="M10 120 Q160 80 310 120"/>
      <circle cx="170" cy="88" r="9"/>
      <path d="M170 88v-6M170 88h5"/>
      <text x="196" y="94">on the ground</text>
      <rect x="100" y="23" width="14" height="14"/>
      <rect class="dim" x="82" y="27" width="16" height="6"/>
      <rect class="dim" x="116" y="27" width="16" height="6"/>
      <path class="dim" d="M114 30h47"/>
      <circle cx="170" cy="30" r="9"/>
      <path d="M170 30v-6M170 30l4 4"/>
      <path d="M186 30h14m-5-4l5 4l-5 4"/>
      <text x="206" y="34">ahead</text>
      <text x="82" y="16">on a satellite</text>
    </svg>
    <div class="rel-clocks">
      <div class="inset rel-readout">
        <span class="label">Clock on the ground</span>
        <span class="num rel-digits" data-id="digits-ground" role="img" aria-label="">–</span>
      </div>
      <div class="inset rel-readout">
        <span class="label">Clock on the satellite</span>
        <span class="num rel-digits" data-id="digits-satellite" role="img" aria-label="">–</span>
      </div>
    </div>
    <p class="rel-note">Both clocks were set together at 00:00:00. The last digits are millionths of a second (µs).</p>
    <div class="rel-pair">
      <div class="inset rel-readout">
        <span class="label">Satellite clock ahead by</span>
        <span class="num rel-off" data-id="gap">–</span>
      </div>
      <div class="inset rel-readout">
        <span class="label">So every measured distance is wrong by</span>
        <span class="num rel-off" data-id="range">–</span>
      </div>
    </div>
    <p class="rel-note">A signal covers about 300 m in one millionth of a second.</p>
    <ul class="rel-why" aria-label="Why the satellite clocks run fast">
      <li>Weaker gravity up there: the clock runs faster, by 45 µs a day</li>
      <li>It moves fast: the clock runs slower, by 7 µs a day</li>
      <li><b>Together: about 38 µs a day faster</b></li>
    </ul>
    <p class="rel-note">Both effects come from Einstein's relativity. Gravity is the bigger one.</p>
  </section>

  <section class="card rel-card" aria-labelledby="rel-b-title">
    <div style="display: grid; gap: var(--s-2)">
      <span class="label">Then</span>
      <h3 id="rel-b-title">So why doesn't your position drift?</h3>
    </div>
    <p class="looking"><b>What you're looking at:</b> the map from the top of the page, twice, with every satellite clock ahead by the same amount. Each map is 40 km wide.</p>
    <p class="rel-note">Cross: where it really is. Dot: where the phone thinks it is.</p>
    <div class="rel-maps">${mapMarkup("trusted", "The phone trusts its clock", "Ground map, 40 km wide. The phone trusts its clock.")}${mapMarkup("solved", "The phone solves for its clock", "Ground map, 40 km wide. The phone solves for its clock.")}
    </div>
    <p class="rel-note" data-id="height-note">Most of the left map's error is height, which a flat map cannot show. The dot shows the sideways part.</p>
    <p class="rel-note" data-id="sentence" role="status" aria-live="polite"></p>
    <div>
      <button class="btn" data-id="reset" type="button" disabled>Reset</button>
      <p class="rel-note" style="margin-top: var(--s-2)" data-id="msg-reset" role="status" aria-live="polite"></p>
    </div>
  </section>
</div>`;

export function mountRelativityStep(container) {
  if (!document.getElementById("rel-style")) {
    const style = document.createElement("style");
    style.id = "rel-style";
    style.textContent = STYLE;
    document.head.append(style);
  }
  container.insertAdjacentHTML("beforeend", PAGE);
  const root = container.lastElementChild;
  const $ = (id) => root.querySelector(`[data-id="${id}"]`);
  const el = {
    status: $("status"), hint: $("hint"), slider: $("slider"), sliderValue: $("slider-value"),
    digitsGround: $("digits-ground"), digitsSatellite: $("digits-satellite"), gap: $("gap"), range: $("range"),
    sentence: $("sentence"), heightNote: $("height-note"), reset: $("reset"), msgReset: $("msg-reset"),
  };
  // The two maps share one set of parts, so one drawing function serves both.
  const maps = {};
  for (const name of ["trusted", "solved"]) {
    maps[name] = {
      svg: $(`map-${name}`), lines: $(`lines-${name}`), dot: $(`dot-${name}`), caption: $(`caption-${name}`),
      value: $(name), badge: $(`${name}-badge`), base: $(`map-${name}`).getAttribute("aria-label").replace(/\.$/, ""),
    };
  }
  const { min_h, max_h, step_h, start_h } = config.relativitySlider;

  let callPython = null; // set when the bridge has loaded
  let receiver = null; // true receiver position, from Python
  let satellites = null; // the four satellites, from Python
  let running = false;
  let wanted = false; // true when a newer run is wanted
  let hintDone = false; // once the user has touched the slider, the hint stays hidden

  el.slider.min = min_h;
  el.slider.max = max_h;
  el.slider.step = step_h;
  el.slider.value = start_h;
  showHours();
  el.slider.addEventListener("input", () => {
    el.hint.hidden = true;
    hintDone = true;
    el.msgReset.textContent = "";
    showHours();
    update();
  });
  el.reset.addEventListener("click", () => {
    el.slider.value = start_h;
    showHours();
    update();
    say(el.msgReset, "Back to the start: one day.");
  });
  whenPythonReady(el.status, start);

  async function start(call) {
    callPython = call;
    try {
      const { lat_deg, lon_deg } = config.receiver;
      receiver = await callPython("coords.latlon_to_xyz", [lat_deg, lon_deg]);
      if (receiver.error) throw new Error(receiver.error);
      satellites = [];
      for (const sat of config.satellites) {
        const point = await callPython("coords.satellite_from_sky", [lat_deg, lon_deg, sat.azimuth_deg, sat.elevation_deg]);
        if (point.error) throw new Error(point.error);
        satellites.push({ id: sat.id, ...point });
      }
    } catch (error) {
      console.error(error);
      el.status.textContent = "The calculation engine loaded but could not place the satellites, so the controls stay off.";
      return;
    }
    el.slider.disabled = false;
    el.reset.disabled = false;
    el.hint.hidden = hintDone;
    if (!hintDone) el.hint.classList.add("is-shown"); // index.html's .hint rule fades it in only with this class
    update();
  }

  function showHours() {
    const hours = Number(el.slider.value);
    el.sliderValue.textContent = `${hours} h`;
    el.slider.setAttribute("aria-valuetext", `${hours} hours`);
  }

  // Many slider moves can arrive before one frame. Only the newest value is worked on, and at most one
  // chain of Python calls runs per animation frame, so dragging stays smooth.
  function update() {
    if (!callPython || !satellites) return;
    wanted = true;
    if (!running) requestAnimationFrame(runNewest);
  }

  async function runNewest() {
    if (running || !wanted) return;
    running = true;
    try {
      while (wanted) {
        wanted = false;
        await runOnce();
        if (wanted) await new Promise((resolve) => requestAnimationFrame(resolve)); // let a frame draw first
      }
    } finally {
      running = false;
    }
  }

  async function runOnce() {
    const hours = Number(el.slider.value); // the slider may move while Python works
    try {
      const result = await callPython("relativity.drift_over_time",
        [receiver, satellites, config.relativityPhoneClockErrorS, [hours]]);
      if (result.error) { failed(result.error); return; } // Python's own plain sentence
      const row = result[0];
      showClocks(row, hours);
      // The same chain of calls the first screen uses, once with the clock trusted and once solved.
      const ranges = await callPython("scenario.make_pseudoranges", [receiver, satellites, row.solved_clock_error_s]);
      if (ranges.error) { failed(ranges.error); return; }
      const trusted = await fix(ranges, false);
      const solved = trusted.error ? trusted : await fix(ranges, true);
      if (solved.error) { failed(solved.error); return; }
      requestAnimationFrame(() => {
        drawMap(maps.trusted, trusted, row.error_clock_trusted_m);
        drawMap(maps.solved, solved, row.error_clock_solved_m);
      });
      showSentence(hours, row);
    } catch (error) {
      console.error(error);
      failed("Something went wrong in the calculation, so the numbers may be out of date.");
    }
  }

  // Solve the position and get its map lines. Returns { lines, local } or { error }.
  async function fix(ranges, solveClock) {
    const solution = await callPython("solver.solve_position", [satellites, ranges, solveClock]);
    if (solution.error) return solution;
    const { lat_deg, lon_deg } = config.receiver;
    const point = { x_m: solution.x_m, y_m: solution.y_m, z_m: solution.z_m };
    const local = await callPython("mapview.to_local", [lat_deg, lon_deg, point]);
    if (local.error) return local;
    const assumedClockS = solveClock ? solution.clock_error_s : 0;
    const lines = await callPython("mapview.distance_lines",
      [lat_deg, lon_deg, satellites, ranges, assumedClockS, config.relativityMapHalfWidthM, config.lineSamples]);
    if (lines.error) return lines;
    return { lines, local };
  }

  // A picture must never outlive its numbers: say what went wrong and hide the lines and dots.
  function failed(words) {
    say(el.sentence, words);
    requestAnimationFrame(() => {
      for (const map of Object.values(maps)) { drawLines(map, []); map.dot.style.display = "none"; }
    });
  }

  // The digits, the gap and the distance. The gap is Python's solved clock error, shown in whole microseconds
  // everywhere, so the digits and the "about N µs" never disagree.
  function showClocks(row, hours) {
    const gapMicroseconds = Math.round(row.solved_clock_error_s * 1e6);
    const digits = formatClockDigits(hours, gapMicroseconds);
    showDigits(el.digitsGround, digits.ground, digits.satellite);
    showDigits(el.digitsSatellite, digits.satellite, digits.ground);
    el.digitsGround.setAttribute("aria-label", `Clock on the ground reads ${digits.ground} (hours, minutes, seconds, then millionths of a second)`);
    el.digitsSatellite.setAttribute("aria-label", `Clock on the satellite reads ${digits.satellite}, ahead by ${gapMicroseconds} millionths of a second`);
    el.gap.textContent = gapMicroseconds === 0 ? "0 µs" : `about ${gapMicroseconds} µs`;
    el.range.textContent = row.range_added_m < 1 ? "0 m" : `about ${formatRoughDistance(row.range_added_m)}`;
  }

  // Digits that differ from the other row are bright; the rest are quiet.
  function showDigits(node, mine, other) {
    node.replaceChildren(...[...mine].map((character, i) => {
      const span = document.createElement("span");
      span.textContent = character;
      if (character !== other[i]) span.className = "diff";
      return span;
    }));
  }

  function showSentence(hours, row) {
    const sentence = hours === 0
      ? "No gap yet. Both maps agree."
      : "Every satellite is off by the same amount. To the phone that looks exactly like its own clock being wrong, and the fourth satellite already fixes that.";
    if (el.sentence.textContent !== sentence) say(el.sentence, sentence); // only when the words change
    el.heightNote.hidden = row.error_clock_trusted_m < 1;
  }

  // ---------- drawing one small map ----------

  function toPixel(metres) { return (metres + config.relativityMapHalfWidthM) * MAP_SIZE / (2 * config.relativityMapHalfWidthM); }

  function drawMap(map, result, errorM) {
    const { lines, local } = result;
    drawLines(map, lines);
    const x = toPixel(local.east_m);
    const y = MAP_SIZE - toPixel(local.north_m); // north is up
    const inside = x >= 0 && x <= MAP_SIZE && y >= 0 && y <= MAP_SIZE;
    const level = errorLevel(errorM);
    map.dot.style.display = inside ? "" : "none";
    map.dot.firstElementChild.setAttribute("cx", x);
    map.dot.firstElementChild.setAttribute("cy", y);
    map.dot.setAttribute("class", `is-${level}`);
    map.value.textContent = errorM < 0.05 ? "0 m off" : `about ${formatRoughDistance(errorM)} off`;
    map.badge.hidden = false;
    map.badge.className = `badge is-${level}`;
    map.badge.textContent = LEVEL_WORDS[level];
    // Like the first screen's caption: say when the map hides something.
    const off = lines.filter((line) => !line.inside).length;
    let words = inside ? "" : "The phone's position is off the edge of this map.";
    if (off > 0) words += ` ${off} of the ${lines.length} distance lines ${off === 1 ? "has" : "have"} moved off the edge of this map.`;
    map.caption.textContent = words.trim();
    map.svg.setAttribute("aria-label", `${map.base}. ${lines.length} distance lines. Position off by ${map.value.textContent.replace(" off", "")}.`);
  }

  function drawLines(map, lines) {
    const known = new Map([...map.lines.children].map((node) => [node.dataset.id, node]));
    for (const line of lines) {
      let node = known.get(line.id);
      if (!node) {
        node = document.createElementNS(SVG, "polyline");
        node.dataset.id = line.id;
        node.setAttribute("class", "map-line");
        map.lines.append(node);
      }
      node.setAttribute("points", line.points.map(([e, n]) => [toPixel(e), MAP_SIZE - toPixel(n)]).join(" "));
      node.classList.toggle("is-hidden", !line.inside);
    }
    const wantedIds = new Set(lines.map((line) => line.id));
    for (const [id, node] of known) if (!wantedIds.has(id)) node.classList.add("is-hidden");
  }
}
