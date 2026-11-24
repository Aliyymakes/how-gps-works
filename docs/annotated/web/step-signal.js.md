# step-signal.js, line by line

Source: `web/step-signal.js`

## What this file is for
This file builds the third section of the page, "How does the phone measure the time?". It lets the reader do the phone's job by hand first. Three rows of 40 steps (chips) are shown: what the satellite sends, what the phone hears (the same pattern, a bit late, with noise), and the phone's own copy. The reader drags the copy sideways until it lines up, and a match score tells them how well it fits. Then a button lets the phone try every shift by itself, with the results drawn in two graphs. Last, a noise slider buries the signal until the phone loses it. The file draws and listens. Every number that is shown comes from Python.

## Which files it talks to
- `mechanism/signal.py`: the page asks for three things through the bridge. `signal.ca_code` gives the satellite's pattern (1023 values, each +1 or -1). `signal.make_received` builds the noisy signal the phone hears. `signal.correlate` tries every shift and scores each one. See [signal.py](../mechanism/signal.py.md).
- `web/startup.js`: `whenPythonReady` tells this file when Python has loaded, and shows the "Loading the maths…" progress and failure words. See [startup.js](startup.js.md).
- `web/say.js`: `say` puts a message in a message line and flashes it briefly. See [say.js](say.js.md).
- `web/theme.css`: gives the colours, fonts and the shared classes (`card`, `btn`, `badge`, `inset`, `num`, `label`, `muted`, `slider`). This file only adds layout. See [theme.css](theme.css.md).
- `index.html`: imports `mountSignalStep` and calls it with the empty box `step-signal`. See [index.html](../index.html.md).
- The exact shapes of the numbers passed to and returned from Python are in `docs/interface.md`.

## In three lines
1. When the page loads, `mountSignalStep` adds the section's HTML and style, waits for Python, and fetches the satellite's pattern once. After that, every change of the noise slider asks Python for the heard signal and for the score of every shift.
2. Sliding the phone's copy (the slider, the keyboard, or dragging the row) does not call Python again. It only reads the score for that shift from the last answer. The search button reveals the scores of all shifts that Python had already worked out.
3. The only arithmetic in JavaScript is turning values into pixel positions, one yes/no check per step (is the copy's value on the same side of zero as the heard value, which only decides how a block is shaded), and choosing "Found", "Barely found" or "Lost" by comparing numbers Python returned.

New to code? See [how to read code](../how-to-read-code.md). Ideas used here for the first time are explained where they appear.

## The code, line by line

### The top note and the imports

```js
// Rung 3: how the time is measured (design.md 2a). The user slides the phone's copy of the
// satellite's pattern by hand, then lets the phone try every shift. It draws and takes input;
// the code, the received signal and every score come from Python (mechanism/signal.py).
// The only arithmetic here is scaling numbers to pixels and one sign comparison per step
// (is the copy's value on the same side of zero as the heard value?), which only picks a fill.
```
Five comments (lines starting with `//` are notes for people; the computer skips them). "Rung 3" is the third step of the page's story. `design.md` is the project's spec. They say that this file only draws and listens, that Python provides the pattern, the heard signal and every score, and that the only arithmetic here is scaling to pixels plus one check per step that only decides whether a block is drawn bright or dim. Nothing breaks without them.

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
  trueDelayChips: 14, // placeholder, provisional: how late the signal really arrives (short, so it fits in the 40-step picture)
```
A chip is one step of the pattern (the whole pattern has 1023 chips). The real signal is made to arrive 14 chips late. The phone's job is to find that 14. It is kept small on purpose, so that the late copy still shows inside the 40 steps of the picture. Without it there would be no hidden delay to find.

```js
  windowChips: 40, // placeholder, provisional: how many steps the three rows show
```
How many chips the three rows show: the first 40 of the 1023.

```js
  shift: { min: 0, max: 30, start: 0 }, // placeholder, provisional: how far the phone's copy can be slid, in chips
```
How far the reader can slide the phone's copy: from 0 to 30 chips, starting at 0. Another object inside the object. It stops at 30 so the copy always has room to show in the 40-step picture.

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
The noise slider's range, measured in multiples of the signal: from 0 to 12 in steps of 0.5, starting at 0. Without it the slider would have no range.

```js
  barelyHoldingBelow: 1.5, // placeholder, provisional: peak_to_next under this = found but barely
```
`peak_to_next` is a number Python returns: the best score divided by the second best score. If it is under 1.5, the best match is found but only just clear of the rest. Worked example: a best score of 0.3 and a second best of 0.25 give 0.3 / 0.25 = 1.2, which is under 1.5, so "barely".

```js
  peakDisplayCap: 1000, // placeholder, provisional: above this the readout says "over 1000x"
```
The biggest value shown exactly. It is there for one special case: when the best score is above 0 and no other score is, Python returns 1,000,000,000 ("extremely clear"). At 1000 or more the readout says "over 1000×" instead of a giant number.

```js
  receivedLimit: 2, // placeholder, provisional: the heard row shows values from -2 to +2, bigger ones are cut off
```
The middle row (what the phone hears) shows values from -2 to +2. Anything outside is cut off at the edge. Without this limit big noise would be drawn out of its row.

```js
  scoreRange: { min: -1.25, max: 1.5 }, // placeholder, provisional: the plots show scores in this range
```
Both score graphs show scores from -1.25 to 1.5. Without it they would have no scale.

```js
  revealMs: 1000, // placeholder, provisional: how long the search takes to draw itself
```
How long, in milliseconds (1000 = one second), the two graphs take to draw themselves left to right after the search button is pressed.

```js
  dragStartPx: 8, // placeholder, provisional: sideways movement before a drag starts, so a vertical swipe still scrolls
```
How far a finger or mouse must move sideways, in pixels, before dragging the copy row starts. Below that the move is ignored, so someone scrolling the page with a vertical swipe over the row does not move the copy by accident.

```js
};
```
Closes the object.

### Fixed sizes and words

```js
const CHIP = 10; // width of one step in the rows picture, in picture units
```
Names in capital letters are a habit meaning "never changes". Each chip is 10 units wide in the rows picture. (Picture units are the private coordinates of a drawing; the page stretches the drawing to fit its box.)

```js
const ROWS_W = signalConfig.windowChips * CHIP; // 400
```
The rows picture's width: 40 chips x 10 = 400 units.

```js
const ROW_MID = { sent: 38, heard: 100, copy: 162 }; // the middle line of each row, in picture units
```
The height of the middle line of each row: 38, 100 and 162 units from the top, for "sent", "heard" and "copy". A wave goes above this line for +1 and below it for -1.

```js
const WAVE = 18; // tallest a wave is drawn, either side of its middle line
```
The most a wave may rise or fall from its middle line: 18 units.

```js
const PLOT_HEIGHT = 120; // the full plot's picture is (number of chips) wide and 120 high
```
The all-1023-shifts graph is drawn on a canvas that is 1023 units wide (one per shift) and 120 units high. This is its height.

```js
const CLOSEUP_HEIGHT = 96; // the close-up's picture is 400 wide and 96 high
```
The close-up graph (the first 40 shifts) is 400 units wide and 96 high.

```js
const CODE_LENGTH = 1023;
```
The satellite's pattern has 1023 chips. After the last chip it starts again from the first, which `copyValue` relies on.

```js
const SCORES_LABEL = "The match score at every one of the 1023 shifts.";
```
A description of the full graph for a screen reader (software that reads the page aloud to people who cannot see it). A screen reader cannot read a picture, so the drawing gets an `aria-label`: words that describe it. `aria-*` attributes are extra labels for such software. This is the starting text; `drawFull` adds the live numbers.

```js
const CLOSEUP_PROMPT = "Each shift you try leaves a bar here.";
```
The words shown under the close-up graph before the search: they tell the reader what to expect.

```js
const GUIDE_WORDS = {
  1: "Step 1. Slide the phone's copy until it lines up with what the phone hears.",
  2: "Step 2. Now let the phone do the same search by itself.",
  3: "Step 3. Add noise until the phone loses the signal.",
};
```
The hint text for each of the three steps of the guide, in an object whose labels are the step numbers 1, 2 and 3. `showGuide` picks one.

### The style

```js
// Layout for this section only. Colours, fonts and radii come from theme.css.
const STYLE = `
```
A comment, then the start of one long piece of text, written between backticks (the backtick quotes allow text over many lines). It holds CSS: the rules for how things look. CSS is explained at "A CSS rule" in [how to read code](../how-to-read-code.md). This text is later put in the page. Colours, fonts and rounded corners are left to [`theme.css`](theme.css.md); here only layout is set. A `var(--s-5)` means "use the value of the setting named `--s-5`", which `theme.css` defines (a CSS variable). The spacing ones are `--s-1` 4 px, `--s-2` 8 px, `--s-3` 12 px, `--s-4` 16 px and `--s-5` 24 px. A pixel (px) is one dot on the screen.

```js
.signal-step { display: grid; grid-template-columns: minmax(0, 1fr); gap: var(--s-5); }
```
The whole section is a grid (a layout of rows and columns) with one column that may shrink to nothing and grow to fill the width (`minmax(0, 1fr)`). `gap` is the space between items: 24 px. Without `minmax(0, ...)` a wide child could push the page wider than the screen.

```js
.signal-step .intro { display: grid; gap: var(--s-2); }
```
The heading and its paragraphs form a small grid with 8 px between them.

```js
.signal-step .grid { display: grid; grid-template-columns: minmax(0, 1fr); gap: var(--s-5); }
```
The main area is also one column on a narrow screen, with 24 px between the two cards.

```js
@media (min-width: 760px) {
  .signal-step .grid { grid-template-columns: 1.4fr 1fr; align-items: start; }
  .signal-step .grid > .stack { position: sticky; top: var(--s-4); }
}
```
A media query is a rule that only applies when a condition is true. Here: only when the window is at least 760 px wide. Then the area becomes two columns, the left 1.4 shares wide and the right 1 share (`fr` means "share"), and both start at the top. The second rule makes the right-hand card (`stack`, with the noise slider and the results) sticky: it stays 16 px from the top of the window while the reader scrolls the long left card, so the results stay in view. On a phone it stays one column and nothing sticks.

```js
.signal-step .stack { display: grid; gap: var(--s-4); grid-template-columns: minmax(0, 1fr); }
```
The right card stacks its parts in one column with 16 px between them.

```js
.signal-step .sketch { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: var(--s-3); margin: 0 0 var(--s-4); }
```
The small three-picture sketch near the top sits in three equal columns, 12 px apart, with 16 px of space below it.

```js
.signal-step .sketch > div { display: grid; gap: var(--s-1); align-content: start; }
```
Each of the three sketch pictures and its caption is a small grid, 4 px apart, starting at the top.

```js
.signal-step .sketch svg { width: 100%; height: auto; display: block; }
```
Each sketch drawing fills the width of its column, and its height follows from its shape. `display: block` stops a stray gap under it.

```js
.signal-step .sketch p { margin: 0; font-size: var(--text-xs); color: var(--text-muted); }
```
The captions under the sketch pictures are small (12 px) grey text with no outer space.

```js
.signal-step .rows { overflow: visible; width: 100%; height: auto; display: block; touch-action: pan-y; user-select: none; -webkit-user-select: none; }
```
The rows picture. `overflow: visible` lets things drawn slightly outside its box (the bracket and its words under the bottom row) still show. It fills the card's width, and its height follows its shape. `touch-action: pan-y` lets a finger scroll the page up and down when it starts on the picture, while sideways moves are left to the drag code. `user-select: none` (and the older `-webkit-` spelling for Safari) stops dragging from highlighting text.

```js
.signal-step .row-name { font: 500 13px var(--font-sans); fill: var(--text-muted); stroke: none; }
```
The names written on the rows ("What the satellite sends" and so on) use a medium-weight 13 px font in grey. `fill` is the colour inside letters and shapes in a drawing; `stroke: none` gives them no outline.

```js
.signal-step .sent { fill: none; stroke: var(--text-muted); stroke-width: 1.5; stroke-linejoin: miter; }
```
The top wave (what the satellite sends): no fill, a grey line 1.5 units thick, with sharp corners (`miter`), which suits a square wave.

```js
.signal-step .received { fill: none; stroke: var(--text); stroke-width: 1.5; stroke-linejoin: miter; }
```
The middle wave (what the phone hears): the same but in the main text colour, so it stands out from the grey one.

```js
.signal-step .cell { fill: var(--text); }
```
Each block of the phone's copy row is filled with the main text colour (bright).

```js
.signal-step .cell.is-dim { fill: var(--text-muted); opacity: 0.4; }
```
A block that also has the class `is-dim` is grey and 40 percent solid (faded). Those are the steps where the copy disagrees with what the phone hears.

```js
.signal-step .copy-outline { fill: none; stroke: none; }
```
A rectangle around the copy row that is invisible by default.

```js
.signal-step[data-guide="1"] .copy-outline { stroke: var(--accent); stroke-width: 1.5; }
```
While the guide is on step 1, the section carries `data-guide="1"` and the outline gets the accent colour. This draws the eye to the row the reader is supposed to drag.

```js
.signal-step .bracket { stroke: var(--text-muted); stroke-width: 1; fill: none; }
```
The bracket under the copy row that shows how far it has slid: a thin grey line.

```js
.signal-step .bracket-text { font: 500 13px var(--font-mono); fill: var(--text); stroke: none; }
```
The words next to the bracket ("slid 5 chips") use the monospace font (every letter the same width) at 13 px.

```js
.signal-step .copy-hit { fill: transparent; cursor: grab; }
```
An invisible rectangle over the copy row that catches the mouse or finger. `transparent` is see-through but still catches touches. The mouse cursor becomes an open hand (`grab`).

```js
.signal-step.is-dragging .copy-hit { cursor: grabbing; }
```
While a drag is going on, the section carries the class `is-dragging` and the cursor becomes a closed hand.

```js
.signal-step .guide-block { border: 1px solid transparent; border-radius: var(--r-inner); padding: var(--s-3); display: grid; gap: var(--s-2); }
```
A guide block is a box that holds one step's controls. It has an invisible 1 px border, so that it can show a coloured one later without the page shifting. It has rounded corners, 12 px of inner space, and 8 px between its parts.

```js
.signal-step[data-guide="1"] .g1, .signal-step[data-guide="2"] .g2, .signal-step[data-guide="3"] .g3 { border-color: var(--accent); }
```
The block for the current guide step gets the accent-coloured border. Three rules in one line (commas separate them): step 1 lights up block `g1`, step 2 lights up `g2`, step 3 lights up `g3`.

```js
.signal-step .slider.guide-block { padding: var(--s-4); }
```
The noise slider's block has a roomier 16 px inside.

```js
.signal-step .hand-score { display: flex; align-items: baseline; gap: var(--s-3); flex-wrap: wrap; }
```
The row with the words "Match score" and the number: side by side (`flex`), lined up along the bottom of the letters (`baseline`), 12 px apart, and allowed to wrap on a narrow screen.

```js
.signal-step .meter { height: 4px; border-radius: 2px; background: var(--line-strong); overflow: hidden; }
```
The score meter is a thin bar, 4 px high with rounded ends, in a grey track. `overflow: hidden` cuts off anything that sticks out of it.

```js
.signal-step .meter-fill { height: 100%; width: 100%; background: var(--text); transform-origin: left; transform: scaleX(0); }
```
The coloured part of the meter is made full size and then squashed sideways. `scaleX(0)` shrinks its width to nothing, and `transform-origin: left` makes it shrink towards the left edge. `drawHand` changes the 0 to a number between 0 and 1, so the bar grows from the left.

```js
.signal-step .plot-title { margin: var(--s-4) 0 var(--s-1); font-size: var(--text-sm); color: var(--text); font-weight: 500; }
```
The titles over the two graphs: 14 px, a little bolder, full text colour, with 16 px of space above and 4 px below.

```js
.signal-step .plot-area { position: relative; }
```
A graph's box. `position: relative` makes it the anchor that things placed inside it by position are measured from.

```js
.signal-step .plot-area > svg { width: 100%; display: block; }
```
A drawing directly inside it fills the width and sits as a block.

```js
.signal-step .plot-area .overlay { position: absolute; left: 0; top: 0; }
```
The overlay drawing is placed on top of the other one, in the same corner. The close-up uses two drawings stacked: one for the shifts the reader tried by hand, one for all of them after the search.

```js
.signal-step .plot-area .bar { fill: var(--text); }
```
Each bar of the close-up graph is filled with the text colour.

```js
.signal-step .plot-full { height: 120px; }
.signal-step .plot-close { height: 96px; }
```
The full graph's box is 120 px high and the close-up's is 96 px, the same as their pictures.

```js
.signal-step .scores { fill: none; stroke: var(--text-muted); stroke-width: 1; vector-effect: non-scaling-stroke; }
```
The score line in the full graph: no fill, grey, 1 pixel thick. The graph is stretched to fit its box, which would normally also stretch the line's thickness. `non-scaling-stroke` stops that, so the line stays 1 pixel thick.

```js
.signal-step [data-reveal="hidden"] { clip-path: inset(0 100% 0 0); }
```
The reveal animation has three states, kept in a `data-reveal` label. `clip-path` cuts away part of what is shown. In the `hidden` state, `inset(0 100% 0 0)` cuts 100 percent from the right, so nothing shows.

```js
.signal-step [data-reveal="running"] { clip-path: inset(0 0 0 0); transition: clip-path var(--reveal-ms, 1000ms) linear; }
```
In the `running` state nothing is cut away, and `transition` makes the change from the hidden cut-off to this one happen smoothly over `--reveal-ms` (one second unless the file set another), at a steady speed (`linear`). The result is a graph that appears from left to right.

```js
.signal-step [data-reveal="done"] { clip-path: none; }
```
In the `done` state the clipping is removed completely.

```js
.signal-step .lane { position: relative; height: 32px; }
```
A lane is a strip above or below a graph that holds a tick mark and its words. It is 32 px high and is the anchor for things placed inside it.

```js
.signal-step .lane .tick { position: absolute; width: 2px; height: 12px; margin-left: -1px; overflow: visible; }
```
A tick is a small mark, 2 px wide and 12 px high, placed by its position inside the lane. The `-1px` left margin centres it on the spot it points at.

```js
.signal-step .lane-top .tick { bottom: 0; }
.signal-step .lane-bottom .tick { top: 0; }
```
In a lane above the graph the tick sits at the bottom of the lane (touching the graph). In a lane below the graph it sits at the top.

```js
.signal-step .lane .tick-label { position: absolute; white-space: nowrap; font-size: var(--text-xs); color: var(--text); line-height: 16px; }
```
The words of a tick ("real delay", "phone's best match") are placed by position, kept on one line (`nowrap`), 12 px, and 16 px tall.

```js
.signal-step .lane-top .tick-label { top: 0; }
.signal-step .lane-bottom .tick-label { bottom: 0; }
```
Above the graph the words sit at the top of the lane, above the tick. Below the graph they sit at the bottom, under the tick.

```js
.signal-step .tick line { stroke-width: 2; }
```
The line inside a tick is 2 units thick.

```js
.signal-step .tick[hidden] { display: none; }
```
`hidden` is an attribute (an extra setting on an HTML element) that means "do not show this". Because the tick's own `position` rules could override `hidden`, this line makes sure that a tick with `hidden` really disappears.

```js
.signal-step .mark-true { stroke: var(--text); }
```
The tick for the real delay is in the main text colour.

```js
.signal-step .mark-best { stroke: currentColor; }
```
The tick for the best match found: `currentColor` means "use the text colour of the surrounding element". The tick gets a class `is-ok`, `is-warn` or `is-bad` (see `setLevelClass`), which sets that colour. So the tick turns green, amber or red with the result.

```js
.signal-step .axis { display: flex; justify-content: space-between; font-size: var(--text-xs); color: var(--text-muted); }
```
The little labels under the full graph ("shift 0" and "shift 1022") sit in a row (`flex`) pushed to the two ends (`space-between`), in small (12 px) grey text.

```js
.signal-step .key { font-size: var(--text-sm); }
```
Explanation notes use 14 px text.

```js
.signal-step .readout { padding: var(--s-4); display: grid; gap: var(--s-2); }
```
A box with results has 16 px of space inside and its rows are 8 px apart.

```js
.signal-step .readout-row { display: flex; justify-content: space-between; align-items: baseline; gap: var(--s-3); }
```
A row in a results box: a name on the left and a number on the right, lined up along the bottom of the letters, with at least 12 px between them.

```js
.signal-step .big { font-size: var(--text-xl); }
```
The big numbers ("Best match found at" and the match score) are large (32 px).

```js
.signal-step .badge[hidden] { display: none; }
```
The shared `badge` style in [`theme.css`](theme.css.md) sets how a badge is laid out, which would override `hidden`. This line makes sure that a badge with `hidden` really disappears. Without it an empty badge would show before the first result.

```js
.signal-step .note { font-size: var(--text-sm); color: var(--text-muted); min-height: 1.5em; }
```
A message line: small grey text that always keeps at least 1.5 lines of height (`em` is the size of one letter), so the page does not jump when a message appears.

```js
.signal-step .note:empty { min-height: 0; }
```
`:empty` picks any note that has no words in it. Those take no space at all. This stops blank gaps in the cards.

```js
.signal-step .stack > .note:empty { margin-bottom: calc(-1 * var(--s-4)); }
```
An empty note that sits directly in the right card would still leave its 16 px gap on each side. This pulls the space below it back by 16 px (`calc` does the sum, and the minus sign makes the margin negative), so an empty note leaves no gap.

```js
.signal-step .slider.guide-block { row-gap: 0; }
```
Inside the noise slider's block the rows have no space between them, so that the next two rules control the spacing.

```js
.signal-step .slider.guide-block .slider-head { margin-bottom: var(--s-2); }
```
The row with the "Add noise" label has 8 px below it.

```js
.signal-step .slider.guide-block > .note:not(:empty) { margin-top: var(--s-2); }
```
A message line under the slider gets 8 px above it, but only when it has words in it (`:not(:empty)`). When it is empty the block stays compact.

```js
.signal-step [data-el="clip-note"]:empty, .signal-step .note[data-el="closeup-note"]:empty { min-height: 1.5em; }
```
Two message lines keep their height even when empty: the warning that the noise is cut off, and the line under the close-up graph. Without it the picture below them would jump each time a message appeared or disappeared. `data-el="clip-note"` picks the one element whose `data-el` label is that.

```js
.signal-step .g1 + .readout { margin: var(--s-3) 0; }
```
The results box that comes straight after the step 1 block (the match score) gets 12 px of space above and below. The `+` means "directly after".

```js
@media (max-width: 759px) {
  .signal-step .row-name, .signal-step .bracket-text { font-size: 16px; }
  .signal-step [data-el="clip-note"]:empty, .signal-step .note[data-el="closeup-note"]:empty { min-height: 3em; }
}
```
On a narrow screen (up to 759 px, the opposite of the earlier rule), the words on the rows picture are larger (16 px) because the whole picture is shrunk to fit and its words would be tiny. The two reserved message lines get 3 lines of room, because their text wraps over more lines on a small screen.

```js
.signal-step h3.label { margin-bottom: var(--s-3); }
```
The small headings have 12 px of space below them.

```js
.signal-step h3.label:not(:first-child) { margin-top: var(--s-5); }
```
A small heading that is not the first thing in its card gets 24 px above it, to separate the parts ("Try it by hand", "Now let the phone search").

```js
.signal-step .hint { font-size: var(--text-sm); font-weight: 500; color: var(--text); }
```
The hint at the top of the section is 14 px, a little bolder, and in the full text colour so it stands out.

```js
.signal-step .slider-head { flex-wrap: wrap; column-gap: var(--s-3); }
```
The row with a slider's label and its value may wrap to a second line on a narrow screen, with 12 px between the items.

```js
.signal-step .btn { touch-action: manipulation; }
```
On a touch screen, tells the browser the button needs no double-tap zoom. This makes a tap react at once.

```js
.signal-step .btn:disabled, .signal-step input[type="range"]:disabled { opacity: 0.4; cursor: not-allowed; }
```
`:disabled` picks a control that cannot be used right now. The buttons and sliders are disabled until Python has loaded. This makes them 40 percent solid (faded) and shows a "not allowed" mouse cursor. Without it a locked control would look like a working one.

```js
.signal-step .btn:disabled:hover { border-color: var(--line-strong); }
```
When the mouse is over a disabled button, its outline does not change. A working button highlights on hover; a locked one should not.

```js
.signal-step input[type="range"] { touch-action: pan-y; }
```
A slider is an `input` of type `range`. On a touch screen, `pan-y` lets the finger scroll the page up and down when it starts on the slider, while left and right drags move the slider.

```js
@media (prefers-reduced-motion: reduce) { .signal-step [data-reveal] { transition: none !important; } }
```
Some people set their device to avoid animation. This rule applies to them: the reveal's smooth change is switched off (`!important` makes sure this wins over the other rule). The JavaScript also skips the animation for them (see `startReveal`).

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
Makes a small helper called `find`. An arrow function (`(name) => ...`) is a short way to write a function. Given a name such as `"noise"` it looks inside `root` for the element whose `data-el` attribute equals that name (`querySelector` finds the first match). Worked example: `find("noise")` finds the noise slider, which is written `data-el="noise"` in the HTML below. The backticks with `${name}` put the name into the text. The `data-el` labels are used instead of `id`s so that the section does not clash with other parts of the page.

```js
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
```
Makes an object called `el` that holds every element the code will touch, each under a short name. Doing the search once here, instead of at every use, is quicker and keeps names in one place. In groups:
- The top: `status` the "Loading the maths…" line, `hint` the guide hint, `clipNote` the warning that noise is cut off.
- The rows picture: `rows` the whole drawing, `sentLine` and `receivedLine` the two waves, `copyCells` the group that will hold the 40 blocks of the copy row, `bracket`, `bracketLine` and `bracketText` the bracket under the copy row and its words, `copyHit` the invisible rectangle that catches dragging.
- The hand controls: `shift` the slider that slides the copy, `shiftValue` its words, `handScore` the match score, `meter` the bar under it, `handSentence` the sentence ("Lined up..." or "Not lined up yet...").
- The search: `search` the button, `msgSearch` its message line.
- The close-up graph: `closeupTries` holds the bars for shifts tried by hand, `closeupRest` the bars for all 40 shifts after the search, and `closeupRestWrap` is the box around the latter that the reveal animation clips.
- The full graph: `fullWrap` the box around it, `fullSvg` the drawing, `scoresLine` the score line.
- The tick marks and their words: the real delay and the best match, each in the close-up (`closeup...`) and in the full graph (`full...`).
- `closeupNote` the line under the close-up.
- The noise controls: `slider`, `sliderValue`, `msgSlider`, then `reset` and `msgReset`.
- The results: `bestDelay`, `trueDelay`, `peak`, `badge`, `sentence`, and `emptyLine`, the line "Press the button and the phone searches." shown before the first search.

If a name were wrong, `find` would give nothing and the first use below would fail.

```js
  let callPython = null; // set when the bridge has loaded
```
`let` makes a variable that can change later (unlike `const`). `callPython` will hold the function that sends a request to Python. The bridge is the connection between the page and Python. `null` means "nothing yet". Without it the file would have no way to ask Python.

```js
  let code = null; // the satellite's 1023 steps, from Python
  let received = null; // what the phone hears at the current noise, from Python
  let result = null; // the scores for the current noise, from Python
```
Three more places to keep Python's answers, empty at first: the satellite's pattern (1023 values of +1 or -1), what the phone hears at the current noise, and the scores for every shift (with the best shift and `peak_to_next`).

```js
  let noise = signalConfig.noise.start;
  let shift = signalConfig.shift.start;
```
The current noise (starting at 0) and the current slide of the phone's copy (starting at 0 chips).

```js
  let searched = false; // has the user pressed the search button yet
```
Whether the reader has pressed the search button yet. Before that, the graphs show only what the reader tried by hand.

```js
  let guide = 1; // which step of the guide is current (0 = finished)
```
Which step of the three-step guide is current: 1, 2 or 3, or 0 when the guide is over.

```js
  const visited = new Set(); // shifts the user has stopped on by hand
```
A `Set` is a collection that holds each value at most once. This one remembers every shift the reader has slid the copy to by hand, which become bars in the close-up graph.

```js
  let shownNoise = 0; // the noise the rows were last drawn with
```
The noise value that the rows picture was last drawn with. It is used in the words that describe the picture for a screen reader.

```js
  let running = false;
  let rerun = false;
```
Two yes/no flags (`true` or `false`). `running` is true while a request to Python is in progress. `rerun` is true when the noise slider moved while that request was running, so a fresh one is needed afterwards. They are used by `update` below.

```js
  let drag = null;
```
Holds the details of a drag in progress (which finger, where it started), or `null` when no drag is going on.

```js
  let revealTimer = 0;
```
A number that identifies the pending timer that ends the reveal animation, so it can be cancelled.

```js
  buildStaticParts();
  setupControls();
  start();
```
Three calls, in this order: build the parts of the picture that never change, set up the sliders and buttons, then start waiting for Python. All are defined below. A function can be called before the line where it is written because JavaScript reads the whole function first. Without them nothing would run.

### Start up

```js
  // ---------- start up ----------
```
A comment that marks a section of the file. Nothing breaks without it.

```js
  async function start() {
```
Starts a function called `start`. `async` marks a function that may wait for slow things. Inside it, the word `await` means "pause here until this finishes, but let the rest of the page keep working".

```js
    whenPythonReady(el.status, async (call) => {
```
Asks [`startup.js`](startup.js.md) to say when Python is ready. The first thing given is the status line, so `startup.js` can show "Loading the maths…" or a failure message there. The second is a function to run once Python is ready; it receives `call`, the function that sends requests to Python. This function is `async` too, because it waits for Python's answer.

```js
      callPython = call;
```
Saves it in the variable made earlier, so the rest of the file can use it.

```js
      const steps = await callPython("signal.ca_code", [signalConfig.prn]);
```
Asks Python to run `ca_code` from `mechanism/signal.py` (see [signal.py](../mechanism/signal.py.md)) for satellite 7, and waits. It returns the satellite's pattern: 1023 values, each +1 or -1. This is the same for every noise level, so it is asked for once.

```js
      if (failed(steps)) return;
```
If Python answered with an error message instead of numbers, show it and stop (see `failed` below).

```js
      code = steps;
```
Keeps the pattern for later.

```js
      setControlsDisabled(false);
```
Unlocks the sliders and the buttons (they start locked).

```js
      showGuide();
```
Shows the first guide hint ("Step 1. Slide the phone's copy until it lines up...").

```js
      update();
```
Does the first calculation and drawing, so the rows and graphs are filled in as soon as Python is ready.

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
  function buildStaticParts() {
```
Starts the function that builds the parts of the rows picture that are the same every time.

```js
    const cells = [];
```
An empty list to collect the blocks of the copy row.

```js
    for (let i = 0; i < signalConfig.windowChips; i += 1) {
```
A loop that counts `i` from 0 up to 39 (while `i` is less than 40, adding 1 each time round).

```js
      cells.push(`<rect class="cell" x="${i * CHIP + 0.5}" width="${CHIP - 1}" height="${WAVE / signalConfig.receivedLimit}"/>`);
```
For each chip, adds the text of one block (an SVG `rect`, a rectangle) to the list. It sits at `i * 10 + 0.5` units from the left and is `10 - 1 = 9` wide, so that there is a small gap between neighbours. Its height is `18 / 2 = 9`. The up-or-down position is set later, because it depends on whether the copy's value is +1 or -1.

```js
    }
```
Closes the loop.

```js
    el.copyCells.innerHTML = cells.join("");
```
Joins the 40 texts with nothing between them and puts them into the copy row's group. Setting `innerHTML` replaces what is inside an element with elements made from the text.

```js
    el.cells = [...el.copyCells.children];
```
Takes the 40 block elements just made and keeps them in a list called `el.cells` (`...` spreads the group's children into a plain list). `drawCopyRow` goes through this list.

```js
    el.trueDelay.textContent = "–";
```
Writes a dash into the "Real delay" readout. The real delay is not shown until the reader has found it or searched (see `updateRealMarks`), so as not to give the answer away.

```js
    placeTick(el.closeupRealTick, el.closeupRealLabel, (signalConfig.trueDelayChips + 0.5) / signalConfig.windowChips);
```
Places the "real delay" tick above the close-up graph. The position is a fraction of the width: (14 + 0.5) / 40 = 0.3625, the middle of the 15th bar's slot (bars are numbered from 0). See `placeTick`. It is placed now, but stays hidden for the moment.

```js
    placeTick(el.fullRealTick, el.fullRealLabel, signalConfig.trueDelayChips / CODE_LENGTH);
```
The same for the full graph: 14 / 1023, about 0.0137 of the way along.

```js
    root.style.setProperty("--reveal-ms", `${signalConfig.revealMs}ms`);
```
Sets the CSS variable `--reveal-ms` to `1000ms` on the section. The reveal rule reads it, so the animation lasts as long as the settings say.

```js
  }
```
Closes `buildStaticParts`.

```js
  function setupControls() {
```
Starts the function that sets up the sliders, the dragging and the buttons.

```js
    const { min, max, step, start: startValue } = signalConfig.noise;
```
Destructuring: takes four values out of the `noise` settings in one line and gives each a name. `start` is renamed `startValue` here, because a function called `start` already exists. With the real numbers: `min` is 0, `max` is 12, `step` is 0.5, `startValue` is 0.

```js
    // The noise slider counts steps (whole numbers), so there are no floating point surprises.
```
A comment. Computers store numbers like 0.1 slightly inexactly (a "floating point" surprise). The slider therefore counts whole steps and the file turns them into noise afterwards.

```js
    el.slider.min = 0;
    el.slider.max = Math.round((max - min) / step);
    el.slider.step = 1;
    el.slider.value = Math.round((startValue - min) / step);
```
Sets the noise slider's own properties. It starts at step 0 and moves 1 step at a time. Its top is `Math.round((max - min) / step)` (`Math.round` rounds to the nearest whole number). Worked example: (12 - 0) / 0.5 = 24, so the slider has 24 steps, 0 to 24. The starting position is (0 - 0) / 0.5 = 0, the left end (no noise). Without these lines the slider would use the browser's default range of 0 to 100.

```js
    el.slider.addEventListener("input", () => {
```
An event is something that happens on the page, like a click or a drag. `addEventListener` says "when this happens to the slider, run this function". `"input"` fires every time the slider moves, even in the middle of a drag. Without it the slider would do nothing.

```js
      noise = Number(el.slider.value) * step + min;
```
Turns the slider position back into a noise size. `el.slider.value` comes as text, so `Number(...)` makes it a number. Worked example: position 7 gives 7 x 0.5 + 0 = 3.5, so the noise is 3.5 times the signal. Without it the file would not know the noise.

```js
      el.msgReset.textContent = "";
      el.msgSearch.textContent = "";
```
Clears the messages under the Reset button and under the search button (such as "Back to the start..." or "The phone tried all 1023 shifts..."), because they are out of date now. `textContent` is the words inside an element.

```js
      if (guide === 3) { guide = 0; showGuide(); }
```
If the guide is on step 3 ("Add noise until the phone loses the signal"), the reader has now done it, so the guide is set to finished (0) and the hint disappears.

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
    el.shift.min = signalConfig.shift.min;
    el.shift.max = signalConfig.shift.max;
    el.shift.step = 1;
    el.shift.value = shift;
```
Sets up the slider that slides the phone's copy: from 0 to 30, one chip at a time, starting at the current shift (0).

```js
    el.shift.addEventListener("input", () => setShift(Number(el.shift.value)));
```
Whenever that slider moves, hands its position to `setShift`, which slides the copy.

```js
    // Dragging the copy row. A drag starts after a few pixels of sideways movement, so a vertical swipe still scrolls the page.
```
A comment: the reader can also drag the copy row itself with a mouse or finger. The drag only starts after a few pixels of sideways movement.

```js
    el.copyHit.addEventListener("pointerdown", (event) => {
```
A "pointer" can be a mouse, a finger or a pen. `pointerdown` fires when it first presses on the invisible rectangle over the copy row. `event` holds the details.

```js
      if (!result) return;
```
If Python has not given a result yet, do nothing. There are no scores to show, so sliding makes no sense yet.

```js
      drag = { id: event.pointerId, x: event.clientX, from: shift, started: false };
```
Notes the start of a possible drag in an object: which pointer it is (`id`), where it was horizontally on the screen (`x`), what the shift was at the time (`from`), and that the drag has not really started yet (`started: false`).

```js
      el.copyHit.setPointerCapture(event.pointerId);
```
Tells the browser to keep sending this pointer's movements to the row, even if the pointer leaves it. Without it a quick drag could slip off the row and stop.

```js
    });
```
Closes the pointerdown function.

```js
    el.copyHit.addEventListener("pointermove", (event) => {
```
Runs each time the pointer moves over the row.

```js
      if (!drag || event.pointerId !== drag.id) return;
```
If no drag is being tracked, or the move comes from a different pointer (a second finger), ignore it.

```js
      const moved = event.clientX - drag.x;
```
How far the pointer has moved sideways since the press, in pixels. Left is negative, right is positive.

```js
      if (!drag.started) {
```
If the drag has not really started yet, check whether it should.

```js
        if (Math.abs(moved) < signalConfig.dragStartPx) return;
```
`Math.abs` drops the minus sign, so this is the distance in either direction. If it is under 8 px, do nothing yet. This is what lets a vertical swipe scroll the page instead.

```js
        drag.started = true;
        root.classList.add("is-dragging");
```
The drag has started. The section gets the class `is-dragging`, which the CSS uses to show the closed-hand cursor.

```js
      }
```
Closes the `if`.

```js
      const chipPixels = (el.rows.getBoundingClientRect().width / ROWS_W) * CHIP;
```
Works out how many screen pixels one chip is wide right now. `getBoundingClientRect().width` is the picture's width on the screen. Worked example: if the picture is 800 px wide on screen, then 800 / 400 x 10 = 20 px per chip. It is worked out each time because the picture changes size with the window.

```js
      setShift(drag.from + Math.round(moved / chipPixels));
```
Turns the pixel movement into whole chips and slides the copy to the starting shift plus that. Worked example: moved 65 px at 20 px per chip is 3.25, which rounds to 3, so the copy is slid to 3 chips beyond where the drag began. `setShift` keeps the result inside the allowed range.

```js
    });
```
Closes the pointermove function.

```js
    const endDrag = (event) => {
```
Defines a function called `endDrag`, used when the pointer lifts or is interrupted.

```js
      if (!drag || event.pointerId !== drag.id) return;
```
The same check: only react to the pointer that started the drag.

```js
      drag = null;
      root.classList.remove("is-dragging");
```
Forgets the drag and removes the class, so the cursor goes back to an open hand.

```js
    };
```
Closes `endDrag`.

```js
    el.copyHit.addEventListener("pointerup", endDrag);
    el.copyHit.addEventListener("pointercancel", endDrag);
```
`endDrag` is run when the pointer lifts (`pointerup`) and also when the browser cancels the touch (`pointercancel`, for example when it decides the gesture is a page scroll). Without these the row would stay stuck in drag mode.

```js
    el.search.addEventListener("click", (event) => search(event.detail === 0)); // detail 0 = pressed from the keyboard
```
When the search button is clicked, runs `search`. `event.detail` is how many clicks in a row this is; it is 0 when the button was "clicked" from the keyboard (Enter or space). So `search(true)` for the keyboard and `search(false)` for the mouse or finger. The keyboard version skips the animation.

```js
    // Any new input ends the reveal at once.
```
A comment: if the reader does anything while the graphs are drawing themselves, the drawing jumps to its end.

```js
    for (const type of ["pointerdown", "keydown", "input"]) root.addEventListener(type, finishReveal, true);
```
A loop over three kinds of event: a press, a key press and a slider move. For each, it asks the whole section to run `finishReveal`. The final `true` means "listen on the way down", before the element that was actually clicked sees the event, so the reveal ends first.

```js
    el.reset.addEventListener("click", () => {
```
When the Reset button is clicked, run this function. It puts everything back as it was at the start.

```js
      noise = startValue;
      el.slider.value = Math.round((startValue - min) / step);
```
Puts the noise back to 0 and moves the noise slider back to its starting position (0 steps).

```js
      shift = signalConfig.shift.start;
      el.shift.value = shift;
```
Puts the phone's copy back at 0 and moves its slider there.

```js
      visited.clear();
      searched = false;
      guide = 1;
```
Forgets the shifts tried by hand, forgets that the search was pressed, and sends the guide back to step 1.

```js
      el.msgSearch.textContent = "";
      el.bestDelay.textContent = "–";
      el.trueDelay.textContent = "–";
      el.peak.textContent = "–";
```
Clears the message under the search button and puts a dash back in the three readout numbers.

```js
      el.badge.hidden = true;
      el.sentence.textContent = "";
      el.emptyLine.hidden = false;
```
Hides the badge, clears the sentence, and shows the "Press the button and the phone searches." line again.

```js
      el.closeupNote.textContent = CLOSEUP_PROMPT;
```
Puts the starting words back under the close-up graph.

```js
      updateRealMarks();
```
Hides the "real delay" ticks again (the reader has not found it, in this fresh start).

```js
      el.closeupBestTick.setAttribute("hidden", "");
      el.closeupBestLabel.hidden = true;
      el.fullBestTick.setAttribute("hidden", "");
      el.fullBestLabel.hidden = true;
```
Hides the four marks for the phone's best match. A tick is an SVG element, which is hidden by setting the `hidden` attribute; a label is an ordinary element, which has a `hidden` property.

```js
      el.hint.hidden = false;
      el.msgReset.textContent = "";
```
Shows the hint again and clears the message under the Reset button (a new one is shown at the end).

```js
      showNoiseValue();
      showGuide();
      setReveal("hidden");
      update();
```
Updates the words next to the slider, shows the step 1 hint, sets the graphs back to their hidden state, and starts a fresh calculation and drawing.

```js
      say(el.msgReset, "Back to the start: copy at 0, no noise.");
```
Shows "Back to the start: copy at 0, no noise." under the button and flashes it. Without it, pressing Reset when the picture is already at the start would show nothing, and the press would feel dead.

```js
    });
```
Closes the Reset function.

```js
    window.addEventListener("resize", placeAllLabels);
```
When the browser window changes size, re-places the tick words. They are placed in pixels, so they must be redone for the new width.

```js
    showNoiseValue();
    setControlsDisabled(true);
```
Writes the starting words next to the noise slider, then locks the sliders and buttons until Python is ready (`start` unlocks them).

```js
  }
```
Closes `setupControls`.

```js
  function setControlsDisabled(disabled) {
    el.slider.disabled = disabled;
    el.shift.disabled = disabled;
    el.search.disabled = disabled;
    el.reset.disabled = disabled;
  }
```
A helper: `true` locks the two sliders and the two buttons, `false` unlocks them. A disabled control ignores clicks and drags. Without it the reader could use them before Python has loaded, and nothing could answer.

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

### The guide

```js
  function showGuide() {
```
Starts the function that shows the hint for the current guide step.

```js
    root.dataset.guide = String(guide);
```
Writes the current step into the section's `data-guide` label (as text). The CSS reads that label to put the accent border round the right block and the accent outline round the copy row.

```js
    el.hint.hidden = guide === 0;
```
Hides the hint when the guide is finished (0), shows it otherwise.

```js
    if (guide !== 0) {
      el.hint.textContent = GUIDE_WORDS[guide];
      el.hint.classList.add("is-shown"); // index.html's .hint rule fades it in only with this class
    }
```
While the guide is not finished: writes that step's words into the hint (square brackets pick the entry named by `guide` from the object `GUIDE_WORDS`), and adds the class `is-shown`. The page's `.hint` rule starts every hint at opacity 0 (invisible) and only the class `is-shown` makes it visible, so without this line the hint would be on the page but unseen.

```js
  }
```
Closes `showGuide`.

```js
  function moveGuideTo(step) {
    if (guide !== 0 && step > guide) { guide = step; showGuide(); }
  }
```
Moves the guide forward to a given step, but only if the guide is not finished and the step is later than the current one. So the guide never goes backwards, and does not come back once finished.

```js
  // Slide the copy to a whole number of chips. No Python call: the score is read from the last result.
```
A comment: sliding the copy does not ask Python anything. The score of every shift was already worked out by Python for the current noise, so the page just looks up the one it needs.

```js
  function setShift(value) {
```
Starts the function that slides the phone's copy to `value` chips. The slider, the keyboard and dragging all use it.

```js
    const { min, max } = signalConfig.shift;
    const next = Math.min(max, Math.max(min, Math.round(value)));
```
Rounds to a whole number of chips, then keeps it within 0 to 30. `Math.max(min, ...)` takes the bigger of the two, so nothing goes below 0. `Math.min(max, ...)` takes the smaller, so nothing goes above 30. Worked example: a drag that asks for 37 gives 30; one that asks for -4 gives 0.

```js
    if (next === shift) return;
```
If the copy is already there, stop. This saves redrawing on every tiny movement.

```js
    shift = next;
    el.shift.value = shift;
```
Keeps the new shift, and moves the slider's handle to match (it matters when the move came from dragging the row).

```js
    visited.add(shift);
```
Remembers this shift as one the reader has stopped on. It becomes a bar in the close-up graph.

```js
    updateRealMarks();
```
Checks whether the real delay should be shown now (it is, once the reader has stopped on it).

```js
    if (shift === signalConfig.trueDelayChips) moveGuideTo(2);
```
If the copy is now exactly at the real delay (14), move the guide on to step 2 ("let the phone do the same search by itself").

```js
    drawHand();
    drawCloseup();
```
Redraws the copy row with its score, and the close-up with the new bar.

```js
  }
```
Closes `setShift`.

### The search

```js
  // ---------- the search ----------
```
A section marker.

```js
  function search(atOnce) {
```
Starts the function that runs when the reader presses the search button. `atOnce` is `true` when the press came from the keyboard.

```js
    if (!result) return;
```
If there is no result from Python yet, do nothing.

```js
    searched = true;
```
Remembers that the search has been pressed. The drawing functions use this to show all the shifts.

```js
    moveGuideTo(3);
```
Moves the guide on to step 3 ("Add noise until the phone loses the signal").

```js
    drawResult();
    drawCloseup();
    drawFull();
```
Fills in the readout (best delay, how much the peak stands out, the badge and sentence), the close-up graph with all 40 bars and the best-match tick, and the full graph with all 1023 scores. The scores were already worked out by Python, using `signal.correlate`, when the picture last updated. The search only shows them.

```js
    if (atOnce) { clearTimeout(revealTimer); setReveal("done"); } else startReveal(); // keyboard actions are never animated
```
A keyboard press shows the finished graphs at once (after cancelling any timer), without an animation. A mouse or touch press starts the left-to-right reveal.

```js
    updateRealMarks();
```
After a search, the real delay is shown.

```js
    say(el.msgSearch, `The phone tried all 1023 shifts. Its best match is at shift ${result.best_delay_chips}.`);
```
Shows a message under the button and flashes it, for example "The phone tried all 1023 shifts. Its best match is at shift 14." It is in a line that a screen reader announces, which tells a listener what happened.

```js
  }
```
Closes `search`.

```js
  function reducedMotion() {
    return window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  }
```
Asks the browser whether the reader has set their device to avoid animation. It answers `true` or `false`.

```js
  function setReveal(state) {
    el.closeupRestWrap.dataset.reveal = state;
    el.fullWrap.dataset.reveal = state;
  }
```
Sets the `data-reveal` label of the two graph boxes to a state: `"hidden"`, `"running"` or `"done"`. The CSS rules turn each state into a clip: nothing shown, a smooth growth to everything, or no clip.

```js
  // The plots are drawn left to right over about a second. The numbers are already on the page.
```
A comment. The reveal is only a show. The readout numbers are already there, and the graph's data is already drawn underneath the clip.

```js
  function startReveal() {
```
Starts the function that plays the reveal.

```js
    clearTimeout(revealTimer);
```
Cancels any earlier timer, so two reveals do not overlap.

```js
    if (reducedMotion()) { setReveal("done"); return; }
```
If the reader wants no animation, show the finished graphs at once and stop.

```js
    setReveal("hidden");
```
Starts from the hidden state.

```js
    void root.offsetWidth; // let the browser see "hidden" first, so the change to "running" animates
```
Reading `offsetWidth` forces the browser to apply the hidden state before moving on (`void` throws the number away). If this were skipped, the browser would merge the two changes and show no animation.

```js
    setReveal("running");
```
Switches to the running state, which the CSS smoothly grows over one second.

```js
    revealTimer = setTimeout(() => setReveal("done"), signalConfig.revealMs);
```
`setTimeout` runs a function after a delay. After 1000 ms it sets the state to `done`, which removes the clip for good. The timer's number is kept in `revealTimer` so it can be cancelled.

```js
  }
```
Closes `startReveal`.

```js
  function finishReveal() {
```
Starts the function that ends the reveal early.

```js
    if (!searched || el.fullWrap.dataset.reveal !== "running") return;
```
Only act if the search was pressed and the reveal is running right now.

```js
    clearTimeout(revealTimer);
    setReveal("done");
```
Cancels the timer and jumps to the finished state.

```js
  }
```
Closes `finishReveal`.

### One run: ask Python, then draw

```js
  // ---------- one run: ask Python, then draw ----------
```
A section marker.

```js
  // Python calls are async. If one is running, remember that a newer run is wanted and do it once after.
```
A comment. A call to Python takes a moment, and the page must not freeze while it waits. That is what "async" (asynchronous) means: start the job, carry on, come back when it is done. If the reader keeps dragging the noise slider, the file does not start a pile of calls; it remembers that one more is wanted and does just one after the current one.

```js
  async function update() {
```
Starts a function called `update`.

```js
    if (!callPython || !code) return;
```
If Python is not ready yet, or the satellite's pattern has not arrived (`!` means "not"), stop at once. `return` leaves the function. Without it a drag before loading would try to use a function that does not exist.

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
Tells the reader in plain words, in the message line under the noise slider. Without it a failure would be silent.

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
Takes three settings out of `signalConfig`: 7, 14 and 1.

```js
    const usedNoise = noise; // the slider may move while Python works
```
Copies the noise now. If the slider moves while Python is busy, `noise` changes, but this run keeps drawing for the value it asked for. Without the copy, the picture could show one noise value in the graph and a different one in the words.

```js
    el.msgSlider.textContent = "";
```
Clears the message line under the noise slider (an earlier error), because a new run is starting.

```js
    const heard = await callPython("signal.make_received", [prn, trueDelayChips, usedNoise, seed]);
```
Asks Python to run `make_received` from `mechanism/signal.py` (see [signal.py](../mechanism/signal.py.md)), giving it the satellite number, the delay in chips, the noise size and the seed, and waits. Python shifts the satellite's pattern later by 14 chips and adds random noise of that size. It returns a list of 1023 numbers: what the phone hears. Without this line there would be nothing to draw.

```js
    if (failed(heard)) return;
```
If Python answered with an error message instead of numbers, show it and give up on this run (see `failed` below).

```js
    const scored = await callPython("signal.correlate", [heard, prn]);
```
Asks Python's `correlate` function to try all 1023 shifts of the satellite's pattern against what was heard and score each one. It sends the heard signal and the satellite number. It returns `scores` (1023 numbers, one per shift), `best_delay_chips` (the shift with the best score) and `peak_to_next` (how many times better the best score is than the second best).

```js
    if (failed(scored)) return;
```
The same check for the second answer.

```js
    requestAnimationFrame(() => {
```
`requestAnimationFrame` asks the browser to run a function just before it next paints the screen. Drawing then happens at the right moment, which avoids flicker and wasted work.

```js
      received = heard;
      result = scored;
```
Only now, inside that function, are the new answers stored in the variables the drawing code reads. Doing it here keeps the stored answers and the screen in step: the picture never shows new numbers with old graphs.

```js
      drawAll(usedNoise);
    });
```
Draws everything for this noise value. Without this the numbers would never reach the screen. Then the end of the function given to `requestAnimationFrame`.

```js
  }
```
Closes `runOnce`.

```js
  function failed(answer) {
```
Starts a helper that says whether Python's answer was an error.

```js
    if (!answer || !answer.error) return false;
```
If there is no answer at all, or the answer has no `error` part, it is not a failure, so answer `false` ("no, it did not fail"). Python returns an object with an `error` sentence when its input was wrong.

```js
    say(el.msgSlider, answer.error); // Python's own plain sentence
```
Otherwise show Python's sentence in the message line under the noise slider. The mechanism writes these sentences in plain words, so the page does not rewrite them.

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
  function levelOf(scored) {
```
Starts a function that turns Python's answer into one of three levels: `"ok"`, `"warn"` or `"bad"`.

```js
    if (scored.best_delay_chips !== signalConfig.trueDelayChips) return "bad";
```
If the best shift is not 14 (`!==` means "is not equal to"), the phone picked the wrong place: the level is "bad". Without it a wrong answer would be shown as a success.

```js
    return scored.peak_to_next < signalConfig.barelyHoldingBelow ? "warn" : "ok";
```
Otherwise the phone found the right place, and the level depends on how clearly. Worked examples: `peak_to_next` 1.2 is under 1.5, so "warn"; 12.4 is not, so "ok".

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

```js
  function formatScore(value) {
```
Starts a function that turns a match score into words for the readout.

```js
    const text = value.toFixed(2);
```
The score to two decimal places. Worked example: 0.9567 becomes "0.96".

```js
    return text === "-0.00" ? "0.00" : text;
```
A tiny negative score such as -0.003 would print as "-0.00", which looks odd. This swaps that one case for "0.00". Anything else is returned as it was.

```js
  }
```
Closes `formatScore`.

```js
  function chips(count) {
    return count === 1 ? "1 chip" : `${count} chips`;
  }
```
Writes a number of chips in words with the right singular or plural: "1 chip", "0 chips", "14 chips".

### Drawing

```js
  // ---------- drawing ----------
```
A section marker.

```js
  function drawAll(usedNoise) {
```
Starts the function that puts a whole run's results on the screen. It gets the noise that was used.

```js
    drawRows(usedNoise);
    drawHand();
    drawCloseup();
```
Redraws the three rows, then the match score for the current shift, then the close-up graph.

```js
    if (searched) { drawFull(); drawResult(); }
```
Only if the search has been pressed, also draws the full graph and the readout. So if the reader moves the noise slider after searching, the graphs and numbers update; before searching they stay unrevealed.

```js
    placeAllLabels();
```
Re-places the words of the tick marks, since the graphs may have changed.

```js
    // Noise peaks regularly pass the heard row's edge once the noise is more than half the row's range.
```
A comment giving the reason for the next lines.

```js
    el.clipNote.textContent = usedNoise * 2 > signalConfig.receivedLimit
      ? "The noise is now taller than the heard row, so its peaks are cut off at the top and bottom." : "";
```
Writes a warning when the noise is large and leaves it empty otherwise. Worked example: the limit is 2, so `usedNoise * 2 > 2` means noise above 1. Noise 3.5 gives 7 > 2, so the warning shows; noise 0.5 gives 1, not above 2, so the line is empty. The heard row shows -2 to +2 and noise swings both ways, so large noise runs off its edge. Without it a reader might think the flat tops were the real signal. (A statement may continue on the next line.)

```js
  }
```
Closes `drawAll`.

```js
  // A square wave: each value is held for one step.
```
A comment describing `stepPoints`: each value is drawn as a flat stretch the width of one chip, with a vertical jump between neighbours.

```js
  function stepPoints(values, mid, unit) {
```
Starts the function. It gets the list of values, the height of the row's middle line, and how many picture units one unit of value takes.

```js
    const parts = [];
```
An empty list to collect the corner points.

```js
    values.forEach((value, index) => {
```
`forEach` goes through a list and runs the function for every item. Here `value` is the number and `index` is its place in the list, starting at 0.

```js
      const y = (mid - value * unit).toFixed(1);
```
The height for this value. Screens count y downwards from the top, so a bigger value means a smaller y: the value times `unit` is taken away from the middle line. Worked example (the sent row, middle 38, unit 18 / 2 = 9): a value of +1 gives 38 - 9 = 29.0, higher up; -1 gives 38 + 9 = 47.0, lower down. `toFixed(1)` keeps one decimal place and gives text.

```js
      parts.push(`${index * CHIP},${y} ${(index + 1) * CHIP},${y}`);
```
Adds two points to the list: the start and the end of this chip's flat stretch, at the same height. Worked example: chip 3 at height 29.0 gives "30,29.0 40,29.0". The next chip's start has the same x as this chip's end, so the line steps up or down there.

```js
    });
    return parts.join(" ");
  }
```
Closes the loop, joins all the points into one text with a space between them (the format the `points` attribute of a `polyline` needs), and closes the function.

```js
  function copyValue(index) {
    return code[(((index - shift) % CODE_LENGTH) + CODE_LENGTH) % CODE_LENGTH];
  }
```
The value of the phone's copy at a given position in the row. Sliding the copy right by `shift` chips means that position `index` shows the pattern's value `index - shift` places back. Worked example: with a shift of 5, position 7 shows `code[2]`, and position 3 shows `code[-2]`, which does not exist. The pattern repeats, so position -2 means 1021, which is how the maths wraps: `%` is the remainder after dividing, and adding `CODE_LENGTH` before the second `%` turns any negative remainder into the matching positive place. (-2 + 1023) % 1023 = 1021. Without this, a slid copy would show blanks at the left.

```js
  function drawRows(usedNoise) {
```
Starts the function that draws the three rows.

```js
    const { windowChips, receivedLimit } = signalConfig;
```
Takes out two settings: 40 chips shown, and the limit of 2.

```js
    const unit = WAVE / receivedLimit;
```
How many picture units one unit of value takes: 18 / 2 = 9. A value of 2 reaches the full wave height of 18; a value of 1 reaches 9.

```js
    const sent = code.slice(0, windowChips);
```
The first 40 values of the satellite's pattern (`slice(0, 40)` takes items 0 to 39). This is the top row: what the satellite sends.

```js
    const heard = received.slice(0, windowChips).map((v) => Math.min(receivedLimit, Math.max(-receivedLimit, v)));
```
The first 40 values of what the phone hears, each cut off to the range -2 to +2. `map` builds a new list by running the function on every item. `Math.max(-2, v)` stops anything going below -2 and `Math.min(2, ...)` stops anything going above +2. Worked example: a heard value of 3.4 becomes 2; -0.7 stays -0.7. Without it big noise would be drawn outside the row.

```js
    el.sentLine.setAttribute("points", stepPoints(sent, ROW_MID.sent, unit));
    el.receivedLine.setAttribute("points", stepPoints(heard, ROW_MID.heard, unit));
```
Draws the top and middle rows. A `polyline` is an SVG shape: a line through many points, and its `points` attribute lists them. Without these lines the rows would stay empty.

```js
    shownNoise = usedNoise;
```
Remembers the noise these rows were drawn with, for the description a screen reader gets.

```js
    drawCopyRow();
```
Draws the bottom row too.

```js
  }
```
Closes `drawRows`.

```js
  // The copy row: each step is a block, lit where its sign agrees with the heard value above it, dim where it does not.
```
A comment. Each of the 40 steps of the copy row is a block. A block is bright where the copy and the heard signal are on the same side of zero (both positive, or both not), and dim where they disagree. When the copy is lined up, most blocks are bright; when it is far off, about half are.

```js
  function drawCopyRow() {
```
Starts the function that draws the bottom row.

```js
    if (!code || !received) return;
```
If the pattern or the heard signal has not arrived yet, there is nothing to draw.

```js
    const unit = WAVE / signalConfig.receivedLimit;
```
The block height again: 18 / 2 = 9.

```js
    let agree = 0;
```
A counter for how many steps agree. It starts at 0.

```js
    el.cells.forEach((cell, index) => {
```
Goes through the 40 blocks, one at a time.

```js
      const value = copyValue(index);
```
The copy's value (+1 or -1) at this position, for the current shift.

```js
      const lit = (value > 0) === (received[index] > 0);
```
Compares two yes/no answers: is the copy's value above 0, and is the heard value above 0? If both answers are the same, `lit` is true. Worked example: copy +1 and heard 0.8 are both above 0, so lit. Copy +1 and heard -1.3 differ, so not lit. This is the only comparison done in JavaScript; it only chooses a shade.

```js
      if (lit) agree += 1;
```
If it agrees, add 1 to the counter.

```js
      cell.setAttribute("y", value > 0 ? ROW_MID.copy - unit : ROW_MID.copy);
```
Places the block. For +1 it sits above the middle line (its top at 162 - 9 = 153, so it fills from 153 to 162). For -1 it sits below (from 162 to 171).

```js
      cell.classList.toggle("is-dim", !lit);
```
`toggle` adds the class `is-dim` when the second value is true and removes it when it is false. So the block is dim exactly when it is not lit.

```js
    });
```
Closes the loop.

```js
    const x = shift * CHIP;
```
The sideways distance the copy has been slid, in picture units: 5 chips is 50.

```js
    el.bracket.style.display = shift === 0 ? "none" : "";
```
Hides the bracket when the shift is 0 (there is nothing to measure) and shows it otherwise. An empty text gives back the normal display.

```js
    el.bracketLine.setAttribute("d", `M0,196 V200 H${x} V196`);
```
Draws the bracket as a path. In SVG the `d` attribute is a list of drawing commands: `M0,196` move to the left end at height 196, `V200` go straight down to 200, `H` + x go sideways to x, `V196` go back up to 196. That makes a square bracket spanning the slid distance.

```js
    const flip = shift > 22; // near the right edge the words sit left of the bracket end
```
Whether to put the bracket's words on the other side. When the shift is more than 22 chips, the words would run off the right edge, so they are placed to the left of the bracket's end.

```js
    el.bracketText.setAttribute("x", flip ? ROWS_W : x + 6);
    el.bracketText.setAttribute("text-anchor", flip ? "end" : "start");
```
Positions the words. Normally they start 6 units right of the bracket's end. When flipped, they end at the right edge of the picture (`text-anchor` says which end of the words sits at that position).

```js
    el.bracketText.textContent = `slid ${chips(shift)}`;
```
Writes the words, for example "slid 5 chips".

```js
    const noiseWords = shownNoise ? `${shownNoise.toFixed(1)} times the signal` : "none";
```
The noise in words for the screen reader. A noise of 0 counts as "no" (false), so it reads "none"; otherwise, for example, "3.5 times the signal".

```js
    el.rows.setAttribute("aria-label",
      `Three rows of ${signalConfig.windowChips} steps. Top: what the satellite sends. Middle: what the phone hears, noise ${noiseWords}. `
      + `Bottom: the phone's own copy, slid ${chips(shift)}; ${agree} of ${signalConfig.windowChips} steps agree with what the phone hears.`);
```
Updates the description that a screen reader gives for the rows picture, for example: "Three rows of 40 steps. Top: what the satellite sends. Middle: what the phone hears, noise none. Bottom: the phone's own copy, slid 5 chips; 22 of 40 steps agree with what the phone hears." The `+` joins the two lines of text. This gives a listener the same information a sighted reader gets from the bright and dim blocks.

```js
  }
```
Closes `drawCopyRow`.

```js
  function drawHand() {
```
Starts the function that updates everything about the hand-slid copy: the row, the words, and the match score.

```js
    drawCopyRow();
    el.shiftValue.textContent = chips(shift);
```
Redraws the bottom row for the current shift, and writes the slide in words next to the slider ("5 chips").

```js
    if (!result) return;
```
If Python has not given scores yet, stop here.

```js
    const score = result.scores[shift];
```
Looks up the score for this shift in the list Python returned. This is the point of the design: no new call to Python, just reading item number `shift`. The score is for the whole 1023-step pattern, not only the 40 steps shown.

```js
    el.handScore.textContent = formatScore(score);
```
Writes the score, for example "0.96".

```js
    el.meter.style.transform = `scaleX(${Math.min(1, Math.max(0, score))})`;
```
Sets how full the meter bar is. The score is cut off to between 0 and 1, then used as the `scaleX` stretch factor: 0 is an empty bar, 0.5 is half, 1 is full. Worked example: a score of 0.96 fills 96 percent of the bar; a score of -0.04 is cut to 0, so the bar is empty.

```js
    el.shift.setAttribute("aria-valuetext", `Copy slid ${chips(shift)}. Match score ${formatScore(score)}.`);
```
What a screen reader says for the sliding slider, instead of a bare position number: "Copy slid 5 chips. Match score 0.12."

```js
    el.handSentence.textContent = shift === signalConfig.trueDelayChips
      ? `Lined up. You slid the copy ${chips(shift)}, so the signal arrived ${chips(shift)} late.`
      : "Not lined up yet. Keep sliding.";
```
A sentence that depends on whether the copy is exactly at the real delay (14). If so, "Lined up. You slid the copy 14 chips, so the signal arrived 14 chips late." If not, "Not lined up yet. Keep sliding." This is where the reader learns the main idea: how far the copy had to slide is how late the signal arrived.

```js
  }
```
Closes `drawHand`.

```js
  // The readout, once the search has been pressed.
```
A comment: this function fills in the results box, but is only used once the search has been pressed.

```js
  function drawResult() {
```
Starts the function that fills in the results box.

```js
    const level = levelOf(result);
```
Works out the level (`"ok"`, `"warn"` or `"bad"`) once, and uses it below.

```js
    el.emptyLine.hidden = true;
```
Hides the "Press the button and the phone searches." line, because there is a result now.

```js
    el.bestDelay.textContent = chips(result.best_delay_chips);
```
Writes the best delay Python found, for example "14 chips".

```js
    el.trueDelay.textContent = chips(signalConfig.trueDelayChips);
```
Writes the real delay, "14 chips". It is only shown now, after the search, so that it does not give the answer away earlier.

```js
    el.peak.textContent = formatPeak(result.peak_to_next);
```
Writes how many times better the best score is than the runner-up, for example "12.3×".

```js
    el.badge.hidden = false;
```
Shows the badge (it starts hidden, because before the first search it has nothing to say).

```js
    el.badge.className = `badge is-${level}`;
```
Sets all the badge's classes at once: `badge` (its shape) plus the colour class. This replaces the old colour. A class is a label that CSS rules can match, and the shared rules in [`theme.css`](theme.css.md) give `is-ok`, `is-warn` and `is-bad` green, amber and red.

```js
    el.badge.textContent = levelWords[level];
```
Writes "Found", "Barely found" or "Lost". Square brackets pick the entry named by `level` from the object `levelWords`.

```js
    el.sentence.textContent = sentenceFor(level, noise);
```
Writes the one-sentence explanation. It is in a `role="status"` line, which a screen reader announces when it changes. It uses the current `noise`, because the readout is only drawn when the picture is current.

```js
  }
```
Closes `drawResult`.

```js
  function scoreY(value, height) {
```
Starts a function that turns a score into a height on a graph of a given height. Both graphs use it.

```js
    const { min, max } = signalConfig.scoreRange;
```
The range of scores shown: -1.25 to 1.5.

```js
    const clamped = Math.min(max, Math.max(min, value));
```
Cuts the value off to the range. `Math.max(min, value)` takes the bigger of the two, so nothing goes below `min`. `Math.min(max, ...)` takes the smaller, so nothing goes above `max`. Worked example: a score of 2 becomes 1.5; a score of -3 becomes -1.25.

```js
    return height - ((clamped - min) / (max - min)) * height;
```
Turns the value into a height. `(clamped - min) / (max - min)` is how far along the range the value is, from 0 to 1. Times the graph's height gives a distance from the bottom. Screens count y downwards from the top, so the result is taken away from the height to flip it. Worked example (height 120, span 1.5 - (-1.25) = 2.75): a score of 1.0 gives (1.0 + 1.25) / 2.75 = 0.818; 0.818 x 120 = 98.2; y = 120 - 98.2 = 21.8, near the top. A score of 0 gives 1.25 / 2.75 = 0.4545, so y = 120 - 54.5 = 65.5.

```js
  }
```
Closes `scoreY`.

```js
  function bars(shifts) {
```
Starts a function that makes the bars of the close-up graph for a list of shifts. A bar rises from the zero line up for a positive score and falls from it down for a negative one.

```js
    const zero = scoreY(0, CLOSEUP_HEIGHT);
```
The height of the zero line in the close-up (a score of 0): (0 + 1.25) / 2.75 x 96 = 43.6 from the bottom, so y = 96 - 43.6 = 52.4.

```js
    return shifts.map((index) => {
```
For each shift in the list, builds the text of one bar and keeps it in a new list.

```js
      const y = scoreY(result.scores[index], CLOSEUP_HEIGHT);
```
The height of this shift's score.

```js
      return `<rect class="bar" x="${index * CHIP + 1}" y="${Math.min(zero, y).toFixed(1)}" width="${CHIP - 2}" height="${Math.max(1, Math.abs(zero - y)).toFixed(1)}"/>`;
```
The text of one bar (an SVG `rect`). It sits at `index * 10 + 1` from the left and is `10 - 2 = 8` wide, so bars have gaps between them. Its top is the smaller of the zero line's y and the score's y (smaller y means higher up), so it grows up for a positive score and starts at the zero line going down for a negative one. Its height is the distance between those two heights, but at least 1 so that a score of nearly zero still leaves a visible sliver.

```js
    }).join("");
```
Closes the `map` and joins all the bar texts into one, with nothing between them.

```js
  }
```
Closes `bars`.

```js
  // The first 40 shifts, close up. Before the search it holds only the shifts the user stopped on.
```
A comment. This graph shows the scores of shifts 0 to 39 as bars. Before the search it shows only the shifts the reader has tried by hand. After the search it shows all 40.

```js
  function drawCloseup() {
```
Starts the function that draws the close-up graph.

```js
    if (!result) return;
```
If there are no scores yet, stop.

```js
    const all = Array.from({ length: signalConfig.windowChips }, (_, index) => index);
```
Makes the list 0, 1, 2, ... 39. `Array.from` builds a list of a given `length`, and the small function turns each place into its own number (the `_` is a name for a value that the function does not use).

```js
    el.closeupTries.innerHTML = bars([...visited].filter((index) => index < signalConfig.windowChips));
```
Draws the bars the reader earned by hand. `[...visited]` turns the set of tried shifts into a list, `filter` keeps only those under 40 (the close-up's width), and `bars` makes the text for them. These go into the overlay drawing, which sits on top.

```js
    el.closeupRest.innerHTML = searched ? bars(all) : "";
```
After the search, draws the bars for all 40 shifts in the other drawing (the one that the reveal animation uncovers). Before the search it is emptied.

```js
    const best = result.best_delay_chips;
```
The best shift Python found.

```js
    const inside = searched && best < signalConfig.windowChips;
```
Whether the best match is worth marking in the close-up: the search must have been pressed, and the best shift must be one of the first 40.

```js
    el.closeupBestTick.toggleAttribute("hidden", !inside);
    el.closeupBestLabel.hidden = !inside;
```
Shows the best-match tick and its words when `inside` is true and hides them otherwise. `toggleAttribute` adds the attribute when the second value is true and removes it when false.

```js
    if (inside) {
      setLevelClass(el.closeupBestTick, levelOf(result));
      placeTick(el.closeupBestTick, el.closeupBestLabel, (best + 0.5) / signalConfig.windowChips);
    }
```
If it is inside, colours the tick by the result (green, amber or red) and places it in the middle of that shift's bar. Worked example: best 14 gives (14 + 0.5) / 40 = 0.3625.

```js
    if (!searched) el.closeupNote.textContent = CLOSEUP_PROMPT;
    else el.closeupNote.textContent = inside ? "" : `The phone's best match is now at shift ${best}, outside this close-up.`;
```
The line under the graph. Before the search it is the starting prompt. After it, it is empty when the best match shows in the close-up. Otherwise it says where it moved to: after enough noise the best shift can jump to a place beyond the first 40.

```js
    const words = searched
      ? `Best match at shift ${best}; the real delay is ${signalConfig.trueDelayChips}.`
      : `Not searched yet; ${visited.size} shifts tried by hand.`;
```
The words for a screen reader about the state: after the search, where the best match is and what the real delay is; before it, how many shifts the reader has tried (`visited.size` counts the set's items).

```js
    el.closeupTries.parentElement.setAttribute("aria-label", `Close-up of the match score at the first ${signalConfig.windowChips} shifts. ${words}`);
```
Sets the description of the overlay drawing (the parent of the group of bars) to a fixed sentence plus those words.

```js
  }
```
Closes `drawCloseup`.

```js
  // All 1023 shifts.
```
A comment: the next function draws the full graph.

```js
  function drawFull() {
```
Starts the function that draws the full graph.

```js
    if (!result) return;
```
If there are no scores yet, stop.

```js
    el.scoresLine.setAttribute("points", toPoints(result.scores));
```
Draws the line through all 1023 scores (see `toPoints`).

```js
    setLevelClass(el.fullBestTick, levelOf(result));
```
Colours the best-match tick by the result.

```js
    el.fullBestTick.removeAttribute("hidden");
    el.fullBestLabel.hidden = false;
```
Shows the best-match tick and its words.

```js
    placeTick(el.fullBestTick, el.fullBestLabel, result.best_delay_chips / CODE_LENGTH);
```
Places the tick at the best shift, as a fraction of the 1023 shifts. Worked example: shift 14 gives 14 / 1023 = 0.0137 of the way along.

```js
    el.fullSvg.setAttribute("aria-label",
      `${SCORES_LABEL} Best match at shift ${result.best_delay_chips}; the real delay is ${signalConfig.trueDelayChips}.`);
```
Updates the description of the full graph for a screen reader: the fixed words, then "Best match at shift 14; the real delay is 14." This is the information a sighted reader gets by looking at where the peak is.

```js
  }
```
Closes `drawFull`.

```js
  function setLevelClass(node, level) {
    node.classList.remove("is-ok", "is-warn", "is-bad");
    node.classList.add(`is-${level}`);
  }
```
Gives an element exactly one of the three colour classes. It removes all three, then adds the one that matches the level. The shared rules in [`theme.css`](theme.css.md) turn them into green, amber or red, and the tick's `currentColor` follows.

```js
  // One point per shift: x is the shift, y is the score scaled into the graph (cut off at the edges).
```
A comment describing `toPoints`: x is the shift number, y is the score turned into a height, and values outside the range are cut off.

```js
  function toPoints(values) {
    return values.map((value, index) => `${index},${scoreY(value, PLOT_HEIGHT).toFixed(1)}`).join(" ");
  }
```
Makes the `points` text for the full graph. `map` goes through the 1023 scores and, for each, writes "shift,height" with the height from `scoreY` to one decimal. `join(" ")` puts a space between them, which is the format a `polyline` needs, for example `"0,65.5 1,64.9 2,66.1"`. Because the graph's canvas is 1023 units wide, the shift number is already the right horizontal position, and no scaling is needed for x.

```js
  // The tick sits at its exact place (a percentage); its words are kept inside the plot's width.
```
A comment: the tick is placed by a percentage of the width, and its words are moved only as much as needed so they do not hang over either end of the plot.

```js
  function placeTick(tick, label, fraction) {
```
Starts a function that places a tick and its words. `fraction` is how far along the graph's width, from 0 to 1.

```js
    tick.dataset.at = String(fraction);
```
Stores the fraction in the tick's `data-at` label, so that `placeAllLabels` can redo the placing later (for example when the window is resized).

```js
    tick.style.left = `${fraction * 100}%`;
```
Puts the tick that far along its lane, as a percentage. Worked example: 0.3625 becomes "36.25%". A percentage follows the lane as the page changes size.

```js
    const lane = label.parentElement;
    const width = lane.clientWidth;
```
The lane that holds the words, and how wide it is on screen in pixels.

```js
    if (!width || label.hidden) return;
```
If the lane has no width yet (it is not shown), or the words are hidden, there is nothing to measure, so stop.

```js
    const labelWidth = label.offsetWidth;
```
How wide the words are on screen, in pixels.

```js
    label.style.left = `${Math.min(width - labelWidth, Math.max(0, fraction * width - labelWidth / 2))}px`;
```
Places the words, centred on the tick but kept inside the lane. `fraction * width - labelWidth / 2` is the position that centres them. `Math.max(0, ...)` stops them going off the left edge; `Math.min(width - labelWidth, ...)` stops them going off the right. Worked example: a lane 400 px wide, words 100 px wide, fraction 0.0137: the centred position would be 5.5 - 50 = -44.5, which is cut to 0, so the words sit at the left edge while the tick stays at its exact place.

```js
  }
```
Closes `placeTick`.

```js
  // The real delay is shown once the user has found it by hand or pressed the search, not before.
```
A comment: the real delay would give the answer away, so it is held back.

```js
  function updateRealMarks() {
```
Starts the function that decides whether to show the real-delay marks.

```js
    const show = searched || visited.has(signalConfig.trueDelayChips);
```
Show them if the search has been pressed, or the reader has stopped on shift 14 by hand (`visited.has(14)`).

```js
    for (const node of [el.closeupRealTick, el.closeupRealLabel, el.fullRealTick, el.fullRealLabel]) node.toggleAttribute("hidden", !show);
```
For each of the four real-delay elements (two ticks and their words), hides it when `show` is false and shows it when true.

```js
    if (show) placeAllLabels();
```
When they are shown, re-places the words, because words that were hidden had no measurable width before.

```js
  }
```
Closes `updateRealMarks`.

```js
  function placeAllLabels() {
```
Starts the function that re-places all four ticks' words.

```js
    for (const [tick, label] of [
      [el.closeupRealTick, el.closeupRealLabel], [el.closeupBestTick, el.closeupBestLabel],
      [el.fullRealTick, el.fullRealLabel], [el.fullBestTick, el.fullBestLabel],
    ]) if (tick.dataset.at) placeTick(tick, label, Number(tick.dataset.at));
```
A loop over four pairs of (tick, words). Each pair is taken apart into `tick` and `label` right in the loop heading. For each pair that has been placed before (it has a stored `data-at`), `placeTick` is run again with the stored fraction. `Number(...)` turns the stored text back into a number.

```js
  }
```
Closes `placeAllLabels`.

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

### The small sketch

```js
// ---------- the small drawing (fixed sketch, no numbers) ----------
```
A section marker. The three small pictures at the top of the section are a fixed sketch of the idea. They do not use any data from Python.

```js
const SKETCH_PATTERN = [1, -1, -1, 1, 1, -1, 1, -1, -1, 1, -1, 1]; // twelve steps, only for the sketch
```
A made-up pattern of twelve steps (+1 and -1), used only to draw the sketch. It is not the satellite's real code.

```js
const SKETCH_LATE = 3; // the late copy in the sketch is three steps late
```
In the sketch, the late copy is 3 steps late.

```js
function sketchWave(values, mid, unit, offset = 0) {
```
Starts a function that makes the `points` text of a square wave for the sketch. `offset = 0` means the offset is 0 unless the caller gives another value.

```js
  const parts = [];
```
An empty list to collect the points.

```js
  if (offset > 0) parts.push(`0,${mid} ${offset * 10},${mid}`);
```
If the wave starts late, first draw a flat line along the middle from the left edge to the start (10 units per step).

```js
  values.forEach((value, index) => {
```
Goes through the values, one by one.

```js
    const y = mid - value * unit;
```
The height for this value: up for +1, down for -1, on a screen where y counts downwards.

```js
    parts.push(`${(index + offset) * 10},${y} ${(index + offset + 1) * 10},${y}`);
```
Adds the flat stretch for this step, shifted along by the offset.

```js
  });
  return parts.join(" ");
}
```
Closes the loop, joins the points with spaces, and closes the function.

```js
function sketchHtml() {
```
Starts a function that returns the HTML of the three-picture sketch.

```js
  const wave = (points, extra = "") => `<polyline class="${extra}" points="${points}"/>`;
```
A small helper that makes the text of a wave line for the given points, with an optional extra class (the sketch uses `dim` for the grey copy).

```js
  const late = SKETCH_PATTERN.slice(0, SKETCH_PATTERN.length - SKETCH_LATE);
```
The pattern with its last 3 steps cut off (`slice` takes the first 9 steps). Shifted 3 steps right, it fits in the same width, like the pattern arriving late.

```js
  return `
  <div class="sketch">
```
Starts the returned text (between backticks) and the outer box of the sketch.

```js
    <div><svg class="figure" viewBox="0 0 120 40" role="img" aria-label="Sketch: the satellite's pattern, a row of high and low steps.">${wave(sketchWave(SKETCH_PATTERN, 20, 8))}</svg><p>1 The pattern</p></div>
```
Picture 1: the pattern as sent. An `svg` is a drawing area, 120 units wide and 40 high (`viewBox`). `role="img"` and `aria-label` tell a screen reader it is one picture and what it shows. The wave is made by `sketchWave`, with its middle line at 20 and 8 units per step. Under it the caption "1 The pattern".

```js
    <div><svg class="figure" viewBox="0 0 120 40" role="img" aria-label="Sketch: the same pattern arriving a few steps late.">${wave(sketchWave(late, 20, 8, SKETCH_LATE))}</svg><p>2 It arrives late</p></div>
```
Picture 2: the same pattern arriving 3 steps late (offset of `SKETCH_LATE`). Caption "2 It arrives late".

```js
    <div><svg class="figure" viewBox="0 0 120 40" role="img" aria-label="Sketch: the phone's copy slid until it lines up with the late pattern.">${wave(sketchWave(late, 11, 6, SKETCH_LATE), "dim")}${wave(sketchWave(late, 29, 6, SKETCH_LATE))}</svg><p>3 Slide your copy until it lines up</p></div>
```
Picture 3: two waves, one above the other, at the same offset, lined up: the first (grey, from the `dim` class) is the phone's copy, the second is the late signal. Caption "3 Slide your copy until it lines up".

```js
  </div>`;
}
```
Closes the sketch box, ends the text, and closes the function.

### The rows and the ticks

```js
function rowsHtml() {
```
Starts a function that returns the HTML of the three-rows picture.

```js
  const rowName = (name, y) => `<text class="row-name" x="0" y="${y}">${name}</text>`;
```
A helper that makes the text of a row's name: an SVG `text` at the left edge (x of 0) and a height `y`.

```js
  return `
  <svg class="rows" data-el="rows" viewBox="0 0 ${ROWS_W} 212" role="img" aria-label="Three rows of steps.">
```
Starts the returned text and the drawing: 400 units wide and 212 high, treated as one picture by a screen reader (`drawCopyRow` later replaces the starting description with a live one). `${ROWS_W}` puts the number 400 into the text.

```js
    ${rowName("What the satellite sends", 11)}
    <polyline class="sent" data-el="sent-line" points=""/>
```
The name of the top row, then the empty line that `drawRows` fills with the sent wave.

```js
    ${rowName("What the phone hears", 73)}
    <polyline class="received" data-el="received-line" points=""/>
```
The name of the middle row, then its empty line.

```js
    ${rowName("The phone's own copy", 135)}
    <g data-el="copy-cells"></g>
```
The name of the bottom row, then an empty group (`g`) that `buildStaticParts` fills with the 40 blocks.

```js
    <rect class="copy-outline" x="-1" y="${ROW_MID.copy - 16}" width="${ROWS_W + 2}" height="32" rx="3"/>
```
The outline round the copy row: a rectangle starting 1 unit left of the picture and 16 above the row's middle line, 402 wide and 32 high, with slightly rounded corners (`rx`). The CSS makes it visible only during guide step 1.

```js
    <g data-el="bracket"><path class="bracket" data-el="bracket-line" d=""/><text class="bracket-text" data-el="bracket-text" y="207"></text></g>
```
A group with the bracket's line (an empty path that `drawCopyRow` fills) and its words (at height 207, empty for now).

```js
    <rect class="copy-hit" data-el="copy-hit" x="0" y="${ROW_MID.copy - 32}" width="${ROWS_W}" height="64"/>
  </svg>`;
}
```
The invisible rectangle that catches dragging: the whole width of the picture, 64 high, centred on the copy row (a bit taller than the row, so it is easy to grab). It comes last, so it sits on top of the others. Then the end of the drawing, of the text, and of the function.

```js
// A tick above (real delay) or below (the phone's best match) a plot, with its words.
```
A comment describing the next function.

```js
function laneHtml(where, name, words, markClass) {
```
Starts a function that returns the HTML of one lane. `where` is `"top"` or `"bottom"`, `name` is the start of the `data-el` labels, `words` is the label text, and `markClass` picks the tick's line style.

```js
  return `<div class="lane lane-${where}"><span class="tick-label" data-el="${name}-label" hidden>${words}</span>
```
The lane box, with the words in a `span`. It starts `hidden`; the code shows it at the right moment. The label's name is for example `closeup-real-label`.

```js
    <svg class="tick ${where === "bottom" ? "is-ok" : ""}" data-el="${name}-tick" aria-hidden="true" hidden><line class="${markClass}" x1="1" x2="1" y1="0" y2="12"/></svg></div>`;
}
```
The tick: a small drawing, hidden, with a vertical line 12 units tall. A tick in a bottom lane (the phone's best match) starts with the class `is-ok`, which gives it a colour until `setLevelClass` sets the real one. `aria-hidden="true"` hides it from screen readers, because the words and the graph's description say the same. Then the end of the lane and of the function.

### The HTML of the section

```js
const PAGE_HTML = `
```
Starts one long piece of text with the section's HTML (the tags that make up the page, see "An HTML tag" in [how to read code](../how-to-read-code.md)). It is a constant, used by `insertAdjacentHTML` above. It sits at the bottom, but it is only used when `mountSignalStep` is called, after the whole file has loaded, so it exists by then. The `${...}` parts put in the results of the helper functions above.

```js
<section class="signal-step" aria-labelledby="signal-title" data-guide="1">
```
The outer element for the whole section. `class="signal-step"` is what every CSS rule above starts with. `aria-labelledby="signal-title"` tells a screen reader that the heading with the id `signal-title` is the name of this section. `data-guide="1"` starts the guide on step 1.

```js
  <header class="intro">
    <p class="label part-label">Part 3 of 4</p>
    <h2 id="signal-title">How does the phone measure the time?</h2>
```
An introduction block. It holds a small label, "Part 3 of 4", and the main heading, `h2`, with the id that the line above points to. The words "How does the phone measure the time?" are shown to the reader.

```js
    <p class="muted">Every satellite repeats a pattern the phone already knows. The phone slides its own copy along what it hears. How far it has to slide is how late the signal arrived.</p>
    <p class="hint" data-el="hint" hidden></p>
  </header>
```
A paragraph (`p`), in the grey `muted` style, that explains the idea in three sentences. Then the guide hint, empty and `hidden` for now (`showGuide` fills and shows it). Then the end of the introduction.

```js
  <div class="grid">
    <div class="card">
      <h3 class="label">Try it by hand</h3>
```
`div` is a plain box. The outer box is the `grid` (two columns on a wide screen). The first inner box is the left `card`: the by-hand part and the graphs. It starts with a small heading, "Try it by hand".

```js
      <p class="looking"><b>What you're looking at:</b> 40 steps of one satellite's pattern (the whole pattern has 1023). Top: what the satellite sends. Middle: what the phone hears, a little later. Bottom: the phone's own copy. Slide it.</p>
```
A paragraph that tells the reader what the three rows are. `<b>` makes the first words bold.

```js
      ${sketchHtml()}
      ${rowsHtml()}
      <p class="key muted" data-el="clip-note" role="status" aria-live="polite"></p>
```
The three-picture sketch, then the three rows, both made by the functions above. Then the empty paragraph that `drawAll` fills with the "cut off" warning. `role="status"` and `aria-live="polite"` tell a screen reader to read out new words here when it is quiet, without interrupting. Without them a listener would not hear the warning appear.

```js
      <div class="guide-block g1">
        <div class="slider-head"><label for="signal-shift">Slide the phone's copy</label><span class="num" data-el="shift-value">0 chips</span></div>
        <input id="signal-shift" data-el="shift" type="range" disabled>
      </div>
```
The box for guide step 1, `g1`. It has a `label` (the visible name of a form control) whose `for="signal-shift"` links it to the input with that `id`, so a click on the words also focuses the slider and a screen reader says the name for it. Next to it, in number style, the words "0 chips" that `drawHand` changes. Then the slider itself, an `input` with `type="range"`, the browser's built-in slider. `disabled` locks it from the start; `start` unlocks it when Python is ready; `setupControls` gives it its range.

```js
      <div class="inset readout">
        <div class="hand-score"><span class="label">Match score</span><span class="num big" data-el="hand-score">–</span></div>
        <div class="meter" aria-hidden="true"><div class="meter-fill" data-el="meter"></div></div>
```
The box for the match score. A row with the name "Match score" and the big number, a dash until the first result. Under it, the meter: a track with a fill inside. `aria-hidden="true"` hides the meter from screen readers, because they read the number.

```js
        <p class="note">Counted over the whole 1023-step pattern, not only the 40 steps shown. 1.00 means every step agrees. Near 0 means no better than chance. Noise can push it a little above or below.</p>
        <p class="note" data-el="hand-sentence" role="status" aria-live="polite">Not lined up yet. Keep sliding.</p>
      </div>
```
A note that explains how to read the score. Then the line where `drawHand` writes "Lined up..." or "Not lined up yet. Keep sliding.", announced politely by screen readers. Then the end of the box.

```js
      <p class="note">Here the delay is short so it fits in the picture. A real one can be anywhere in the 1023 steps.</p>
```
A note that is honest about the sketch: the 14-chip delay was chosen to fit.

```js
      <h3 class="label">Now let the phone search</h3>
      <div class="guide-block g2">
        <div><button class="btn" data-el="search" type="button" disabled>Let the phone try every shift</button></div>
        <p class="note" data-el="msg-search" role="status" aria-live="polite"></p>
      </div>
```
A new small heading, then the box for guide step 2, `g2`. It holds the search button. `type="button"` says that it does nothing by itself (a button without it could try to send a form). It starts `disabled`. Under it, the message line for "The phone tried all 1023 shifts...".

```js
      <p class="plot-title">Match score at each of the first 40 shifts</p>
      <div class="plot-lanes">
        ${laneHtml("top", "closeup-real", "real delay", "mark-true")}
```
The title of the close-up graph, then a box for the graph with its lanes. First comes the top lane, with the tick for the real delay.

```js
        <div class="plot-area plot-close">
          <div data-el="closeup-rest-wrap" data-reveal="hidden"><svg viewBox="0 0 ${ROWS_W} ${CLOSEUP_HEIGHT}" preserveAspectRatio="none" height="96" width="100%" aria-hidden="true"><g data-el="closeup-rest"></g></svg></div>
```
The close-up graph's box. Inside it is a wrapper that the reveal animation clips (it starts in the `hidden` state), and in it a drawing that will hold the bars for all 40 shifts. `viewBox` gives it 400 by 96 inside units. `preserveAspectRatio="none"` lets it stretch to fill its box instead of keeping its proportions. It is hidden from screen readers, which get the overlay's description.

```js
          <svg class="overlay" viewBox="0 0 ${ROWS_W} ${CLOSEUP_HEIGHT}" preserveAspectRatio="none" height="96" width="100%" role="img" aria-label="Close-up of the match score at the first 40 shifts."><g data-el="closeup-tries"></g></svg>
        </div>
```
The second drawing on top (`overlay`), with the same size, that holds the bars for the shifts tried by hand. This one is the picture a screen reader describes (`role="img"` and `aria-label`, updated by `drawCloseup`). Then the end of the graph's box.

```js
        ${laneHtml("bottom", "closeup-best", "phone's best match", "mark-best")}
      </div>
      <p class="note" data-el="closeup-note" role="status" aria-live="polite">${CLOSEUP_PROMPT}</p>
```
The bottom lane, with the tick for the phone's best match, then the end of the graph's box. Under it, the message line, which starts with the prompt "Each shift you try leaves a bar here."

```js
      <p class="plot-title">Match score at all 1023 shifts</p>
      <div class="plot-lanes">
        ${laneHtml("top", "full-real", "real delay", "mark-true")}
```
The title of the full graph, a box for it, and its top lane with the real delay tick.

```js
        <div class="plot-area plot-full" data-el="full-wrap" data-reveal="hidden">
          <svg data-el="scores-plot" viewBox="0 0 1023 ${PLOT_HEIGHT}" preserveAspectRatio="none" height="120" width="100%" role="img" aria-label="The match score at every one of the 1023 shifts."><polyline class="scores" data-el="scores-line" points=""/></svg>
        </div>
```
The full graph's box, with the reveal state (it starts hidden). Its drawing is 1023 units wide (one per shift) and 120 high, with the score line empty until `drawFull` fills it. Without `viewBox` the points would be placed in the wrong units.

```js
        ${laneHtml("bottom", "full-best", "phone's best match", "mark-best")}
      </div>
      <div class="axis" aria-hidden="true"><span>shift 0</span><span>shift 1022</span></div>
    </div>
```
The bottom lane with the best-match tick, then the end of the graph's box. Under it, the labels "shift 0" and "shift 1022", hidden from screen readers because the graph's description says it all. Then the end of the left card.

```js
    <div class="card stack">
      <h3 class="label">Then add noise</h3>
```
The right card: the noise controls and the results, stacked (and sticky on a wide screen). Its heading is "Then add noise".

```js
      <p class="note" data-el="status" role="status" aria-live="polite">Loading the maths…</p>
```
The status line. It starts with "Loading the maths…". [`startup.js`](startup.js.md) changes it as Python loads, and clears it when ready.

```js
      <div class="slider inset guide-block g3">
        <div class="slider-head">
          <label for="signal-noise">Add noise</label>
          <span class="num" data-el="noise-value">No noise</span>
        </div>
```
The box for guide step 3, `g3`, with three shared styles, and the row at its top: the label "Add noise" (linked to the slider below by `for="signal-noise"`) and the words that show the current noise ("No noise" at the start), in number style. `showNoiseValue` changes them.

```js
        <input id="signal-noise" data-el="noise" type="range" disabled>
        <p class="note" data-el="msg-slider" role="status" aria-live="polite"></p>
      </div>
```
The noise slider itself, locked from the start (`id="signal-noise"` is what the label points to), and the message line under it, announced politely by screen readers. Errors appear here. Then the end of the box.

```js
      <div class="inset readout">
        <span class="label">Best match found at</span>
        <span class="num big" data-el="best-delay">–</span>
```
The results box and its first small heading, "Best match found at", then the big number. It starts as a dash ("–") until the search is pressed.

```js
        <div class="readout-row"><span class="muted">Real delay</span><span class="num" data-el="true-delay">–</span></div>
        <div class="readout-row"><span class="muted">Best score is this many times the runner-up</span><span class="num" data-el="peak">–</span></div>
```
Two rows, each with a name on the left and a number on the right: "Real delay" (filled in by `drawResult`, "14 chips") and "Best score is this many times the runner-up" (also filled in by `drawResult`, for example "12.3×").

```js
        <div><span class="badge is-ok" data-el="badge" hidden></span></div>
```
The badge that says "Found", "Barely found" or "Lost". It starts hidden and empty. It sits in its own `div` so it does not stretch the full width.

```js
        <p class="note" data-el="empty-line">Press the button and the phone searches.</p>
        <p class="note" data-el="sentence" role="status" aria-live="polite"></p>
      </div>
```
The line shown before the first search, "Press the button and the phone searches.", then the line for the one-sentence explanation, announced politely. Then the end of the results box.

```js
      <div>
        <button class="btn" data-el="reset" type="button" disabled>Reset</button>
        <p class="note" style="margin-top: var(--s-2)" data-el="msg-reset" role="status" aria-live="polite"></p>
      </div>
```
The Reset button (`type="button"`, starts `disabled`) and the message line under it, with 8 px of space above it set by a `style` attribute, which puts a CSS rule on this one element. The "Back to the start: copy at 0, no noise." message goes here. Then the end of this box.

```js
    </div>
  </div>
</section>`;
```
Closes, in order: the right card, the grid and the section, then the backtick that ends the long text, and the semicolon that ends the line. Without any of these closings the page structure would be wrong, or the file would fail to load.
