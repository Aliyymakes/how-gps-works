# bridge.js, line by line

Source: `web/bridge.js`

## What this file is for
The page is written in JavaScript, but all the position maths is written in Python. A web browser cannot run Python by itself. This file is the go-between (the "bridge"): it downloads a copy of Python that runs inside the browser tab, puts the team's Python files into it, and offers one simple function, `callPython`, that the rest of the page uses to run a Python function and get its answer back.

## Which files it talks to
- [`mechanism/__init__.py`](../mechanism/__init__.py.md), [`constants.py`](../mechanism/constants.py.md), [`coords.py`](../mechanism/coords.py.md), [`scenario.py`](../mechanism/scenario.py.md), [`solver.py`](../mechanism/solver.py.md), [`mapview.py`](../mechanism/mapview.py.md), [`geometry.py`](../mechanism/geometry.py.md), [`signal.py`](../mechanism/signal.py.md), [`relativity.py`](../mechanism/relativity.py.md): all nine are downloaded and copied into Python's file system (see the list at the top of the file). Which one runs is decided by the text the page passes to `callPython`.
- [`web/startup.js`](startup.js.md): loads this file (inside `loadBridge()`, which `attempt()` runs) and hands the page its `callPython`. The agreed rules for this (the "contract") are in `docs/interface.md` ("The page side").
- [`web/first-screen.js`](first-screen.js.md), [`web/step-geometry.js`](step-geometry.js.md), [`web/step-signal.js`](step-signal.js.md), [`web/step-relativity.js`](step-relativity.js.md): every call from the page to Python goes through `callPython`, for example `solver.solve_position` ([solver.py explained](../mechanism/solver.py.md)), `coords.latlon_to_xyz` ([coords.py](../mechanism/coords.py.md)) and `mapview.distance_lines` ([mapview.py](../mechanism/mapview.py.md)).
- [`web/bridge-test.html`](bridge-test.html.md): the test page that uses `evalPython`.
- [`index.html`](../index.html.md): repeats the Pyodide web address in a `<link rel="modulepreload">` so the download can start early. See [index.html explained](../index.html.md).
- Pyodide itself, a copy in the repo's `vendor/` folder (experiment branch only).

## In three lines
1. Download Pyodide (Python and numpy) and, at the same time, download the team's nine Python files.
2. Write those files into Pyodide's pretend disk and add a small Python helper that can run any function by its name.
3. `callPython("module.function", [arguments])` turns the arguments into text, runs the Python function, and turns the text answer back into JavaScript values.

New to code? See [how to read code](../how-to-read-code.md).

## Three ideas before the code

**Pyodide.** Pyodide is the real Python language, packaged so it can run inside a web page. It is compiled to WebAssembly, a compact program format that browsers can run at high speed. The page needs no Python installed on your computer and no server somewhere else computing the answers: the maths runs on your own machine, in the tab. The price is a download of several megabytes on the first visit (Python itself and the numpy library), which is why the page shows "Step 1 of 2" while it waits.

**The virtual file system.** Python programs find their other files by reading a disk. A browser tab has no disk Python may use. So Pyodide gives Python a pretend disk that lives only in the tab's memory: the virtual file system, reached from JavaScript as `pyodide.FS`. This file creates a folder in it and writes the nine `mechanism` files into that folder as text. When the Python code says `import mechanism.solver`, Python looks in that pretend folder and finds the file we wrote. The pretend disk is empty again every time the page is reloaded, so the files are written again on every visit.

**Why text goes in and out.** JavaScript and Python store numbers and lists differently. The easiest safe way to move data between them is JSON, a plain-text format both understand: a list of numbers looks like `[1, 2.5, 3]` and a labelled record looks like `{"x_m": 1.5}`. The bridge turns every argument into JSON text, Python turns it back into Python values, runs the function, turns the answer into JSON text, and JavaScript turns that back into JavaScript values. That is why the Python functions return plain Python numbers and lists (see `_save_step` in [solver.py](../mechanism/solver.py.md)).

## The code, line by line

```js
// Bridge between the page (JavaScript) and the Python mechanism (Pyodide).
// loadMechanism(onStatus) loads everything; callPython("module.function", [args]) calls it.
// Contract: docs/interface.md ("The page side").
```
A comment block (lines starting `//` are notes for people; the computer skips them). It says this file is the bridge between the page (JavaScript) and the Python mechanism (Pyodide), names the two functions the rest of the page uses, and points to `docs/interface.md`, the team's written agreement on what the page may ask Python for and what comes back (the "contract"). Nothing breaks if they are removed.

```js
// Pinned Pyodide version (ships Python 3.14.2). index.html repeats this address in its
// <link rel="modulepreload">: change both together.
```
A comment: the exact version of Pyodide is fixed (pinned) on purpose, so the page behaves the same for everyone and does not change when a newer Pyodide appears. The same address is written again in [`index.html`](../index.html.md) (a `<link rel="modulepreload">`), and the comment warns that both must be changed together. If only one were changed, the early download would fetch a different file from the one the page really uses and would be wasted.

```js
const PYODIDE_BASE = new URL('../vendor/pyodide/v314.0.8/full/', import.meta.url).href;
```
`const` makes a named value that can never be reassigned. `PYODIDE_BASE` is the web address of the folder where Pyodide's files live. On this experiment branch they are a copy inside the repo, in `vendor/`; `new URL(..., import.meta.url)` turns the path into a full address measured from where `bridge.js` itself is. The version is `v314.0.8`. Other lines add file names to the end of it, so the address must finish with a `/`. Without it the page would not know where to download Python from.

```js
// Files of the `mechanism` package. A file that cannot be fetched makes the whole load fail.
```
A comment: the files below are all required. If even one cannot be downloaded, the whole load fails, because a missing file would break an `import` later.

```js
const MECHANISM_FILES = [
  '__init__.py', 'constants.py', 'coords.py', 'scenario.py', 'solver.py',
  'mapview.py', 'geometry.py', 'signal.py', 'relativity.py',
];
```
`MECHANISM_FILES` is a list (square brackets) of the nine file names of the Python `mechanism` package, in quotes, separated by commas. The list is run through to download each one and to write each one into the pretend disk. [`__init__.py`](../mechanism/__init__.py.md) is the file that tells Python that the folder is a package that can be imported as `mechanism`. A file that is not on this list is never copied, so `import` would fail for it.

```js
const MECHANISM_DIR = '/home/pyodide/mechanism';
```
The folder, inside the pretend disk, where the files will be written. `/home/pyodide` is a folder that Pyodide provides, and `mechanism` is the package folder created inside it. The folder name `mechanism` matters: Python code and the helper below say `mechanism.solver`, which means "the file [`solver.py`](../mechanism/solver.py.md) inside the folder called `mechanism`".

```js
let pyodide = null;
```
`let` makes a value that may change later. `pyodide` will hold the running Python once it has loaded. It starts as `null`, meaning "nothing yet". `callPython` checks it, so calling too early gives a clear error instead of a confusing one.

```js
let loading = null;
```
`loading` will hold the one "load in progress" promise. A Promise is JavaScript's way of saying "the answer is not ready yet, but here is a ticket for it; you can wait on the ticket". Starting as `null` means "no load has started". It is what stops the page downloading Python twice when several sections of the page ask for it.

```js
const listeners = []; // every status function passed to loadMechanism
```
`listeners` is an empty list. Each section of the page passes in a status function (a function that receives a progress sentence and shows it). All of them are collected here. The comment says what the list is for.

```js
let latestText = null; // the most recent progress message
```
`latestText` remembers the most recent progress sentence. It starts as `null` (none yet). It lets a section that asks late still see the current sentence at once.

```js
// Every caller gets every progress message, also when another caller started the load.
```
A comment: every caller gets every progress message, even when it was a different caller that began the load. That is why there are two memory variables above instead of one.

```js
export function loadMechanism(onStatus = () => {}) {
```
Starts the function `loadMechanism`. `export` means other files may import it ([`startup.js`](startup.js.md) does). It takes one input, `onStatus`: the status function. The part `= () => {}` gives it a default: if nobody passes one, it is a function that does nothing, so the code below can always call it safely. The function returns the loading promise, so a caller can wait until everything is ready (`await`).

```js
  if (!listeners.includes(onStatus)) listeners.push(onStatus);
```
`if (...) listeners.push(onStatus)` adds this caller's status function to the list, but only if it is not already there (`!` means "not", `includes` asks "is it in the list?"). Without the check, a caller who asks twice would receive every message twice.

```js
  if (latestText !== null) onStatus(latestText);
```
If a progress sentence already exists (`latestText` is not `null`; `!==` means "is not equal to"), give it to this caller straight away. Otherwise a section that joined late would show nothing until the next message.

```js
  if (!loading) {
```
`if (!loading)` means "if no load has been started yet". Only the first caller starts the real work. Later callers skip this and share the same ticket.

```js
    loading = doLoad().catch((error) => {
```
Starts the real work: `doLoad()` (defined further down) returns a promise. `.catch(...)` says what to do if it fails. The result is saved in `loading`.

```js
      loading = null; // a failed load is not remembered: the next call tries again
```
On failure, forget the ticket by setting `loading` back to `null`. The comment says why: a failed load is not remembered, so if the user tries again (the "Try again" button), the next call to `loadMechanism` starts a fresh load. Without it, one bad network moment would break the page for good.

```js
      throw error;
```
`throw error` passes the failure on to whoever is waiting, so they can show a failure message. Without it, the failure would be swallowed and nobody would be told.

```js
    });
```
Closes the function that handles failure and the `.catch(...)` call (`}` ends the block, `)` ends the call, `;` ends the statement).

```js
  }
```
Closes the `if (!loading)` block.

```js
  return loading;
```
Hands back the ticket, so the caller can `await` it. `await` means "pause here until it is ready".

```js
}
```
Closes `loadMechanism`.

```js
function tell(text) {
```
Starts `tell`, a helper that announces one progress sentence (`text`).

```js
  latestText = text;
```
Stores the sentence in `latestText`, so later callers can be given it (`loadMechanism` above hands it to a caller who joins late).

```js
  for (const listener of listeners) listener(text);
```
A loop: `for (const listener of listeners)` takes the status functions one at a time, and `listener(text)` calls each with the sentence, so every section updates its own progress line.

```js
}
```
Closes `tell`.

```js
async function fetchText(name) {
```
Starts `fetchText`, which downloads one file as text. `async` marks a function that can wait for things (the network) using `await`; it always returns a Promise. `name` is the file name, for example [`solver.py`](../mechanism/solver.py.md).

```js
  let response;
```
Makes an empty box `response` for the server's reply. It is declared out here so it can be used both inside and after the `try` block below.

```js
  try {
```
`try {` begins a block where something may go wrong. If it does, the program does not stop; it jumps to the `catch` part.

```js
    response = await fetch(new URL('../mechanism/' + name, import.meta.url));
```
`fetch(...)` asks the network for a file; `await` waits until the reply starts to arrive. The address is made by `new URL('../mechanism/' + name, import.meta.url)`. `import.meta.url` is the address of `bridge.js` itself, which is in the `web` folder. `../` means "go up one folder", so [`solver.py`](../mechanism/solver.py.md) becomes the address of [`mechanism/solver.py`](../mechanism/solver.py.md) next to the `web` folder, wherever the site is hosted. A fixed web address could not work on both a local test copy and the final published page.

```js
  } catch {
```
`} catch {` runs if the network failed altogether (no connection, blocked, ...).

```js
    response = null;
```
Sets `response` to `null`, "no reply". That way a network failure and a bad reply are handled by one single check below.

```js
  }
```
Closes the `catch` block.

```js
  if (!response || !response.ok) throw new Error('could not load mechanism/' + name);
```
Stops with an error message if there is no reply (`!response`) or the server says the file is not available (`!response.ok`; `||` means "or"). `throw new Error(...)` raises the error. The message is exactly `could not load mechanism/` plus the file name. One missing file is therefore a failed load, as the comment above the list says.

```js
  return response.text();
```
Returns the file's contents as text (`response.text()` also gives a promise, which the caller waits on).

```js
}
```
Closes `fetchText`.

```js
async function doLoad() {
```
Starts `doLoad`, the real loading work. It is `async` because it waits for downloads.

```js
  tell('Step 1 of 2: downloading Python and numpy. This is the slow step on a first visit…');
```
Announces the first progress sentence to every section (through `tell`). The words shown are exactly: `Step 1 of 2: downloading Python and numpy. This is the slow step on a first visit…`. It is honest about the slow part.

```js
  // Our own files download while Pyodide does; they are written into Python's file system later.
```
A comment: the team's own files download at the same time as Pyodide, to save waiting. They cannot be written into the pretend disk yet, because the pretend disk does not exist until Pyodide has loaded.

```js
  const sources = Promise.all(MECHANISM_FILES.map(fetchText));
```
Starts all nine downloads at once: `MECHANISM_FILES.map(fetchText)` calls `fetchText` once for each name and gives a list of nine promises. `Promise.all(...)` joins them into one promise that finishes when all nine have arrived, or fails if any one fails. It is not awaited yet, so the program carries on to the Pyodide download straight away.

```js
  sources.catch(() => {}); // the failure is reported where the result is awaited below
```
Adds a do-nothing failure handler `.catch(() => {})`. Reason (from the comment): if a file fails while Pyodide is still downloading, nobody is waiting on the promise yet, and the browser would print a stray "unhandled error" warning. This line quietens that. The real failure is still reported, further down, where `await sources` happens.

```js
  const { loadPyodide } = await import(PYODIDE_BASE + 'pyodide.mjs');
```
`await import(...)` loads Pyodide's code file (`pyodide.mjs`) from the address in `PYODIDE_BASE`. A dynamic `import()` is the way to load JavaScript from an address chosen while the program runs. `{ loadPyodide }` takes out of it the one function we need, `loadPyodide`. If this download fails, an error is raised and the page learns the load failed.

```js
  pyodide = await loadPyodide({ indexURL: PYODIDE_BASE, packages: ['numpy'] });
```
`loadPyodide(...)` downloads and starts Python and waits until it is ready. `indexURL` tells it where the rest of its files are (the same folder). `packages: ['numpy']` also downloads numpy, the maths library that [`solver.py`](../mechanism/solver.py.md) and others use. The running Python is saved in the variable `pyodide`. This is the slow step. Without `numpy` here, `import numpy` in the mechanism files would fail.

```js
  tell('Step 2 of 2: loading our GPS code…');
```
Announces the second sentence, exactly: `Step 2 of 2: loading our GPS code…`.

```js
  const texts = await sources;
```
Waits for the nine files to finish arriving (`await sources`). `texts` is a list of nine pieces of text, in the same order as `MECHANISM_FILES`. If any download failed, the error is raised here and the whole load fails.

```js
  pyodide.FS.mkdirTree(MECHANISM_DIR);
```
Creates the folder `/home/pyodide/mechanism` inside the pretend disk. `FS` is the file system. `mkdirTree` makes the folder and any missing folders above it. Without it, writing the files below would fail because the folder would not exist.

```js
  MECHANISM_FILES.forEach((name, i) => pyodide.FS.writeFile(MECHANISM_DIR + '/' + name, texts[i]));
```
Writes the files. `forEach` runs the small function once for every name, and `i` is the position in the list (0, 1, 2, ...). For `i = 4` the name is [`solver.py`](../mechanism/solver.py.md), and `texts[4]` is its downloaded text, so this writes the text to `/home/pyodide/mechanism/solver.py`. The `(name, i) => ...` form is a short way of writing a function. After this line the pretend disk holds the team's nine files.

```js
  // The folder holding the package must be on sys.path.
```
A comment: Python has a list of folders it looks in when asked to import something, called `sys.path`. The folder that holds the package folder (`/home/pyodide`) must be on it.

```js
  pyodide.runPython('import sys\nif "/home/pyodide" not in sys.path: sys.path.insert(0, "/home/pyodide")');
```
`pyodide.runPython(...)` runs a piece of Python text. The text here has two lines, joined by `\n` (which means "new line"): `import sys`, then `if "/home/pyodide" not in sys.path: sys.path.insert(0, "/home/pyodide")`. It adds `/home/pyodide` to the front of Python's search list (position 0) only if it is not already there. Without it, `import mechanism.solver` would say "no module named mechanism".

```js
  // Runs in Python: import the module, call the function, return the result as JSON text.
```
A comment saying what the next block of Python does: import the module, call the function, return the result as JSON text.

```js
  pyodide.runPython(`
```
`pyodide.runPython(` followed by a backtick starts the next piece of Python. The backtick quotes make a "template string": text that may span many lines. Everything from here to the closing backtick, a few blocks further down, is Python code, not JavaScript. It is run once, right now, and defines a Python function that stays available inside Pyodide for later.

```js
import importlib, json
```
Python (inside the text). This statement brings in two of Python's built-in toolboxes. `importlib` can import a module when we only know its name as text. `json` converts to and from JSON text. Without them the function below could not work.

```js
def _bridge_call(target, args_json):
```
Python. Starts a function called `_bridge_call`. It takes `target`, the text `"module.function"`, for example `"solver.solve_position"`, and `args_json`, the arguments written as JSON text. The leading underscore is a habit meaning "internal". The indented lines below belong to it (Python marks blocks by indentation instead of brackets).

```js
    module_name, _, function_name = target.partition(".")
```
Python. `target.partition(".")` splits the text at the first dot into three parts: before, the dot itself, after. For `"solver.solve_position"` that gives `"solver"`, `"."` and `"solve_position"`. The three names on the left receive them in order. The middle one is called `_` because it is not needed. So `module_name` is `"solver"` and `function_name` is `"solve_position"`.

```js
    try:
```
Python. `try:` begins a block where an error may happen, to be handled by the `except` below.

```js
        module = importlib.import_module("mechanism." + module_name)
```
Python. Imports the file by name. Joining text, `"mechanism." + module_name` gives `"mechanism.solver"`. `importlib.import_module(...)` loads that file from the pretend disk and returns it as `module`. Only files inside the `mechanism` package can be reached this way, which is a good limit.

```js
    except ImportError:
```
Python. If the import fails (`ImportError`, which includes "no such file"), do the next line.

```js
        raise ValueError("unknown module: mechanism." + module_name)
```
Python. Stops with a readable error, `unknown module: mechanism.` plus the name. An ImportError raised from inside a mechanism file (for example a mistyped import in it) is also reported with this message, so its wording may be misleading in that case. This message will be what the page's error text shows.

```js
    function = getattr(module, function_name, None)
```
Python. `getattr(module, function_name, None)` looks inside the loaded file for something with that name, and gives back `None` (Python's "nothing") if it is missing.

```js
    if not callable(function):
```
Python. `callable(function)` asks "can this be called like a function?" `not` flips the answer. If the name is missing or is something else (like a number), go on to the next line.

```js
        raise ValueError("unknown function: mechanism." + target)
```
Python. Stops with the error `unknown function: mechanism.` plus the full target text, such as `mechanism.solver.nonsense`. This catches typing mistakes in the page code with a clear message.

```js
    return json.dumps(function(*json.loads(args_json)))
```
Python. The real call, read from the inside out. `json.loads(args_json)` turns the JSON text back into a Python list. The star in `function(*...)` spreads that list into separate inputs, so `[a, b, c]` becomes `function(a, b, c)`. Python runs the function. `json.dumps(...)` turns the answer into JSON text. `return` hands that text back. Worked example: the page passes `"solver.solve_position"` and the text `[sats, ranges, true]` (really the full lists); Python calls `solve_position(sats, ranges, True)`, and the returned dictionary comes back as JSON text. If the answer held certain numpy values (an array, or numpy's own whole numbers or true/false values), `json.dumps` would refuse them, which is why the mechanism files convert to plain numbers first (see [solver.py explained](../mechanism/solver.py.md)).

```js
`);
```
JavaScript again. The backtick closes the template string and `)` closes the `runPython` call. Python now has a function `_bridge_call` that stays available inside Python for every later call.

```js
  tell('Ready.');
```
Announces the last sentence, `Ready.`. In practice [`startup.js`](startup.js.md) empties the status lines straight after, as soon as the load finishes, so it is hardly seen. Then the sections start using the Python code.

```js
}
```
Closes `doLoad`. When it finishes without an error, the promise in `loading` is done and everyone waiting on `loadMechanism` carries on.

```js
export async function callPython(target, args = []) {
```
Starts `callPython`, the function the whole page uses. It is `async`, so calling it always gives a promise, which the page waits for with `await`. `target` is the text `"module.function"`. `args` is the list of inputs; `= []` means "no inputs" when none are given. Example from the page: `callPython("coords.latlon_to_xyz", [lat_deg, lon_deg])`, which runs [coords.py](../mechanism/coords.py.md)'s function of that name.

```js
  if (!pyodide) throw new Error('callPython: call loadMechanism() first');
```
Safety check: if `pyodide` is still `null`, loading has not finished, so stop with a clear message, `callPython: call loadMechanism() first`, instead of a confusing crash.

```js
  const bridgeCall = pyodide.globals.get('_bridge_call');
```
`pyodide.globals.get('_bridge_call')` fetches the Python helper function (`_bridge_call`, defined in the Python text above) as an object JavaScript can call. It is called `bridgeCall`. This object is a handle (a "proxy") to something that lives in Python's memory.

```js
  try {
```
`try {` begins a block with error handling and a clean-up step (`finally`, below).

```js
    return JSON.parse(bridgeCall(target, JSON.stringify(args)));
```
The real call, read from the inside out. `JSON.stringify(args)` turns the JavaScript list into JSON text, for example `[1, 2]` becomes the text `"[1,2]"`. `bridgeCall(target, text)` runs the Python helper, which runs the mechanism function and returns JSON text. `JSON.parse(...)` turns that text back into a normal JavaScript number, list or record, and `return` gives it to the caller. While Python runs, the page waits; the mechanism functions are quick enough for that.

```js
  } catch (error) {
```
`} catch (error) {` runs if the Python side raised an error (a wrong function name, wrong inputs, a failed calculation), or if the text could not be converted.

```js
    // Python exceptions arrive as PythonError; the last line holds the readable part.
```
A comment explaining the next lines. An error from Python arrives in JavaScript as a `PythonError` whose message is a long report; only the final line says what actually went wrong.

```js
    const lines = String(error.message).trim().split('\n');
```
Takes the message text (`String(error.message)`), removes blank space at the ends (`trim()`), and splits it at each new line (`split('\n')`) into a list of lines.

```js
    throw new Error(lines[lines.length - 1]);
```
Raises a new, shorter error containing only the last line. `lines.length - 1` is the position of the last item, because counting starts at 0 (a list of 5 lines has positions 0 to 4). Example: the last line may read `ValueError: unknown function: mechanism.solver.nonsense`. The page's own message code then shows it.

```js
  } finally {
```
`} finally {` starts a block that runs always: after success, and after an error.

```js
    bridgeCall.destroy();
```
`bridgeCall.destroy()` releases the handle to the Python function. The handle takes up memory on the Python side until it is released; without this line, memory would creep up on every call, which matters for the slider (dragging calls Python many times).

```js
  }
```
Closes the `finally` block.

```js
}
```
Closes `callPython`.

```js
// Debug helper for the test page only: evaluates one Python expression, returns it as a JS value.
```
A comment: `evalPython` is a debugging tool for the test page only ([`web/bridge-test.html`](bridge-test.html.md)). It evaluates a single Python expression and returns the answer as a JavaScript value. The real page does not use it.

```js
export function evalPython(expression) {
```
Starts `evalPython`. `export` lets the test page import it. It takes `expression`, Python code as text, for example `"1 + 1"`. It is not `async`: it returns the answer straight away.

```js
  if (!pyodide) throw new Error('evalPython: call loadMechanism() first');
```
Same safety check as in `callPython`, with the name of this function in the message.

```js
  return JSON.parse(pyodide.runPython('import json\njson.dumps(' + expression + ')'));
```
Builds a two-line piece of Python, `import json` and then `json.dumps(` plus the expression plus `)`, runs it, and turns the JSON text it gives back into a JavaScript value with `JSON.parse`. For the expression `1 + 1` the Python run is `json.dumps(1 + 1)`, which is the text `2`, and JavaScript gets the number 2. Because the expression is pasted straight into Python code, never pass it text from a user; the test page only passes its own fixed text.

```js
}
```
Closes `evalPython`. End of the file.
