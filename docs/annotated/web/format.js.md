# format.js, line by line

Source: `web/format.js`

## What this file is for
This file holds one small tool that turns a number of metres into the text the page shows, for example `1,235 m`. Every readout on the page that shows metres uses it, so they all look the same. It does no measuring and no maths of its own, only the writing of the number.

## Which files it talks to
- `web/first-screen.js`, `web/step-geometry.js` and `web/step-relativity.js`: each imports `formatMetres` and uses it for their metre readouts. In `web/step-geometry.js` it writes the "Position off by" number.
- It uses nothing from other files. It uses `Intl.NumberFormat`, a number-writing tool that is built into every browser.

## In three lines
1. Take a number of metres.
2. Write it with one decimal place if it is under 100, and as a whole number if it is 100 or more, with commas between thousands.
3. Add a space that cannot break across lines, then the letter `m`.

New to code? See [how to read code](../how-to-read-code.md).

## The code, line by line

```js
// One rule for every metres readout: one decimal place below 100 m, whole metres from 100 m up,
// always with a thousands separator. The space before "m" cannot break across lines.
```
Two comment lines (a comment starts with `//`; the computer ignores it). They state the rule the function follows: under 100 m, one digit after the decimal point; from 100 m up, whole metres; always a comma between thousands. The "space that cannot break" is a special space character: if the text reaches the end of a line, the number and the `m` stay together instead of `m` being left alone on the next line. Nothing breaks without the comments.

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
Hands back the final text. The backticks make a template string: text with a hole, where `${digits}` is replaced by the number text from the line above. Between `${digits}` and the `m` is the no-break space described in the comment (it looks like an ordinary space, but it is a different character that never lets the line break there). Worked example: `digits` is `1,235`, so the result is `1,235 m`. Without this line the function would hand back nothing, and the readout would show the word `undefined`.

```js
}
```
Ends the function.
