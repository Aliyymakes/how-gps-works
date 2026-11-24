# index.html, line by line

Source: `index.html`

## What this file is for
This is the page itself, the one file a visitor opens. It holds the words, the map drawing, the slider, the buttons and the switches, plus the page's own layout rules. It does not do any maths or react to clicks: it only lays things out. On a phone the map card stays pinned to the top of the screen while the controls scroll under it, so the number and the map are always in view. The JavaScript files it loads at the bottom find these pieces by their `id` names and make them work.

## Which files it talks to
- [`web/theme.css`](web/theme.css.md): the shared look (colours, fonts, cards, buttons, switches). This file only adds layout on top. See `docs/ui-guide.md`.
- [`web/bridge.js`](web/bridge.js.md): the address of Pyodide (a copy of Python that runs inside the browser; `bridge.js` downloads it) is repeated here in a `modulepreload` line so the download can start early. See [bridge.js explained](web/bridge.js.md).
- [`web/illustrations.js`](web/illustrations.js.md): draws the small sketch under the heading (a satellite, a signal, a phone). A short script at the bottom of this file asks it for the drawing and puts it in the empty `figure-first` box.
- [`web/first-screen.js`](web/first-screen.js.md): finds the ids below (`map`, `clock`, `solve`, `switches` and so on) and drives the first screen. It calls Python through the bridge: `coords.latlon_to_xyz` and `coords.satellite_from_sky` ([coords.py](mechanism/coords.py.md)), `scenario.make_pseudoranges` ([scenario.py](mechanism/scenario.py.md)), `solver.solve_position` ([solver.py explained](mechanism/solver.py.md)), and `mapview.to_local` and `mapview.distance_lines` ([mapview.py](mechanism/mapview.py.md)).
- [`web/step-geometry.js`](web/step-geometry.js.md), [`web/step-signal.js`](web/step-signal.js.md), [`web/step-relativity.js`](web/step-relativity.js.md): each fills the empty `<div>` placed for it near the bottom.
- Outside the repo: Google Fonts (the two typefaces) and the Pyodide download address.

## In three lines
1. The head asks the browser to start downloading fonts, Pyodide and the shared style sheet early, and adds this page's layout rules (one layout for phones, another from 760 pixels wide).
2. The body is the first screen: a "Part 1 of 4" label, a heading and a small sketch, one line saying what the map shows, the map card (the map and the error number), the controls (clock slider, solve button, satellite switches, reset), then the map key.
3. Three more empty sections and three quiet link sentences follow, and the scripts at the bottom fill the sections in.

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
  main { max-width: 1100px; margin: 0 auto; padding: var(--s-6) max(var(--s-4), env(safe-area-inset-right)) var(--s-6) max(var(--s-4), env(safe-area-inset-left)); display: grid; grid-template-columns: minmax(0, 1fr); --main-gap: var(--s-5); gap: var(--main-gap); }
```
The rule for `main`, the page's main content. `max-width: 1100px` stops it getting wider than 1100 pixels on big screens. `margin: 0 auto` puts zero space above and below and splits the leftover space equally left and right, which centres it. `padding` is the space inside the edge, written as four values (top, right, bottom, left): 32 pixels top and bottom, and on each side `max(var(--s-4), env(safe-area-inset-...))`, which means "16 pixels, or more if the phone says its screen has a notch or a rounded corner there" (`max` picks the larger; `env(safe-area-inset-right)` is a number the phone supplies). `display: grid` lays the children out as a grid with a single column `minmax(0, 1fr)` (width from 0 up to all the space: see the next comment). `--main-gap: var(--s-5)` makes a new CSS variable of this page's own, 24 pixels, and `gap: var(--main-gap)` uses it as the space between rows. Keeping the gap in a variable lets other rules read it: the phone layout shrinks it, and the link sentences subtract it to get their spacing exactly right (see `.link-line` below). Without it the page would stretch edge to edge.

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
  /* First screen. Phone order: the "looking at" line, the map card (sticky) with the result beside it, the controls, the map notes. */
```
A comment describing the first screen's order on a phone, top to bottom: one line saying what you are looking at, the map card (which sticks to the top) with the result number beside the map, then the controls, then the map notes (the key). Nothing breaks without the comment.

```html
  .grid { display: grid; grid-template-columns: minmax(0, 1fr); gap: var(--s-4); }
```
The `.grid` class (the "looking at" line, the map card, the controls and the map notes) is a grid with one shrinkable column and a 16 pixel gap (`--s-4`). This is the layout for narrow screens such as phones: the parts stack.

```html
  .looking-map { margin: 0; }
```
The "what you're looking at" line above the map (the class `looking-map`) gets no margin of its own. The spacing around it comes from the grid gap instead.

```html
  .map-card { display: grid; grid-template-columns: minmax(0, 1fr); gap: var(--s-4); }
```
The map card (the card that holds the map and the result) is also a grid: one shrinkable column, 16 pixels between the map and the result. The phone layout below changes this to two columns.

```html
  .map-card .readout { align-content: start; }
```
Inside the map card, the result box (`.readout`) packs its pieces at the top of its space (`align-content: start`) instead of spreading them out if the box is taller than they need.

```html
  .figure-strip svg { display: block; width: 100%; }
```
The sketch under the heading lives in a box with the class `figure-strip`. Any drawing (`svg`) in it fills the box's width (`width: 100%`) and is `display: block`, which removes the small gap browsers leave under a drawing sitting in a line of text.

```html
  .figure-strip .figure-narrow { height: 64px; }
  .figure-strip .figure-wide { display: none; height: 76px; }
```
The page draws the sketch twice, a narrow version for phones and a wide one for bigger screens (see [`web/illustrations.js`](web/illustrations.js.md)). By default the narrow one is 64 pixels tall, and the wide one is switched off (`display: none`) and would be 76 pixels tall. The wide-window layout further down swaps them.

```html
  .figure :is(rect, line, path, circle) { vector-effect: non-scaling-stroke; }
```
For the shapes in the sketch (`rect` rectangles, `line`s, `path`s and `circle`s: `:is(...)` means "any of these"), `vector-effect: non-scaling-stroke` keeps the outline the same thickness on screen even though the drawing is scaled to fit. Without it the lines would get thicker or thinner with the screen width.

```html
  /* The pulse runs once along the line, then rests at the phone's end of it (reduced motion: it only rests). */
```
A comment about the small dot in the sketch that stands for the signal. It travels once along the dashed line from the satellite to the phone, then stays at the phone's end. For visitors who ask for less motion, it does not travel and simply sits there.

```html
  .fig-pulse { fill: var(--text); stroke: none; transform: translateX(var(--travel)); animation: fig-travel 1.2s linear 0.4s 1 backwards; }
```
The pulse dot (`.fig-pulse`) is filled with the main text colour and has no outline. `transform: translateX(var(--travel))` shifts it sideways by the length of the dashed line; `--travel` is a variable that each drawing sets for itself, in pixels, so the dot rests at the phone's end. `animation: fig-travel 1.2s linear 0.4s 1 backwards` runs the animation named `fig-travel` (defined next) for 1.2 seconds at constant speed (`linear`), after waiting 0.4 seconds, once (`1`). `backwards` means that during the wait the dot already shows the first frame of the animation (invisible, at the start), instead of sitting at the end and then jumping back.

```html
  @keyframes fig-travel { from { transform: translateX(0); opacity: 0; } 15% { opacity: 1; } to { transform: translateX(var(--travel)); opacity: 1; } }
```
`@keyframes` defines an animation as a list of moments. `from` (the start): the dot is at its starting place (`translateX(0)`) and fully see-through (`opacity: 0`). At 15 % of the way through it has faded in (`opacity: 1`). At `to` (the end) it has moved the whole distance to the phone and stays visible. Worked example: for a dashed line 104 pixels long, the dot slides 104 pixels to the right in 1.2 seconds.

```html
  @media (prefers-reduced-motion: reduce) { .fig-pulse { animation: none; } }
```
For a visitor whose computer is set to reduce motion, the animation is switched off (`animation: none`). The dot then just sits at the end, where its `transform` puts it.

```html
  .figure-strip { min-height: 64px; } /* the drawing is added by a script: keep its room so nothing below moves */
```
The sketch box keeps a minimum height of 64 pixels. The comment explains why: the drawing is put in by a script a moment after the page loads, and without this reserved room everything below would jump down when it arrived.

```html
  /* Phones: the map card stays at the top while its grid is on screen, so the map and the number are never scrolled away from the controls. */
```
A comment introducing the phone rules. On a phone the map card is pinned to the top while the visitor works the controls, so the map and the error number are never scrolled away. Nothing breaks without the comment.

```html
  @media (max-width: 759px) {
```
A media query: the rules inside the braces apply only when the window is 759 pixels wide or narrower, that is, on phones and small tablets. The next several blocks are inside it.

```html
    /* The "Part 1 of 4" label costs about 25 px; these four tighter gaps pay it back so the slider stays above the fold. */
```
A comment: the new "Part 1 of 4" label above the heading takes about 25 pixels of height. The next few rules tighten gaps to win that height back, so that the slider is still on screen without scrolling (the "fold" is the bottom edge of the first screenful).

```html
    main { padding-top: var(--s-3); --main-gap: var(--s-3); }
```
On phones the top padding of `main` falls to 12 pixels and the variable `--main-gap` drops from 24 to 12 pixels, so every row of the page grid sits closer together.

```html
    main .intro > .part-label { margin-bottom: 0; }
```
The "Part 1 of 4" label (`.part-label`, a direct child `>` of the intro inside `main`) gets no margin below it on phones.

```html
    .grid .looking-map { margin-bottom: 0; }
    .grid { gap: var(--s-3); }
```
Inside the first-screen grid, the "looking at" line gets no bottom margin and the gap between the grid's parts drops to 12 pixels.

```html
    .slider-head label { font-size: var(--text-sm); }
```
The slider's label (`Make the phone's clock wrong`) is set to the small size, 14 pixels, so it fits on one line on a phone.

```html
    .grid .card { --pad-card: var(--s-4); }
    .grid .controls { --pad-card: var(--s-3); }
    .grid .map-card { --pad-card: var(--s-3); }
```
`--pad-card` is the variable [`theme.css`](web/theme.css.md) uses for the space inside a card. Here it is turned down for the cards of the first screen: 16 pixels for any card in the grid, then 12 pixels for the controls card and for the map card (these two rules are more specific, so they win). Cards are smaller on phones to leave room for the map.

```html
    .guide-target { padding: var(--s-3); }
    .intro { gap: var(--s-1); }
```
The three groups the guide highlights get 12 pixels of padding instead of 16, and the intro's pieces (label, heading, sketch) are only 4 pixels apart instead of 8.

```html
    .map-card { grid-template-columns: minmax(0, 1fr) minmax(0, 1fr); align-items: start; gap: var(--s-3); }
```
On a phone the map card has two equal columns, the map on the left and the result on the right, with 12 pixels between them, both aligned to the top (`align-items: start`). This makes the pinned card short, so it does not cover too much of the screen.

```html
    .map-card .readout { padding: 0; background: none; border: 0; gap: var(--s-1); }
```
On a phone the result box inside the map card loses its own padding, background and border (so it does not look like a box inside a box), and its parts sit 4 pixels apart.

```html
    .map-card .note { font-size: var(--text-xs); }
    .map-card .big { line-height: 1.2; }
```
In the map card on a phone, messages are set at the smallest size (`--text-xs`, 12 pixels), and the big error number gets a line height of 1.2 times its size, which keeps it compact.

```html
    .map .map-wait { font-size: 30px; }
```
The "map appears when Python has loaded" text is given a font size of 30 on phones. The map is drawn smaller there, and the size is in the drawing's own units rather than screen pixels, so this larger number is what keeps the words readable.

```html
  }
```
Closes the phone block.

```html
  @media (max-width: 759px) and (min-height: 600px) {
```
Another media query: it applies only when the window is both narrow (759 pixels or less) and at least 600 pixels tall. On a short phone, for example held sideways, a pinned card would cover too much of the screen, so the pinning below is left out.

```html
    .map-card { position: sticky; top: env(safe-area-inset-top, 0px); z-index: 2; }
```
This is the sticky map card. `position: sticky` makes the card scroll normally until it reaches `top`, and then stay pinned there while the rest scrolls under it. `top: env(safe-area-inset-top, 0px)` is the top edge of the screen, moved down by the phone's notch if it has one (0 if not). `z-index: 2` puts the card in front of the controls that scroll underneath it.

```html
    /* A focused control is never scrolled in under the sticky card. --sticky-h is set in first-screen.js. */
```
A comment: when a control is selected, for example with the keyboard, the browser scrolls it into view. These rules keep it from stopping underneath the pinned card. `--sticky-h` is the card's height, written into the page by [`web/first-screen.js`](web/first-screen.js.md) (it measures the card and updates the number when the card changes size).

```html
    .controls :is(input, button) { scroll-margin-top: calc(var(--sticky-h, 220px) + var(--s-3)); }
```
For any slider, switch or button inside the controls card, `scroll-margin-top` tells the browser to leave that much room above it when it scrolls it into view: the card's height plus 12 pixels. `var(--sticky-h, 220px)` means "use `--sticky-h`, or 220 pixels if it has not been set yet".

```html
    .controls #clock { scroll-margin-top: calc(var(--sticky-h, 220px) + 7rem); }
```
The clock slider (`#clock`) needs more room above it: the card's height plus `7rem` (7 times the page's base text size, 112 pixels at the usual 16), because the hint and the message line sit above the slider and should stay visible too.

```html
    .controls :is(input, button) { scroll-margin-bottom: var(--s-6); }
```
And the same controls keep 32 pixels free below them when scrolled into view, so they are not right at the bottom edge of the screen.

```html
  }
```
Closes the tall-phone block.

```html
  @media (min-width: 760px) {
```
A media query for windows at least 760 pixels wide: laptops, desktops and tablets. The blocks inside it make the two-column layout.

```html
    .figure-strip { min-height: 76px; }
    .figure-strip .figure-narrow { display: none; }
    .figure-strip .figure-wide { display: block; }
```
On a wide window the sketch box reserves 76 pixels, the narrow drawing is hidden and the wide drawing is shown (`display: block`). This is the swap mentioned earlier.

```html
    .grid { grid-template-columns: minmax(0, 1.1fr) minmax(0, 1fr); grid-template-areas: "looking ." "map controls" "notes controls"; grid-template-rows: auto auto 1fr; column-gap: var(--s-5); row-gap: 0; align-items: start; }
```
The page grid becomes two columns sharing the room in proportion 1.1 to 1 (an `fr` is one share; `minmax(0, ...)` lets them shrink). Worked example: if 1,000 px is left after the gap, one share is 1,000 / 2.1 = 476.2 px, so the left column is 1.1 x 476.2 = 523.8 px and the right one 476.2 px. `grid-template-areas` draws the layout as a picture in words: three rows, each in quotes, two cells per row. Row 1 is `looking` on the left and `.` (a dot means "empty") on the right. Row 2 is `map` on the left and `controls` on the right. Row 3 is `notes` on the left and `controls` again, which means the controls card is tall and covers rows 2 and 3 on the right. `grid-template-rows: auto auto 1fr` makes the first two rows only as tall as their contents and gives the third row all the leftover height. `column-gap: var(--s-5)` is 24 pixels between columns and `row-gap: 0` is no space between rows (the rules below add their own margins). `align-items: start` aligns everything to the top.

```html
    .looking-map { grid-area: looking; margin-bottom: var(--s-3); }
    .map-card { grid-area: map; }
    .controls { grid-area: controls; }
    .map-notes { grid-area: notes; margin-top: var(--s-4); }
```
Each part says which named area it goes in: the "looking at" line in `looking` (with 12 pixels below), the map card in `map`, the controls card in `controls`, and the map notes in `notes` (with 16 pixels above). Without these lines the parts would fill the cells in the order they are written, which would not match the picture.

```html
    /* The map is capped so the number under it stays on a laptop screen; the result is one compact row. */
```
A comment: the map is limited in size so that the error number under it still fits on a laptop screen without scrolling, and the result is one tidy row.

```html
    .map-card .map { width: min(100%, 420px, max(240px, calc(100vh - 400px))); margin: 0 auto; }
```
The map's width is the smallest (`min`) of three things: 100 % of the card, 420 pixels, and `max(240px, calc(100vh - 400px))`. `100vh` is the height of the window, so the third is "the window height minus 400 pixels, but never less than 240". Worked example: on a window 800 px tall, the third value is 400 px, so the map is the smaller of the card width, 420 and 400. `margin: 0 auto` centres it in the card.

```html
    .map-card .readout { display: flex; flex-wrap: wrap; align-items: baseline; column-gap: var(--s-4); }
    .map-card .readout #msg-readout { flex-basis: 100%; }
```
On a wide window the result box becomes a row (`display: flex`): the label "Position off by", the big number and the badge sit side by side on the same text line (`align-items: baseline`), 16 pixels apart, and wrap to a new line if there is no room. The message line (`#msg-readout`, `#` means "the element with this id") takes 100 % of the width (`flex-basis: 100%`), so it always goes on its own line below.

```html
  }
```
Closes the wide-window block.

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
  .map-key { list-style: none; margin: 0; padding: 0; display: grid; gap: var(--s-1); font-size: var(--text-sm); color: var(--text-muted); }
```
The map key list (`.map-key`): `list-style: none` removes bullet points, `margin: 0` and `padding: 0` remove the default space around and inside it (the space now comes from the notes box that holds it), it is a grid with 4 pixels between entries, and the text is small (`--text-sm`, 14 pixels) and muted grey.

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
  .slider > #status:empty { margin-top: calc(-1 * var(--s-2)); } /* an empty line below the slider takes no room, not even its grid gap */
```
The status line now sits under the slider, as the last child (`>` means a direct child) of the slider block. While it is empty, `margin-top: calc(-1 * var(--s-2))` pulls it up by 8 pixels, which is the grid gap of the slider block ([`theme.css`](web/theme.css.md) sets `.slider` to `gap: var(--s-2)`). The two cancel out, so an empty status line takes no room at all, not even the gap. The comment says the same.

```html
  /* One reserved line above the slider holds the step-1 hint or, when there is one, the message (same grid cell), so the slider never moves. */
```
A comment: above the slider there is one reserved space. It shows either the step-1 hint or, when there is a message, the message. Both are in the same place, so the slider never moves up or down when one replaces the other.

```html
  .slider > #hint-1, .slider > #msg-slider { grid-area: 1 / 1; font-size: var(--text-sm); }
```
Both the hint (`#hint-1`) and the message (`#msg-slider`) are placed in grid row 1, column 1 (`grid-area: 1 / 1`), the same single cell, so they overlap exactly. Both get the small text size.

```html
  .slider > #msg-slider { min-height: 3em; }
```
The message line keeps a height of at least `3em` (three lines of text), even when empty. This is the reserved space from the comment above. A rule that names an id is stronger than the general `.note:empty` rule further down, so this one wins and the room is kept.

```html
  .slider > #msg-slider:not(:empty) + #hint-1 { visibility: hidden; }
```
When the message line has words in it (`:not(:empty)`), the element right after it (`+ #hint-1`, the hint) is made invisible with `visibility: hidden`, which hides it but keeps its place. So the message and the hint never print over each other.

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
  /* An empty message line takes no room, not even its block's grid gap. They answer a press, so a one-line shift when words appear is fine. The readout's line keeps its height. */
  .note:empty { min-height: 0; }
```
A comment, then a rule. `.note:empty { min-height: 0; }`: a message line with nothing in it takes no room. The comment explains the choice: these lines answer a button press, so if the page moves down by one line when words appear, that is acceptable. The exceptions are the slider's message line (above) and the result's message line (next).

```html
  #msg-readout:empty { min-height: 1.5em; }
```
The exception for the result. The message line under the error number (`#msg-readout`) keeps a height of `1.5em` (21 pixels at 14 pixels text) even when empty. The error number is the thing a visitor watches, and it should not jump when a message arrives.

```html
  /* Out of the flow while empty, so it makes no grid row and no gap (a negative margin cannot shrink a grid track); it stays a live region. */
  #msg-solve:empty, #msg-switch:empty, #msg-reset:empty { position: absolute; }
```
A comment, then a rule for the message lines under the solve button, the satellite switches and the reset button. When one of them is empty, `position: absolute` takes it "out of the flow": the grid treats it as if it were not there, so it makes no row and no gap between rows. The comment says why not use a negative margin: a margin cannot shrink a grid row, but removing the item can. The line is still in the page, so screen readers still announce it when words arrive (it "stays a live region"). When words are added the rule stops matching (`:empty` no longer applies), the line goes back into the flow and the controls below move down one line.

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
  .link-line { font-size: calc(var(--text-lg) * 0.9); color: var(--text-muted); font-weight: 400; text-wrap: balance; /* main's grid gap is added to the margins, so subtract it: --s-7 above the bridge, --s-3 below. */ margin: calc(var(--s-7) - var(--main-gap)) 0 calc(var(--s-3) - var(--main-gap)); }
```
The link sentences between sections (the "bridges", `.link-line`). `calc(var(--text-lg) * 0.9)` is 20 pixels x 0.9 = 18 pixels. The colour is muted grey, the weight is 400 (normal, not bold) and `text-wrap: balance` evens out the lines. The `margin` is the space around the sentence, written top, sides, bottom: `calc(var(--s-7) - var(--main-gap)) 0 calc(var(--s-3) - var(--main-gap))`. The comment inside the rule explains it: `main`'s grid gap is added on top of margins, so the gap is subtracted to land on the wanted totals: 48 pixels (`--s-7`) above the sentence and 12 pixels (`--s-3`) below. Worked example on a wide window, where `--main-gap` is 24: the top margin is 48 - 24 = 24, plus the 24 gap = 48 above. The bottom margin is 12 - 24 = -12 (a negative margin pulls things closer), plus the 24 gap = 12 below. On a phone `--main-gap` is 12, and the totals are the same. So each bridge sits near the section it introduces and far from the one before.

```html
  .link-line strong { color: var(--text-muted); font-weight: 500; }
```
The words in bold in a link sentence (`strong`: "but" and "Therefore") are now the same muted colour as the rest, with a medium weight of 500. The bridges are quiet: they link sections without competing with them for attention.

```html
  .intro > .part-label { margin: 0 0 var(--s-2); }
```
The "Part 1 of 4" label (`.part-label`, a direct child of the intro) gets no margin on top or the sides and 8 pixels below (`margin` with three values means top, left and right, bottom). The same label class is used by the other three sections; each of them writes its own "Part 2 of 4", "Part 3 of 4" and "Part 4 of 4".

```html
  .looking { font-size: var(--text-sm); color: var(--text); margin: 0 0 var(--s-3); }
```
The "What you're looking at" line, a shared class `.looking`: small text (14 pixels) in the main text colour, with 12 pixels below. Every section uses it as the first line over its picture, so a visitor always gets one plain sentence about what the drawing shows.

```html
  .looking b { font-weight: 600; }
```
The bold opening words of that line (`b`, "What you're looking at:") are given a weight of 600, a semibold.

```html
  .figure { stroke: var(--text); stroke-width: 1.5; fill: none; }
```
The class `.figure` is for the small sketches from [`web/illustrations.js`](web/illustrations.js.md): their lines are drawn in the main text colour, 1.5 wide, and shapes are not filled in (`fill: none`).

```html
  .figure .dim { stroke: var(--text-muted); }
```
Parts of a sketch marked with the class `dim` (such as the dashed signal line) are drawn in the quieter muted colour.

```html
  .figure text { stroke: none; fill: var(--text-muted); font: 400 var(--text-xs) var(--font-sans); }
```
Words inside a sketch (`text`) have no outline (`stroke: none`), are filled with the muted colour, and use the shorthand `font: 400 var(--text-xs) var(--font-sans)`: weight 400, size 12 pixels, the sans-serif font. (An SVG word is coloured with `fill`, not `color`.)

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
    <p class="label part-label">Part 1 of 4</p>
```
A small label (the `label` look from [`theme.css`](web/theme.css.md): tiny capital letters in muted grey) saying `Part 1 of 4`. The page is told as four parts, and each part starts with one of these, so a visitor always knows where they are. The class `part-label` is what the page's own CSS uses to tighten its spacing.

```html
    <h1>How does your phone know where you are?</h1>
```
The page's main heading, `h1`: `How does your phone know where you are?`. It is now the second thing in the intro, after the part label.

```html
    <div class="figure-strip" id="figure-first"></div>
```
An empty box for the small sketch under the heading: a satellite, a dashed line with a pulse travelling along it, a phone, and the words "travel time x speed of light = distance". It replaces the two paragraphs that used to say this in words. The box starts empty; the script near the bottom of the file puts the drawing in, using the `id`. The class `figure-strip` is what the CSS above uses to size it and to keep room for it.

```html
  </header>
```
Closes the header.

```html
  <div class="grid">
```
Opens `div class="grid"`, a generic box (`div`) that holds the first screen's four parts: the "looking at" line, the map card, the controls card and the map notes. On a wide window they sit in two columns; on a phone they stack (see the `.grid` rules in the style block above).

```html
    <p class="looking looking-map" id="looking-map"><b>What you're looking at:</b> a map of the ground around the phone. Each line is one satellite's distance to you. Where the lines meet is where your phone thinks you are.</p>
```
The one-line introduction to the map: `What you're looking at: a map of the ground around the phone. Each line is one satellite's distance to you. Where the lines meet is where your phone thinks you are.` The `<b>` makes the first words bold. `class="looking looking-map"` has two classes: `looking` is the shared look every section uses for this kind of line, and `looking-map` is the one the layout rules use to place this one. It sits above the map card, so a visitor reads what the picture shows before the picture.

```html
    <section class="card map-card" aria-label="Ground map and result">
```
Opens the first card: a `<section>`, with the shared `card` look and the `map-card` class that the phone and wide layouts use (the phone layout pins it to the top). `aria-label="Ground map and result"` names the section for screen readers. This card now holds the map and the error number together; the old heading `Ground map` is gone because the "looking at" line above does that job.

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
        <text id="map-wait" class="map-wait" x="200" y="252" text-anchor="middle"><tspan x="200">The map appears when </tspan><tspan x="200" dy="1.3em">Python has loaded.</tspan></text>
```
The waiting text, `The map appears when Python has loaded.`, now on two lines so it fits in a map that is small on a phone. `text-anchor="middle"` centres each line on its `x`. The `<text>` is placed at x 200 (the middle across) and y 252 (low down). It sits below the middle on purpose: the "where it really is" cross is drawn in the middle and its arms end at y 212, so words at y 200 were drawn over the cross. Inside it, two `<tspan>` pieces are the two lines: the first, `The map appears when `, and the second, `Python has loaded.`. Both are at `x="200"` so they stay centred; `dy="1.3em"` moves the second line down by 1.3 times the font size (about 18 units for a 14 unit font), which is what makes it a second line. The code hides the whole text once the map is ready.

```html
      </svg>
```
Closes the SVG.

```html
      <div class="inset readout">
```
Opens the error readout box, an `inset` look with the `readout` layout rules. It now sits inside the map card, under the map (on a phone, beside it), so the number is always next to the map it describes.

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
    </section>
```
Closes the map card.

```html
    <section class="card stack controls" aria-label="Controls">
```
Opens the second card, the controls. `class="card stack controls"` gives it the card look, a vertical pile (`stack`), and the `controls` class that the layout rules use to place it and to size its scroll margins. `aria-label="Controls"` names it.

```html
      <div class="slider inset guide-target highlight" id="block-slider">
```
Opens the slider block. `slider` and `inset` are look classes from [`theme.css`](web/theme.css.md), and `guide-target highlight` make it the first step of the guide, with the highlight border visible from the start. `id="block-slider"` lets the code switch the highlight.

```html
        <p class="note" id="msg-slider" role="status" aria-live="polite"></p>
```
The message line for the slider, now above the slider, empty until the code has something to say. It shares one reserved space with the first hint below (see the `#msg-slider` rules in the style block), so the slider does not move when a message appears.

```html
        <p class="hint" id="hint-1" hidden>Step 1. This only works if the phone's clock is right. Drag the slider to make it wrong.</p>
```
The first hint: `Step 1. This only works if the phone's clock is right. Drag the slider to make it wrong.` It now says why the step matters, and replaces the short intro paragraph that said the same thing. The `hidden` attribute hides it at first; the code reveals it.

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
        <p class="note" id="status" role="status" aria-live="polite">Loading the maths…</p>
```
The status line, shown first: `Loading the maths…`. It has moved from the top of the controls card to just under the slider. The code changes it while Python loads and shows failure messages here. When it is empty it takes no room (see the `#status:empty` rule above).

```html
      </div>
```
Closes the slider block.

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
Closes the first card.

```html
    <div class="map-notes">
```
Opens a box for the notes about the map: the key and the caption. It used to sit inside the map card. Now it is its own part of the grid, so that on a phone the pinned map card is short and the notes scroll away, and on a wide window the notes sit under the map. The class `map-notes` is how the layout rules place it.

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
    </div>
```
Closes the map notes.

```html
  </div>
```
Closes the grid.

```html
  <!-- Rungs 2 to 4. Each step mounts into its own div. All of them share one bridge, so Pyodide loads once. -->
```
A comment: three more sections follow ("rung" is the team's word for one part of the story; these are rungs 2 to 4). Each one is "mounted", which means put on the page, in its own empty `div`, and all of them share the one bridge, so Python is loaded only once.

```html
  <p class="link-line">Solving for the clock works, <strong>but</strong> only if the satellites are spread across the sky. <strong>Therefore</strong> where they sit matters as much as how many there are.</p>
```
A link sentence (a "bridge") between the first screen and the next section. The words: `Solving for the clock works, but only if the satellites are spread across the sky. Therefore where they sit matters as much as how many there are.` The `<strong>` words (`but`, `Therefore`) are bold. Each of these sentences ties one section to the next, in quiet grey text.

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
<script type="module">
```
Opens a small script, a JavaScript *module* (the first of three at the bottom) with its code written right in the page, between the tags. It runs once the page has been read, so the empty `figure-first` box above exists by then.

```html
  import { firstScreenFigure } from "./web/illustrations.js";
```
One `import` line: it brings the function `firstScreenFigure` from [`web/illustrations.js`](web/illustrations.js.md). The `./` starts the address from this page's folder. The function returns the sketch as a piece of SVG text (drawing instructions).

```html
  document.getElementById("figure-first").innerHTML = firstScreenFigure();
```
`document.getElementById("figure-first")` looks up the empty box with that `id` (`document` is the page, as the program sees it). `.innerHTML = ...` puts the text on the right of the `=` inside it as the box's contents, and `firstScreenFigure()` runs the function to get that text: the narrow and the wide drawing, one of which the CSS hides. Without this line the box would stay empty.

```html
</script>
```
Closes this small script.

```html
<script type="module" src="web/first-screen.js"></script>
```
Loads [`web/first-screen.js`](web/first-screen.js.md) as a JavaScript *module* (`type="module"`). A module may import other files and runs only after the page has been read, so the elements above already exist when it looks for them. It brings the first screen to life: finds the ids, loads Python, and wires up the slider, button and switches.

```html
<script type="module">
```
Opens a third module, again with the code written right in the page, between the tags.

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
