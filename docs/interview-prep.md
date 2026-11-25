# Interview prep: questions a judge may ask

**Draft for Icarus.** Not reviewed. Round 2 is a recorded team interview (design.md 5a): all four on camera, one take, up to 10 minutes of answers. Judges' questions are written from our submission and source code, so every teammate must be able to answer every section in their own words.

How to use this file:
- Answers marked "team to fill in" are team decisions or opinions that no code can answer. The owner says them in their own words. Nobody should invent how it works.
- Answers about the mechanism (`solver.py`, `coords.py`, `scenario.py`, `mapview.py`, `geometry.py`, `signal.py`, `relativity.py`, `scripts/check_relativity.py`) are taken from the code on `main`. Answers about the bridge come from `web/bridge.js`, and answers about the page come from `index.html`, `web/first-screen.js`, `web/step-geometry.js`, `web/step-signal.js`, `web/step-relativity.js`, `web/config.js`, `web/startup.js`, `web/say.js` and `web/format.js`. All of these are merged on `main`, and the answers were re-checked against them on 24 Nov 2026 after the final page changes (#56 to #68). The answers about the signal and relativity sections (5.7, 6.6, 6.7) were checked again on 25 Nov 2026 against the redesigned page (#77, pull request #83). For line-by-line reading of any file, see [annotated/how-to-read-code.md](annotated/how-to-read-code.md). The page shows metres through one rule (`web/format.js`: one decimal under 100 m, whole metres from 100 m up), so 520.3 m below is what the code computes and "520 m" is what the page shows.
- Numbers here are only ones that appear in docs/facts.md or that the code computed. The numbers computed by the code use the placeholder values in `web/config.js` and the step files, so they change if the placeholders change. Any number we show on the page must be checked against a source (design.md 2a).

---

## 1. The solver loop (solver.py)

Owner explains each answer in their own words. The code is on `main`. Step counts and error sizes below were computed by `solver.py` and `scenario.py` with the first screen's placeholder satellites from `web/config.js` (Jakarta, four satellites at azimuths 10, 100, 235 and 325 degrees and elevations 60, 35, 20 and 20 degrees); they can change if the placeholders change.

**1.1 What does `solve_position` do, in one minute?**
Answer: It guesses where the phone is, checks the guess against the measured distances, and improves the guess until it stops moving. Each round it works out, for every satellite, the straight-line distance from the current guess (Pythagoras in 3D) and compares it with the measured distance. The gaps tell it which way to move. It solves all the gaps together for the best small move, with numpy's `lstsq` (a least-squares fit). Then it adds that move to the guess and saves it as one step. It stops when the move is under 1 mm, or after 20 guesses (`mechanism/solver.py`).
(Contract: it takes the satellites and the measured distances and returns x, y, z, the clock error, the list of guesses (`steps`) and whether it `converged`. Source: docs/interface.md.)

**1.2 Why does the solver start from the centre of the Earth, and why does it need several steps?**
Answer: The solver knows nothing about where the phone is, so it starts at a fixed point that needs no outside information: the centre of the Earth, clock error 0 (`mechanism/solver.py`, comment "Start at the Earth's centre"). Each round it replaces the real curved problem with a flat, straight-line version of it, and that is only roughly right when the guess is far off. So one round gets close, not exact, and the next round, from the better guess, gets closer. On the first screen with a 1 microsecond clock error and the clock solved, `steps` holds 6 guesses: the centre of the Earth, then 5 improved guesses (computed by the solver this run). That "flat version" explanation is my reading of the code's `row` of directions, so check it with Icarus.
(Contract: the first guess in `steps` is the centre of the Earth. Source: docs/interface.md.)

**1.3 What does `converged` mean, and what does the page do if it is false?**
Answer: `converged` is true when the last move was smaller than 1 mm (0.001 m, `STOP_WHEN_CHANGE_IS_SMALLER_THAN`). It is false if the solver used all 20 guesses (`MAX_STEPS`) and was still moving. Separately, if the satellites cannot give one clear position, or a guess lands exactly on a satellite, the solver returns an `error` sentence instead. On the first screen (`web/first-screen.js`, `showWords`), when `converged` is false the page writes "The solver did not settle on an answer."

**1.4 What does the solver do differently with `solve_clock=False`?**
Answer: It solves for three unknowns (x, y, z) instead of four. With `True`, each row of the table gets a fourth entry, 1.0, because a clock error adds the same extra distance to every satellite, and the solver moves the clock guess too. With `False` that fourth entry is left out and the clock stays at 0, so the result says `clock_error_s` is 0. It then needs only 3 satellites instead of 4 (`mechanism/solver.py`).
(Contract: it trusts the phone's clock, keeps the clock error at 0 and needs at least 3 satellites. With `True` it needs at least 4. Source: docs/interface.md.)

**1.5 Trap: Why do you need 4 satellites, not 3?**
Conceptual part from the spec: there are four unknowns (east, north, up and the clock error), so at least four measurements are needed. The first screen refuses in one sentence when there are 3 satellites and the clock is solved (design.md 2b).
Answer for the code: at the top of `solve_position`, `needed = 4 if solve_clock else 3`. With fewer satellites it returns `{"error": "At least 4 satellites are needed."}` and does no maths. As a second safety check, if the table of directions is degenerate (`rank` below `needed`), it returns `{"error": "These satellites cannot give one clear position."}`. On the first screen (`runOnce` in `web/first-screen.js`), the page does not even call the solver for 3 satellites with the clock solved. `refuse()` writes its own sentence under the switches ("Can't solve: four things are unknown (east, north, up and the clock), but only 3 satellites are on, and each satellite gives one measurement. Turn a satellite back on."), writes "No position: see the message under the satellite switches." under the readout, and calls `showNoFix()`, which clears the metres readout, hides the badge and hides the dot, so no fix is shown. It still draws the distance lines of the satellites that are on.

**1.6 Trap: With 4 satellites and the clock trusted, why do the distance lines visibly miss each other?**
Conceptual part from the spec: there are more measurements than unknowns, so with a wrong clock they cannot all agree. With only 3 satellites the solver still lands on one point, just the wrong one, so the picture could not show the problem (design.md 2b).
Answer for what the solver then returns: with the clock trusted, it still runs, but no point fits all four distances, so `lstsq` returns the best compromise, the move that makes the gaps smallest overall. That compromise is not the true position. On the first screen, a 1 microsecond clock error that is trusted gives a fix about 520 m off (520.3 m, computed by the solver this run with the four default satellites; the page shows "520 m"). Of that, about 506 m is height (below the true spot); the dot on the map moves about 120 m. That is not 300 m: see 3.6. With the clock solved, the error is 0 m, because the solver finds the 1.00 microsecond itself.

**1.7 Where does the measured distance come from in the demo, and is it real data?**
Conceptual part from the spec: `make_pseudoranges` builds each distance as true distance, plus the clock error effect, plus random noise (docs/interface.md). It is computed from the user's inputs, not prepared (design.md 1, point 5). The README says the satellites are simulated; the page itself does not yet.
Answer for the code: `scenario.make_pseudoranges(receiver, satellites, clock_error_s, noise_m, seed)` finds each true distance by Pythagoras in 3D, adds `clock_error_s` times the speed of light (299 792 458 m/s, docs/facts.md row 2), and adds a random number from numpy's `default_rng(seed).normal(0, noise_m)`. The same seed always gives the same noise, so a run can be repeated. (The first screen passes no noise, so its distances carry only the clock effect.) The receiver comes from `coords.latlon_to_xyz` and each satellite from `coords.satellite_from_sky`, so nothing is stored in advance (`mechanism/scenario.py`).

---

## 2. The bridge (bridge.js, Pyodide)

The bridge is `web/bridge.js`, merged on `main`. These answers were checked against it.

**2.1 What is Pyodide, and what does the bridge do?**
Answer: Pyodide is Python that runs inside the browser, so our Python files can run on the user's own computer with no server. The bridge (`web/bridge.js`) does the setup and the calling. `loadMechanism` loads a pinned Pyodide version (v314.0.8) from a public CDN (jsDelivr) together with numpy, and downloads each file of the `mechanism` folder at the same time, then writes them into Pyodide's in-memory file system. While it loads, the page shows "Step 1 of 2: downloading Python and numpy. This is the slow step on a first visit…" and then "Step 2 of 2: loading our GPS code…". Then `callPython("solver.solve_position", [args])` turns the arguments into JSON text, a small Python helper (`_bridge_call`) imports `mechanism.solver` and calls the function, and the result comes back as JSON text that JavaScript turns into plain values. The first screen and the three later steps (`index.html`) all start through one shared start-up (`web/startup.js`, `whenPythonReady`) and use the same bridge, so Pyodide loads only once. The page needs internet to fetch Pyodide the first time.
(Contract: `loadMechanism(onStatus)` loads Pyodide, numpy and the mechanism files and reports progress. `callPython("module.function", [args])` calls `mechanism.<module>.<function>` and returns a plain JavaScript value. Source: docs/interface.md.)

**2.2 What is allowed to cross between Python and JavaScript, and why?**
Only plain numbers, strings, booleans, lists and dicts. No numpy arrays and no custom classes. The reason recorded is that this is simple to convert in Pyodide and simple to explain (docs/interface.md, decisions.md 2026-11-22).

**2.3 Does the page do any GPS maths?**
No. The page calls Python and draws what comes back (docs/interface.md). The only arithmetic in the page files is turning metres or chips into pixels, turning slider steps into values (for example 0.05 µs steps on the first screen), rounding numbers for display, the slider to angle blend and the sky drawing scale (geometry step), `Math.hypot` to turn east, north and up differences into one error length in metres, and, in the signal step, one sign check per step that only chooses whether a step of the phone's copy is drawn lit or dim (is it on the same side of zero as the heard value?). No number on screen comes from that check (`web/first-screen.js`, `web/step-geometry.js`, `web/step-signal.js`, `web/step-relativity.js`).

**2.4 What happens if Python fails or the engine cannot load?**
All four sections start through `whenPythonReady` in `web/startup.js`, which loads `bridge.js` inside a function that catches failure. On failure every section shows the same plain message ("Python could not be downloaded, so nothing here can calculate yet. Check your internet connection, then press Try again.") and one "Try again" button that restarts the load; the controls stay off, instead of breaking the page. For bad input, a Python function returns `{"error": "<plain message>"}` and the page shows that sentence (docs/interface.md).
Answer for the bridge (`web/bridge.js`): if you name a module or function that does not exist, Python raises "unknown module" or "unknown function". If any Python code crashes, the bridge throws a JavaScript `Error` carrying the last line of the Python message. If `callPython` is used before `loadMechanism` finished, it throws "call loadMechanism() first". A mechanism file that cannot be fetched makes the whole load fail ("could not load mechanism/<name>"), so you get the failure message and "Try again" instead of a confusing error later. If a call throws on the first screen, `update` shows "Something went wrong in the calculation. Press Reset to start again." and calls `showNoFix()`. The `{"error": ...}` sentences that Python returns on purpose are not thrown; they come back as normal results for the page to show.

**2.5 Trap: A Python call takes time. What stops the page showing a stale result while the user drags a slider?**
The first screen and the geometry and signal steps keep a `running` flag and a `rerun` flag in their `update` function. If a call is in progress, it remembers that a newer run is wanted and runs once more afterwards (`web/first-screen.js`, `web/step-geometry.js`, `web/step-signal.js`). The relativity step does the same with a `running` flag and a `wanted` flag, and starts at most one chain of Python calls per animation frame, always with the newest slider value (`web/step-relativity.js`). The geometry, signal and relativity steps also copy the slider value at the start of a run, so a run draws the value it was started with.
Answer for the bridge side (`web/bridge.js`): the bridge does not protect against this. Its `callPython` is an `async` function, but the Python call inside it runs in one go and holds the page until it returns. `loadMechanism` keeps one loading promise, so calling it twice loads Pyodide only once. Keeping the screen current is the job of each step's running flag described above.

**2.6 Trap: How do you know the numbers on screen were computed in the browser and not prepared?**
Answer: The bridge (`web/bridge.js`) fetches our `.py` files from the `mechanism/` folder when the page loads, so you can see them in the browser's network tab. Every call sends the current inputs, such as the slider value, into Python and gets a fresh result. The page has no table of answers to look up, and the first screen's error number is the `Math.hypot` of the east, north and up that Python returned (`web/first-screen.js`). Move a slider and the numbers change.
(What the repo also says: every number and line comes from the mechanism functions (design.md 2b); the mechanism must compute its outputs from the user's inputs, with no prepared results and no hosted AI (AGENTS.md rule 7).)

---

## 3. Coordinates and the map lines (coords.py, mapview.py)

**3.1 What coordinate system does the mechanism use?**
Positions are x, y, z in metres from the centre of the Earth (docs/interface.md). Latitude and longitude are converted by `latlon_to_xyz` and back by `xyz_to_latlon`.
Answer for the formulas (`mechanism/coords.py`): the Earth is a sphere of radius 6 371 008.7714 m (docs/facts.md row 33). The x axis points to latitude 0, longitude 0; y to longitude 90 east; z to the north pole. With radius r (the Earth's radius plus any height): x = r cos(lat) cos(lon), y = r cos(lat) sin(lon), z = r sin(lat). `xyz_to_latlon` goes back with `atan2`: latitude is the angle above the equator plane, longitude is the angle round the pole axis, and the height is the distance from the centre minus the Earth's radius. Latitude outside -90 to 90 returns an error sentence.

**3.2 How is a satellite placed from "azimuth and elevation"?**
Contract: `satellite_from_sky` returns a point at GPS orbit height, seen from the receiver in that direction. Azimuth 0 is north and 90 is east. Elevation 0 is the horizon and 90 is straight up (docs/interface.md).
Answer for how it is worked out (`mechanism/coords.py`): at the receiver it builds three arrows of length 1: east, north and up. The direction to the satellite is cos(elevation) times a mix of east and north (sin(azimuth) of east plus cos(azimuth) of north), plus sin(elevation) times up. Then it walks along that direction from the receiver until the distance from the centre of the Earth equals the GPS orbit radius, 26 559.7 km (docs/facts.md row 3). That is a quadratic equation, and the code takes the positive answer, the one ahead of the receiver. Elevation outside 0 to 90 returns an error sentence.

**3.3 What is a "distance line" on the ground map?**
Conceptual part from the spec: the satellite's measured distance defines a sphere around the satellite. The line is where that sphere cuts the ground. At about 2 km wide (the placeholder in design.md 2b) it looks almost straight, which is why the page calls it a "distance line" (design.md 2b, docs/interface.md).
Answer for how `distance_lines` finds the points (`mechanism/mapview.py`): it puts each satellite in a local frame of east, north and up metres around the true receiver, so the ground is the plane where up is 0. If the satellite is `up` metres above that plane and the distance is `d`, the sphere cuts the plane in a circle centred right under the satellite. By Pythagoras its radius is the square root of d squared minus up squared. The code then walks around that circle near the map square and keeps the points inside it (`_circle_points`). The circle is huge, because the satellites are about 20,200 km up (docs/facts.md row 4), so the part inside a 2 km map looks straight.

**3.4 Which distance does each line use, and why does it matter?**
Contract: `pseudorange - assumed_clock_error_s * SPEED_OF_LIGHT_M_PER_S` (docs/interface.md). So when the page assumes the clock error is 0, the lines use the raw measurements and pull apart. When it uses the solved clock error, the lines meet (design.md 2b).
Answer for the code (`mechanism/mapview.py`): `distance = pseudorange - assumed_clock_error_s * SPEED_OF_LIGHT_M_PER_S` for each satellite. The page passes 0 for the clock when it trusts the phone, and the solved clock error after the solver has run, so the lines move to meet.

**3.5 What does `inside: false` mean?**
Contract: the line does not cross the square map, so `points` is empty (docs/interface.md).
Answer for how it is decided (`mechanism/mapview.py`): `inside` is true only when at least 10 points of the circle land in the square (`_MIN_POINTS`). If too few land inside, the code samples the circle more densely, doubling each time up to 20 000 samples, and then gives up. A line that only clips a corner is too short to draw, so it gets `inside: false` and an empty `points`. If the distance is no bigger than the satellite's height above the ground plane, the sphere never reaches the plane and the line is also empty.

**3.6 Trap: A clock that is 1 microsecond ahead adds about 300 m to every distance. Is the position error 300 m?**
No. Spec: the distance error is about 300 m per microsecond, but the position error depends on where the satellites are, so the page always shows the error the solver computes, never a fixed 300 m (design.md 2b). With the four default satellites, 1 microsecond trusted gives 520.3 m (computed this run; the page shows "520 m"). Of that, about 506 m is height (below the true spot); the dot on the map moves about 120 m. The page measures it as the distance between the solved point and the true receiver (`Math.hypot` of east, north and up in `web/first-screen.js`).

**3.7 Trap: Why is the map flat when the Earth is round?**
See section 6, question 6.2.

---

## 4. DOP (geometry.py)

**4.1 What is DOP in plain words?**
It tells you how much the layout of the satellites multiplies the measurement errors. Lower is better (docs/interface.md). The page shows PDOP (`web/step-geometry.js` reads `dop.pdop`). For the first screen's four default satellites it is 3.37 (computed by `geometry.dop` this run).

**4.2 How does `dop` work?**
For each satellite it takes the direction from the receiver to the satellite as an arrow of length 1, and adds a 1 for the clock. That gives one row per satellite. It then multiplies the transpose of the table by the table itself (Hᵀ H, where H is the table; in the code `table.T @ table`). The result is 4 by 4, one row and column per unknown: x, y, z (the Earth-centred axes) and the clock. It inverts that, (Hᵀ H)⁻¹, and takes square roots of sums of the diagonal (`mechanism/geometry.py`).

**4.3 What is the difference between GDOP, PDOP and TDOP?**
From the code: GDOP uses all four diagonal entries (position and clock together), PDOP uses the first three (position only), TDOP uses the last one (the clock) (`mechanism/geometry.py`).

**4.4 Why does `dop` need at least 4 satellites?**
The table has four columns (x, y, z and clock), so with fewer than four rows the 4 by 4 product `table.T @ table` cannot be inverted. The code returns an error sentence if there are fewer than 4 (`mechanism/geometry.py`, docs/interface.md).

**4.5 Does `dop` use the measured distances or the noise?**
No. It uses only the directions to the satellites (docs/interface.md, `mechanism/geometry.py`). That is why it needs no local map frame.

**4.6 Trap: What happens to DOP when the satellites are bunched into one patch of sky, and why?**
Spec (design.md 2a rung 2): the same satellites and the same error give a far worse fix when they are bunched. Computed this run with the geometry step's placeholder sets (noise 3 m, seed 1, 1 microsecond clock, clock solved): spread out PDOP is 2.2 and the fix is 4.6 m off; bunched PDOP is 344.7 and the fix is 480.8 m off (the page shows "481 m" and "4.6 m"). Code reason: the rows of the table become almost the same, so the multiplied table is almost impossible to invert and the result gets very large. If it truly cannot be inverted, the code returns an error sentence ("These satellites are laid out so that DOP cannot be worked out.") (`mechanism/geometry.py`).

**4.7 Trap: If DOP is only about layout, how does the geometry demo show the real position error?**
The page runs the solver with the clock solved, on measurements with the same noise (3 m) and seed (1) every run, so only the layout changes between runs. The page shows PDOP and the error in metres between the solved and true positions, the `Math.hypot` of east, north and up from `mapview.to_local` (`runOnce` in `web/step-geometry.js`).

---

## 5. The C/A code and correlation (signal.py)

**5.1 What is the C/A code?**
Each satellite sends its own repeating pattern of 1023 values, each +1 or -1 (`ca_code(prn)`, docs/interface.md). The receiver knows every satellite's pattern, so it can tell them apart.

**5.2 How is the code generated?**
Two 10-stage shift registers (G1 and G2), both starting as all ones, are clocked once per chip. For each chip, the G1 output is added (XOR) to the G2 output. The G2 output adds two chosen stages, and that choice is what makes each satellite's code different (`mechanism/signal.py`, taken from IS-GPS-200 Table 3-Ia, section 3.3.2.3).

**5.3 How is a delay turned into something the receiver can measure?**
`make_received` shifts the code by a whole number of chips and wraps the end round to the start, then adds random noise with a set standard deviation and seed. The code itself has size 1 (docs/interface.md, `mechanism/signal.py`).

**5.4 How does `correlate` find the delay?**
It tries every shift of the satellite's code, multiplies it chip by chip with what was received, and averages. A perfect match with no noise scores 1.0. The shift with the highest score is `best_delay_chips` (`mechanism/signal.py`).

**5.5 What is `peak_to_next`?**
The best score divided by the second best score. A big number means a clear winner. If no score is above 0 it returns 1.0. If only the best is above 0 it returns 1e9, because infinity is not valid JSON (`mechanism/signal.py`). The page calls a value under 1.5 "Barely found" and caps the display at "over 1000×" (`web/step-signal.js`, placeholders).

**5.6 Trap: Why does correlation work when the signal is below the noise?**
Conceptual: one chip on its own is buried in noise. But the score adds up 1023 chip-by-chip products. At the right shift every product leans the same way, so they add up. Noise is random, so its products point both ways and mostly cancel. At the wrong shifts the code does not line up with itself, so those also stay small. (Reasoning from how `correlate` averages; check the explanation wording with Icarus.)

**5.7 Trap: What happens when the noise gets too big, and how does the page show it?**
The page has a noise slider and shows whether the best shift equals the true delay. When it does not, the page says "Lost"; when the peak is only barely above the next score, it says "Barely found" (`web/step-signal.js`). Where exactly it fails depends on the noise and seed. With the page's placeholders (PRN 7, delay 14 chips, seed 1, noise in steps of 0.5), the code computed this run: found up to 7.0 times the signal, barely found from 7.5 times to 11.5 times, lost at 12.0 times, the slider's last notch (best shift 713, not 14), for this one seed (PRN 7, delay 14, seed 1). Say these are for one seed, not a general limit.

**5.8 Trap: Your delays are whole chips. Real signals are not. Does that matter?**
See section 6, question 6.4.

**5.9 Is the noise real?**
It is simulated: random numbers from a generator with a fixed seed, so a run can be repeated (`mechanism/signal.py`, `web/step-signal.js`).

---

## 6. The simplifications

**6.1 Why is the Earth a sphere of one radius?**
The real Earth is slightly flattened. We use a sphere because the conversions are a few lines anyone on the team can explain. The simulated truth and the solver use the same model, so the solver recovers the simulated position to far below a millimetre. This is agreement with our own sphere model, not real-world accuracy. The README says this is a simplification; the page itself does not yet (decisions.md 2026-11-23, marked provisional).

**6.2 Why a flat 2D ground map of about 2 km?**
At that zoom the distance lines look almost straight, and the map ignores "up" when drawing (design.md 2b, docs/interface.md). The line is still where the satellite's distance sphere cuts the ground plane.
Answer for how `mapview.py` does the cut: see question 3.3. It finds the circle where the distance sphere meets the plane where up is 0, and keeps the part inside a square of half-width 1000 m by default (`half_width_m`).

**6.3 Are the satellites real?**
No. Satellites are placed from an azimuth and an elevation we choose, at GPS orbit height. The browser cannot read how many satellites the phone really uses; it only gives latitude, longitude, accuracy, altitude, heading and speed. A "real satellites above you" view was cut or left for last because predicting orbits is hard to explain and a library for it would be code we did not write (design.md 2, 2a).

**6.4 Why are signal delays whole chips?**
In the code, `delay_chips` must be a whole number from 0 to 1022 (`mechanism/signal.py`, docs/interface.md). This keeps the demo simple to explain: on the page the real delay is 14 chips and you slide the phone's copy by a whole number of chips. A real receiver is not limited to whole chips. Reason the team chose this: team to fill in.

**6.5 Is the first screen's "microsecond clock error" realistic?**
The slider range, noise and error limits are placeholders to be tuned in testing, and the page's own numbers are to be checked against a source before shipping (`web/config.js`, design.md 2a). Icarus decides which stay.

**6.6 What other simplifications should we admit?**
- The satellites do not move; each scenario is a fixed snapshot (`web/config.js` sets fixed azimuth and elevation).
- Noise on distances is a plain random value with a chosen size (docs/interface.md).
- Relativity (rung 4) is on the page as one slider from 0 to 24 hours (it starts at 24) that drives two cards (`web/step-relativity.js`, from `relativity.drift_over_time`; the function is not yet in docs/interface.md). The first card shows two clocks as digits, how far the satellite clock is ahead and how wrong each distance is. The second shows two 40 km maps: the position if the phone trusted its clock, and the position because the phone solves for its clock. It treats the drift as the same for every satellite, so solving for the clock absorbs it completely (see 6.7). The reflections step is not built; it is the first rung to cut (design.md 2b).

**6.7 Trap: What would happen if all the satellite clocks drifted the same way?**
Tested with the team's solver (`scripts/check_relativity.py`, computed this run with its own five satellites): the satellite clocks would gain about 38 microseconds a day if uncorrected; real satellites are set slow before launch to cancel it (docs/facts.md rows 28-29), and our slider (starting at 24 hours) shows the uncorrected case (row 27). Every distance changes by the same amount (a satellite clock running ahead makes each distance read shorter; our model adds it as longer, which flips the sign of the solved clock but not the position result). With the phone's clock solved, the position error stays 0 m after a day, and the solved clock grows by 38 microseconds instead, because the solver cannot tell a phone clock error from a shared satellite clock drift. With the clock trusted, the same drift gives about 17 km (17 296 m, which also includes the script's 1 microsecond phone clock error) of position error after a day, for the script's five satellites. After 24 hours the range changes by about 11 km (11 392 m is 38 µs × c; the spec's exact offset gives about 11.6 km) and the solved clock reads 39.0 microseconds (1 from the phone plus the drift). So in this model the page can show the range error growing, and a position error only if the phone trusted its clock, never a position drift with the clock solved (decisions.md, gotchas.md 2026-11-23). On the page itself (phone clock error 0, the page's four satellites), 24 hours reads 11,392 m (each distance, shown as "about 11 km"), 19,767 m (trusted, shown as "about 20 km off") and 0 m (solved, shown as "0 m off"); computed by running `relativity.drift_over_time`. The 19,767 m is bigger than the 11,392 m because the layout multiplies the range error, like DOP. Do not say the position would be 11 km off.

**6.8 Trap: What is the real accuracy of your demo compared with a phone?**
Team to fill in. Do not quote a number we have not verified (design.md 2a).

---

## 7. Why Python in the browser (design.md 3)

**7.1 Why is the mechanism written in Python and not JavaScript?**
Two of the four teammates code only in Python, and they own the mechanism (design.md 3, Icarus, 2026-11-22).

**7.2 How does Python run in a web browser?**
Through Pyodide, which runs Python in the user's browser (design.md 3). The page loads it with numpy and the mechanism files (docs/interface.md). How the loading works (`web/bridge.js`): see question 2.1.

**7.3 Why not call a server?**
The brief requires a public link with no sign-in, download or API key (design.md 1, point 3), and requires that outputs are computed by our code from the user's inputs (point 5). Running in the browser keeps it all in the page. Whether a server was ever considered: team to fill in.

**7.4 Why plain numbers, strings, lists and dicts between the two sides?**
See question 2.2.

**7.5 Trap: How do you know the page is not just playing recorded results?**
Every number and line comes from the mechanism functions (design.md 2b). The mechanism must be our own code that computes outputs from the inputs, with no prepared results (AGENTS.md rule 7, design.md 1 point 5). A judge can change a slider and see new values.

**7.6 Trap: What did you use that you did not write?**
Pyodide and numpy are open-source components, and Google Fonts supplies the typefaces. The brief allows them if the team can explain why it chose them (design.md 1, point 7). Why these two: Pyodide because the mechanism owners write Python (design.md 3). Numpy: the code uses it for the least-squares step in the solver (`np.linalg.lstsq`), the matrix inverse in `dop`, the seeded random noise in `scenario.py` and `signal.py`, and the shifting and averaging in `correlate`; why the team chose it: team to fill in. The C/A code taps come from the public IS-GPS-200 spec, cited in `mechanism/signal.py`.

---

## 8. What AI tools did and did not do

**8.1 Did you use AI tools?**
The fairness page allows AI tools for building and asks for no log or disclosure. It also says the team must understand and be able to explain its own work (design.md 5a). Roster: each teammate works with their own AI agent (AGENTS.md; design.md 4: Claude Code, Codex, Antigravity). Anything beyond that: team to fill in.

**8.2 What did AI not do?**
Answer: team to fill in.
(What the repo states: the mechanism must be the team's own code and must compute its outputs from the user's inputs, with no hosted AI in the mechanism (AGENTS.md rule 7, design.md 1 point 6). The spec, decisions and reviews are by Icarus (AGENTS.md rule 4).)

**8.3 How did you keep AI work under control?**
From AGENTS.md: one issue per session, work on a branch, merge through a pull request, never push to `main`, stage files by name, stay in your own area, and the spec is `.memory/design.md`. Every pull request has an "Explain it" part in plain words (AGENTS.md rules 1, 2, 3, 6, 8).

**8.4 Can each of you explain the code you merged?**
Rule 8 says every teammate must be able to explain the code they merge. Per-person answer: each teammate to fill in for their own files.

**8.5 Trap: Show me a part of the code where the AI was wrong and you fixed it.**
Answer: team to fill in. Use a real case from a pull request review. Do not make one up.

**8.6 Trap: If an AI wrote a function, how do you know it is correct?**
Partly from the repo: AGENTS.md rule 9 says to state plainly what was verified and what could not be. The C/A code is checked against a public spec (`mechanism/signal.py` cites its source tables). Tests and what was actually run: team to fill in from each pull request.

**8.7 Trap: What is the outside-help rule in the interview, and are you following it?**
The fairness page lists outside help in the interview as grounds for disqualification (design.md 5a). So no AI or notes during the take. Team to confirm how they will prepare.

---

## Still to fill in

- Groups 6, 7, 8: lines marked "team to fill in" (team decisions, not answerable from code): 6.4, 6.5, 6.8, 7.3, 7.6 (why numpy), and all of group 8.
