# startup.js, line by line

Source: `web/startup.js`

## What this file is for
The page's calculations run in Python, and Python has to be downloaded into the browser first. That can take a while, and it can fail if the internet connection is bad. This file is the one place that handles the waiting. It shows the same progress words in every section, shows the same failure words and a shared "Try again" button, and tells each section when it is safe to start.

## Which files it talks to
- `web/bridge.js`: the file that actually downloads Python and the mechanism code. This file loads it on demand (see `loadBridge`) and takes two things from it: `loadMechanism` (does the download, reports progress) and `callPython` (asks a Python function to run).
- `web/first-screen.js`, `web/step-geometry.js`, `web/step-signal.js` and `web/step-relativity.js`: each calls `whenPythonReady` once. They are annotated on their own pages, for example [`step-relativity.js`](step-relativity.js.md).
- `web/theme.css`: gives the "Try again" button its look through the class `btn`.
- The Python files themselves (`mechanism/*.py`) are not called here; this file only waits until they are ready.

## In three lines
1. The first section to ask starts the download. Every section is remembered in a list.
2. While loading, every section shows the latest progress words. If the download fails, every section shows the failure words and a "Try again" button.
3. When the download works, each section is handed `callPython` and its own start function runs, once.

New to code? See [how to read code](../how-to-read-code.md). Browser words used here:
- The **DOM** is the browser's live model of the page. Each tag on the page is an object (an **element**) that code can find, read and change.
- A **Promise** is a ticket for a result that has not arrived yet. It later turns out either well or badly. `async` and `await` are described in the how-to-read-code page.
- A **module** is a file that other files can `import` things from.

## The code, line by line

```js
// One start-up path for every section: the same progress words, the same failure words
// and one shared "Try again" button. Each section calls whenPythonReady once.
// bridge.js is imported inside attempt(), not at the top: if that file fails to download,
// a top-level import would stop this whole file, and the page would wait forever.
```
Four comment lines (the browser ignores them). They explain the design. The last two matter most: if `bridge.js` were imported at the very top and that download failed, this whole file would fail to load too, so nothing would ever show an error or a "Try again" button. By loading `bridge.js` later, inside a function that can catch the failure, the page can say what went wrong.

```js
let callPython = null; // set once the bridge has loaded
```
Makes a box called `callPython` holding `null` (nothing yet). `let` means the content may be replaced later, and it will be, once `bridge.js` has loaded. Sections need this function to ask Python for answers. Without the box there would be nowhere to keep it.

```js
const FAILURE_WORDS = "Python could not be downloaded, so nothing here can calculate yet. Check your internet connection, then press Try again.";
```
A fixed sentence (`const` means it never changes). It is the message every section shows when the download fails. Keeping it in one place means all sections use identical words. Without it, each section would need its own copy.

```js
const sections = []; // one { statusNode, onReady, hasControls, retryButton, done } per section
```
An empty list (`[]`) that will hold one record per section of the page. The comment names what each record holds: `statusNode` (the message line to write into), `onReady` (the function to run when Python is ready), `hasControls` (does the section have sliders or buttons), `retryButton` (the "Try again" button, once made) and `done` (has it already started). Without this list, the file could not tell every section about progress or failure.

```js
let state = "loading"; // "loading", "failed" or "ready"
let started = false;
let latestProgress = "";
```
Three more boxes that can change.
- `state` is the one fact everything depends on: still loading, failed, or ready. It starts as `"loading"`.
- `started` says whether the download has been kicked off yet. It starts `false`, so only the first section starts it.
- `latestProgress` holds the newest progress words from the download (`""` means none yet). A section that arrives late can still show the most recent words.

```js
export function whenPythonReady(statusNode, onReady, { hasControls = true } = {}) {
```
The one function other files call. `export` makes it available to them. It takes three things:
- `statusNode`: the page element where this section's message goes.
- `onReady`: the section's own start function, to be run when Python is ready.
- `{ hasControls = true } = {}`: an optional third item. It is an "options" bundle, and the part in curly brackets picks out `hasControls` from it, using `true` if it is missing. The trailing `= {}` means the whole bundle may be left out. So a section has controls unless it says otherwise.

```js
  const section = { statusNode, onReady, hasControls, retryButton: null, done: false };
```
Builds this section's record: the three things given, plus `retryButton: null` (no button yet) and `done: false` (not started yet). Writing `statusNode` on its own is short for `statusNode: statusNode`.

```js
  sections.push(section);
```
Adds the record to the end of the list, so later progress, failure and success messages reach this section too.

```js
  if (!started) {
    started = true;
    attempt();
```
`!started` means "the download has not been started". If so, mark it started (so no second section starts it again) and call `attempt()` to begin. Without `started`, every section would start its own download.

```js
  } else if (state === "ready") {
    finish(section);
```
Otherwise (a download is already under way or over), if it is already ready, this late-arriving section is started right away by `finish`.

```js
  } else if (state === "failed") {
    showFailure(section);
```
If the download already failed, this section shows the failure words and the "Try again" button immediately.

```js
  } else {
    showProgress(section);
  }
}
```
Anything else means it is still loading, so show the progress words so far. The last two lines close the `else` and the function. Without these four branches, a section that arrives late would stay silent.

```js
function attempt() {
```
Starts a function called `attempt`. One attempt is one try at downloading Python. It is called first by `whenPythonReady` and again by the "Try again" button.

```js
  state = "loading";
```
Sets the state back to loading. After a failure this is what lets progress words show again.

```js
  for (const section of sections) removeRetryButton(section);
```
A **loop**: it takes each record in the list in turn, calling it `section`, and calls `removeRetryButton` on it. So when a new try starts, the old "Try again" buttons disappear. Without it, the buttons would stay on screen during the retry.

```js
  loadBridge().then(
```
Calls `loadBridge` (below), which returns a Promise, and `.then(...)` says what to do when it settles. `.then` takes two functions: the first runs if it worked, the second if it failed.

```js
    () => {
      state = "ready";
      for (const section of sections) finish(section);
    },
```
The success function. `() => { ... }` is a small unnamed function with no inputs. It sets the state to ready, then loops over every section and calls `finish`, which clears the message and starts the section. Without it, nothing would start even after a good download.

```js
    (error) => {
      console.error(error);
      state = "failed";
      for (const section of sections) showFailure(section);
    },
```
The failure function. It receives `error`, a description of what went wrong. `console.error(error)` writes it into the browser's developer console, a hidden log for programmers, so the cause is not lost. Then it sets the state to failed and shows the failure words on every section. Without it a failed download would leave the sections saying "loading" for ever.

```js
  );
}
```
Closes the `.then(` call and the `attempt` function.

```js
async function loadBridge() {
```
Starts a function called `loadBridge`. `async` marks it as a function that has to wait for things, and it hands back a Promise automatically.

```js
  const bridge = await import("./bridge.js");
```
`import("./bridge.js")` downloads the bridge file now, while the page is running (the "late import" the top comment talked about). `await` pauses here until it arrives. The arrived file is stored in `bridge`. If the download fails, the error stops this function and arrives at the failure function in `attempt`.

```js
  callPython = bridge.callPython;
```
Copies the bridge's `callPython` function into the box made at the top of this file. Sections are later handed it, so they can ask Python for answers.

```js
  await bridge.loadMechanism(onProgress);
```
Starts the real download of Python and the mechanism code, and waits for it to end. `onProgress` is handed over as the function the bridge should call with each progress message. Without this line, Python would never load.

```js
}
```
Closes `loadBridge`.

```js
function onProgress(text) {
```
Starts a function called `onProgress`, which the bridge calls with a progress message (`text`) each time it has news.

```js
  latestProgress = text;
```
Saves the newest words, so a section that arrives later can show them.

```js
  if (state !== "loading") return;
```
`!==` means "is not". If we are not in the loading state (for example the download has just failed or finished), a late progress message is ignored: `return` ends the function. Without this a stale progress line could overwrite a failure message.

```js
  for (const section of sections) showProgress(section);
```
Otherwise show the new words in every section.

```js
}
```
Closes `onProgress`.

```js
function showProgress(section) {
```
Starts a function that writes the progress words into one section.

```js
  const prefix = section.hasControls ? "The controls switch on when this finishes. " : "";
```
Chooses a short lead-in. If the section has controls (the `? :` is a short if), the lead-in is "The controls switch on when this finishes. " and otherwise it is empty text. It tells the reader why sliders are greyed out. A section without controls would find that sentence confusing, so it gets none.

```js
  section.statusNode.textContent = prefix + latestProgress;
```
Sets the words shown in the section's message element: the lead-in followed by the newest progress words. (`+` joins two pieces of text.) `textContent` is the text inside an element. Without this line, the reader would see no progress.

```js
}
```
Closes `showProgress`.

```js
function finish(section) {
```
Starts a function that starts one section, now that Python is ready.

```js
  if (section.done) return;
```
If the section was already started, stop. This guarantees each section's start function runs once only, even if `finish` is called twice. Without it, a section could build its sliders twice.

```js
  section.done = true;
```
Marks it as started.

```js
  section.statusNode.textContent = "";
```
Clears the progress or failure message, because loading is over.

```js
  removeRetryButton(section);
```
Removes the "Try again" button if the section has one.

```js
  section.onReady(callPython);
```
Runs the section's own start function and hands it `callPython`. This is the moment the section can begin asking Python for answers (for example [`step-relativity.js`](step-relativity.js.md) uses it to place the satellites).

```js
}
```
Closes `finish`.

```js
function showFailure(section) {
```
Starts a function that shows the failure for one section.

```js
  section.statusNode.textContent = FAILURE_WORDS;
```
Writes the fixed failure sentence into the section's message element.

```js
  if (section.retryButton) return;
```
If this section already has a "Try again" button, stop. Without this line, every call would add one more button.

```js
  const button = document.createElement("button");
```
Makes a new, empty `<button>` element in memory. `document` is the page, and `createElement` builds a new element that is not yet on screen.

```js
  button.className = "btn";
```
Gives it the style class `btn`, which `theme.css` styles as the page's standard button. Without it the button would look plain.

```js
  button.type = "button";
```
Says it is an ordinary button that does nothing by itself. Without this, a button inside a form could submit the form.

```js
  button.textContent = "Try again";
```
Sets the words on the button.

```js
  button.addEventListener("click", () => attempt()); // restarts the load for every section
```
An **event listener**: when the button is clicked, call `attempt()`. That starts the download again and resets the state to loading for every section, not just this one (as the comment says). Without it the button would do nothing.

```js
  section.statusNode.after(button);
```
Puts the button on the page, directly after the message element. Until now it was only in memory.

```js
  section.retryButton = button;
```
Remembers the button in the section's record, so that `removeRetryButton` can find it and so the earlier check can tell that one already exists.

```js
}
```
Closes `showFailure`.

```js
function removeRetryButton(section) {
```
Starts a function that removes one section's "Try again" button.

```js
  if (!section.retryButton) return;
```
If there is no button, there is nothing to remove, so stop.

```js
  section.retryButton.remove();
```
Takes the button off the page.

```js
  section.retryButton = null;
```
Forgets it (back to "no button"), so that `showFailure` can make a new one on a later failure.

```js
}
```
Closes `removeRetryButton`. That is the end of the file.
