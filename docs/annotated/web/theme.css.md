# theme.css, line by line

Source: `web/theme.css`

## What this file is for
This is the page's look, written once. CSS ("cascading style sheets") is a list of rules that say how things on a web page should look: colours, sizes, spacing, fonts. This file holds the dark and light colour sets, the type sizes, the spacing steps, the shapes of cards, buttons, sliders, switches and badges, and the little drawing of the sky. Every page that wants the same look links this one file instead of repeating the rules.

## Which files it talks to
- [`index.html`](../index.html.md), [`web/theme-preview.html`](theme-preview.html.md), [`web/dev/step-geometry.html`](dev/step-geometry.html.md) and [`web/dev/step-signal.html`](dev/step-signal.html.md): each loads this file with a `<link rel="stylesheet">` tag, so they all look the same.
- [`web/theme.js`](theme.js.md): sets the `data-theme="light"` or `data-theme="dark"` mark on the page (which picks the colour set below) and sets the `--px` and `--py` numbers that place the glow on cards. It does not edit this file.
- [`web/step-geometry.js`](step-geometry.js.md), [`web/step-signal.js`](step-signal.js.md) and [`web/step-relativity.js`](step-relativity.js.md): add a few style rules of their own, but they reuse the names (`--s-4`, `--line`, `.btn`, and so on) defined here.
- `docs/ui-guide.md`: the written rules this file follows (white means "you can use this", colour only for a state).
- Fonts are not loaded here. Each page loads them from Google Fonts (the comment on the first lines shows the address) and this file only names them.

## In three lines
1. Define named colours, sizes, spaces and timings once, as "variables" (names that stand for values) on the whole page.
2. Swap the colour variables when the page is marked light, so every rule below changes with no edits.
3. Style each reusable piece (card, button, slider, switch, badge, sky drawing) using only those variable names, and calm the motion for people who asked their device for less movement.

New to code? See [how to read code](../how-to-read-code.md).

## The code, line by line

```css
/* Instrument theme for how-gps-works.
   Rules: docs/ui-guide.md section 2. Interactive = white. Colour only for state (ok / warn / bad).
   Pages load the fonts with:
   <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Instrument+Sans:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap"> */
```
A comment. In CSS a comment starts with `/*` and ends with `*/`; the browser skips everything in between. These four lines say what the file is, point at the rules in `docs/ui-guide.md`, and give the exact `<link>` tag every page must use to fetch the two fonts (Instrument Sans for words, JetBrains Mono for numbers). The headline rule: white means "you can press or drag this", and colour is only used to show a state (good, careful, bad). Without it nothing breaks, but the next person would not know why the page is black, white and three colours.

```css
:root {
  color-scheme: dark;
```
`:root` is a CSS rule aimed at the very top element of the page (the `<html>` element). A CSS rule is a selector (who it applies to) followed by curly brackets holding settings. Because every other element sits inside the top element, settings made here are available everywhere. `color-scheme: dark;` tells the browser "this page is dark", so things the browser draws itself (scroll bars, the checkbox, the slider before we restyle it) come out dark too. Without it, some parts would flash white.

```css
  /* Surfaces and text */
  --bg: #0a0a0a;
  --surface: #121212;
  --surface-2: #1a1a1a;
  --line: rgba(255, 255, 255, 0.09);
  --line-strong: rgba(255, 255, 255, 0.18);
  --text: #ededed;
  --text-muted: #9a9a9a;
  --text-faint: #5f5f5f;
```
A comment, then eight CSS variables for surfaces and text. A CSS variable is a name that starts with two dashes and holds a value; later rules write `var(--bg)` to mean "use whatever `--bg` is". Change a value once here and every use changes. Colours are written as hex codes (`#0a0a0a`: red, green, blue amounts from 00 to ff) or as `rgba(red, green, blue, opacity)`.
- `--bg` (`#0a0a0a`): the page background, nearly black.
- `--surface` (`#121212`) and `--surface-2` (`#1a1a1a`): slightly lighter greys for cards and for boxes inside cards.
- `--line` and `--line-strong`: thin border colours, made of white at 9% and 18% opacity, so they show as faint lines on any dark ground.
- `--text` (`#ededed`): main words. `--text-muted` (`#9a9a9a`): quieter words. `--text-faint` (`#5f5f5f`): the quietest.
Without these, every later `var(--bg)` and its friends would have no value and the page would lose its background and text colours.

```css
  /* Interactive is white */
  --accent: #ffffff;
  --accent-ink: #0a0a0a;
```
Two variables for the "interactive" colour. `--accent` is pure white (`#ffffff`): anything you can press or drag is white. `--accent-ink` (`#0a0a0a`) is the colour of words drawn on top of a white shape, for example the text inside the white primary button. Without `--accent-ink`, text on a white button would also be white and could not be read.

```css
  /* State only */
  --ok: #3ccf8e;
  --warn: #f2a93b;
  --bad: #f0524f;
```
Three variables for state, the only places colour is allowed. `--ok` is green (`#3ccf8e`), `--warn` is amber (`#f2a93b`) and `--bad` is red (`#f0524f`). They show a state, such as how far off a position is or whether the signal was found. Without them, the badges and the fix marks (further down) would have no colour for each state.

```css
  /* Type */
  --font-sans: "Instrument Sans", system-ui, -apple-system, "Segoe UI", sans-serif;
  --font-mono: "JetBrains Mono", ui-monospace, "SF Mono", Menlo, monospace;
```
A comment, then the two font stacks. A font stack is a list: the browser uses the first font it can find and falls back down the list. `--font-sans` starts with "Instrument Sans" (used for normal words), then `system-ui` and `-apple-system` (the phone's or computer's own interface font), `"Segoe UI"`, and finally plain `sans-serif` as the last resort. `--font-mono` starts with "JetBrains Mono" (used for numbers, because each digit takes the same width) and falls back to the system's fixed-width fonts. Names with spaces are in quote marks. Without the fallbacks, a visitor whose font download failed would see an ugly default font.

```css
  --text-xs: 12px;
  --text-sm: 14px;
  --text-md: 16px;
  --text-lg: 20px;
  --text-xl: 32px;
```
Five text sizes: `--text-xs` 12 px, `--text-sm` 14 px, `--text-md` 16 px, `--text-lg` 20 px and `--text-xl` 32 px. A px (pixel) is one dot of the screen at normal size. Keeping a short fixed list means every piece of text on the page is one of five sizes, which looks tidy. Without them the size rules below would have nothing to point at.

```css
  /* Space (4 px grid) */
  --s-1: 4px; --s-2: 8px; --s-3: 12px; --s-4: 16px; --s-5: 24px; --s-6: 32px; --s-7: 48px;
```
A comment, then the spacing steps. The page spaces everything in multiples of 4 px: `--s-1` is 4, `--s-2` is 8, `--s-3` is 12, `--s-4` is 16, `--s-5` is 24, `--s-6` is 32 and `--s-7` is 48 pixels. (Several settings can share one line; each ends with a semicolon.) Without them, gaps would be random numbers and the layout would look uneven.

```css
  /* Concentric radii: inner = outer - padding */
  --r-card: 16px;
  --pad-card: var(--s-5);
  --r-inner: max(4px, calc(var(--r-card) - var(--pad-card) / 2));
  --r-pill: 999px;
```
A comment, then four shape variables. `--r-card` is how round a card's corners are (16 px). `--pad-card` is the space inside a card, and it reuses another variable: `var(--s-5)` is 24 px. `--r-inner` is the corner roundness for a box inside a card. The comment says the idea: an inner corner looks right when it is the outer radius minus the gap. The line does that with `calc(...)` (the browser does the sum) and `max(4px, ...)` (take the bigger of the two, so the corner is never tighter than 4 px). Worked example: `--r-card` 16 px minus `--pad-card` 24 px divided by 2 (= 12 px) gives 16 - 12 = 4 px; the bigger of 4 px and 4 px is 4 px. `--r-pill` is 999 px, far larger than any button's half height, so the ends of buttons and badges are fully round. Without them, boxes inside cards would have corners that look wrong next to the card's.

```css
  /* Motion (docs/ui-guide.md section 3) */
  --ease-out: cubic-bezier(0.23, 1, 0.32, 1);
  --ease-in-out: cubic-bezier(0.77, 0, 0.175, 1);
  --dur-press: 120ms;
  --dur-small: 180ms;
  --dur-panel: 280ms;
```
A comment, then the motion settings. `--ease-out` and `--ease-in-out` are `cubic-bezier(...)` curves: they describe how a movement speeds up and slows down (the four numbers are the shape of the curve). `--ease-out` starts fast and settles gently. `--dur-press` is 120 ms, `--dur-small` is 180 ms and `--dur-panel` is 280 ms, where "ms" is a thousandth of a second. Pressing a button takes 0.12 s, small changes 0.18 s. Without them, the transition rules below would have no timing and changes would be instant.

```css
  /* Pointer light, set by theme.js */
  --px: 50%;
  --py: 50%;
}
```
A comment, then the starting place of the pointer glow: `--px` and `--py` begin at `50%`, the middle of the card. [`web/theme.js`](theme.js.md) replaces them with the real pointer position (in pixels from the card's top-left corner) every time the mouse moves over a card; for example a pointer 100 px across and 40 px down sets `--px: 100px` and `--py: 40px`. The closing `}` ends the `:root` rule. Without the starting values, the glow would have no position before the first mouse move.

```css
[data-theme="light"] {
  color-scheme: light;
```
The light theme. `[data-theme="light"]` is a selector for any element that carries the attribute `data-theme` with the value `light`. An attribute is an extra label written inside an HTML tag, like `data-theme="light"` on the top `<html>` tag; [`web/theme.js`](theme.js.md) writes it when a page opens (from the choice saved earlier, "dark" if none) and when the visitor presses the light/dark button on the preview page. `color-scheme: light;` tells the browser to draw its own parts light as well.

```css
  --bg: #fafafa;
  --surface: #ffffff;
  --surface-2: #f2f2f2;
  --line: rgba(0, 0, 0, 0.08);
  --line-strong: rgba(0, 0, 0, 0.16);
  --text: #111111;
  --text-muted: #666666;
  --text-faint: #a3a3a3;
```
The surface and text variables again, with light values: a near-white page (`#fafafa`), white cards (`#ffffff`), grey boxes (`#f2f2f2`), faint lines made of black at 8% and 16% opacity, and dark text (`#111111`, `#666666`, `#a3a3a3`). Because the names are the same as in the dark set, nothing else needs to change: the rules below write `var(--bg)` and get whichever colour is current. Without this block there would be no light theme.

```css
  --accent: #111111;
  --accent-ink: #ffffff;
  --ok: #18a86b;
  --warn: #c7820f;
  --bad: #d63a37;
}
```
The accent flips too: now interactive things are near-black (`--accent: #111111`) and the ink on top of them is white (`--accent-ink: #ffffff`). The three state colours are made slightly deeper (`--ok` `#18a86b`, `--warn` `#c7820f`, `--bad` `#d63a37`) so they still stand out on a white ground; the bright dark-theme versions would look washed out. The `}` ends the light-theme rule. Without these lines the light theme would keep white buttons on a white page, which could not be seen.

```css
*, *::before, *::after { box-sizing: border-box; }
```
A rule for every element (`*`) and for the two invisible extra parts every element can have (`::before` and `::after`, small decorations added by CSS; more on them below). `box-sizing: border-box;` means a width or height set on a box includes its padding and border. Example: a box set to 100 px wide with 10 px padding is 100 px in all, not 120 px. Without it, boxes would come out wider than their set size and overflow their cards.

```css
body {
  margin: 0;
  background: var(--bg);
  color: var(--text);
  font-family: var(--font-sans);
  font-size: var(--text-md);
  line-height: 1.5;
  -webkit-font-smoothing: antialiased;
}
```
The rule for `body`, the element that holds everything you see. `margin: 0` removes the browser's default gap around the page. `background` and `color` use the variables for the page and text colours. `font-family` uses the sans stack; `font-size` is `var(--text-md)`, 16 px. `line-height: 1.5` makes each line of text 1.5 times the text size tall (24 px for 16 px text), which is easy to read. `-webkit-font-smoothing: antialiased` asks Safari and Chrome on Mac to draw thinner, smoother letters, which suits light text on a dark ground. Without this rule the page would use the browser's default white background, black Times-like text and an 8 px margin.

```css
h1, h2, h3 { margin: 0; font-weight: 600; letter-spacing: -0.02em; line-height: 1.15; }
```
Headings. `h1, h2, h3` are three selectors sharing one set of settings (the comma means "all of these"). `margin: 0` removes the default gap, `font-weight: 600` makes them semi-bold, `letter-spacing: -0.02em` pulls letters 0.02 of a text-size closer (an `em` is one text size; for 32 px that is 0.64 px) and `line-height: 1.15` keeps wrapped heading lines close together. Without it, headings would use the browser's big default margins and look loose.

```css
h1 { font-size: var(--text-xl); }
h2 { font-size: var(--text-lg); }
p { margin: 0; }
```
`h1` is 32 px (`--text-xl`), `h2` is 20 px (`--text-lg`), and `p` (a paragraph) loses its default top and bottom margin so spacing is controlled by the layout rules instead. Without these, headings would have the browser's default sizes and paragraphs would add unwanted gaps.

```css
.muted { color: var(--text-muted); }
.mono, .num { font-family: var(--font-mono); font-variant-numeric: tabular-nums; }
.label { font-size: var(--text-xs); color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.08em; }
```
Three small helper classes. A class is a name you add to an HTML tag (`class="muted"`); a CSS selector that starts with a dot targets it. `.muted` makes text the quieter grey. `.mono, .num` switch to the number font, and `font-variant-numeric: tabular-nums` makes every digit the same width, so a number that changes (for example 299 then 300) does not wobble sideways. `.label` is for small captions: 12 px, muted, `text-transform: uppercase` (shown in capitals) and `letter-spacing: 0.08em` (spread out). Without them, the readouts and captions on the pages would all look like plain text.

```css
/* Card with pointer-tracked light */
.card {
  position: relative;
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: var(--r-card);
  padding: var(--pad-card);
  overflow: hidden;
}
```
A comment, then the card, the main box of the page. `position: relative` makes the card the reference point for things placed inside it (the glow below). It gets the `--surface` colour, a 1 px border in `--line`, rounded corners from `--r-card` (16 px) and 24 px of padding. `overflow: hidden` cuts off anything that sticks out of the rounded corners, which stops the glow squaring off the corners. Without this rule a card would be an unstyled block.

```css
.card::before {
  content: "";
  position: absolute;
  inset: 0;
  border-radius: inherit;
```
`.card::before` is the invisible extra part drawn inside each card, before its real contents. A `::before` part only appears if it has `content`, so `content: ""` (empty text) creates it. `position: absolute` with `inset: 0` makes it stretch over the whole card (0 distance from all four edges). `border-radius: inherit` gives it the same round corners as the card. Without these lines the glow layer would not exist or would not fit the card.

```css
  background: radial-gradient(360px circle at var(--px) var(--py), rgba(255, 255, 255, 0.06), transparent 60%);
  opacity: 0;
  transition: opacity var(--dur-small) ease;
  pointer-events: none;
}
```
This is the glow. `radial-gradient(360px circle at var(--px) var(--py), rgba(255, 255, 255, 0.06), transparent 60%)` paints a circle of light with a radius of 360 px (for a circle, the size given is the radius), centred on the pointer position from `--px` and `--py`. It is white at 6% opacity in the middle and fades to fully see-through at 60% of the way out (0.6 x 360 = 216 px from the centre). `opacity: 0` hides it for now. `transition: opacity var(--dur-small) ease` means a change in opacity takes 0.18 s instead of snapping. `pointer-events: none` lets mouse clicks pass straight through the glow to whatever is underneath. Without `pointer-events: none` the glow layer would swallow clicks on buttons inside the card.

```css
.card:hover::before { opacity: 1; }
```
When the pointer is over a card (`:hover`), its glow layer becomes fully visible (`opacity: 1`), and the transition above fades it in over 0.18 s. Without it the glow would stay hidden forever.

```css
[data-theme="light"] .card::before {
  background: radial-gradient(360px circle at var(--px) var(--py), rgba(0, 0, 0, 0.04), transparent 60%);
}
```
In the light theme the glow is black at 4% opacity instead of white at 6% (white light would be invisible on a white card). The selector `[data-theme="light"] .card::before` means "the glow layer of a card that sits inside something marked light". Without it the glow would be white on white and vanish in the light theme.

```css
.inset {
  background: var(--surface-2);
  border: 1px solid var(--line);
  border-radius: var(--r-inner);
}
```
`.inset` is a quieter box for use inside a card (for example the "Position off by" readout). It uses the slightly different `--surface-2` colour, a faint border and the smaller `--r-inner` corners (4 px). Without it, boxes inside cards would have no look.

```css
/* Buttons */
```
A comment naming the next group, the buttons.

```css
.btn {
  display: inline-flex; align-items: center; justify-content: center; gap: var(--s-2);
  min-height: 44px; padding: 0 var(--s-4);
```
The start of the button rule. `display: inline-flex` lays the button's contents out in a row that sits in a line with text; `align-items: center`, `justify-content: center` centre them both ways and `gap: var(--s-2)` puts 8 px between an icon and its words. `min-height: 44px` makes the button at least 44 pixels tall, the usual smallest size a finger can hit reliably. `padding: 0 var(--s-4)` adds 0 above and below and 16 px left and right. Without these the buttons would be small and cramped.

```css
  border-radius: var(--r-pill);
  border: 1px solid var(--line-strong);
  background: transparent; color: var(--text);
```
`border-radius: var(--r-pill)` makes the ends fully round. `border` is a 1 px line in `--line-strong`. `background: transparent` leaves the inside empty so the card shows through, and `color: var(--text)` makes the words normal text colour. Without them the button would be a square browser-grey box.

```css
  font: 500 var(--text-sm) var(--font-sans);
  cursor: pointer;
  transition: transform var(--dur-press) var(--ease-out), background-color var(--dur-small) ease, border-color var(--dur-small) ease;
}
```
`font: 500 var(--text-sm) var(--font-sans)` is a short way to set weight 500 (medium), size 14 px and the sans font in one go. `cursor: pointer` turns the mouse arrow into a hand. The `transition` line lists what should animate: `transform` over 120 ms with the `--ease-out` curve, and `background-color` and `border-color` over 180 ms. The final `}` ends the rule. Without the `transition`, the press shrink and hover changes below would jump instead of glide.

```css
.btn:hover { border-color: var(--accent); }
.btn:active { transform: scale(0.97); }
.btn-primary { background: var(--accent); color: var(--accent-ink); border-color: var(--accent); }
```
Three more button rules. `.btn:hover` (pointer over the button) turns the border white (`--accent`). `.btn:active` (while pressed) shrinks the button to 97% of its size with `transform: scale(0.97)`: a 100 px wide button becomes 97 px for a moment, a tiny "pressed in" feel. `.btn-primary` is the main call-to-action: `--accent` background (white) with `--accent-ink` words (near black) and a matching border. Without them the buttons would give no feedback when touched and there would be no main button.

```css
/* Focus */
:focus-visible { outline: 2px solid var(--accent); outline-offset: 3px; border-radius: 6px; }
```
A comment, then the keyboard focus ring. `:focus-visible` matches whichever element is currently selected by the keyboard (for example by pressing Tab), and only when a visible ring is useful. It gets a 2 px solid white outline (`--accent`), set 3 px away from the element (`outline-offset`) and rounded corners of 6 px. People who cannot use a mouse need this to see where they are. Without it the browser's default ring would appear, which may be hard to see on a dark page.

```css
/* Slider */
.slider { display: grid; gap: var(--s-2); }
.slider-head { display: flex; justify-content: space-between; align-items: baseline; }
```
A comment, then the slider's layout. `.slider` is a vertical stack (`display: grid`) with 8 px between its rows. `.slider-head` is the row above the slider: `display: flex` puts the label and the value on one line, `justify-content: space-between` pushes one to each end, and `align-items: baseline` lines up the bottoms of their letters. Without them the label and value would stack awkwardly.

```css
input[type="range"] {
  -webkit-appearance: none; appearance: none;
  width: 100%; height: 44px; background: transparent; cursor: pointer; margin: 0;
}
```
The rule for the slider control itself (`<input type="range">`). `-webkit-appearance: none; appearance: none;` removes the browser's own look, so the parts can be redrawn in the page's style. It is 100% wide, `height: 44px` (the finger-sized hit area; the visible line is thinner), `background: transparent`, `cursor: pointer` and `margin: 0`. Without this, the slider would look like the plain default one.

```css
input[type="range"]::-webkit-slider-runnable-track { height: 4px; border-radius: 2px; background: var(--line-strong); }
input[type="range"]::-moz-range-track { height: 4px; border-radius: 2px; background: var(--line-strong); }
```
The slider's track, the line you drag along: 4 px tall with 2 px rounded ends, in `--line-strong`. There are two rules, one with the `-webkit-` name (Chrome and Safari) and one with the `-moz-` name (Firefox), because browsers name these inner parts differently and each only reads its own. Without the pair, one family of browsers would show an unstyled track.

```css
input[type="range"]::-webkit-slider-thumb {
  -webkit-appearance: none; width: 20px; height: 20px; margin-top: -8px;
  border-radius: 50%; background: var(--accent); border: 0;
  transition: transform var(--dur-press) var(--ease-out);
}
```
The slider's thumb, the round handle you drag (Chrome and Safari version). It is 20 px by 20 px, round (`border-radius: 50%`) and white (`--accent`), with no border. `margin-top: -8px` lines it up with the thin track: the control is 44 px tall so the 4 px track sits 20 px from the top (44 - 4, halved), and the thumb is shifted 8 px up, from the track's top edge, so it covers 12 px to 32 px and its centre is at 22 px, the middle of the control. `transition: transform var(--dur-press) var(--ease-out)` lets the thumb grow smoothly when pressed. Without the margin the thumb would sit below the track.

```css
input[type="range"]::-moz-range-thumb { width: 20px; height: 20px; border-radius: 50%; background: var(--accent); border: 0; }
```
The same thumb for Firefox (`-moz-range-thumb`): 20 px, round, white, no border. Firefox centres the thumb on the track itself, so it needs no negative margin. There is no grow-on-press rule for Firefox, so no transition is set either. Without it Firefox would show the default thumb.

```css
input[type="range"]:active::-webkit-slider-thumb { transform: scale(1.15); }
```
While the slider is being pressed or dragged (`:active`), its thumb scales up to 115% (`scale(1.15)`): 20 px becomes 23 px. It is a hint that you have hold of it. Without it there would be no feedback on drag in Chrome and Safari.

```css
/* Toggle */
.toggle { display: inline-flex; align-items: center; gap: var(--s-3); min-height: 44px; cursor: pointer; }
.toggle input { position: absolute; opacity: 0; width: 1px; height: 1px; }
```
A comment, then the on/off switch (a checkbox dressed as a switch). `.toggle` is the whole clickable label: a row (`inline-flex`) with its parts centred, 12 px apart, at least 44 px tall, and a hand cursor. `.toggle input` is the real checkbox inside it. It is not removed (screen readers and the keyboard still use it) but made invisible and 1 px small: `position: absolute; opacity: 0; width: 1px; height: 1px;`. A screen reader is a program that reads the page aloud for people who cannot see it. Without hiding it, the plain browser checkbox would show beside our switch.

```css
.toggle-track {
  width: 40px; height: 24px; border-radius: var(--r-pill);
  background: var(--line-strong); position: relative;
  transition: background-color var(--dur-small) ease;
}
```
`.toggle-track` is the switch's body: 40 px wide, 24 px tall, with fully round ends, in the `--line-strong` colour (so "off" looks grey). `position: relative` makes it the reference for the knob drawn inside it. The `transition` makes its colour change over 0.18 s. Without it there would be no visible switch.

```css
.toggle-track::after {
  content: ""; position: absolute; top: 3px; left: 3px; width: 18px; height: 18px;
  border-radius: 50%; background: var(--text-muted);
  transition: transform var(--dur-small) var(--ease-out), background-color var(--dur-small) ease;
}
```
`.toggle-track::after` is the knob, an extra part drawn inside the track (after its contents). `content: ""` creates it; `position: absolute` with `top: 3px; left: 3px` places it 3 px from the top-left of the track; `width: 18px; height: 18px` gives it its size, 18 px by 18 px. It is round, grey (`--text-muted`) when off, and `transition` makes it slide and change colour smoothly (0.18 s). Check the fit: the track is 24 px tall, so 3 px + 18 px + 3 px = 24 px: the knob has equal gaps above and below. Without it there would be no knob.

```css
.toggle input:checked + .toggle-track { background: var(--accent); }
.toggle input:checked + .toggle-track::after { transform: translateX(16px); background: var(--accent-ink); }
```
The "on" state. `.toggle input:checked + .toggle-track` means "the track right after a checkbox that is ticked". The `+` means "the next element at the same level". When ticked, the track turns white (`--accent`), and its knob moves right by 16 px (`translateX(16px)`) and turns dark (`--accent-ink`). Check: the knob started 3 px from the left, so it now spans 19 px to 37 px of the 40 px track, leaving 3 px on the right, the same gap as the left. Without these two lines the switch would never look on.

```css
.toggle input:focus-visible + .toggle-track { outline: 2px solid var(--accent); outline-offset: 3px; }
```
When the real (hidden) checkbox has keyboard focus, `:focus-visible` shows the white focus ring around the visible track instead, since the checkbox itself is invisible. Without it, keyboard users would not see which switch they are on.

```css
/* State badges: the only coloured elements */
.badge {
  display: inline-flex; align-items: center; gap: var(--s-2);
```
A comment, then the badge, a small pill showing a state such as "within 5 m". `display: inline-flex` with centred contents and an 8 px gap lets the little dot and the words sit in a row. Without them the dot and words would not line up.

```css
  padding: 2px var(--s-3); border-radius: var(--r-pill);
  font: 500 var(--text-xs) var(--font-mono);
  border: 1px solid currentColor;
}
```
`padding: 2px var(--s-3)` is 2 px above and below, 12 px left and right. `border-radius: var(--r-pill)` makes it a pill. `font: 500 var(--text-xs) var(--font-mono)` makes it 12 px medium-weight number font. `border: 1px solid currentColor` draws a 1 px line in `currentColor`, a special word meaning "whatever the text colour is". So a badge's border changes colour together with its text. Without `currentColor` the border would not follow the state colour.

```css
.badge::before { content: ""; width: 6px; height: 6px; border-radius: 50%; background: currentColor; }
```
`.badge::before` is a small dot drawn before the words: an empty (`content: ""`), 6 px by 6 px shape, made round by `border-radius: 50%` and filled with `background: currentColor`, so the dot is the same colour as the text. Without it, the badge would have no dot.

```css
.is-ok { color: var(--ok); }
.is-warn { color: var(--warn); }
.is-bad { color: var(--bad); }
```
The three state classes. Add `class="is-ok"` to something and its text colour becomes green (`--ok`), `is-warn` amber, `is-bad` red. Because the badge border and dot use `currentColor`, setting the text colour is enough to colour the whole badge; the sky drawing's fix mark also uses it (below). These are the only coloured elements on the page. Without them nothing could show a state.

```css
/* Sky drawing (SVG) */
.sky-ring { fill: none; stroke: var(--line); }
.sky-sat { fill: var(--accent); transition: opacity var(--dur-small) ease; }
```
A comment, then rules for the sky drawing, which is an SVG. SVG (scalable vector graphics) is a way to draw shapes, such as circles and lines, with tags in the page; it stays sharp at any size. `.sky-ring` draws each ring with no fill (`fill: none`, see-through inside) and a faint outline (`stroke: var(--line)`; in SVG `stroke` is the outline colour and `fill` is the inside colour). `.sky-sat` is a satellite dot: filled white (`--accent`), and its opacity changes over 0.18 s. Without them the SVG shapes would be drawn in default black.

```css
.sky-sat.is-off { opacity: 0.2; }
```
A satellite that has been switched off also carries the class `is-off` (the selector `.sky-sat.is-off` means both classes together). It drops to 20% opacity, so it looks faded. Without it a switched-off satellite would look the same as one that is on.

```css
.sky-signal { stroke: var(--line-strong); stroke-dasharray: 2 4; }
.sky-fix { stroke: currentColor; fill: none; stroke-width: 2; }
```
`.sky-signal` is the line from the receiver to a satellite: a `--line-strong` outline, `stroke-dasharray: 2 4` meaning dashes 2 units long with gaps 4 units long. `.sky-fix` is the mark showing the calculated position: its outline takes the current text colour (`currentColor`, so a parent marked `is-ok`, `is-warn` or `is-bad` colours it), no fill, and `stroke-width: 2` draws a 2-unit outline. Without them the signals would be solid lines and the fix mark would have no colour.

```css
@media (prefers-reduced-motion: reduce) {
```
A media query: a block of rules that apply only when a condition is true. `prefers-reduced-motion: reduce` is true when the visitor has asked their device to cut down movement (some people get dizzy or distracted by animation). Everything between this line's `{` and the final `}` applies only then. Without it, those visitors would still get every animation.

```css
  * { transition-property: opacity, color, background-color, border-color !important; }
  .btn:active { transform: none; }
}
```
Inside the media query. For every element (`*`), `transition-property` is cut down to `opacity, color, background-color, border-color`, so only fades can animate and slides and size changes (such as a button shrinking) become instant. `!important` makes this win over any other rule. `.btn:active { transform: none; }` also cancels the button's shrink when pressed. The last `}` ends the media query. Note: the `*` rule does not reach the `::before` and `::after` extra parts, so the toggle knob (`::after`) and the slider thumb (a built-in inner part) still slide and grow; [`index.html`](../index.html.md) adds its own rule for those. Without these lines the reduced-motion request would be ignored.
