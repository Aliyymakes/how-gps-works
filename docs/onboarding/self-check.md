# Self-check

Sixty questions, ten per area. Try to answer aloud before you open the answer. Most come from [../interview-prep.md](../interview-prep.md) (same facts and numbers); where it has fewer than ten for an area, the rest are checked against the code. Questions that interview-prep leaves for the team to fill in are skipped. Numbers use the placeholders in [web/config.js](../../web/config.js) and the step files, so they change if those change.

## 1. Solver

Code: [mechanism/solver.py](../../mechanism/solver.py), [mechanism/scenario.py](../../mechanism/scenario.py). Numbers use the default satellites in [web/config.js](../../web/config.js). From interview-prep sections 1.1 to 1.7, plus code questions.

**1.1 What does `solve_position` do, in one minute?**

<details><summary>Answer</summary>

It guesses where the phone is, compares the guess with the measured distances, and improves it until it stops moving. Each round, for every satellite, it takes the straight-line distance from the guess (Pythagoras in 3D) and subtracts it from the measured distance. It asks numpy's `np.linalg.lstsq` for the small move that best reduces all the gaps, adds that move, and saves the guess in `steps`. It stops when the move is under 1 mm or after 20 guesses (`mechanism/solver.py`).

</details>

**1.2 Where does the solver start, and why does it need several steps?**

<details><summary>Answer</summary>

At the centre of the Earth with clock error 0 (comment "Start at the Earth's centre" in `solve_position`), because that needs no outside information. Each round uses a straight-line approximation of the real curved problem, which is only roughly right when the guess is far off, so each round gets closer. With a 1 µs clock error and the clock solved, `steps` held 6 guesses: the centre plus 5 improved ones (computed this run in interview-prep 1.2). The "flat version" explanation is a reading of the code, so check it with Icarus.

</details>

**1.3 What does `converged` mean, and what does the page do if it is false?**

<details><summary>Answer</summary>

`converged` is true when the last correction was under `STOP_WHEN_CHANGE_IS_SMALLER_THAN` (0.001 m). It is false if all `MAX_STEPS` (20) guesses were used. In `showWords` in [web/first-screen.js](../../web/first-screen.js), when `converged` is false the page writes "The solver did not settle on an answer."

</details>

**1.4 What does `solve_clock=False` change?**

<details><summary>Answer</summary>

The table of directions has no fourth column, so the solver finds three unknowns (x, y, z) and the clock stays 0, so `clock_error_s` comes back as 0. It needs at least 3 satellites instead of 4 (`needed = 4 if solve_clock else 3` in `solve_position`).

</details>

**1.5 Why do you need 4 satellites, not 3?**

<details><summary>Answer</summary>

Four unknowns: east, north, up and the clock error, so four measurements. `solve_position` returns `{"error": "At least 4 satellites are needed."}` for fewer when `solve_clock` is true. The page does not even call it: `runOnce` in first-screen.js writes "Four things are unknown (east, north, up and the clock), but three satellites give only three measurements." and calls `showNoFix()`.

</details>

**1.6 With 4 satellites and the clock trusted, why do the distance lines miss each other?**

<details><summary>Answer</summary>

There are more measurements than unknowns, so with a wrong clock no point fits all four distances and `lstsq` returns the best compromise, which is not the true position. With 3 satellites the three spheres would still meet at one point, just the wrong one (design.md 2b). On the first screen, 1 µs trusted gives 520.3 m; with the clock solved the error is 0 m and the clock is found as 1.00 µs.

</details>

**1.7 Is a 1 µs clock error a 300 m position error?**

<details><summary>Answer</summary>

No. 1 µs adds about 300 m to each distance (docs/facts.md row 32), but the position error depends on where the satellites are. The page always shows the error the solver computed (`Math.hypot` of east, north, up in `runOnce`), 520.3 m with the default satellites.

</details>

**1.8 Where does the measured distance come from, and is it real data?**

<details><summary>Answer</summary>

`scenario.make_pseudoranges(receiver, satellites, clock_error_s, noise_m, seed)` computes each one: true straight-line distance, plus `clock_error_s` times 299 792 458 m/s, plus random noise from `numpy.random.default_rng(seed).normal(0, noise_m)`. It is computed from the user's inputs, not prepared. The first screen passes no noise, so only the clock effect is added.

</details>

**1.9 What does each entry of `steps` hold, and in what unit is the clock?**

<details><summary>Answer</summary>

`_save_step` stores `x_m`, `y_m`, `z_m` and `clock_error_s`. Inside the loop the clock is kept as extra distance (`clock_m`, metres) for easier maths, and `_save_step` divides by `SPEED_OF_LIGHT_M_PER_S` to give seconds.

</details>

**1.10 What errors can `solve_position` return instead of an answer?**

<details><summary>Answer</summary>

Never raises on these; it returns `{"error": ...}`: different list lengths ("There must be one distance for each satellite."), too few satellites, a guess exactly on a satellite ("The guess is exactly on a satellite."), and a degenerate layout when `rank < needed` ("These satellites cannot give one clear position.").

</details>

## 2. Coordinates and the map

Code: [mechanism/coords.py](../../mechanism/coords.py), [mechanism/mapview.py](../../mechanism/mapview.py), [mechanism/constants.py](../../mechanism/constants.py). From interview-prep sections 3 and 6.1 to 6.2, plus code questions.

**2.1 What coordinate system does the mechanism use?**

<details><summary>Answer</summary>

x, y, z in metres from the centre of the Earth. x points to latitude 0, longitude 0; y to longitude 90 east; z to the north pole. `latlon_to_xyz` gives x = r cos(lat) cos(lon), y = r cos(lat) sin(lon), z = r sin(lat), with r the Earth radius (6 371 008.7714 m, docs/facts.md row 33) plus any height. `xyz_to_latlon` goes back with `atan2`.

</details>

**2.2 How is a satellite placed from azimuth and elevation?**

<details><summary>Answer</summary>

`satellite_from_sky` builds unit arrows east, north and up at the receiver (`_local_directions`), mixes them into the sky direction (cos(elevation) times a mix of east and north, plus sin(elevation) times up), then walks along it until the distance from the Earth's centre equals `GPS_ORBIT_RADIUS_M` (26 559.7 km, facts.md row 3). That is a quadratic in the distance walked; the code takes the positive root (`t = -b + math.sqrt(b * b - c)`).

</details>

**2.3 What are azimuth and elevation here?**

<details><summary>Answer</summary>

Azimuth 0 is north and 90 is east. Elevation 0 is the horizon and 90 is straight up (docs/interface.md). `satellite_from_sky` returns `{"error": "Elevation must be between 0 and 90 degrees."}` outside 0 to 90.

</details>

**2.4 What is a "distance line" on the ground map?**

<details><summary>Answer</summary>

The satellite's measured distance defines a sphere around it; the line is where that sphere cuts the ground. In `mapview.distance_lines` the sphere meets the plane where up is 0 in a circle centred right under the satellite, with radius the square root of distance squared minus up squared. `_circle_points` keeps the points inside the 2 km square. The circle is huge, so the part on the map looks almost straight.

</details>

**2.5 Which distance does each line use, and why does it matter?**

<details><summary>Answer</summary>

`distance = pseudorange - assumed_clock_error_s * SPEED_OF_LIGHT_M_PER_S`. The page passes 0 when it trusts the phone, so lines use the raw measurements and pull apart. After solving it passes the solved clock error, so they meet (`runOnce`: `assumedClockS`).

</details>

**2.6 What does `inside: false` mean?**

<details><summary>Answer</summary>

The line does not cross the square, so `points` is empty. `inside` is true only when at least 10 points land in the square (`_MIN_POINTS`). If too few do, `_circle_points` samples twice as densely, up to 20 000 (`_MAX_SAMPLES`). A line that only clips a corner is too short to draw.

</details>

**2.7 What does `mapview.to_local` return and what is it for?**

<details><summary>Answer</summary>

`{"east_m", "north_m", "up_m"}`: where a point (the solved position) is relative to the true receiver. The page takes `Math.hypot` of the three to show "Position off by", and uses east and north to place the dot.

</details>

**2.8 Why is the Earth a sphere of one radius?**

<details><summary>Answer</summary>

The real Earth is slightly flattened. The sphere keeps the conversions a few lines anyone can explain, and the simulated truth and the solver use the same model so results stay exact. The page must say it is a simplification (decisions.md 2026-11-23, provisional).

</details>

**2.9 Why a flat 2D ground map about 2 km wide?**

<details><summary>Answer</summary>

At that zoom the lines look almost straight and the map ignores "up" when drawing (design.md 2b, docs/interface.md). `mapHalfWidthM` is 1000 in [web/config.js](../../web/config.js). interview-prep gives no further reason, and neither do I.

</details>

**2.10 What happens if you pass bad input to the coordinate functions?**

<details><summary>Answer</summary>

They return an error dict, not an exception: latitude outside -90 to 90 gives "Latitude must be between -90 and 90 degrees.", and `xyz_to_latlon(0, 0, 0)` gives "The centre of the Earth has no latitude or longitude." `mapview.to_local` gives "A point needs numbers for x_m, y_m and z_m." for a bad point.

</details>

## 3. Geometry (DOP)

Code: [mechanism/geometry.py](../../mechanism/geometry.py), [web/step-geometry.js](../../web/step-geometry.js). From interview-prep section 4, plus code questions.

**3.1 What is DOP in plain words?**

<details><summary>Answer</summary>

How much the satellites' layout multiplies measurement errors. Lower is better (docs/interface.md). The page shows PDOP (`dop.pdop` in step-geometry.js). For the first screen's four default satellites it is 3.37.

</details>

**3.2 How does `dop` work?**

<details><summary>Answer</summary>

`make_table` makes one row per satellite: the unit direction from the receiver to the satellite plus a 1 for the clock. `dop` computes `table.T @ table`, inverts it with `np.linalg.inv`, and takes square roots of sums of the diagonal.

</details>

**3.3 What is the difference between GDOP, PDOP and TDOP?**

<details><summary>Answer</summary>

GDOP uses all four diagonal entries, PDOP the first three (position only), TDOP the last (the clock): `diagonal.sum()`, `diagonal[:3].sum()`, `diagonal[3]` in `dop`.

</details>

**3.4 Why does `dop` need at least 4 satellites?**

<details><summary>Answer</summary>

The table has four columns (x, y, z, clock), so fewer than four rows cannot be inverted. `make_table` returns "At least 4 satellites are needed to work out DOP."

</details>

**3.5 Does `dop` use the measured distances or the noise?**

<details><summary>Answer</summary>

No. Only the directions to the satellites (docs/interface.md), so it needs no local map frame.

</details>

**3.6 What happens to DOP when satellites are bunched, and why?**

<details><summary>Answer</summary>

It explodes. With the geometry step's placeholder sets (noise 3 m, seed 1, 1 µs clock, clock solved): spread PDOP 2.2 and the fix 4.6 m off; bunched PDOP 344.7 and 480.8 m off. The rows of the table become almost the same, so the multiplied table is almost impossible to invert. If it truly cannot be inverted, `dop` returns "These satellites are laid out so that DOP cannot be worked out."

</details>

**3.7 If DOP is only about layout, how does the geometry demo show a real position error?**

<details><summary>Answer</summary>

`runOnce` in step-geometry.js runs `solver.solve_position` with the clock solved on measurements with the same noise (`noise_m: 3`) and seed (`seed: 1`) every run, so only the layout changes. It shows PDOP and the `Math.hypot` of the east, north and up from `mapview.to_local`.

</details>

**3.8 How does the "Bunch the satellites" slider change the layout?**

<details><summary>Answer</summary>

`geometryConfig` holds two sets of azimuth and elevation, `spread` and `bunched`. The slider (0 to `slider_steps` 100) blends the angles in a straight line between them; each run asks Python for new satellite positions with `coords.satellite_from_sky`.

</details>

**3.9 What errors can `dop` return?**

<details><summary>Answer</summary>

Error dicts: receiver without numbers ("The receiver must have numbers x_m, y_m and z_m."), a satellite without numbers, a satellite at the receiver's spot ("A satellite is at the same spot as the receiver."), and a table that cannot be inverted (`np.linalg.LinAlgError`) or gives a bad diagonal.

</details>

**3.10 Why does a nearly bunched layout give a huge number rather than an error?**

<details><summary>Answer</summary>

gotchas.md (2026-11-23): bunched satellites are rarely exactly singular in floating point, so `dop` gives a huge number (about 350 for four satellites within 10 degrees). The page shows it as it is.

</details>

## 4. Signal (C/A code and correlation)

Code: [mechanism/signal.py](../../mechanism/signal.py), [web/step-signal.js](../../web/step-signal.js). From interview-prep section 5, plus code questions.

**4.1 What is the C/A code?**

<details><summary>Answer</summary>

Each satellite sends its own repeating pattern of 1023 values, each +1 or -1 (`ca_code(prn)`, `CODE_LENGTH = 1023`). It is 1 ms long (docs/facts.md rows 11 and 13). The receiver knows every satellite's pattern, so it can tell them apart.

</details>

**4.2 How is the code generated?**

<details><summary>Answer</summary>

`_logic_bits` runs two 10-stage shift registers G1 and G2, both starting as all ones, clocked once per chip. The chip is `g1_out ^ g2_out`. The G2 output XORs two stages picked by `G2_TAPS` for that PRN, which makes each satellite's code different (IS-GPS-200 Table 3-Ia, section 3.3.2.3). `ca_code` maps logic 0 to +1 and logic 1 to -1.

</details>

**4.3 What is a PRN?**

<details><summary>Answer</summary>

A whole number from 1 to 32 that picks a satellite's code. Anything else returns "prn must be a whole number from 1 to 32." The page uses `prn: 7` (`signalConfig`).

</details>

**4.4 How is a delay turned into a signal the receiver can measure?**

<details><summary>Answer</summary>

`make_received` shifts the code by `delay_chips` with `np.roll` (the end wraps to the start) and adds random noise from `default_rng(seed).normal(0.0, noise_std, 1023)`. The code itself has size 1.

</details>

**4.5 How does `correlate` find the delay?**

<details><summary>Answer</summary>

For each of 1023 shifts it computes `np.dot(values, np.roll(code_array, shift)) / CODE_LENGTH`: multiply chip by chip and average. A perfect noise-free match scores 1.0. The shift with the top score is `best_delay_chips`.

</details>

**4.6 What is `peak_to_next`?**

<details><summary>Answer</summary>

The best score divided by the second best. A big number means a clear winner. If no score is above 0 it returns 1.0; if only the best is above 0 it returns 1e9, because infinity is not valid JSON. The page calls under 1.5 "Barely found" (`barelyHoldingBelow`) and shows "over 1000×" above `peakDisplayCap`.

</details>

**4.7 Why does correlation work when the signal is below the noise?**

<details><summary>Answer</summary>

The score adds up 1023 chip-by-chip products. At the right shift they all lean the same way and add up; noise products point both ways and mostly cancel; at wrong shifts the code does not line up with itself. This is reasoning from how `correlate` averages; interview-prep says to check the wording with Icarus.

</details>

**4.8 What happens when the noise gets too big, and how does the page show it?**

<details><summary>Answer</summary>

`levelOf` in step-signal.js says "Lost" when `best_delay_chips` is not the true delay (300), "Barely found" when `peak_to_next` is under 1.5, else "Found". With PRN 7, delay 300, seed 1 (computed in interview-prep): found at noise 0, 1, 4 and 8 times the signal (peak_to_next 16.2, 7.3, 2.3 and 1.2, so 8 is "barely"), lost at 12 (best shift 713). That is one seed, not a general limit.

</details>

**4.9 Your delays are whole chips. Does that matter?**

<details><summary>Answer</summary>

In the code `make_received` rejects anything but a whole number from 0 to 1022 (float `delay_chips` or `seed` returns an error, gotchas.md). One chip is about 293 m of travel (docs/facts.md row 14, derived), so the demo cannot show smaller delays. A real receiver is not limited to whole chips. Why the team chose it: not recorded (interview-prep: team to fill in).

</details>

**4.10 Is the noise real?**

<details><summary>Answer</summary>

No. It is random numbers from a seeded generator, so a run can repeat (`make_received`; `seed: 1` in `signalConfig`).

</details>

## 5. Relativity

Code: [mechanism/relativity.py](../../mechanism/relativity.py), [scripts/check_relativity.py](../../scripts/check_relativity.py), [web/step-relativity.js](../../web/step-relativity.js). interview-prep has one question here (6.7), so most questions below come from the code, decisions.md and gotchas.md.

**5.1 What happens if all the satellite clocks drift the same way?**

<details><summary>Answer</summary>

Tested with `scripts/check_relativity.py` (its own five satellites, computed in interview-prep 6.7): with the phone's clock solved, the position error stays 0 m after a day and the solved clock grows by the drift instead, because the solver cannot tell a phone clock error from a shared satellite clock drift. With the clock trusted, the same drift gives about 17 km (17 296 m) of position error after a day. Do not say the position would be 11 km off.

</details>

**5.2 How big is the relativity drift, and where does the number come from?**

<details><summary>Answer</summary>

`RELATIVITY_DRIFT_S_PER_DAY = 38e-6` in constants.py: "about 38" microseconds a day (docs/facts.md row 27: NIST, NASA). It is 45 minus 7 rounded (rows 25, 26); the exact factory offset gives 38.58 µs (row 30), so say "about".

</details>

**5.3 What does the drift add to the distances?**

<details><summary>Answer</summary>

About 11 km of range a day: 38 µs times the speed of light is 11 392 m (facts.md row 31, D6). In `drift_over_time`, `range_added_m` is `drift_s * SPEED_OF_LIGHT_M_PER_S`.

</details>

**5.4 What does `drift_over_time` do?**

<details><summary>Answer</summary>

For each number of hours it computes `drift_s = RELATIVITY_DRIFT_S_PER_DAY * hours / 24`, makes distances with `make_pseudoranges(receiver, satellites, phone_clock_error_s + drift_s)`, then solves twice with `solve_position`: clock solved and clock trusted.

</details>

**5.5 What does it return?**

<details><summary>Answer</summary>

A list with one dict per hour: `hours`, `range_added_m`, `error_clock_solved_m`, `error_clock_trusted_m`, `solved_clock_error_s`. Bad input returns `{"error": ...}`.

</details>

**5.6 Why is the drift "the same as a phone clock error" to the solver?**

<details><summary>Answer</summary>

Every satellite's distance grows by the same number of metres, which is exactly what the clock column of 1.0s in `solve_position` models, so the clock solve takes it in. After 24 hours the solved clock reads 39.0 µs (1 from the phone plus the drift, interview-prep 6.7).

</details>

**5.7 So does relativity ever move the position in this model?**

<details><summary>Answer</summary>

Not with the clock solved. decisions.md (2026-11-23, `scripts/check_relativity.py`): position error 0.0000 m after 1 h, 6 h and 1 day. With the clock trusted, the error grows from 444 m to 17.3 km. The page can show the range error growing, not a position drift (gotchas.md).

</details>

**5.8 Why does `drift_over_time` need at least 4 satellites?**

<details><summary>Answer</summary>

Because it solves with the clock solved, which needs four (`_check_input` returns "At least 4 satellites are needed.").

</details>

**5.9 What does the relativity table on the page show?**

<details><summary>Answer</summary>

[web/step-relativity.js](../../web/step-relativity.js) calls `relativity.drift_over_time` once with `config.relativityHours` (0, 1, 6, 24) and a phone clock error of 1 µs. Columns: Hours, "Each distance gains" (`range_added_m`) and "Position off by (clock solved)" (`error_clock_solved_m`). The text under it says the position stays put.

</details>

**5.10 What input does `drift_over_time` reject?**

<details><summary>Answer</summary>

`_check_input`: fewer than 4 satellites, an empty or non-list `hours_list`, a clock error or hour that is not a finite number (booleans do not count), negative hours ("Hours must not be negative."), and points without numeric `x_m`, `y_m`, `z_m`.

</details>

## 6. Bridge and page

Code: [web/bridge.js](../../web/bridge.js), [web/first-screen.js](../../web/first-screen.js), [index.html](../../index.html). From interview-prep sections 2 and 7, plus code questions.

**6.1 What is Pyodide, and what does the bridge do?**

<details><summary>Answer</summary>

Pyodide is Python running inside the browser, so our Python runs on the user's own computer with no server. `loadMechanism` in bridge.js loads Pyodide v314.0.8 from the jsDelivr CDN, then numpy, then fetches each file in `MECHANISM_FILES` into Pyodide's in-memory file system. `callPython("solver.solve_position", [args])` sends the arguments as JSON, the helper `_bridge_call` imports `mechanism.solver` and calls the function, and the result comes back as JSON. The page needs internet the first time.

</details>

**6.2 What is allowed to cross between Python and JavaScript, and why?**

<details><summary>Answer</summary>

Only plain numbers, strings, booleans, lists and dicts; no numpy arrays or custom classes. The recorded reason: simple to convert in Pyodide and simple to explain (docs/interface.md; decisions.md 2026-11-22).

</details>

**6.3 Does the page do any GPS maths?**

<details><summary>Answer</summary>

No. It calls Python and draws what comes back. The only arithmetic is metres or chips to pixels, the slider-to-angle blend and sky scale (geometry step), scaling a bar (relativity step) and `Math.hypot` for the error length.

</details>

**6.4 What happens if Python fails or the engine cannot load?**

<details><summary>Answer</summary>

`first-screen.js` loads the bridge with `import("./bridge.js")` inside `try/catch` and shows "The calculation engine could not load, so the controls stay off. Reload the page to try again." For bad input Python returns `{"error": ...}` and `failed()` shows that sentence. If a call throws, `update` shows "Something went wrong in the calculation. Press Reset to start again." and calls `showNoFix()`. A missing unknown module or function raises "unknown module" / "unknown function" in `_bridge_call`; `callPython` rethrows the last line of the Python message.

</details>

**6.5 A Python call takes time. What stops the page showing a stale result while the user drags?**

<details><summary>Answer</summary>

`update` in first-screen.js keeps `running` and `rerun` flags: if a run is going it sets `rerun = true`, and runs once more afterwards, so the latest slider value wins. The geometry and signal steps also copy the slider value at the start of a run (`currentSky()`, `usedNoise`). The bridge itself does not protect against this.

</details>

**6.6 How do you know the numbers were computed in the browser and not prepared?**

<details><summary>Answer</summary>

The bridge fetches our `.py` files when the page loads (visible in the network tab), and every call sends the current inputs into Python. The page has no table of answers; the error is the `Math.hypot` of east, north, up that Python returned. AGENTS.md rule 7 requires the mechanism to compute from inputs with no prepared results.

</details>

**6.7 Why is the mechanism Python and not JavaScript, and why not a server?**

<details><summary>Answer</summary>

Two of the four teammates code only in Python and own the mechanism (design.md section 3). A server: the brief requires a public link with no sign-in, download or API key (design.md 1 point 3). Whether a server was considered is not recorded.

</details>

**6.8 How do the first screen and the three steps share one Pyodide?**

<details><summary>Answer</summary>

All import `./bridge.js` (one module instance), and `loadMechanism` memoises its promise (`if (!loading) loading = doLoad(onStatus)`), so Pyodide loads once (decisions.md 2026-11-23).

</details>

**6.9 What does the page do at start-up, in order?**

<details><summary>Answer</summary>

`start()` loads the bridge, `buildScene()` calls `coords.latlon_to_xyz` for the receiver and `coords.satellite_from_sky` for each satellite in `config.satellites`, then enables the controls and calls `update("start")`. If building the scene fails it says the engine could not set up the satellites.

</details>

**6.10 Where do the page's tunable numbers live, and what are the default satellites?**

<details><summary>Answer</summary>

In [web/config.js](../../web/config.js) (and `geometryConfig`, `signalConfig` in the step files), never inline. Default receiver Jakarta (-6.2, 106.8); satellites at azimuths 10, 100, 235, 325 and elevations 60, 35, 20, 20, chosen so no two lines are parallel and PDOP is under 4 (3.37; decisions.md 2026-11-24, #43).

</details>
