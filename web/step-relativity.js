// Rung 4: relativity (design.md 2a, 2b). One slider, two results side by side. Every number comes
// from Python (relativity.drift_over_time); nothing is calculated here except choosing a badge colour.
import * as config from "./config.js";
import { whenPythonReady } from "./startup.js";
import { say } from "./say.js";
import { formatMetres } from "./format.js";

// Layout for this section only. Colours, fonts and radii come from theme.css.
const STYLE = `
.rel { display: grid; grid-template-columns: minmax(0, 1fr); gap: var(--s-4); }
.rel-stack { grid-template-columns: minmax(0, 1fr); }
.rel-note { font-size: var(--text-sm); color: var(--text-muted); min-height: 1.5em; }
.rel-note:empty { min-height: 0; }
.rel-card { display: grid; grid-template-columns: minmax(0, 1fr); gap: var(--s-4); }
.rel-highlight { border-color: var(--accent); padding: var(--s-4); }
.rel-readout { padding: var(--s-4); display: grid; gap: var(--s-2); }
.rel-big { font-size: var(--text-xl); }
.rel-pair { display: grid; grid-template-columns: minmax(0, 1fr); gap: var(--s-4); }
@media (min-width: 760px) { .rel-pair { grid-template-columns: 1fr 1fr; } }
.rel .hint { font-size: var(--text-sm); font-weight: 500; color: var(--text); }
.rel .slider-head { flex-wrap: wrap; column-gap: var(--s-3); }
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

// Draft sentences: every visible sentence below is for Icarus to approve.
const PAGE = `
<div class="rel">
  <header class="rel-stack" style="display: grid; gap: var(--s-2)">
    <h2 id="rel-title">Do the satellites' own clocks matter?</h2>
    <p class="muted">A satellite's clock does not tick at the same rate as a clock on the ground. Left uncorrected, the difference grows every hour. Here every satellite drifts by the same amount.</p>
    <p class="rel-note" data-id="status" role="status" aria-live="polite">Loading the maths…</p>
  </header>
  <section class="card rel-card" aria-labelledby="rel-title">
    <p class="hint" data-id="hint" hidden>Drag this slider to let the satellite clocks drift for a day.</p>
    <div class="slider inset rel-highlight">
      <div class="slider-head">
        <label for="rel-hours">Hours without correcting the satellite clocks</label>
        <span class="num" data-id="slider-value">0 h</span>
      </div>
      <input id="rel-hours" data-id="slider" type="range" disabled>
    </div>
    <div class="inset rel-readout">
      <span class="label">Each measured distance is wrong by</span>
      <span class="num rel-big" data-id="range">–</span>
    </div>
    <div class="rel-pair">
      <div class="inset rel-readout">
        <span class="label">If the phone trusted its clock</span>
        <span class="num rel-big" data-id="trusted">–</span>
        <div><span class="badge is-ok" data-id="trusted-badge" hidden></span></div>
      </div>
      <div class="inset rel-readout">
        <span class="label">Because the phone solves for its clock</span>
        <span class="num rel-big" data-id="solved">–</span>
        <div><span class="badge is-ok" data-id="solved-badge" hidden></span></div>
      </div>
    </div>
    <p class="rel-note" data-id="sentence" role="status" aria-live="polite"></p>
    <div>
      <button class="btn" data-id="reset" type="button" disabled>Reset</button>
      <p class="rel-note" style="margin-top: var(--s-2)" data-id="msg-reset" role="status" aria-live="polite"></p>
    </div>
  </section>
  <p>The drift is the same for every satellite, so it looks just like the phone's own clock error, and solving for the clock absorbs it. The position stays put.</p>
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
    range: $("range"), trusted: $("trusted"), trustedBadge: $("trusted-badge"),
    solved: $("solved"), solvedBadge: $("solved-badge"), sentence: $("sentence"),
    reset: $("reset"), msgReset: $("msg-reset"),
  };
  const { min_h, max_h, step_h, start_h } = config.relativitySlider;

  let callPython = null; // set when the bridge has loaded
  let receiver = null; // true receiver position, from Python
  let satellites = null; // the four satellites, from Python
  let running = false;
  let rerun = false;
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
    say(el.msgReset, "Back to the start: no drift.");
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
    el.sliderValue.textContent = `${hours} h`;
    el.slider.setAttribute("aria-valuetext", `${hours} hours`);
  }

  // Python calls are async. If one is running, remember that a newer run is wanted and do it once after.
  async function update() {
    if (!callPython || !satellites) return;
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
    const hours = Number(el.slider.value); // the slider may move while Python works
    try {
      const result = await callPython("relativity.drift_over_time",
        [receiver, satellites, config.relativityPhoneClockErrorS, [hours]]);
      if (result.error) { say(el.sentence, result.error); return; } // Python's own plain sentence
      showResult(result[0], hours);
    } catch (error) {
      console.error(error);
      say(el.sentence, "Something went wrong in the calculation, so the numbers may be out of date.");
    }
  }

  function showResult(row, hours) {
    el.range.textContent = formatMetres(row.range_added_m);
    showError(el.trusted, el.trustedBadge, row.error_clock_trusted_m);
    showError(el.solved, el.solvedBadge, row.error_clock_solved_m);
    const sentence = hours === 0
      ? "No drift yet. Both ways of solving agree."
      : "Every distance is wrong by the same amount, so solving for the clock absorbs it. Trusting the clock would not.";
    if (el.sentence.textContent !== sentence) say(el.sentence, sentence); // only when the words change
  }

  function showError(valueNode, badgeNode, errorM) {
    const level = errorLevel(errorM);
    valueNode.textContent = formatMetres(errorM);
    badgeNode.hidden = false;
    badgeNode.className = `badge is-${level}`;
    badgeNode.textContent = LEVEL_WORDS[level];
  }
}
