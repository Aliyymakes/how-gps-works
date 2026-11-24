// Rung 3: how the time is measured (design.md 2a). The user slides the phone's copy of the
// satellite's pattern by hand, then lets the phone try every shift. It draws and takes input;
// the code, the received signal and every score come from Python (mechanism/signal.py).
// The only arithmetic here is scaling numbers to pixels and one sign comparison per step
// (is the copy's value on the same side of zero as the heard value?), which only picks a fill.
import { whenPythonReady } from "./startup.js";
import { say } from "./say.js";

// Every tunable number lives here.
export const signalConfig = {
  prn: 7, // placeholder, provisional: which satellite's code (1 to 32)
  trueDelayChips: 14, // placeholder, provisional: how late the signal really arrives (short, so it fits in the 40-step picture)
  windowChips: 40, // placeholder, provisional: how many steps the three rows show
  shift: { min: 0, max: 30, start: 0 }, // placeholder, provisional: how far the phone's copy can be slid, in chips
  seed: 1, // placeholder, provisional: same noise every time, so a run can be repeated
  signalSize: 1, // placeholder, provisional: the code has size 1 (interface.md)
  noise: { min: 0, max: 12, step: 0.5, start: 0 }, // placeholder, provisional: noise size, in multiples of the signal
  barelyHoldingBelow: 1.5, // placeholder, provisional: peak_to_next under this = found but barely
  peakDisplayCap: 1000, // placeholder, provisional: above this the readout says "over 1000x"
  receivedLimit: 2, // placeholder, provisional: the heard row shows values from -2 to +2, bigger ones are cut off
  scoreRange: { min: -0.5, max: 2.5 }, // placeholder, provisional: the plots show scores in this range
  revealMs: 1000, // placeholder, provisional: how long the search takes to draw itself
  dragStartPx: 8, // placeholder, provisional: sideways movement before a drag starts, so a vertical swipe still scrolls
};

const CHIP = 10; // width of one step in the rows picture, in picture units
const ROWS_W = signalConfig.windowChips * CHIP; // 400
const ROW_MID = { sent: 38, heard: 100, copy: 162 }; // the middle line of each row, in picture units
const HALF = 22; // half the height of a row
const PLOT_HEIGHT = 120; // the full plot's picture is (number of chips) wide and 120 high
const CLOSEUP_HEIGHT = 60; // the close-up's picture is 400 wide and 60 high
const CODE_LENGTH = 1023;

const SCORES_LABEL = "The match score at every one of the 1023 shifts.";
const GUIDE_WORDS = {
  1: "Step 1. Slide the phone's copy until it lines up with what the phone hears.",
  2: "Step 2. Now let the phone do the same search by itself.",
  3: "Step 3. Add noise until the phone loses the signal.",
};

// Layout for this section only. Colours, fonts and radii come from theme.css.
const STYLE = `
.signal-step { display: grid; grid-template-columns: minmax(0, 1fr); gap: var(--s-5); }
.signal-step .intro { display: grid; gap: var(--s-2); }
.signal-step .grid { display: grid; grid-template-columns: minmax(0, 1fr); gap: var(--s-5); }
@media (min-width: 760px) { .signal-step .grid { grid-template-columns: 1.4fr 1fr; align-items: start; } }
.signal-step .stack { display: grid; gap: var(--s-4); grid-template-columns: minmax(0, 1fr); }
.signal-step .sketch { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: var(--s-3); margin: 0 0 var(--s-4); }
.signal-step .sketch > div { display: grid; gap: var(--s-1); align-content: start; }
.signal-step .sketch svg { width: 100%; height: auto; display: block; }
.signal-step .sketch p { margin: 0; font-size: var(--text-xs); color: var(--text-muted); }
.signal-step .rows { width: 100%; height: auto; display: block; touch-action: pan-y; user-select: none; -webkit-user-select: none; }
.signal-step .row-name { font: 500 13px var(--font-sans); fill: var(--text-muted); stroke: none; }
.signal-step .sent { fill: none; stroke: var(--text-muted); stroke-width: 1.5; stroke-linejoin: miter; }
.signal-step .received { fill: none; stroke: var(--text); stroke-width: 1.5; stroke-linejoin: miter; }
.signal-step .cell { fill: var(--text); }
.signal-step .cell.is-dim { fill: var(--text-muted); opacity: 0.4; }
.signal-step .copy-outline { fill: none; stroke: none; }
.signal-step[data-guide="1"] .copy-outline { stroke: var(--accent); stroke-width: 1.5; }
.signal-step .bracket { stroke: var(--text-muted); stroke-width: 1; fill: none; }
.signal-step .bracket-text { font: 500 13px var(--font-mono); fill: var(--text); stroke: none; }
.signal-step .copy-hit { fill: transparent; cursor: grab; }
.signal-step.is-dragging .copy-hit { cursor: grabbing; }
.signal-step .guide-block { border: 1px solid transparent; border-radius: var(--r-inner); padding: var(--s-3); display: grid; gap: var(--s-2); }
.signal-step[data-guide="1"] .g1, .signal-step[data-guide="2"] .g2, .signal-step[data-guide="3"] .g3 { border-color: var(--accent); }
.signal-step .slider.guide-block { padding: var(--s-4); }
.signal-step .hand-score { display: flex; align-items: baseline; gap: var(--s-3); flex-wrap: wrap; }
.signal-step .meter { height: 4px; border-radius: 2px; background: var(--line-strong); overflow: hidden; }
.signal-step .meter-fill { height: 100%; width: 100%; background: var(--text); transform-origin: left; transform: scaleX(0); }
.signal-step .plot-title { margin: var(--s-4) 0 var(--s-1); font-size: var(--text-sm); color: var(--text); font-weight: 500; }
.signal-step .plot-area { position: relative; }
.signal-step .plot-area > svg { width: 100%; display: block; }
.signal-step .plot-area .overlay { position: absolute; left: 0; top: 0; }
.signal-step .plot-area .bar { fill: var(--text); }
.signal-step .plot-full { height: 96px; }
.signal-step .plot-close { height: 60px; }
.signal-step .scores { fill: none; stroke: var(--text-muted); stroke-width: 1; vector-effect: non-scaling-stroke; }
.signal-step [data-reveal="hidden"] { clip-path: inset(0 100% 0 0); }
.signal-step [data-reveal="running"] { clip-path: inset(0 0 0 0); transition: clip-path var(--reveal-ms, 1000ms) linear; }
.signal-step [data-reveal="done"] { clip-path: none; }
.signal-step .lane { position: relative; height: 32px; }
.signal-step .lane .tick { position: absolute; width: 2px; height: 12px; margin-left: -1px; overflow: visible; }
.signal-step .lane-top .tick { bottom: 0; }
.signal-step .lane-bottom .tick { top: 0; }
.signal-step .lane .tick-label { position: absolute; white-space: nowrap; font-size: var(--text-xs); color: var(--text); line-height: 16px; }
.signal-step .lane-top .tick-label { top: 0; }
.signal-step .lane-bottom .tick-label { bottom: 0; }
.signal-step .tick line { stroke-width: 2; }
.signal-step .tick[hidden] { display: none; }
.signal-step .mark-true { stroke: var(--text); }
.signal-step .mark-best { stroke: currentColor; }
.signal-step .axis { display: flex; justify-content: space-between; font-size: var(--text-xs); color: var(--text-muted); }
.signal-step .key { font-size: var(--text-sm); }
.signal-step .readout { padding: var(--s-4); display: grid; gap: var(--s-2); }
.signal-step .readout-row { display: flex; justify-content: space-between; align-items: baseline; gap: var(--s-3); }
.signal-step .big { font-size: var(--text-xl); }
.signal-step .badge[hidden] { display: none; }
.signal-step .note { font-size: var(--text-sm); color: var(--text-muted); min-height: 1.5em; }
.signal-step .note:empty { min-height: 0; }
.signal-step .note[data-el="msg-slider"]:empty { min-height: 1.5em; }
.signal-step h3.label { margin-bottom: var(--s-3); }
.signal-step h3.label:not(:first-child) { margin-top: var(--s-5); }
.signal-step .hint { font-size: var(--text-sm); font-weight: 500; color: var(--text); }
.signal-step .slider-head { flex-wrap: wrap; column-gap: var(--s-3); }
.signal-step .btn { touch-action: manipulation; }
.signal-step .btn:disabled, .signal-step input[type="range"]:disabled { opacity: 0.4; cursor: not-allowed; }
.signal-step .btn:disabled:hover { border-color: var(--line-strong); }
.signal-step input[type="range"] { touch-action: pan-y; }
@media (prefers-reduced-motion: reduce) { .signal-step [data-reveal] { transition: none !important; } }
`;

export function mountSignalStep(container) {
  addStyleOnce();
  container.insertAdjacentHTML("beforeend", PAGE_HTML);
  const root = container.lastElementChild;
  const find = (name) => root.querySelector(`[data-el="${name}"]`);
  const el = {
    status: find("status"), hint: find("hint"), clipNote: find("clip-note"),
    rows: find("rows"), sentLine: find("sent-line"), receivedLine: find("received-line"), copyCells: find("copy-cells"),
    bracket: find("bracket"), bracketLine: find("bracket-line"), bracketText: find("bracket-text"), copyHit: find("copy-hit"),
    shift: find("shift"), shiftValue: find("shift-value"), handScore: find("hand-score"), meter: find("meter"), handSentence: find("hand-sentence"),
    search: find("search"), msgSearch: find("msg-search"),
    closeupRest: find("closeup-rest"), closeupRestWrap: find("closeup-rest-wrap"), closeupTries: find("closeup-tries"),
    fullWrap: find("full-wrap"), fullSvg: find("scores-plot"), scoresLine: find("scores-line"),
    closeupRealTick: find("closeup-real-tick"), closeupRealLabel: find("closeup-real-label"),
    closeupBestTick: find("closeup-best-tick"), closeupBestLabel: find("closeup-best-label"),
    fullRealTick: find("full-real-tick"), fullRealLabel: find("full-real-label"),
    fullBestTick: find("full-best-tick"), fullBestLabel: find("full-best-label"),
    closeupNote: find("closeup-note"),
    slider: find("noise"), sliderValue: find("noise-value"), msgSlider: find("msg-slider"),
    reset: find("reset"), msgReset: find("msg-reset"),
    bestDelay: find("best-delay"), trueDelay: find("true-delay"), peak: find("peak"), badge: find("badge"), sentence: find("sentence"), emptyLine: find("empty-line"),
  };

  let callPython = null; // set when the bridge has loaded
  let code = null; // the satellite's 1023 steps, from Python
  let received = null; // what the phone hears at the current noise, from Python
  let result = null; // the scores for the current noise, from Python
  let noise = signalConfig.noise.start;
  let shift = signalConfig.shift.start;
  let searched = false; // has the user pressed the search button yet
  let guide = 1; // which step of the guide is current (0 = finished)
  const visited = new Set(); // shifts the user has stopped on by hand
  let shownNoise = 0; // the noise the rows were last drawn with
  let running = false;
  let rerun = false;
  let drag = null;
  let revealTimer = 0;

  buildStaticParts();
  setupControls();
  start();

  // ---------- start up ----------

  async function start() {
    whenPythonReady(el.status, async (call) => {
      callPython = call;
      const steps = await callPython("signal.ca_code", [signalConfig.prn]);
      if (failed(steps)) return;
      code = steps;
      setControlsDisabled(false);
      showGuide();
      update();
    });
  }

  // ---------- controls ----------

  function buildStaticParts() {
    const cells = [];
    for (let i = 0; i < signalConfig.windowChips; i += 1) {
      cells.push(`<rect class="cell" x="${i * CHIP + 0.5}" width="${CHIP - 1}" height="${HALF / signalConfig.receivedLimit}"/>`);
    }
    el.copyCells.innerHTML = cells.join("");
    el.cells = [...el.copyCells.children];
    el.trueDelay.textContent = "–";
    placeTick(el.closeupRealTick, el.closeupRealLabel, (signalConfig.trueDelayChips + 0.5) / signalConfig.windowChips);
    placeTick(el.fullRealTick, el.fullRealLabel, signalConfig.trueDelayChips / CODE_LENGTH);
    root.style.setProperty("--reveal-ms", `${signalConfig.revealMs}ms`);
  }

  function setupControls() {
    const { min, max, step, start: startValue } = signalConfig.noise;
    // The noise slider counts steps (whole numbers), so there are no floating point surprises.
    el.slider.min = 0;
    el.slider.max = Math.round((max - min) / step);
    el.slider.step = 1;
    el.slider.value = Math.round((startValue - min) / step);
    el.slider.addEventListener("input", () => {
      noise = Number(el.slider.value) * step + min;
      el.msgReset.textContent = "";
      if (guide === 3) { guide = 0; showGuide(); }
      showNoiseValue();
      update();
    });

    el.shift.min = signalConfig.shift.min;
    el.shift.max = signalConfig.shift.max;
    el.shift.step = 1;
    el.shift.value = shift;
    el.shift.addEventListener("input", () => setShift(Number(el.shift.value)));

    // Dragging the copy row. A drag starts after a few pixels of sideways movement, so a vertical swipe still scrolls the page.
    el.copyHit.addEventListener("pointerdown", (event) => {
      if (!result) return;
      drag = { id: event.pointerId, x: event.clientX, from: shift, started: false };
      el.copyHit.setPointerCapture(event.pointerId);
    });
    el.copyHit.addEventListener("pointermove", (event) => {
      if (!drag || event.pointerId !== drag.id) return;
      const moved = event.clientX - drag.x;
      if (!drag.started) {
        if (Math.abs(moved) < signalConfig.dragStartPx) return;
        drag.started = true;
        root.classList.add("is-dragging");
      }
      const chipPixels = (el.rows.getBoundingClientRect().width / ROWS_W) * CHIP;
      setShift(drag.from + Math.round(moved / chipPixels));
    });
    const endDrag = (event) => {
      if (!drag || event.pointerId !== drag.id) return;
      drag = null;
      root.classList.remove("is-dragging");
    };
    el.copyHit.addEventListener("pointerup", endDrag);
    el.copyHit.addEventListener("pointercancel", endDrag);

    el.search.addEventListener("click", search);
    // Any new input ends the reveal at once.
    for (const type of ["pointerdown", "keydown", "input"]) root.addEventListener(type, finishReveal, true);
    el.reset.addEventListener("click", () => {
      noise = startValue;
      el.slider.value = Math.round((startValue - min) / step);
      shift = signalConfig.shift.start;
      el.shift.value = shift;
      visited.clear();
      searched = false;
      guide = 1;
      el.msgSearch.textContent = "";
      el.bestDelay.textContent = "–";
      el.trueDelay.textContent = "–";
      el.peak.textContent = "–";
      el.badge.hidden = true;
      el.sentence.textContent = "";
      el.emptyLine.hidden = false;
      el.closeupNote.textContent = "";
      el.closeupBestTick.setAttribute("hidden", "");
      el.closeupBestLabel.hidden = true;
      el.fullBestTick.setAttribute("hidden", "");
      el.fullBestLabel.hidden = true;
      el.hint.hidden = false;
      el.msgReset.textContent = "";
      showNoiseValue();
      showGuide();
      setReveal("hidden");
      update();
      say(el.msgReset, "Back to the start: copy at 0, no noise.");
    });
    window.addEventListener("resize", placeAllLabels);
    showNoiseValue();
    setControlsDisabled(true);
  }

  function setControlsDisabled(disabled) {
    el.slider.disabled = disabled;
    el.shift.disabled = disabled;
    el.search.disabled = disabled;
    el.reset.disabled = disabled;
  }

  function showNoiseValue() {
    el.sliderValue.textContent = noise === 0 ? "No noise" : `${noise.toFixed(1)}× the signal`;
    el.slider.setAttribute("aria-valuetext", noise === 0 ? "No noise" : `Noise ${noise.toFixed(1)} times the signal`);
  }

  function showGuide() {
    root.dataset.guide = String(guide);
    el.hint.hidden = guide === 0;
    if (guide !== 0) {
      el.hint.textContent = GUIDE_WORDS[guide];
      el.hint.classList.add("is-shown"); // index.html's .hint rule fades it in only with this class
    }
  }

  function moveGuideTo(step) {
    if (guide !== 0 && step > guide) { guide = step; showGuide(); }
  }

  // Slide the copy to a whole number of chips. No Python call: the score is read from the last result.
  function setShift(value) {
    const { min, max } = signalConfig.shift;
    const next = Math.min(max, Math.max(min, Math.round(value)));
    if (next === shift) return;
    shift = next;
    el.shift.value = shift;
    visited.add(shift);
    if (shift === signalConfig.trueDelayChips) moveGuideTo(2);
    drawHand();
    drawCloseup();
  }

  // ---------- the search ----------

  function search() {
    if (!result) return;
    searched = true;
    moveGuideTo(3);
    drawResult();
    drawCloseup();
    drawFull();
    startReveal();
    say(el.msgSearch, `The phone tried all 1023 shifts. Its best match is at shift ${result.best_delay_chips}.`);
  }

  function reducedMotion() {
    return window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  }

  function setReveal(state) {
    el.closeupRestWrap.dataset.reveal = state;
    el.fullWrap.dataset.reveal = state;
  }

  // The plots are drawn left to right over about a second. The numbers are already on the page.
  function startReveal() {
    clearTimeout(revealTimer);
    if (reducedMotion()) { setReveal("done"); return; }
    setReveal("hidden");
    void root.offsetWidth; // let the browser see "hidden" first, so the change to "running" animates
    setReveal("running");
    revealTimer = setTimeout(() => setReveal("done"), signalConfig.revealMs);
  }

  function finishReveal() {
    if (!searched || el.fullWrap.dataset.reveal !== "running") return;
    clearTimeout(revealTimer);
    setReveal("done");
  }

  // ---------- one run: ask Python, then draw ----------

  // Python calls are async. If one is running, remember that a newer run is wanted and do it once after.
  async function update() {
    if (!callPython || !code) return;
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
    const heard = await callPython("signal.make_received", [prn, trueDelayChips, usedNoise, seed]);
    if (failed(heard)) return;
    const scored = await callPython("signal.correlate", [heard, prn]);
    if (failed(scored)) return;
    requestAnimationFrame(() => {
      received = heard;
      result = scored;
      drawAll(usedNoise);
    });
  }

  function failed(answer) {
    if (!answer || !answer.error) return false;
    say(el.msgSlider, answer.error); // Python's own plain sentence
    return true;
  }

  // ---------- reading the result ----------

  // "Lost" means the best shift is not the true delay. The threshold only separates ok from "barely".
  function levelOf(scored) {
    if (scored.best_delay_chips !== signalConfig.trueDelayChips) return "bad";
    return scored.peak_to_next < signalConfig.barelyHoldingBelow ? "warn" : "ok";
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

  function formatScore(value) {
    const text = value.toFixed(2);
    return text === "-0.00" ? "0.00" : text;
  }

  function chips(count) {
    return count === 1 ? "1 chip" : `${count} chips`;
  }

  // ---------- drawing ----------

  function drawAll(usedNoise) {
    drawRows(usedNoise);
    drawHand();
    drawCloseup();
    if (searched) { drawFull(); drawResult(); }
    placeAllLabels();
    // Noise peaks regularly pass the heard row's edge once the noise is more than half the row's range.
    el.clipNote.textContent = usedNoise * 2 > signalConfig.receivedLimit
      ? "The noise is now taller than the heard row, so its peaks are cut off at the top and bottom." : "";
  }

  // A square wave: each value is held for one step.
  function stepPoints(values, mid, unit) {
    const parts = [];
    values.forEach((value, index) => {
      const y = (mid - value * unit).toFixed(1);
      parts.push(`${index * CHIP},${y} ${(index + 1) * CHIP},${y}`);
    });
    return parts.join(" ");
  }

  function copyValue(index) {
    return code[(((index - shift) % CODE_LENGTH) + CODE_LENGTH) % CODE_LENGTH];
  }

  function drawRows(usedNoise) {
    const { windowChips, receivedLimit } = signalConfig;
    const unit = HALF / receivedLimit;
    const sent = code.slice(0, windowChips);
    const heard = received.slice(0, windowChips).map((v) => Math.min(receivedLimit, Math.max(-receivedLimit, v)));
    el.sentLine.setAttribute("points", stepPoints(sent, ROW_MID.sent, unit));
    el.receivedLine.setAttribute("points", stepPoints(heard, ROW_MID.heard, unit));
    shownNoise = usedNoise;
    drawCopyRow();
  }

  // The copy row: each step is a block, lit where its sign agrees with the heard value above it, dim where it does not.
  function drawCopyRow() {
    if (!code || !received) return;
    const unit = HALF / signalConfig.receivedLimit;
    let agree = 0;
    el.cells.forEach((cell, index) => {
      const value = copyValue(index);
      const lit = (value > 0) === (received[index] > 0);
      if (lit) agree += 1;
      cell.setAttribute("y", value > 0 ? ROW_MID.copy - unit : ROW_MID.copy);
      cell.classList.toggle("is-dim", !lit);
    });
    const x = shift * CHIP;
    el.bracket.style.display = shift === 0 ? "none" : "";
    el.bracketLine.setAttribute("d", `M0,196 V200 H${x} V196`);
    el.bracketText.setAttribute("x", x + 6);
    el.bracketText.textContent = `slid ${chips(shift)}`;
    const noiseWords = shownNoise ? `${shownNoise.toFixed(1)} times the signal` : "none";
    el.rows.setAttribute("aria-label",
      `Three rows of ${signalConfig.windowChips} steps. Top: what the satellite sends. Middle: what the phone hears, noise ${noiseWords}. `
      + `Bottom: the phone's own copy, slid ${chips(shift)}; ${agree} of ${signalConfig.windowChips} steps agree with what the phone hears.`);
  }

  function drawHand() {
    drawCopyRow();
    el.shiftValue.textContent = chips(shift);
    if (!result) return;
    const score = result.scores[shift];
    el.handScore.textContent = formatScore(score);
    el.meter.style.transform = `scaleX(${Math.min(1, Math.max(0, score))})`;
    el.shift.setAttribute("aria-valuetext", `Copy slid ${chips(shift)}. Match score ${formatScore(score)}.`);
    el.handSentence.textContent = shift === signalConfig.trueDelayChips
      ? `Lined up. You slid the copy ${chips(shift)}, so the signal arrived ${chips(shift)} late.`
      : "Not lined up yet. Keep sliding.";
  }

  // The readout, once the search has been pressed.
  function drawResult() {
    const level = levelOf(result);
    el.emptyLine.hidden = true;
    el.bestDelay.textContent = chips(result.best_delay_chips);
    el.trueDelay.textContent = chips(signalConfig.trueDelayChips);
    el.peak.textContent = formatPeak(result.peak_to_next);
    el.badge.hidden = false;
    el.badge.className = `badge is-${level}`;
    el.badge.textContent = levelWords[level];
    el.sentence.textContent = sentenceFor(level, noise);
  }

  function scoreY(value, height) {
    const { min, max } = signalConfig.scoreRange;
    const clamped = Math.min(max, Math.max(min, value));
    return height - ((clamped - min) / (max - min)) * height;
  }

  function bars(shifts) {
    const zero = scoreY(0, CLOSEUP_HEIGHT);
    return shifts.map((index) => {
      const y = scoreY(result.scores[index], CLOSEUP_HEIGHT);
      return `<rect class="bar" x="${index * CHIP + 1}" y="${Math.min(zero, y).toFixed(1)}" width="${CHIP - 2}" height="${Math.max(1, Math.abs(zero - y)).toFixed(1)}"/>`;
    }).join("");
  }

  // The first 40 shifts, close up. Before the search it holds only the shifts the user stopped on.
  function drawCloseup() {
    if (!result) return;
    const all = Array.from({ length: signalConfig.windowChips }, (_, index) => index);
    el.closeupTries.innerHTML = bars([...visited].filter((index) => index < signalConfig.windowChips));
    el.closeupRest.innerHTML = searched ? bars(all) : "";
    const best = result.best_delay_chips;
    const inside = searched && best < signalConfig.windowChips;
    el.closeupBestTick.toggleAttribute("hidden", !inside);
    el.closeupBestLabel.hidden = !inside;
    if (inside) {
      setLevelClass(el.closeupBestTick, levelOf(result));
      placeTick(el.closeupBestTick, el.closeupBestLabel, (best + 0.5) / signalConfig.windowChips);
    }
    el.closeupNote.textContent = searched && !inside
      ? `The phone's best match is now at shift ${best}, outside this close-up.` : "";
    const words = searched
      ? `Best match at shift ${best}; the real delay is ${signalConfig.trueDelayChips}.`
      : `Not searched yet; ${visited.size} shifts tried by hand.`;
    el.closeupTries.parentElement.setAttribute("aria-label", `Close-up of the match score at the first ${signalConfig.windowChips} shifts. ${words}`);
  }

  // All 1023 shifts.
  function drawFull() {
    if (!result) return;
    el.scoresLine.setAttribute("points", toPoints(result.scores));
    setLevelClass(el.fullBestTick, levelOf(result));
    el.fullBestTick.removeAttribute("hidden");
    el.fullBestLabel.hidden = false;
    placeTick(el.fullBestTick, el.fullBestLabel, result.best_delay_chips / CODE_LENGTH);
    el.fullSvg.setAttribute("aria-label",
      `${SCORES_LABEL} Best match at shift ${result.best_delay_chips}; the real delay is ${signalConfig.trueDelayChips}.`);
  }

  function setLevelClass(node, level) {
    node.classList.remove("is-ok", "is-warn", "is-bad");
    node.classList.add(`is-${level}`);
  }

  // One point per shift: x is the shift, y is the score scaled into the graph (cut off at the edges).
  function toPoints(values) {
    return values.map((value, index) => `${index},${scoreY(value, PLOT_HEIGHT).toFixed(1)}`).join(" ");
  }

  // The tick sits at its exact place (a percentage); its words are kept inside the plot's width.
  function placeTick(tick, label, fraction) {
    tick.dataset.at = String(fraction);
    tick.style.left = `${fraction * 100}%`;
    const lane = label.parentElement;
    const width = lane.clientWidth;
    if (!width || label.hidden) return;
    const labelWidth = label.offsetWidth;
    label.style.left = `${Math.min(width - labelWidth, Math.max(0, fraction * width - labelWidth / 2))}px`;
  }

  function placeAllLabels() {
    for (const [tick, label] of [
      [el.closeupRealTick, el.closeupRealLabel], [el.closeupBestTick, el.closeupBestLabel],
      [el.fullRealTick, el.fullRealLabel], [el.fullBestTick, el.fullBestLabel],
    ]) if (tick.dataset.at) placeTick(tick, label, Number(tick.dataset.at));
  }
}

function addStyleOnce() {
  if (document.getElementById("signal-step-style")) return;
  const style = document.createElement("style");
  style.id = "signal-step-style";
  style.textContent = STYLE;
  document.head.append(style);
}

// ---------- the small drawing (fixed sketch, no numbers) ----------

const SKETCH_PATTERN = [1, -1, -1, 1, 1, -1, 1, -1, -1, 1, -1, 1]; // twelve steps, only for the sketch
const SKETCH_LATE = 3; // the late copy in the sketch is three steps late

function sketchWave(values, mid, unit, offset = 0) {
  const parts = [];
  if (offset > 0) parts.push(`0,${mid} ${offset * 10},${mid}`);
  values.forEach((value, index) => {
    const y = mid - value * unit;
    parts.push(`${(index + offset) * 10},${y} ${(index + offset + 1) * 10},${y}`);
  });
  return parts.join(" ");
}

function sketchHtml() {
  const wave = (points, extra = "") => `<polyline class="${extra}" points="${points}"/>`;
  const late = SKETCH_PATTERN.slice(0, SKETCH_PATTERN.length - SKETCH_LATE);
  return `
  <div class="sketch">
    <div><svg class="figure" viewBox="0 0 120 40" role="img" aria-label="Sketch: the satellite's pattern, a row of high and low steps.">${wave(sketchWave(SKETCH_PATTERN, 20, 8))}</svg><p>1 The pattern</p></div>
    <div><svg class="figure" viewBox="0 0 120 40" role="img" aria-label="Sketch: the same pattern arriving a few steps late.">${wave(sketchWave(late, 20, 8, SKETCH_LATE))}</svg><p>2 It arrives late</p></div>
    <div><svg class="figure" viewBox="0 0 120 40" role="img" aria-label="Sketch: the phone's copy slid until it lines up with the late pattern.">${wave(sketchWave(late, 11, 6, SKETCH_LATE), "dim")}${wave(sketchWave(late, 29, 6, SKETCH_LATE))}</svg><p>3 Slide your copy until it lines up</p></div>
  </div>`;
}

function rowsHtml() {
  const rowName = (name, y) => `<text class="row-name" x="0" y="${y}">${name}</text>`;
  return `
  <svg class="rows" data-el="rows" viewBox="0 0 ${ROWS_W} 212" role="img" aria-label="Three rows of steps.">
    ${rowName("What the satellite sends", 11)}
    <polyline class="sent" data-el="sent-line" points=""/>
    ${rowName("What the phone hears", 73)}
    <polyline class="received" data-el="received-line" points=""/>
    ${rowName("The phone's own copy", 135)}
    <g data-el="copy-cells"></g>
    <rect class="copy-outline" x="-1" y="${ROW_MID.copy - HALF - 2}" width="${ROWS_W + 2}" height="${HALF * 2 + 4}" rx="3"/>
    <g data-el="bracket"><path class="bracket" data-el="bracket-line" d=""/><text class="bracket-text" data-el="bracket-text" y="207"></text></g>
    <rect class="copy-hit" data-el="copy-hit" x="0" y="${ROW_MID.copy - 32}" width="${ROWS_W}" height="64"/>
  </svg>`;
}

// A tick above (real delay) or below (the phone's best match) a plot, with its words.
function laneHtml(where, name, words, markClass) {
  return `<div class="lane lane-${where}"><span class="tick-label" data-el="${name}-label"${where === "bottom" ? " hidden" : ""}>${words}</span>
    <svg class="tick ${where === "bottom" ? "is-ok" : ""}" data-el="${name}-tick" aria-hidden="true" ${where === "bottom" ? "hidden" : ""}><line class="${markClass}" x1="1" x2="1" y1="0" y2="12"/></svg></div>`;
}

const PAGE_HTML = `
<section class="signal-step" aria-labelledby="signal-title" data-guide="1">
  <header class="intro">
    <h2 id="signal-title">How does the phone measure the time?</h2>
    <p class="muted">Every satellite repeats a pattern the phone already knows. The phone slides its own copy along what it hears. How far it has to slide is how late the signal arrived.</p>
  </header>

  <div class="grid">
    <div class="card">
      <h3 class="label">Try it by hand</h3>
      <p class="looking"><b>What you're looking at:</b> 40 steps of one satellite's pattern (the whole pattern has 1023). Top: what the satellite sends. Middle: what the phone hears, a little later. Bottom: the phone's own copy. Slide it.</p>
      ${sketchHtml()}
      ${rowsHtml()}
      <p class="key muted" data-el="clip-note" role="status" aria-live="polite"></p>

      <div class="guide-block g1">
        <div class="slider-head"><label for="signal-shift">Slide the phone's copy</label><span class="num" data-el="shift-value">0 chips</span></div>
        <input id="signal-shift" data-el="shift" type="range" disabled>
      </div>
      <div class="inset readout">
        <div class="hand-score"><span class="label">Match score</span><span class="num big" data-el="hand-score">–</span></div>
        <div class="meter" aria-hidden="true"><div class="meter-fill" data-el="meter"></div></div>
        <p class="note">Counted over the whole 1023-step pattern, not only the 40 steps shown. 1.00 means every step agrees. Near 0 means no better than chance.</p>
        <p class="note" data-el="hand-sentence" role="status" aria-live="polite">Not lined up yet. Keep sliding.</p>
      </div>
      <p class="note">Here the delay is short so it fits in the picture. A real one can be anywhere in the 1023 steps.</p>

      <h3 class="label">Now let the phone search</h3>
      <div class="guide-block g2">
        <div><button class="btn" data-el="search" type="button" disabled>Let the phone try every shift</button></div>
        <p class="note" data-el="msg-search" role="status" aria-live="polite"></p>
      </div>

      <p class="plot-title">The first 40 shifts, close up</p>
      <div class="plot-lanes">
        ${laneHtml("top", "closeup-real", "real delay", "mark-true")}
        <div class="plot-area plot-close">
          <div data-el="closeup-rest-wrap" data-reveal="hidden"><svg viewBox="0 0 ${ROWS_W} ${CLOSEUP_HEIGHT}" preserveAspectRatio="none" height="60" width="100%" aria-hidden="true"><g data-el="closeup-rest"></g></svg></div>
          <svg class="overlay" viewBox="0 0 ${ROWS_W} ${CLOSEUP_HEIGHT}" preserveAspectRatio="none" height="60" width="100%" role="img" aria-label="Close-up of the match score at the first 40 shifts."><g data-el="closeup-tries"></g></svg>
        </div>
        ${laneHtml("bottom", "closeup-best", "phone's best match", "mark-best")}
      </div>
      <p class="note" data-el="closeup-note" role="status" aria-live="polite"></p>

      <p class="plot-title">All 1023 shifts</p>
      <div class="plot-lanes">
        ${laneHtml("top", "full-real", "real delay", "mark-true")}
        <div class="plot-area plot-full" data-el="full-wrap" data-reveal="hidden">
          <svg data-el="scores-plot" viewBox="0 0 1023 ${PLOT_HEIGHT}" preserveAspectRatio="none" height="96" width="100%" role="img" aria-label="The match score at every one of the 1023 shifts."><polyline class="scores" data-el="scores-line" points=""/></svg>
        </div>
        ${laneHtml("bottom", "full-best", "phone's best match", "mark-best")}
      </div>
      <div class="axis" aria-hidden="true"><span>shift 0</span><span>shift 1022</span></div>
    </div>

    <div class="card stack">
      <p class="note" data-el="status" role="status" aria-live="polite">Loading the maths…</p>
      <p class="hint" data-el="hint" hidden></p>
      <div class="slider inset guide-block g3">
        <div class="slider-head">
          <label for="signal-noise">Add noise</label>
          <span class="num" data-el="noise-value">No noise</span>
        </div>
        <input id="signal-noise" data-el="noise" type="range" disabled>
        <p class="note" data-el="msg-slider" role="status" aria-live="polite"></p>
      </div>

      <div class="inset readout">
        <span class="label">Best match found at</span>
        <span class="num big" data-el="best-delay">–</span>
        <div class="readout-row"><span class="muted">Real delay</span><span class="num" data-el="true-delay">–</span></div>
        <div class="readout-row"><span class="muted">Best score is this many times the runner-up</span><span class="num" data-el="peak">–</span></div>
        <div><span class="badge is-ok" data-el="badge" hidden></span></div>
        <p class="note" data-el="empty-line">Press the button and the phone searches.</p>
        <p class="note" data-el="sentence" role="status" aria-live="polite"></p>
      </div>

      <div>
        <button class="btn" data-el="reset" type="button" disabled>Reset</button>
        <p class="note" style="margin-top: var(--s-2)" data-el="msg-reset" role="status" aria-live="polite"></p>
      </div>
    </div>
  </div>
</section>`;
