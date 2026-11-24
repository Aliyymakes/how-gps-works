# illustrations.js, line by line

Source: `web/illustrations.js`

## What this file is for
This file draws one small picture: the strip above the first map. It shows a satellite, a dashed line with a pulse travelling along it, and a phone, with the words "travel time x speed of light = distance" and "one distance = one line on the map". It is a sketch only. It shows no measured numbers; every real number on the page comes from the Python mechanism. The drawing is made of SVG, a way of describing shapes as text that the browser draws sharply at any size.

## Which files it talks to
- [`index.html`](../index.html.md): imports `firstScreenFigure` and puts the result inside the element with the `id` `figure-first`. The styles named in the comments (`.figure`, `.dim`, `.fig-pulse`) and the rule that shows the narrow or the wide drawing live in its `<style>` part.
- It imports nothing from other files.

## In three lines
1. Small helper functions each return the text for one shape: a satellite, a phone, a dashed signal line with a pulse, an arrow with a short line, and a piece of writing.
2. `firstScreenFigure` joins these helpers into two complete pictures: a narrow one for phones and a wide one for larger windows.
3. The page shows one of the two and hides the other.

New to code? See [how to read code](../how-to-read-code.md).

## The code, line by line

```js
// Small sketches drawn with SVG. Each function returns a string of SVG markup; the page puts it in place.
// No numbers are drawn here: these are sketches, and the real numbers always come from the Python mechanism.
// Styles (.figure, .dim, .fig-pulse) live in index.html's style block.
```
Three comment lines (the computer ignores them). A "string of SVG markup" is plain text such as `<rect .../>` that the browser turns into a shape. They say that nothing here is a measurement, and that the looks (line colour, the moving pulse) are set in `index.html`.

```js
const WORDS = "Sketch: a signal travels from a satellite to a phone. Travel time times the speed of light is one distance, and one distance is one line on the map.";
```
Stores a sentence under the name `WORDS`. It is used as the spoken description of the picture for readers who use a screen reader, which cannot see drawings. `const` means the name will not change.

```js
// A satellite: a small box with two wings. (x, y) is the centre of the box.
function satellite(x, y) {
```
A comment, then a function (a named recipe) called `satellite`. It is handed two numbers: `x` is how far across the picture and `y` is how far down, where the satellite's centre goes.

```js
  return `<rect x="${x - 4}" y="${y - 4}" width="8" height="8"/>`
    + `<rect x="${x - 13}" y="${y - 2}" width="7" height="4"/><rect x="${x + 6}" y="${y - 2}" width="7" height="4"/>`;
}
```
`return` hands back the finished text. Backticks make a template string: text with holes, where `${x - 4}` is replaced by the result of that sum. `<rect>` is a rectangle with a left edge `x`, top edge `y`, `width` and `height`. The first one is the 8 by 8 body, drawn from 4 left and 4 above the centre so the centre is in the middle. The next two are the wings, 7 wide and 4 tall: one starts 13 to the left of the centre and one 6 to the right. The `+` joins the pieces of text into one. Without this function there would be no satellite.

```js
// A phone: a tall rounded rectangle. (x, y) is its top left corner.
function phone(x, y) {
```
A comment, then `phone`, which takes the position of the phone's top left corner.

```js
  return `<rect x="${x}" y="${y}" width="14" height="24" rx="3"/><line x1="${x + 5}" y1="${y + 19}" x2="${x + 9}" y2="${y + 19}"/>`;
}
```
Returns the text for two shapes. The first is a rectangle 14 wide and 24 tall whose corners are rounded by `rx="3"`. The second is a short line from 5 to 9 across and 19 down, near the bottom of the phone: the home bar. The brace ends the function.

```js
// A dashed line from one x to another with one short pulse that travels along it.
function signalLine(x1, x2, y) {
```
A comment, then `signalLine`. It gets where the line starts (`x1`), where it ends (`x2`) and how far down it sits (`y`).

```js
  const travel = x2 - x1;
```
Works out how long the line is (end minus start) and keeps it under the name `travel`. The pulse needs this to know how far to move.

```js
  return `<line class="dim" x1="${x1}" y1="${y}" x2="${x2}" y2="${y}" stroke-dasharray="4 4"/>`
    + `<circle class="fig-pulse" cx="${x1}" cy="${y}" r="3" style="--travel: ${travel}px"/>`;
}
```
Two shapes joined. The first is a straight line from `x1` to `x2` at height `y`. `class="dim"` gives it the quieter colour from the page styles, and `stroke-dasharray="4 4"` makes it dashed: 4 drawn, 4 empty. The second is a small circle (the pulse) of radius 3 (`r="3"`), placed at the start of the line. `class="fig-pulse"` is what the page style uses to make it travel. `--travel: ${travel}px` hands the style the line's length as a variable, so the pulse moves that far. Without this the signal would not be shown.

```js
// A small arrow, then a short straight line: one distance is one line on the map.
function arrowAndLine(arrowX, lineX1, lineX2, y) {
```
A comment, then `arrowAndLine`. It gets where the arrow starts (`arrowX`), where the line starts and ends (`lineX1`, `lineX2`) and the height `y`.

```js
  return `<path d="M${arrowX} ${y}h12m-4 -4l4 4l-4 4"/><line x1="${lineX1}" y1="${y}" x2="${lineX2}" y2="${y}"/>`;
}
```
A `<path>` draws by instructions in its `d` text: `M` moves to the start point, `h12` draws 12 across, `m-4 -4` lifts the pen 4 back and 4 up, `l4 4` draws down and right to the tip, and `l-4 4` draws down and left. Together these make an arrow pointing right. Then a plain straight line from `lineX1` to `lineX2` at the same height: a sketch of one line on the map. The brace ends the function.

```js
function text(x, y, words) {
```
A function called `text`. It takes a position and the `words` to write.

```js
  return `<text x="${x}" y="${y}">${words}</text>`;
}
```
Returns an SVG `<text>` element holding the words at that position. It exists so the pictures below can write words in one short call.

```js
// The strip above the first map. Two sizes: a narrow one for phones (64 px tall) and a wide one (96 px tall).
// The page shows one of them and hides the other (index.html).
export function firstScreenFigure() {
```
Two comments, then the function the page uses. `export` makes it available to other files, which bring it in with `import`. The comments say there are two sizes and the page shows one of them and hides the other. (The comment says the wide one is 96 px tall, but the wide drawing's own space below is 76 tall; this is recorded as written.)

```js
  const narrow = `<svg class="figure figure-narrow" viewBox="0 0 358 64" preserveAspectRatio="xMinYMid meet" role="img" aria-label="${WORDS}">`
```
Starts the narrow picture and keeps it under the name `narrow`. `<svg ...>` opens a drawing. `viewBox="0 0 358 64"` says the drawing's own space is 358 across and 64 down; the browser scales it to fit. `preserveAspectRatio="xMinYMid meet"` keeps the proportions and lines it up to the left. `role="img"` and `aria-label` tell screen readers it is one picture described by `WORDS`.

```js
    + satellite(14, 18) + signalLine(34, 138, 18) + phone(144, 6)
```
Adds the satellite with its centre at 14 across and 18 down, the dashed signal line from 34 to 138 across at height 18, and the phone with its top left corner at 144 across and 6 down. The line ends just left of the phone.

```js
    + text(0, 46, "travel time × speed of light") + text(0, 60, "= distance")
```
Writes the two lines of the first caption, on the left, 46 and 60 down.

```js
    + arrowAndLine(176, 198, 354, 18)
```
Adds the arrow starting at 176 and a line from 198 to 354, at height 18, to the right of the phone.

```js
    + text(198, 46, "one distance =") + text(198, 60, "one line on the map")
```
Writes the second caption under that line, starting at 198 across.

```js
    + `</svg>`;
```
Closes the drawing and ends the `const narrow` statement.

```js
  const wide = `<svg class="figure figure-wide" viewBox="0 0 640 76" preserveAspectRatio="xMinYMid meet" role="img" aria-label="${WORDS}">`
```
The same for the wide picture, `wide`: its own space is 640 across and 76 down, and its class is `figure-wide`, which the page styles use to show it only in larger windows.

```js
    + satellite(20, 28) + signalLine(46, 290, 28) + phone(296, 16)
```
The satellite, the long signal line and the phone, placed for the larger space. The signal line is much longer here (46 to 290), so the pulse has a long path.

```js
    + text(0, 66, "travel time × speed of light = distance")
```
Writes the first caption on one line, at the left.

```js
    + arrowAndLine(350, 380, 630, 28)
```
The arrow at 350 and the line from 380 to 630, at height 28.

```js
    + text(380, 66, "one distance = one line on the map")
```
Writes the second caption on one line, under the line.

```js
    + `</svg>`;
```
Closes the wide drawing.

```js
  return narrow + wide;
}
```
Hands back both drawings joined into one piece of text. The page puts it into the strip and its style rules show one and hide the other, so a phone gets the narrow one and a wider window gets the wide one. The brace ends the function.
