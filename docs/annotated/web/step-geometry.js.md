# step-geometry.js, line by line

Source: `web/step-geometry.js`

## What this file is for
This builds the second section of the page, "Does it matter where the satellites are?". It shows a sky diagram with four satellites and a slider that pushes them from spread out to bunched together. Each time the slider moves, the page asks Python for the answers and shows two numbers: DOP (how much the layout multiplies errors) and how far off the position is. The page itself draws and takes input; every number comes from Python.

## Which files it talks to
- `web/startup.js`: `whenPythonReady` waits until the Python engine has loaded, then hands over the function that calls Python. See [startup.js](startup.js.md).
- `web/say.js`: `say` writes the message lines and flashes them. See [say.js](say.js.md).
- `web/format.js`: `formatMetres` writes the "Position off by" number. See [format.js](format.js.md).
- `web/theme.css`: provides the colours, fonts and spacing (the `var(--...)` names, and classes such as `card`, `inset`, `badge`). See [theme.css](theme.css.md).
- Python, through the bridge: [`coords.latlon_to_xyz`](../mechanism/coords.py.md) places the phone, [`coords.satellite_from_sky`](../mechanism/coords.py.md) places each satellite from its direction in the sky, [`geometry.dop`](../mechanism/geometry.py.md) gives the DOP, [`scenario.make_pseudoranges`](../mechanism/scenario.py.md) makes the measured distances with the clock error and noise, [`solver.solve_position`](../mechanism/solver.py.md) works out the position, and [`mapview.to_local`](../mechanism/mapview.py.md) turns that position into east, north and up metres from the true spot. The shapes of these calls are in `docs/interface.md`.
- Whatever loads the page calls `mountGeometryStep` with the element that should hold this section.

## In three lines
1. Build the section: a sky diagram, a slider, two readouts and a Reset button, all switched off until Python is ready.
2. When the slider moves, redraw the sky at once, then ask Python in turn for satellite positions, DOP, measured distances, the position fix and the fix's distance from the truth.
3. Show DOP and the error with a plain sentence and a badge (Good fix, Fix is off, Fix is far off).

New to code? See [how to read code](../how-to-read-code.md).

## The code, line by line

```js
// Rung 2: geometry (design.md 2a). It draws and takes input; every number comes from Python.
// The only arithmetic here: Math.hypot for the position error, the slider-to-angle blend,
// and the sky drawing scale.
```
Three comment lines (a comment starts with `//`; the computer ignores it). They say this is step 2 ("rung 2") of the page, that the page code only draws and takes input, and that the only maths in this file is three small things, explained below. Nothing breaks without them.

```js
import { whenPythonReady } from "./startup.js";
```
An `import` brings a named tool from another file. This one takes `whenPythonReady` from [`startup.js`](startup.js.md). It is used to wait until the Python engine has loaded. Without it, the section could not call Python.

```js
import { say } from "./say.js";
import { formatMetres } from "./format.js";
```
Two more imports: `say` (puts a sentence in a message line and flashes it) and `formatMetres` (writes a number of metres such as `1,235 m`). Without them, the messages and the error number could not be written.

```js
// Every tunable number for this step. All of these are provisional until Icarus confirms them.
export const geometryConfig = {
```
A comment, then the start of an object: a set of labelled values written with curly brackets. `const` makes a named box whose name cannot be pointed at something else later, and `export` lets other files read it (the checks and the page can look at the settings). Without it the settings would have no home.

```js
  receiver: { lat_deg: -6.2, lon_deg: 106.8 }, // placeholder, provisional (Jakarta, as on the first screen)
```
Where the phone is: latitude -6.2 degrees (just south of the equator) and longitude 106.8 degrees (east of the start line), which is Jakarta. The comment says it is a placeholder, not final. Without it the page would not know where to put the phone.

```js
  // Four satellites spread around the sky: one nearly overhead, three low and 120 degrees apart.
  // Elevation stays between 15 and 80 degrees.
  spread: [ // placeholder, provisional
```
Two comments describe the good layout. Then `spread` starts a list (square brackets) of satellites, one object each. Azimuth is the compass direction (0 is north, 90 is east, and so on); elevation is the height above the horizon (0 at the horizon, 90 straight overhead).

```js
    { id: "1", azimuth_deg: 30, elevation_deg: 80 },
    { id: "2", azimuth_deg: 90, elevation_deg: 20 },
    { id: "3", azimuth_deg: 210, elevation_deg: 20 },
    { id: "4", azimuth_deg: 330, elevation_deg: 20 },
  ],
```
The four satellites in the spread layout. Each has a name `id` shown on the diagram, a compass direction and a height. Satellite 1 is high (80 degrees, nearly overhead), and the other three sit low (20 degrees) at 90, 210 and 330 degrees, which is 120 degrees apart. The `],` closes the list. Without these, there would be no layout to start from.

```js
  // The same four satellites bunched into one patch of sky, all within about 10 degrees.
  bunched: [ // placeholder, provisional
```
A comment, then the second layout: the same four satellites squeezed into one patch of sky.

```js
    { id: "1", azimuth_deg: 40, elevation_deg: 44 },
    { id: "2", azimuth_deg: 44, elevation_deg: 48 },
    { id: "3", azimuth_deg: 48, elevation_deg: 52 },
    { id: "4", azimuth_deg: 50, elevation_deg: 46 },
  ],
```
The bunched positions: all four are between 40 and 50 degrees on the compass and between 44 and 52 degrees high. They are listed in the same order as the spread ones, so satellite 1 moves from its spread place to its bunched place. Without them there would be nothing to slide towards.

```js
  clock_error_s: 1e-6, // placeholder, provisional: the phone's clock is 1 microsecond ahead
```
The phone's clock error, in seconds. `1e-6` means 1 times ten to the power minus six, which is 0.000001 s, one microsecond. Python turns it into a distance error (see `scenario.make_pseudoranges`). Without it every distance would be measured with a perfect clock.

```js
  noise_m: 3, // placeholder, provisional: measurement noise, standard deviation in metres
  seed: 1, // placeholder, provisional: the same seed every run, so only the layout changes
```
`noise_m` is how big the random wobble added to each measured distance is (3 metres typical). `seed` is a number that fixes the "random" wobble: with the same seed, Python makes exactly the same wobble every time, so when the slider moves, only the layout changes and the wobble does not. Without the seed the numbers would jitter on every move.

```js
  slider_steps: 100, // placeholder, provisional: 0 = spread, 100 = bunched
  error_limits: { ok_m: 10, warn_m: 100 }, // placeholder, provisional: below ok is "ok", below warn is "warn", else "bad"
};
```
`slider_steps` is how many steps the slider has: position 0 is fully spread and 100 is fully bunched. `error_limits` sets the badge thresholds: under 10 metres off is "ok", under 100 metres is "warn", anything more is "bad". The `};` closes the object. Without these the slider would have no range and the badge no thresholds.

```js
const SVG = "http://www.w3.org/2000/svg";
```
A name for a fixed address. SVG is a way to draw shapes (circles, lines, text) on a web page using elements. Creating SVG pieces from code needs this address so that the browser knows they are SVG and not ordinary page parts. Without it the circles would not show.

```js
const SKY_SIZE = 240; // the sky SVG viewBox is 240 by 240
const SKY_RADIUS = 110; // horizon circle radius in that box
```
Two numbers for the drawing. The sky picture is drawn on an imaginary square 240 units wide and 240 high (the `viewBox`), which the browser then scales to fit the screen. The horizon circle has radius 110 units in that square, leaving a margin for the labels. Without them the drawing code would have no sizes.

```js
const SKY_LABEL = "Sky diagram. The edge is the horizon and the centre is straight overhead. Four dots are the satellites.";
```
The words a screen reader says for the picture. A screen reader is software that reads the page aloud for people who cannot see it. Without it the diagram would be silent.

```js
const LEVEL_WORDS = { ok: "Good fix", warn: "Fix is off", bad: "Fix is far off" };
```
A table from a level name to the words shown on the badge: "Good fix", "Fix is off" or "Fix is far off". Without it the badge would show the raw level names.

```js
// Layout for this section only. Colours, fonts and radii come from theme.css.
const STYLE = `
```
A comment, then the start of a long piece of text in backticks called `STYLE`. It holds CSS: rules about how things look. A CSS rule has the form `selector { property: value; }`. Colours, fonts and the like are not set here; they come from the page's shared [`theme.css`](theme.css.md). A `var(--s-5)` is a CSS variable: a named value defined once in `theme.css` (here `--s-5` is 24 pixels, `--s-4` is 16, `--s-3` is 12, `--s-2` is 8 and `--s-1` is 4). Without the rules the section would look unstyled.

```js
.geo { display: grid; grid-template-columns: minmax(0, 1fr); gap: var(--s-5); }
```
Rule for anything with class `geo` (the whole section). `display: grid` lays children out in a grid. `grid-template-columns: minmax(0, 1fr)` makes one column that takes the full width but may shrink to zero, so long content cannot push the page wider than the screen. `gap: var(--s-5)` leaves 24 pixels between children.

```js
.geo-grid { display: grid; grid-template-columns: minmax(0, 1fr); gap: var(--s-5); }
```
The same for `geo-grid`, the area holding the sky card and the controls: one column on a narrow screen, with a 24 pixel gap.

```js
@media (min-width: 760px) { .geo-grid { grid-template-columns: 1fr 1fr; align-items: start; } }
```
A media query: rules that apply only if the screen meets a condition. Here, if the screen is at least 760 pixels wide, `geo-grid` becomes two equal columns (`1fr 1fr`, the sky on the left and controls on the right), with items lined up at the top (`align-items: start`). On a phone it stays one column. Without it the two cards would never sit side by side.

```js
.geo-stack { display: grid; grid-template-columns: minmax(0, 1fr); gap: var(--s-4); }
```
A vertical stack: one column with a 16 pixel gap, used for the heading and for the controls card.

```js
.geo-sky { width: 100%; max-width: 320px; aspect-ratio: 1; display: block; margin: 0 auto; }
```
The sky picture: as wide as its space but at most 320 pixels (`max-width`), always square (`aspect-ratio: 1`), shown as its own block, and centred (`margin: 0 auto` means no space above and below and equal space left and right). Without `aspect-ratio` the picture could stretch out of shape.

```js
.geo-sky .sky-sat { transition: none; }
```
For a satellite dot inside the sky, switch off the shared fade effect. The comment in the code says the sky follows the slider with no easing, so a dot must jump with the slider rather than glide behind it.

```js
.geo-sky text { fill: var(--text-muted); font: 500 var(--text-xs) var(--font-mono); }
```
Text inside the sky (the satellite numbers) is soft grey (`--text-muted`), weight 500, 12 pixels (`--text-xs`), in the page's fixed-width font (`--font-mono`).

```js
.geo-note { font-size: var(--text-sm); color: var(--text-muted); min-height: 1.5em; }
```
A message line: 14 pixels (`--text-sm`), grey, and at least 1.5 lines tall (`em` is the text's own height) so the layout does not jump when a sentence appears.

```js
.geo-note:empty { min-height: 0; }
```
`:empty` picks a message line with nothing in it; such a line gets no reserved height. Without it, many empty lines would leave gaps.

```js
.geo-note[data-id="msg-slider"]:empty { min-height: 1.5em; }
```
An exception: the message line under the slider keeps its height even when empty, because its sentence changes while the user drags and the controls below must not jump. `[data-id="msg-slider"]` picks the element that has that data-id label.

```js
.geo h3.label { margin-bottom: var(--s-3); }
```
A small heading (`h3` with class `label`) inside the section gets 12 pixels of space below it.

```js
.geo-highlight { border-color: var(--accent); padding: var(--s-4); }
```
The slider box gets an outline in the accent colour (white in dark mode, near black in light mode), to draw the eye, and 16 pixels of space inside.

```js
.geo-readout { padding: var(--s-4); display: grid; grid-template-columns: minmax(0, 1fr); gap: var(--s-2); }
```
The boxes showing DOP and the error: 16 pixels padding inside, one column, 8 pixel gap.

```js
.geo-big { font-size: var(--text-xl); }
```
The big numbers use the largest text size, 32 pixels (`--text-xl`).

```js
.geo .badge[hidden] { display: none; }
```
A badge that has the `hidden` attribute (see the page text below) is not shown at all. The browser already hides such elements, but the badge's own style could override that, so this makes sure.

```js
.geo .hint { font-size: var(--text-sm); font-weight: 500; color: var(--text); }
```
The hint sentence ("Drag this slider...") is 14 pixels, medium weight, in the main text colour, so it stands out from the grey notes.

```js
.geo .slider-head { flex-wrap: wrap; column-gap: var(--s-3); }
```
The row holding the slider's label and its value may wrap onto a second line on narrow screens (`flex-wrap`), with 12 pixels between items.

```js
.geo-closing { max-width: 60ch; }
```
The closing paragraph is at most 60 characters wide (`ch` is the width of a zero), which keeps lines easy to read.

```js
.geo .btn { touch-action: manipulation; }
```
For buttons, tell touch screens not to treat a double tap as a zoom, so taps are quick. Without it some phones wait before acting on a tap.

```js
.geo input[type="range"] { touch-action: pan-y; }
```
For the slider (an `input` of type `range`), touch moves up and down still scroll the page, while sideways moves go to the slider. Without it, dragging the slider on a phone could fight with scrolling.

```js
.geo .btn:disabled, .geo input[type="range"]:disabled { opacity: 0.4; cursor: not-allowed; }
```
A button or slider that is `disabled` (switched off) looks 40 % solid, and the mouse pointer shows a "not allowed" sign. This is how the controls look while Python loads.

```js
.geo .btn:disabled:hover { border-color: var(--line-strong); }
```
A disabled button keeps its normal border colour when the mouse is over it, so it does not light up as if it could be pressed.

```js
`;
```
Closes the `STYLE` text.

```js
const PAGE = `
```
Starts another long text, `PAGE`, which holds HTML: the page's parts. HTML is written in tags such as `<p>...</p>`; each tag makes an element. An attribute is a label inside a tag, such as `class="card"`. A `class` is a name that CSS rules can pick; `data-id` is a private label this file uses to find an element later.

```js
<div class="geo">
  <header class="geo-stack" style="gap: var(--s-2)">
```
A `div` is a plain box. This one, with class `geo`, holds the whole section. Inside it, a `header` groups the section's heading. It uses the stack style with its gap reduced to 8 pixels by an inline `style` attribute.

```js
    <h2>Does it matter where the satellites are?</h2>
    <p class="muted">Same four satellites, same clock error, same noise. Only the layout changes.</p>
  </header>
```
The section's title, `h2` (a second-level heading), and a `p` (paragraph) in grey (`muted`). Then `</header>` closes the header. They tell the reader what is being tested: only the layout changes.

```js
  <div class="geo-grid">
    <section class="card" aria-labelledby="geo-sky-title">
```
The box that holds the two cards, then the first card. A `section` is a part of the page; `card` is a theme style (a panel). `aria-labelledby` is one of the `aria-*` attributes, which add information for screen readers: it says this section is named by the element whose `id` is `geo-sky-title` (the heading just below).

```js
      <h3 class="label" id="geo-sky-title">Sky, seen from below</h3>
```
The card's heading, small capital letters in grey. Its `id` is a unique name so the line above can point at it. Without it the section would have no spoken name.

```js
      <svg class="geo-sky" data-id="sky" viewBox="0 0 ${SKY_SIZE} ${SKY_SIZE}" role="img"
           aria-label="${SKY_LABEL}"></svg>
```
The drawing area, an `svg`. `data-id="sky"` lets this file find it. `viewBox="0 0 ${SKY_SIZE} ${SKY_SIZE}"` has holes `${...}` that are replaced with the numbers from the top, so it reads `0 0 240 240`: the imaginary square described above. `role="img"` tells screen readers to treat the whole drawing as one picture, and `aria-label` gives its spoken description, taken from `SKY_LABEL`. The circles and dots are added later by code. Without the viewBox the drawing would not scale.

```js
      <p class="geo-note" style="margin-top: var(--s-3)">Edge is the horizon, centre is straight overhead.</p>
    </section>
```
A visible caption under the diagram, with 12 pixels of space above it, telling how to read the picture. `</section>` closes the card.

```js
    <section class="card geo-stack" aria-label="Controls and results">
```
The second card, which holds the controls and numbers, laid out as a stack. `aria-label` gives it a spoken name, "Controls and results".

```js
      <p class="geo-note" data-id="status" role="status" aria-live="polite">Loading the maths…</p>
```
A message line that starts with "Loading the maths…". `role="status"` and `aria-live="polite"` mean a screen reader reads out changes to this line, but waits until it has finished what it is saying. [`startup.js`](startup.js.md) changes this line while Python loads. Without the live attributes blind users would not hear progress.

```js
      <p class="hint" data-id="hint" hidden>Drag this slider to push the four satellites into one patch of sky.</p>
```
A hint telling the user what to do. The `hidden` attribute hides it until the code shows it (once Python is ready). Without the hint a new user might not know to drag.

```js
      <div class="slider inset geo-highlight">
        <div class="slider-head">
```
A box for the slider, using theme styles `slider` and `inset` plus the accent outline. Inside, `slider-head` is the row with the label and the value.

```js
          <label for="geo-bunch">Bunch the satellites</label>
```
The slider's text label. `for="geo-bunch"` links it to the element whose `id` is `geo-bunch`, so clicking the text works the slider and screen readers read it as the slider's name.

```js
          <span class="num" data-id="slider-value">0 % bunched</span>
        </div>
```
A `span` (a small piece of inline text) that shows the slider's value in words, starting as "0 % bunched". The class `num` gives it the number font. `</div>` closes the head row.

```js
        <input id="geo-bunch" data-id="slider" type="range" value="0" disabled>
```
The slider itself: an `input` of `type="range"`, with `id` `geo-bunch` (matching the label) and starting `value` 0. `disabled` switches it off until Python is ready. Without `disabled`, a user could drag it before there was anything to answer.

```js
        <p class="geo-note" data-id="msg-slider" role="status" aria-live="polite"></p>
      </div>
```
An empty message line under the slider. It later shows the plain sentence for how things are going ("Spread across the sky..."), and error messages. It is a live area, so screen readers announce it. `</div>` closes the slider box.

```js
      <div class="inset geo-readout">
        <span class="label">DOP</span>
        <span class="num geo-big" data-id="dop">–</span>
```
The DOP box. A small label "DOP", then a big number that starts as an en dash (–), meaning "no number yet".

```js
        <p class="geo-note" style="min-height: 0">DOP (dilution of precision): how much the satellites' layout multiplies measurement errors. Lower is better.</p>
        <p class="geo-note" data-id="msg-dop" role="status" aria-live="polite"></p>
      </div>
```
A permanent explanation of DOP (`min-height: 0` so it reserves no extra height), then an empty live message line for DOP. `</div>` closes the box.

```js
      <div class="inset geo-readout">
        <span class="label">Position off by</span>
        <span class="num geo-big" data-id="error">–</span>
```
The error box. The label says "Position off by" and the big number starts as a dash.

```js
        <div><span class="badge is-ok" data-id="badge" hidden></span></div>
        <p class="geo-note" data-id="msg-error" role="status" aria-live="polite"></p>
      </div>
```
The badge, hidden at first, inside a `div` so it takes its own row. `is-ok` is only a starting class; the code replaces it. Then an empty live message line for the error. Without the badge there would be no quick good/bad signal.

```js
      <div>
        <button class="btn" data-id="reset" type="button" disabled>Reset</button>
```
A box holding the Reset button. `type="button"` says it is a plain button (not one that sends a form). It is `disabled` until Python is ready.

```js
        <p class="geo-note" style="margin-top: var(--s-2)" data-id="msg-reset" role="status" aria-live="polite"></p>
      </div>
    </section>
  </div>
```
A live message line under Reset, with 8 pixels above it. Then the closing tags: the box, the controls card (`</section>`) and the grid (`</div>`).

```js
  <p class="geo-closing">Spread out, the same errors barely move the fix. Bunched, they multiply. But all of this error began with time, so next: how does the phone measure it at all?</p>
</div>`;
```
The closing paragraph, which leads to the next section. Then `</div>` closes the whole section and the backtick ends the `PAGE` text.

```js
export function mountGeometryStep(container) {
```
Starts the main function, `mountGeometryStep`. "Mount" means "put this section onto the page". It is given `container`, the element that will hold the section. Everything else in this file happens inside it. Without it the section never appears.

```js
  if (!document.getElementById("geo-style")) {
```
`document` is the whole page; the DOM is the page's tree of elements that code can read and change. This looks for an element with `id` `geo-style`. The `!` means "not", so the block runs only if none exists yet. It stops the style being added twice if the function is run twice.

```js
    const style = document.createElement("style");
    style.id = "geo-style";
    style.textContent = STYLE;
    document.head.append(style);
  }
```
Makes a new `style` element, gives it the id `geo-style` (so the check above will find it next time), fills it with the CSS from `STYLE`, and adds it to the page's head (the part for settings). From then on the browser applies the rules. Without this the section would be unstyled.

```js
  container.innerHTML = PAGE;
```
Puts the HTML text from `PAGE` inside the container. `innerHTML` turns text into real elements. Without it the section would be empty.

```js
  const $ = (id) => container.querySelector(`[data-id="${id}"]`);
```
Makes a tiny helper named `$` (a short name). Given a name such as `"sky"`, it finds the element inside the container whose `data-id` equals that name. `=>` is a short way of writing a function. Worked example: `$("dop")` finds `<span ... data-id="dop">`. Without it the code below would repeat the long form each time.

```js
  const el = {
    status: $("status"), hint: $("hint"), sky: $("sky"), slider: $("slider"), sliderValue: $("slider-value"),
    msgSlider: $("msg-slider"), dop: $("dop"), msgDop: $("msg-dop"),
    error: $("error"), badge: $("badge"), msgError: $("msg-error"), reset: $("reset"), msgReset: $("msg-reset"),
  };
```
Collects every element the code needs to change into one object called `el`, each under a short name (`el.slider`, `el.dop`, and so on). They are found once, here. Without this the later code would have nothing to work on.

```js
  const { receiver, spread, bunched } = geometryConfig;
```
Pulls three settings out of `geometryConfig` into their own names, so the code can write `spread` instead of `geometryConfig.spread`.

```js
  let callPython = null; // set when the bridge has loaded
  let receiverPoint = null; // true receiver position, from Python
  let running = false;
  let rerun = false;
  let hintDone = false; // once the user has touched the slider, the hint stays hidden
```
Five variables, boxes whose contents can change (`let`, unlike `const`). `callPython` will hold the function for calling Python; `null` means nothing yet. `receiverPoint` will hold the phone's true position in metres from the Earth's centre. `running` is true while a calculation is going; `rerun` is true if the user moved the slider meanwhile (both used below). `hintDone` becomes true after the first touch of the slider.

```js
  el.slider.min = 0;
  el.slider.max = geometryConfig.slider_steps;
  el.slider.step = 1;
  el.slider.value = 0;
```
Sets up the slider: lowest value 0, highest value 100 (`slider_steps`), moves in steps of 1, starts at 0 (fully spread). Without these the slider would use the browser's defaults.

```js
  buildSky();
  showSlider();
```
Calls two functions defined below: `buildSky` draws the rings and the satellite dots once, and `showSlider` writes the slider text and places the dots for the starting position. This makes the sky visible straight away, before Python loads.

```js
  el.slider.addEventListener("input", () => { el.hint.hidden = true; hintDone = true; el.msgReset.textContent = ""; showSlider(); update(); });
```
An event is something that happens on the page. An event listener runs a function when it does. Here, whenever the user moves the slider (the `input` event), five things happen in order: hide the hint; remember that the hint is done; clear the Reset message; redraw the sky and the value text (`showSlider`); and start the calculation (`update`). The sky moves at once, while the numbers wait for Python. Without this line the slider would do nothing.

```js
  el.reset.addEventListener("click", () => {
    el.slider.value = 0;
    showSlider();
    update();
    say(el.msgReset, "Back to the start: satellites spread out.");
  });
```
When Reset is clicked: put the slider back at 0, redraw the sky, ask for new numbers, and say "Back to the start: satellites spread out." in the message line under the button (the line flashes, so the user sees the press worked even if already at the start). Without it, Reset would do nothing.

```js
  start();
```
Calls `start` (below) to begin waiting for Python.

```js
  // ---------- start up ----------
```
A comment dividing the file into parts.

```js
  function start() {
    whenPythonReady(el.status, async (call) => {
```
Defines `start`. It calls `whenPythonReady`, giving it the status line (so the shared start-up code can show "Loading..." words there) and a function to run when Python is ready. That function is `async`: it may wait for slow jobs with `await`, and the page stays usable meanwhile. When it runs, it receives `call`, the function for calling Python.

```js
      callPython = call;
```
Saves that function in the `callPython` box so every other function here can use it.

```js
      try {
        receiverPoint = await callPython("coords.latlon_to_xyz", [receiver.lat_deg, receiver.lon_deg]);
```
`try` means "attempt this; if something goes wrong, jump to `catch`". This asks Python's `latlon_to_xyz` (in [`coords.py`](../mechanism/coords.py.md)) to turn the phone's latitude and longitude into x, y, z metres from the Earth's centre. `await` waits for the answer. Worked example: for latitude -6.2 and longitude 106.8 the answer is about x = -1,830,654, y = 6,063,417 and z = -688,065 metres, a point about 6.37 million metres from the Earth's centre. Without it the code would not know where the phone really is.

```js
        if (receiverPoint.error) throw new Error(receiverPoint.error);
```
Python reports a problem by returning an object with an `error` sentence. If there is one, `throw new Error(...)` raises a problem on purpose, which jumps to `catch` below. Without this check the page would carry on with a broken position.

```js
      } catch (error) {
        console.error(error);
        el.status.textContent = "The calculation engine loaded but could not place the phone, so the controls stay off.";
        return;
      }
```
If anything failed above: write the details to the browser's developer console (`console.error`, for the team to see), tell the user in plain words in the status line that the controls stay off, and `return`, which stops the function here. The slider and button stay switched off. Without it, a failure would leave the user with no explanation.

```js
      el.slider.disabled = false;
      el.reset.disabled = false;
```
Python is ready and the phone is placed, so switch on the slider and the Reset button.

```js
      el.hint.hidden = hintDone;
```
Show the hint (set `hidden` to false), unless the user has already touched the slider while Python was loading (`hintDone` true), in which case it stays hidden.

```js
      update();
```
Run the calculation for the starting slider position, so the numbers appear without the user having to do anything.

```js
    });
  }
```
Closes the ready function, the `whenPythonReady` call and `start`.

```js
  // ---------- the slider and the sky (drawing only) ----------
```
Comment: the next part draws the sky.

```js
  function bunchAmount() { return Number(el.slider.value) / geometryConfig.slider_steps; }
```
Turns the slider position into a number from 0 to 1: 0 is fully spread, 1 is fully bunched. A slider's value is text, so `Number(...)` makes it a number first. Worked example: slider at 25 gives 25 / 100 = 0.25.

```js
  // Blend each satellite's angles between the spread set and the bunched set.
  function currentSky() {
```
A comment, then a function that works out where each satellite is for the current slider position.

```js
    const t = bunchAmount();
```
Stores the 0-to-1 amount in `t`.

```js
    return spread.map((from, i) => ({
```
`spread.map(...)` goes through the list of spread satellites and builds a new list with one result per satellite. In each pass, `from` is the satellite's spread values and `i` is its place in the list (0 for the first), so `bunched[i]` is the same satellite's bunched values.

```js
      id: from.id,
      azimuth_deg: from.azimuth_deg + (bunched[i].azimuth_deg - from.azimuth_deg) * t,
      elevation_deg: from.elevation_deg + (bunched[i].elevation_deg - from.elevation_deg) * t,
    }));
  }
```
Each new satellite keeps its `id`. Its angles are a blend: start at the spread value, add the whole gap to the bunched value multiplied by `t`. At `t = 0` the satellite is at its spread place, at `t = 1` at its bunched place, and halfway in between at `t = 0.5`. Worked example for satellite 1 at `t = 0.25` (slider 25): azimuth 30 + (40 - 30) * 0.25 = 30 + 2.5 = 32.5 degrees; elevation 80 + (44 - 80) * 0.25 = 80 - 9 = 71 degrees. At `t = 1` the elevation is 80 + (-36) = 44, the bunched value. The `}));` closes the object, the function in `map` and the call; the last `}` closes `currentSky`.

```js
  function showSlider() {
```
A function that updates everything that depends on the slider position but not on Python.

```js
    el.sliderValue.textContent = `${Math.round(bunchAmount() * 100)}\u00a0% bunched`;
```
Writes the value text, for example "25 % bunched". `bunchAmount() * 100` makes a percentage and `Math.round` rounds it to a whole number (0.37 gives 37). `\u00a0` is a special code for a space that cannot be split from the `%` across lines. Without it the user would not see how far the slider is.

```js
    el.slider.setAttribute("aria-valuetext", el.sliderValue.textContent);
```
Sets the slider's `aria-valuetext` attribute to that same sentence. A screen reader reads this instead of the bare number, so it says "25 % bunched" rather than just "25".

```js
    el.sky.setAttribute("aria-label", `${SKY_LABEL} ${el.sliderValue.textContent}.`);
```
Updates the sky picture's spoken description: the standard sentence followed by the percentage, such as "...Four dots are the satellites. 25 % bunched." Without it the spoken description would not change as the slider moves.

```js
    drawSky(currentSky()); // instant, no easing: the sky follows the slider every frame
  }
```
Works out the current satellite angles (`currentSky`) and moves the dots there (`drawSky`) straight away, with no gliding, so the picture keeps up with the slider. The `}` ends the function.

```js
  function buildSky() {
    const mid = SKY_SIZE / 2;
```
Starts the function that builds the fixed parts of the sky. `mid` is the middle of the square: 240 / 2 = 120.

```js
    for (const fraction of [1, 2 / 3, 1 / 3]) { // horizon, then rings at 30 and 60 degrees up
```
A loop that runs its lines once for each value in the list: 1, two thirds and one third. These make three rings: the horizon, and rings for 30 degrees and 60 degrees up. A satellite 30 degrees up sits (90 - 30) / 90 = 2/3 of the way out from the middle, and one 60 degrees up sits (90 - 60) / 90 = 1/3 of the way out. Without the loop there would be no rings.

```js
      const ring = document.createElementNS(SVG, "circle");
```
Makes a new `circle` element. `createElementNS` is the version for SVG, which needs the address stored in `SVG`.

```js
      ring.setAttribute("class", "sky-ring");
```
Gives it the class `sky-ring`, which the theme styles as an unfilled ring with a faint line.

```js
      ring.setAttribute("cx", mid); ring.setAttribute("cy", mid); ring.setAttribute("r", SKY_RADIUS * fraction);
```
Sets the circle's centre (`cx` across, `cy` down), both at 120, and its radius `r`. Worked example: 110 * 1 = 110 for the horizon, 110 * 2/3 = 73.3 for the next ring, 110 * 1/3 = 36.7 for the inner one.

```js
      el.sky.append(ring);
    }
```
Adds the circle to the sky drawing, then the loop ends and repeats for the next fraction.

```js
    for (const sat of spread) {
```
Another loop, once per satellite in the spread list. (It uses `spread` only to know the ids; the positions come later.)

```js
      const group = document.createElementNS(SVG, "g");
```
Makes a `g`, an SVG group: a bundle of shapes that can be moved as one.

```js
      group.dataset.id = sat.id;
```
Gives the group a `data-id` label equal to the satellite's id ("1" to "4"), so `drawSky` can find it. `dataset` is the code's way to set `data-` attributes.

```js
      group.innerHTML = '<circle class="sky-sat" r="7"></circle><text text-anchor="middle" dy="-12"></text>';
```
Fills the group with two shapes: a circle of radius 7 (the dot, class `sky-sat`) and a `text` for its number. `text-anchor="middle"` centres the text on the dot, and `dy="-12"` lifts it 12 units up so it sits above the dot, not on it.

```js
      group.querySelector("text").textContent = sat.id;
```
Finds that text inside the group and sets it to the satellite's id, so the dot is labelled 1, 2, 3 or 4.

```js
      el.sky.append(group);
    }
  }
```
Adds the group to the drawing; the loop ends, and `buildSky` ends. At this point the dots exist but sit at the top left corner, until `drawSky` moves them.

```js
  // Overhead (90 degrees) is the middle, the horizon (0 degrees) is the edge. Azimuth 0 is north, at the top.
  function drawSky(sats) {
```
A comment that gives the drawing rule, then the function that places the dots. It is given a list of satellites with their angles.

```js
    const mid = SKY_SIZE / 2;
```
The middle again: 120.

```js
    for (const sat of sats) {
```
Loop over each satellite.

```js
      const away = (90 - sat.elevation_deg) / 90 * SKY_RADIUS;
```
How far the dot is from the middle, in drawing units. Straight overhead (90 degrees up) is 0 away; the horizon (0 degrees) is a full 110 away. Worked example: elevation 20 gives (90 - 20) / 90 * 110 = 70 / 90 * 110 = 85.6. Elevation 80 gives 10 / 90 * 110 = 12.2.

```js
      const angle = sat.azimuth_deg * Math.PI / 180;
```
Turns the compass direction from degrees into radians, the unit that `Math.sin` and `Math.cos` need (180 degrees is `Math.PI`, about 3.1416, radians). Worked example: 90 degrees * 3.1416 / 180 = 1.5708.

```js
      const group = el.sky.querySelector(`g[data-id="${sat.id}"]`);
```
Finds the group for this satellite by its id (for example `g[data-id="2"]`).

```js
      group.setAttribute("transform", `translate(${mid + away * Math.sin(angle)} ${mid - away * Math.cos(angle)})`);
    }
  }
```
Moves the group (`translate` means shift by this much across and down). Across: the middle plus `away` times the sine of the angle (the east part of the direction). Down: the middle minus `away` times the cosine (the north part; the minus is because on a screen, down is bigger, and north is at the top). Worked example, satellite 2 spread (azimuth 90, elevation 20): away is 85.6, angle 1.5708, sine 1, cosine about 0. So across = 120 + 85.6 * 1 = 205.6, down = 120 - 85.6 * 0 = 120: due east, near the right edge. Satellite 1 spread (azimuth 30, elevation 80): away 12.2, sine of 30 degrees 0.5, cosine 0.866. Across = 120 + 6.1 = 126.1, down = 120 - 10.6 = 109.4: just up and right of the middle. Then the loop and the function end.

```js
  // ---------- one run: ask Python, then draw ----------
```
Comment: the next part asks Python and shows the numbers.

```js
  // Python calls are async. If one is running, remember that a newer run is wanted and do it once after.
  async function update() {
```
A comment, then `update`, an `async` function (it waits for slow jobs). Moving the slider fires many events a second, and each Python run takes time. This function stops runs from piling up.

```js
    if (!callPython) return;
```
If Python is not ready yet (`callPython` is still `null`), do nothing. Without it, moving the slider early would crash.

```js
    if (running) { rerun = true; return; }
```
If a run is already going, do not start another. Instead, make a note (`rerun = true`) that a newer run is wanted, and stop. Several moves while one run is going collapse into one extra run.

```js
    running = true;
```
Note that a run is now going.

```js
    try {
      do {
        rerun = false;
        await runOnce();
      } while (rerun);
```
`do ... while` repeats its lines as long as the condition after `while` is true, and always runs them at least once. Each pass first clears the note (`rerun = false`), then does one calculation (`await runOnce()`, waiting for it to finish). If the user moved the slider during that calculation, `rerun` was set to true, so the loop runs again with the newest slider position. The sky has already moved without waiting.

```js
    } finally {
      running = false;
    }
  }
```
`finally` runs whatever happens, even if something fails: it clears `running`, so later updates can start. Without it, one failure would block all future runs.

```js
  async function runOnce() {
```
Defines `runOnce`, which makes one full trip: ask Python for everything, then show it.

```js
    el.msgDop.textContent = el.msgError.textContent = "";
```
Empties the DOP message line and the error message line. The two `=` signs in a row mean "set both to the empty text". (The code never writes anything into these two lines, so they stay empty.)

```js
    const position = Number(el.slider.value); // the slider position this run is about
    const sky = currentSky(); // the layout this run is about, even if the slider moves meanwhile
```
Takes a snapshot of the slider position and the satellite layout when the run starts. Because the run waits for Python several times, the user may move the slider meanwhile; the snapshot makes sure all the numbers of one run belong to the same layout.

```js
    try {
      const sats = [];
```
`try` starts a guarded part. `sats` is an empty list that will collect each satellite's real position.

```js
      for (const sat of sky) {
        const point = await callPython("coords.satellite_from_sky", [receiver.lat_deg, receiver.lon_deg, sat.azimuth_deg, sat.elevation_deg]);
```
For each satellite, ask Python's `satellite_from_sky` (in [`coords.py`](../mechanism/coords.py.md)) for its x, y, z position in metres, given the phone's latitude and longitude and the satellite's compass direction and elevation. `await` waits for each answer.

```js
        if (failed(point)) return;
```
If Python answered with an error, `failed` (below) shows the message and says so; `return` then ends this run. Without it, the error would feed into the next calls.

```js
        sats.push({ id: sat.id, ...point });
      }
```
Adds an entry to the list: the satellite's `id`, plus all of what Python returned (`...point` spreads the x, y, z values into the new object). The loop ends.

```js
      const dop = await callPython("geometry.dop", [receiverPoint, sats]);
      if (failed(dop)) return;
```
Asks Python's `dop` (in [`geometry.py`](../mechanism/geometry.py.md)) for the DOP numbers, given the phone's position and the satellites, then stops if there was an error.

```js
      const ranges = await callPython("scenario.make_pseudoranges", [receiverPoint, sats, geometryConfig.clock_error_s, geometryConfig.noise_m, geometryConfig.seed]);
      if (failed(ranges)) return;
```
Asks Python's `make_pseudoranges` (in [`scenario.py`](../mechanism/scenario.py.md)) for the measured distances: the true distance to each satellite, plus the clock error and the noise. It is given the receiver, the satellites, the clock error (1e-6 s), the noise (3 m) and the seed (1). Worked example: 1e-6 s * 299,792,458 m/s is about 300 m of extra distance on every measurement. Then stop if it failed.

```js
      // Clock solved, as a real phone does: the clock error is removed, and what remains is the
      // noise multiplied by the layout. That is exactly what DOP describes.
      const solution = await callPython("solver.solve_position", [sats, ranges, true]);
      if (failed(solution)) return;
```
A comment, then the key call: Python's `solve_position` (in [`solver.py`](../mechanism/solver.py.md)) works out where the phone is from the satellites and the measured distances. The final `true` means "also solve for the clock error", as a real phone does. What is left over is the noise multiplied by the layout, which DOP describes. Then stop if it failed.

```js
      const point = { x_m: solution.x_m, y_m: solution.y_m, z_m: solution.z_m };
```
Picks out just the three position numbers of the answer into a small object. (This `point` is a new box, separate from the satellite `point` inside the loop above.)

```js
      const local = await callPython("mapview.to_local", [receiver.lat_deg, receiver.lon_deg, point]);
      if (failed(local)) return;
```
Asks Python's `to_local` (in [`mapview.py`](../mechanism/mapview.py.md)) to say where that position is compared with the true phone spot, as `east_m`, `north_m` and `up_m` metres. Then stop if it failed.

```js
      const errorM = Math.hypot(local.east_m, local.north_m, local.up_m);
```
The straight-line distance between the fix and the truth. `Math.hypot` takes the square root of the sum of the squares (the three-way Pythagoras rule). Worked example: east 3, north 4, up 12 gives the square root of 9 + 16 + 144 = the square root of 169 = 13 metres off.

```js
      requestAnimationFrame(() => showResult(dop.pdop, errorM, position));
```
`requestAnimationFrame` asks the browser to run a function just before it draws its next picture, so the numbers change at a smooth moment. The function shows the result using the position part of DOP (`dop.pdop`), the error in metres, and the slider position snapshot from the start of this run.

```js
    } catch (error) {
      console.error(error);
      say(el.msgSlider, "Something went wrong in the calculation, so the numbers below may be out of date.");
    }
  }
```
If anything unexpected goes wrong in the guarded part: log the details to the developer console, and tell the user in the slider message line, with a flash, that the numbers may be out of date. Then the function ends.

```js
  function failed(result) {
```
A small helper that checks a Python answer for an error.

```js
    if (!result || !result.error) return false;
```
If there is no answer at all (`!result`) or the answer has no `error` entry, nothing is wrong: hand back `false`. A `||` means "or".

```js
    say(el.msgSlider, result.error); // Python's own plain sentence
    return true;
  }
```
Otherwise show Python's own plain-words sentence in the slider message line (with a flash) and hand back `true`, so the caller stops. Without this, error sentences from Python would never reach the user.

```js
  // ---------- show numbers ----------
```
Comment: the next part shows the numbers.

```js
  function errorLevel(errorM) {
    if (errorM < geometryConfig.error_limits.ok_m) return "ok";
    if (errorM < geometryConfig.error_limits.warn_m) return "warn";
    return "bad";
  }
```
Sorts the error into one of three levels, using the limits in the settings. Under 10 metres is `"ok"`; otherwise under 100 metres is `"warn"`; otherwise `"bad"`. Each `return` stops the function, so only the first true check counts. Worked examples: 5 m is ok, 40 m is warn, 250 m is bad.

```js
  function stateSentence(level, position) {
    if (position === 0) return "Spread across the sky: small measurement errors stay small.";
```
Chooses the sentence for under the slider. At position 0 (fully spread), `===` (is exactly equal) is true and the first sentence is used.

```js
    if (level === "ok") return "Still a good fix, but DOP is climbing. Keep dragging.";
    if (level === "warn") return "The same small measurement errors now move the fix by tens of metres.";
    return "Bunched together: the same small measurement errors now throw the fix far off.";
  }
```
If the slider has moved and the level is good, use "Still a good fix, but DOP is climbing. Keep dragging."; if it is `warn`, "The same small measurement errors now move the fix by tens of metres."; otherwise the last sentence about the fix being thrown far off. The `}` ends the function.

```js
  function showResult(pdop, errorM, position) {
    const level = errorLevel(errorM);
```
Starts the function that shows a finished run. It is given the DOP, the error in metres and the slider position. It sorts the error into a level.

```js
    const dopText = new Intl.NumberFormat("en", { maximumFractionDigits: 1 }).format(pdop);
```
Writes the DOP with at most one decimal place using the browser's number writer (as in [format.js](format.js.md)). Worked example: 3.456 becomes `3.5`; 12 stays `12`.

```js
    const sentence = stateSentence(level, position);
```
Chooses the sentence to show.

```js
    if (el.msgSlider.textContent !== sentence) say(el.msgSlider, sentence); // only when the words change
```
`!==` means "is not exactly equal". The sentence is written (with a flash) only if it differs from what is already there. Without the check, the line would flash on every little slider move and distract the user. It also keeps screen readers from repeating the same sentence.

```js
    const percent = Math.round(position / geometryConfig.slider_steps * 100);
```
Turns the slider position into a whole percentage. Worked example: 25 / 100 * 100 = 25.

```js
    el.sky.setAttribute("aria-label", `Sky diagram. Satellites ${percent} % bunched. DOP ${dopText}.`);
```
Updates the sky picture's spoken description to include the result, for example "Sky diagram. Satellites 25 % bunched. DOP 3.5." Without it, screen reader users would not hear the DOP.

```js
    el.dop.textContent = dopText;
    el.error.textContent = formatMetres(errorM);
```
Shows the DOP text in the DOP box, and the error in the error box, written by `formatMetres` (for 13 it gives `13 m`, for 1234.6 it gives `1,235 m`).

```js
    el.badge.hidden = false;
```
Makes the badge visible (it started hidden).

```js
    el.badge.className = `badge is-${level}`;
```
Sets the badge's classes to `badge` plus `is-ok`, `is-warn` or `is-bad`, which the theme colours. Without it, the badge would not change colour.

```js
    el.badge.textContent = LEVEL_WORDS[level];
  }
}
```
Writes the badge words from the table at the top: `LEVEL_WORDS["warn"]` is "Fix is off". The first `}` ends `showResult`; the last ends `mountGeometryStep`, and the file.
