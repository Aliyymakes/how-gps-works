# step-relativity.js, line by line

Source: `web/step-relativity.js`

## What this file is for
This builds the "Do the satellites' own clocks matter?" section of the page. It draws one slider (hours of clock drift, 0 to 24) and shows two results side by side: the position error if the phone trusted its own clock, and the position error when the phone solves for its clock. It calculates nothing itself. Every number comes from Python; the only thing decided here is which colour badge to show.

## Which files it talks to
- `web/config.js` ([config.js](config.js.md)): gives the phone's place, the four satellite directions, the colour limits (`errorLimits`), the slider settings (`relativitySlider`) and the phone's own clock error (`relativityPhoneClockErrorS`).
- `web/startup.js`: [`whenPythonReady`](startup.js.md) waits for Python to download and then runs this file's `start` function.
- `web/say.js` ([say.js](say.js.md)): `say` writes a message into a line on the page and gives it a brief fade, so pressing something always gives a visible answer.
- `web/format.js` ([format.js](format.js.md)): `formatMetres` turns a number of metres into text such as `11,392 m`.
- `web/theme.css` ([theme.css](theme.css.md)): all colours, fonts and the classes `card`, `inset`, `badge`, `btn`, `slider`, `label`, `num` and `muted` come from here.
- `index.html` ([index.html](../index.html.md)): imports this file and calls `mountRelativityStep` with the empty box `step-relativity`.
- Python, through the bridge (see [`startup.js`](startup.js.md)):
  - `coords.latlon_to_xyz` and `coords.satellite_from_sky`, in [`coords.py`](../mechanism/coords.py.md): place the phone and the satellites in space.
  - `relativity.drift_over_time`, in [`relativity.py`](../mechanism/relativity.py.md): adds the shared drift, solves twice and returns the errors. It uses `scenario.make_pseudoranges` and `solver.solve_position` (see [`solver.py`](../mechanism/solver.py.md)). The exact shapes are in `docs/interface.md`.

## In three lines
1. Build the section's text and controls, and wait until Python is ready.
2. Once ready, place the phone and the satellites (Python) and switch on the slider and the Reset button.
3. Each time the slider moves, ask Python for the two errors at that many hours and show them with a "Good fix", "Fix is off" or "Fix is far off" badge.

New to code? See [how to read code](../how-to-read-code.md). Browser words used here:
- The **DOM** is the browser's live model of the page. Each tag is an object (an **element**) that code can find and change.
- An **attribute** is a labelled setting on a tag, such as `type="range"` or `hidden`.
- An **event** is something that happens on the page (a click, a slider moving).
- A **Promise** is a ticket for a result that has not arrived yet; `await` waits for it (see the `async and await` part of [how to read code](../how-to-read-code.md)).
- A **CSS variable** is a named value in the style sheet, written like `--s-4`, which a rule reads with `var(--s-4)`.
- A **media query** is a style rule that only applies when a condition about the screen is true.
- **aria-\* attributes** are extra labels for screen readers (software that reads the page aloud to people who cannot see it).

## The code, line by line

```js
// Rung 4: relativity (design.md 2a, 2b). One slider, two results side by side. Every number comes
// from Python (relativity.drift_over_time); nothing is calculated here except choosing a badge colour.
```
Two comments. "Rung 4" is this section's place on the page's ladder of steps. `design.md` is the project's spec. The second line states the rule of the whole file: numbers come from Python.

```js
import * as config from "./config.js";
```
Brings in everything exported by [`config.js`](config.js.md) under the name `config`, so the code can write `config.receiver`. These are the page's tunable settings. Without this line every `config.` below would be unknown.

```js
import { whenPythonReady } from "./startup.js";
import { say } from "./say.js";
import { formatMetres } from "./format.js";
```
Three imports, each taking one named function from another file: `whenPythonReady` (wait for Python), `say` (write a message with a short fade) and `formatMetres` (make `11392.1` into `11,392 m`). Without them those names would be unknown and the file would fail to load.

```js
// Layout for this section only. Colours, fonts and radii come from theme.css.
const STYLE = `
```
A comment, then the start of a piece of text called `STYLE` that holds this section's own style rules (CSS, the language that sets how things look). The backtick (`` ` ``) starts text that may run over many lines. Colours, fonts and corner shapes come from [`theme.css`](theme.css.md) so they stay the same everywhere; only layout is here.

```js
.rel { display: grid; grid-template-columns: minmax(0, 1fr); gap: var(--s-4); }
.rel-stack { grid-template-columns: minmax(0, 1fr); }
```
Two CSS rules. A rule is a selector (which things it applies to) and then settings in curly brackets.
- `.rel` (the class `rel`, the section's outer box) uses `display: grid`, which lays children out in rows and columns. `grid-template-columns: minmax(0, 1fr)` makes one column that may shrink to zero width and takes all the room (`1fr` is one share of the space). `gap: var(--s-4)` leaves a space between children, read from the CSS variable `--s-4`.
- `.rel-stack` repeats the one-column layout for the heading block.
Without `minmax(0, ...)` a wide piece of content could push the column wider than a phone screen.

```js
.rel-note { font-size: var(--text-sm); color: var(--text-muted); min-height: 1.5em; }
.rel-note:empty { min-height: 0; }
```
- `.rel-note` styles the small message lines: smaller text (`--text-sm`), a softer colour (`--text-muted`) and a minimum height of 1.5 times the text size, so the page does not jump when a message appears.
- `.rel-note:empty` says that a note with nothing in it needs no minimum height (`:empty` means "has no content"), so empty notes take no room.

```js
.rel-card { display: grid; grid-template-columns: minmax(0, 1fr); gap: var(--s-4); }
.rel-highlight { border-color: var(--accent); padding: var(--s-4); }
.rel-readout { padding: var(--s-4); display: grid; gap: var(--s-2); }
.rel-big { font-size: var(--text-xl); }
```
- `.rel-card`: the main card, again one column with gaps.
- `.rel-highlight`: the slider's box gets the accent colour for its border and padding (space inside the edge), so it stands out as the thing to touch.
- `.rel-readout`: each result box has padding and stacks its label, number and badge with a small gap (`--s-2`).
- `.rel-big`: the numbers use the extra large text size (`--text-xl`).

```js
.rel-pair { display: grid; grid-template-columns: minmax(0, 1fr); gap: var(--s-4); }
@media (min-width: 760px) { .rel-pair { grid-template-columns: 1fr 1fr; } }
```
`.rel-pair` holds the two result boxes. On a narrow screen they stack in one column. The `@media (min-width: 760px)` line is a media query: only when the screen is at least 760 pixels wide, the pair gets two equal columns (`1fr 1fr`), putting the results side by side. Without the media query, the boxes would be squeezed side by side even on a phone.

```js
.rel .hint { font-size: var(--text-sm); font-weight: 500; color: var(--text); }
.rel .slider-head { flex-wrap: wrap; column-gap: var(--s-3); }
.rel .badge[hidden] { display: none; }
```
- `.rel .hint`: the "Drag this slider..." line is a little smaller, medium weight and in the full text colour so it is easy to read. (Two classes with a space means "a `hint` inside a `rel`".)
- `.rel .slider-head`: the line above the slider (label and value) may wrap onto a second row on a narrow screen (`flex-wrap`), with a gap between columns.
- `.rel .badge[hidden]`: a badge that has the `hidden` attribute is not shown at all (`display: none`). Some style rules for badges would otherwise make a hidden badge appear anyway; this makes sure it stays hidden.

```js
.rel .btn { touch-action: manipulation; }
.rel input[type="range"] { touch-action: pan-y; }
```
`touch-action` tells a phone how fingers may behave on something.
- On buttons, `manipulation` allows tapping and scrolling but turns off double-tap zoom, so quick repeated taps are not delayed.
- On the slider (an `input` whose `type` is `range`), `pan-y` lets a finger drag up and down scroll the page, while a sideways drag moves the slider. Without it, touching the slider could block scrolling the page.

```js
.rel .btn:disabled, .rel input[type="range"]:disabled { opacity: 0.4; cursor: not-allowed; }
.rel .btn:disabled:hover { border-color: var(--line-strong); }
`;
```
- A switched-off button or slider (`:disabled`, set while Python loads) is faded to 40% opacity, and the mouse pointer shows the "not allowed" sign. The comma means the rule applies to both.
- A disabled button should not react to the mouse, so hovering it keeps the normal strong border colour.
- The last line is the closing backtick and semicolon: the end of the `STYLE` text.

```js
const LEVEL_WORDS = { ok: "Good fix", warn: "Fix is off", bad: "Fix is far off" };
```
An **object**: a set of labelled values. It matches each level name to the words on the badge. Page words: "Good fix", "Fix is off" and "Fix is far off". Without it the badge would have no words.

```js
function errorLevel(errorM) {
```
Starts a function called `errorLevel`. It is given an error in metres (`errorM`) and returns the level name.

```js
  if (errorM < config.errorLimits.ok_m) return "ok";
```
If the error is below the first limit, `ok_m`, the answer is `"ok"`, and `return` ends the function. In [`config.js`](config.js.md) that limit is 10 metres, so 5 m is `"ok"`.

```js
  if (errorM < config.errorLimits.warn_m) return "warn";
```
If it got past the first check, the error is 10 m or more. If it is under `warn_m` (100 m), the answer is `"warn"`. Example: 50 m is `"warn"`.

```js
  return "bad";
```
Anything else (100 m or more) is `"bad"`. Example: 19,767 m (the "trusted" error after 24 hours, see below) is `"bad"`. Without this line the function would return nothing for large errors.

```js
}
```
Closes `errorLevel`.

```js
// Draft sentences: every visible sentence below is for Icarus to approve.
const PAGE = `
```
A comment saying that the visible sentences are drafts waiting for Icarus (the project lead) to approve. Then `PAGE` begins: a block of HTML (the language that describes the tags on a page) held as text.

```js
<div class="rel">
  <header class="rel-stack" style="display: grid; gap: var(--s-2)">
    <h2 id="rel-title">Do the satellites' own clocks matter?</h2>
```
- `<div class="rel">` opens a plain box with the class `rel`, which the `.rel` style rule above targets.
- `<header ...>` opens the section's top part. Its `style` attribute puts a grid with a small gap right on the tag.
- `<h2 id="rel-title">` is a second-level heading, and the page shows "Do the satellites' own clocks matter?". The `id` is a unique name so that the card below can point at it.

```js
    <p class="muted">A satellite's clock does not tick at the same rate as a clock on the ground. Left uncorrected, the difference grows every hour. Here every satellite drifts by the same amount.</p>
```
A paragraph (`<p>`) in the softer `muted` style. The page shows: "A satellite's clock does not tick at the same rate as a clock on the ground. Left uncorrected, the difference grows every hour. Here every satellite drifts by the same amount." The last sentence matters: it sets up the simplification the whole section depends on.

```js
    <p class="rel-note" data-id="status" role="status" aria-live="polite">Loading the maths…</p>
```
The status line. `data-id="status"` is a private label the code uses to find this tag later (see `$` below). `role="status"` and `aria-live="polite"` tell screen readers that this text changes and should be read out when the reader is idle, without cutting in. It starts with "Loading the maths…" and is later overwritten by startup progress.

```js
  </header>
  <section class="card rel-card" aria-labelledby="rel-title">
```
`</header>` closes the heading block. `<section>` opens the main card (classes `card` and `rel-card`). `aria-labelledby="rel-title"` tells screen readers that this section is named by the heading with that `id`.

```js
    <p class="hint" data-id="hint" hidden>Drag this slider to let the satellite clocks drift for a day.</p>
```
The hint: "Drag this slider to let the satellite clocks drift for a day." The `hidden` attribute hides it until the code shows it, once the slider is live.

```js
    <div class="slider inset rel-highlight">
      <div class="slider-head">
        <label for="rel-hours">Hours without correcting the satellite clocks</label>
        <span class="num" data-id="slider-value">0 h</span>
      </div>
```
The slider's box (classes `slider`, `inset` and `rel-highlight`) and its top line.
- The `<label>` shows "Hours without correcting the satellite clocks". Its `for="rel-hours"` ties it to the slider with that `id`, so clicking the words picks the slider and screen readers read them as its name.
- The `<span>` (an inline piece of text) shows the current value, starting as "0 h". The class `num` styles it as a number.

```js
      <input id="rel-hours" data-id="slider" type="range" disabled>
    </div>
```
The slider itself: an `<input>` of `type="range"`. Its `id` matches the label. It starts `disabled` (switched off) until Python is ready, because moving it before then could not do anything. Its minimum, maximum and step are set later from [`config.js`](config.js.md). The `</div>` closes the slider's box.

```js
    <div class="inset rel-readout">
      <span class="label">Each measured distance is wrong by</span>
      <span class="num rel-big" data-id="range">–</span>
    </div>
```
The first result box, showing how much the shared drift adds to each measured distance. The label reads "Each measured distance is wrong by". The big number starts as a dash ("–") and is later replaced by Python's `range_added_m`.

```js
    <div class="rel-pair">
      <div class="inset rel-readout">
        <span class="label">If the phone trusted its clock</span>
        <span class="num rel-big" data-id="trusted">–</span>
        <div><span class="badge is-ok" data-id="trusted-badge" hidden></span></div>
      </div>
```
The pair of result boxes starts. The first box has the label "If the phone trusted its clock", a number (a dash for now) and a badge. The badge starts with the class `is-ok` and `hidden`, so it shows nothing until there is a result. The `<div>` around the badge stops it from stretching across the box.

```js
      <div class="inset rel-readout">
        <span class="label">Because the phone solves for its clock</span>
        <span class="num rel-big" data-id="solved">–</span>
        <div><span class="badge is-ok" data-id="solved-badge" hidden></span></div>
      </div>
    </div>
```
The second box, in the same shape, labelled "Because the phone solves for its clock". The last `</div>` closes `rel-pair`.

```js
    <p class="rel-note" data-id="sentence" role="status" aria-live="polite"></p>
```
An empty message line for a one-sentence summary of what the results mean. It is also a polite status region, so screen readers read each new sentence. Empty notes take up no room (see `.rel-note:empty`).

```js
    <div>
      <button class="btn" data-id="reset" type="button" disabled>Reset</button>
      <p class="rel-note" style="margin-top: var(--s-2)" data-id="msg-reset" role="status" aria-live="polite"></p>
    </div>
```
The Reset area. The `<button>` says "Reset", has the page's button style `btn`, is `type="button"` (an ordinary button) and starts `disabled`. Below it is another polite status line (with a small top margin) that will confirm the reset in words.

```js
  </section>
  <p>The drift is the same for every satellite, so it looks just like the phone's own clock error, and solving for the clock absorbs it. The position stays put.</p>
</div>`;
```
- `</section>` closes the card.
- The closing paragraph says: "The drift is the same for every satellite, so it looks just like the phone's own clock error, and solving for the clock absorbs it. The position stays put." This is the point of the section. The position stays put because the same extra amount is added to every satellite's measured distance, and the solver has a clock term that soaks up exactly such a shared amount.
- `</div>` closes the `rel` box, and the backtick and semicolon end the `PAGE` text.

```js
export function mountRelativityStep(container) {
```
The function [`index.html`](../index.html.md) calls. `export` makes it available to other files. "Mount" means "put it on the page". `container` is the empty element it should fill.

```js
  if (!document.getElementById("rel-style")) {
```
Looks on the page for an element with the `id` `rel-style` (`getElementById`). `!` means "not found". This protects against adding the style rules twice if the function is ever called twice.

```js
    const style = document.createElement("style");
    style.id = "rel-style";
    style.textContent = STYLE;
    document.head.append(style);
  }
```
Makes a new `<style>` element in memory, gives it the `id` `rel-style` (the one the check above looks for), fills it with the `STYLE` text, and adds it to the page's `<head>` (the hidden top part where styles live). Once added, the browser applies the rules. The `}` closes the `if`. Without these lines the section would have no layout.

```js
  container.insertAdjacentHTML("beforeend", PAGE);
```
Turns the `PAGE` text into real elements and puts them at the end of the container (`"beforeend"`). After this line the section appears on the page, still switched off.

```js
  const root = container.lastElementChild;
```
Grabs the last element inside the container, which is the `<div class="rel">` just added. All later searches look only inside it, so they cannot hit other sections.

```js
  const $ = (id) => root.querySelector(`[data-id="${id}"]`);
```
Makes a tiny finder called `$` (a legal, short name). Given a word, it looks inside `root` for the element whose `data-id` attribute equals that word. Example: `$("slider")` finds the tag marked `data-id="slider"`. Without it every lookup below would be a long line.

```js
  const el = {
    status: $("status"), hint: $("hint"), slider: $("slider"), sliderValue: $("slider-value"),
    range: $("range"), trusted: $("trusted"), trustedBadge: $("trusted-badge"),
    solved: $("solved"), solvedBadge: $("solved-badge"), sentence: $("sentence"),
    reset: $("reset"), msgReset: $("msg-reset"),
  };
```
Builds an object called `el` that gathers every element the code needs under an easy name, for example `el.slider` and `el.reset`. Doing the search once, here, is neater than searching each time. If a `data-id` were misspelt the entry would be empty and later lines would fail.

```js
  const { min_h, max_h, step_h, start_h } = config.relativitySlider;
```
Pulls four named values out of `config.relativitySlider` in one go. In [`config.js`](config.js.md) they are: minimum 0 hours, maximum 24 hours, step 1 hour and start 0 hours.

```js
  let callPython = null; // set when the bridge has loaded
  let receiver = null; // true receiver position, from Python
  let satellites = null; // the four satellites, from Python
  let running = false;
  let rerun = false;
  let hintDone = false; // once the user has touched the slider, the hint stays hidden
```
Six boxes that change as the section runs.
- `callPython`: the function for asking Python, filled in when Python is ready.
- `receiver`: the phone's position in space, from Python.
- `satellites`: the four satellites with their positions, from Python.
- `running`: is a calculation in progress right now.
- `rerun`: was another calculation asked for while one was running.
- `hintDone`: has the reader already touched the slider.

```js
  el.slider.min = min_h;
  el.slider.max = max_h;
  el.slider.step = step_h;
  el.slider.value = start_h;
```
Sets the slider from the config: it runs from 0 to 24, moves one hour at a time and sits at 0. Without these lines the slider would use the browser's defaults of 0 to 100.

```js
  showHours();
```
Calls `showHours` (below) once so the "0 h" next to the slider and its screen-reader text match the starting value.

```js
  el.slider.addEventListener("input", () => {
```
An **event listener**: the `input` event fires every time the slider's value changes while the reader drags it. The following lines are what runs.

```js
    el.hint.hidden = true;
    hintDone = true;
    el.msgReset.textContent = "";
```
- Hide the hint (the reader has found the slider).
- Remember that, so the hint is not shown again when Python becomes ready later.
- Clear the "Back to the start" message from an earlier Reset, so it does not stay stale.

```js
    showHours();
    update();
  });
```
Refresh the hours text, then ask for a new calculation with `update()`. The last line closes the function and the listener. Without `update()` the slider would move but the results would stay as they were.

```js
  el.reset.addEventListener("click", () => {
```
Another event listener: when Reset is clicked, run the lines below.

```js
    el.slider.value = start_h;
    showHours();
    update();
```
Put the slider back at the starting value (0), refresh the hours text and recalculate. Setting `value` in code does not fire an `input` event, so `showHours` and `update` are called by hand.

```js
    say(el.msgReset, "Back to the start: no drift.");
  });
```
Writes "Back to the start: no drift." under the button using `say`, which also flashes it briefly. Pressing Reset when already at 0 still gives a visible answer. The last line closes the listener.

```js
  whenPythonReady(el.status, start);
```
Tells [`startup.js`](startup.js.md): "show loading and failure words in `el.status`, and when Python is ready run `start`". Without it the controls would stay off for ever.

```js
  async function start(call) {
```
Starts the function that runs when Python is ready. `async` lets it use `await`. `call` is the function for asking Python.

```js
    callPython = call;
```
Keeps it in the box made earlier, so the other functions in this file can use it.

```js
    try {
      const { lat_deg, lon_deg } = config.receiver;
```
`try` means "attempt the lines below; if one fails, jump to `catch`". The second line picks the phone's latitude and longitude out of `config.receiver`: -6.2 and 106.8 (Jakarta).

```js
      receiver = await callPython("coords.latlon_to_xyz", [lat_deg, lon_deg]);
```
Asks Python to run `latlon_to_xyz` in the `coords` file with the two numbers. It converts a place on the Earth into three numbers (x, y, z) in metres from the Earth's centre (see [`coords.py`](../mechanism/coords.py.md)). `await` waits for the answer.

```js
      if (receiver.error) throw new Error(receiver.error);
```
If Python reports a problem, its answer has an `error` field with a plain sentence. `throw new Error(...)` then jumps to the `catch` below. Without the check, bad data would carry on and cause confusing failures later.

```js
      satellites = [];
      for (const sat of config.satellites) {
```
Starts with an empty list, then a **loop** over the four satellites in [`config.js`](config.js.md). Each one has an `id`, a compass direction (`azimuth_deg`) and a height above the horizon (`elevation_deg`).

```js
        const point = await callPython("coords.satellite_from_sky", [lat_deg, lon_deg, sat.azimuth_deg, sat.elevation_deg]);
```
For each satellite, asks Python's `satellite_from_sky` (see [`coords.py`](../mechanism/coords.py.md)) to place it in space from where the phone is and where in the sky it appears. The answer holds the satellite's x, y, z position.

```js
        if (point.error) throw new Error(point.error);
```
Same safety check as for the phone.

```js
        satellites.push({ id: sat.id, ...point });
      }
```
Adds a record to the list: the satellite's `id` plus everything in `point` (`...point` spreads out its fields). The `}` closes the loop. Python's relativity function needs these records.

```js
    } catch (error) {
      console.error(error);
      el.status.textContent = "The calculation engine loaded but could not place the satellites, so the controls stay off.";
      return;
    }
```
The `catch` runs if anything above failed. It writes the error to the browser's developer console (a hidden log for programmers), shows "The calculation engine loaded but could not place the satellites, so the controls stay off." on the status line, and `return` ends `start`. So the slider stays disabled. Without this block a failure would leave the reader looking at a silent, dead section.

```js
    el.slider.disabled = false;
    el.reset.disabled = false;
```
Everything worked, so switch the slider and the button on.

```js
    el.hint.hidden = hintDone;
```
Show the hint unless the reader already touched the slider while loading (`hintDone` true makes `hidden` true).

```js
    update();
  }
```
Run a first calculation so the result boxes show real numbers at 0 hours. The `}` closes `start`.

```js
  function showHours() {
    const hours = Number(el.slider.value);
```
A function that refreshes the hours text. `el.slider.value` is text such as `"12"`; `Number(...)` makes it a real number, 12.

```js
    el.sliderValue.textContent = `${hours} h`;
```
Shows it next to the slider, e.g. "12 h". The space before `h` is a non-breaking space, so the number and the `h` never split across two lines.

```js
    el.slider.setAttribute("aria-valuetext", `${hours} hours`);
  }
```
Sets the `aria-valuetext` attribute to "12 hours". A screen reader reads this in place of the bare number, so it says "12 hours" instead of "12". The `}` closes `showHours`.

```js
  // Python calls are async. If one is running, remember that a newer run is wanted and do it once after.
  async function update() {
```
A comment, then the function that asks for a calculation. Calls to Python take time (they are `async`). Dragging the slider quickly could start many at once, so `update` lines them up: only one runs at a time.

```js
    if (!callPython || !satellites) return;
```
If Python is not ready yet (no `callPython`) or the satellites are not placed, there is nothing to calculate, so stop. `||` means "or".

```js
    if (running) { rerun = true; return; }
```
If a calculation is already running, write down that a newer one is wanted (`rerun = true`) and stop. The running one will do it when it finishes. This avoids piling up calculations and avoids old answers arriving after newer ones.

```js
    running = true;
```
Marks that one is now running.

```js
    try {
      do {
        rerun = false;
        await runOnce();
      } while (rerun);
```
A `do ... while` loop runs its body first, then repeats while the condition holds. Each time round: clear `rerun`, run one calculation and wait for it. If the slider moved meanwhile, `rerun` was set to `true`, so the loop goes round again with the new value. If many moves arrive, only one extra calculation is made at the end, using the slider's latest value.

```js
    } finally {
      running = false;
    }
  }
```
`finally` runs whatever happens, even if something failed. It clears `running`, so the next slider move can start a new calculation. Without `finally` one failure could leave `running` stuck on `true` and the slider would never update again. The last `}` closes `update`.

```js
  async function runOnce() {
    const hours = Number(el.slider.value); // the slider may move while Python works
```
The function that does one calculation. First it reads the slider as a number and keeps that copy, because the slider may move while Python works and the answer must be shown against the hours it was asked for.

```js
    try {
      const result = await callPython("relativity.drift_over_time",
        [receiver, satellites, config.relativityPhoneClockErrorS, [hours]]);
```
Asks Python's `drift_over_time` in `relativity.py` (see [`relativity.py`](../mechanism/relativity.py.md)). It is given the phone's position, the satellites, the phone's own clock error (0 seconds in [`config.js`](config.js.md)) and a list of hours with just one entry. In Python the drift is 38 millionths of a second per day, so for `hours` hours it is 38e-6 × hours / 24 seconds. It is added to every measured distance as a shared amount, in the same way a phone clock error would be (this is the model the page uses). The distance equivalent is that time times the speed of light. Worked example for 24 hours: 38e-6 × 299,792,458 = 11,392.1 metres. For 12 hours it is half of that, 5,696.1 metres. Python then solves the position twice, once solving for the clock and once trusting it, and returns a list with one row per hour.

```js
      if (result.error) { say(el.sentence, result.error); return; } // Python's own plain sentence
```
If Python replies with an `error`, its own plain sentence is shown in the summary line, and `return` stops. Without it a refused calculation would show nothing.

```js
      showResult(result[0], hours);
```
`result` is a list with one row, since one hour value was sent. `result[0]` is that first row (lists count from 0). It is shown with `showResult`.

```js
    } catch (error) {
      console.error(error);
      say(el.sentence, "Something went wrong in the calculation, so the numbers may be out of date.");
    }
  }
```
If anything fails, write the error to the developer console and tell the reader, "Something went wrong in the calculation, so the numbers may be out of date." The last `}` closes `runOnce`. Without the `try` and `catch`, an error would be silent.

```js
  function showResult(row, hours) {
```
A function that puts one row of Python's answer on the page.

```js
    el.range.textContent = formatMetres(row.range_added_m);
```
Shows how much the drift added to each distance. Example: `range_added_m` is 11392.1 for 24 hours, so `formatMetres` gives "11,392 m". At 1 hour: 474.67, shown as "475 m". (`formatMetres` shows one decimal place under 100 m and whole metres from 100 m up.)

```js
    showError(el.trusted, el.trustedBadge, row.error_clock_trusted_m);
    showError(el.solved, el.solvedBadge, row.error_clock_solved_m);
```
Shows the two position errors, each with its number box and badge. The first is the error if the phone trusted its clock. The second is the error when the clock is solved. Python measures each as the straight-line distance between the found position and the true one. With the page's settings (no noise, phone clock error 0): at 0 hours both are 0 m; at 1 hour the trusted error is about 824 m and the solved one 0 m; at 12 hours 9,885 m and 0 m; at 24 hours 19,767 m and 0 m. The trusted error is bigger than the 11,392 m added to each distance because the four distance errors are combined through the satellites' layout. The solved error stays 0 m because the solver takes the whole shared drift as clock error (38 microseconds after 24 hours), so none of it becomes a position error.

```js
    const sentence = hours === 0
      ? "No drift yet. Both ways of solving agree."
      : "Every distance is wrong by the same amount, so solving for the clock absorbs it. Trusting the clock would not.";
```
Chooses the summary sentence with a short if. `===` asks "exactly equal?". At zero hours the sentence is "No drift yet. Both ways of solving agree." At any other hour it is "Every distance is wrong by the same amount, so solving for the clock absorbs it. Trusting the clock would not."

```js
    if (el.sentence.textContent !== sentence) say(el.sentence, sentence); // only when the words change
  }
```
Writes the sentence only if it differs from what is already shown. Otherwise dragging the slider would flash the same words over and over, and a screen reader could read them out again each time. The `}` closes `showResult`.

```js
  function showError(valueNode, badgeNode, errorM) {
    const level = errorLevel(errorM);
```
A function that shows one error. It receives the number element, the badge element and the error in metres. It first works out the level (`"ok"`, `"warn"` or `"bad"`) using `errorLevel` above.

```js
    valueNode.textContent = formatMetres(errorM);
```
Shows the number as text such as "0 m" (the solved error) or "19,767 m" (the trusted error after 24 hours).

```js
    badgeNode.hidden = false;
```
Reveals the badge, which started `hidden`.

```js
    badgeNode.className = `badge is-${level}`;
```
Sets the badge's classes to `badge` plus `is-ok`, `is-warn` or `is-bad`, which [`theme.css`](theme.css.md) colours differently. Example: an error of 50 m gives `badge is-warn`. Without it the badge keeps its first colour.

```js
    badgeNode.textContent = LEVEL_WORDS[level];
  }
}
```
Sets the badge words by looking up the level in `LEVEL_WORDS`: for example `"warn"` gives "Fix is off". The first `}` closes `showError` and the last closes `mountRelativityStep`. That is the end of the file.
