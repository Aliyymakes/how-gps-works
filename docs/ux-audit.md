# UX audit of the live page

Audit date: 2026-11-24, of https://aliyymakes.github.io/how-gps-works/ at commit `b10f664` (plan 004, item 1). Written before any fix, so it is the "before" record. Items 2 to 7 of the plan close these findings; the final review (item 12) re-runs this audit.

## How it was done

The page was driven in real browsers with Playwright: Chromium and WebKit (Safari's engine), at 1200 px and 390 px wide, by mouse, by touch emulation (390 px runs) and by keyboard only. Every control was used in every state, including silly ones: all satellites off, 45 rapid clicks, sliders at both ends, Reset straight after a drag, and resizing the window from 1200 px to 390 px and 760 px. Three more runs changed the network: a slow one (every download from the Pyodide server delayed by 4 seconds), one with that server blocked (offline), and one with one Python file missing.

For every step the script recorded all the words on the page, what the map showed, and the longest gap between two screen frames (how long the page was frozen).

Each finding below says: what the user did, what they expected, what happened, the gap, and how bad it is.

- **Blocks understanding**: a first-time user can fail to get the main idea because of it.
- **Confuses**: the user gets there, but is puzzled or misled on the way.
- **Polish**: it works and is clear, but could be nicer.

## Blocks understanding

| # | What the user did | Expected | What happened | The gap |
|---|---|---|---|---|
| B1 | Opened the page for the first time | To touch something within a second or two | Every control stayed off for 9.7 s, 32.5 s and 44.8 s in three first visits (Chromium, Chromium, WebKit). The browser downloads about 9 MB first: the Python engine (3.4 MB), its standard library (2.5 MB) and numpy (2.9 MB). The map is empty and the only words are one small grey line, "Loading the maths…". [Screenshot](ux-audit/03-loading-1200.png) | Up to a third of the two minutes passes with nothing to do, nothing to read, and no sign of how long it will take. |
| B2 | Waited, and scrolled down while waiting | Each section to say what it is waiting for | Only one section (a different one each time) shows progress ("Loading Python…", "Loading numpy…"). The other three say "Loading the maths…" until the end. Cause: `web/bridge.js` line 20 keeps only the first caller's status function. | Three of four sections look stuck. |
| B3 | Looked at the ground map | To know what the lines, the dot and the small cross are | Nothing visible says it. The explanation exists only in the hidden label for screen readers. The cross that marks the true position is dark grey on near-black (contrast 2.9 to 1) and has no label. [Screenshot](ux-audit/01-ready-1200.png) | The central picture is a starburst with no key. "Distance line" is never defined on screen. |
| B4 | Clock trusted, switched satellites off until 2, 1, then 0 were on | The map to show only the lines of satellites that are on | The map kept showing 3 lines with 2, 1 and 0 satellites on. [Screenshot](ux-audit/09-all-off.png) Cause: when Python refuses, `failed()` in `web/first-screen.js` clears the number and dot but never hides the lines. | The picture contradicts the switches. |
| B5 | Same as B4, and then pressed "Let the phone solve for its clock" with no satellites on | A sentence that is true and says what to do | With 0 on: "At least one satellite is needed." (three are needed). With 0, 1 or 2 on and the clock solved: "…but three satellites give only three measurements." (there are not three). No message says what to do next. [Screenshot](ux-audit/10-solve-no-satellites.png) | Messages contradict the screen (ui-guide section 6). |
| B6 | Pressed "Let the phone solve for its clock", then pressed it again, then moved the slider | To see which mode the phone is in | The button looks the same before and after. A second press changes nothing at all. Moving the slider silently goes back to trusting the clock, so the error jumps back with no reason given. [Screenshot](ux-audit/06-solved.png) | The main idea is "trusting the clock fails, solving for it works", and the page never shows which of the two is on. |

## Confuses

| # | What the user did | Expected | What happened | The gap |
|---|---|---|---|---|
| C1 | During the three-satellite refusal, pressed the solve button again | Some answer | Nothing changed anywhere. | Silent action. |
| C2 | Pressed Reset when everything was already at the start (all three sections) | Some answer | Nothing changed anywhere. | Silent action. |
| C3 | Switched a satellite off with the clock solved | To see at the result why there is no position | The reason appears under the switches (right place for the control used), but the "Position off by" box shows only a bare "–" above a blank area. [Screenshot](ux-audit/07-refusal-390.png) | The result box does not say "no position". |
| C4 | Dragged the clock slider to its end (3 µs) | To see the lines miss each other more and more | Two of the four lines leave the map and the other two are cut short at the edges. Nothing says so. [Screenshot](ux-audit/05-clock-max.png) | At the extreme the picture reads "the lines vanished", not "the lines miss". |
| C5 | Opened the page with the Pyodide server blocked | To be told what failed and be given a way to retry | All four sections say "The calculation engine could not load, so the controls stay off. Reload the page to try again." [Screenshot](ux-audit/04-offline-390.png) There is no button, the greyed controls carry no reason next to them, and `bridge.js` remembers the failure, so nothing but a full reload can retry. | Words are right; the action is missing. "Calculation engine" is jargon. |
| C6 | Opened the page with one Python file missing | A sentence naming the problem | The signal section shows dashes and "Something went wrong while calculating, so the picture may be out of date." Reset does nothing. The bridge only writes a warning to the console. | The page pretends to be ready when part of it cannot work. |
| C7 | Used the noise slider at 390 px | Label and value on tidy lines | The head wraps into two ragged columns: "Add / noise" and "Noise is 12.0× the / signal". [Screenshot](ux-audit/12-signal-max-390.png) The clock slider's label also wraps at 390 px. | Hard to read on a phone. |
| C8 | Pushed noise to the top | To see the noise grow | The top graph cuts values off at ±4, so from about 5× on it is a solid white block that no longer changes. Nothing says the graph is cut off. | The graph stops answering the slider. |
| C9 | Reached the relativity section | Something to touch and a result to watch | There is no control. A table shows four rows that all end in "0 m, Good fix". [Screenshot](ux-audit/13-relativity-390-webkit.png) | The one section with nothing to do; the point ("the drift is real but the clock solve absorbs it") is only in the paragraph below. The column title "Each distance gains" also has the known sign problem (gotchas.md, 2026-11-24). |
| C10 | Dragged "Bunch the satellites" to the middle | To see the fix get worse as DOP grows | At 50 % DOP has tripled (2.2 to 6.4) but the error is 7.1 m and the badge stays green. The failure only shows in the last part of the slider (344.7 and 480.8 m at 100 %). [Screenshot](ux-audit/11-geometry-bunched.png) | Nothing tells the user to keep going; the closing paragraph sits below the readouts inside the control card. |
| C11 | Used a screen reader's view of the page | Result changes to be announced | The line under "Position off by" (`#msg-readout`) has no live role, so "the distance lines miss each other" is never announced. Badges ("Good fix") are not announced either. | Feedback exists for the eye only. |
| C12 | Watched the page while Python starts | No freeze | The page froze for about 1.1 s once during start-up (longest frame gap 1102 ms in Chromium, 994 ms in WebKit). | A press during that moment gets no feedback. |
| C13 | Read the words | Plain words | "Fix", "DOP" and "calculation engine" are never explained in plain words where they first appear; "µs" is never spelled out. | Jargon for a first-time judge. |
| C14 | Pressed Tab in WebKit | Focus to move to the slider | Focus stays on the page body. Safari's default is that Tab skips sliders, buttons and switches; Option+Tab reaches all of them in the right order. | Not a page bug. Recorded so nobody "fixes" it. |

## Polish

| # | What | Gap |
|---|---|---|
| P1 | Section headings are the same size (20 px) as the "but / therefore" lines between sections. | The page reads as one grey column; sections do not stand out. |
| P2 | The first control is marked only by a white border. | Nothing says "start here", and nothing goes away once the user has started. |
| P3 | When the phone solves for its clock the lines jump to their new place in one frame. | The key moment (the lines snap together) is easy to miss. |
| P4 | An empty line is kept under every slider for messages. | It looks like something failed to load. |
| P5 | Numbers: "1,561 m" beside "520.3 m" and "0 m". | Mixed precision. |
| P6 | The dashed "true delay" marker in the signal graph uses the same dark grey as the map cross (2.7 to 2.9 to 1 on the card). | Hard to see. All other text measured 5.0 to 1 or better. |

## What already works

- **Speed after loading.** Every slider drag, switch and button was answered inside one or two frames: the longest frame gap during any interaction was 68 ms, usually 19 ms, in both browsers. No calculation needs moving off the page's thread for speed.
- **Abuse.** 45 rapid clicks on solve, switches and Reset, and Reset straight after a drag, always ended in the correct state.
- **Widths.** No sideways scrolling at 390, 760 or 1200 px, also after resizing a loaded page.
- **Keyboard.** Tab order is the reading order: clock slider, solve, four switches, Reset, bunch slider, Reset, noise slider, Reset. Every focused control shows a white ring. [Screenshot](ux-audit/14-focus-ring.png)
- **Console.** No errors or warnings on a normal load in either browser.
- **Refusal.** Three satellites with the clock solved gives the sentence from the spec and shows no number, badge or dot.
- **Offline.** All four sections say so in words; nothing shows a made-up number.

## Numbers measured

| What | Value |
|---|---|
| First visit, time until the controls work | 9.7 s, 32.5 s (Chromium), 44.8 s (WebKit); it depends on the network |
| Later visits (files already downloaded), time until the controls work | 2.4 to 3.0 s |
| Download before the controls work | about 9 MB (3.4 + 2.5 + 2.9 MB, plus small files) |
| Longest freeze while Python starts | 1102 ms (Chromium), 994 ms (WebKit) |
| Longest freeze during any interaction | 68 ms (first solve press); 18 to 40 ms otherwise |
| Contrast of grey text (#9a9a9a) on the three backgrounds | 7.0, 6.7, 6.2 to 1 |
| Contrast of the faint grey (#5f5f5f) on the three backgrounds | 3.1, 2.9, 2.7 to 1 |

## Not checked

- A real phone and real Safari: WebKit in Playwright is the same engine but not the same app.
- A real screen reader (VoiceOver): C11 comes from reading the page's roles, not from listening.
- Timing with a human: the "two minutes" is judged from load times and the number of steps, not from a test person.

## Screenshots

All in [`ux-audit/`](ux-audit/): `01-ready-1200`, `02-ready-390-webkit`, `03-loading-1200`, `04-offline-390`, `05-clock-max`, `06-solved`, `07-refusal-390`, `08-two-satellites`, `09-all-off`, `10-solve-no-satellites`, `11-geometry-bunched`, `12-signal-max-390`, `13-relativity-390-webkit`, `14-focus-ring`.
