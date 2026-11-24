# theme.js, line by line

Source: `web/theme.js`

## What this file is for
This small file holds three helpers for how the page looks. One makes a soft patch of light follow the mouse across a card. The other two switch the page between a dark look and a light look, and remember the choice for the next visit. It does no maths and never asks Python for anything.

## Which files it talks to
- `web/theme.css` ([theme.css](theme.css.md)): holds the actual colours. It has a rule for `[data-theme="light"]`, and the card glow reads two variables named `--px` and `--py`. This file only sets those variables and the `data-theme` label; `theme.css` decides what they look like.
- `docs/ui-guide.md` (section 2): the rules for the page's look. This file follows them.
- [`first-screen.js`](first-screen.js.md) calls `loadSavedTheme` and `trackPointerLight` when the page opens; the two test pages [dev/step-geometry.html](dev/step-geometry.html.md) and [dev/step-signal.html](dev/step-signal.html.md) do the same. `setTheme` is called by `loadSavedTheme`, and by the light/dark button on the design preview page [theme-preview.html](theme-preview.html.md). The main page has no light/dark button, so there the look is "light" only if "light" was saved earlier.

## In three lines
1. While the mouse moves over a card, work out where the mouse is inside that card and store it in two CSS variables so the glow can follow.
2. `setTheme` writes the chosen look ("dark" or "light") on the page and saves it in the browser.
3. `loadSavedTheme` reads the saved choice when the page opens and applies it, using "dark" if nothing sensible was saved.

New to code? See [how to read code](../how-to-read-code.md). Browser words used here:
- The **DOM** is the browser's live model of the page: every tag on the page is an object (an **element**) that code can read and change.
- An **attribute** is a labelled setting on a tag, like `data-theme="light"`.
- A **CSS variable** is a named value in the style sheet, written with two dashes, like `--px`. A style rule can read it, and code can change it.

## The code, line by line

```js
// Instrument theme helpers: pointer light on cards and a light/dark switch.
// Rules: docs/ui-guide.md section 2.
```
Two comments (lines starting with `//` are notes for people; the browser ignores them). They say what the file is for and where the rules are written down. Nothing breaks without them.

```js
export function trackPointerLight(root = document) {
```
Starts a function called `trackPointerLight`. `export` means other files may import and use it. The part in brackets is a **parameter**: a value the caller can hand in. `root = document` means "if nobody hands one in, use `document`", which is the whole page. So by default the function watches the entire page.

```js
  root.addEventListener("pointermove", (event) => {
```
Adds an **event listener**: a rule saying "when this happens, run this function". The event is `pointermove`, which fires every time the mouse (or a finger or pen) moves over the page. The small function `(event) => { ... }` is what runs each time, and `event` is a record of what happened (where the pointer is, which element it is over). Without this line nothing would ever react to the mouse.

```js
    const card = event.target.closest?.(".card");
```
`event.target` is the element the pointer is over right now. `closest(".card")` looks at that element, then its parent, then its parent's parent and so on, and returns the first one that has the style class `card` (the page's boxed panels). That way, hovering over a word inside a card still finds the card. The `?.` before the brackets means "only call this if it exists": some targets, such as the page background, have no `closest`, and without `?.` the code would crash there. `const` makes a named box for a value that will not be replaced.

```js
    if (!card) return;
```
`!card` means "there is no card". In that case `return` ends the function straight away. The pointer is not over a card, so there is nothing to light up. Without this line the next lines would fail on an empty value.

```js
    const box = card.getBoundingClientRect();
```
Asks the browser for the card's rectangle on screen: its left edge, top edge, width and height, measured in pixels from the top-left corner of the visible window. We need the left and top edges to turn a window position into a position inside the card.

```js
    card.style.setProperty("--px", `${event.clientX - box.left}px`);
```
`event.clientX` is how far the pointer is from the window's left edge. Subtracting `box.left` (the card's left edge) gives how far the pointer is from the card's own left edge. The backticks build a piece of text, and `${...}` drops the number into it, then adds `px` (pixels). `setProperty` writes it into the card's `--px` variable. Worked example: the card's left edge is at 100 pixels and the pointer is at 160, so `--px` becomes `60px`. The glow in [`theme.css`](theme.css.md) is centred on `--px` and `--py`, so without this line it would stay at its starting spot (50%).

```js
    card.style.setProperty("--py", `${event.clientY - box.top}px`);
```
The same for the up-and-down direction: pointer height minus the card's top edge. Worked example: card top at 300, pointer at 340 gives `--py` of `40px`. Without it the glow could follow left and right but not up and down.

```js
  });
}
```
The first line closes the small function and the `addEventListener` call. The second closes `trackPointerLight`.

```js
export function setTheme(name) {
```
Starts a function called `setTheme` that other files can use. `name` is the look to switch to: the code in this file uses `"dark"` and `"light"`.

```js
  document.documentElement.dataset.theme = name;
```
`document.documentElement` is the very top tag of the page (`<html>`). `dataset.theme` is its `data-theme` attribute. Setting it to `"light"` makes the tag `data-theme="light"`, which switches on the `[data-theme="light"]` colour rules in [`theme.css`](theme.css.md). Without this line, nothing on screen would change.

```js
  try { localStorage.setItem("theme", name); } catch (_) { /* storage can be blocked; the switch still works */ }
```
`localStorage` is a small notebook the browser keeps for this site, and `setItem("theme", name)` writes the chosen look into it, so the choice survives closing the page. Some browsers or privacy settings block that notebook and raise an error. `try { ... } catch (_) { ... }` means "attempt this, and if it fails, carry on instead of crashing". The `_` is a name for the error that nobody uses. The text between `/* */` is a comment. Without `try`, a blocked notebook would stop the function with an error. Because the `data-theme` line ran first, the switch still works for this visit, but the choice is not remembered.

```js
}
```
Closes `setTheme`.

```js
export function loadSavedTheme() {
```
Starts a function called `loadSavedTheme`. It takes nothing. It is meant to run once when the page opens.

```js
  let saved = null;
```
Makes a box called `saved` and puts `null` in it, which means "nothing". `let` (unlike `const`) means the content may change later. This is the starting value if nothing can be read.

```js
  try { saved = localStorage.getItem("theme"); } catch (_) { /* ignore */ }
```
Tries to read the earlier choice from the browser's notebook. If the notebook is blocked, the error is ignored and `saved` stays `null`. Without `try`, a blocked notebook would crash the page start-up.

```js
  setTheme(saved === "light" ? "light" : "dark");
```
Picks the look and applies it. `saved === "light"` asks "is the saved word exactly light?". The `? :` is a short if: if yes use `"light"`, otherwise use `"dark"`. So only an exact "light" gives the light look. Nothing saved, a blocked notebook, or an odd leftover word all give "dark". Then `setTheme` does the real work from above (set the label on the page and save it again). Without this line the page would open with no look chosen.

```js
}
```
Closes `loadSavedTheme`. That is the end of the file.
