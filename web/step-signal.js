// Rung 3: how the time is measured (design.md 2a). It draws and takes input;
// the received signal and every score come from Python (mechanism/signal.py).
// The only arithmetic here is scaling numbers to pixels.
import { whenPythonReady } from "./startup.js";
import { say } from "./say.js";

// Every tunable number lives here.
export const signalConfig = {
  prn: 7, // placeholder, provisional: which satellite's code (1 to 32)
  trueDelayChips: 300, // placeholder, provisional: how late the signal really arrives
  seed: 1, // placeholder, provisional: same noise every time, so a run can be repeated
  signalSize: 1, // placeholder, provisional: the code has size 1 (interface.md)
  noise: { min: 0, max: 12, step: 0.5, start: 0 }, // placeholder, provisional: noise size, in multiples of the signal
  barelyHoldingBelow: 1.5, // placeholder, provisional: peak_to_next under this = found but barely
  peakDisplayCap: 1000, // placeholder, provisional: above this the readout says "over 1000x"
  receivedLimit: 4, // placeholder, provisional: the top graph shows values from -4 to +4, bigger ones are cut off
  scoreRange: { min: -0.5, max: 2.5 }, // placeholder, provisional: the bottom graph shows scores in this range
};

const SVG = "http://www.w3.org/2000/svg";
const RECEIVED_LABEL = "The received signal: the satellite's pattern plus noise, one value per chip.";
const SCORES_LABEL = "The match score at every shift. A tall peak means the phone found the signal's timing.";
const PLOT_HEIGHT = 120; // the viewBox of both graphs is (number of chips) wide and 120 high

// Layout for this section only. Colours, fonts and radii come from theme.css.
const STYLE = `
.signal-step { display: grid; grid-template-columns: minmax(0, 1fr); gap: var(--s-5); }
.signal-step .intro { display: grid; gap: var(--s-2); }
.signal-step .grid { display: grid; grid-template-columns: minmax(0, 1fr); gap: var(--s-5); }
@media (min-width: 760px) { .signal-step .grid { grid-template-columns: 1.4fr 1fr; align-items: start; } }
.signal-step .stack { display: grid; gap: var(--s-4); }
.signal-step .plot { width: 100%; height: 120px; display: block; margin-top: var(--s-2); }
.signal-step .axis { display: flex; justify-content: space-between; font-size: var(--text-xs); color: var(--text-muted); }
.signal-step .received { fill: none; stroke: var(--text); stroke-width: 1; vector-effect: non-scaling-stroke; }
.signal-step .scores { fill: none; stroke: var(--text-muted); stroke-width: 1; vector-effect: non-scaling-stroke; }
.signal-step .mark-true { stroke: var(--text-muted); stroke-width: 1; stroke-dasharray: 3 3; vector-effect: non-scaling-stroke; }
.signal-step .mark-best { stroke: currentColor; stroke-width: 2; vector-effect: non-scaling-stroke; }
.signal-step .key { font-size: var(--text-sm); }
.signal-step .readout { padding: var(--s-4); display: grid; gap: var(--s-2); }
.signal-step .readout-row { display: flex; justify-content: space-between; align-items: baseline; gap: var(--s-3); }
.signal-step .big { font-size: var(--text-xl); }
.signal-step .badge[hidden] { display: none; }
.signal-step .note { font-size: var(--text-sm); color: var(--text-muted); min-height: 1.5em; }
.signal-step .note:empty { min-height: 0; }
.signal-step .note[data-el="msg-slider"]:empty { min-height: 1.5em; }
.signal-step h3.label { margin-bottom: var(--s-3); }
.signal-step .highlight { border-color: var(--accent); padding: var(--s-4); }
.signal-step .hint { font-size: var(--text-sm); font-weight: 500; color: var(--text); }
.signal-step .slider-head { flex-wrap: wrap; column-gap: var(--s-3); }
.signal-step .btn { touch-action: manipulation; }
.signal-step .btn:disabled, .signal-step input[type="range"]:disabled { opacity: 0.4; cursor: not-allowed; }
.signal-step .btn:disabled:hover { border-color: var(--line-strong); }
.signal-step input[type="range"] { touch-action: pan-y; }
`;

export function mountSignalStep(container) {
  addStyleOnce();
  container.insertAdjacentHTML("beforeend", PAGE_HTML);
  const root = container.lastElementChild;
  const find = (name) => root.querySelector(`[data-el="${name}"]`);
  const el = {
    status: find("status"), hint: find("hint"), clipNote: find("clip-note"), receivedPlot: find("received-plot"), scoresPlot: find("scores-plot"), slider: find("noise"), sliderValue: find("noise-value"), msgSlider: find("msg-slider"),
    reset: find("reset"), msgReset: find("msg-reset"), receivedLine: find("received-line"), scoresLine: find("scores-line"),
    trueMark: find("true-mark"), bestMark: find("best-mark"), bestGroup: find("best-group"),
    bestDelay: find("best-delay"), trueDelay: find("true-delay"), peak: find("peak"),
    badge: find("badge"), sentence: find("sentence"),
  };

  let callPython = null; // set when the bridge has loaded
  let noise = signalConfig.noise.start;
  let running = false;
  let rerun = false;
  let hintDone = false; // once the user has touched the slider, the hint stays hidden

  setupControls();
  start();

  // ---------- start up ----------

  function start() {
    whenPythonReady(el.status, (call) => {
      callPython = call;
      setControlsDisabled(false);
      el.hint.hidden = hintDone;
      if (!hintDone) el.hint.classList.add("is-shown"); // index.html's .hint rule fades it in only with this class
      update();
    });
  }

  // ---------- controls ----------

  function setupControls() {
    const { min, max, step, start: startValue } = signalConfig.noise;
    // The slider counts steps (whole numbers), so there are no floating point surprises.
    el.slider.min = 0;
    el.slider.max = Math.round((max - min) / step);
    el.slider.step = 1;
    el.slider.value = Math.round((startValue - min) / step);
    el.slider.addEventListener("input", () => {
      noise = Number(el.slider.value) * step + min;
      el.hint.hidden = true;
      hintDone = true;
      el.msgReset.textContent = "";
      showNoiseValue();
      update();
    });
    el.reset.addEventListener("click", () => {
      noise = startValue;
      el.slider.value = Math.round((startValue - min) / step);
      showNoiseValue();
      update();
      say(el.msgReset, "Back to the start: no noise.");
    });
    el.trueDelay.textContent = `${signalConfig.trueDelayChips} chips`;
    drawMark(el.trueMark, signalConfig.trueDelayChips);
    showNoiseValue();
    setControlsDisabled(true);
  }

  function setControlsDisabled(disabled) {
    el.slider.disabled = disabled;
    el.reset.disabled = disabled;
  }

  function showNoiseValue() {
    el.sliderValue.textContent = noise === 0 ? "No noise" : `${noise.toFixed(1)}× the signal`;
    el.slider.setAttribute("aria-valuetext", noise === 0 ? "No noise" : `Noise ${noise.toFixed(1)} times the signal`);
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
    } catch (error) {
      console.error(error);
      say(el.msgSlider, "Something went wrong while calculating, so the picture may be out of date.");
    } finally {
      running = false;
    }
  }

  async function runOnce() {
    const { prn, trueDelayChips, seed } = signalConfig;
    const usedNoise = noise; // the slider may move while Python works
    el.msgSlider.textContent = "";
    const received = await callPython("signal.make_received", [prn, trueDelayChips, usedNoise, seed]);
    if (failed(received)) return;
    const result = await callPython("signal.correlate", [received, prn]);
    if (failed(result)) return;
    requestAnimationFrame(() => draw(received, result, usedNoise));
  }

  function failed(result) {
    if (!result || !result.error) return false;
    say(el.msgSlider, result.error); // Python's own plain sentence
    return true;
  }

  // ---------- reading the result ----------

  // "Lost" means the best shift is not the true delay. The threshold only separates ok from "barely".
  function levelOf(result) {
    if (result.best_delay_chips !== signalConfig.trueDelayChips) return "bad";
    return result.peak_to_next < signalConfig.barelyHoldingBelow ? "warn" : "ok";
  }

  const levelWords = { ok: "Found", warn: "Barely found", bad: "Lost" };

  function sentenceFor(level, usedNoise) {
    if (level === "bad") return "The phone can no longer find where the signal starts.";
    if (level === "warn") return "The match still points to the right place, but only just.";
    if (usedNoise > signalConfig.signalSize) return "The noise is bigger than the signal, yet the match still finds it.";
    return "The match stands out clearly from everything else.";
  }

  function formatPeak(value) {
    if (value >= signalConfig.peakDisplayCap) return `over ${signalConfig.peakDisplayCap}×`;
    return `${value.toFixed(1)}×`;
  }

  // ---------- drawing ----------

  function draw(received, result, usedNoise) {
    const { receivedLimit, scoreRange } = signalConfig;
    el.receivedLine.setAttribute("points", toPoints(received, -receivedLimit, receivedLimit));
    el.scoresLine.setAttribute("points", toPoints(result.scores, scoreRange.min, scoreRange.max));
    const level = levelOf(result);
    drawMark(el.bestMark, result.best_delay_chips);
    el.bestGroup.setAttribute("class", `is-${level}`);
    el.bestDelay.textContent = `${result.best_delay_chips} chips`;
    el.peak.textContent = formatPeak(result.peak_to_next);
    el.badge.hidden = false;
    el.badge.className = `badge is-${level}`;
    el.badge.textContent = levelWords[level];
    el.sentence.textContent = sentenceFor(level, usedNoise);
    // Noise peaks regularly pass the graph's edge once the noise is more than half the graph's range.
    el.clipNote.textContent = usedNoise * 2 > receivedLimit
      ? "The noise is now taller than this graph, so its peaks are cut off at the top and bottom." : "";
    const noiseWords = `${usedNoise.toFixed(1)} times the signal`;
    el.receivedPlot.setAttribute("aria-label", `${RECEIVED_LABEL} Noise ${noiseWords}.`);
    el.scoresPlot.setAttribute("aria-label",
      `${SCORES_LABEL} Best match at shift ${result.best_delay_chips}; the real delay is ${signalConfig.trueDelayChips}.`);
  }

  // One point per chip: x is the chip number, y is the value scaled into the graph (cut off at the edges).
  function toPoints(values, low, high) {
    return values.map((value, index) => {
      const clamped = Math.min(high, Math.max(low, value));
      const y = PLOT_HEIGHT - ((clamped - low) / (high - low)) * PLOT_HEIGHT;
      return `${index},${y.toFixed(1)}`;
    }).join(" ");
  }

  function drawMark(line, chip) {
    line.setAttribute("x1", chip);
    line.setAttribute("x2", chip);
    line.setAttribute("y1", 0);
    line.setAttribute("y2", PLOT_HEIGHT);
  }
}

function addStyleOnce() {
  if (document.getElementById("signal-step-style")) return;
  const style = document.createElement("style");
  style.id = "signal-step-style";
  style.textContent = STYLE;
  document.head.append(style);
}

const PAGE_HTML = `
<section class="signal-step" aria-labelledby="signal-title">
  <header class="intro">
    <h2 id="signal-title">How does the phone measure the time?</h2>
    <p class="muted">The satellite's signal is a known pattern of 1023 steps, called chips. The phone slides its own copy along what it hears and scores the match at every shift.</p>
  </header>

  <div class="grid">
    <div class="card">
      <h3 class="label">What the phone hears</h3>
      <svg class="plot" data-el="received-plot" viewBox="0 0 1023 120" preserveAspectRatio="none" role="img"
        aria-label="The received signal: the satellite's pattern plus noise, one value per chip.">
        <polyline class="received" data-el="received-line" points=""/>
      </svg>
      <div class="axis" aria-hidden="true"><span>chip 0</span><span>chip 1022</span></div>
      <p class="key muted" data-el="clip-note" role="status" aria-live="polite"></p>

      <h3 class="label" style="margin-top: var(--s-5)">How well the code matches at each shift</h3>
      <svg class="plot" data-el="scores-plot" viewBox="0 0 1023 120" preserveAspectRatio="none" role="img"
        aria-label="The match score at every shift. A tall peak means the phone found the signal's timing.">
        <line class="mark-true" data-el="true-mark"/>
        <polyline class="scores" data-el="scores-line" points=""/>
        <g data-el="best-group" class="is-ok"><line class="mark-best" data-el="best-mark"/></g>
      </svg>
      <div class="axis" aria-hidden="true"><span>shift 0</span><span>shift 1022</span></div>
      <p class="key muted">Solid line: the best match the phone found. Dashed line: where the signal really is.</p>
    </div>

    <div class="card stack">
      <p class="note" data-el="status" role="status" aria-live="polite">Loading the maths…</p>
      <p class="hint" data-el="hint" hidden>Drag this slider to bury the signal in noise, until the phone loses it.</p>
      <div class="slider inset highlight">
        <div class="slider-head">
          <label for="signal-noise">Add noise</label>
          <span class="num" data-el="noise-value">No noise</span>
        </div>
        <input id="signal-noise" data-el="noise" type="range" disabled>
        <p class="note" data-el="msg-slider" role="status" aria-live="polite"></p>
      </div>

      <div class="inset readout">
        <span class="label">Best delay found</span>
        <span class="num big" data-el="best-delay">–</span>
        <div class="readout-row"><span class="muted">Real delay</span><span class="num" data-el="true-delay">–</span></div>
        <div class="readout-row"><span class="muted">Peak stands out by</span><span class="num" data-el="peak">–</span></div>
        <div><span class="badge is-ok" data-el="badge" hidden></span></div>
        <p class="note" data-el="sentence" role="status" aria-live="polite"></p>
      </div>

      <div>
        <button class="btn" data-el="reset" type="button" disabled>Reset</button>
        <p class="note" style="margin-top: var(--s-2)" data-el="msg-reset" role="status" aria-live="polite"></p>
      </div>
    </div>
  </div>
</section>`;
