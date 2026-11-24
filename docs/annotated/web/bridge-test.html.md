# bridge-test.html, line by line

Source: `web/bridge-test.html`

## What this file is for
**This is a developer test page. It is not part of the page judges see.** [`index.html`](../index.html.md) never links to it. It exists so a teammate can check, on its own, that the bridge ([`web/bridge.js`](bridge.js.md)) can download Python, load our `mechanism/` files into it, call a function and report an error. It has no styling, because it does not load [`theme.css`](theme.css.md); it looks like a plain unstyled page.

**Does it still work with today's code?** Yes, by reading it against [`web/bridge.js`](bridge.js.md): the three functions it imports (`loadMechanism`, `callPython`, `evalPython`) are all still exported, [`constants.py`](../mechanism/constants.py.md) is still in the file list that the bridge copies into Python, and `constants.SPEED_OF_LIGHT_M_PER_S` still exists. The expected "unknown function" error text also still matches the bridge's wording. I did not run it in a browser. To open any of these pages you must serve the project folder over `http://` (for example run `python3 -m http.server` in the project's top folder and visit `http://localhost:8000/web/...`) because the browser refuses to load code modules or fetch files from a plain `file://` address. Python and numpy come from an internet address (a CDN), so you also need to be online.

## Which files it talks to
- `web/bridge.js`: this page imports `loadMechanism`, `callPython` and `evalPython` from it and tests all three. See [bridge.js, line by line](bridge.js.md).
- `mechanism/constants.py`: the page asks Python for `SPEED_OF_LIGHT_M_PER_S` from it. See [constants.py, line by line](../mechanism/constants.py.md).
- Nothing else uses this page; no other file links to it.

## In three lines
1. Show a list of the progress messages the bridge reports while Python loads, each with the seconds since the page opened.
2. When loading ends, ask Python for the speed of light and the numpy version and show them with the total time.
3. Call a Python function that does not exist and show that the bridge rejects it with a readable message.

New to code? See [how to read code](../how-to-read-code.md).

## The code, line by line

```html
<!DOCTYPE html>
<html lang="en">
```
`<!DOCTYPE html>` tells the browser "this is a modern web page" (without it, browsers fall back to an old, quirky mode). `<html lang="en">` is the outermost tag that wraps the whole page. A tag is a word in angle brackets that marks a part of the page; most come in pairs, an opening tag and a closing tag with a slash. `lang="en"` is an attribute, an extra label inside a tag, saying the page is in English, which helps screen readers (programs that read pages aloud) pronounce it correctly.

```html
<head>
<meta charset="utf-8">
<title>Bridge test</title>
```
`<head>` holds information about the page that is not shown in the page body. `<meta charset="utf-8">` says the text uses the UTF-8 alphabet, so special characters display correctly (without it, a character like "µ" could appear as nonsense). `<title>Bridge test</title>` is the words shown in the browser tab.

```html
</head>
<body>
<h1>Bridge test</h1>
```
`</head>` closes the head. `<body>` opens the part of the page you see. `<h1>Bridge test</h1>` is the top heading, the biggest. Without the heading the page would have no title on screen.

```html
<h2>Status messages</h2>
<ul id="status-log"></ul>
```
`<h2>` is a second-level heading, "Status messages". `<ul id="status-log"></ul>` is an empty bulleted list (`ul` is an "unordered list"). Its `id` attribute is a unique name, `status-log`, that the script below uses to find it. The page itself is called a tree of elements (the DOM, Document Object Model): every tag becomes an element the script can look up and change. This list starts empty; the script adds one bullet for each progress message.

```html
<p id="result-line">Waiting...</p>
<p id="error-line"></p>
```
Two paragraphs (`<p>`), each with an `id`. `result-line` starts with the text "Waiting..." and is where the final result or failure shows. `error-line` starts empty and is where the result of the "bad function name" test shows. Without them, the script would have nowhere to write its answers.

```html
<script type="module">
import { loadMechanism, callPython, evalPython } from './bridge.js';
```
`<script type="module">` starts a block of JavaScript. `type="module"` makes it a module: code that is allowed to bring in other files with `import`, and that may use `await` at its top level. The `import` line brings in the three functions from [`bridge.js`](bridge.js.md) (the `./` means "the same folder as this page"): `loadMechanism` downloads and starts Python, `callPython` calls a Python function and returns its answer, and `evalPython` runs one short Python expression (the bridge's comment says it is a debug helper for exactly this test page). Without the import, the page could not talk to Python.

```html
const t0 = performance.now();
const log = document.getElementById('status-log');
```
`performance.now()` is the browser's stopwatch: the number of milliseconds since the page started. `t0` is a variable (a name for a value) that remembers the stopwatch reading at this moment, so later lines can work out how long things took. `document.getElementById('status-log')` finds the list element by its `id`, and `log` is a name for it. `const` means the name will not be reassigned. Without them the page could not time anything or find the list.

```html
function onStatus(text) {
  const item = document.createElement('li');
  item.textContent = ((performance.now() - t0) / 1000).toFixed(2) + ' s: ' + text;
  log.appendChild(item);
}
```
A function (a named recipe) called `onStatus`, which receives one progress message (`text`) and adds it to the list. `document.createElement('li')` makes a new, empty list item (a bullet) that is not on the page yet. `item.textContent = ...` sets its words: `(performance.now() - t0) / 1000` is the elapsed milliseconds turned into seconds, `.toFixed(2)` keeps two decimal places, then `' s: '` and the message are added on the end with `+`. Worked example: if the stopwatch now reads 2500 ms and `t0` was 0, then 2500 / 1000 = 2.5, shown as "2.50", so the bullet reads "2.50 s: Ready.". `log.appendChild(item)` puts the bullet at the end of the list so it appears on screen. The bridge is given this function and calls it for each progress message. Without it you would see no progress.

```html
onStatus('Page opened.');
```
Calls `onStatus` by hand once, with the text "Page opened.". It puts the first bullet, at about 0.00 s, in the list before the slow loading starts. Without it the list would stay empty until the first message from the bridge.

```html
try {
  await loadMechanism(onStatus);
```
`try {` begins a safety net: if anything inside fails, the code jumps to the matching `catch` below instead of crashing. The next line, `await loadMechanism(onStatus);`, starts the download of Python and numpy and copies our mechanism files into it. `await` means "pause here until this slow job finishes" (the job returns a Promise, a note that says "the answer will come later"). The `onStatus` function is passed in, so every progress message the bridge announces becomes a bullet. Without `await`, the next lines would run before Python was ready and fail.

```html
  const speed = evalPython('__import__("mechanism.constants", fromlist=["x"]).SPEED_OF_LIGHT_M_PER_S');
  const numpyVersion = evalPython('__import__("numpy").__version__');
```
Asks Python two questions through `evalPython`. The first line runs a short Python expression, `__import__("mechanism.constants", fromlist=["x"]).SPEED_OF_LIGHT_M_PER_S`: Python's built-in way to import a module by name, then read one named number from it. The number is 299,792,458 (metres per second). The second line reads `numpy.__version__`, the version of the numpy library that Pyodide installed. The answers are stored in `speed` and `numpyVersion`. This checks that Python really started and that our [`constants.py`](../mechanism/constants.py.md) file was copied in correctly.

```html
  const seconds = ((performance.now() - t0) / 1000).toFixed(2);
  document.getElementById('result-line').textContent =
    'speed of light ' + speed + ' m/s, numpy ' + numpyVersion + ', ready after ' + seconds + ' s';
```
The first line works out the total time, with the same arithmetic as before: the stopwatch's milliseconds divided by 1000 and rounded to 2 decimal places (for example 14,230 ms gives "14.23"). The other two lines find the `result-line` paragraph and set its words to one sentence joined with `+`: "speed of light 299792458 m/s, numpy <version>, ready after <seconds> s". (The speed shows without commas, because the number arrives from Python as a plain number.) A long statement can be split over two lines; it ends at the semicolon.

```html
} catch (error) {
  document.getElementById('result-line').textContent = 'FAILED: ' + error.message;
}
```
`} catch (error) {` runs only if something above failed (for example no internet or a missing file). The failure is held in `error`, and its `message` is placed in the same paragraph with the prefix "FAILED: ". So a person sees why loading failed instead of the page staying on "Waiting...". `}` closes the catch.

```html
try {
  await callPython('constants.no_such_function', []);
  document.getElementById('error-line').textContent = 'ERROR: unknown function did not fail';
```
A second safety net, for the second test. `await callPython('constants.no_such_function', [])` asks the bridge to call a function that is not in [`constants.py`](../mechanism/constants.py.md), with an empty list of arguments. If it somehow succeeded (it should not), the next line writes "ERROR: unknown function did not fail" into `error-line`, which would tell the developer the bridge was not rejecting bad names. Without this check there would be no proof that errors are reported.

```html
} catch (error) {
  document.getElementById('error-line').textContent = 'Unknown function rejected: ' + error.message;
}
```
The expected path. The bridge's Python helper raises an error ("unknown function: mechanism.constants.no_such_function"), `callPython` turns it into a normal JavaScript error carrying the last line of Python's message, and this `catch` writes "Unknown function rejected: " followed by that message into `error-line`. The last line of Python's message includes the error's kind, so the page should read "Unknown function rejected: ValueError: unknown function: mechanism.constants.no_such_function". Seeing that sentence means the error path works. Without the `catch`, the failure would stop the script and nothing would show.

```html
</script>
</body>
</html>
```
`</script>` ends the JavaScript, `</body>` closes the visible part and `</html>` closes the whole page. Without the closing tags most browsers would guess, but it is correct to close them.
