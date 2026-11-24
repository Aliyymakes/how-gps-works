# theme-preview.html, line by line

Source: `web/theme-preview.html`

## What this file is for
**This is a developer test page. It is not part of the page judges see.** It is a showroom for [`web/theme.css`](theme.css.md): one screen with a sample sky drawing, a slider, three switches, three state badges and two buttons, all filled with made-up sample content, plus a button that flips between the dark and light themes. A designer opens it to check the look without waiting for the real page. It does no GPS maths and never talks to Python.

**Does it still work with today's code?** Yes, by reading it: [`theme.css`](theme.css.md) is in the same folder (the link `theme.css` is correct), and [`web/theme.js`](theme.js.md) still exports `trackPointerLight`, `loadSavedTheme` and `setTheme`, which is all the page imports. All the class names it uses (`card`, `btn`, `btn-primary`, `slider`, `toggle`, `toggle-track`, `inset`, `badge`, `is-ok`, `sky-ring`, and so on) still exist in `theme.css`. One thing is stale sample text only: the badge "within 5 m" does not match the real limit (`errorLimits.ok_m` is 10 m in [`web/config.js`](config.js.md)). I did not run it in a browser. To open any of these pages you must serve the project folder over `http://` (for example run `python3 -m http.server` in the project's top folder and visit `http://localhost:8000/web/...`) because the browser refuses to load code modules or fetch files from a plain `file://` address. Python and numpy come from an internet address (a CDN), so you also need to be online.

## Which files it talks to
- `web/theme.css`: provides the whole look; this page only adds a few layout rules of its own. See [theme.css, line by line](theme.css.md).
- `web/theme.js`: switches the theme and moves the card glow. See [theme.js, line by line](theme.js.md).
- Google Fonts: the page loads the two fonts from the internet. If you are offline it uses the fallback fonts named in [`theme.css`](theme.css.md).
- Nothing else uses this page.

## In three lines
1. Load the theme, the fonts and a handful of layout rules, then lay out sample content: a sky drawing in one card, controls in another.
2. Switch on the theme code: remembered theme, pointer glow, and a button that flips dark and light.
3. Show the slider's value as you drag it (sample only, no maths).

New to code? See [how to read code](../how-to-read-code.md).

## The code, line by line

```html
<!doctype html>
<html lang="en" data-theme="dark">
```
`<!doctype html>` says this is a modern web page; `<html lang="en" data-theme="dark">` opens the page, says the language is English, and adds the attribute `data-theme="dark"`. The attribute is the switch [`theme.css`](theme.css.md) reads: with `dark` the default colours apply, with `light` the light colour set takes over. The script below changes it. Without the attribute the page would start with no theme mark (the dark colours would still show, because dark is the default).

```html
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
```
`<head>` opens the part with information about the page. `<meta charset="utf-8">` sets the alphabet so characters like "µ" show correctly. `<meta name="viewport" content="width=device-width, initial-scale=1">` tells phones to use the real screen width instead of pretending to be a wide desktop, which is what makes the page fit a phone. Without the viewport line, a phone would show a tiny zoomed-out page.

```html
<title>Theme preview</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
```
`<title>` is the text in the browser tab. The two `<link rel="preconnect">` lines tell the browser to open the connections to Google's font servers early (`fonts.googleapis.com`, then `fonts.gstatic.com` with `crossorigin`, which the font files require). It only saves a little time; nothing breaks without them.

```html
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Instrument+Sans:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap">
<link rel="stylesheet" href="theme.css">
```
`<link rel="stylesheet">` loads a stylesheet, a file of CSS rules. The first loads the fonts Instrument Sans (weights 400, 500 and 600) and JetBrains Mono (400, 500) from Google Fonts; `display=swap` shows text at once in a fallback font and swaps to the real one when it arrives. The second, `href="theme.css"`, loads our theme from the same folder. Without the second line the page would have no styling at all.

```html
<style>
  /* Preview layout only. Not part of the theme. */
```
`<style>` opens a block of CSS written straight into the page, for rules only this page needs. The comment (CSS comments are `/* ... */`) says these are preview layout only and not part of the theme.

```html
  main { max-width: 960px; margin: 0 auto; padding: var(--s-7) var(--s-5); display: grid; gap: var(--s-5); }
  .grid { display: grid; grid-template-columns: 1.2fr 1fr; gap: var(--s-5); }
```
The page's main block: `main { max-width: 960px; margin: 0 auto; padding: ... }` limits the content to 960 pixels wide, centres it (`margin: 0 auto` means no margin above or below and automatic equal margins left and right), adds padding (`var(--s-7)` is 48 px above and below and `var(--s-5)` is 24 px left and right, both taken from [`theme.css`](theme.css.md)), and `display: grid; gap: var(--s-5)` stacks its children with 24 px between them. Line 14, `.grid`, makes a two-column layout: `grid-template-columns: 1.2fr 1fr` splits the width into 1.2 parts and 1 part (an `fr` is a share of the free space), so at the full 960 px width less 48 px of side padding and 24 px of gap, 888 px is shared: about 484 px and 404 px. Without them the page would be a full-width single column.

```html
  @media (max-width: 720px) { .grid { grid-template-columns: 1fr; } }
  .stack { display: grid; gap: var(--s-4); }
```
A media query: rules that apply only if a condition is true. `@media (max-width: 720px)` is true on screens 720 px wide or narrower, and there `.grid` becomes a single column (`1fr`), so the two cards stack on a phone. `.stack { display: grid; gap: var(--s-4); }` is a helper class: put the children in a column with 16 px between them. Without the media query the two columns would be squeezed on a phone.

```html
  .row { display: flex; align-items: center; justify-content: space-between; gap: var(--s-3); flex-wrap: wrap; }
  .sky { width: 100%; aspect-ratio: 1; display: block; }
  .readout { padding: var(--s-4); display: grid; gap: var(--s-1); }
  .big { font-size: 28px; }
```
More helper classes. `.row` lays children in a line (`display: flex`), centred up and down, spread to both ends (`justify-content: space-between`), 12 px apart, and allowed to wrap onto a new line on a narrow screen (`flex-wrap: wrap`). `.sky` makes the drawing fill its card's width and stay square (`aspect-ratio: 1`; `display: block` removes a small gap under pictures). `.readout` is the padding (16 px) and spacing (4 px) inside the "Position off by" box. `.big` makes a number 28 px. Without them these samples would have no layout.

```html
</style>
</head>
<body>
<main>
```
`</style>` ends the CSS block, `</head>` ends the head, `<body>` starts the visible page and `<main>` marks the page's main content (screen readers can jump straight to it). Everything between is the sample content.

```html
  <div class="row">
    <div class="stack" style="gap: var(--s-2)">
```
A `<div>`, a plain box with no look of its own, with `class="row"`: the header row. A class is a name that CSS rules and scripts can pick out. Inside is another `div` with classes `stack` and an inline `style` attribute, `gap: var(--s-2)`, which overrides the stack's 16 px gap to 8 px for this one box. Without them the header would not be laid out in a row.

```html
      <span class="label">Theme preview, sample content only</span>
      <h1>How does your phone know where you are?</h1>
      <p class="muted">Switch satellites off and drag the clock error. Watch the fix move.</p>
```
Three lines in the header. A `<span>` is a small inline piece of text; with `class="label"` it gets the small capital-letters caption look, here the words "Theme preview, sample content only", so nobody mistakes this page for the real one. `<h1>` is the main heading: "How does your phone know where you are?". The `<p class="muted">` is a quieter paragraph: "Switch satellites off and drag the clock error. Watch the fix move." Both are sample words.

```html
    </div>
    <button class="btn" id="theme-switch" type="button">Light theme</button>
  </div>
```
Line 30 closes the stack box. Line 31 is the theme button: `<button class="btn" id="theme-switch" type="button">`. `type="button"` says it does nothing by itself (a button inside a form would otherwise submit the form). Its words, "Light theme", are replaced by the script depending on the current theme. `id="theme-switch"` is the name the script uses to find it. Line 32 closes the row. Without the button there would be no way to try the light theme.

```html
  <div class="grid">
    <section class="card">
```
`<div class="grid">` is the two-column layout from the CSS above. `<section class="card">` is the first column: a card (rounded box, border, pointer glow from [`theme.css`](theme.css.md)). `<section>` is a tag for a themed part of the page.

```html
      <svg class="sky" viewBox="0 0 400 400" role="img" aria-label="Sample sky view with five satellites">
```
`<svg ...>` starts the sky drawing. SVG (scalable vector graphics) lets you draw shapes with tags, and it stays sharp at any size. `viewBox="0 0 400 400"` defines the drawing's own coordinate system: it is 400 units wide and 400 units tall, with (0, 0) at the top-left, and the browser scales it to the card. `role="img"` tells screen readers to treat the whole drawing as one picture, and `aria-label="Sample sky view with five satellites"` is the sentence they read aloud for it. `aria-*` attributes exist only to help assistive tools like screen readers; they do not change how the page looks. Without the label a blind visitor would hear nothing for this drawing.

```html
        <circle class="sky-ring" cx="200" cy="200" r="180"/>
        <circle class="sky-ring" cx="200" cy="200" r="120"/>
        <circle class="sky-ring" cx="200" cy="200" r="60"/>
```
Three rings, drawn as `<circle>` tags. `cx` and `cy` are the centre (200, 200: the middle of the 400 by 400 box) and `r` is the radius: 180, 120 and 60 units. The class `sky-ring` from [`theme.css`](theme.css.md) makes each an outline only, with no fill. So they are three circles inside each other, like the rings of a target, with the receiver at the middle. Without them the drawing would have no rings.

```html
        <line class="sky-signal" x1="200" y1="200" x2="120" y2="70"/>
        <line class="sky-signal" x1="200" y1="200" x2="310" y2="110"/>
        <line class="sky-signal" x1="200" y1="200" x2="80" y2="260"/>
        <line class="sky-signal" x1="200" y1="200" x2="290" y2="300"/>
```
Four straight dashed lines, `<line>` tags, from the centre (200, 200) to four points: (120, 70), (310, 110), (80, 260) and (290, 300). `x1`, `y1` are where the line starts and `x2`, `y2` where it ends. They stand for the signals from four satellites to the phone. The class `sky-signal` makes them dashed. Worked example, the first line: it runs from (200, 200) to (120, 70), which is 80 units left (200 - 120) and 130 units up (200 - 70) from the middle. They are sample positions, not the real satellite positions from [`web/config.js`](config.js.md).

```html
        <circle class="sky-sat" cx="120" cy="70" r="7"/>
        <circle class="sky-sat" cx="310" cy="110" r="7"/>
        <circle class="sky-sat" cx="80" cy="260" r="7"/>
        <circle class="sky-sat" cx="290" cy="300" r="7"/>
        <circle class="sky-sat is-off" cx="215" cy="345" r="7"/>
```
Five satellite dots, as small circles of radius 7 units, centred at (120, 70), (310, 110), (80, 260), (290, 300) and (215, 345). The first four sit at the ends of the four lines. The fifth has the classes `sky-sat is-off`, so it is drawn faded (20% opacity) to show a satellite that is switched off, and it has no line. Without them there would be no satellites.

```html
        <g class="is-ok"><circle class="sky-fix" cx="200" cy="200" r="10"/></g>
        <g class="is-warn"><circle class="sky-fix" cx="230" cy="185" r="10"/></g>
        <g class="is-bad"><circle class="sky-fix" cx="160" cy="235" r="10"/></g>
```
Three example "fix" marks, circles of radius 10 units that show a calculated position, each inside a `<g>` tag. `<g>` is an SVG group: a way to give several shapes one setting; here the group's class sets the colour that the circle's `currentColor` outline picks up. `is-ok` puts it in green at the true centre (200, 200), `is-warn` in amber at (230, 185) and `is-bad` in red at (160, 235). The further the mark is from the centre, the worse the error it shows. The three colours are the only colours on this page. Without them the colour states could not be previewed.

```html
      </svg>
    </section>
```
`</svg>` ends the drawing and `</section>` ends the first card.

```html
    <section class="card stack">
      <div class="slider">
        <div class="slider-head">
```
`<section class="card stack">` is the second column: a card whose children stack in a column. Inside is `<div class="slider">`, a stack made of a head row and the slider itself, and `<div class="slider-head">`, the row holding the label and the value, spread to opposite ends by [`theme.css`](theme.css.md).

```html
          <label for="clock">Phone clock error</label>
          <span class="num" id="clock-value">1.0 µs</span>
        </div>
```
`<label for="clock">Phone clock error</label>` is the slider's name; `for="clock"` connects it to the control with `id="clock"`, so clicking the words works the slider and screen readers read the name when the slider is focused. `<span class="num" id="clock-value">1.0 µs</span>` is the number beside it, in the number font. "µs" is microseconds (millionths of a second), and the 1.0 is the slider's starting value; the script updates it. Line 60 closes the head row.

```html
        <input id="clock" type="range" min="0" max="10" step="0.1" value="1">
      </div>
```
`<input id="clock" type="range" min="0" max="10" step="0.1" value="1">` is the slider. `type="range"` makes it a slider, `min` and `max` set its ends (0 and 10), `step="0.1"` makes it move in tenths (so 101 positions from 0 to 10) and `value="1"` starts it at 1. Line 62 closes the slider's box. Without it there would be no slider.

```html
      <label class="toggle"><input type="checkbox" checked><span class="toggle-track"></span>Satellite 1</label>
      <label class="toggle"><input type="checkbox" checked><span class="toggle-track"></span>Satellite 2</label>
      <label class="toggle"><input type="checkbox"><span class="toggle-track"></span>Satellite 5</label>
```
Three switches. Each `<label class="toggle">` contains a real checkbox (`<input type="checkbox">`) and an empty `<span class="toggle-track">`, then the words. [`theme.css`](theme.css.md) hides the checkbox and draws the track and knob in its place, so clicking either the switch or the words toggles it. The first two carry `checked` so they start on ("Satellite 1" and "Satellite 2"); the third, "Satellite 5", has no `checked` so it starts off. Without the real checkbox, keyboards and screen readers could not use the switch.

```html
      <div class="inset readout">
        <span class="label">Position off by</span>
        <span class="num big">300 m</span>
```
`<div class="inset readout">` is a smaller grey box inside the card (the `inset` style plus the layout from the page's own style block). It holds a caption (`<span class="label">Position off by</span>`) and a big number (`<span class="num big">300 m</span>`): the sample reading "300 m". The number is typed in by hand; nothing calculates it.

```html
        <div class="row" style="justify-content: flex-start">
          <span class="badge is-ok">within 5 m</span>
          <span class="badge is-warn">off by tens</span>
          <span class="badge is-bad">off by hundreds</span>
        </div>
      </div>
```
A row of three state badges. `<div class="row" style="justify-content: flex-start">` makes a row that packs to the left (the inline `style` overrides the row's usual spread-out setting). Each badge is a `<span class="badge ...">`: `is-ok` (green) says "within 5 m", `is-warn` (amber) "off by tens" and `is-bad` (red) "off by hundreds". Together they show the three colours the real page uses for errors. Lines 75 and 76 close the row and the readout box. (The "5 m" wording is only sample text; the real page uses the limits in [`web/config.js`](config.js.md), 10 m and 100 m.)

```html
      <div class="row" style="justify-content: flex-start">
        <button class="btn btn-primary" type="button">Add fourth satellite</button>
        <button class="btn" type="button">Reset</button>
      </div>
    </section>
```
The last row holds two buttons: a main one, `<button class="btn btn-primary" type="button">Add fourth satellite</button>` (white fill), and a plain one, `Reset`. They do nothing when pressed except show the hover and press effects from [`theme.css`](theme.css.md). Lines 81 and 82 close the row and the second card.

```html
  </div>
</main>
<script type="module">
```
`</div>` closes the two-column layout, `</main>` closes the main area, and `<script type="module">` opens the JavaScript. `type="module"` is what allows the `import` on the next line.

```html
  import { trackPointerLight, loadSavedTheme, setTheme } from "./theme.js";
  loadSavedTheme();
  trackPointerLight();
```
Line 86 imports three helper functions from [`theme.js`](theme.js.md): `trackPointerLight` (moves the glow on cards with the pointer), `loadSavedTheme` (reads the remembered theme from the browser's storage and applies it) and `setTheme` (switches theme and remembers it). Line 87 calls `loadSavedTheme()`: if the visitor chose light last time, the page becomes light now; otherwise it stays dark. Line 88 calls `trackPointerLight()`: from now on, when the pointer moves over a card, the glow follows it. Without these the page would never use the saved theme and the glow would never move.

```html
  const button = document.getElementById("theme-switch");
  const label = () => { button.textContent = document.documentElement.dataset.theme === "dark" ? "Light theme" : "Dark theme"; };
  label();
```
Line 89 finds the theme button by its `id`. Line 90 creates a tiny function called `label` that sets the button's words: if the current theme (`document.documentElement.dataset.theme`, the value of `data-theme` on the top `<html>` tag) is "dark" the button says "Light theme" (what pressing it would give you); otherwise it says "Dark theme". The `? :` is a short if-else: condition, then the value if true, then the value if false. Line 91 calls it once so the button's words are right when the page opens. Without it the button would keep its starting words even when a saved light theme is loaded.

```html
  button.addEventListener("click", () => {
    setTheme(document.documentElement.dataset.theme === "dark" ? "light" : "dark");
    label();
  });
```
Lines 92 to 95 add an event listener to the button: a function that waits for something to happen (here a `click`) and then runs. When clicked it calls `setTheme(...)` with the opposite theme (if the current one is "dark" then "light", otherwise "dark"), which updates `data-theme` on the page and saves the choice in the browser, and then calls `label()` to update the button words. The `() => { ... }` is an arrow function, a short way to write a nameless function. Without it the button would not do anything.

```html
  // Preview only: shows the slider value, does no GPS maths.
  const clock = document.getElementById("clock");
  clock.addEventListener("input", () => { document.getElementById("clock-value").textContent = `${Number(clock.value).toFixed(1)} µs`; });
```
A comment (`//` makes the rest of the line a note) saying this part is preview only: it shows the slider value and does no GPS maths. Line 97 finds the slider by its `id`. Line 98 adds an `input` event listener: the `input` event fires continuously while the slider is dragged. Each time, it takes the slider's `value` (a piece of text like "2.5"), turns it into a number with `Number(...)`, rounds it to one decimal place with `.toFixed(1)` and writes it plus " µs" into the `clock-value` span using a template string (words in backticks with `${...}` holes for values). Worked example: dragging to 7 shows "7.0 µs"; dragging to 2.5 shows "2.5 µs". Without it the number beside the slider would stay at "1.0 µs".

```html
</script>
</body>
</html>
```
`</script>` ends the JavaScript, `</body>` ends the visible page and `</html>` ends the whole page.
