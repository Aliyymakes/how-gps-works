# format.js, line by line

Source: `web/format.js`

## What this file is for
This file holds three small tools that write numbers as text for the page. `formatMetres` turns a number of metres into text such as `1,235 m`; every metre readout uses it, so they all look the same. `formatRoughDistance` writes distances that must not look exact, such as `2.8 km`. `formatClockDigits` writes the two clock rows of the relativity section. They do no measuring and no maths of their own, only the writing of numbers.

## Which files it talks to
- [`web/first-screen.js`](first-screen.js.md), [`web/step-geometry.js`](step-geometry.js.md) and [`web/step-relativity.js`](step-relativity.js.md): each imports `formatMetres` and uses it for their metre readouts. Only [`web/step-relativity.js`](step-relativity.js.md) also imports `formatRoughDistance` and `formatClockDigits`. In [`web/step-geometry.js`](step-geometry.js.md) it writes the "Position off by" number.
- It uses nothing from other files. It uses `Intl.NumberFormat`, a number-writing tool that is built into every browser.

## In three lines
1. `formatMetres`: one decimal place under 100 m, a whole number from 100 m up, commas between thousands, then a space and `m`.
2. `formatRoughDistance`: under 1000 m it uses the rule above; from 1 km it writes kilometres, with one decimal under 10 km and whole kilometres from 10 km.
3. `formatClockDigits`: writes a ground clock and a satellite clock as `HH:00:00.000 000` text, the satellite one showing its tiny gap in microseconds.

New to code? See [how to read code](../how-to-read-code.md).

## The code, line by line

```js
// One rule for every metres readout: one decimal place below 100 m, whole metres from 100 m up,
// always with a thousands separator. The space before "m" cannot break across lines.
```
Two comment lines (a comment starts with `//`; the computer ignores it). They state the rule the function follows: under 100 m, one digit after the decimal point; from 100 m up, whole metres; always a comma between thousands. The comment says the space before the `m` "cannot break across lines", meaning the number and the `m` would stay together at the end of a line. Nothing breaks without the comments.

```js
export function formatMetres(m) {
```
Starts a function (a named recipe) called `formatMetres`. It is handed one number, called `m` here, which is a distance in metres. `export` makes it available to other files; they bring it in with `import`. Without `export`, no other file could use it.

```js
  const digits = new Intl.NumberFormat("en", { maximumFractionDigits: m < 100 ? 1 : 0 }).format(m);
```
This line writes the number as text. `Intl.NumberFormat` is the browser's built-in number writer. `"en"` asks for English style: a comma between thousands and a point for decimals. `maximumFractionDigits` is the most digits allowed after the decimal point. The part `m < 100 ? 1 : 0` reads "if `m` is less than 100, use 1, otherwise use 0". `.format(m)` then writes `m` using those settings, and the result is stored in a named box called `digits`. The writer rounds to the allowed digits, and it drops a trailing `.0`. Worked examples: `7.46` is under 100, so one decimal is allowed and it becomes `7.5`. `1234.6` is 100 or more, so no decimals are allowed: it rounds to 1235 and gets a comma, `1,235`. `0.04` becomes `0`. Without this line the page would show long raw numbers like `7.4612345678`.

```js
  return `${digits} m`;
```
Hands back the final text. The backticks make a template string: text with a hole, where `${digits}` is replaced by the number text from the line above. Between `${digits}` and the `m` there is a no-break space: it looks like an ordinary space, but it is a different character that never lets the line break there. Worked example: `digits` is `1,235`, so the result is `1,235 m`. Without this line the function would hand back nothing, and the readout would show the word `undefined`.

```js
}
```
Ends the function.

```js
// Rough distances for numbers that must never look exact (gotchas: "about 11 km"). Under 1000 m the metres
// rule above; from 1 km one decimal ("2.8 km"); from 10 km whole kilometres ("11 km"). The word "about" goes in the label.
```
Two comments for the next function. Some distances on the page are estimates, and writing them with many digits would pretend they are exact. So they are written roughly: under 1000 m the ordinary metres rule; from 1 km, kilometres with one decimal (`2.8 km`); from 10 km, whole kilometres (`11 km`). The word "about" is not added here; the label next to the number carries it. `gotchas` is the project's list of traps to avoid. Nothing breaks without the comments.

```js
export function formatRoughDistance(m) {
```
Starts a second function, `formatRoughDistance`. It is handed a distance `m` in metres, and `export` makes it available to other files.

```js
  if (m < 1000) return formatMetres(m);
```
An `if` is a question: "is `m` less than 1000?" If yes, the function hands back whatever `formatMetres` writes for it and stops, so `640` stays `640 m`. Without this line short distances would turn into `0.6 km`.

```js
  const km = m / 1000;
```
Divides by 1000 to change metres into kilometres and stores the result in a named box `km`. Worked example: `2840` becomes `2.84`.

```js
  return `${new Intl.NumberFormat("en", { maximumFractionDigits: km < 10 ? 1 : 0 }).format(km)} km`;
```
Writes `km` with the browser's number writer, as in `formatMetres`: one decimal allowed when `km` is under 10, none from 10 up. The text ` km` is added after it. Worked examples: `2840` m gives `2.8 km`; `11200` m gives `11 km`. Without this line the function would hand back nothing.

```js
}
```
Ends the function.

```js
// Clock digits written "HH:00:00.000 000". Whole hours come from the slider; the six decimals are millionths of a
// second. The ground row has none; the satellite row shows the gap in whole microseconds (for example "000 038").
```
Two comments. The relativity section shows two clocks as digits, like `24:00:00.000 038`. The part before the point is the hour (whole hours come from the slider). The six digits after the point are millionths of a second, in two groups of three. The ground clock has zero there; the satellite clock shows how far it has drifted, in whole microseconds. Nothing breaks without the comments.

```js
export function formatClockDigits(hours, gapMicroseconds) {
```
Starts a third function. It is handed two numbers: `hours` (the slider value) and `gapMicroseconds` (the clock gap in millionths of a second). `export` shares it with other files.

```js
  const start = `${String(hours).padStart(2, "0")}:00:00.`;
```
Builds the front of the text. `String(hours)` turns the number into text; `.padStart(2, "0")` adds a `0` in front if it is shorter than two characters, so `5` becomes `05`. Then `:00:00.` is added for the minutes, seconds and the point. Worked example: `24` gives `24:00:00.`, `5` gives `05:00:00.`.

```js
  const gap = String(gapMicroseconds).padStart(6, "0");
```
Turns the gap into text and pads it with zeros in front to six characters. Worked example: `38` becomes `000038`.

```js
  return { ground: `${start}000 000`, satellite: `${start}${gap.slice(0, 3)} ${gap.slice(3)}` };
```
Hands back an object (labelled values) with two texts. `ground` is the front plus `000 000`: the ground clock has no gap. `satellite` is the front plus the gap split in two: `gap.slice(0, 3)` is the first three characters, `gap.slice(3)` is everything from the fourth on. Worked example with 24 hours and a gap of 38: `{ ground: "24:00:00.000 000", satellite: "24:00:00.000 038" }`. Without this line the page could not write the clock rows.

```js
}
```
Ends the function.
