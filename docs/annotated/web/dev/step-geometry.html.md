# step-geometry.html, line by line

Source: `web/dev/step-geometry.html`

## What this file is for
**This is a developer test page. It is not part of the page judges see.** It mounts one section of the real page (the second rung, "does it matter where the satellites are?", the one with the sky and the spread-out versus bunched satellites) all by itself on an otherwise empty page, so a teammate can work on that section without loading all of [`index.html`](../../index.html.md). It loads the same [`theme.css`](../theme.css.md) and fonts as the real page and calls `mountGeometryStep`, which builds the section inside one empty box.

**Does it still work with today's code?** Yes, by reading it: `../theme.css` and `../theme.js` are the right paths from `web/dev/`, [`web/theme.js`](../theme.js.md) still exports `trackPointerLight` and `loadSavedTheme`, and [`web/step-geometry.js`](../step-geometry.js.md) still exports `mountGeometryStep(container)`, which is exactly how it is called. That function builds the section and, through [`web/startup.js`](../startup.js.md) and [`web/bridge.js`](../bridge.js.md), loads Python. In turn the section calls `coords.latlon_to_xyz`, `coords.satellite_from_sky`, `geometry.dop`, `scenario.make_pseudoranges`, `solver.solve_position` and `mapview.to_local` through the bridge; all six still exist in `mechanism/`. I did not run it in a browser. To open any of these pages you must serve the project folder over `http://` (for example run `python3 -m http.server` in the project's top folder and visit `http://localhost:8000/web/...`) because the browser refuses to load code modules or fetch files from a plain `file://` address. Python and numpy come from an internet address (a CDN), so you also need to be online. The address for this page is `http://localhost:8000/web/dev/step-geometry.html`: the bridge looks for the `mechanism/` folder next to `web/`, so the server must start in the project's top folder, not in `web/`.

## Which files it talks to
- `web/theme.css` (as `../theme.css`): the look. See [theme.css, line by line](../theme.css.md).
- `web/theme.js` (as `../theme.js`): remembered theme and pointer glow. See [theme.js, line by line](../theme.js.md).
- `web/step-geometry.js`: provides `mountGeometryStep`, which builds the whole section. See [step-geometry.js, line by line](../step-geometry.js.md).
- [`index.html`](../../index.html.md): mounts the same section into the real page; this page does the same alone.
- Nothing else links to this page.

## In three lines
1. Load the fonts and the theme, and give the page one empty box.
2. Apply the saved theme and switch on the pointer glow.
3. Hand the empty box to the section's `mount` function, which does everything else.

New to code? See [how to read code](../../how-to-read-code.md).

## The code, line by line

```html
<!doctype html>
<html lang="en" data-theme="dark">
```
`<!doctype html>` says this is a modern web page and `<html lang="en" data-theme="dark">` opens it: English, with the attribute `data-theme="dark"`, which [`theme.css`](../theme.css.md) reads to choose the dark colours. (An attribute is an extra label inside a tag.) [`theme.js`](../theme.js.md) may change it to `light` when the script runs, if the visitor chose light before.

```html
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
```
`<head>` opens the part with information about the page. `<meta charset="utf-8">` sets the alphabet so special characters display properly. `<meta name="viewport" content="width=device-width, initial-scale=1">` makes a phone use its real screen width instead of a zoomed-out desktop view. Without the viewport line the page would look tiny on a phone.

```html
<meta name="theme-color" content="#0a0a0a">
<title>Rung 2: geometry (test page)</title>
```
`<meta name="theme-color" content="#0a0a0a">` tells a phone's browser to colour its address bar near-black (`#0a0a0a` is the dark page background), so the browser frame matches the page. It only affects looks. Then `<title>` sets the text in the browser tab: "Rung 2: geometry (test page)". It marks the page as a test page.

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
```
Two `<link rel="preconnect">` tags tell the browser to start connecting to Google's font servers early (`fonts.googleapis.com` for the style sheet, `fonts.gstatic.com` for the font files; `crossorigin` is needed for the files). It only saves a little time. Nothing breaks without them.

```html
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Instrument+Sans:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap">
<link rel="stylesheet" href="../theme.css">
```
`<link rel="stylesheet">` loads a stylesheet, a file of CSS rules. The first loads the two fonts, Instrument Sans (for words) and JetBrains Mono (for numbers) from Google Fonts; `display=swap` shows text in a fallback font straight away and swaps in the real one when it arrives. The second, `../theme.css`, loads the project's theme. The `../` means "go up one folder", because this page lives in `web/dev/` and the theme is in `web/`. Without the second line the section would be unstyled.

```html
<style>
  main { max-width: 1100px; margin: 0 auto; padding: var(--s-6) var(--s-4); }
</style>
```
`<style>` opens CSS written into the page itself. The rule `main { max-width: 1100px; margin: 0 auto; padding: var(--s-6) var(--s-4); }` limits the content to 1100 pixels wide, centres it (`margin: 0 auto`: nothing above and below, equal automatic space left and right), and pads it by `var(--s-6)` = 32 px above and below and `var(--s-4)` = 16 px left and right (variables from [`theme.css`](../theme.css.md); a CSS variable is a named value). `</style>` closes the block. Without it the section would stretch across a wide screen edge to edge.

```html
</head>
<body>
<main id="step"></main>
```
`</head>` ends the head. `<body>` starts the visible page. `<main id="step"></main>` is the one empty box this page contains. `main` marks the page's main content (screen readers can jump straight to it). The `id="step"` is a unique name so the script can find the box. The section builds itself inside it. Without the box the script would have nowhere to put the section.

```html
<script type="module">
  import { trackPointerLight, loadSavedTheme } from "../theme.js";
  import { mountGeometryStep } from "../step-geometry.js";
```
`<script type="module">` starts JavaScript. `type="module"` makes it a module, which is what allows `import` lines. The first import brings in two helpers from `../theme.js`: `trackPointerLight` (a soft glow on cards that follows the pointer) and `loadSavedTheme` (apply the dark or light theme the visitor chose last time). `../` again means up one folder. The second import brings in `mountGeometryStep` from `../step-geometry.js`: the function that builds this section. Without imports the page would have no code to run.

```html
  loadSavedTheme();
  trackPointerLight();
```
The first call, `loadSavedTheme()`, reads the remembered theme from the browser's storage and sets `data-theme` on the top tag (dark if nothing was saved). The second, `trackPointerLight()`, makes the pointer glow follow the mouse over any card from then on. Without the first the page would never use the visitor's saved theme, and without the second the card glow would never follow the pointer.

```html
  mountGeometryStep(document.getElementById("step"));
```
`document.getElementById("step")` finds the empty box by its `id` (the page is a tree of elements called the DOM, the Document Object Model, and a script can look things up in it). That element is handed to `mountGeometryStep(...)`, which fills it with the section's headings, controls and drawings, and starts loading Python in the background. On screen the section starts with the heading "Does it matter where the satellites are?" and shows a status line while Python loads. Without this line the page would stay empty.

```html
</script>
</body>
</html>
```
`</script>` ends the JavaScript. `</body>` ends the visible page and `</html>` ends the whole page.
