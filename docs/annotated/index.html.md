# index.html, line by line

Source: `index.html`

## What this file is for
This is the page itself, the one file a visitor opens. It holds the words, the map drawing, the slider, the buttons and the switches, plus the page's own layout rules. It does not do any maths or react to clicks: it only lays things out. The JavaScript files it loads at the bottom find these pieces by their `id` names and make them work.

## Which files it talks to
- [`web/theme.css`](web/theme.css.md): the shared look (colours, fonts, cards, buttons, switches). This file only adds layout on top. See `docs/ui-guide.md`.
- [`web/bridge.js`](web/bridge.js.md): the address of Pyodide (a copy of Python that runs inside the browser; `bridge.js` downloads it) is repeated here in a `modulepreload` line so the download can start early. See [bridge.js explained](web/bridge.js.md).
- [`web/first-screen.js`](web/first-screen.js.md): finds the ids below (`map`, `clock`, `solve`, `switches` and so on) and drives the first screen. It calls Python through the bridge: `coords.latlon_to_xyz` and `coords.satellite_from_sky` ([coords.py](mechanism/coords.py.md)), `scenario.make_pseudoranges` ([scenario.py](mechanism/scenario.py.md)), `solver.solve_position` ([solver.py explained](mechanism/solver.py.md)), and `mapview.to_local` and `mapview.distance_lines` ([mapview.py](mechanism/mapview.py.md)).
- [`web/step-geometry.js`](web/step-geometry.js.md), [`web/step-signal.js`](web/step-signal.js.md), [`web/step-relativity.js`](web/step-relativity.js.md): each fills the empty `<div>` placed for it near the bottom.
- Outside the repo: Google Fonts (the two typefaces) and the Pyodide download address.

## In three lines
1. The head asks the browser to start downloading fonts, Pyodide and the shared style sheet early, and adds a few layout rules.
2. The body is the first screen: a heading, a ground map with a legend, then the controls (clock slider, error readout, solve button, satellite switches, reset).
3. Three more empty sections and three link sentences follow, and the scripts at the bottom fill the sections in.

New to code? See [how to read code](how-to-read-code.md). A few web ideas used a lot below:

- The page is built from *elements*. An element is written as a start tag and an end tag around its contents, like `<p>words</p>`. Extra information goes inside the start tag as *attributes*, like `id="map"` (a unique name) or `class="note"` (a label shared by many elements, used by CSS and JavaScript to find them). The nested structure of elements is called the DOM.
- *CSS* is the list of rules that says how elements look. A rule is `selector { property: value; }`: the selector says which elements, each property line says one thing about them.
- A *CSS variable* is a named value written `--name: ...` and used as `var(--name)`. The names here (`--s-4`, `--text-muted`, and so on) are defined in [`web/theme.css`](web/theme.css.md), so one change there changes every use. In [`theme.css`](web/theme.css.md), `--s-1` to `--s-6` are spaces of 4, 8, 12, 16, 24 and 32 pixels.
- *Screen readers* are programs that read a page aloud for blind people. They use the structure of the page, and extra `aria-...` attributes (ARIA) that describe what something is or when it changes.

## The code, line by line

```html
<!doctype html>
```
Tells the browser this is a modern HTML page (HTML is the language web pages are written in). Without it the browser switches to an old, quirky mode and layout can go wrong.

```html
<html lang="en" data-theme="dark">
```
Opens the `<html>` element that wraps everything. `lang="en"` says the page is in English, so screen readers pronounce it correctly and browsers can offer translation. `data-theme="dark"` is a custom attribute that [`theme.css`](web/theme.css.md) reads to choose the dark colours (it also has a light set). It is the default look.

```html
<head>
```
Opens the `<head>`: information about the page that is not drawn in the page itself.

```html
<meta charset="utf-8">
```
Says the file's text is stored in the UTF-8 way, which includes characters such as the `µ` and `×` signs used below. Without it these could turn into garbage.

```html
<meta name="viewport" content="width=device-width, initial-scale=1">
```
Tells phones to use the real screen width for the page (`width=device-width`) and not to zoom out (`initial-scale=1`). Without it a phone shows a tiny shrunken copy of a desktop page.

```html
<meta name="theme-color" content="#0a0a0a">
```
Sets the colour of the browser's own toolbar on phones to `#0a0a0a`, nearly black, so it matches the dark page.

```html
<title>How does your phone know where you are?</title>
```
The page's title, shown on the browser tab: `How does your phone know where you are?`

```html
<link rel="preconnect" href="https://cdn.jsdelivr.net" crossorigin>
```
Asks the browser to open a network connection to `cdn.jsdelivr.net`, where Pyodide is hosted, ahead of time, so the later download starts faster. `crossorigin` is needed because the files will be fetched in the way scripts are.

```html
<!-- Same Pyodide address as PYODIDE_BASE in web/bridge.js: change both together. -->
```
A comment, written `<!-- ... -->`. It warns that the web address on the next line must match `PYODIDE_BASE` in [`web/bridge.js`](web/bridge.js.md), and both must be changed together.

```html
<link rel="modulepreload" href="https://cdn.jsdelivr.net/pyodide/v314.0.8/full/pyodide.mjs" crossorigin>
```
`modulepreload` asks the browser to start downloading the Pyodide loader script now, while the page is still being read, instead of waiting until the JavaScript asks for it. This saves time on the slow first visit. The address must be identical to the one in [`bridge.js`](web/bridge.js.md), or the early download is wasted.

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
```
Two more early connections, to Google's font servers (`fonts.googleapis.com`, which gives the font list, and `fonts.gstatic.com`, which holds the font files). The second needs `crossorigin` because font files are fetched that way.

```html
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Instrument+Sans:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap">
```
Loads the two typefaces: Instrument Sans (weights 400, 500, 600, for normal text) and JetBrains Mono (weights 400, 500, for numbers). `display=swap` means text appears at once in a fallback font and switches when the real font arrives, so the page never shows blank text while waiting.

```html
<link rel="stylesheet" href="web/theme.css">
```
Loads the shared style sheet, [`web/theme.css`](web/theme.css.md): colours, fonts, cards, buttons and switches. The page's layout rules below rely on its CSS variables.

```html
<style>
```
Opens a `<style>` element: CSS written directly in the page. These rules are only for this page's layout. The CSS lines below are quoted a few at a time.

```html
  /* Layout for this page only. Colours, fonts and radii come from theme.css. */
```
A CSS comment, written `/* ... */`. It says what this style block is for: layout only, since colours, fonts and rounded-corner sizes come from [`theme.css`](web/theme.css.md).

```html
  main { max-width: 1100px; margin: 0 auto; padding: var(--s-6) var(--s-4); display: grid; grid-template-columns: minmax(0, 1fr); gap: var(--s-5); }
```
The rule for `main`, the page's main content. `max-width: 1100px` stops it getting wider than 1100 pixels on big screens. `margin: 0 auto` puts zero space above and below and splits the leftover space equally left and right, which centres it. `padding: var(--s-6) var(--s-4)` is space inside the edge: 32 pixels top and bottom, 16 on the sides. `display: grid` lays the children out as a grid, with a single column `minmax(0, 1fr)` (width from 0 up to all the space: see the next comment), and `gap: var(--s-5)` leaves 24 pixels between rows. Without it the page would stretch edge to edge.

```html
  /* Grid columns may shrink below their content, so nothing is cut off at 200 % zoom. */
```
A comment explaining the trick in the next rule: normally a grid column cannot shrink smaller than its content. `minmax(0, 1fr)` lets it shrink to nothing, so long lines wrap rather than stick out. This keeps everything visible when a visitor zooms to 200 %.

```html
  .intro, .stack, .readout, .slider { grid-template-columns: minmax(0, 1fr); }
```
Applies the same single, shrinkable column to four kinds of element: `.intro`, `.stack`, `.readout` and `.slider` (a dot before a name means "elements with that class"). Commas mean "all of these".

```html
  .slider-head { flex-wrap: wrap; column-gap: var(--s-3); }
```
In the slider's title row (`.slider-head`), `flex-wrap: wrap` lets the label and the value drop onto two lines when there is not enough room, and `column-gap: var(--s-3)` keeps 12 pixels between them when side by side.

```html
  .intro { display: grid; gap: var(--s-2); }
```
The intro block is a grid with 8 pixels between its pieces (`--s-2`).

```html
  h1 { text-wrap: balance; }
```
For the heading `h1`, `text-wrap: balance` makes the browser spread the words evenly across lines, so a heading that wraps does not leave one lonely word.

```html
  .grid { display: grid; grid-template-columns: minmax(0, 1fr); gap: var(--s-5); }
```
The `.grid` class (the two big cards: map and controls) is a grid with one shrinkable column and a 24 pixel gap. This is the layout for narrow screens such as phones: the cards stack.

```html
  @media (min-width: 760px) { .grid { grid-template-columns: 1.1fr 1fr; align-items: start; } }
```
A *media query*: `@media (min-width: 760px)` means "only apply the rule inside the braces when the window is at least 760 pixels wide". Then `.grid` gets two columns, `1.1fr 1fr`, which share the room in proportion 1.1 to 1 (an `fr` is one share), and `align-items: start` aligns both cards to the top instead of stretching them to equal height. Worked example: if 1,000 px is left after the gap, one share is 1,000 / 2.1 = 476.2 px, so the map card is 1.1 x 476.2 = 523.8 px and the controls card 476.2 px. Below 760 px the cards stack.

```html
  .stack { display: grid; gap: var(--s-4); }
```
`.stack` is a grid with 16 pixels (`--s-4`) between its children: a vertical pile of controls.

```html
  .map { width: 100%; aspect-ratio: 1; display: block; }
```
The map drawing (`.map`): `width: 100%` fills its card, `aspect-ratio: 1` keeps it square (height equals width), and `display: block` removes the small gap browsers leave under drawings that sit in a line of text.

```html
  .map-frame { fill: none; stroke: var(--line-strong); }
  .map-true { stroke: var(--text-muted); stroke-width: 1.5; fill: none; }
  .map-wait { fill: var(--text-muted); font: 400 14px var(--font-sans); }
```
Three rules for the parts of the map drawing (SVG is described later). `.map-frame`: the border square has no fill and a stroke (outline) in `--line-strong`. `.map-true`: the "where it really is" cross has a muted-grey outline 1.5 wide, no fill. `.map-wait`: the waiting text is filled in the muted colour, with the font shorthand `400 14px var(--font-sans)` meaning weight 400, size 14 pixels, the sans-serif font.

```html
  .intro p { max-width: 60ch; }
```
Limits paragraphs inside the intro to `60ch`: sixty times the width of the letter 0, about 60 characters per line, which is comfortable to read.

```html
  .map-key { list-style: none; margin: var(--s-3) 0 0; padding: 0; display: grid; gap: var(--s-1); font-size: var(--text-sm); color: var(--text-muted); }
```
The map key list (`.map-key`): `list-style: none` removes bullet points, `margin: var(--s-3) 0 0` gives 12 pixels above and nothing elsewhere, `padding: 0` removes the default indent, it is a grid with 4 pixels between entries, and the text is small (`--text-sm`, 14 pixels) and muted grey.

```html
  .map-key li { display: flex; align-items: center; gap: var(--s-2); }
```
Each key entry (`li`) lays out its small picture and its words in a row (`display: flex`), centred up and down, 8 pixels apart.

```html
  .map-key svg { width: 24px; height: 12px; flex: none; }
```
The small picture in each entry is 24 by 12 pixels, and `flex: none` stops the row squeezing it smaller.

```html
  .is-ok-sample { color: var(--text); }
```
Gives the sample dot in the key the full text colour. The "where the phone thinks it is" dot normally takes its colour from its state (see `.map-dot` below); this sample has no state, so it is given one.

```html
  .guide-target { border: 1px solid transparent; border-radius: var(--r-inner); padding: var(--s-4); }
```
The `.guide-target` class marks the three groups the guide highlights. Each gets a 1 pixel border that is invisible (`transparent`) so that, when it turns visible, nothing moves. `border-radius: var(--r-inner)` rounds the corners, and `padding: var(--s-4)` is 16 pixels of room inside.

```html
  .guide-target.highlight { border-color: var(--accent); }
```
When a guide target also has the `highlight` class, its border takes the accent colour (white in the dark theme). The page's code adds and removes `highlight` to show which control to use next.

```html
  .hint { font-size: var(--text-sm); font-weight: 500; color: var(--text); opacity: 0; transition: opacity var(--dur-small) ease; }
  .hint-done { font-size: var(--text-sm); color: var(--text); opacity: 0; transition: opacity var(--dur-small) ease; }
  .hint.is-shown, .hint-done.is-shown { opacity: 1; }
```
The guide's sentences. `.hint` is small, medium weight, and fully see-through (`opacity: 0`); `.hint-done` is the same without the weight. `transition: opacity var(--dur-small) ease` makes a change of opacity fade smoothly over `--dur-small` (180 milliseconds) instead of jumping. The line `.hint.is-shown, .hint-done.is-shown { opacity: 1; }` (two classes written together mean "an element with both") makes a hint visible when the code adds `is-shown`. Adding the class after the hint appears is what makes the fade run.

```html
  .map-line { stroke: var(--text-muted); stroke-width: 1.5; fill: none; transition: opacity var(--dur-small) ease; }
  .map-line.is-hidden { opacity: 0; }
```
The distance lines on the map. `.map-line` gives each line the muted colour, 1.5 width, no fill, and a fade on opacity. `.map-line.is-hidden { opacity: 0; }` fades a line out when the code marks it hidden (for example a line that lies off the map) while keeping it in the page.

```html
  .map-dot { fill: currentColor; fill-opacity: 0.25; stroke: currentColor; stroke-width: 2; }
```
The dot for "where the phone thinks it is": `currentColor` means "whatever the text colour is here", so the dot's colour follows the good / warning / bad state class. It is filled at 25 % opacity (`fill-opacity: 0.25`) with a solid outline 2 wide.

```html
  .map-caption { margin-top: var(--s-3); font-size: var(--text-sm); }
```
The caption under the map gets 12 pixels of space above and small text.

```html
  .badge[hidden] { display: none; }
```
The `hidden` attribute normally hides an element. But `.badge` in [`theme.css`](web/theme.css.md) sets `display: inline-flex`, and a stylesheet rule overrides the browser's built-in hiding, so the badge would show even when marked `hidden`. This rule puts the hiding back, only for badges that have the attribute.

```html
  .highlight { border-color: var(--accent); }
```
A second, general `.highlight` rule giving the accent border to anything with that class. It repeats the effect of the `.guide-target.highlight` rule above for elements that are not `.guide-target`.

```html
  .readout { padding: var(--s-4); display: grid; gap: var(--s-2); }
```
The error readout box: 16 pixels of padding inside, laid out as a grid with 8 pixels between its parts.

```html
  .big { font-size: var(--text-xl); }
```
`.big` makes the big error number large, `--text-xl` (32 pixels).

```html
  .note { font-size: var(--text-sm); color: var(--text-muted); min-height: 1.5em; }
```
Message lines (`.note`): small and muted, with a minimum height of `1.5em`. An `em` is the current font size, so at 14 pixels it is 21 pixels. A line of text keeps its room even when empty.

```html
  /* An empty message line takes no room, except where a control sits below it: those keep their height so nothing moves when words appear. */
  .note:empty { min-height: 0; }
```
A comment, then a rule. `.note:empty { min-height: 0; }`: a message line with nothing in it takes no room, so there are no blank gaps. The comment states the exception handled in the next rule: where a control sits below, the line keeps its height so nothing jumps when words appear.

```html
  #msg-slider:empty, #msg-readout:empty, #msg-solve:empty, #msg-switch:empty { min-height: 1.5em; }
```
The exception. These ids (a `#` before a name means "the element with that id") are the message lines under the slider, the readout, the solve button and the satellite switches. For them `min-height: 1.5em` (21 pixels) is set again even when empty. An id selector is more specific than the `:empty` rule above, so it wins.

```html
  h2.label, h3.label { margin-bottom: var(--s-3); }
```
Section titles (`h2.label`, `h3.label`: a heading with the `label` class) get 12 pixels of space below.

```html
  .switches { display: grid; grid-template-columns: 1fr 1fr; column-gap: var(--s-4); }
```
The satellite switches (`.switches`) are two equal columns (`1fr 1fr`) with 16 pixels between columns, so four switches make a 2 by 2 block.

```html
  @media (max-width: 359px) { .switches { grid-template-columns: minmax(0, 1fr); } }
```
On very narrow screens, narrower than 360 pixels (`max-width: 359px`), the switches go back to one column so each has room.

```html
  .actions { display: flex; flex-wrap: wrap; gap: var(--s-3); }
```
The row holding the reset button: a flex row that may wrap to a second line (`flex-wrap: wrap`), 12 pixels between buttons.

```html
  .btn:disabled, input:disabled + .toggle-track, input[type="range"]:disabled { opacity: 0.4; cursor: not-allowed; }
```
How anything switched off (`:disabled`) looks: a disabled button, a disabled satellite switch's track (`input:disabled + .toggle-track`: the track element right after a disabled input), and a disabled slider all go to `opacity: 0.4` (faded) with a `not-allowed` mouse pointer. The controls are disabled until Python has loaded.

```html
  .btn:disabled:hover { border-color: var(--line-strong); }
```
A disabled button should not react to the mouse. [`theme.css`](web/theme.css.md) makes buttons get an accent border on hover; this puts the normal border (`--line-strong`) back for disabled ones.

```html
  .btn-primary:disabled:hover { border-color: var(--accent); }
```
Same, but for the main (primary) button, whose normal border is the accent colour.

```html
  .btn { touch-action: manipulation; }
```
`touch-action: manipulation` on buttons removes the old delay phones used to wait for a possible double-tap-to-zoom, so taps feel instant.

```html
  input[type="range"] { touch-action: pan-y; }
```
On the slider, `touch-action: pan-y` lets a finger scroll the page up and down, while sideways movement belongs to the slider. Without it, a finger on the slider could lock page scrolling on phones.

```html
  /* 3:1 against the card for the slider track and the switch outline when off (was 1.7:1). */
```
A comment: the slider track and the unchecked switch outline use the muted grey so they reach a contrast of 3 to 1 against the card (accessibility: it was 1.7 to 1 and too faint).

```html
  input[type="range"]::-webkit-slider-runnable-track { background: var(--text-muted); }
  input[type="range"]::-moz-range-track { background: var(--text-muted); }
```
The line the slider thumb slides along (the "track") is coloured `--text-muted`. It is written twice, with `-webkit-` for Chrome and Safari and `-moz-` for Firefox, because the two browser families name this part differently.

```html
  .toggle input:not(:checked) + .toggle-track { box-shadow: inset 0 0 0 1px var(--text-muted); }
```
When a switch is off (`:not(:checked)`), its track gets a 1 pixel inner outline (`box-shadow: inset 0 0 0 1px`) in the muted colour, so an off switch is still easy to see.

```html
  /* theme.css's reduced-motion rule does not reach pseudo-elements: stop the switch knob and slider thumb moving. */
```
A comment: [`theme.css`](web/theme.css.md) already slows motion for people who ask for less movement, but its rule does not reach the knob and the slider thumb (they are drawn as "pseudo-elements", parts that are not their own elements), so the next rules stop them moving.

```html
  @media (prefers-reduced-motion: reduce) {
```
A media query that applies only if the visitor has asked their computer to reduce motion (`prefers-reduced-motion: reduce`), which helps people made unwell by animations.

```html
    .toggle-track::after { transition-property: background-color; }
```
On the switch knob, the only thing that still changes smoothly is the background colour (so the knob no longer slides).

```html
    input[type="range"]::-webkit-slider-thumb { transition: none; }
```
The slider thumb gets no transition at all, so it does not grow smoothly.

```html
  }
```
Closes the reduced-motion block.

```html
  /* 18 px (0.9 of --text-lg), no max-width: WebKit reports no first paint while the CDN is slow with 16 px text or a capped width here (test_speed). */
```
A comment giving a reason for the next rule, taken from the team's speed test (`test_speed`): the link sentences are 18 pixels (0.9 of the large text size) and have no maximum width, because of a problem the test found in Safari-type browsers (WebKit). With 16 pixel text or a capped width, those browsers did not report a "first paint" (the moment something is first drawn on screen) while the CDN (the public file server Pyodide is downloaded from) was slow.

```html
  .link-line { font-size: calc(var(--text-lg) * 0.9); color: var(--text-muted); text-wrap: balance; }
```
The link sentences between sections (`.link-line`): `calc(var(--text-lg) * 0.9)` is 20 pixels x 0.9 = 18 pixels, muted colour, and `text-wrap: balance` for even lines.

```html
  .link-line strong { color: var(--text); }
```
Bold words in a link sentence (`strong`) go back to the full text colour, so the "but" and "Therefore" stand out.

```html
  #step-geometry, #step-signal, #step-relativity { margin-top: var(--s-6); }
```
The three empty section holders get 32 pixels of space above (`--s-6`), separating the sections.

```html
</style>
```
Closes the `<style>` block.

```html
</head>
```
Closes the `<head>`.

```html
<body>
```
Opens the `<body>`: everything that is drawn on the page.

```html
<main>
```
Opens `<main>`, the main content. Screen readers can jump straight to it. The `main` CSS rule above applies here.

```html
  <header class="intro">
```
Opens the intro block, a `<header>`. `class="intro"` links it to the intro rules above.

```html
    <h1>How does your phone know where you are?</h1>
```
The page's main heading, `h1`: `How does your phone know where you are?`.

```html
    <p>Each satellite's signal says when it left. Your phone times the trip, and travel time × the speed of light = distance. Each distance draws one line on the map, and you are where the lines meet.</p>
```
The first paragraph (`<p>`) tells the whole idea in one go: each satellite's signal says when it left, the phone times the trip, and travel time x the speed of light = distance.

```html
    <p class="muted">That only works if the phone's clock is right. Make it wrong and watch what happens.</p>
```
A second paragraph with the class `muted` (a muted colour from [`theme.css`](web/theme.css.md)): `That only works if the phone's clock is right. Make it wrong and watch what happens.`

```html
  </header>
```
Closes the header.

```html
  <div class="grid">
```
Opens `div class="grid"`, a generic box (`div`) that holds the two cards side by side, or stacked on a phone (see the two `.grid` rules in the style block above).

```html
    <section class="card" aria-labelledby="map-title">
```
Opens the first card: a `<section>`, with the shared `card` look. `aria-labelledby="map-title"` says that the element with that id (the heading on the next line) is this section's name, so screen readers announce it as "Ground map".

```html
      <h2 class="label" id="map-title">Ground map</h2>
```
The card's heading `Ground map`, with `id="map-title"` for the line above to point to.

```html
      <svg class="map" id="map" viewBox="0 0 400 400" role="img" aria-label="Ground map. Each satellite draws a distance line. The dot is where the phone thinks it is.">
```
Opens an `<svg>`, the map. SVG is a way to draw shapes with text commands inside a page, so the drawing stays sharp at any size. `viewBox="0 0 400 400"` sets its inner coordinates: 0 to 400 across and down, regardless of the pixel size on screen; the code scales positions to this: `MAP_SIZE` (400) in [`web/first-screen.js`](web/first-screen.js.md) is the size every map position is scaled to. `role="img"` tells screen readers to treat it as one picture, and `aria-label` is the description they read: `Ground map. Each satellite draws a distance line. The dot is where the phone thinks it is.`

```html
        <rect class="map-frame" x="0.5" y="0.5" width="399" height="399"/>
```
The border: a rectangle at x 0.5, y 0.5, 399 wide and 399 high (half a unit in, so the 1 unit outline is not cut off at the edge), with the `map-frame` look from the CSS.

```html
        <g class="map-true" id="map-true"></g>
```
A group `<g>` (a container for shapes) with id `map-true`, empty for now. The code puts the cross "where it really is" in it.

```html
        <g id="map-lines"></g>
```
An empty group `map-lines`, which holds the distance lines the code draws, in front of the true-position cross.

```html
        <g id="map-dot" class="is-ok" style="display: none"><circle class="map-dot" r="9"/></g>
```
A group `map-dot` for the "where the phone thinks it is" dot. `class="is-ok"` is its starting colour state. `style="display: none"` hides it until the code has a position. It contains a circle of radius 9 with the `map-dot` look. The code moves it by changing its centre numbers.

```html
        <text id="map-wait" class="map-wait" x="200" y="240" text-anchor="middle">The map appears when Python has loaded.</text>
```
The waiting text, `The map appears when Python has loaded.`, centred (`text-anchor="middle"`) horizontally in the middle of the square (x 200) and low down (y 240). It sits below the middle on purpose: the "where it really is" cross is drawn in the middle and its arms end at y 212, so words at y 200 were drawn over the cross. The code hides it once the map is ready.

```html
      </svg>
```
Closes the SVG.

```html
      <ul class="map-key" aria-label="Map key">
```
Opens the map key, a list (`<ul>`). `aria-label="Map key"` names the list for screen readers.

```html
        <li><svg viewBox="0 0 24 12" aria-hidden="true"><line class="map-line" x1="1" y1="6" x2="23" y2="6"/></svg> A distance line: one satellite says you are somewhere on it</li>
```
The first key item (`<li>`): a tiny 24 by 12 drawing of a line from x 1 to x 23 at height 6 (`<line>`), followed by `A distance line: one satellite says you are somewhere on it`. `aria-hidden="true"` on the drawing hides it from screen readers, since it only repeats what the words say.

```html
        <li><svg viewBox="0 0 24 12" aria-hidden="true"><circle class="map-dot is-ok-sample" cx="12" cy="6" r="4"/></svg> Where the phone thinks it is</li>
```
The second item: a little circle of radius 4 at the centre (12, 6) of its drawing, with the sample colour class, then `Where the phone thinks it is`.

```html
        <li><svg viewBox="0 0 24 12" aria-hidden="true"><path class="map-true" d="M6 6h12M12 0v12"/></svg> Where it really is</li>
```
The third item: a cross drawn by a `<path>`. In its `d` text, `M6 6` moves to (6, 6), `h12` draws 12 across, `M12 0` moves to (12, 0), and `v12` draws 12 down. Then `Where it really is`.

```html
      </ul>
```
Closes the list.

```html
      <p class="map-caption muted" id="map-caption" role="status" aria-live="polite"></p>
```
The caption under the map: empty at the start, filled in by the code with how wide the map is (for example `The map is about 2 km wide. North is up.`), or that the phone's position is off the edge, plus how many distance lines have moved off the map. `role="status"` and `aria-live="polite"` make a screen reader read out any change to it when it next has a pause, without cutting off what it is saying. The pattern is repeated on every message line below.

```html
    </section>
```
Closes the first card.

```html
    <section class="card stack" aria-label="Controls">
```
Opens the second card, the controls. `class="card stack"` gives it both the card look and a vertical pile. `aria-label="Controls"` names it.

```html
      <p class="note" id="status" role="status" aria-live="polite">Loading the maths…</p>
```
The status line, shown first: `Loading the maths…`. The code changes it while Python loads and shows failure messages here.

```html
      <div class="slider inset guide-target highlight" id="block-slider">
```
Opens the slider block. `slider` and `inset` are look classes from [`theme.css`](web/theme.css.md), and `guide-target highlight` make it the first step of the guide, with the highlight border visible from the start. `id="block-slider"` lets the code switch the highlight.

```html
        <p class="hint" id="hint-1" hidden>Step 1. Drag this slider to the right.</p>
```
The first hint: `Step 1. Drag this slider to the right.` The `hidden` attribute hides it at first; the code reveals it.

```html
        <div class="slider-head">
```
A row (`.slider-head`) holding the title and the current value.

```html
          <label for="clock">Make the phone's clock wrong</label>
```
A `<label>` is the visible name of a form control. `for="clock"` ties it to the control whose id is `clock`, so clicking the words focuses the slider, and screen readers announce the slider as `Make the phone's clock wrong`.

```html
          <span class="num" id="clock-value">0.00 µs</span>
```
The slider's current value, shown starting at `0.00 µs` (microseconds, millionths of a second). The class `num` uses the number font. The code updates this text.

```html
        </div>
```
Closes the row.

```html
        <input id="clock" type="range" value="0" disabled>
```
The slider itself: an `<input>` of `type="range"`, a draggable bar. `value="0"` starts it at the left end. `disabled` keeps it switched off until Python has loaded. What switches it on: `start()` in [`web/first-screen.js`](web/first-screen.js.md) waits (through `whenPythonReady`) for Python, builds the scene with `buildScene`, then calls `setControlsDisabled(false)`. No range is written here: `setupControls` in the same file sets the smallest value to 0, the largest to 60 and the step to 1. With the clock settings in [`web/config.js`](web/config.js.md) (0 to 3 microseconds in steps of 0.05) that is 3e-6 / 5e-8 = 60 steps, and each step is 0.05 microseconds.

```html
        <p class="note" id="msg-slider" role="status" aria-live="polite"></p>
```
The message line under the slider, empty until the code has something to say.

```html
      </div>
```
Closes the slider block.

```html
      <div class="inset readout">
```
Opens the error readout box, an `inset` look with the `readout` layout rules.

```html
        <span class="label">Position off by</span>
```
The small heading `Position off by`, in the label look.

```html
        <span class="num big" id="error-value">–</span>
```
The error number, big and in the number font, starting as an en dash `–` (no value yet). The code writes the error in metres here.

```html
        <div><span class="badge is-ok" id="error-badge" hidden></span></div>
```
A box holding the badge, a small pill. The `badge` look and `is-ok` colour come from [`theme.css`](web/theme.css.md). It is `hidden` until there is a result, and the code then writes words such as `Good fix` into it and changes the colour class.

```html
        <p class="note" id="msg-readout" role="status" aria-live="polite"></p>
```
A message line for the readout.

```html
      </div>
```
Closes the readout.

```html
      <div class="stack guide-target" id="block-solve" style="gap: var(--s-2)">
```
Opens the solve block: a vertical pile, a guide target, `id="block-solve"`, with a style written inline in the element (`style="gap: var(--s-2)"`) that reduces the spacing to 8 pixels.

```html
        <p class="hint" id="hint-2" hidden>Step 2. The lines no longer meet. Press this button.</p>
```
The second hint, `Step 2. The lines no longer meet. Press this button.`, hidden until its turn.

```html
        <button class="btn btn-primary" id="solve" type="button" aria-pressed="false" disabled>Let the phone solve for its clock</button>
```
The solve button. `class="btn btn-primary"`: the main button look. `type="button"` says it does nothing by itself (inside forms, buttons submit them). `aria-pressed="false"` tells screen readers it is a toggle button that is currently off; the code flips it to true. `disabled` keeps it off until Python is ready. Its words are `Let the phone solve for its clock`. This is the control that makes the page ask Python to run `solver.solve_position` with the clock solved for, see [solver.py explained](mechanism/solver.py.md).

```html
        <p class="note" id="msg-solve" role="status" aria-live="polite"></p>
```
The message line for the solve button.

```html
      </div>
```
Closes the solve block.

```html
      <div class="stack guide-target" id="block-switches" style="gap: var(--s-1)">
```
Opens the satellite block, the third guide target, with a tight 4 pixel gap (`--s-1`).

```html
        <p class="hint" id="hint-3" hidden>Step 3. Now switch one satellite off.</p>
```
The third hint: `Step 3. Now switch one satellite off.`

```html
        <span class="label" id="switch-label">Satellites</span>
```
A plain label, `Satellites`, with an id so the next line can point to it. It is a `<span>` (an inline wrapper), not a form label, because it names a group, not one control.

```html
        <div class="switches" id="switches" role="group" aria-labelledby="switch-label"></div>
```
The container for the switches. It starts empty: the code creates one switch per satellite in [`config.js`](web/config.js.md) (four). `role="group"` says its contents belong together, and `aria-labelledby="switch-label"` names the group `Satellites` for screen readers.

```html
        <p class="note" id="msg-switch" role="status" aria-live="polite"></p>
```
The message line for the switches, for example when too few satellites are on.

```html
      </div>
```
Closes the satellite block.

```html
      <div class="stack" style="gap: var(--s-2)">
```
Opens the last control block, with an 8 pixel gap.

```html
        <div class="actions">
```
A row for buttons (`.actions`).

```html
          <button class="btn" id="reset" type="button" disabled>Reset</button>
```
The `Reset` button: normal look, `type="button"`, disabled until Python is ready. The code puts the page back to its start state when it is pressed.

```html
        </div>
```
Closes the button row.

```html
        <p class="note" id="msg-reset" role="status" aria-live="polite"></p>
```
The message line for reset.

```html
      </div>
```
Closes the block.

```html
      <p class="hint-done" id="hint-done" role="status" aria-live="polite" hidden>That is the main idea: the phone needs four satellites because its own clock is a fourth unknown. Keep playing, or scroll on.</p>
```
The final message, shown at the end of the guide, hidden until then: `That is the main idea: the phone needs four satellites because its own clock is a fourth unknown. Keep playing, or scroll on.` It is also a status region, so screen readers read it when it appears.

```html
    </section>
```
Closes the controls card.

```html
  </div>
```
Closes the grid of two cards.

```html
  <!-- Rungs 2 to 4. Each step mounts into its own div. All of them share one bridge, so Pyodide loads once. -->
```
A comment: three more sections follow ("rung" is the team's word for one part of the story; these are rungs 2 to 4). Each one is "mounted", which means put on the page, in its own empty `div`, and all of them share the one bridge, so Python is loaded only once.

```html
  <p class="link-line">Solving for the clock works, <strong>but</strong> only if the satellites are spread across the sky. <strong>Therefore</strong> where they sit matters as much as how many there are.</p>
```
A link sentence between the first screen and the next section. The words: `Solving for the clock works, but only if the satellites are spread across the sky. Therefore where they sit matters as much as how many there are.` The `<strong>` words (`but`, `Therefore`) are bold. Each of these sentences ties one section to the next.

```html
  <div id="step-geometry"></div>
```
The empty holder for the geometry section. [`web/step-geometry.js`](web/step-geometry.js.md) fills it.

```html
  <p class="link-line">Good geometry only helps if the phone can read each distance in the first place, <strong>but</strong> the signal is buried in noise. <strong>Therefore</strong> the phone has to dig out the timing.</p>
```
The link sentence before the signal section: `Good geometry only helps if the phone can read each distance in the first place, but the signal is buried in noise. Therefore the phone has to dig out the timing.`

```html
  <div id="step-signal"></div>
```
The empty holder for the signal section, filled by [`web/step-signal.js`](web/step-signal.js.md).

```html
  <p class="link-line">The phone can now read the time from each satellite, <strong>but</strong> the satellites' own clocks drift too. <strong>Therefore</strong> let us see whether that drift can move the position.</p>
```
The link sentence before the last section: `The phone can now read the time from each satellite, but the satellites' own clocks drift too. Therefore let us see whether that drift can move the position.`

```html
  <div id="step-relativity"></div>
```
The empty holder for the relativity section, filled by [`web/step-relativity.js`](web/step-relativity.js.md).

```html
</main>
```
Closes `<main>`.

```html
<script type="module" src="web/first-screen.js"></script>
```
Loads [`web/first-screen.js`](web/first-screen.js.md) as a JavaScript *module* (`type="module"`). A module may import other files and runs only after the page has been read, so the elements above already exist when it looks for them. It brings the first screen to life: finds the ids, loads Python, and wires up the slider, button and switches.

```html
<script type="module">
```
Opens a second module, this time with the code written right in the page, between the tags.

```html
  import { mountGeometryStep } from "./web/step-geometry.js";
  import { mountSignalStep } from "./web/step-signal.js";
  import { mountRelativityStep } from "./web/step-relativity.js";
```
Three `import` lines. Each brings one function from another file: `mountGeometryStep` from [`web/step-geometry.js`](web/step-geometry.js.md), `mountSignalStep` from [`web/step-signal.js`](web/step-signal.js.md) and `mountRelativityStep` from [`web/step-relativity.js`](web/step-relativity.js.md). The `./` starts the address from this page's folder. Without these lines the three sections would never appear.

```html
  mountGeometryStep(document.getElementById("step-geometry"));
  mountSignalStep(document.getElementById("step-signal"));
  mountRelativityStep(document.getElementById("step-relativity"));
```
Each line finds one of the empty holders with `document.getElementById(...)` (look up the element with that `id` in the page: `document` is the page, as the program sees it) and passes it to the matching function, which fills it in with its own controls. The names (`step-geometry`, `step-signal`, `step-relativity`) must match the ids of the three empty `<div>` holders above. If they did not, the function would be given nothing and could not draw its section.

```html
</script>
```
Closes the script.

```html
</body>
```
Closes the body.

```html
</html>
```
Closes the whole page.
