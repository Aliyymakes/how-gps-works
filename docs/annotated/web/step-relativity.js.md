# step-relativity.js, line by line

Source: `web/step-relativity.js`

## What this file is for
This builds the "Do the satellites' own clocks matter?" section of the page (part 4 of 4). One slider (hours since the satellite clocks were last corrected, 0 to 24, starting at 24) drives two cards. The first card, "Satellite clocks run fast", shows a ground clock and a satellite clock side by side with the gap between them and the extra distance error that gap causes. The second card, "So why doesn't your position drift?", shows two small ground maps: one where the phone trusts its own clock and one where it solves for its clock. It calculates nothing itself. Every number comes from Python; the only things decided here are which colour badge to show and which clock digits to light up. The fixed numbers 45, 7 and 38 millionths of a second a day (from `docs/facts.md` rows 25 to 27) are only words on the page.

## Which files it talks to
- `web/config.js` ([config.js](config.js.md)): gives the phone's place, the four satellite directions, the colour limits (`errorLimits`), the slider settings (`relativitySlider`), the map size (`relativityMapHalfWidthM`), the number of points per line (`lineSamples`) and the phone's own clock error (`relativityPhoneClockErrorS`).
- `web/startup.js`: [`whenPythonReady`](startup.js.md) waits for Python to download and then runs this file's `start` function.
- `web/say.js` ([say.js](say.js.md)): `say` writes a message into a line on the page and gives it a brief fade, so pressing something always gives a visible answer.
- `web/format.js` ([format.js](format.js.md)): `formatMetres` turns a number of metres into text such as `11,392 m`, `formatRoughDistance` into rough text such as `11 km`, and `formatClockDigits` into a clock reading such as `24:00:00.000 038`.
- `web/theme.css` ([theme.css](theme.css.md)): all colours, fonts and the classes `card`, `inset`, `badge`, `btn`, `slider`, `label`, `num` and `muted` come from here.
- `index.html` ([index.html](../index.html.md)): imports this file and calls `mountRelativityStep` with the empty box `step-relativity`.
- Python, through the bridge (see [`startup.js`](startup.js.md)):
  - `coords.latlon_to_xyz` and `coords.satellite_from_sky`, in [`coords.py`](../mechanism/coords.py.md): place the phone and the satellites in space.
  - `relativity.drift_over_time`, in [`relativity.py`](../mechanism/relativity.py.md): adds the shared drift, solves twice and returns the clock gap and the errors. It uses `scenario.make_pseudoranges` and `solver.solve_position` (see [`solver.py`](../mechanism/solver.py.md)).
  - `scenario.make_pseudoranges` ([`scenario.py`](../mechanism/scenario.py.md)) and `solver.solve_position`, called again here for the two maps.
  - `mapview.to_local` and `mapview.distance_lines` ([`mapview.py`](../mechanism/mapview.py.md)): turn a position into east and north metres and make the distance lines for a map. The exact shapes are in `docs/interface.md`.

## In three lines
1. Build the section's text, the two cards and the controls, and wait until Python is ready.
2. Once ready, place the phone and the satellites (Python) and switch on the slider and the Reset button.
3. Each time the slider moves, ask Python for the clock gap and the errors at that many hours. Show the two clocks and the gap in the first card, and solve the position twice (clock trusted, clock solved) to draw the two maps in the second card, each with a "Good fix", "Fix is off" or "Fix is far off" badge.

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
// Rung 4: relativity (design.md 2a, 2b). One slider drives two cards: (a) the satellite clocks pull ahead,
// (b) the position does not drift. Every number comes from Python (relativity.drift_over_time and the first
// screen's own chain of calls); the only fixed numbers are the 45, 7 and 38 µs a day from docs/facts.md rows 25 to 27.
```
Three comment lines. "Rung 4" is this section's place on the page's ladder of steps. `design.md` is the project's spec. They say the section has one slider that drives two cards: first the satellite clocks pull ahead, then the position does not drift. Every number comes from Python (`relativity.drift_over_time`, plus the same chain of calls the first screen uses). The only fixed numbers in the file are 45, 7 and 38 millionths of a second a day, from `docs/facts.md` rows 25 to 27 (the NIST and NASA figures). They appear in the page's words only; no calculation uses them.

```js
import * as config from "./config.js";
```
Brings in everything exported by [`config.js`](config.js.md) under the name `config`, so the code can write `config.receiver`. These are the page's tunable settings. Without this line every `config.` below would be unknown.

```js
import { whenPythonReady } from "./startup.js";
import { say } from "./say.js";
import { formatMetres, formatRoughDistance, formatClockDigits } from "./format.js";
```
Three imports, each taking named functions from another file. `whenPythonReady` waits for Python. `say` writes a message with a short fade. From [`format.js`](format.js.md) come three text makers: `formatMetres` (`11392.1` becomes `11,392 m`), `formatRoughDistance` (a rough distance such as `11 km`, for numbers that must not look exact) and `formatClockDigits` (writes a clock reading such as `24:00:00.000 038`). Without them those names would be unknown and the file would fail to load.

```js
const SVG = "http://www.w3.org/2000/svg";
const MAP_SIZE = 200; // each small map's viewBox is 200 by 200
```
Two constants. `SVG` is the web address that marks a drawing element as an SVG one (needed when code makes drawing parts, see `drawLines`). `MAP_SIZE` is 200: each small map is drawn on an imaginary square 200 units wide and high, which the browser scales to fit the screen.

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
.rel-readout { padding: var(--s-4); display: grid; gap: var(--s-2); grid-template-columns: minmax(0, 1fr); }
.rel-sketch { width: 100%; max-width: 360px; height: auto; display: block; }
```
- `.rel-card`: each of the two cards is one column with gaps.
- `.rel-highlight`: the slider's box gets the accent colour for its border and padding (space inside the edge), so it stands out as the thing to touch.
- `.rel-readout`: each result box has padding and stacks its label and number with a small gap (`--s-2`).
- `.rel-sketch`: the little clock sketch fills its box up to 360 pixels wide, keeps its shape (`height: auto`) and is a block of its own (`display: block`).

```js
.rel-clocks { display: grid; grid-template-columns: minmax(0, 1fr); gap: var(--s-3); }
.rel-digits { font-size: var(--text-lg); color: var(--text-muted); overflow-wrap: anywhere; }
.rel-digits .diff { color: var(--text); }
```
- `.rel-clocks`: the two clock readouts sit in one column with a gap.
- `.rel-digits`: the clock digits use the large text size (`--text-lg`) in the soft colour, and may break onto a new line on a very narrow screen (`overflow-wrap: anywhere`).
- `.rel-digits .diff`: a digit marked `diff` (one that differs from the other clock) uses the full text colour, so the differing digits stand out. (A space between two class names means "inside".)

```js
.rel-pair { display: grid; grid-template-columns: minmax(0, 1fr); gap: var(--s-4); }
@media (min-width: 560px) { .rel-pair { grid-template-columns: 1fr 1fr; } }
```
`.rel-pair` holds two result boxes. On a narrow screen they stack in one column. The `@media (min-width: 560px)` line is a media query: only when the screen is at least 560 pixels wide, the pair gets two equal columns (`1fr 1fr`), putting the boxes side by side. Without the media query the boxes would be squeezed side by side even on a phone.

```js
.rel-why { margin: 0; padding: 0; list-style: none; display: grid; gap: var(--s-2); font-size: var(--text-sm); }
```
`.rel-why` styles the short list of reasons (45, 7 and 38 millionths of a second a day). It removes the default margin, padding and bullet dots (`list-style: none`), stacks the items with a small gap and uses small text.

```js
.rel-maps { max-width: 640px; display: grid; grid-template-columns: minmax(0, 1fr); gap: var(--s-4); }
@media (min-width: 340px) { .rel-maps { grid-template-columns: minmax(0, 1fr) minmax(0, 1fr); } }
```
`.rel-maps` holds the two small maps. It is at most 640 pixels wide and one column by default. The media query switches to two equal columns from 340 pixels wide, so on most phones the two maps still sit side by side for comparison.

```js
.rel-map { display: grid; grid-template-columns: minmax(0, 1fr); gap: var(--s-2); align-content: start; }
.rel-map-title { font-size: var(--text-sm); font-weight: 600; margin: 0; }
```
- `.rel-map`: one map and the words under it stack in a column, packed at the top (`align-content: start`).
- `.rel-map-title`: the title above each map is small and semi-bold (`font-weight: 600`), with no outer margin.

```js
.rel-off { font-size: var(--text-lg); overflow-wrap: anywhere; }
.rel-map .rel-off { font-size: var(--text-md); white-space: nowrap; }
```
- `.rel-off`: the big "off by" or "ahead by" number uses the large text size and may break onto a new line.
- `.rel-map .rel-off`: inside a map the number is one size smaller (`--text-md`) and must stay on one line (`white-space: nowrap`), because the maps are narrow.

```js
.rel .hint { font-size: var(--text-sm); font-weight: 500; color: var(--text); }
.rel .slider-head { flex-wrap: nowrap; column-gap: var(--s-3); }
.rel .slider-head .num { white-space: nowrap; }
```
- `.rel .hint`: the "Drag this back to 0..." line is a little smaller, medium weight and in the full text colour so it is easy to read.
- `.rel .slider-head`: the line above the slider (label and value) does not wrap (`nowrap`) and has a gap between columns, so the value stays on the same row as the label.
- `.rel .slider-head .num`: the value text such as "24 h" never splits across two lines.

```js
.rel-control { position: sticky; top: var(--s-2); z-index: 5; background: var(--surface); }
.rel-control, .rel input, .rel button { scroll-margin-top: 140px; }
```
- `.rel-control`: the card with the slider is **sticky**. `position: sticky; top: var(--s-2)` keeps it near the top of the screen while the reader scrolls down through the two cards, so the slider is always in reach. `z-index: 5` keeps it above the content that scrolls under it, and the solid `background` stops that content showing through.
- The next rule gives the control, any input and any button a `scroll-margin-top` of 140 pixels. When the browser scrolls one of them into view (for example when it takes keyboard focus), it leaves that much room at the top so the sticky card does not cover it.

```js
@media (max-width: 559px) { .rel-control { padding: var(--s-3); gap: var(--s-2); } .rel-control .rel-highlight { padding: var(--s-3); } }
@media (max-width: 419px) { .rel-map .rel-off { font-size: var(--text-sm); } }
```
Two media queries for small screens.
- Under 560 pixels wide the sticky card (and its highlighted slider box) gets less padding, so it takes less of a small screen.
- Under 420 pixels wide the number inside a map shrinks to the small text size so it still fits.

```js
.rel [data-id="sentence"] { color: var(--text); font-size: var(--text-md); }
.rel .badge[hidden] { display: none; }
```
- `.rel [data-id="sentence"]`: the summary sentence (picked out by its `data-id`) uses the full text colour and the medium size, so it reads as the conclusion.
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
An **object**: a set of labelled values. It matches each level name to the words on a badge: "Good fix", "Fix is off" and "Fix is far off". Without it the badges would have no words.

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
// One small ground map, like the first screen's: frame, cross at the true place, distance lines, dot.
function mapMarkup(name, title, label) {
```
A comment, then a function that builds the HTML for one small ground map. It is like the map on the first screen: a frame, a cross where the phone really is, one line per satellite distance, and a dot where the phone thinks it is. It takes three words: `name` (`"trusted"` or `"solved"`, used to make each map's labels unique), `title` (the words above the map) and `label` (the spoken description for screen readers). It returns text, so the same pieces are built twice with different words.

```js
  return `
      <div class="rel-map">
        <p class="rel-map-title">${title}</p>
```
`return` followed by a backtick starts the returned text. The `${...}` holes are filled in with the function's values. This is a box with the class `rel-map` and the map's title, a paragraph whose words are `${title}`.

```js
        <svg class="map" data-id="map-${name}" viewBox="0 0 ${MAP_SIZE} ${MAP_SIZE}" role="img" aria-label="${label}">
```
The drawing area, an `svg`. Its `data-id` is `map-trusted` or `map-solved`, so each can be found later. `viewBox` says the imaginary drawing square is `0 0 200 200` (from `MAP_SIZE`). `role="img"` tells screen readers to treat the whole drawing as one picture and `aria-label` gives its spoken description.

```js
          <rect class="map-frame" x="0.5" y="0.5" width="${MAP_SIZE - 1}" height="${MAP_SIZE - 1}"/>
          <path class="map-true" d="M92 100h16M100 92v16"/>
```
- The frame: a `rect` (rectangle) the size of the square, minus one unit so its edge line is not cut off. `${MAP_SIZE - 1}` is worked out when the text is built, giving 199.
- The cross: a `path` (a drawn line) that moves to point 92,100, draws 16 units right (`h16`), moves to 100,92 and draws 16 units down (`v16`). It marks the centre of the map, the phone's true place.

```js
          <g data-id="lines-${name}"></g>
          <g data-id="dot-${name}" class="is-ok" style="display: none"><circle class="map-dot" r="6"/></g>
```
- `<g data-id="lines-${name}">` is an empty group where the code adds one line per satellite later (a **group**, `g`, collects drawing parts).
- A second group holds the dot, the place the phone thinks it is. It starts with the class `is-ok` (a colour) and `style="display: none"`, so it is hidden until a result exists. Inside it a `circle` of radius 6 gets its centre set later.

```js
        </svg>
```
Closes the drawing.

```js
        <span class="num rel-off" data-id="${name}">–</span>
        <div><span class="badge is-ok" data-id="${name}-badge" hidden></span></div>
```
- A `span` with the classes `num` and `rel-off` starts as a dash. Later it shows how far off the phone thinks it is, for example "about 20 km off". Its `data-id` is just `trusted` or `solved`.
- A badge for the level, wrapped in a `div` so it does not stretch across the box. It starts `hidden`; its `data-id` is `trusted-badge` or `solved-badge`.

```js
        <p class="rel-note" data-id="caption-${name}" role="status" aria-live="polite"></p>
      </div>`;
}
```
A message line under the map, a polite status line for screen readers (`role="status"`, `aria-live="polite"`). The code uses it to say when the map hides something. Then the `</div>` closes the map's box, and the closing backtick ends the text that `mapMarkup` returns. The last `}` closes the function.

```js
// Draft sentences: every visible sentence below is for Icarus to approve.
const PAGE = `
```
A comment saying that the visible sentences are drafts waiting for Icarus (the project lead) to approve. Then `PAGE` begins: a block of HTML (the language that describes the tags on a page) held as text.

```js
<div class="rel">
  <header class="rel-stack" style="display: grid; gap: var(--s-2)">
    <p class="label part-label">Part 4 of 4</p>
    <h2 id="rel-title">Do the satellites' own clocks matter?</h2>
    <p class="rel-note" data-id="status" role="status" aria-live="polite">Loading the maths…</p>
  </header>
```
- `<div class="rel">` opens a plain box with the class `rel`, which the `.rel` style rule above targets.
- `<header ...>` opens the section's top part. Its `style` attribute puts a grid with a small gap right on the tag.
- A small label, "Part 4 of 4", with the classes `label` and `part-label` (the theme's small-capitals look), tells the reader where they are on the page.
- `<h2 id="rel-title">` is a second-level heading: "Do the satellites' own clocks matter?".
- The status line. `data-id="status"` is a private label the code uses to find this tag later (see `$` below). `role="status"` and `aria-live="polite"` tell screen readers that this text changes and should be read out when the reader is idle, without cutting in. It starts with "Loading the maths…" and is later overwritten by startup progress.
- `</header>` closes the heading block.

```js
  <section class="card rel-card rel-control" aria-label="Control">
    <p class="hint" data-id="hint" hidden>Drag this back to 0 and the two clocks agree. Drag it forward and watch the gap grow.</p>
```
The control card, which is sticky (see `.rel-control`). `aria-label="Control"` gives it a spoken name. Inside it is the hint: "Drag this back to 0 and the two clocks agree. Drag it forward and watch the gap grow." The `hidden` attribute hides it until the code shows it, once the slider is live.

```js
    <div class="slider inset rel-highlight">
      <div class="slider-head">
        <label for="rel-hours">Time since the satellite clocks were last corrected</label>
        <span class="num" data-id="slider-value">24 h</span>
      </div>
```
The slider's box (classes `slider`, `inset` and `rel-highlight`) and its top line.
- The `<label>` shows "Time since the satellite clocks were last corrected". Its `for="rel-hours"` ties it to the slider with that `id`, so clicking the words picks the slider and screen readers read them as its name.
- The `<span>` (an inline piece of text) shows the current value. It starts as "24 h", the same as the slider's starting position, so the page never shows a wrong number first. The class `num` styles it as a number.

```js
      <input id="rel-hours" data-id="slider" type="range" disabled>
    </div>
  </section>
```
The slider itself: an `<input>` of `type="range"`. Its `id` matches the label. It starts `disabled` (switched off) until Python is ready, because moving it before then could not do anything. Its minimum, maximum, step and starting value are set later from [`config.js`](config.js.md). The `</div>` closes the slider's box and `</section>` closes the control card.

```js
  <section class="card rel-card" aria-labelledby="rel-a-title">
    <div style="display: grid; gap: var(--s-2)">
      <span class="label">First</span>
      <h3 id="rel-a-title">Satellite clocks run fast.</h3>
    </div>
```
The first of the two cards, **satellite clocks run fast**. `aria-labelledby="rel-a-title"` says the card is named by the heading with that `id`. At the top of the card, in a small box with a gap, are a small label "First" and the heading "Satellite clocks run fast." (an `h3`, a third-level heading).

```js
    <p class="looking"><b>What you're looking at:</b> two clocks that started together. One stayed on the ground. One is on a GPS satellite.</p>
```
A plain-words line in the page's `looking` style, with "What you're looking at:" in bold (`<b>`): two clocks that started together, one kept on the ground and one on a GPS satellite. It tells the reader what the next picture and numbers are before they see them.

```js
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
```
A small hand-drawn sketch (an `svg`, class `figure`, with a spoken description in `aria-label`). It is drawn on an imaginary 320 by 130 square and is only a picture; no numbers come from it. Each tag is one drawing part:
- The first `path` (the soft `dim` colour) is a gentle curve across the bottom: the ground.
- A `circle` with a short `path` for its hands and the `text` "on the ground" draw the **ground clock**.
- The `rect` shapes (a small square with a flat panel on each side, in the soft colour) and the thin line from it draw the **satellite**, with its labelling `text` "on a satellite".
- A second `circle` with hands is the **satellite clock**. Its hands are drawn at a different angle from the ground clock's. An arrow `path` points to the `text` "ahead".

```js
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
```
Two readout boxes, one after the other, for the two clocks.
- The first has the label "Clock on the ground" and a `span` (`data-id="digits-ground"`) that starts as a dash. Later the code fills it with the clock reading as separate digits.
- The second, "Clock on the satellite", is the same with `data-id="digits-satellite"`.
- Both have `role="img"` and an empty `aria-label`, which the code fills in with a full sentence, because a screen reader would otherwise read the digits one by one and make no sense of them.

```js
    <p class="rel-note">Both clocks were set together at 00:00:00. The last digits are millionths of a second (µs).</p>
```
A note under the clocks: "Both clocks were set together at 00:00:00. The last digits are millionths of a second (µs)." It tells the reader how to read the digits (hours, minutes, seconds, then the six decimals).

```js
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
```
Two more readout boxes in a pair (side by side on wide screens).
- "Satellite clock ahead by" with a number (`data-id="gap"`) that starts as a dash. Later it shows the clock gap in whole microseconds, for example "about 38 µs".
- "So every measured distance is wrong by" with a number (`data-id="range"`) that later shows how much extra distance that gap adds, for example "about 11 km".

```js
    <p class="rel-note">A signal covers about 300 m in one millionth of a second.</p>
```
A note: "A signal covers about 300 m in one millionth of a second." This links the two numbers above it: signals travel at the speed of light, about 300,000 km a second, which is 300 m in a millionth of a second.

```js
    <ul class="rel-why" aria-label="Why the satellite clocks run fast">
      <li>Weaker gravity up there: the clock runs faster, by 45 µs a day</li>
      <li>It moves fast: the clock runs slower, by 7 µs a day</li>
      <li><b>Together: about 38 µs a day faster</b></li>
    </ul>
    <p class="rel-note">Both effects come from Einstein's relativity. Gravity is the bigger one.</p>
  </section>
```
A short list (`<ul>`; each `<li>` is a line) of why satellite clocks run fast, with the three numbers from `docs/facts.md` rows 25 to 27 (NIST and NASA figures). They are written into the page text; no code uses them.
- "Weaker gravity up there: the clock runs faster, by 45 µs a day" (row 26, general relativity).
- "It moves fast: the clock runs slower, by 7 µs a day" (row 25, special relativity).
- "**Together: about 38 µs a day faster**" (row 27; the bold `<b>` marks the conclusion). 45 minus 7 is 38.
The `aria-label` names the list for screen readers. The paragraph after it says both effects come from Einstein's relativity and gravity is the bigger one. `</section>` closes the first card.

```js
  <section class="card rel-card" aria-labelledby="rel-b-title">
    <div style="display: grid; gap: var(--s-2)">
      <span class="label">Then</span>
      <h3 id="rel-b-title">So why doesn't your position drift?</h3>
    </div>
```
The second card, **why the position does not drift**. It is named by the heading with the `id` `rel-b-title`. At the top are the small label "Then" and the heading "So why doesn't your position drift?".

```js
    <p class="looking"><b>What you're looking at:</b> the map from the top of the page, twice, with every satellite clock ahead by the same amount. Each map is 40 km wide.</p>
    <p class="rel-note">Cross: where it really is. Dot: where the phone thinks it is.</p>
```
- A "What you're looking at" line: the map from the top of the page, shown twice, with every satellite clock ahead by the same amount. Each map is 40 km wide (this matches `relativityMapHalfWidthM` in [`config.js`](config.js.md): 20,000 m each side of centre).
- A note explaining the symbols: the cross is where the phone really is and the dot is where the phone thinks it is.

```js
    <div class="rel-maps">${mapMarkup("trusted", "The phone trusts its clock", "Ground map, 40 km wide. The phone trusts its clock.")}${mapMarkup("solved", "The phone solves for its clock", "Ground map, 40 km wide. The phone solves for its clock.")}
    </div>
```
The two maps. `${mapMarkup(...)}` calls the function above twice and puts the results straight into the text: first with `"trusted"`, the title "The phone trusts its clock" and its spoken label, then with `"solved"`, the title "The phone solves for its clock" and its label. The closing `</div>` ends the `rel-maps` box.

```js
    <p class="rel-note" data-id="height-note">Most of the left map's error is height, which a flat map cannot show. The dot shows the sideways part.</p>
    <p class="rel-note" data-id="sentence" role="status" aria-live="polite"></p>
```
- A note under the maps, named `height-note`: "Most of the left map's error is height, which a flat map cannot show. The dot shows the sideways part." The map shows only east and north, so an error that is mostly up and down does not show on it. The code hides this note when the trusted error is under 1 m (see `showSentence`).
- An empty polite status line for the summary sentence.

```js
    <div>
      <button class="btn" data-id="reset" type="button" disabled>Reset</button>
      <p class="rel-note" style="margin-top: var(--s-2)" data-id="msg-reset" role="status" aria-live="polite"></p>
    </div>
  </section>
</div>`;
```
- A box holding the Reset button. The `<button>` says "Reset", has the page's button style `btn`, is `type="button"` (an ordinary button) and starts `disabled`.
- Below it, a polite status line (with a small top margin) that will confirm the reset in words.
- `</section>` closes the second card, `</div>` closes the `rel` box, and the backtick and semicolon end the `PAGE` text.

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
    digitsGround: $("digits-ground"), digitsSatellite: $("digits-satellite"), gap: $("gap"), range: $("range"),
    sentence: $("sentence"), heightNote: $("height-note"), reset: $("reset"), msgReset: $("msg-reset"),
  };
```
Builds an object called `el` that gathers every element the code needs under an easy name, for example `el.slider`, `el.digitsGround` and `el.gap`. Doing the search once, here, is neater than searching each time. The maps' parts are gathered separately, just below. If a `data-id` were misspelt the entry would be empty and later lines would fail.

```js
  // The two maps share one set of parts, so one drawing function serves both.
  const maps = {};
```
A comment and an empty object `maps`. The two maps have the same parts, so one drawing function serves both (see `drawMap`). `maps` will hold each map's parts under the names `trusted` and `solved`.

```js
  for (const name of ["trusted", "solved"]) {
    maps[name] = {
      svg: $(`map-${name}`), lines: $(`lines-${name}`), dot: $(`dot-${name}`), caption: $(`caption-${name}`),
      value: $(name), badge: $(`${name}-badge`), base: $(`map-${name}`).getAttribute("aria-label").replace(/\.$/, ""),
    };
  }
```
A **loop** over the two names. For each, `maps[name]` becomes an object holding that map's parts, found with `$`:
- `svg`: the drawing; `lines`: the group for the distance lines; `dot`: the group for the dot; `caption`: the message line under the map;
- `value`: the "off by" number; `badge`: the level badge;
- `base`: the map's spoken label with its final full stop removed (`.replace(/\.$/, "")`). `drawMap` adds the numbers to this base later.

```js
  const { min_h, max_h, step_h, start_h } = config.relativitySlider;
```
Pulls four named values out of `config.relativitySlider` in one go. In [`config.js`](config.js.md) they are: minimum 0 hours, maximum 24 hours, step 1 hour and start 24 hours. The slider starts at one day so the effect is already showing when the reader arrives.

```js
  let callPython = null; // set when the bridge has loaded
  let receiver = null; // true receiver position, from Python
  let satellites = null; // the four satellites, from Python
  let running = false;
  let wanted = false; // true when a newer run is wanted
  let hintDone = false; // once the user has touched the slider, the hint stays hidden
```
Six boxes that change as the section runs.
- `callPython`: the function for asking Python, filled in when Python is ready.
- `receiver`: the phone's position in space, from Python.
- `satellites`: the four satellites with their positions, from Python.
- `running`: is a calculation in progress right now.
- `wanted`: has a newer calculation been asked for. When it is true, one more run is needed.
- `hintDone`: has the reader already touched the slider.

```js
  el.slider.min = min_h;
  el.slider.max = max_h;
  el.slider.step = step_h;
  el.slider.value = start_h;
```
Sets the slider from the config: it runs from 0 to 24, moves one hour at a time and sits at 24. Without these lines the slider would use the browser's defaults of 0 to 100.

```js
  showHours();
```
Calls `showHours` (below) once so the "24 h" next to the slider and its screen-reader text match the starting value.

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
Put the slider back at the starting value (24), refresh the hours text and recalculate. Setting `value` in code does not fire an `input` event, so `showHours` and `update` are called by hand.

```js
    say(el.msgReset, "Back to the start: one day.");
  });
```
Writes "Back to the start: one day." under the button using `say`, which also flashes it briefly. Pressing Reset when already at 24 still gives a visible answer. The last line closes the listener.

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
Adds a record to the list: the satellite's `id` plus everything in `point` (`...point` spreads out its fields). The `}` closes the loop. Python's relativity function and the solver need these records.

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
    if (!hintDone) el.hint.classList.add("is-shown"); // index.html's .hint rule fades it in only with this class
```
Fades the hint in. The page's `.hint` rule starts every hint at opacity 0 (invisible) and only the class `is-shown` makes it opacity 1, so removing `hidden` alone left the hint on the page but unseen. The `if` skips this when the reader already used the slider. Without this line the hint would be invisible.

```js
    update();
  }
```
Run a first calculation so the clocks, gap and maps show real numbers at 24 hours straight away. The `}` closes `start`.

```js
  function showHours() {
    const hours = Number(el.slider.value);
```
A function that refreshes the hours text. `el.slider.value` is text such as `"12"`; `Number(...)` makes it a real number, 12.

```js
    el.sliderValue.textContent = `${hours} h`;
```
Shows it next to the slider, e.g. "12 h".

```js
    el.slider.setAttribute("aria-valuetext", `${hours} hours`);
  }
```
Sets the `aria-valuetext` attribute to "12 hours". A screen reader reads this in place of the bare number, so it says "12 hours" instead of "12". The `}` closes `showHours`.

```js
  // Many slider moves can arrive before one frame. Only the newest value is worked on, and at most one
  // chain of Python calls runs per animation frame, so dragging stays smooth.
  function update() {
```
A comment, then the function that asks for a calculation. Calls to Python take time. Dragging the slider quickly could start many at once, so `update` collects them: many slider moves can arrive before the browser draws one frame, but only the newest value is worked on.

```js
    if (!callPython || !satellites) return;
```
If Python is not ready yet (no `callPython`) or the satellites are not placed, there is nothing to calculate, so stop. `||` means "or".

```js
    wanted = true;
    if (!running) requestAnimationFrame(runNewest);
```
Write down that a newer calculation is wanted (`wanted = true`). Then, if nothing is running, schedule one with `requestAnimationFrame(runNewest)`, which means "call `runNewest` just before the browser draws the next frame". If one is already running, it will see `wanted` and go round again. This keeps the work to at most one chain of Python calls per animation frame, so dragging stays smooth.

```js
  }
```
Closes `update`.

```js
  async function runNewest() {
    if (running || !wanted) return;
    running = true;
```
`runNewest` is the loop that does the work. `async` lets it wait for Python. If a run is already going, or nothing is wanted, it stops at once. Otherwise it marks `running` as true.

```js
    try {
      while (wanted) {
        wanted = false;
        await runOnce();
        if (wanted) await new Promise((resolve) => requestAnimationFrame(resolve)); // let a frame draw first
      }
```
`try` and a `while` loop (repeat while the condition holds). Each time round: clear `wanted`, run one calculation and wait for it (`await runOnce()`). If the slider moved meanwhile, `wanted` is true again, so it waits one animation frame (the `new Promise` with `requestAnimationFrame`) to let the picture draw, then goes round again with the newest value. If many moves arrive, only the newest is calculated.

```js
    } finally {
      running = false;
    }
  }
```
`finally` runs whatever happens, even if something failed. It clears `running`, so the next slider move can start a new calculation. Without `finally` one failure could leave `running` stuck on `true` and the slider would never update again. The last `}` closes `runNewest`.

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
Asks Python's `drift_over_time` in `relativity.py` (see [`relativity.py`](../mechanism/relativity.py.md)). It is given the phone's position, the satellites, the phone's own clock error (0 seconds in [`config.js`](config.js.md)) and a list of hours with just one entry. In Python the drift is 38 millionths of a second per day (`RELATIVITY_DRIFT_S_PER_DAY`, the figure from `docs/facts.md` row 27), so for `hours` hours it is 38e-6 x hours / 24 seconds. Python adds it to every measured distance as a shared amount, in the same way a phone clock error would be (this is the model the page uses). The distance equivalent is that time times the speed of light. Worked example for 24 hours: 38e-6 x 299,792,458 = 11,392.1 metres. For 12 hours it is half of that, 5,696.1 metres. Python then solves the position twice, once solving for the clock and once trusting it, and returns a list with one row per hour. Each row has `hours`, `range_added_m`, `error_clock_solved_m`, `error_clock_trusted_m` and `solved_clock_error_s`.

```js
      if (result.error) { failed(result.error); return; } // Python's own plain sentence
```
If Python replies with an `error`, `failed` shows its own plain sentence (see below) and `return` stops. Without it a refused calculation would show nothing.

```js
      const row = result[0];
      showClocks(row, hours);
```
`result` is a list with one row, since one hour value was sent. `result[0]` is that first row (lists count from 0). `showClocks` puts the clock digits, the gap and the distance on the page.

```js
      // The same chain of calls the first screen uses, once with the clock trusted and once solved.
      const ranges = await callPython("scenario.make_pseudoranges", [receiver, satellites, row.solved_clock_error_s]);
      if (ranges.error) { failed(ranges.error); return; }
```
The same chain of calls the first screen uses, once with the clock trusted and once solved. First `scenario.make_pseudoranges` (see [`scenario.py`](../mechanism/scenario.py.md)) makes the measured distances from the true position, the satellites and a clock error. The clock error given is Python's `solved_clock_error_s` for this hour: the shared drift (38 microseconds at 24 hours). So these are the distances the phone would measure when every satellite clock is that far ahead. If Python reports an error, `failed` shows it and the function stops.

```js
      const trusted = await fix(ranges, false);
      const solved = trusted.error ? trusted : await fix(ranges, true);
      if (solved.error) { failed(solved.error); return; }
```
- `fix(ranges, false)` solves the position **trusting** the phone's clock.
- `fix(ranges, true)` solves it **with the clock solved** too. The line `trusted.error ? trusted : await fix(...)` skips the second call if the first one failed and keeps the error instead. (`? :` is a short if-else.)
- If the second result is an error, `failed` shows it and the function stops.
Both use the same measured distances, so the two maps differ only in how the phone treats its clock.

```js
      requestAnimationFrame(() => {
        drawMap(maps.trusted, trusted, row.error_clock_trusted_m);
        drawMap(maps.solved, solved, row.error_clock_solved_m);
      });
```
`requestAnimationFrame(...)` waits for the next drawing moment and then draws both maps in one go, so they never show different slider positions. `drawMap` is given each map's parts, the result of the fix and the position error from Python (`error_clock_trusted_m` for the left map, `error_clock_solved_m` for the right).

```js
      showSentence(hours, row);
```
`showSentence` sets the one-line summary under the maps and the height note.

```js
    } catch (error) {
      console.error(error);
      failed("Something went wrong in the calculation, so the numbers may be out of date.");
    }
  }
```
If anything fails, write the error to the developer console and tell the reader, "Something went wrong in the calculation, so the numbers may be out of date." The last `}` closes `runOnce`. Without the `try` and `catch`, an error would be silent.

```js
  // Solve the position and get its map lines. Returns { lines, local } or { error }.
  async function fix(ranges, solveClock) {
    const solution = await callPython("solver.solve_position", [satellites, ranges, solveClock]);
    if (solution.error) return solution;
```
A comment, then `fix`, which solves a position and gets its map lines. `ranges` are the measured distances and `solveClock` says whether the clock is solved. It asks Python's `solver.solve_position` (see [`solver.py`](../mechanism/solver.py.md)) for the position. If the answer has an `error`, the function returns it unchanged so the caller can show it.

```js
    const { lat_deg, lon_deg } = config.receiver;
    const point = { x_m: solution.x_m, y_m: solution.y_m, z_m: solution.z_m };
    const local = await callPython("mapview.to_local", [lat_deg, lon_deg, point]);
    if (local.error) return local;
```
- Picks the phone's latitude and longitude from the config.
- `point` takes just the solved x, y and z.
- Asks Python's `mapview.to_local` (see [`mapview.py`](../mechanism/mapview.py.md)) where that point is relative to the true place, as east, north and up metres. The map only needs east and north.
- Returns early if Python reported an error.

```js
    const assumedClockS = solveClock ? solution.clock_error_s : 0;
```
Works out what clock error to draw the distance lines with. If the clock was solved, it uses the solver's `clock_error_s`; if it was trusted, 0. Each map must use the clock error its own solution assumed.

```js
    const lines = await callPython("mapview.distance_lines",
      [lat_deg, lon_deg, satellites, ranges, assumedClockS, config.relativityMapHalfWidthM, config.lineSamples]);
    if (lines.error) return lines;
```
Asks Python's `mapview.distance_lines` for one line per satellite: where the sphere of its measured distance cuts the ground, within the map's half-width (20,000 m, `relativityMapHalfWidthM`), with `lineSamples` points per line. Again, an error is passed on.

```js
    return { lines, local };
  }
```
Returns the lines and the local position together as one object. The `}` closes `fix`.

```js
  // A picture must never outlive its numbers: say what went wrong and hide the lines and dots.
  function failed(words) {
    say(el.sentence, words);
```
A comment: a picture must never outlive its numbers. `failed` writes the plain sentence into the summary line with `say`.

```js
    requestAnimationFrame(() => {
      for (const map of Object.values(maps)) { drawLines(map, []); map.dot.style.display = "none"; }
    });
  }
```
Then, at the next frame, for each map (`Object.values(maps)` is the list of the two maps) it clears the lines (`drawLines(map, [])` marks all of them hidden) and hides the dot. The old picture is gone, so it cannot disagree with the missing numbers. The last `}` closes `failed`.

```js
  // The digits, the gap and the distance. The gap is Python's solved clock error, shown in whole microseconds
  // everywhere, so the digits and the "about N µs" never disagree.
  function showClocks(row, hours) {
```
A comment and the function `showClocks`. It shows the digits, the gap and the distance for one row of Python's answer. The gap is Python's `solved_clock_error_s`, shown in whole microseconds everywhere, so the digits and the "about N µs" never disagree.

```js
    const gapMicroseconds = Math.round(row.solved_clock_error_s * 1e6);
    const digits = formatClockDigits(hours, gapMicroseconds);
```
`row.solved_clock_error_s` is in seconds; times a million (`1e6`) is microseconds; `Math.round` makes it whole. At 24 hours it is 38. Then `formatClockDigits` (see [`format.js`](format.js.md)) writes both clocks as text: the ground clock reads `24:00:00.000 000` and the satellite clock reads `24:00:00.000 038`.

```js
    showDigits(el.digitsGround, digits.ground, digits.satellite);
    showDigits(el.digitsSatellite, digits.satellite, digits.ground);
```
Writes the two rows of digits. `showDigits` is given the row's text and the other row's text, so it can make the differing digits bright.

```js
    el.digitsGround.setAttribute("aria-label", `Clock on the ground reads ${digits.ground} (hours, minutes, seconds, then millionths of a second)`);
    el.digitsSatellite.setAttribute("aria-label", `Clock on the satellite reads ${digits.satellite}, ahead by ${gapMicroseconds} millionths of a second`);
```
Sets the spoken sentence for each row, since the digits alone would be read out badly. Example: "Clock on the satellite reads 24:00:00.000 038, ahead by 38 millionths of a second".

```js
    el.gap.textContent = gapMicroseconds === 0 ? "0 µs" : `about ${gapMicroseconds} µs`;
```
Shows the gap as "about 38 µs". At zero it says exactly "0 µs" instead of "about 0 µs".

```js
    el.range.textContent = row.range_added_m < 1 ? "0 m" : `about ${formatRoughDistance(row.range_added_m)}`;
  }
```
Shows how much extra distance the gap adds. `range_added_m` is Python's number. Under 1 m it says "0 m"; otherwise it says "about" and `formatRoughDistance`: 11,392 m reads as "about 11 km". The word "about" is there because this number comes from a model, not an exact fact. The `}` closes `showClocks`.

```js
  // Digits that differ from the other row are bright; the rest are quiet.
  function showDigits(node, mine, other) {
    node.replaceChildren(...[...mine].map((character, i) => {
```
A comment and the function `showDigits(node, mine, other)`. It writes one row of clock digits into `node`. `[...mine]` splits the text into single characters, and `.map` makes one piece of output per character, with its position `i`. `replaceChildren` swaps the old contents for the new pieces.

```js
      const span = document.createElement("span");
      span.textContent = character;
      if (character !== other[i]) span.className = "diff";
```
For each character it makes a `span` and puts the character in it. If that character is different from the character at the same place in the other row (`character !== other[i]`), the span gets the class `diff` so it is drawn bright (see `.rel-digits .diff`). Equal digits stay quiet. At 24 hours the rows differ only in the last digits, so "038" lights up on the satellite row.

```js
      return span;
    }));
  }
```
Hands back the finished span, then closes the `map` and the `replaceChildren` call, and the function. If the two rows were equal, nothing would be bright.

```js
  function showSentence(hours, row) {
    const sentence = hours === 0
      ? "No gap yet. Both maps agree."
      : "Every satellite is off by the same amount. To the phone that looks exactly like its own clock being wrong, and the fourth satellite already fixes that.";
```
`showSentence` chooses the summary sentence with a short if-else. `===` asks "exactly equal?". At zero hours the sentence is "No gap yet. Both maps agree." At any other hour it is "Every satellite is off by the same amount. To the phone that looks exactly like its own clock being wrong, and the fourth satellite already fixes that." That answers the card's question: a shared offset looks like the phone's own clock error, which the fourth satellite lets it solve for.

```js
    if (el.sentence.textContent !== sentence) say(el.sentence, sentence); // only when the words change
    el.heightNote.hidden = row.error_clock_trusted_m < 1;
  }
```
- Writes the sentence only if it differs from what is already shown. Otherwise dragging the slider would flash the same words over and over, and a screen reader could read them out again each time.
- Shows the height note under the maps only if the trusted error is at least 1 m (`hidden` is set to true when it is under 1 m). The `}` closes `showSentence`.

```js
  // ---------- drawing one small map ----------

  function toPixel(metres) { return (metres + config.relativityMapHalfWidthM) * MAP_SIZE / (2 * config.relativityMapHalfWidthM); }
```
A comment and `toPixel`, which turns metres into a place on the 200-unit map. The map is 40 km wide, from -20,000 to +20,000 m. Adding the half-width moves the range to 0 to 40,000, and multiplying by `MAP_SIZE` then dividing by the full width makes it 0 to 200. Example: 0 m (the centre) becomes 100; +20,000 m becomes 200.

```js
  function drawMap(map, result, errorM) {
    const { lines, local } = result;
    drawLines(map, lines);
```
`drawMap` draws one map from a result. It takes the map's parts, the result of `fix` (lines and local position) and the position error in metres from Python. It unpacks the two parts of the result, then `drawLines` draws the distance lines.

```js
    const x = toPixel(local.east_m);
    const y = MAP_SIZE - toPixel(local.north_m); // north is up
    const inside = x >= 0 && x <= MAP_SIZE && y >= 0 && y <= MAP_SIZE;
```
Works out where the dot goes. The x place is from the east metres. The y place is the map's height minus the north place, because on a screen y grows downward but north must point up. `inside` is true when the dot is on the map. (The trusted dot can fall off the map; then it is hidden.)

```js
    const level = errorLevel(errorM);
    map.dot.style.display = inside ? "" : "none";
    map.dot.firstElementChild.setAttribute("cx", x);
    map.dot.firstElementChild.setAttribute("cy", y);
    map.dot.setAttribute("class", `is-${level}`);
```
- `errorLevel` turns the error in metres into `"ok"`, `"warn"` or `"bad"`.
- The dot is shown only when it is inside the map (`display` is set to empty, meaning "normal", or to `none`).
- Its centre (`cx`, `cy`) is set to the worked-out place.
- Its class becomes `is-ok`, `is-warn` or `is-bad`, so [`theme.css`](theme.css.md) colours it.

```js
    map.value.textContent = errorM < 0.05 ? "0 m off" : `about ${formatRoughDistance(errorM)} off`;
    map.badge.hidden = false;
    map.badge.className = `badge is-${level}`;
    map.badge.textContent = LEVEL_WORDS[level];
```
- The number under the map says "0 m off" for errors under 0.05 m, and otherwise "about" plus the rough distance and "off". Example: the trusted map at 24 hours says "about 20 km off".
- The badge is revealed, gets its level class and the level's words from `LEVEL_WORDS`: for the solved map "Good fix", for the trusted map "Fix is far off".

```js
    // Like the first screen's caption: say when the map hides something.
    const off = lines.filter((line) => !line.inside).length;
    let words = inside ? "" : "The phone's position is off the edge of this map.";
    if (off > 0) words += ` ${off} of the ${lines.length} distance lines ${off === 1 ? "has" : "have"} moved off the edge of this map.`;
    map.caption.textContent = words.trim();
```
A comment and the message line for the map. Like the first screen's caption, it says when the map hides something.
- `off` counts the lines that have moved off the map (`line.inside` is false for them).
- `words` starts as the sentence "The phone's position is off the edge of this map." if the dot is outside, else empty.
- If any lines are off the map, it adds "N of the M distance lines has/have moved off the edge of this map." (`has` for one, `have` for more, chosen by the short if-else).
- `words.trim()` removes the extra space at the start before it is written.

```js
    map.svg.setAttribute("aria-label", `${map.base}. ${lines.length} distance lines. Position off by ${map.value.textContent.replace(" off", "")}.`);
  }
```
Updates the map's spoken description so a screen reader hears the numbers: the base label, then the count of lines, then "Position off by" and the distance (the number's text without its word "off"). The last `}` closes `drawMap`.

```js
  function drawLines(map, lines) {
    const known = new Map([...map.lines.children].map((node) => [node.dataset.id, node]));
```
`drawLines` draws or updates one polyline for each distance line. `known` is a list of the lines already on the map, indexed by their `id`, so existing lines can be reused instead of rebuilt each time.

```js
    for (const line of lines) {
      let node = known.get(line.id);
      if (!node) {
```
For each wanted line: look for an existing one with that `id`. If there is none, make a new `polyline` (a connected run of straight pieces) with `createElementNS`, which needs the `SVG` address from the top because drawing parts live in their own namespace.

```js
        node = document.createElementNS(SVG, "polyline");
        node.dataset.id = line.id;
        node.setAttribute("class", "map-line");
        map.lines.append(node);
      }
```
A new line gets its `id`, the class `map-line` (its look comes from the theme) and is added to the map's group of lines.

```js
      node.setAttribute("points", line.points.map(([e, n]) => [toPixel(e), MAP_SIZE - toPixel(n)]).join(" "));
      node.classList.toggle("is-hidden", !line.inside);
    }
```
Sets the line's shape. `line.points` is a list of east/north pairs from Python; each is turned into pixel x and y with `toPixel` (flipping north to up) and `.join(" ")` makes them one text. Then the class `is-hidden` is switched on if the line is not inside the map and off if it is. The `}` closes the loop.

```js
    const wantedIds = new Set(lines.map((line) => line.id));
    for (const [id, node] of known) if (!wantedIds.has(id)) node.classList.add("is-hidden");
```
- `wantedIds` is the set of ids in the new answer.
- Any old line whose id is not in it gets `is-hidden`, so lines for satellites that are gone disappear.

```js
  }
}
```
The first `}` closes `drawLines` and the last closes `mountRelativityStep`. That is the end of the file.
