# UI redesign plan (issue #77, branch `ui-redesign`)

Written 2026-11-24 about 21:30 WIB by the design lead, from: plan-005 and its appendix (Icarus's notes), `docs/ui-guide.md`, `docs/ux-audit.md`, the three notes in `docs/ui-research/`, report-2026-11-24c questions 1 and 5, `docs/facts.md`, `.memory/gotchas.md`, the page code, the "before" screenshots in `docs/ux-audit/redesign/before/`, and a run of the mechanism in Python to get the real numbers quoted below.

Everything here is a proposal until Icarus approves the before/after screenshots. Nothing merges before that (plan-005, approval gate).

## 1. The target experience

A judge opens the link on a phone or a laptop and, without scrolling, sees a question, a small drawing of a signal travelling from a satellite to a phone, a map with four lines meeting at a dot, and one slider with one instruction. Every picture on the page has one line above it that says what it shows, so no picture has to be decoded. Each of the four parts has one thing to do with a finger and one thing to watch, and the thing being watched stays on screen while the finger moves. The two parts that failed user testing become things you do by hand: you slide the phone's copy of the pattern until it lines up with what the phone hears, and you watch two clocks pull apart and then see why the map does not care. The page feels exact (one type scale, one spacing scale, tops of cards in line, quiet grey for everything that is not the point) and it feels alive (what you drag follows your finger in the same frame, and pictures move to their new place so you can see what changed). Every number still comes from the Python mechanism, and no motion ever makes a result wait.

## 2. What does not change

- The depth ladder and its order: two-minute idea, geometry, how the time is measured, relativity (`design.md` 2a). Relativity stays one rung; it becomes two cards inside that rung.
- Every computed result comes from `mechanism/` through `web/bridge.js`. **`mechanism/` is not touched by this plan.** Section 5 lists the calls each piece uses.
- No silent actions (ui-guide 6). Dark first. Colour only for state (ok / warn / bad). Instrument Sans and JetBrains Mono. Reduced motion respected. Motion never delays a computed result: the number is in the page as soon as Python answers, and drawing catches up.
- Illustrations are our own simple SVG, drawn by our code. Nothing is copied from any site: no layout, drawing, wording or code.
- Only numbers in `docs/facts.md` or returned by the mechanism appear on the page.
- Existing theme tokens (`--s-*`, `--text-*`, `--r-*`, the greys). The research note's 10-step grey ramp and 6/12 px radii are **not** adopted: they conflict with ui-guide section 2. One new token is proposed (section 4, improvement 7) and is a question for Icarus.

## 3. Originality: read this before building 1 and 2

`docs/ui-research/explainers.md` says Ciechanowski's GPS article reportedly uses sliding-code plots for correlation and a clock-beside-clock widget, and tells us to avoid both. Icarus's 20:00 note asks for a dragged copy and for two clocks. Icarus's note is the brief, so we build them, but the idea "slide a copy" and "compare two clocks" is the physics itself; what must be ours is the picture. What makes ours different, and must stay different:

- Signal: not plots of curves. Three rows of 40 square steps, the bottom one dragged by hand, each step lit or dimmed by whether it agrees, a score found by hand before the machine search, and a trail of the user's own tries.
- Relativity: not clock faces or bars. Two rows of digits in mono type where only the digits that differ are bright, then the same gap as a distance, then the same gap on our own ground map from the first screen, twice.

The research was read through a summarising tool, so nobody on this run has seen that article. **Before merge, one person opens it and compares it with our two sections by eye** (Question 1).

## 4. The improvements, ranked

Order of groups, as the brief sets it: user testing and the per-section labels and illustrations (1 to 4), the 19:30 fixes (5 to 10), report questions 1 and 5 (11, 12), motion and feel (13 to 15).

Sizes: S under 45 minutes, M 1 to 2 hours, L 2 to 3 hours, for one Sonnet implementer including its tests. "Must" fits before 25 Nov 10:00 WIB. "If time" is built only when every Must is reviewed.

| # | Improvement | Size | When |
|---|---|---|---|
| 1 | Signal section rebuilt: slide the copy by hand | L | Must |
| 2 | Relativity split into two steps | L | Must |
| 3 | "What you're looking at" line on every picture | S | Must |
| 4 | A small drawing for the first screen and for geometry | M | Must (first screen), if time (geometry) |
| 5 | Phone: first action above the fold | M | Must |
| 6 | Card spacing and aligned tops | S | Must |
| 7 | Text hierarchy: headings lead, bridges go quiet | S | Must |
| 8 | One bridge between geometry and signal | S | Must |
| 9 | Signal: the real delay is always visible | built in 1 | Must |
| 10 | Relativity: starts with the effect showing | built in 2 | Must |
| 11 | Phone: compact sticky map | built with 5 | Must |
| 12 | Phone: the step-1 hint is on the first screen | built with 5 | Must |
| 13 | Lines glide on Reset and on satellite switches | S | If time |
| 14 | Drawings play once when they scroll into view | S | If time |
| 15 | Exact press, hover and drag states | S | If time |

Each entry below has: **What**, **Why**, **Quality** (which quality and from where), **Check** (a testable check, a Playwright test idea, the screenshot-only reader test), **Taste call**.

The reader test, used throughout: a Haiku subagent gets only the section's screenshot at 390 px and at 1200 px, with no other context, and answers three questions: "What does this picture show? What should you do here? What is the point?" The entry says what the answer must contain. If it does not, the section is not done.

---

### 1. Signal section rebuilt: slide the copy by hand

**What.** File: `web/step-signal.js` (rewrite of `PAGE_HTML`, `STYLE`, `draw`; the start-up, `update`/`runOnce` pattern and `say` stay). Tests: `tests/ui/test_layers.py`, `test_accessibility.py`, `test_final_fixes.py`.

Config changes in `signalConfig`: `trueDelayChips: 14` (was 300), new `windowChips: 40`, new `shift: { min: 0, max: 30, start: 0 }`. Why 14: the delay must fit inside the 40-step picture so it can be found by hand. Checked in Python with PRN 7, seed 1: at delay 14 the best shift is 14 for noise 0 to 10 and is lost at noise 12 (the slider's last notch), so the existing "Lost" behaviour stays. The implementer re-checks every half step.

Heading and words (drafts for Icarus):
- h2: "How does the phone measure the time?" (unchanged)
- Under it: "Every satellite repeats a pattern the phone already knows. The phone slides its own copy along what it hears. How far it has to slide is how late the signal arrived."

Left card, the picture:
1. The line: "**What you're looking at:** 40 steps of one satellite's pattern (the whole pattern has 1023). Top: what the satellite sends. Middle: what the phone hears, a little later. Bottom: the phone's own copy. Slide it."
2. The drawing (the 20:05 illustration for this section): three tiny frames in a row, 12 steps each, static, labelled "1 The pattern", "2 It arrives late", "3 Slide your copy until it lines up". Fixed sketch, no numbers.
3. One SVG, `viewBox="0 0 400 210"`, three rows, each a square wave of 40 steps 10 units wide, with the row's name in plain text at its left above the wave:
   - "What the satellite sends": `code[0..39]`, grey line.
   - "What the phone hears": `received[0..39]`, white line, values cut off at ±`receivedLimit` as today (the clip note stays).
   - "The phone's own copy": 40 steps showing `code[(i - shift) mod 1023]`. Each step is a filled block: white where its sign agrees with the heard value above it, dim grey (`--text-muted` at 40 % opacity) where it disagrees. No state colour here: agreeing is not "ok", it is just lit.
   - A thin bracket from the left edge to the start of the copy, labelled "slid N chips".
4. Dragging: the copy row is the handle. `pointerdown` on it captures the pointer; it follows the finger 1:1 with no easing and snaps to whole chips; about 8 px of sideways movement before a drag starts, so a vertical swipe still scrolls (`touch-action: pan-y`). Cursor `grab` / `grabbing`. The row has a white outline while it is the current step of the guide.
5. Under the SVG a real range input, `data-el="shift"`, label "Slide the phone's copy", value "N chips". It and the drag set the same number. Arrow keys move one chip, never animated. This is the keyboard and screen-reader path; `aria-valuetext`: "Copy slid N chips. Match score X."
6. The live score, big mono number, `data-el="hand-score"`, label "Match score", with a thin meter bar under it. Caption: "Counted over the whole 1023-step pattern, not only the 40 steps shown. 1.00 means every step agrees. Near 0 means no better than chance." (This caption is needed: at a wrong shift the 40 visible steps can look half right while the score is near 0, and the page must not contradict itself.)
7. When `shift` equals `trueDelayChips`: the sentence (`data-el="hand-sentence"`, live region) says "Lined up. You slid the copy 14 chips, so the signal arrived 14 chips late." Otherwise: "Not lined up yet. Keep sliding."
8. An honest note in small grey: "Here the delay is short so it fits in the picture. A real one can be anywhere in the 1023 steps."

Under the rows, in the same card, the search:
9. Button `data-el="search"`: "Let the phone try every shift". Under it two plots:
   - "The first 40 shifts, close up": 40 bars in line with the 40 steps above. Before the button is pressed it shows a bar only for each shift the user has visited by hand ("your tries"). After, all 40.
   - "All 1023 shifts": the full score line as today (`viewBox` 0 to 1023).
   - Pressing the button reveals both left to right over 1000 ms, linear (`clip-path` on a wrapper, so only the clip animates). Reduced motion or a keyboard press: at once. Any new input ends the reveal at once. The readout numbers go into the page the moment Python has answered, before the reveal finishes.
   - After the first press, noise changes redraw both plots at once, with no reveal.
10. Markers (this is improvement 9): above each plot a small white tick with the words "real delay", placed from `trueDelayChips`; below each plot a tick in the state colour with the words "phone's best match", placed from `best_delay_chips`. One sits above and one below, so both are seen when they are at the same shift. When the best match is outside 0 to 39 the close-up says: "The phone's best match is now at shift N, outside this close-up."

Right card, controls and result (top lines up with the left card, no outer wrapper; see improvement 6):
11. Status line (`data-el="status"`), then a three-step guide in the style of the first screen, one hint at a time (`data-el="hint"`): "Step 1. Slide the phone's copy until it lines up with what the phone hears." → "Step 2. Now let the phone do the same search by itself." → "Step 3. Add noise until the phone loses the signal." All three controls are enabled as soon as Python is ready; the guide only moves the white border.
12. Noise slider: keeps `id="signal-noise"`, `data-el="noise"`, `data-el="noise-value"`, `data-el="msg-slider"`, label "Add noise".
13. Readout, filled once the search has been pressed (before: "–" and the line "Press the button and the phone searches."): "Best match found at" `data-el="best-delay"`; "Real delay" `data-el="true-delay"`; "Best score is this many times the runner-up" `data-el="peak"`; badge `data-el="badge"` (Found / Barely found / Lost); sentence `data-el="sentence"` as today.
14. Reset (`data-el="reset"`, `data-el="msg-reset"`): copy back to 0, noise 0, tries cleared, search not pressed. Message: "Back to the start: copy at 0, no noise."

Mechanism calls (all existing, `docs/interface.md`): `signal.ca_code(prn)` once at start; per noise value `signal.make_received(prn, trueDelayChips, noise, seed)` then `signal.correlate(received, prn)`, exactly as today. Dragging makes no Python call: the score shown is `scores[shift]` from the last `correlate`, and the copy row is `ca_code` read at a shifted index. **One thing is done in JavaScript that is not a mechanism output:** whether a step is lit is a sign comparison between two numbers Python returned. It only chooses a fill; no number on screen comes from it. This is said plainly in the PR. If the team wants even that in Python, it needs a new mechanism function, which is flagged here and not planned.

**Why.** Testers saw "a glitchy texture block". 1023 steps in 500 px cannot be read; 40 can. Finding the match by hand is the idea itself: the judge feels the score jump, then the automatic search is "the phone does what I just did, 1023 times". The noise step then answers a question the judge already has.

**Quality.** Direct manipulation, 1:1 under the finger, no easing while dragging (Apple, WWDC18 "Designing Fluid Interfaces", `motion.md` source 2). Step down to one case, step up to all cases, linked by markers (Bret Victor, "Up and Down the Ladder of Abstraction", `explainers.md` 6). A picture that already teaches before any touch, and one line that says what to try (Red Blob Games, `explainers.md` 2). Saying what is simplified (`explainers.md` 1, as an idea only).

**Check.**
- Testable: with no noise, `hand-score` reads "1.00" only at 14 chips; the sentence says "Lined up"; at noise 12 the badge is "Lost".
- Playwright: fill `[data-el=shift]` with 14, assert `hand-score` is "1.00" and the sentence starts "Lined up"; fill 13, assert the score starts "0.0" or "-0.0"; drag the copy row with `page.mouse` by 14 step widths and assert the range input's value is "14"; press search, assert `best-delay` is "14 chips" at once (before 1000 ms); assert both marker labels are visible and do not overlap (bounding boxes); set noise to 24, assert badge "Lost" and the close-up's "outside this close-up" line. Reduced-motion run: the plots are complete on the next frame. Check opacity with computed style, not `is_visible` (gotchas).
- Reader test passes when the answer contains: a pattern is sent; the phone hears it later; you slide the copy until it matches; the amount slid is the delay.

**Taste call for Icarus:** yes, all of it. In particular: the three row names, the score as a number (1.00) and not a percentage, the delay of 14, lit/dim in white and grey with no colour, and the wording.

---

### 2. Relativity split into two steps

**What.** Files: `web/step-relativity.js` (rewrite of `PAGE`, `STYLE`, `showResult`), `web/config.js` (`relativitySlider`), `web/format.js` (one new formatter). Tests: `tests/ui/test_layers.py` and others that name `#step-relativity`.

Config: `relativitySlider = { min_h: 0, max_h: 24, step_h: 1, start_h: 24 }` (the range stays 0 to 24 h; only the start changes from 0 to 24, which is improvement 10). New `relativityMapHalfWidthM: 20000`. Both numbers come from a run of `mapview.distance_lines` with the page's satellites: with the clock trusted at 24 h, a 40 km wide map keeps all four lines on it, a 20 km wide map loses two, and at 48 h even a 40 km map loses two. So the slider stops at 24 h and the maps are 40 km wide.

New formatter in `web/format.js`, `formatRoughDistance(m)`: under 1000 m use `formatMetres`; from 1 km one decimal ("2.8 km"); from 10 km whole kilometres ("11 km"). The word "about" is in the labels, because gotchas says never to show these as exact.

One heading for the rung, then two cards, one under the other, each with a small "First" / "Then" label (the existing `.label` class).

- h2: "Do the satellites' own clocks matter?" (unchanged)
- The one control sits above both cards and drives both: slider `id="rel-hours"`, `data-id="slider"`, label "Time since the satellite clocks were last corrected", value "24 h" (`data-id="slider-value"`, as today). Hint (`data-id="hint"`): "Drag this back to 0 and the two clocks agree. Drag it forward and watch the gap grow."

**Card a, "Satellite clocks run fast."**
1. "**What you're looking at:** two clocks that started together. One stayed on the ground. One is on a GPS satellite."
2. The drawing (20:05): a curve for the ground with a small clock on it, a small satellite above with a clock, a short stroke by the satellite's clock that reads "ahead". Static sketch.
3. Two rows of mono digits, the same width, one above the other:
   - "Clock on the ground" `24:00:00.000 000`
   - "Clock on the satellite" `24:00:00.000 038`
   Digits that are the same in both rows are `--text-muted`; digits that differ are `--text`. The hours come from the slider; the six decimals of the satellite row are the gap from Python rounded to whole millionths of a second, written as digits. No tenths: gotchas says 38 must never look exact to a decimal. Small caption: "The last digits are millionths of a second (µs)."
4. Two readouts side by side: "Satellite clock ahead by" `data-id="gap"`, "about 38 µs" (always whole µs, the same rounding as the digit rows, so the two never disagree); and "So every measured distance is wrong by" `data-id="range"`, "about 11 km". Under them one grey line: "A signal covers about 300 m in one millionth of a second." (facts row 32)
5. The why, three short rows, fixed text from `docs/facts.md` rows 25 to 27, not scaled by the slider:
   - "Weaker gravity up there: the clock runs faster, by 45 µs a day"
   - "It moves fast: the clock runs slower, by 7 µs a day"
   - "Together: about 38 µs a day faster"
   A line under them: "Both effects come from Einstein's relativity. Gravity is the bigger one."
6. Only if Icarus says yes (Question 5): "Real GPS satellites are built with their clocks set to tick slightly slow, so that in orbit they keep time with the ground."

**Card b, "So why doesn't your position drift?"**
1. "**What you're looking at:** the map from the top of the page, twice, with every satellite clock ahead by the same amount. Each map is 40 km wide."
2. Two square maps side by side (stacked under 420 px), drawn like the first screen: frame, cross at the true place, distance lines, dot.
   - Left, title "The phone trusts its clock": lines miss, dot away from the cross. Readout `data-id="trusted"` with badge `data-id="trusted-badge"`: "about 20 km off". Small grey line: "Most of that is height, which a flat map cannot show. The dot shows the sideways part." Under the map, the first screen's caption rule is reused: if `distance_lines` reports a line with `inside` false, the caption says "N of the 4 distance lines have moved off the edge of this map." (With the numbers above this should not happen; the rule is there so the picture never hides it.)
   - Right, title "The phone solves for its clock": lines meet on the cross. Readout `data-id="solved"` with badge `data-id="solved-badge"`: "0 m off".
3. One sentence (`data-id="sentence"`, live region): "Every satellite is off by the same amount. To the phone that looks exactly like its own clock being wrong, and the fourth satellite already fixes that." At 0 h: "No gap yet. Both maps agree."
4. Reset (`data-id="reset"`, `data-id="msg-reset"`): back to 24 h. Message: "Back to the start: one day."

On a 40 km map the dot's sideways move at 24 h is about a quarter of the way from the centre to the edge, so each map must be at least 150 px wide at 390 px (two side by side fit) and the dot and cross must not overlap; the implementer checks this in the first screenshot.

The closing paragraph under the old card is removed (it repeats the sentence).

The honest number in 2b: at 24 h the mechanism gives a position error of 19.8 km when the clock is trusted, but only about 4.6 km of that is sideways; the rest is downward. The readout shows the mechanism's figure and the grey line says why the dot looks closer. Do not drop that line.

Words to avoid in this section (there is a test, and a gotcha about the sign): "gain", "longer", "shorter", including "no longer". Say "ahead", "fast", "wrong by".

Mechanism calls (all existing): `coords.latlon_to_xyz`, `coords.satellite_from_sky` at start, as today. Per slider value:
- `relativity.drift_over_time(receiver, satellites, 0, [hours])` → `range_added_m` (the "wrong by" readout), `solved_clock_error_s` (the gap in µs and the satellite row's digits), `error_clock_trusted_m`, `error_clock_solved_m` (the two "off" readouts and badges).
- For the two maps: `scenario.make_pseudoranges(receiver, satellites, solved_clock_error_s)`, then `solver.solve_position(satellites, ranges, False)` and `(…, True)`, then `mapview.to_local` for each answer and `mapview.distance_lines(lat, lon, satellites, ranges, 0, 20000, 40)` and `(…, solved clock, 20000, 40)`. This is the chain the first screen already uses. The value passed as the clock error is a number Python returned; JavaScript does no arithmetic on it.

Three flags, none of them planned work:
- `drift_over_time` is not listed in `docs/interface.md` (the file only says later rungs add it). The contract should gain its row; that is a doc change to list in the PR, not a mechanism change.
- The only source of the gap in seconds is `solved_clock_error_s`, which is what the solver found, not a separately returned drift. With the phone's own error at 0 they are the same number. A cleaner `drift_s` field would be a mechanism change.
- A breakdown that grows with the slider (gravity part, speed part) would need the mechanism to return the two parts. So the breakdown is fixed text per day.

If time: a "Play one day" button that moves the slider from 0 to 24 h over about 3 seconds (reduced motion: jumps). Not in the Must build.

**Why.** Testers did not get it because one table tried to say two things. Now each card says one: (a) the clocks really do pull apart, and that is kilometres; (b) and yet the dot stays, because the phone was already solving for exactly this kind of error. Card b reuses the first screen's map, so the judge needs no new picture to understand it; it is the first screen's lesson paying off.

**Quality.** One idea per picture, and the next picture answers the question the last one raised (ui-guide 1.3, 1.4; `explainers.md` 1, idea only). Make the claim testable by the reader: trust the clock or solve for it, side by side (Bret Victor, "Explorable Explanations", `explainers.md` 5). A warning against the likely misreading, next to the figure (Distill, `explainers.md` 4). Mono, tabular digits and exact alignment for comparison (Vercel Geist typography, `layout.md` 1.1).

**Check.**
- Testable: at load the section already shows a gap, a distance and two different maps. At 0 h both digit rows are identical and both maps agree.
- Playwright: on load assert `gap` contains "38", `range` contains "11 km", `trusted-badge` is "Fix is far off", `solved-badge` is "Good fix", and the two dots' positions differ by more than 20 px; fill the slider with 0 and assert the two digit rows have equal text and `sentence` starts "No gap yet"; Reset returns the slider to "24"; the section's words never contain gain, longer, shorter; no sideways scroll at 390 px.
- Reader test passes when the answer contains: the satellite clock is ahead; that makes distances wrong by kilometres; trusting the clock moves the position; solving for the clock keeps it; because the error is the same for every satellite.

**Taste call for Icarus:** yes, all of it. In particular: digits instead of clock faces, starting at one day, the 40 km maps, the fixed-text breakdown, and the wording.

---

### 3. "What you're looking at" line on every picture

**What.** A shared class, `.looking`, in `index.html`'s style block, where `.hint` already lives (ui-guide section 2 says additions to `theme.css` need their own issue; the section files are mounted into this page, so the rule reaches them). It is `--text-sm`, colour `--text`, margin below `--s-3`, with its lead-in words "What you're looking at:" in weight 600. It replaces the small grey capitals ("GROUND MAP", "SKY, SEEN FROM BELOW") as the first thing in each picture card; the old label text moves into the SVG's `aria-label` where it is not there already.

- First screen (`index.html`), placed directly above the map card and outside it, because on phones that card is sticky and must stay small (improvements 5 and 11): "**What you're looking at:** a map of the ground around the phone. Each line is one satellite's distance to you. Where the lines meet is where your phone thinks you are." (Icarus's own example sentence.)
- Geometry (`web/step-geometry.js`): "**What you're looking at:** the sky above the phone, seen from below. Each dot is a satellite. The centre is straight overhead, the edge is the horizon." The separate line "Edge is the horizon, centre is straight overhead." is then removed.
- Signal and relativity: written in improvements 1 and 2.

**Why.** Audit B3: the central picture was "a starburst with no key". The key helps once you look for it; a sentence above the picture is read first.

**Quality.** Prose that points at the figure and says what to look for (Distill, `explainers.md` 4; Red Blob Games, `explainers.md` 2). Words next to what they describe (ui-guide 1.6).

**Check.** Testable: every picture card starts with a `.looking` line. Playwright: every picture has a visible `.looking` whose box is above the picture's box and within 40 px of it; computed opacity 1. Reader test: for each section, the answer to "what does this picture show?" matches the line's content without the reader having seen the rest of the page.

**Taste call:** the wording of each line.

---

### 4. A small drawing for the first screen and for geometry

**What.** New file `web/illustrations.js` exporting functions that return SVG markup strings; shared class `.figure` in `index.html`'s style block (white and grey strokes 1.5 px, text `--text-xs`, no fill colour). Every drawing has `role="img"` and an `aria-label` that says the same thing as its labels. Drawings are sketches: no numbers, and the caption style makes that clear. (The signal and relativity drawings are built inside improvements 1 and 2 and may live in their own files, so those two can be built at the same time.)

- First screen (Must): a strip above the map, 64 px tall on phones, about 96 px on desktop. Left: a small satellite. Right: a phone. Between them a dashed line with one short pulse on it. Under the line: "travel time × speed of light = distance". At the far right, after a small arrow: a short straight line labelled "one distance = one line on the map". It replaces the first intro paragraph, which says the same thing in more words. The second intro sentence moves into the step-1 hint (improvement 5).
- Geometry (if time): two small circles side by side. Left, "Spread out": four dots around the circle and a small shaded patch in the middle, labelled "small zone of doubt". Right, "Bunched": four dots close together and a long thin shaded patch, labelled "large zone of doubt". Caption: "Sketch, not to scale." The patches are grey, not coloured.

**Why.** Icarus, 20:05: show the idea in its simplest form before the user touches anything. On the first screen the drawing also earns its space by letting the intro lose a paragraph, which is what puts the slider above the fold on phones.

**Quality.** A diagram that teaches before any click (Red Blob Games, `explainers.md` 2). Monochrome first, colour only for state (Vercel brand guidelines, `layout.md` 1.3).

**Check.** Testable: the drawing is in the first HTML (it must not wait for Python: gotchas, 9 MB download), so it is on screen within the first paint. Playwright: with the CDN delayed 3000 ms, the first-screen figure is visible within 1 s; `test_speed` still passes in WebKit. Reader test: shown only the strip, the reader says "a signal goes from a satellite to a phone, and the time it takes gives the distance".

**Taste call:** the drawing style, and removing the intro paragraph.

---

### 5. Phone: first action above the fold

**What.** Files: `index.html` (markup order and the style block), `web/first-screen.js` (only if an id moves; all ids stay). Built together with 11 and 12.

At 390 × 844 the first screen is, top to bottom: the h1; the drawing strip (improvement 4); the "What you're looking at" line; the compact map with the result beside it (improvement 11); the slider block with its hint. The budget, to be measured, not trusted: 16 padding + about 70 h1 + 64 strip + about 63 line + about 214 map + about 130 slider block + gaps = about 600 px.

To get there:
- The intro's two paragraphs go: the first is replaced by the drawing and the "looking at" line, the second becomes the hint.
- Hint 1 becomes: "Step 1. This only works if the phone's clock is right. Drag the slider to make it wrong."
- The map key and the caption move out of the map card into their own block (`.map-notes`). Desktop: under the map card in the left column. Phones: after the controls.
- The slider block's hint and its message share one line above the slider (see improvement 6), so the block is one line shorter.

If the measured bottom of the slider is still below 620 px, the drawing strip moves below the controls on phones only. The slider wins over the drawing.

**Why.** 19:30 note, item 1, "highest priority": a judge on a phone sees a title, text and a picture, and nothing to do. The two-minute path starts with the slider.

**Quality.** Fitts's law: the main control near the result and within the thumb's reach (Laws of UX, `layout.md` 3). First control within about 600 px on a 390 × 844 phone (`layout.md` 6.2, from Vercel's guidelines on mobile density).

**Check.** Testable: at 390 × 844, with no scrolling, the whole slider and its hint are on screen. Playwright (Chromium and WebKit): viewport 390 × 844, after ready, `#clock` bounding box bottom ≤ 620 and `#hint-1` box inside the viewport with computed opacity 1; the same before ready (the disabled slider and the status line are in place, nothing jumps when Python arrives: compare `#clock`'s y before and after, difference ≤ 2 px). Reader test, phone screenshot only: "what can you do on this screen?" → "drag the slider to make the clock wrong".

**Taste call:** yes: losing the intro paragraphs, and the new hint wording.

---

### 6. Card spacing and aligned tops

**What.** Files: `index.html` style block, the `STYLE` strings in `web/step-geometry.js`, `step-signal.js`, `step-relativity.js`.

- The empty band under the clock slider: the block reserves one line for `#msg-slider` under the slider and has `.guide-target` padding around it. Put the hint and the message in one reserved line above the slider (the hint shows at step 1; after that the line is free for the message). One reserved line, not two.
- The empty space under the "Step 2" button and above the satellite switches: `#msg-solve` and `#msg-switch` keep a line when empty. Make them collapse when empty (they answer a press, not a drag, so a one-line shift is acceptable), and cancel the grid gap an empty line still takes: `.stack > .note:empty { margin-bottom: calc(-1 * var(--s-4)); }` (do not use `display: none` on a live region). The same rule removes the empty band at the top of the right-hand cards once the status line empties.
- Side-by-side cards: `align-items: stretch`, the same `--pad-card` on both, and the first child of each starts at the same y. In geometry and signal the right card must not wrap its content in a second padded box.
- Every gap is a token: `--s-2` inside a control block, `--s-4` between blocks in a card, `--s-5` between cards, `--s-7` before a new section (was `--s-6`).
- The first screen's result box moves into the map card (needed by 11), which also shortens the tall right-hand card so the two columns end nearer the same height.

**Why.** 19:30 item 2. Uneven gaps read as "something failed to load" (audit P4) and make the page look unfinished next to the precision we want.

**Quality.** Vercel precision: one spacing scale, tighter inside a group than between groups, tops aligned by the grid and not by eye (`layout.md` 1.2, 1.6). Proximity and common region (Laws of UX, `layout.md` 3).

**Check.** Testable: no empty band taller than `--s-5` inside any card at rest. Playwright: for each pair of side-by-side cards at 1200 px, the tops differ by ≤ 1 px and the first children's tops differ by ≤ 1 px; in `#block-slider`, the distance from the slider's bottom to the block's bottom is ≤ 24 px at rest; dragging the clock slider does not move the solve button (y before and after within 1 px). Reader test: not applicable; reviewed by screenshot pair.

**Taste call:** small. The one visible trade: a message appearing under the solve button now pushes the switches down by one line.

---

### 7. Text hierarchy: headings lead, bridges go quiet

**What.** Files: `web/theme.css` (one token), `index.html` style block.

- Section headings (h2) go from 20 px to 24 px, weight 600, colour `--text`. This needs one new token, `--text-h: 24px`, in `theme.css` (Question 4). h1 stays 32 px.
- Bridges (`.link-line`) keep their size, 18 px, and keep no `max-width`: **do not change either**. Gotchas records that WebKit reported no first paint with 16 px or a width cap there, cause unknown. They go quiet by colour and weight only: whole line `--text-muted`, weight 400, and the "but" / "therefore" words become weight 500 in `--text-muted` too, no white.
- Each bridge moves close to the heading it leads into: `--s-7` above the bridge, `--s-3` between the bridge and the h2. Today it floats halfway between two sections.
- A small part label above each h2 in the existing `.label` style: "Part 2 of 4", "Part 3 of 4", "Part 4 of 4" (and "Part 1 of 4" above the h1). "Part", not "Step", because the first screen's hints already say "Step 1".
- Section subtitles are `--text-md` in `--text-muted` today and stay so.

After any change to `.link-line`, re-run `tests/ui/test_speed.py` in WebKit three times.

**Why.** 19:30 item 3 and audit P1: headings and bridges are the same size, so the page reads as one grey column and a judge skimming cannot see where a part starts.

**Quality.** Vercel precision: few type steps, each with one job; emphasis by weight and colour inside a size (`layout.md` 1.1). De-emphasise the secondary so the primary stands out (Refactoring UI, `layout.md` 2, secondary source).

**Check.** Testable: in every section the h2 has the largest font size and the brightest colour of any text in that section. Playwright: computed font size of each h2 is greater than that of the `.link-line` before it; the link line's colour equals `--text-muted`; the gap between link line and h2 is smaller than the gap above the link line; `test_speed` passes in WebKit. Reader test, full-page screenshot at 1200 px scaled down: "how many parts does this page have and what are their titles?" → four, with the four questions.

**Taste call:** yes: the new token, the part labels, the bridges losing their white words.

---

### 8. One bridge between geometry and signal

**What.** File: `web/step-geometry.js`. The closing paragraph (`.geo-closing`) loses its last sentence and becomes: "Spread out, the same errors barely move the fix. Bunched, they multiply." The bridge in `index.html` ("Good geometry only helps if the phone can read each distance in the first place, **but** the signal is buried in noise. **Therefore** the phone has to dig out the timing.") stays, because every other join on the page uses that form. `test_layers.py` checks only that `.geo-closing` exists once and sits outside the control card; both stay true.

**Why.** 19:30 item 4: two paragraphs in a row saying nearly the same thing.

**Quality.** Each part ends on the problem the next one solves, once (ui-guide 1.4; `explainers.md` 1, idea only).

**Check.** Playwright: `.geo-closing` text does not contain "next". Reader test: not needed.

**Taste call:** which of the two to keep. Recommendation above.

---

### 9. Signal: the real delay is always visible

Built in improvement 1, point 10: "real delay" is a labelled white tick above the plots, "phone's best match" a labelled tick in the state colour below them, so they never hide each other; the full-width plot is joined by a close-up of the first 40 shifts. Closes 19:30 item 5 and audit P6 (the old dashed marker was 2.7 to 1 against the card; the new tick uses `--text`).

**Why.** The proof that the search worked is that the phone's answer sits on the real delay. If one mark hides the other, the judge sees one line and no proof.

**Quality.** Known truth drawn beside the result so the reader can judge it (Distill, `explainers.md` 4). Exact alignment and labels in place of a legend (Vercel, `layout.md` 1.6; Refactoring UI, `layout.md` 2).

**Check.** Playwright: with no noise both labels are visible, their boxes do not overlap, and their x centres are within 2 px of each other. Contrast test: the tick colour against the card is at least 3 to 1.

**Taste call:** covered by 1.

### 10. Relativity: starts with the effect showing

Built in improvement 2: the slider starts at 24 h, so the first thing seen is a gap of about 38 µs, about 11 km, and two maps that differ. The hint tells the user to drag back to 0. Closes 19:30 item 6 and audit C9.

**Quality.** Start every picture in a state that already teaches (Red Blob Games, `explainers.md` 2).

**Check.** Playwright: on load, before any input, `[data-id=range]` is not "0 m", and all four lines of the trusted-clock map are drawn (none has the hidden class). Reader test: covered by 2.

**Taste call:** yes (Question 3): start at one day, or start at 0 with a stronger hint.

---

### 11. Phone: compact sticky map (report question 1)

**What.** File: `index.html` style block and markup. Built with 5.

Under 760 px wide and at least 600 px tall, the map card is `position: sticky; top: 0`, with an opaque `--surface` background and `z-index: 2`. Inside it, two columns: the map on the left, about 46 % of the card (about 160 to 180 px square); on the right the result: "Position off by", the number, the badge, and the one-line message (`#error-value`, `#error-badge`, `#msg-readout`, same ids, moved in the markup from the controls card into the map card). On desktop the same result box sits under the map inside the map card.

The card sticks only while its parent (the first screen's `.grid`) is on screen, so it lets go by itself when the user scrolls on to geometry. Every control below it gets `scroll-margin-top` equal to the sticky card's height plus `--s-3`, so a focused control is never under it.

The ready-made closing line ("That is the main idea…") still scrolls into view as today.

**Why.** Report question 1 (finding N4): on a phone, when the user presses the solve button the map is off screen, so the moment the lines come together, which is the main idea of the page, is not seen. The earlier recommendation was "keep, no layout risk before judging"; plan-005 puts the sticky map in scope now.

**Quality.** Apple fluidity: the thing you are changing answers where you are looking, as you touch (WWDC18, `motion.md` source 2). A compact sticky result on phones, safe-area and focus rules (Vercel guidelines, `layout.md` 1.7).

**Check.** Testable: on a phone, at the moment each first-screen control is used, the map and the number are on screen. Playwright (390 × 844, both browsers): scroll `#solve` into view and click it: `#map` and `#error-value` boxes are inside the viewport; same for each satellite switch and Reset; Tab (Alt+Tab in WebKit) through the controls and assert each focused control's box does not intersect the sticky card's box; scroll to `#step-geometry` and assert the map card is out of the viewport; at 390 × 500 (landscape-like) the card is not sticky; no sideways scroll. Reader test, phone screenshot taken just after pressing solve: "what just happened?" → "the lines meet again and the position is right".

**Taste call:** yes (Question 2). It changes how the first screen looks on every phone.

### 12. Phone: the step-1 hint is on the first screen (report question 5)

Closed by improvement 5: the hint sits directly above the slider, and both are above the fold. No separate build.

**Why.** The hint is the only thing that says "start here". Below the fold, a phone user has a control and no instruction.

**Quality.** Text that tells the reader exactly what to try, next to the control (Red Blob Games, `explainers.md` 2; ui-guide 1.6).

**Check.** The Playwright check in 5 (`#hint-1` inside the 390 × 844 viewport, computed opacity 1).

**Taste call:** no.

---

### 13. Lines glide on Reset and on satellite switches (if time)

**What.** File: `web/first-screen.js`. Today the lines glide (450 ms) only when the solve button is pressed with a mouse or finger. Use the same `glide()` when Reset is pressed and when a satellite is switched back on or off with the clock solved, so the picture moves to its new state. Rules unchanged: never while dragging the slider (it tracks the finger directly), never for keyboard presses, never under reduced motion, and a new input ends a glide at once (`cancelGlide` already does this). The number and the words are set at once, as now.

ui-guide section 3 allows springs only for drags with momentum, so this stays the existing ease-out glide. A spring that keeps its speed when interrupted (`motion.md` proposal) is a possible later change and would need Icarus's yes.

**Why.** A jump hides what changed; a 450 ms move shows which line went where.

**Quality.** Apple fluidity: changes are continuous and can be redirected mid-way (WWDC18, `motion.md` source 2). Emil Kowalski: frequency decides: occasional actions may animate, constant ones must not (`motion.md` source 1).

**Check.** Playwright: after clicking Reset with a mouse, a line's `points` attribute changes over several frames and ends equal to the directly drawn result; with reduced motion it is final on the next frame; `#error-value` holds the final text on the first frame. Reader test: not applicable.

**Taste call:** yes, like the first glide (report-24c taste call 2).

### 14. Drawings play once when they scroll into view (if time)

**What.** File: `web/illustrations.js`. Each drawing may move once, for at most 1.2 s, the first time it is at least half on screen (`IntersectionObserver`): the pulse travels from satellite to phone; the small copy slides until it lines up; the satellite clock's "ahead" stroke grows. Only `transform` and `opacity`. Reduced motion: still, shown in its end state. The end state is what is in the HTML, so a screenshot or a slow device always shows a complete drawing.

**Why.** 20:05 note: "may animate gently once". The motion says which way the idea runs (signal goes down, copy slides right).

**Quality.** A little delight for things seen once (ui-guide 3; Emil Kowalski, `motion.md` source 1).

**Check.** Playwright: under reduced motion no drawing has a running animation (`getAnimations().length === 0`); without it, each drawing has none 2 s after scrolling into view. Reader test: unchanged from 4 (the still frame must pass by itself).

**Taste call:** yes.

### 15. Exact press, hover and drag states (if time)

**What.** File: `index.html` style block (and `theme.css` only if Icarus agrees). Slider thumb: scale 1.15 while pressed, 120 ms `--ease-out`. Switch rows and the signal copy row: hover raises the border one step (`--line` to `--line-strong`), 120 ms. Buttons already scale to 0.97 on press. All transitions on `transform`, `opacity`, `border-color` only; removed under reduced motion except colour.

**Why.** Small, but it is what makes a control feel like it heard the finger before the result arrives (ui-guide 6: feedback within 100 ms).

**Quality.** Vercel precision: hover, active and focus each clearly stronger than rest, fast and subtle (`layout.md` 1.5). Press feedback at touch-down (Apple WWDC18; Emil Kowalski's 0.97 press scale; `motion.md` sources 1 and 2).

**Check.** Playwright: computed `transition-duration` on these is ≤ 160 ms; the existing reduced-motion test for the thumb still passes. Reader test: not applicable.

**Taste call:** yes.

---

### Considered and left out

- **The dot easing through each solver step** (19:45 idea). `solve_position` returns its steps, but it starts at the centre of the Earth, thousands of kilometres from a 2 km map, so nearly every step would be off the map and the "convergence" would be one jump at the end. Showing it properly needs a different picture. Not for this deadline.
- **The readout counting smoothly to its new number** (19:45 idea). The numbers in between were never computed by anything; showing them breaks "every number comes from the mechanism". The glide already shows the change.
- **Dragging satellites in the sky view** (19:45 idea). Worth doing, but it is a new input model (polar limits, keyboard path, four free satellites instead of one clear slider) in a section that passed user testing. Too large and too risky before the 10:00 deadline; propose after the freeze if Icarus wants it.
- **A new grey ramp and 6/12 px radii** (`layout.md`). Conflicts with ui-guide section 2; the existing tokens already do the job.
- **Sticky pictures on phones in parts 2 to 4.** Same benefit as 11, but each is a layout risk; only after 11 is approved.

## 5. Where each computed thing comes from

| Piece | Call (all in `docs/interface.md` except where noted) |
|---|---|
| First screen: lines, dot, error, clock words | unchanged: `scenario.make_pseudoranges`, `solver.solve_position`, `mapview.to_local`, `mapview.distance_lines` |
| Geometry | unchanged: `geometry.dop`, `scenario.make_pseudoranges`, `solver.solve_position`, `mapview.to_local` |
| Signal: the three rows | `signal.ca_code(7)` (top row and the copy), `signal.make_received(7, 14, noise, 1)` (middle row) |
| Signal: hand score, both plots, best match, runner-up ratio | `signal.correlate(received, 7)` → `scores[shift]`, `scores`, `best_delay_chips`, `peak_to_next` |
| Signal: lit or dim steps | sign comparison in JavaScript of values from the two calls above (drawing only; flagged) |
| Relativity a: gap, distance | `relativity.drift_over_time` → `solved_clock_error_s`, `range_added_m` (function exists in `mechanism/relativity.py` but is missing from `docs/interface.md`; flagged) |
| Relativity a: 45, 7, 38 µs a day | fixed text, `docs/facts.md` rows 26, 25, 27 |
| Relativity b: the two "off" numbers and badges | `relativity.drift_over_time` → `error_clock_trusted_m`, `error_clock_solved_m` |
| Relativity b: the two maps | `scenario.make_pseudoranges`, `solver.solve_position` (False and True), `mapview.to_local`, `mapview.distance_lines` with `half_width_m` 20000 |
| All drawings (illustrations) | no numbers; fixed sketches |

Nothing in this plan needs a mechanism change.

## 6. Build order

One improvement at a time, each reviewed by the design lead with screenshots at 390 and 1200 px in Chromium and WebKit before the next one in the same lane starts. Three lanes can run at the same time in separate worktrees because they touch different files. If Icarus has not answered by 16:00, only the signal section, the relativity section and the phone layout merge (plan-005), so steps 1 to 3 below must each work without steps 4 onward.

| Step | Improvement | Files | Lane |
|---|---|---|---|
| 0 | Shared classes only: `.looking`, `.figure`. No visible change. | `index.html` (style block) | first, alone |
| 1 | 1 Signal rebuild (with 9, its own label and drawing) | `web/step-signal.js`, `tests/ui/test_layers.py`, `test_accessibility.py`, `test_final_fixes.py` | A |
| 2 | 2 Relativity split (with 10, its own label and drawing) | `web/step-relativity.js`, `web/config.js`, `web/format.js`, tests | B |
| 3 | 5 + 11 + 12 Phone layout, with the first-screen label (part of 3) and the first-screen drawing (part of 4) | `index.html`, `web/first-screen.js`, `web/illustrations.js` (new), tests | C |
| 4 | 3 (geometry label) + 8 (one bridge) | `web/step-geometry.js` | A, after step 1 |
| 5 | 7 Text hierarchy | `web/theme.css`, `index.html` | C, after step 3 |
| 6 | 6 Card spacing | `index.html`, the three `step-*.js` style strings | after 1 to 5, alone |
| 7 | 4 Geometry drawing (if time) | `web/illustrations.js`, `web/step-geometry.js` | after 6 |
| 8 | 13, 14, 15 (if time), in that order | `web/first-screen.js`; `web/illustrations.js`; `index.html` | after 6 |
| 9 | Annotations for every changed web file, once, at the end | `docs/annotated/web/*`, `docs/annotated/index.html.md` | after the last page change |
| 10 | Reader tests, after-screenshots, PR | `docs/ux-audit/redesign/after/` | last |

Files touched by more than one step, so never at the same time:
- `index.html`: steps 0, 3, 5, 6, 8 (15).
- `web/theme.css`: step 5 only (the `--text-h` token, if Icarus agrees).
- `web/step-geometry.js`: steps 4, 6, 7.
- `web/step-signal.js` and `web/step-relativity.js`: their own rebuild, then step 6.
- `web/illustrations.js`: steps 3, 7, 8 (14).
- `tests/ui/test_layers.py`, `test_accessibility.py`, `test_final_fixes.py`: steps 1 and 2 both edit them, in different tests. Merge lane A before lane B rebases, or the other way round; do not edit the same test in both.

Tests that will fail until rewritten, so nobody is surprised:
- `test_layers.py::test_hints_show_after_ready…` (the signal hint now hides after the copy is slid, not after noise; the relativity slider no longer starts at 0).
- `test_layers.py::test_signal_clip_note_badge…` (still valid if `clip-note`, `badge`, `noise`, `noise-value` keep their names; the badge appears only after the search is pressed, so the test presses it).
- `test_layers.py::test_relativity_slider_results_and_reset` (starts at 24 h, new number format, new reset message).
- `test_accessibility.py` near line 385 (it picks the signal SVGs by position).
- `test_first_two_minutes.py` wherever it reads the intro words.
- `tests/test_annotations.py` for every changed web file until step 9.

The full UI suite takes minutes; run the changed test file first, the full suite once per step, in the background.

Time budget (now about 21:30 on 24 Nov; the PR must be open by 10:00 on 25 Nov; 12.5 hours):

| When | What |
|---|---|
| 21:30 to 22:00 | step 0, lanes start |
| 22:00 to 01:30 | steps 1, 2, 3 in three lanes, each with one review round and one fix round |
| 01:30 to 03:30 | steps 4, 5, 6 |
| 03:30 to 05:00 | reader tests for all four parts; redo what fails |
| 05:00 to 06:30 | if time: steps 7 and 8 |
| 06:30 to 08:30 | step 9, full suite in both browsers, after-screenshots |
| 08:30 to 09:30 | PR with a before/after pair per improvement, desktop and phone |
| 09:30 to 10:00 | spare |

If steps 1 to 3 are not all reviewed by 03:00, drop steps 7 and 8 without asking.

## 7. Questions for Icarus

Each is a taste call or a fact call. The recommendation is what gets built as the draft.

1. **Likeness to Ciechanowski's GPS article.** Our research note says his article slides a code copy and compares clocks; your 20:00 note asks for both ideas. We build them with our own pictures (section 3). Nobody on this run has seen his page. *Recommendation:* you or a teammate open it once and compare with our signal and relativity sections before merge. If either looks alike, say so and we change the picture, not the idea.
2. **Phones: a compact sticky map** with the result beside it, and the intro paragraphs replaced by a drawing and a one-line label so the slider is on the first screen. *Recommendation:* yes. It is the only way the map and the control are seen together on a phone.
3. **Relativity starts at one day**, with the gap already showing (the slider still runs 0 to 24 h). *Recommendation:* yes. Starting at 0 shows a row of zeros, which is what testers saw.
4. **One new type size, 24 px, for section headings** (`--text-h` in `theme.css`), and small "Part 2 of 4" labels. The bridges keep their size and go grey. *Recommendation:* yes to both. Without the token the fallback is headings at 20 px and bridges grey, which is a weaker fix.
5. **The sentence about clocks being set slow before launch.** `docs/facts.md` rows 28 and 29 confirm the factory offset from IS-GPS-200N, but the sheet does not quote the words that say the offset is there to cancel relativity. *Recommendation:* someone adds that quote to `facts.md` first (same document, section 3.3.1.1), then the sentence goes in. If nobody has, leave it out.
6. **Signal: the delay becomes 14 chips** (was 300) so it can be found by hand inside a 40-step picture, with a line on the page saying it is short on purpose. *Recommendation:* yes.
7. **Signal: the match score as a plain number** ("1.00", "0.06") with a one-line explanation, not a percentage. With noise the score can pass 1.00, and a percentage over 100 looks like a bug. *Recommendation:* the number.
8. **Signal: lit and dim steps are chosen in JavaScript** by comparing two values Python returned. No number on screen comes from it. *Recommendation:* accept and say so in the PR. The other way is a new mechanism function after the freeze.
9. **Relativity, trusted-clock map: "about 20 km off" beside a dot that looks 4.6 km away**, because most of the error is height. The page says so in one grey line. *Recommendation:* keep the mechanism's number and the line. Showing only the sideways part would need arithmetic on the page.
10. **Relativity: digits, not clock faces.** Two rows of mono digits with the differing digits bright. A clock face cannot show millionths of a second without faking the scale. *Recommendation:* digits.
11. **Motion left out:** the dot stepping through the solver's guesses, numbers counting up, and dragging satellites in the sky (reasons in "Considered and left out"). *Recommendation:* agree for this deadline; satellite dragging can be proposed again after the freeze.
12. **All new wording** (the five "What you're looking at" lines, the row names, the hints, the two relativity card titles, the breakdown lines). Each is in this document. *Recommendation:* read them in the screenshots and strike what you do not like; every one is a single string in one file.

## 8. Verified and not verified

Verified while writing this plan:
- The numbers quoted for relativity (38 µs, 11.4 km, 19.8 km, about 4.6 km sideways at 24 h; solved-clock error 0 m at every hour tried up to 168 h) and for the signal (delay 14 found for noise 0 to 10, lost at 12; off-peak scores of about −0.06, 0.00, 0.06; ratio 16.2 with no noise) came from running `mechanism/` in Python with the page's config.
- The call chain for the two relativity maps was run in Python: `make_pseudoranges`, both `solve_position` calls, `to_local`, and `distance_lines` at half-widths of 10, 15, 20, 30 and 40 km for 6, 12, 24 and 48 h. Result: with the clock trusted at 24 h, lines on the map are 2 of 4 at 10 km, 3 of 4 at 15 km, 4 of 4 at 20 km; at 48 h, 0 of 4 at 10 and 15 km, 2 of 4 at 20 km. With the clock solved all four are on the map every time.
- The current page was read in the "before" screenshots (Chromium and WebKit, 390 and 1200 px) and in the code.

Not verified:
- Nothing in this plan has been built. The phone height budget (about 600 px) is arithmetic from the current type sizes, not a measurement.
- How long 7 Python calls per relativity slider move take in the browser. The first screen makes 4 and stays inside two frames; if 7 is too slow, the maps update on release and the numbers on every move.
- Whether the sticky map behaves in real Safari on a real phone (Playwright's WebKit is the same engine, not the same app).
- The originality question in section 3.
