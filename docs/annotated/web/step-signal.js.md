# step-signal.js, line by line

Source: `web/step-signal.js`

## What this file is for
This file builds the third section of the page, "How does the phone measure the time?". It shows two graphs: what the phone hears (a known satellite pattern buried in noise) and how well the phone's copy of the pattern matches at every possible shift. A slider adds noise, so the reader can bury the signal until the phone loses it. The file draws and listens to the slider. Every number that is shown comes from Python.

## Which files it talks to
- `mechanism/signal.py`: the page asks for two things through the bridge. `signal.make_received` builds the noisy signal the phone hears, and `signal.correlate` tries every shift and scores each one. See [signal.py](../mechanism/signal.py.md).
- `web/startup.js`: `whenPythonReady` tells this file when Python has loaded, and shows the "Loading the maths…" progress and failure words. See [startup.js](startup.js.md).
- `web/say.js`: `say` puts a message in a message line and flashes it briefly. See [say.js](say.js.md).
- `web/theme.css`: gives the colours, fonts and the shared classes (`card`, `btn`, `badge`, `inset`, `num`, `label`, `muted`, `slider`). This file only adds layout. See [theme.css](theme.css.md).
- `index.html`: imports `mountSignalStep` and calls it with the empty box `step-signal`. See [index.html](../index.html.md).
- The exact shapes of the numbers passed to and returned from Python are in `docs/interface.md`.

## In three lines
1. When the page loads, `mountSignalStep` adds the section's HTML and style to the page and waits for Python.
2. Each time the slider moves, the file asks Python for the noisy signal, then asks Python to score every shift, then draws both graphs and the readout.
3. The only arithmetic in JavaScript is turning values into pixel positions, and choosing "Found", "Barely found" or "Lost" by comparing numbers Python returned.

New to code? See [how to read code](../how-to-read-code.md). Ideas used here for the first time are explained where they appear.

## The code, line by line

### The top note and the imports

```js
// Rung 3: how the time is measured (design.md 2a). It draws and takes input;
// the received signal and every score come from Python (mechanism/signal.py).
// The only arithmetic here is scaling numbers to pixels.
```
Three comments (lines starting with `//` are notes for people; the computer skips them). "Rung 3" is the third step of the page's story. `design.md` is the project's spec. They say that this file only draws and listens, that Python works out the signal and every score, and that the only arithmetic here is scaling to pixels. Nothing breaks without them.

```js
import { whenPythonReady } from "./startup.js";
```
Brings in one function, `whenPythonReady`, from [`startup.js`](startup.js.md). Python is downloaded into the browser when the page opens, which takes a few seconds. This function calls back when it is ready and shows the loading words in the meantime. Without it the file could not know when Python is ready, and the name would be unknown and the file would fail to load.

```js
import { say } from "./say.js";
```
Brings in `say`, which sets the words of a message line and flashes it for a moment so the reader notices even when the words are the same as before. Without it the messages below could not be shown.

### The settings

```js
// Every tunable number lives here.
```
A comment: all the numbers that can be changed are in the next object.

```js
export const signalConfig = {
```
Starts an object (a set of labelled values in curly brackets) called `signalConfig`, and `export` shares it so other files could read it. It is the settings list for this section only.

```js
  prn: 7, // placeholder, provisional: which satellite's code (1 to 32)
```
`prn` is the number that tells the satellites apart: each one sends its own pattern, and the numbers go from 1 to 32. Here it is 7. The note says it is a placeholder (a temporary value that stays until Icarus confirms it). Without it Python would not know whose pattern to use.

```js
  trueDelayChips: 300, // placeholder, provisional: how late the signal really arrives
```
A chip is one step of the pattern (the pattern has 1023 chips). The real signal is made to arrive 300 chips late. The phone's job is to find that 300. Without it there would be no hidden delay to find.

```js
  seed: 1, // placeholder, provisional: same noise every time, so a run can be repeated
```
Noise is random. A seed is a starting number for the random numbers: the same seed gives the same noise every time. This makes a run repeatable, so a given slider position always draws the same picture. Without it the page would have no seed to send to Python's `make_received`, which only accepts a whole number of 0 or more.

```js
  signalSize: 1, // placeholder, provisional: the code has size 1 (interface.md)
```
The pattern's values are +1 or -1, so its size is 1. This is used only to say whether the noise is bigger than the signal (further down).

```js
  noise: { min: 0, max: 12, step: 0.5, start: 0 }, // placeholder, provisional: noise size, in multiples of the signal
```
The slider's range for noise, measured in multiples of the signal: from 0 to 12 in steps of 0.5, starting at 0. A nested object (an object inside an object). Without it the slider would have no range.

```js
  barelyHoldingBelow: 1.5, // placeholder, provisional: peak_to_next under this = found but barely
```
`peak_to_next` is a number Python returns: the best score divided by the second best score. If it is under 1.5, the best match is found but only just clear of the rest. Worked example: a best score of 0.3 and a second best of 0.25 give 0.3 / 0.25 = 1.2, which is under 1.5, so "barely".

```js
  peakDisplayCap: 1000, // placeholder, provisional: above this the readout says "over 1000x"
```
The biggest value shown exactly. With the page's settings and no noise, the ratio is only about 16.2 (best score 1.0, second best about 0.06), so the cap is not reached. It is there for one special case: when the best score is above 0 and no other score is, Python returns 1,000,000,000 ("extremely clear"). At 1000 or more the readout says "over 1000×" instead of a giant number.

```js
  receivedLimit: 4, // placeholder, provisional: the top graph shows values from -4 to +4, bigger ones are cut off
```
The top graph shows values from -4 to +4. Anything outside is cut off at the edge. Without this limit big noise would be drawn off the graph.

```js
  scoreRange: { min: -0.5, max: 2.5 }, // placeholder, provisional: the bottom graph shows scores in this range
```
The bottom graph shows scores from -0.5 to 2.5. Without it the bottom graph would have no scale.

```js
};
```
Closes the object.

### Fixed names and the style

```js
const SVG = "http://www.w3.org/2000/svg";
```
A fixed piece of text (the standard web address that names the drawing language called SVG, which draws shapes like lines on a page). Names in capital letters are a habit meaning "never changes". In this file it is not used again further down, so removing it would not change how the page behaves.

```js
const RECEIVED_LABEL = "The received signal: the satellite's pattern plus noise, one value per chip.";
const SCORES_LABEL = "The match score at every shift. A tall peak means the phone found the signal's timing.";
```
Two descriptions of the two graphs. A screen reader (software that reads the page aloud to people who cannot see it) cannot read a picture, so each graph has an `aria-label`: words that describe it. `aria-*` attributes are extra labels for such software. These two are the starting words; `draw` adds the live numbers to them later.

```js
const PLOT_HEIGHT = 120; // the viewBox of both graphs is (number of chips) wide and 120 high
```
Each graph is drawn on a canvas that is 1023 units wide (one per chip) and 120 units high. This is the height. A `viewBox` is the private coordinate system of a drawing (the page then stretches it to fit). Without it the drawing code could not place anything vertically.

```js
// Layout for this section only. Colours, fonts and radii come from theme.css.
const STYLE = `
```
A comment, then the start of one long piece of text, written between backticks (the backtick quotes allow text over many lines). It holds CSS: the rules for how things look. CSS is explained at "A CSS rule" in [how to read code](../how-to-read-code.md). This text is later put in the page. Colours, fonts and rounded corners are left to [`theme.css`](theme.css.md); here only layout is set. A `var(--s-5)` means "use the value of the setting named `--s-5`", which `theme.css` defines (a CSS variable). The spacing ones are `--s-2` 8 px, `--s-3` 12 px, `--s-4` 16 px and `--s-5` 24 px. A pixel (px) is one dot on the screen.

```js
.signal-step { display: grid; grid-template-columns: minmax(0, 1fr); gap: var(--s-5); }
```
The whole section is a grid (a layout of rows and columns) with one column that may shrink to nothing and grow to fill the width (`minmax(0, 1fr)`). `gap` is the space between items: 24 px. Without `minmax(0, ...)` a wide child could push the page wider than the screen.

```js
.signal-step .intro { display: grid; gap: var(--s-2); }
```
The heading and its paragraph form a small grid with 8 px between them.

```js
.signal-step .grid { display: grid; grid-template-columns: minmax(0, 1fr); gap: var(--s-5); }
```
The main area (the graphs and the controls) is also one column on a narrow screen, with 24 px between the two cards.

```js
@media (min-width: 760px) { .signal-step .grid { grid-template-columns: 1.4fr 1fr; align-items: start; } }
```
A media query is a rule that only applies when a condition is true. Here: only when the window is at least 760 px wide. Then the area becomes two columns, the left 1.4 shares wide and the right 1 share (`fr` means "share"), and both start at the top. On a phone it stays one column.

```js
.signal-step .stack { display: grid; gap: var(--s-4); }
```
The controls card stacks its parts with 16 px between them.

```js
.signal-step .plot { width: 100%; height: 120px; display: block; margin-top: var(--s-2); }
```
Each graph fills the card's width, is 120 px high, behaves as a block (so no stray gap appears under it) and has 8 px of space above it.

```js
.signal-step .axis { display: flex; justify-content: space-between; font-size: var(--text-xs); color: var(--text-muted); }
```
The little labels under each graph ("chip 0" and "chip 1022") sit in a row (`flex`) pushed to the two ends (`space-between`), in small (12 px) grey text.

```js
.signal-step .received { fill: none; stroke: var(--text); stroke-width: 1; vector-effect: non-scaling-stroke; }
```
The line in the top graph: no fill inside, drawn in the main text colour (`stroke` is the colour of a line) and 1 pixel thick. The graph is stretched to fit its box, which would normally also stretch the line's thickness. `non-scaling-stroke` stops that, so the line stays 1 pixel thick. Without it the line would look thick in one direction and thin in the other.

```js
.signal-step .scores { fill: none; stroke: var(--text-muted); stroke-width: 1; vector-effect: non-scaling-stroke; }
```
The score line in the bottom graph, the same, but in the grey text colour.

```js
.signal-step .mark-true { stroke: var(--text-muted); stroke-width: 1; stroke-dasharray: 3 3; vector-effect: non-scaling-stroke; }
```
The marker for where the signal really is: a grey line 1 pixel thick. `stroke-dasharray: 3 3` makes it dashed: 3 units drawn, 3 units gap.

```js
.signal-step .mark-best { stroke: currentColor; stroke-width: 2; vector-effect: non-scaling-stroke; }
```
The marker for the best match the phone found: a solid line 2 pixels thick. `currentColor` means "use the text colour of the surrounding element". The group around it gets a class `is-ok`, `is-warn` or `is-bad` (see `draw`), which sets that colour. So the line turns green, amber or red with the result.

```js
.signal-step .key { font-size: var(--text-sm); }
```
The explanation under the graphs uses 14 px text.

```js
.signal-step .readout { padding: var(--s-4); display: grid; gap: var(--s-2); }
```
The box with the results has 16 px of space inside and its rows are 8 px apart.

```js
.signal-step .readout-row { display: flex; justify-content: space-between; align-items: baseline; gap: var(--s-3); }
```
A row in that box: a name on the left and a number on the right (`space-between`), lined up along the bottom of the letters (`baseline`), with at least 12 px between them.

```js
.signal-step .big { font-size: var(--text-xl); }
```
The "Best delay found" number is large (32 px).

```js
.signal-step .badge[hidden] { display: none; }
```
`hidden` is an attribute (an extra setting on an HTML element) that means "do not show this". The shared `badge` style in [`theme.css`](theme.css.md) sets how a badge is laid out, which would override `hidden`. This line makes sure that a badge with `hidden` really disappears. Without it an empty badge would show before the first result.

```js
.signal-step .note { font-size: var(--text-sm); color: var(--text-muted); min-height: 1.5em; }
```
A message line: small grey text that always keeps at least 1.5 lines of height (`em` is the size of one letter), so the page does not jump when a message appears.

```js
.signal-step .note:empty { min-height: 0; }
```
`:empty` picks any note that has no words in it. Those take no space at all. This stops blank gaps in the controls.

```js
.signal-step .note[data-el="msg-slider"]:empty { min-height: 1.5em; }
```
But the message line right under the slider keeps its height even when empty. Without it the controls would shift each time an error message appeared or disappeared. `data-el="msg-slider"` picks the one element whose `data-el` label is that.

```js
.signal-step h3.label { margin-bottom: var(--s-3); }
```
The small headings above each graph have 12 px of space below them.

```js
.signal-step .highlight { border-color: var(--accent); padding: var(--s-4); }
```
The box holding the slider has an outline in the accent colour (to draw the eye to it) and 16 px of space inside.

```js
.signal-step .hint { font-size: var(--text-sm); font-weight: 500; color: var(--text); }
```
The hint "Drag this slider..." is 14 px, a little bolder, and in the full text colour so it stands out.

```js
.signal-step .slider-head { flex-wrap: wrap; column-gap: var(--s-3); }
```
The row with the "Add noise" label and its value may wrap to a second line on a narrow screen, with 12 px between the items.

```js
.signal-step .btn { touch-action: manipulation; }
```
On a touch screen, tells the browser the button needs no double-tap zoom. This makes a tap react at once.

```js
.signal-step .btn:disabled, .signal-step input[type="range"]:disabled { opacity: 0.4; cursor: not-allowed; }
```
`:disabled` picks a control that cannot be used right now. The button and the slider are disabled until Python has loaded. This makes them 40 percent solid (faded) and shows a "not allowed" mouse cursor. Without it a locked control would look like a working one.

```js
.signal-step .btn:disabled:hover { border-color: var(--line-strong); }
```
When the mouse is over a disabled button, its outline does not change. A working button highlights on hover; a locked one should not.

```js
.signal-step input[type="range"] { touch-action: pan-y; }
```
The slider is an `input` of type `range`. On a touch screen, `pan-y` lets the finger scroll the page up and down when it starts on the slider, while left and right drags move the slider. Without it, a finger on the slider could block scrolling.

```js
`;
```
Closes the long piece of text.

### Building the section

```js
export function mountSignalStep(container) {
```
Starts a function (a named recipe) called `mountSignalStep` and shares it. `container` is the empty page element the section goes into ([`index.html`](../index.html.md) hands it `step-signal`). Everything below, up to the closing bracket just before `addStyleOnce`, is the inside of this function. "Mount" means "put onto the page". Without it `index.html` would have nothing to call.

```js
  addStyleOnce();
```
Calls a helper further down that puts the CSS above into the page, once. Without it the section would have no layout.

```js
  container.insertAdjacentHTML("beforeend", PAGE_HTML);
```
The DOM is the browser's live model of the page: a tree of elements (each tag such as a paragraph or a button becomes an element). `insertAdjacentHTML` turns the text `PAGE_HTML` (at the bottom of the file) into elements and adds them inside `container`, at its end (`"beforeend"`). Without it the section would stay empty.

```js
  const root = container.lastElementChild;
```
Takes the element just added (the last child of the container) and calls it `root`. Later searches only look inside it. Without it the file would have to search the whole page, and could pick up the wrong thing.

```js
  const find = (name) => root.querySelector(`[data-el="${name}"]`);
```
Makes a small helper called `find`. An arrow function (`(name) => ...`) is a short way to write a function. Given a name such as `"slider"` it looks inside `root` for the element whose `data-el` attribute equals that name (`querySelector` finds the first match). Worked example: `find("noise")` finds the slider, which is written `data-el="noise"` in the HTML below. The backticks with `${name}` put the name into the text. The `data-el` labels are used instead of `id`s so that the section does not clash with other parts of the page.

```js
  const el = {
    status: find("status"), hint: find("hint"), clipNote: find("clip-note"), receivedPlot: find("received-plot"), scoresPlot: find("scores-plot"), slider: find("noise"), sliderValue: find("noise-value"), msgSlider: find("msg-slider"),
    reset: find("reset"), msgReset: find("msg-reset"), receivedLine: find("received-line"), scoresLine: find("scores-line"),
    trueMark: find("true-mark"), bestMark: find("best-mark"), bestGroup: find("best-group"),
    bestDelay: find("best-delay"), trueDelay: find("true-delay"), peak: find("peak"),
    badge: find("badge"), sentence: find("sentence"),
  };
```
Makes an object called `el` that holds every element the code will touch, each under a short name. Doing the search once here, instead of at every use, is quicker and keeps names in one place. What each one is: `status` the "Loading the maths…" line; `hint` the "Drag this slider" hint; `clipNote` the warning that the noise is cut off; `receivedPlot` and `scoresPlot` the two graph drawings; `slider` the noise slider and `sliderValue` the words showing its value; `msgSlider` the message line under the slider; `reset` the Reset button and `msgReset` its message line; `receivedLine` and `scoresLine` the two lines drawn in the graphs; `trueMark` the dashed marker for the real delay, `bestMark` the solid marker for the best match and `bestGroup` the group that holds it; `bestDelay`, `trueDelay` and `peak` the three numbers in the readout; `badge` the "Found" label and `sentence` the one sentence of explanation. If a name were wrong, `find` would give nothing and the first use below would fail.

```js
  let callPython = null; // set when the bridge has loaded
```
`let` makes a variable that can change later (unlike `const`). `callPython` will hold the function that sends a request to Python. The bridge is the connection between the page and Python. `null` means "nothing yet". Without it the file would have no way to ask Python.

```js
  let noise = signalConfig.noise.start;
```
The current noise, starting at 0 (the `start` value from the settings).

```js
  let running = false;
  let rerun = false;
```
Two yes/no flags (`true` or `false`). `running` is true while a request to Python is in progress. `rerun` is true when the slider moved while that request was running, so a fresh one is needed afterwards. They are used by `update` below.

```js
  let hintDone = false; // once the user has touched the slider, the hint stays hidden
```
Whether the reader has touched the slider yet. Once they have, the hint is not shown again (even if Python finishes loading later).

```js
  setupControls();
  start();
```
Two calls, in this order: set up the slider and button, then start waiting for Python. Both are defined below. A function can be called before the line where it is written because JavaScript reads the whole function first. Without them nothing would run.

### Start up

```js
  // ---------- start up ----------
```
A comment that marks a section of the file. Nothing breaks without it.

```js
  function start() {
```
Starts a function called `start`.

```js
    whenPythonReady(el.status, (call) => {
```
Asks [`startup.js`](startup.js.md) to say when Python is ready. The first thing given is the status line, so `startup.js` can show "Loading the maths…" or a failure message there. The second is a function to run once Python is ready; it receives `call`, the function that sends requests to Python.

```js
      callPython = call;
```
Saves it in the variable made earlier, so the rest of the file can use it.

```js
      setControlsDisabled(false);
```
Unlocks the slider and the Reset button (they start locked).

```js
      el.hint.hidden = hintDone;
```
Shows the hint ("Drag this slider to bury the signal in noise, until the phone loses it.") unless the reader has already used the slider. `hidden = false` shows it, `hidden = true` hides it, so the flag sets this directly.

```js
      update();
```
Does the first calculation and drawing, so the graphs are filled in as soon as Python is ready.

```js
    });
  }
```
Closes the function given to `whenPythonReady`, then `start`.

### The controls

```js
  // ---------- controls ----------
```
A section marker.

```js
  function setupControls() {
```
Starts the function that sets up the slider and the Reset button.

```js
    const { min, max, step, start: startValue } = signalConfig.noise;
```
Destructuring: takes four values out of the `noise` settings in one line and gives each a name. `start` is renamed `startValue` here, because a function called `start` already exists. With the real numbers: `min` is 0, `max` is 12, `step` is 0.5, `startValue` is 0.

```js
    // The slider counts steps (whole numbers), so there are no floating point surprises.
```
A comment. Computers store numbers like 0.1 slightly inexactly (a "floating point" surprise). The slider therefore counts whole steps and the file turns them into noise afterwards.

```js
    el.slider.min = 0;
    el.slider.max = Math.round((max - min) / step);
    el.slider.step = 1;
    el.slider.value = Math.round((startValue - min) / step);
```
Sets the slider's own properties. It starts at step 0 and moves 1 step at a time. Its top is `Math.round((max - min) / step)` (`Math.round` rounds to the nearest whole number). Worked example: (12 - 0) / 0.5 = 24, so the slider has 24 steps, 0 to 24. The starting position is (0 - 0) / 0.5 = 0, the left end (no noise). Without these lines the slider would use the browser's default range of 0 to 100.

```js
    el.slider.addEventListener("input", () => {
```
An event is something that happens on the page, like a click or a drag. `addEventListener` says "when this happens to the slider, run this function". `"input"` fires every time the slider moves, even in the middle of a drag. Without it the slider would do nothing.

```js
      noise = Number(el.slider.value) * step + min;
```
Turns the slider position back into a noise size. `el.slider.value` comes as text, so `Number(...)` makes it a number. Worked example: position 7 gives 7 x 0.5 + 0 = 3.5, so the noise is 3.5 times the signal. Without it the file would not know the noise.

```js
      el.hint.hidden = true;
      hintDone = true;
```
The reader has used the slider, so the hint is hidden and remembered as done. Without the second line the hint would come back when Python finished loading.

```js
      el.msgReset.textContent = "";
```
Clears the message under the Reset button (such as "Back to the start: no noise."), because it is out of date now. `textContent` is the words inside an element.

```js
      showNoiseValue();
      update();
```
Updates the words next to the slider, then starts a new calculation and drawing.

```js
    });
```
Closes the slider's event function.

```js
    el.reset.addEventListener("click", () => {
```
When the Reset button is clicked, run this function.

```js
      noise = startValue;
      el.slider.value = Math.round((startValue - min) / step);
```
Puts the noise back to 0 and moves the slider back to its starting position (0 steps).

```js
      showNoiseValue();
      update();
```
Updates the words, then redraws.

```js
      say(el.msgReset, "Back to the start: no noise.");
```
Shows "Back to the start: no noise." under the button and flashes it. Without it, pressing Reset when the picture is already at the start would show nothing, and the press would feel dead.

```js
    });
```
Closes the Reset function.

```js
    el.trueDelay.textContent = `${signalConfig.trueDelayChips} chips`;
```
Writes the real delay in the readout. With the settings it reads "300 chips". It never changes, so it is written once.

```js
    drawMark(el.trueMark, signalConfig.trueDelayChips);
```
Draws the dashed line at chip 300 in the bottom graph (see `drawMark` below). It is drawn once, since the true delay never changes.

```js
    showNoiseValue();
    setControlsDisabled(true);
```
Writes the starting words next to the slider, then locks the slider and button until Python is ready (`start` unlocks them).

```js
  }
```
Closes `setupControls`.

```js
  function setControlsDisabled(disabled) {
    el.slider.disabled = disabled;
    el.reset.disabled = disabled;
  }
```
A helper: `true` locks both controls, `false` unlocks them. A disabled control ignores clicks and drags. Without it the reader could move the slider before Python has loaded, and nothing could answer.

```js
  function showNoiseValue() {
```
Starts the function that writes the noise size in words.

```js
    el.sliderValue.textContent = noise === 0 ? "No noise" : `${noise.toFixed(1)}× the signal`;
```
The words next to the slider. `a ? b : c` is a short if: if the noise is exactly 0, say "No noise", otherwise write the noise to one decimal place (`toFixed(1)`) followed by "× the signal". Worked example: noise 3.5 gives "3.5× the signal"; noise 3 gives "3.0× the signal".

```js
    el.slider.setAttribute("aria-valuetext", noise === 0 ? "No noise" : `Noise ${noise.toFixed(1)} times the signal`);
```
An attribute is an extra setting on an element. `aria-valuetext` is read aloud by a screen reader instead of the slider's raw position number (which is 0 to 24 and means nothing to the listener). The symbol "×" may be read badly, so here the words are "Noise 3.5 times the signal". Without it the listener would hear "7" and not know what it means.

```js
  }
```
Closes `showNoiseValue`.

### One run: ask Python, then draw

```js
  // ---------- one run: ask Python, then draw ----------
```
A section marker.

```js
  // Python calls are async. If one is running, remember that a newer run is wanted and do it once after.
```
A comment. A call to Python takes a moment, and the page must not freeze while it waits. That is what "async" (asynchronous) means: start the job, carry on, come back when it is done. If the reader keeps dragging, the file does not start a pile of calls; it remembers that one more is wanted and does just one after the current one.

```js
  async function update() {
```
Starts a function called `update`. `async` marks a function that may wait for slow things. Inside it, the word `await` means "pause here until this finishes, but let the rest of the page keep working".

```js
    if (!callPython) return;
```
If Python is not ready yet (`callPython` is still `null`; `!` means "not"), stop at once. `return` leaves the function. Without it a drag before loading would try to use a function that does not exist.

```js
    if (running) { rerun = true; return; }
```
If a run is already in progress, only note that another is wanted and leave. Without it, overlapping runs could finish in the wrong order and draw an old picture over a new one.

```js
    running = true;
```
Marks that a run has started.

```js
    try {
```
`try` starts a block where something might go wrong. If it does, the code jumps to `catch` below instead of crashing.

```js
      do {
        rerun = false;
        await runOnce();
      } while (rerun);
```
A `do ... while` loop: do the body, then repeat while the condition is true. It clears the `rerun` flag, then waits for `runOnce` (one full ask-and-draw). If the slider moved meanwhile, `rerun` is true again, so it goes round again with the new noise. When no move happened, it ends. Without the loop, a move during a run would be lost and the picture would not match the slider.

```js
    } catch (error) {
```
This runs if something inside `try` failed.

```js
      console.error(error);
```
Writes the technical error in the browser's developer console (a hidden window for programmers). It is for the team, not the reader.

```js
      say(el.msgSlider, "Something went wrong while calculating, so the picture may be out of date.");
```
Tells the reader in plain words, in the message line under the slider. Without it a failure would be silent.

```js
    } finally {
      running = false;
    }
```
`finally` runs whether or not there was an error. It marks that nothing is running. Without it, one error would leave `running` stuck on `true` and the slider would never work again.

```js
  }
```
Closes `update`.

```js
  async function runOnce() {
```
Starts the function that does one complete run.

```js
    const { prn, trueDelayChips, seed } = signalConfig;
```
Takes three settings out of `signalConfig`: 7, 300 and 1.

```js
    const usedNoise = noise; // the slider may move while Python works
```
Copies the noise now. If the slider moves while Python is busy, `noise` changes, but this run keeps drawing for the value it asked for. Without the copy, the picture could show one noise value in the graph and a different one in the words.

```js
    el.msgSlider.textContent = "";
```
Clears the message line under the slider (an earlier error), because a new run is starting.

```js
    const received = await callPython("signal.make_received", [prn, trueDelayChips, usedNoise, seed]);
```
Asks Python to run `make_received` from `mechanism/signal.py` (see [signal.py](../mechanism/signal.py.md)), giving it the satellite number, the delay in chips, the noise size and the seed, and waits. Python shifts the satellite's pattern later by 300 chips and adds random noise of that size. It returns a list of 1023 numbers: what the phone hears. Without this line there would be nothing to draw.

```js
    if (failed(received)) return;
```
If Python answered with an error message instead of numbers, show it and give up on this run (see `failed` below).

```js
    const result = await callPython("signal.correlate", [received, prn]);
```
Asks Python's `correlate` function to try all 1023 shifts of the satellite's pattern against what was heard and score each one. It sends the heard signal and the satellite number. It returns `scores` (1023 numbers), `best_delay_chips` (the shift with the best score) and `peak_to_next` (how many times better the best score is than the second best).

```js
    if (failed(result)) return;
```
The same check for the second answer.

```js
    requestAnimationFrame(() => draw(received, result, usedNoise));
```
`requestAnimationFrame` asks the browser to run a function just before it next paints the screen. Drawing then happens at the right moment, which avoids flicker and wasted work. The function calls `draw` with everything this run produced. Without it the numbers would never reach the screen.

```js
  }
```
Closes `runOnce`.

```js
  function failed(result) {
```
Starts a helper that says whether Python's answer was an error.

```js
    if (!result || !result.error) return false;
```
If there is no answer at all, or the answer has no `error` part, it is not a failure, so answer `false` ("no, it did not fail"). Python returns an object with an `error` sentence when its input was wrong.

```js
    say(el.msgSlider, result.error); // Python's own plain sentence
```
Otherwise show Python's sentence in the message line under the slider. The mechanism writes these sentences in plain words, so the page does not rewrite them.

```js
    return true;
  }
```
Answers `true` ("yes, it failed") and closes the helper. Without it the callers would carry on and draw from an error.

### Reading the result

```js
  // ---------- reading the result ----------
```
A section marker.

```js
  // "Lost" means the best shift is not the true delay. The threshold only separates ok from "barely".
```
A comment that sets out the rule. "Lost" is decided by whether Python's best shift equals the real delay. The 1.5 limit only separates a clear find from a barely-clear one.

```js
  function levelOf(result) {
```
Starts a function that turns Python's answer into one of three levels: `"ok"`, `"warn"` or `"bad"`.

```js
    if (result.best_delay_chips !== signalConfig.trueDelayChips) return "bad";
```
If the best shift is not 300 (`!==` means "is not equal to"), the phone picked the wrong place: the level is "bad". Without it a wrong answer would be shown as a success.

```js
    return result.peak_to_next < signalConfig.barelyHoldingBelow ? "warn" : "ok";
```
Otherwise the phone found the right place, and the level depends on how clearly. Worked examples: `peak_to_next` 1.2 is under 1.5, so "warn"; 12.4 is not, so "ok". With the page's settings (satellite 7, delay 300, seed 1), Python gives: no noise 16.2 (Found), noise 5 gives 1.9 (Found), noise 8 gives 1.2 (Barely found), and noise 10 picks shift 713 instead of 300 (Lost).

```js
  }
```
Closes `levelOf`.

```js
  const levelWords = { ok: "Found", warn: "Barely found", bad: "Lost" };
```
The word shown in the badge for each level: "Found", "Barely found" or "Lost".

```js
  function sentenceFor(level, usedNoise) {
```
Starts a function that picks the one explanatory sentence.

```js
    if (level === "bad") return "The phone can no longer find where the signal starts.";
    if (level === "warn") return "The match still points to the right place, but only just.";
```
For "bad" and "warn", it returns those exact sentences. `===` means "is equal to". Once a function reaches a `return`, it ends, so later lines are skipped.

```js
    if (usedNoise > signalConfig.signalSize) return "The noise is bigger than the signal, yet the match still finds it.";
```
If we reach this line the level is "ok". If the noise is bigger than the signal (above 1), say so: the phone still finds it. Worked example: noise 3.5 is bigger than 1, so this sentence is used. Why it works: the pattern is 1023 chips long and noise is random, so a total over all chips still adds up in one place only.

```js
    return "The match stands out clearly from everything else.";
```
Otherwise (small noise) this is the sentence. Without a final line the function would return nothing, and the page would show no sentence.

```js
  }
```
Closes `sentenceFor`.

```js
  function formatPeak(value) {
```
Starts a function that turns `peak_to_next` into words for the readout.

```js
    if (value >= signalConfig.peakDisplayCap) return `over ${signalConfig.peakDisplayCap}×`;
```
At 1000 or more, show "over 1000×" (the cap goes into the sentence). Worked example: Python's "extremely clear" value of 1,000,000,000 would be shown as "over 1000×", not as ten digits.

```js
    return `${value.toFixed(1)}×`;
```
Otherwise show the number with one decimal place. Worked example: 12.34 becomes "12.3×".

```js
  }
```
Closes `formatPeak`.

### Drawing

```js
  // ---------- drawing ----------
```
A section marker.

```js
  function draw(received, result, usedNoise) {
```
Starts the function that puts a run's results on the screen. It gets the heard signal, Python's scoring result and the noise that was used.

```js
    const { receivedLimit, scoreRange } = signalConfig;
```
Takes out the two graph scales: 4, and the range -0.5 to 2.5.

```js
    el.receivedLine.setAttribute("points", toPoints(received, -receivedLimit, receivedLimit));
```
Draws the top graph. A `polyline` is an SVG shape: a line through many points, and its `points` attribute lists them. `toPoints` (below) makes that list from the 1023 values, scaled to run from -4 to +4. Without this line the top graph would stay empty.

```js
    el.scoresLine.setAttribute("points", toPoints(result.scores, scoreRange.min, scoreRange.max));
```
The same for the bottom graph, using the scores and the range -0.5 to 2.5.

```js
    const level = levelOf(result);
```
Works out the level (`"ok"`, `"warn"` or `"bad"`) once, and uses it below.

```js
    drawMark(el.bestMark, result.best_delay_chips);
```
Draws the solid line at the shift Python found best (see `drawMark`).

```js
    el.bestGroup.setAttribute("class", `is-${level}`);
```
Sets the `class` of the group around that line to `is-ok`, `is-warn` or `is-bad`. A class is a label that CSS rules can match. The shared rules in [`theme.css`](theme.css.md) give those classes green, amber and red colours, and the solid line's `currentColor` follows. Without it the line would not change colour with the result.

```js
    el.bestDelay.textContent = `${result.best_delay_chips} chips`;
```
Writes the best delay in the readout, for example "300 chips".

```js
    el.peak.textContent = formatPeak(result.peak_to_next);
```
Writes how much the peak stands out, for example "12.3×".

```js
    el.badge.hidden = false;
```
Shows the badge (it starts hidden, because before the first run it has nothing to say).

```js
    el.badge.className = `badge is-${level}`;
```
Sets all the badge's classes at once: `badge` (its shape) plus the colour class. This replaces the old colour. Without it the badge would keep an old colour.

```js
    el.badge.textContent = levelWords[level];
```
Writes "Found", "Barely found" or "Lost". Square brackets pick the entry named by `level` from the object `levelWords`.

```js
    el.sentence.textContent = sentenceFor(level, usedNoise);
```
Writes the one-sentence explanation. It is in a `role="status"` line, which a screen reader announces when it changes.

```js
    // Noise peaks regularly pass the graph's edge once the noise is more than half the graph's range.
```
A comment giving the reason for the next lines.

```js
    el.clipNote.textContent = usedNoise * 2 > receivedLimit
      ? "The noise is now taller than this graph, so its peaks are cut off at the top and bottom." : "";
```
Writes a warning when the noise is large and leaves it empty otherwise. Worked example: the limit is 4, so `usedNoise * 2 > 4` means noise above 2. Noise 3.5 gives 7 > 4, so the warning shows; noise 1.5 gives 3, not above 4, so the line is empty. The graph shows -4 to +4 and noise swings both ways, so large noise runs off the edge. Without it a reader might think the flat tops were the real signal.

```js
    const noiseWords = `${usedNoise.toFixed(1)} times the signal`;
```
The noise as words, for example "3.5 times the signal". It is used in the label below.

```js
    el.receivedPlot.setAttribute("aria-label", `${RECEIVED_LABEL} Noise ${noiseWords}.`);
```
Updates the description that a screen reader gives for the top graph: the fixed words plus the noise, for example "...one value per chip. Noise 3.5 times the signal." Without it a listener could not tell how noisy it is.

```js
    el.scoresPlot.setAttribute("aria-label",
      `${SCORES_LABEL} Best match at shift ${result.best_delay_chips}; the real delay is ${signalConfig.trueDelayChips}.`);
```
The same for the bottom graph: the fixed words, then "Best match at shift 300; the real delay is 300." This is the information a sighted reader gets by comparing the two lines. (A statement may continue on the next line; the closing bracket ends it.)

```js
  }
```
Closes `draw`.

```js
  // One point per chip: x is the chip number, y is the value scaled into the graph (cut off at the edges).
```
A comment describing `toPoints`: x is the chip's number, y is the value turned into a height, and values outside the range are cut off.

```js
  function toPoints(values, low, high) {
```
Starts the function. It gets the list of numbers and the lowest and highest values the graph shows.

```js
    return values.map((value, index) => {
```
`map` goes through a list and builds a new list: for every item, it runs the function and keeps the result. Here `value` is the number and `index` is its place in the list, starting at 0. The function's result is one `x,y` text for each of the 1023 values.

```js
      const clamped = Math.min(high, Math.max(low, value));
```
Cuts the value off to the range. `Math.max(low, value)` takes the bigger of the two, so nothing goes below `low`. `Math.min(high, ...)` takes the smaller, so nothing goes above `high`. Worked example with the top graph (low -4, high 4): a value of 10 becomes 4; a value of -7 becomes -4; a value of 1 stays 1. Without it big noise would be drawn outside the graph.

```js
      const y = PLOT_HEIGHT - ((clamped - low) / (high - low)) * PLOT_HEIGHT;
```
Turns the value into a height. (`clamped - low) / (high - low)` is how far along the range the value is, from 0 to 1. Times 120 gives a distance from the bottom. Screens count y downwards from the top, so the result is taken away from 120 to flip it. Worked example (top graph): value 1: (1 - (-4)) / (4 - (-4)) = 5 / 8 = 0.625; 0.625 x 120 = 75; y = 120 - 75 = 45. Value 4 gives y = 0 (the top); value -4 gives y = 120 (the bottom). Worked example (bottom graph, range -0.5 to 2.5, span 3): a score of 1.0 gives (1.0 + 0.5) / 3 = 0.5, so y = 120 - 60 = 60, halfway; a score of 0 gives 0.5 / 3 x 120 = 20, so y = 100.

```js
      return `${index},${y.toFixed(1)}`;
```
Joins the chip number and the height, to one decimal, with a comma. Worked example: chip 5 with y 45 gives "5,45.0". Because the graph's canvas is 1023 units wide, the chip number is already the right horizontal position, and no scaling is needed for x.

```js
    }).join(" ");
```
Closes the `map` and joins all 1023 texts into one, with a space between. This is the format the `points` attribute needs, for example `"0,60.0 1,58.5 2,61.2"`.

```js
  }
```
Closes `toPoints`.

```js
  function drawMark(line, chip) {
```
Starts a function that draws one upright line at a given chip. It is used for both the dashed and the solid marker.

```js
    line.setAttribute("x1", chip);
    line.setAttribute("x2", chip);
```
A `line` in SVG goes from (x1, y1) to (x2, y2). Both x values are the chip number, so the line is straight up and down. Worked example: chip 300 puts the line at x = 300.

```js
    line.setAttribute("y1", 0);
    line.setAttribute("y2", PLOT_HEIGHT);
```
The line runs from the top (0) to the bottom (120), the full height of the graph.

```js
  }
```
Closes `drawMark`.

```js
}
```
Closes `mountSignalStep`.

### Helpers outside the function

```js
function addStyleOnce() {
```
Starts a function that puts the CSS into the page. It sits outside `mountSignalStep` because it does not need any of that function's variables.

```js
  if (document.getElementById("signal-step-style")) return;
```
`document` is the whole page. If a `style` element with the id `signal-step-style` is already there, stop. The id is a name that is unique on the page. Without this check, mounting twice would add the same rules twice.

```js
  const style = document.createElement("style");
```
Makes a new, empty `style` element. It is not on the page yet.

```js
  style.id = "signal-step-style";
```
Gives it the id, so the check above can find it next time.

```js
  style.textContent = STYLE;
```
Puts the CSS text in it.

```js
  document.head.append(style);
```
Adds it to the page's `head` (the part of a page for settings, not shown). The browser then applies the rules. Without this line the section would have no layout.

```js
}
```
Closes `addStyleOnce`.

### The HTML of the section

```js
const PAGE_HTML = `
```
Starts one long piece of text with the section's HTML (the tags that make up the page, see "An HTML tag" in [how to read code](../how-to-read-code.md)). It is a constant, used by `insertAdjacentHTML` above. It sits at the bottom, but it is only used when `mountSignalStep` is called, after the whole file has loaded, so it exists by then.

```js
<section class="signal-step" aria-labelledby="signal-title">
```
The outer element for the whole section. `class="signal-step"` is what every CSS rule above starts with. `aria-labelledby="signal-title"` tells a screen reader that the heading with the id `signal-title` is the name of this section.

```js
  <header class="intro">
    <h2 id="signal-title">How does the phone measure the time?</h2>
```
An introduction block, and inside it the main heading, `h2`, with the id that the line above points to. The words "How does the phone measure the time?" are shown to the reader.

```js
    <p class="muted">The satellite's signal is a known pattern of 1023 steps, called chips. The phone slides its own copy along what it hears and scores the match at every shift.</p>
  </header>
```
A paragraph (`p`), in the grey `muted` style, that explains the idea in two sentences. Then the end of the introduction.

```js
  <div class="grid">
    <div class="card">
```
`div` is a plain box. The outer box is the `grid` (two columns on a wide screen). The first inner box is the left `card`: the graphs.

```js
      <h3 class="label">What the phone hears</h3>
```
A small heading over the top graph: "What the phone hears".

```js
      <svg class="plot" data-el="received-plot" viewBox="0 0 1023 120" preserveAspectRatio="none" role="img"
        aria-label="The received signal: the satellite's pattern plus noise, one value per chip.">
```
An `svg` is a drawing area. `viewBox="0 0 1023 120"` makes its inside 1023 units wide and 120 high, starting at 0,0. `preserveAspectRatio="none"` lets it stretch to fill its box instead of keeping its proportions, so one chip is always one equal slice of the width. `role="img"` tells a screen reader to treat the whole drawing as one picture, and `aria-label` is the description it reads out (the same words as `RECEIVED_LABEL`, which `draw` later extends). `data-el="received-plot"` is the label that `find` uses. Without `viewBox` the points would be placed in the wrong units.

```js
        <polyline class="received" data-el="received-line" points=""/>
      </svg>
```
The line that `draw` fills in. Its `points` start empty, so nothing is drawn until the first result. The slash at the end closes the tag, because it has nothing inside. Then the end of the drawing.

```js
      <div class="axis" aria-hidden="true"><span>chip 0</span><span>chip 1022</span></div>
```
The labels under the top graph: "chip 0" on the left and "chip 1022" on the right (a `span` is a small piece of text inside a line). `aria-hidden="true"` hides them from screen readers, because they only repeat what the graph's description says.

```js
      <p class="key muted" data-el="clip-note" role="status" aria-live="polite"></p>
```
The empty paragraph that `draw` fills with the "cut off" warning. `role="status"` and `aria-live="polite"` tell a screen reader to read out new words here when it is quiet, without interrupting. Without them a listener would not hear the warning appear.

```js
      <h3 class="label" style="margin-top: var(--s-5)">How well the code matches at each shift</h3>
```
The heading over the bottom graph. A `style` attribute puts a CSS rule on this one element: here 24 px of space above it (`--s-5`).

```js
      <svg class="plot" data-el="scores-plot" viewBox="0 0 1023 120" preserveAspectRatio="none" role="img"
        aria-label="The match score at every shift. A tall peak means the phone found the signal's timing.">
```
The bottom graph's drawing area, set up like the top one (1023 by 120 units, stretches, one picture for a screen reader), with the description from `SCORES_LABEL`.

```js
        <line class="mark-true" data-el="true-mark"/>
```
The dashed line for the real delay. It has no position yet; `setupControls` gives it one.

```js
        <polyline class="scores" data-el="scores-line" points=""/>
```
The score line, empty until `draw` fills it in.

```js
        <g data-el="best-group" class="is-ok"><line class="mark-best" data-el="best-mark"/></g>
      </svg>
```
A `g` is a group in SVG: it holds shapes together so they can share a class. This one holds the solid line for the best match. Its starting class `is-ok` is replaced by `draw` after each run. Then the end of the drawing. The group comes last so that the solid line is drawn on top of the others.

```js
      <div class="axis" aria-hidden="true"><span>shift 0</span><span>shift 1022</span></div>
```
The labels under the bottom graph: "shift 0" and "shift 1022", hidden from screen readers for the same reason as before.

```js
      <p class="key muted">Solid line: the best match the phone found. Dashed line: where the signal really is.</p>
    </div>
```
A key explaining the two lines. Then the end of the left card.

```js
    <div class="card stack">
```
The right card: the controls and results, stacked.

```js
      <p class="note" data-el="status" role="status" aria-live="polite">Loading the maths…</p>
```
The status line. It starts with "Loading the maths…". [`startup.js`](startup.js.md) changes it as Python loads, and clears it when ready.

```js
      <p class="hint" data-el="hint" hidden>Drag this slider to bury the signal in noise, until the phone loses it.</p>
```
The hint. It starts `hidden` (a bare attribute that means "do not show"). `start` shows it once Python is ready, unless the slider has been used.

```js
      <div class="slider inset highlight">
        <div class="slider-head">
```
The box that holds the slider, with three shared styles (`slider`, `inset` and `highlight`), and the row at its top.

```js
          <label for="signal-noise">Add noise</label>
```
A `label` is the visible name of a form control. `for="signal-noise"` links it to the input with that `id`, so a click on the words also focuses the slider, and a screen reader says "Add noise" for it.

```js
          <span class="num" data-el="noise-value">No noise</span>
        </div>
```
The words that show the current noise ("No noise" at the start), in number style. `showNoiseValue` changes them. Then the end of the row.

```js
        <input id="signal-noise" data-el="noise" type="range" disabled>
```
The slider itself. An `input` with `type="range"` is the browser's built-in slider. `id="signal-noise"` is what the label points to. `disabled` makes it locked from the start; `start` unlocks it when Python is ready. `setupControls` sets its range and starting position. Without it there would be nothing to drag.

```js
        <p class="note" data-el="msg-slider" role="status" aria-live="polite"></p>
      </div>
```
The message line under the slider, announced politely by screen readers. Errors appear here. Then the end of the slider box.

```js
      <div class="inset readout">
        <span class="label">Best delay found</span>
```
The results box and its first small heading, "Best delay found".

```js
        <span class="num big" data-el="best-delay">–</span>
```
The big number. It starts as a dash ("–") until the first result arrives.

```js
        <div class="readout-row"><span class="muted">Real delay</span><span class="num" data-el="true-delay">–</span></div>
        <div class="readout-row"><span class="muted">Peak stands out by</span><span class="num" data-el="peak">–</span></div>
```
Two rows, each with a name on the left and a number on the right: "Real delay" (filled in by `setupControls`, "300 chips") and "Peak stands out by" (filled in by `draw`, for example "12.3×").

```js
        <div><span class="badge is-ok" data-el="badge" hidden></span></div>
```
The badge that says "Found", "Barely found" or "Lost". It starts hidden and empty. It sits in its own `div` so it does not stretch the full width.

```js
        <p class="note" data-el="sentence" role="status" aria-live="polite"></p>
      </div>
```
The line for the one-sentence explanation, announced politely. Then the end of the results box.

```js
      <div>
        <button class="btn" data-el="reset" type="button" disabled>Reset</button>
```
The Reset button. `type="button"` says that it does nothing by itself (a button without it could try to send a form). It starts `disabled`.

```js
        <p class="note" style="margin-top: var(--s-2)" data-el="msg-reset" role="status" aria-live="polite"></p>
      </div>
```
The message line under the button, with 8 px of space above it. The "Back to the start: no noise." message goes here. Then the end of this box.

```js
    </div>
  </div>
</section>`;
```
Closes, in order: the right card, the grid and the section, then the backtick that ends the long text, and the semicolon that ends the line. Without any of these closings the page structure would be wrong, or the file would fail to load.
