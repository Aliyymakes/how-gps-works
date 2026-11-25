# Decisions

Each record: we chose X over Y because Z; the cost is W. Sources are mainly [.memory/decisions.md](../../.memory/decisions.md) ("decisions.md" below, cited by entry date and file) and [.memory/design.md](../../.memory/design.md) ("design.md", cited by section). Where no reason is written there, the record says "reason not recorded". Some records also cite .memory/gotchas.md, docs/facts.md or the code where they add a cost or a fact; each says so where it does. Nothing here is new.

## 1. Python in the browser (Pyodide)

- We chose: the mechanism in Python, run in the user's browser through Pyodide.
- Over: not named in the sources.
- Because: "two of the four teammates code only in Python, and they own the mechanism" (design.md section 3, Icarus, 2026-11-22).
- The cost: Pyodide downloads when the page first opens and takes a few seconds, so a loading message is needed (.memory/gotchas.md, 2026-11-22). A first visit downloads about 9 MB and took 9.7 s to 44.8 s to be ready in the audit (gotchas.md, 2026-11-24). So every section shows the same progress words, "Step 1 of 2: downloading Python and numpy. This is the slow step on a first visit…" then "Step 2 of 2: loading our GPS code…", and one "Try again" if the download fails (`web/startup.js`; decisions.md, 2026-11-24). To make it faster, numpy loads with Pyodide and our files download in parallel; there is no Web Worker because no interaction took over 100 ms (decisions.md, 2026-11-24, `web/bridge.js`).
- Also recorded: Pyodide pinned to v314.0.8 from jsDelivr, and CI moved to Python 3.14 to match (decisions.md, 2026-11-23, `web/bridge.js`).

## 2. A sphere Earth

- We chose: the Earth as a sphere of one radius.
- Over: the real, slightly flattened shape.
- Because: "the conversions are a few lines anyone on the team can explain, and the simulated truth and the solver use the same model so results stay exact" (decisions.md, 2026-11-23, `docs/interface.md`, `mechanism/coords.py`; marked provisional). In plain terms: the solver recovers the simulated position to far below a millimetre. This is agreement with our own sphere model, not real-world accuracy.
- The cost: the page must say this is a simplification (same entry). The sources do not give a size for the error.

## 3. The 2D ground map

- We chose: a local flat map about 2 km wide, centred on the true position, east and north in metres, up ignored for drawing; one "distance line" per satellite where its distance sphere cuts the ground (design.md section 2b item 2; `docs/interface.md` section on `mapview.py`).
- Over: not named in the sources.
- Because: reason not recorded. design.md section 2b explains why the screen uses four satellites with the clock trusted (more measurements than unknowns, so the lines visibly miss each other), but not why a flat map was chosen.
- The cost: "The lines look almost straight at this zoom" (design.md section 2b). decisions.md (2026-11-23, `mechanism/mapview.py`) says a line that only clips a corner by a few points is not drawn, and the map size is a placeholder (design.md section 2b item 2).

## 4. Solving for the clock

- We chose: the solver can solve for the phone's clock as well as the position (`solve_clock`), and the first screen contrasts "clock trusted" with "clock solved".
- Over: trusting the phone's clock.
- Because: with 4 satellites and the clock trusted there are more measurements than unknowns, "the distance lines visibly miss each other"; with the clock solved they meet (design.md section 2b). With 3 satellites and a wrong clock the spheres still meet at one point, "just the wrong one", so that picture could not show the failure (same section). The page decides refusals by counting the switched-on satellites: fewer than 4 with the clock solved, fewer than 3 with the clock trusted (decisions.md, 2026-11-24, `web/first-screen.js`).
- The cost: four unknowns need four satellites. With three the page refuses in words, with the true count: four unknowns (east, north, up, clock), and only as many measurements as satellites that are on (design.md section 2b item 5; the sentence is in `refuse()` in first-screen.js), and it still draws the lines of the satellites that are on. Also design.md section 2b: the position error depends on where the satellites are, so the page shows the solver's error and never a fixed 300 m.

## 5. Whole-chip code delays

- We chose: the delay in the signal step is a whole number of chips.
- Over: not named in the sources.
- Because: reason not recorded in decisions.md or design.md.
- The cost: not recorded in those files. What the code shows: `signal.make_received` returns an error unless `delay_chips` is a whole number from 0 to 1022. One chip is about 293 m of travel (docs/facts.md row 14, derived), so a whole-chip delay cannot show smaller steps. The page's real delay is 14 chips (it was 300): ui-redesign.md says the delay must fit inside the 40-step picture so a reader can find it by hand, by sliding the phone's copy a whole number of chips (`signalConfig.trueDelayChips`, `shift` in web/step-signal.js).

## 6. The relativity result

- We chose: rung 4 shows, for a slider of 0 to 24 hours (it starts at 24, so the effect is already showing), the satellite clock pulling ahead of a ground clock, the range error growing, and two small maps: the position if the phone trusted its clock and the position when the phone solves for its clock (which stays at 0), not a drifting position.
- Over: a position that drifts.
- Because: design.md section 2b says rung 4 "is tested before it is promised": a drift shared by all satellites may be absorbed by the clock solve. The test (decisions.md, 2026-11-23, `scripts/check_relativity.py`) found a shared drift of 38 µs a day is absorbed completely: position error 0.0000 m after 1 h, 6 h and 1 day, while the solved clock error grows by the drift. With the clock trusted, the error grows from 444 m to 17.3 km (these are the script's five satellites; with the page's four satellites and a phone clock error of 0 the trusted error is 0 m at 0 h and 19,767 m at 24 h, which the page now shows as "about 20 km off" on the "The phone trusts its clock" map and "0 m off" on the "The phone solves for its clock" map; the phone clock error is 0 on purpose, so that at 0 h "No gap yet. Both maps agree." is true, decisions.md 2026-11-24).
- The cost: the page cannot say "your position would be 11 km off per day". The drift adds about 11 km of range a day, but the position stays put when the clock is solved (.memory/gotchas.md, 2026-11-23). decisions.md marks the entry provisional, and design.md section 2a says the 38 µs figure is "from memory, unverified" (later confirmed as "about 38" in docs/facts.md row 27).

## 7. No frameworks

- We chose: a page of plain HTML, CSS and JavaScript (design.md section 3: "The page is HTML, CSS and JavaScript"). No `package.json` or build files appear in `git ls-files`.
- Over: a framework: not named in the sources.
- Because: reason not recorded. The nearest written lines are that the theme "built new" from the UI guide (decisions.md, 2026-11-23, `web/theme.css`, `web/theme.js`) and that step sections each export a `mount...Step(container)` function and inject their own style (decisions.md, 2026-11-23, `web/step-geometry.js`, `web/step-signal.js`).
- The cost: not recorded.
