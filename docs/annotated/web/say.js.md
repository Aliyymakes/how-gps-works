# say.js, line by line

Source: `web/say.js`

## What this file is for
This file holds one small tool, `say`, that puts a sentence into a message line on the page and makes that line flash briefly. The flash means that pressing something always gives a visible answer, even when the words are the same as last time.

## Which files it talks to
- [`web/step-geometry.js`](step-geometry.js.md), [`web/first-screen.js`](first-screen.js.md), [`web/step-relativity.js`](step-relativity.js.md) and [`web/step-signal.js`](step-signal.js.md): each imports `say` and uses it for their message lines. In [`web/step-geometry.js`](step-geometry.js.md) it writes the messages under the slider, the Reset button and for errors.
- It uses nothing from other files. It uses `node.animate`, a built-in browser tool for short animations.

## In three lines
1. Put the sentence into the message line.
2. If there is a sentence and the browser can animate, fade the line from dim to full brightness in 0.16 seconds.
3. That flash is what shows the user that the page answered.

New to code? See [how to read code](../how-to-read-code.md).

## The code, line by line

```js
// Put words in a message line and flash it briefly, so pressing something always gives a visible answer,
// even when the words are the same as before.
```
Two comment lines (a comment starts with `//`; the computer ignores it). They say what the function is for. Without them nothing breaks.

```js
export function say(node, text) {
```
Starts a function (a named recipe) called `say`. It is given two things: `node`, which is one element on the page (an element is one piece of the page, such as a paragraph, and the page's tree of elements is called the DOM), and `text`, the sentence to show. `export` makes it available to other files that `import` it. Without `export`, no other file could call it.

```js
  node.textContent = text;
```
Sets the words inside the element to `text`. `textContent` is the element's text; setting it replaces whatever was there. The browser treats it as plain words, never as page code, which is safe. This happens before the animate check below, so the text is already set by the time any flash is tried. Without this line the message would never appear.

```js
  if (text && node.animate) node.animate([{ opacity: 0.3 }, { opacity: 1 }], { duration: 160, easing: "ease" });
```
An `if` with one action. The condition is `text && node.animate`; `&&` means "and", so both parts must be true. `text` is true when the sentence is not empty, so an empty sentence (used to clear a line) does not flash. `node.animate` is true when this browser knows how to animate; very old browsers do not, and without this check they would stop with an error. When both hold, `node.animate(...)` plays a short animation on the element. The first list gives two frames: start with `opacity: 0.3` (30 % solid, so dim) and end at `opacity: 1` (fully solid). The `{ duration: 160, easing: "ease" }` part says it lasts 160 milliseconds (0.16 seconds) and starts and ends gently. Even if the sentence is exactly the same as before, the flash replays, so the user sees that the press was noticed. Without this line the text would still change, but a repeated sentence would show no sign of life.

```js
}
```
Ends the function.
