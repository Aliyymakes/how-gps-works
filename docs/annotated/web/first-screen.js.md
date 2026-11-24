# first-screen.js, line by line

Source: `web/first-screen.js`

## What this file is for
This is the code behind the first screen of the page: a clock slider, a "solve" button, four satellite switches and a small ground map. It reads what the visitor does, asks the Python mechanism for the numbers, and draws the answer: lines on the map, a dot, a readout in metres and plain sentences. It does no satellite maths of its own.

## Which files it talks to
- [`web/theme.js`](theme.js.md): gives `loadSavedTheme` (light or dark look) and `trackPointerLight` (a soft glow that follows the mouse over cards).
- [`web/config.js`](config.js.md): the placeholder numbers (where the phone is, the four satellites, map size, slider range, colour limits).
- [`web/startup.js`](startup.js.md): gives `whenPythonReady`, which waits until Python has loaded and shows the loading and failure words.
- [`web/say.js`](say.js.md): gives `say`, which writes a sentence into a message line and flashes it.
- [`web/format.js`](format.js.md): gives `formatMetres`, the one rule for showing a distance in metres.
- [`index.html`](../index.html.md): holds every element this file looks up by its `id` (the slider, buttons, map, message lines, hints). Layout and fades for the classes used here are in its `<style>` part; the colours come from [`web/theme.css`](theme.css.md).
- [`web/bridge.js`](bridge.js.md): not imported here. [`startup.js`](startup.js.md) loads it, and the `call` function it hands over is what this file calls `callPython`.
- Python functions it calls, by name: `coords.latlon_to_xyz` ([coords.py](../mechanism/coords.py.md)), `coords.satellite_from_sky` ([coords.py](../mechanism/coords.py.md)), `scenario.make_pseudoranges` ([scenario.py](../mechanism/scenario.py.md)), `solver.solve_position` ([solver.py](../mechanism/solver.py.md)), `mapview.to_local` and `mapview.distance_lines` ([mapview.py](../mechanism/mapview.py.md)). The shapes of what goes in and comes out are in `docs/interface.md`.

## In three lines
1. When Python is ready, ask it where the phone and the four satellites are, then switch the controls on.
2. Every time the visitor moves the slider, presses a button or flips a switch, ask Python for the measured distances, the solved position and the distance lines, then draw them.
3. Show a guided path of hints (slider, then button, then switches) and, on a mouse or touch press of the solve button, glide the lines together.

New to code? See [how to read code](../how-to-read-code.md). Browser ideas are explained here the first time they appear.

## The code, line by line

```js
// The first screen (design.md 2b). It draws and takes input; every number comes from Python.
// The only arithmetic here: Math.hypot for the position error, and the map's metres-to-pixels scaling.
```
Two comments (a comment is a note for people; the computer skips it). They say this file draws and takes input, and that all numbers come from Python. The only maths done in the browser is `Math.hypot`, which gives the length of the position error, and the scaling from metres to map pixels. "design.md 2b" points at the team's design spec. Without the comments nothing breaks.

```js
import { trackPointerLight, loadSavedTheme } from "./theme.js";
```
Brings in two functions from [`theme.js`](theme.js.md). `loadSavedTheme` sets the page to the light or dark look the visitor chose last time, and `trackPointerLight` makes the card glow follow the mouse. `import` is how one file borrows from another (see [An import](../how-to-read-code.md#an-import)). Without this line the two calls near the bottom would fail.

```js
import * as config from "./config.js";
```
Brings in everything from [`config.js`](config.js.md) under one name, `config`. `import * as config` means "all the exported things, gathered under the name `config`". Later lines write `config.receiver` or `config.mapHalfWidthM`. Without it the page would not know where the phone or the satellites are.

```js
import { whenPythonReady } from "./startup.js";
```
Brings in `whenPythonReady` from [`startup.js`](startup.js.md). The page runs the maths in Python inside the browser, and that takes a few seconds to download. This function waits for it. Without it the page could ask Python for answers before Python exists.

```js
import { say } from "./say.js";
```
Brings in `say`, which puts a sentence into a message line on the page and flashes it briefly, so pressing something always gives a visible reply. Without it no message could be shown.

```js
import { formatMetres } from "./format.js";
```
Brings in `formatMetres`, which turns a number such as 3.14159 into the text `3.1 m` (one decimal place below 100 m, whole metres above, with thousands separators). Without it the error readout would show raw numbers.

```js
const SVG = "http://www.w3.org/2000/svg";
```
A name for the web address `http://www.w3.org/2000/svg`. SVG is the browser's way of drawing shapes (lines, circles) inside the page. To create an SVG shape from code the browser must be told that address, which acts as a label meaning "this is an SVG shape, not an ordinary page element". `const` means the name never changes. It is used twice below, to make map lines and the cross mark. Without it those shapes would not appear.

```js
const MAP_SIZE = 400; // the SVG viewBox is 400 by 400
```
The map is drawn in a square that is 400 units wide and 400 units tall (the comment says this matches the SVG `viewBox`, the SVG's own coordinate box in [`index.html`](../index.html.md)). It is the number used to turn metres into map positions later. Without it the scaling lines could not work.

```js
const $ = (id) => document.getElementById(id);
```
Makes a tiny shortcut named `$`. `$("clock")` means "find the element on the page whose `id` is `clock`". The DOM is the browser's live model of the page: every heading, button and slider is an element in it, and `document.getElementById` fetches one by its `id` (a unique name written in [`index.html`](../index.html.md)). The `(id) => ...` part is a short way to write a function: it takes `id` and hands back the element. Without it every lookup would be written out in full.

```js
const el = {
  status: $("status"), slider: $("clock"), sliderValue: $("clock-value"),
  errorValue: $("error-value"), badge: $("error-badge"), solve: $("solve"), reset: $("reset"),
  switches: $("switches"), lines: $("map-lines"), map: $("map"), dot: $("map-dot"), caption: $("map-caption"),
  msgSlider: $("msg-slider"), msgReadout: $("msg-readout"), msgSolve: $("msg-solve"), msgSwitch: $("msg-switch"), msgReset: $("msg-reset"),
};
```
One object named `el` (short for "elements") that collects every element this file needs, looked up once so the code can reuse it. An object is a set of labelled values, here `name: value` pairs. Reading the lines in order: the status line, the clock slider, the text that shows the slider value, the error number, the good/bad badge, the solve and reset buttons, the box holding the satellite switches, the box that will hold the distance lines, the whole map, the dot that marks the phone's position, and the line of words under the map. The last line holds the five message lines (under the slider, under the readout, under the solve button, under the switches, under reset). If an `id` is misspelled, the lookup gives `null` and the first use of that element would fail.

```js
let callPython = null; // set when the bridge has loaded
```
A variable named `callPython`, empty (`null`) for now. `let` means the value can change later. It will hold the function that sends a request to Python, once Python has loaded. Checking whether it is still `null` is how the page knows Python is not ready.

```js
let receiverPoint = null; // true receiver position, from Python
```
A variable for where the phone really is, as three numbers (x, y, z, in metres from the Earth's centre). It starts empty and is filled by Python. The map's centre cross marks this spot.

```js
let allSatellites = []; // from Python, with ids from config.js
```
A list (an array) of satellites. It starts empty, and is filled later with each satellite's id and its three position numbers. `[]` is an empty list.

```js
const state = { clockErrorS: 0, mode: "trusted", on: config.satellites.map(() => true) };
```
The page's current settings, kept together in one object `state`. `clockErrorS: 0` is the phone's clock error in seconds, starting at zero. `mode: "trusted"` means the phone believes its clock (the other mode is `"solved"`). `on` is a list of four `true` values, one per satellite: `config.satellites.map(() => true)` takes the list of satellites and makes a same-length list where every entry is `true`, meaning all satellites are switched on. Without `state` the page would forget what the visitor chose.

```js
let running = false;
```
A yes/no variable `running`. It is `true` while a request to Python is in progress. It stops two requests from running at the same time.

```js
let rerun = false;
```
A yes/no variable `rerun`. It is set to `true` when the visitor does something new while a request is already running, so the page remembers to run once more afterwards.

```js
let lastCause = "start"; // what the newest wanted run is about
```
Remembers what the newest wanted run is about: `"start"`, `"slider"`, `"solve"`, `"switch"` and so on. The words decide which message line is used and what is said. It starts as `"start"`.

```js
let lastAnimate = false; // true when the newest run came from a mouse or touch press on the solve button
```
Remembers whether the newest run came from a real mouse or touch press on the solve button by a visitor who has not asked for less motion. That is the only case that plays the gliding animation.

```js
let guideStep = 1; // 1 slider, 2 solve button, 3 satellite switches, 4 done
```
Which hint is showing in the guided path: 1 for the slider, 2 for the solve button, 3 for the satellite switches, 4 for finished. It starts at 1.

```js
const lastPoints = new Map(); // pixel points last drawn for each distance line, by id
```
A `Map`, which is like a dictionary: it stores a value under a key. Here the key is a satellite's id and the value is the list of map points that were last drawn for its distance line. It is kept so that the glide knows where each line was before. `new Map()` makes an empty one.

```js
let lastDot = null; // pixel position of the dot, or null while it is hidden
```
The map position of the dot as last drawn, `{ x, y }`, or `null` while the dot is hidden. Used by the glide to know where the dot starts.

```js
let glideFrame = 0;
```
A number that remembers the id of the next animation frame the glide has asked for (0 means none). It is needed so the glide can be stopped half way.

```js
let glideFinish = null; // draws the end of a running glide at once
```
A slot for a small function that draws the end of a running glide at once. It is `null` when no glide is running. It lets a new run skip ahead to the final picture instead of leaving a half-moved line.

```js
loadSavedTheme();
trackPointerLight();
setupControls();
drawTrueMark();
start();
```
Five calls that run once, when the file loads, in this order. `loadSavedTheme()` sets light or dark. `trackPointerLight()` starts the card glow. `setupControls()` prepares the slider and switches and listens for clicks. `drawTrueMark()` draws the small cross that marks the phone's real position. `start()` begins waiting for Python. Calling a function means running its steps. These are the function names that are defined further down; JavaScript lets a function be used above the place it is written. Without these calls nothing would happen.

```js
// ---------- start up ----------
```
A comment used as a heading to group the functions that follow. The rows of dashes are only decoration.

```js
function start() {
  whenPythonReady(el.status, async (call) => {
    callPython = call;
```
Starts the function `start`. It calls `whenPythonReady`, giving it two things: the status line (where loading words and errors are shown) and a function to run when Python is ready. That second function is written `async (call) => { ... }`. `async` means it may pause to wait for slow things. The first line inside stores the received `call` function in `callPython`, so the rest of the file can ask Python for things.

```js
    try {
      await buildScene();
    } catch (error) {
```
`try` means "attempt this and, if it fails, jump to the `catch` part". `await buildScene()` runs `buildScene` (written below) and waits for it to finish. `await` pauses this function until a slow step is done, without freezing the page. `buildScene` asks Python where the phone and the satellites are.

```js
      console.error(error);
      el.status.textContent = "Python loaded, but the satellites could not be set up, so the controls stay off. Reload the page to try again.";
      return;
    }
```
The `catch` part runs if `buildScene` failed. It writes the error to the browser's developer log with `console.error` (a place for programmers to look, not shown to the visitor). It then puts a plain sentence in the status line: "Python loaded, but the satellites could not be set up, so the controls stay off. Reload the page to try again." `return` stops the function right there, so the next lines do not run and the controls stay off. Without this block a failure would leave the visitor with no explanation.

```js
    setControlsDisabled(false);
    showGuide();
    update("start");
  });
}
```
If setup worked: `setControlsDisabled(false)` switches the slider, buttons and satellite switches on, `showGuide()` shows the first hint, and `update("start")` does the first calculation and drawing. The closing brackets end the ready-function, the call to `whenPythonReady`, and the function `start`. Without these lines the page would load and then do nothing.

```js
async function buildScene() {
```
Starts `buildScene`, also `async` so it can wait for Python. It sets up the phone's and the satellites' positions.

```js
  const { lat_deg, lon_deg } = config.receiver;
```
Takes the latitude and longitude of the phone out of `config.receiver` as two named values. The `{ lat_deg, lon_deg }` form is called destructuring: it picks named items out of an object in one step. In [`config.js`](config.js.md) they are -6.2 and 106.8 degrees (Jakarta). Without them Python could not be asked where the phone is.

```js
  receiverPoint = await callPython("coords.latlon_to_xyz", [lat_deg, lon_deg]);
```
Asks Python to turn latitude and longitude into x, y, z metres from the Earth's centre. `callPython("coords.latlon_to_xyz", [lat_deg, lon_deg])` means: call the Python function `latlon_to_xyz` in [`coords.py`](../mechanism/coords.py.md) with those two numbers, and wait (`await`) for the answer. See [coords.py](../mechanism/coords.py.md). The answer is stored in `receiverPoint`.

```js
  if (receiverPoint.error) throw new Error(receiverPoint.error);
```
If Python's answer contains an `error` message, stop by raising a `new Error(...)` with Python's own sentence. `throw` jumps out of the function to the `catch` in `start`. Without this check a bad answer would be used as if it were a position.

```js
  allSatellites = [];
```
Empties the satellite list, so building the scene twice never doubles it.

```js
  for (const sat of config.satellites) {
```
A loop: it repeats the lines inside the braces once for each item in `config.satellites`, calling the current item `sat`. There are four items in [`config.js`](config.js.md).

```js
    const point = await callPython("coords.satellite_from_sky", [lat_deg, lon_deg, sat.azimuth_deg, sat.elevation_deg]);
```
Asks Python where that satellite is: `coords.satellite_from_sky` is given the phone's latitude and longitude, and the satellite's compass direction (`azimuth_deg`) and height above the horizon (`elevation_deg`). It returns x, y, z in metres. See [coords.py](../mechanism/coords.py.md). Worked example: satellite 1 has azimuth 10 degrees and elevation 60 degrees (from [`config.js`](config.js.md)), so it is nearly north and high in the sky.

```js
    if (point.error) throw new Error(point.error);
```
The same error check as before, for this satellite.

```js
    allSatellites.push({ id: sat.id, ...point });
```
Adds the satellite to the list. `{ id: sat.id, ...point }` makes a new object with the satellite's `id` (such as `"1"`) followed by everything Python returned (`x_m`, `y_m`, `z_m`). The three dots `...` mean "copy all the items of this object in here". `push` adds to the end of the list. Without this the list stays empty and no distances could be made.

```js
  }
}
```
These close the loop and the function `buildScene`.

```js
// ---------- controls ----------
```
A heading comment for the controls.

```js
function setupControls() {
  const { min_s, max_s, step_s } = config.clockSlider;
```
Starts `setupControls`. It takes the slider's smallest value, largest value and step out of `config.clockSlider`: 0 seconds, 0.000003 seconds (3 microseconds) and 0.00000005 seconds (0.05 microseconds). A microsecond is one millionth of a second.

```js
  // The slider counts steps (whole numbers), so there are no floating point surprises.
  el.slider.min = 0;
  el.slider.max = Math.round((max_s - min_s) / step_s);
  el.slider.step = 1;
  el.slider.value = 0;
```
The comment explains the plan: the slider counts whole steps rather than seconds, so no tiny decimal errors creep in. The lines set the slider's properties on the page: `min` is 0 and `max` is `Math.round((max_s - min_s) / step_s)`. Worked example: (0.000003 - 0) / 0.00000005 = 60, so `max` is 60 and the slider has 61 positions (0 to 60). `Math.round` makes a whole number out of any tiny decimal fuzz. `step` is 1 and the starting `value` is 0. A property is a named setting on an element, and these ones control the slider. Without them the slider would run from the browser's default of 0 to 100.

```js
  showClockValue();
```
Writes the slider's current clock value as text next to it (`showClockValue`, defined below). At the start it shows `0.00 µs`.

```js
  config.satellites.forEach((sat, index) => {
    const label = document.createElement("label");
    label.className = "toggle";
    label.innerHTML = '<input type="checkbox" checked disabled><span class="toggle-track"></span>';
    label.append(`Satellite ${sat.id}`);
```
Makes one switch for each satellite. `forEach` runs the steps once per satellite, with its position number `index` (0 to 3). `document.createElement("label")` creates a new, empty `<label>` element in memory. `label.className = "toggle"` gives it a class, a name the stylesheet uses to style it. `label.innerHTML = ...` fills it with HTML text: a checkbox that starts `checked` and `disabled` (not usable until Python is ready), followed by an empty `<span>` that the stylesheet draws as the switch track. `label.append(...)` adds the text, such as `Satellite 1`, after them. The backticks `` ` `` make a template string: `${sat.id}` is replaced by the id.

```js
    label.querySelector("input").addEventListener("change", (event) => {
      state.on[index] = event.target.checked;
      update("switch");
    });
```
`label.querySelector("input")` finds the checkbox inside the label. `addEventListener("change", ...)` says: when the visitor ticks or unticks it (an event is something the visitor does that the page can react to), run this function. The function stores whether the box is ticked (`event.target.checked`, `true` or `false`) in `state.on` at this satellite's position, then calls `update("switch")` to recalculate and redraw. Without this the switches would do nothing.

```js
    el.switches.append(label);
  });
```
Puts the finished label into the switches box on the page. The last lines close the `forEach`.

```js
  el.slider.addEventListener("input", () => {
    const wasSolved = state.mode === "solved";
    state.clockErrorS = Number(el.slider.value) * config.clockSlider.step_s + config.clockSlider.min_s;
```
Listens for the `input` event on the slider, which fires continuously while the slider is dragged or moved by the keyboard. `wasSolved` remembers whether the page was in the "solved" mode just before this move. Then the clock error is computed from the slider position: `Number(el.slider.value) * step_s + min_s`. `Number(...)` turns the slider's text value into a number. Worked example: at position 10, the clock error is 10 x 0.00000005 + 0 = 0.0000005 s, which is 0.5 microseconds. Without this the slider would not change the clock error.

```js
    state.mode = "trusted"; // moving the slider again goes back to trusting the clock
    showMode();
    showClockValue();
    update(wasSolved ? "slider-back" : "slider");
  });
```
The mode goes back to `"trusted"`, because moving the slider again means "trust the clock". `showMode()` updates the button, `showClockValue()` updates the microsecond text, and `update(...)` redraws. The cause given is `"slider-back"` if the page had been solved, otherwise `"slider"`. `a ? b : c` is a short if-else: pick `b` when `a` is true, otherwise `c`. The cause decides which message is shown. The `});` closes the listener.

```js
  el.solve.addEventListener("click", (event) => {
    state.mode = "solved";
    showMode();
```
Listens for a click on the solve button. The function receives the click `event`. It sets the mode to `"solved"` and updates the button's look with `showMode()`.

```js
    // Keyboard presses have detail 0 and are never animated.
    const calm = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    update("solve", event.detail > 0 && !calm);
  });
```
The comment says a keyboard press has `detail` 0 and is never animated (a real mouse or touch click has `detail` of 1 or more). `window.matchMedia("(prefers-reduced-motion: reduce)").matches` asks the browser whether the visitor has asked their device to avoid movement; `calm` is `true` if so. `update("solve", event.detail > 0 && !calm)` redraws, and its second value is `true` only for a real press when the visitor has not asked for less motion (`&&` means "and", `!` means "not"). So the glide plays only for those. Without this check, keyboard users and people who want less movement would be shown the animation.

```js
  el.reset.addEventListener("click", resetAll);
  setControlsDisabled(true);
}
```
The reset button runs `resetAll` when clicked. `setControlsDisabled(true)` switches the controls off until Python is ready. Without it the visitor could press buttons before Python can answer. The `}` ends `setupControls`.

```js
function setControlsDisabled(disabled) {
  el.slider.disabled = disabled;
  el.solve.disabled = disabled;
  el.reset.disabled = disabled;
  el.switches.querySelectorAll("input").forEach((box) => { box.disabled = disabled; });
}
```
`setControlsDisabled` takes `disabled` (`true` or `false`) and applies it to the slider, the solve button, the reset button and every checkbox. `querySelectorAll("input")` finds all the checkboxes inside the switches box, and `forEach` visits each one (`box`). A disabled control is greyed out and cannot be used. Without it the controls could not be switched off and on.

```js
function resetAll() {
  state.clockErrorS = 0;
  state.mode = "trusted";
  state.on = config.satellites.map(() => true);
  el.slider.value = 0;
  el.switches.querySelectorAll("input").forEach((box) => { box.checked = true; });
```
`resetAll` puts everything back to the start: clock error 0, mode `"trusted"`, a fresh list of four `true` values for `state.on`, the slider back to 0, and every checkbox ticked (`box.checked = true`).

```js
  showMode();
  showClockValue();
  update("reset");
}
```
Then `showMode()` and `showClockValue()` refresh the button and the text, and `update("reset")` redraws. The closing brace ends the function.

```js
// The solve button shows which mode the page is in (design: a state, not the next action, once solved).
function showMode() {
```
The comment says the solve button shows which mode the page is in, as a state rather than as the next action, once solved. Then `showMode` starts.

```js
  const solved = state.mode === "solved";
  el.solve.setAttribute("aria-pressed", String(solved));
  el.solve.textContent = solved ? "The phone is solving for its clock" : "Let the phone solve for its clock";
```
`solved` is `true` when the mode is `"solved"`. `setAttribute("aria-pressed", String(solved))` sets an `aria-` attribute, which is extra information for screen readers (software that reads the page aloud to blind visitors). `aria-pressed` tells it whether the button is switched on, and `String(solved)` turns `true`/`false` into the words "true"/"false". The next line sets the button text: if solved, `The phone is solving for its clock`, otherwise `Let the phone solve for its clock`.

```js
  el.solve.classList.toggle("btn-primary", !solved);
}
```
`classList.toggle("btn-primary", !solved)` adds the class `btn-primary` (the prominent button look) when not solved and removes it when solved. So the button looks like a call to action only before it has been pressed. The `}` ends the function.

```js
function showClockValue() {
  el.sliderValue.textContent = formatMicroseconds(state.clockErrorS);
  el.slider.setAttribute("aria-valuetext", el.sliderValue.textContent);
```
`showClockValue` writes the clock error as text, using `formatMicroseconds` (below), and then copies that same text to the slider's `aria-valuetext` attribute so a screen reader says `0.50 µs` rather than the raw step number.

```js
}
```
Ends `showClockValue`.

```js
// ---------- one run: ask Python, then draw ----------

// Python calls are async. If one is running, remember that a newer run is wanted and do it once after.
```
A heading comment, then a comment explaining the plan. Python calls take time (they are async), so if a run is going and the visitor does something new, the page notes that a newer run is wanted and does it once after, instead of starting several at once.

```js
async function update(cause, animate = false) {
  if (!callPython) return;
```
Starts `update`, `async`. It takes the reason `cause` and a yes/no `animate` that defaults to `false` (`animate = false`). `if (!callPython) return;` means: if Python is not ready, do nothing and leave. `!` means "not".

```js
  cancelGlide();
  lastCause = cause;
  lastAnimate = animate;
  if (running) { rerun = true; return; }
```
`cancelGlide()` finishes any glide in progress. The next two lines remember the newest `cause` and `animate`. `if (running) { rerun = true; return; }` says: if a run is already going, just note that another is wanted and leave. The running one will pick it up. Without this, two runs could overlap and an old answer could be drawn over a new one.

```js
  running = true;
  try {
    do {
      rerun = false;
      try {
        await runOnce(lastCause);
```
`running = true` marks that a run has begun. The outer `try` begins a guarded block (its `finally` is at the end of the function). `do { ... } while (rerun)` is a loop that runs at least once and repeats while `rerun` is `true`. Inside, `rerun` is set to `false`, then a second `try` guards `await runOnce(lastCause)`, which does one full calculation and drawing, using the newest cause.

```js
      } catch (error) {
        console.error(error);
        say(el.msgSolve, "Something went wrong in the calculation. Press Reset to start again.");
        hideAllLines();
        showNoFix();
      }
    } while (rerun);
```
If `runOnce` fails, the inner `catch` logs the error, shows `Something went wrong in the calculation. Press Reset to start again.` in the solve message line, hides every distance line and clears the position readout. The `while (rerun)` then repeats the loop if another run was asked for in the meantime. Without the inner catch, one failure would end the whole update and leave the page frozen.

```js
    if (lastCause === "reset") say(el.msgReset, "Back to the start: clock right, all four satellites on.");
  } finally {
    running = false;
  }
}
```
After the loop: if the last cause was `"reset"`, say `Back to the start: clock right, all four satellites on.` in the reset message line. The `finally` block always runs, error or not, and sets `running` back to `false`. Without `finally` a crash would leave `running` stuck on `true` and the page would never update again.

```js
async function runOnce(cause) {
  const solveClock = state.mode === "solved";
```
`runOnce` does one calculation and one drawing. `solveClock` is `true` when the mode is `"solved"`.

```js
  const sats = allSatellites.filter((_, i) => state.on[i]);
```
Builds the list of satellites that are switched on. `filter` keeps an item when the test is true. `(_, i)` means "ignore the item, use only its position `i`", and `state.on[i]` is `true` when that satellite's switch is on. So switching off satellite 3 leaves satellites 1, 2 and 4.

```js
  const slot = { slider: el.msgSlider, "slider-back": el.msgSlider, switch: el.msgSwitch }[cause] || el.msgSolve;
```
Picks which message line this run writes to. The object maps a cause to a line: `"slider"` and `"slider-back"` to the slider line, `"switch"` to the switch line. `[cause]` looks up the cause. `|| el.msgSolve` means "or, if there is no match, use the solve line", which is the case for `"solve"`, `"reset"` and `"start"`.

```js
  clearMessages();
  if (cause === "slider-back") say(el.msgSlider, "Back to trusting the clock. Press the button below to solve for it again.");
```
`clearMessages()` empties every message line, so old sentences do not stay. If the cause is `"slider-back"`, the slider line says `Back to trusting the clock. Press the button below to solve for it again.`

```js
  if (sats.length < (solveClock ? 4 : 3)) {
    await refuse(sats, solveClock, slot); // the page decides by itself: the solver cannot work here
    return;
  }
```
Checks whether enough satellites are on. `solveClock ? 4 : 3` is 4 when solving for the clock (x, y, z and the clock are four unknowns) and 3 when trusting it. If there are fewer, `await refuse(...)` shows the explanation and the lines (see below), and `return` ends the run, so Python's solver is never asked to do something that cannot work. The comment says the page decides this itself.

```js
  const ranges = await callPython("scenario.make_pseudoranges", [receiverPoint, sats, state.clockErrorS]);
  if (failed(ranges, slot)) return;
```
Asks Python for the measured distances: `scenario.make_pseudoranges` gets the phone's true position, the satellites that are on, and the clock error in seconds, and returns one measured distance (in metres) per satellite. A pseudorange is a distance that includes the clock error. See [scenario.py](../mechanism/scenario.py.md). Then `failed(ranges, slot)` checks for an error answer. If so it shows the message and the code stops with `return`.

```js
  const solution = await callPython("solver.solve_position", [sats, ranges, solveClock]);
  if (failed(solution, slot)) return;
```
Asks Python to work out the position: `solver.solve_position` gets the satellites, the measured distances and `solveClock` (`true` or `false`, which becomes Python's `True` or `False`). It returns x, y, z and the clock error, and says whether it settled. See [solver.py](../mechanism/solver.py.md). Another error check follows.

```js
  const { lat_deg, lon_deg } = config.receiver;
  const point = { x_m: solution.x_m, y_m: solution.y_m, z_m: solution.z_m };
  const local = await callPython("mapview.to_local", [lat_deg, lon_deg, point]);
  if (failed(local, slot)) return;
```
Takes the phone's latitude and longitude again, and picks the solved x, y, z out of `solution` into `point`. `mapview.to_local` turns that point into metres east, north and up from the true position, which is easier to draw on a ground map. See [mapview.py](../mechanism/mapview.py.md). Worked example: a solved point 3 m east, 4 m north and 12 m up from the true position. The error check follows.

```js
  const assumedClockS = solveClock ? solution.clock_error_s : 0;
  const lines = await callPython("mapview.distance_lines", [lat_deg, lon_deg, sats, ranges, assumedClockS, config.mapHalfWidthM, config.lineSamples]);
  if (failed(lines, slot)) return;
```
`assumedClockS` is the clock error the page tells Python to subtract when drawing the lines: Python's solved clock error when solving, otherwise 0 (the phone trusts its clock). Then `mapview.distance_lines` is asked for the lines: for each satellite, the points on the ground where its measured distance would put the phone. Its inputs are the phone's latitude and longitude, the satellites, the distances, `assumedClockS`, the map half-width (1000 m) and the number of sample points (40). Python spreads those 40 points along the part of each line near the map and keeps only the ones that land inside it, so a line comes back with fewer points (with the page's numbers, 26 to 32) or none. It returns one entry per satellite with `id`, `points` and `inside`. See [mapview.py](../mechanism/mapview.py.md). Another error check follows.

```js
  const errorM = Math.hypot(local.east_m, local.north_m, local.up_m);
  const animate = cause === "solve" && lastAnimate;
  requestAnimationFrame(() => draw(lines, local, errorM, animate));
  showWords(solution, errorM, solveClock);
```
`Math.hypot(a, b, c)` gives the straight-line length sqrt(a squared + b squared + c squared), here the size of the position error. Worked example: east 3, north 4, up 12 gives sqrt(9 + 16 + 144) = sqrt(169) = 13 m. `animate` is `true` only when the cause is `"solve"` and the newest press was a real mouse or touch press with motion allowed. `requestAnimationFrame(callback)` asks the browser to run the callback just before it next paints the screen, which keeps drawing smooth and in step with the display. So `draw` runs in the next frame. `showWords` writes the sentences.

```js
  if (guideStep === 1 && !solveClock && errorLevel(errorM) !== "ok") nextGuideStep();
  else if (guideStep === 2 && solveClock) nextGuideStep();
```
Moves the guided path forward. Step 1 (slider) completes when the page trusts the clock and the error is no longer `"ok"` (the lines have stopped meeting). Step 2 (solve button) completes when the mode is solved. `else if` means "otherwise, if".

```js
  // Step 2's hint says "the lines no longer meet": if they meet again (slider back, or Reset), go back to step 1.
  else if (guideStep === 2 && !solveClock && errorLevel(errorM) === "ok") { guideStep = 1; showGuide(); }
}
```
The comment explains this last case: step 2's hint says "the lines no longer meet". If they do meet again (slider moved back, or Reset), the guide goes back to step 1 by setting `guideStep = 1` and calling `showGuide()`. The closing brace ends `runOnce`.

```js
function failed(result, slot) {
  if (!result || !result.error) return false;
  say(slot, result.error); // Python's own plain sentence
```
`failed` checks a Python answer for an error. The first test `!result || !result.error` means: the answer is missing or has no `error`. In that case return `false` (no failure). Otherwise `say(slot, result.error)` shows Python's own plain sentence in the chosen message line.

```js
  hideAllLines();
  showNoFix();
  return true;
}
```
Then it hides every line and clears the readout so the picture never shows an old answer, and returns `true` so the caller stops. The closing brace ends `failed`.

```js
function clearMessages() {
  for (const node of [el.msgSlider, el.msgReadout, el.msgSolve, el.msgSwitch, el.msgReset]) node.textContent = "";
}
```
`clearMessages` goes through the five message lines in a list (`for (const node of [...])` repeats for each) and sets each one's text to an empty string, which empties it.

```js
// ---------- refusing: too few satellites ----------
```
A heading comment for the refusal part.

```js
function countWords(n) {
  if (n === 0) return "no satellites are";
  return `only ${n} satellite${n === 1 ? " is" : "s are"}`;
}
```
`countWords` makes the phrase for how many satellites are on. For 0 it returns `no satellites are`. Otherwise it returns a template string: `only ${n} satellite${n === 1 ? " is" : "s are"}`. Worked examples: `n` of 1 gives `only 1 satellite is`; `n` of 2 gives `only 2 satellites are`. `===` means "is exactly equal to". The grammar is chosen so the sentence reads correctly.

```js
// No dot, no metres value, no badge. The map shows just the distance lines of the satellites that are on.
async function refuse(sats, solveClock, slot) {
  const n = sats.length;
```
The comment says what a refusal looks like: no dot, no metres value, no badge, and the map shows just the distance lines of the satellites that are on. `refuse` is `async` and takes the satellites that are on, whether the clock is being solved, and the message line. `n` is how many satellites are on.

```js
  say(el.msgSwitch, solveClock
    ? `Can't solve: four things are unknown (east, north, up and the clock), but ${countWords(n)} on, and each satellite gives one measurement. Turn a satellite back on.`
    : `Can't find a position: three things are unknown (east, north, up), but ${countWords(n)} on. Turn a satellite back on.`);
```
Writes a sentence in the switch message line. If solving for the clock it is `Can't solve: four things are unknown (east, north, up and the clock), but` plus the count words plus `on, and each satellite gives one measurement. Turn a satellite back on.` Otherwise it is `Can't find a position: three things are unknown (east, north, up), but` plus the count words plus `on. Turn a satellite back on.` The `? :` chooses between the two. Worked example: 2 satellites on and solving: `Can't solve: four things are unknown (east, north, up and the clock), but only 2 satellites are on, and each satellite gives one measurement. Turn a satellite back on.`

```js
  say(el.msgReadout, "No position: see the message under the satellite switches.");
  showNoFix();
  if (guideStep === 3 && solveClock) nextGuideStep();
```
The readout line says `No position: see the message under the satellite switches.` `showNoFix()` hides the dot, the metres number and the badge. If the guided path is at step 3 and the page was solving for the clock, the guide moves on to the next step.

```js
  let lines = [];
```
`lines` starts as an empty list, used if no satellite is on.

```js
  if (n > 0) {
    const ranges = await callPython("scenario.make_pseudoranges", [receiverPoint, sats, state.clockErrorS]);
    if (failed(ranges, slot)) return;
```
If at least one satellite is on, get its measured distances from Python (the same call as before) and stop if it failed.

```js
    lines = await callPython("mapview.distance_lines", [config.receiver.lat_deg, config.receiver.lon_deg, sats, ranges, 0, config.mapHalfWidthM, config.lineSamples]);
    if (failed(lines, slot)) return;
  }
```
Then ask Python for the lines, with an assumed clock error of 0 (the page does not solve for the clock here). If it fails, stop. The closing brace ends the `if`.

```js
  el.caption.textContent = captionFor(true, lines);
  requestAnimationFrame(() => { drawLines(lines); describeMap(lines.length, null); });
}
```
Writes the caption under the map using `captionFor`. The `true` picks the normal opening sentence (`The map is about 2 km wide. North is up.`), since there is no dot that could be off the edge. Then in the next frame it draws the lines and sets the map's spoken description to say there is no position (`describeMap(lines.length, null)`). The brace ends `refuse`.

```js
// ---------- words ----------
```
A heading comment for the sentences.

```js
function showWords(solution, errorM, solveClock) {
  if (solveClock) {
    say(el.msgSolve, describeClock(solution.clock_error_s) + " The lines meet again.");
  } else {
```
`showWords` writes the sentence after a good run. When the clock is being solved, it says the clock sentence from `describeClock` followed by ` The lines meet again.` The `+` joins the two pieces of text into one.

```js
    say(el.msgReadout, errorLevel(errorM) === "ok"
      ? "The distance lines meet at the dot."
      : "The phone trusts its clock, so the distance lines miss each other.");
  }
```
Otherwise (the phone trusts its clock) the readout line says `The distance lines meet at the dot.` when the error level is `"ok"`, or `The phone trusts its clock, so the distance lines miss each other.` otherwise. The nested `? :` picks one of two sentences.

```js
  if (solution.converged === false) say(el.msgReadout, "The solver did not settle on an answer.");
}
```
If Python reports `converged` as exactly `false` (the solver ran out of tries), it adds `The solver did not settle on an answer.` to the readout line. Checking `=== false` means a missing value does not trigger it.

```js
function describeClock(clockErrorS) {
  const shown = formatMicroseconds(Math.abs(clockErrorS));
```
`describeClock` takes the clock error in seconds. `Math.abs` removes the minus sign, and `formatMicroseconds` writes it as text. Worked example: -0.0000005 s becomes `0.50 µs`.

```js
  if (shown.startsWith("0.00")) return "The phone found its clock is right.";
  return `The phone found its clock is ${shown} ${clockErrorS > 0 ? "fast" : "slow"}.`;
}
```
If the text starts with `0.00` (the clock error rounds to zero) the sentence is `The phone found its clock is right.` Otherwise it is `The phone found its clock is` plus the amount plus `fast` if the original error was above zero, or `slow` if not. Worked example: 5e-7 s gives `The phone found its clock is 0.50 µs fast.` Without the sign check, the words could not say fast or slow.

```js
function formatMicroseconds(seconds) {
  return `${(seconds * 1e6).toFixed(2)} µs`;
}
```
`formatMicroseconds` multiplies seconds by 1,000,000 (`1e6`) to get microseconds and `.toFixed(2)` keeps two decimal places. Worked example: 0.0000005 s x 1,000,000 = 0.5, so the text is `0.50 µs`. 1.234e-6 s gives `1.23 µs`. The `µ` is the Greek letter mu, the symbol for "micro".

```js
// ---------- drawing ----------
```
A heading comment for the drawing part.

```js
function errorLevel(errorM) {
  if (errorM < config.errorLimits.ok_m) return "ok";
  if (errorM < config.errorLimits.warn_m) return "warn";
  return "bad";
}
```
`errorLevel` sorts an error in metres into three words using the limits in [`config.js`](config.js.md): below 10 m is `"ok"`, below 100 m is `"warn"`, otherwise `"bad"`. Worked examples: 3 m gives `ok`, 40 m gives `warn`, 500 m gives `bad`. The words are used for colours and the badge text.

```js
const levelWords = { ok: "Good fix", warn: "Fix is off", bad: "Fix is far off" };
```
A lookup table from each level word to the badge words shown to the visitor: `Good fix`, `Fix is off`, `Fix is far off`.

```js
function toPixelX(east_m) { return (east_m + config.mapHalfWidthM) * MAP_SIZE / (2 * config.mapHalfWidthM); }
function toPixelY(north_m) { return (config.mapHalfWidthM - north_m) * MAP_SIZE / (2 * config.mapHalfWidthM); }
```
Two small functions that turn metres on the ground into map pixels. The map shows -1000 m to +1000 m both ways (`config.mapHalfWidthM` is 1000) on a 400-pixel square. East: `(east_m + 1000) * 400 / 2000`. Worked examples: 0 m east gives (0 + 1000) x 400 / 2000 = 200 (the middle); 500 m east gives 1500 x 400 / 2000 = 300; -1000 m gives 0. North goes the other way because pixel rows count downward from the top: `(1000 - north_m) * 400 / 2000`. Worked example: 500 m north gives 500 x 400 / 2000 = 100, so north is up the screen; -1000 m north gives 400 (the bottom).

```js
function draw(lines, local, errorM, animate = false) {
  cancelGlide();
  $("map-wait").style.display = "none";
```
`draw` is the main drawing step. It takes the lines from Python, where the phone is, the error in metres and whether to glide. `cancelGlide()` ends any earlier glide. Then it hides the "The map appears when Python has loaded." text by setting its CSS `display` style to `"none"`.

```js
  const fromLines = new Map(lastPoints);
  const fromDot = lastDot;
  drawLines(lines);
```
`new Map(lastPoints)` copies where each line was last drawn, and `lastDot` copies where the dot was, before they change, so a glide can start from there. Then `drawLines(lines)` draws the new lines. The next line names the error level.

```js
  const level = errorLevel(errorM);
  const x = toPixelX(local.east_m);
  const y = toPixelY(local.north_m);
  const inside = x >= 0 && x <= MAP_SIZE && y >= 0 && y <= MAP_SIZE;
```
Works out the dot's map pixel position with the two scaling functions, and `inside` is `true` when both are between 0 and 400 (`&&` is "and"), so the dot is on the map. Worked example: 3 m east and 4 m north gives x = 1003 x 400 / 2000 = 200.6 and y = 996 x 400 / 2000 = 199.2, so `inside` is `true`.

```js
  el.dot.style.display = inside ? "" : "none";
  el.dot.firstElementChild.setAttribute("cx", x);
  el.dot.firstElementChild.setAttribute("cy", y);
  lastDot = inside ? { x, y } : null;
```
Shows or hides the dot (`""` lets the stylesheet decide, `"none"` hides it). `el.dot.firstElementChild` is the circle inside the dot's group, and `setAttribute("cx", x)` and `"cy"` move its centre. `lastDot` remembers `{ x, y }` or `null`.

```js
  if (animate) glide(fromLines, new Map(lastPoints), fromDot, lastDot);
  el.dot.setAttribute("class", `is-${level}`);
```
If a glide was asked for, `glide(...)` starts it from the old lines and dot to the new ones. Then the dot gets the CSS class `is-ok`, `is-warn` or `is-bad`, which the stylesheet uses for its colour.

```js
  el.errorValue.textContent = formatMetres(errorM);
  el.badge.hidden = false;
  el.badge.className = `badge is-${level}`;
  el.badge.textContent = levelWords[level];
```
Writes the error in metres into the readout (for example `13 m`), shows the badge by setting `hidden` to `false`, gives it the class for its colour, and sets its text from `levelWords`.

```js
  el.caption.textContent = captionFor(inside, lines);
  const meaning = !inside ? "The phone's position is off the edge of this map" : level === "ok" ? "They meet at the dot" : "They miss each other";
  describeMap(lines.length, meaning);
}
```
Sets the sentence under the map with `captionFor`. `meaning` is the sentence for screen readers: if the dot is off the map, `The phone's position is off the edge of this map`; otherwise `They meet at the dot` when the level is `"ok"` and `They miss each other` when not. `describeMap` writes it for screen readers. The brace ends `draw`.

```js
// The map's words for screen readers, rebuilt after every drawing. null means no position.
function describeMap(count, meaning) {
```
A comment saying `describeMap` rewrites the map's description for screen readers after every drawing, and that `null` means no position. Then `describeMap` starts with the line count and the meaning.

```js
  const lines = `${count} distance line${count === 1 ? "" : "s"}`;
  el.map.setAttribute("aria-label", meaning
    ? `Ground map. ${lines}. ${meaning}. Position off by ${el.errorValue.textContent}.`
    : `Ground map. ${lines}. No position.`);
}
```
`lines` is a sentence such as `4 distance lines` (and `1 distance line` for one). `aria-label` is an attribute that gives an element a spoken name; a map drawn as shapes has no text a screen reader could read, so this text stands in. If there is a meaning, the label reads `Ground map. 4 distance lines. They meet at the dot. Position off by 13 m.` Otherwise it reads `Ground map. 4 distance lines. No position.` Without it a blind visitor would hear nothing useful about the map.

```js
// The map sentence, plus how many distance lines have left the map (design: the picture says what it hides).
function captionFor(inside, lines) {
  let words = inside
    ? `The map is about ${config.mapHalfWidthM * 2 / 1000} km wide. North is up.`
    : "The phone's position is off the edge of this map.";
```
A comment says the caption also says how many lines have left the map. `captionFor` takes whether the dot is on the map and the lines. `let words = inside ? A : B` picks the first sentence. If the dot is on the map, the start is `The map is about` followed by the width in kilometres and `km wide. North is up.` Worked example: `config.mapHalfWidthM * 2 / 1000` is 1000 x 2 / 1000 = 2, so `The map is about 2 km wide. North is up.` If the dot is off the map, it says `The phone's position is off the edge of this map.` instead.

```js
  const off = lines.filter((line) => !line.inside).length;
```
`off` counts the lines whose `inside` is `false` (`filter` keeps the matching ones, `.length` counts them).

```js
  if (off > 0) words += ` ${off} of the ${lines.length} distance lines ${off === 1 ? "has" : "have"} moved off the edge of this map.`;
  return words;
}
```
If any are off, it adds a sentence: for example `1 of the 4 distance lines has moved off the edge of this map.` (the verb is `has` for one, `have` for more). `+=` adds to the end of the existing text. It returns the finished sentence.

```js
// When the page refuses to solve: no metres value, no badge, no dot (issue #40).
// Done in the next frame so it lands after any drawing an earlier run has already queued.
function showNoFix() {
```
Two comments say what `showNoFix` is for: when the page refuses to solve, there is no metres value, no badge and no dot (issue #40), and it is done in the next frame so it lands after any drawing an earlier run has already queued. Then `showNoFix` starts.

```js
  cancelGlide();
  lastDot = null;
  requestAnimationFrame(() => {
    el.dot.style.display = "none";
    el.errorValue.textContent = "–";
    el.badge.hidden = true;
  });
}
```
Ends any glide, forgets the dot position, and in the next frame hides the dot, shows `–` (a dash) for the error and hides the badge. Without it the old numbers would still be shown after a refusal.

```js
function drawLines(lines) {
  const known = new Map([...el.lines.children].map((node) => [node.dataset.id, node]));
  const wanted = new Set(lines.map((line) => line.id));
```
`drawLines` draws the distance lines on the map. `known` is a Map of lines already on the map, from each one's id to its element: `[...el.lines.children]` makes a list of the child elements, and `node.dataset.id` is a `data-id` value stored on the element. `wanted` is a `Set` (a collection with no repeats) of the ids that Python returned now.

```js
  for (const line of lines) {
    let node = known.get(line.id);
    if (!node) {
      node = document.createElementNS(SVG, "polyline");
      node.dataset.id = line.id;
      node.setAttribute("class", "map-line");
      el.lines.append(node);
    }
```
For each line from Python, find its element in `known`. If there is none (`!node`), make one: `document.createElementNS(SVG, "polyline")` creates an SVG polyline (a shape joining points with straight segments), stores the id in `dataset.id`, gives it the class `map-line`, and adds it to the map. Without it a new satellite's line could not appear.

```js
    const pixels = line.points.map(([e, n]) => [toPixelX(e), toPixelY(n)]);
    lastPoints.set(line.id, pixels);
    node.setAttribute("points", pixels.join(" "));
    node.classList.toggle("is-hidden", !line.inside);
  }
```
`line.points.map(([e, n]) => [toPixelX(e), toPixelY(n)])` turns each east-north point into a pixel point. The result is saved in `lastPoints` for the glide. `pixels.join(" ")` writes the points as text for the SVG `points` attribute, which is a list of `x,y` pairs. Worked example: points (0, 0) and (500, 500) become pixels (200, 200) and (300, 100), written `200,200 300,100`. `classList.toggle("is-hidden", !line.inside)` hides a line that is off the map by fading it out.

```js
  // A switched-off satellite is not in the list: fade its line out.
  for (const [id, node] of known) if (!wanted.has(id)) node.classList.add("is-hidden");
}
```
A comment explains the last line: a switched-off satellite is not in the list, so its old line is faded out. The `for` goes through every known element and, if its id is not in `wanted`, adds `is-hidden`. The brace ends `drawLines`.

```js
// Glide the lines and the dot from their old places to their new ones over 450 ms (ease-out), so the lines are seen coming together.
function glide(fromLines, toLines, fromDot, toDot) {
  const start = performance.now();
  const blend = (from, to, e) => from + (to - from) * e;
```
A comment says the glide moves the lines and the dot from their old places to the new ones over 450 ms (ease-out), so the visitor sees the lines come together. `glide` takes the old and new lines and dots. `performance.now()` is the browser's clock in milliseconds, saved as `start`. `blend(from, to, e)` returns a point `e` of the way between two numbers: when `e` is 0 it is `from`, when 1 it is `to`. Worked example: `blend(200, 300, 0.5)` is 200 + (300 - 200) x 0.5 = 250.

```js
  function show(e) {
    for (const [id, to] of toLines) {
      const from = fromLines.get(id);
      if (!from || from.length === 0 || to.length === 0) continue; // no old points: it stays at its new place
      const node = el.lines.querySelector(`[data-id="${id}"]`);
      if (e === 1) { node.setAttribute("points", to.join(" ")); continue; } // the end is the exact result
```
`show(e)` draws one moment of the glide, where `e` runs from 0 (the old picture) to 1 (the new one). For each new line it finds the old points `from`. If there are none or either list is empty, it skips that line (`continue` jumps to the next), since a line with no old points just stays at its new place. It looks up the element by its `data-id`. When `e` is exactly 1, the end is set to the exact result.

```js
      const a = resample(from);
      const b = resample(to);
      node.setAttribute("points", b.map(([x, y], i) => `${blend(a[i][0], x, e)},${blend(a[i][1], y, e)}`).join(" "));
    }
```
Otherwise both old and new points are made the same length by `resample` (below) as `a` and `b`, and each point is blended between the old and new position by `e`. Then the result is joined into the `points` text. Worked example: old x 200, new x 300, `e` 0.5 gives 250.

```js
    if (fromDot && toDot) {
      el.dot.firstElementChild.setAttribute("cx", blend(fromDot.x, toDot.x, e));
      el.dot.firstElementChild.setAttribute("cy", blend(fromDot.y, toDot.y, e));
    }
  }
```
If the dot was drawn before and is drawn now, its centre is blended in the same way. The braces end `show`.

```js
  function frame(now) {
    const t = Math.min((now - start) / 450, 1);
    show(1 - (1 - t) ** 3);
```
`frame(now)` runs on each animation frame; `now` is the time. `t` is how far through the 450 ms we are, from 0 to 1: `Math.min((now - start) / 450, 1)` stops at 1. Worked example: 90 ms in gives t = 90 / 450 = 0.2. `show(1 - (1 - t) ** 3)` applies the easing: it moves fast at first and slows at the end. `**` means "to the power of". Worked examples: t = 0.2 gives 1 - 0.8 x 0.8 x 0.8 = 1 - 0.512 = 0.488; t = 0.5 gives 1 - 0.125 = 0.875; t = 1 gives 1.

```js
    glideFrame = t < 1 ? requestAnimationFrame(frame) : 0;
    if (t >= 1) glideFinish = null;
  }
```
If `t` is under 1, ask for another frame and remember its number in `glideFrame`; otherwise store 0. When `t` reaches 1, `glideFinish` is cleared because there is nothing left to finish.

```js
  glideFinish = () => show(1);
  show(0);
  glideFrame = requestAnimationFrame(frame);
}
```
`glideFinish` is a function that jumps to the end by calling `show(1)`; `cancelGlide` uses it. `show(0)` draws the starting picture straight away, and `requestAnimationFrame(frame)` starts the animation. Without this the glide would never start.

```js
// Give a point list exactly config.lineSamples points by linear interpolation along the list, so old and new lines match point by point.
function resample(points) {
```
A comment: give a point list exactly `config.lineSamples` points (40) by linear interpolation (finding values on the straight segments between points) so old and new lines match point by point. `resample` starts.

```js
  return Array.from({ length: config.lineSamples }, (_, i) => {
    const at = i * (points.length - 1) / (config.lineSamples - 1);
```
`Array.from({ length: 40 }, (_, i) => ...)` builds a list of 40 results, one for each position `i` from 0 to 39. `at` is how far along the old list the new point `i` sits: `i * (points.length - 1) / (40 - 1)`. Worked example: with 10 points, `i` of 20 gives 20 x 9 / 39 = 4.615.

```js
    const low = Math.floor(at);
    const high = Math.min(low + 1, points.length - 1);
    const f = at - low;
```
`low` is the whole number just below (`Math.floor`), `high` is the next point but not past the end (`Math.min`), and `f` is the leftover fraction. Worked example: `at` 4.615 gives low 4, high 5, f 0.615.

```js
    return [blend2(points[low][0], points[high][0], f), blend2(points[low][1], points[high][1], f)];
  });
}
```
Returns the point a fraction `f` of the way from point `low` to point `high`, for the x and the y. Worked example: if point 4 has x 100 and point 5 has x 130, then 100 + (130 - 100) x 0.615 = 118.45. For the last `i` (39) `at` is 9 and `high` is capped at 9, so the last new point is exactly the list's own last point.

```js
function blend2(from, to, f) { return from + (to - from) * f; }
```
The small helper that does the same blend as above: from + (to - from) x f. It is a separate function because `blend` lives inside `glide` and cannot be reached from here.

```js
// A new run or a refusal ends a glide: draw its end at once.
function cancelGlide() {
  cancelAnimationFrame(glideFrame);
```
A comment says a new run or a refusal ends a glide by drawing its end at once. `cancelGlide` calls `cancelAnimationFrame(glideFrame)`, which cancels the animation frame that was asked for.

```js
  glideFrame = 0;
  if (glideFinish) glideFinish();
  glideFinish = null;
}
```
Resets `glideFrame` to 0. If `glideFinish` holds a function, it runs it, which draws the end of the glide. Then `glideFinish` is cleared. Without this a half-finished glide could leave lines in the wrong place.

```js
// ---------- the guided path ----------

// Only the hint for the current step shows, and the white border sits on that step's control.
function showGuide() {
```
A heading comment, then a comment saying only the hint for the current step shows, and the white border sits on that step's control. `showGuide` starts.

```js
  const blocks = ["block-slider", "block-solve", "block-switches"];
  blocks.forEach((id, i) => $(id).classList.toggle("highlight", guideStep === i + 1));
```
The three blocks on the page, by `id`, in step order. `blocks.forEach(...)` goes through them with each block's `id` and position `i` (0 to 2). It adds the class `highlight` when `guideStep === i + 1` and removes it otherwise, so the border sits on the block of the current step.

```js
  for (const [name, step] of [["hint-1", 1], ["hint-2", 2], ["hint-3", 3], ["hint-done", 4]]) {
    const node = $(name);
    const show = guideStep === step;
    node.hidden = !show;
    node.classList.remove("is-shown");
```
Goes through the four hints and the step each belongs to (`hint-1` is step 1, `hint-done` is 4). `for (const [name, step] of [...])` unpacks each pair. `node` is the hint's element. `show` is `true` only for the current step. `node.hidden = !show` hides or reveals it. `classList.remove("is-shown")` removes the fade-in class first.

```js
    if (show) {
      void node.offsetWidth; // let the browser see opacity 0 first, so the fade runs
      node.classList.add("is-shown");
    }
  }
}
```
If this hint is to be shown, `void node.offsetWidth;` reads a layout value and throws it away. That forces the browser to notice the hint at opacity 0 first, so that adding `is-shown` (which makes it fully visible) then fades it in instead of showing it at once. Without it there would be no fade. The braces end the `if`, the loop and the function.

```js
function nextGuideStep() {
  guideStep += 1; // Reset does not bring back a finished path
  showGuide();
}
```
`nextGuideStep` adds 1 to `guideStep` and shows the hint for the new step. The comment says Reset does not bring back a finished path: nothing ever lowers `guideStep` once it has passed step 2. (The one step back is in `runOnce`, from step 2 to step 1, when the lines meet again.)

```js
// A picture must never outlive its numbers: hide every distance line.
function hideAllLines() {
  requestAnimationFrame(() => { drawLines([]); describeMap(0, null); });
}
```
A comment: a picture must never outlive its numbers, so hide every distance line. `hideAllLines` draws an empty list of lines in the next frame (so every old line fades out) and sets the map's description to say there is no position.

```js
// The true position is always the middle of the map.
function drawTrueMark() {
  const middle = MAP_SIZE / 2;
  const group = $("map-true");
```
A comment: the true position is always the middle of the map. `drawTrueMark` draws a small cross there. `middle` is half of 400, which is 200. `group` is the map's `<g>` element that holds the cross.

```js
  for (const [x1, y1, x2, y2] of [[middle - 12, middle, middle + 12, middle], [middle, middle - 12, middle, middle + 12]]) {
    const line = document.createElementNS(SVG, "line");
```
Goes through two lines, each described by four numbers `[x1, y1, x2, y2]` (a start point and an end point). The first runs from (188, 200) to (212, 200), the horizontal bar of the cross, since 200 - 12 = 188 and 200 + 12 = 212. The second runs from (200, 188) to (200, 212), the vertical bar. `line` is a new SVG `line` element for each.

```js
    for (const [name, value] of Object.entries({ x1, y1, x2, y2 })) line.setAttribute(name, value);
    group.append(line);
  }
}
```
`Object.entries({ x1, y1, x2, y2 })` gives name and value pairs, such as `["x1", 188]`, and `setAttribute(name, value)` sets each on the line. `group.append(line)` puts the line on the map. The braces end the loop and `drawTrueMark`. Without this function the map would not show where the phone really is.
