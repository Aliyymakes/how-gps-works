# Follow one click

Two traces through the first screen. Everything below is in [web/first-screen.js](../../web/first-screen.js) (JavaScript), [web/bridge.js](../../web/bridge.js) (the bridge), [web/startup.js](../../web/startup.js) (the shared start-up) and `mechanism/` (Python). Line-by-line notes: [annotated first-screen.js](../annotated/web/first-screen.js.md). Defaults come from [web/config.js](../../web/config.js): the receiver is Jakarta (`lat_deg: -6.2, lon_deg: 106.8`); the four satellites are at azimuths 10, 100, 235, 325 degrees and elevations 60, 35, 20, 20 degrees.

## Before any click: the scene is built once

`start()` in first-screen.js calls `whenPythonReady` from [startup.js](../../web/startup.js). That file loads the bridge once for all four sections, and while it loads it puts progress words in each section's status line ("Step 1 of 2: downloading Python and numpy. This is the slow step on a first visit…", then "Step 2 of 2: loading our GPS code…"). The controls stay off until it finishes. If the download fails, the status line says so and one "Try again" button appears; pressing it restarts the load. When it finishes, startup.js calls the function `start()` gave it, and that calls `buildScene()` to turn the config into points:

- `callPython("coords.latlon_to_xyz", [lat_deg, lon_deg])` gives `receiverPoint`.
- For each satellite, `callPython("coords.satellite_from_sky", [lat_deg, lon_deg, azimuth_deg, elevation_deg])` gives its x,y,z. The page stores them in `allSatellites` with their `id`.

Then it enables the controls, calls `showGuide()` (the three-step hints, see the end of this file) and calls `update("start")`. Until then the map shows "The map appears when Python has loaded."

## Part 1: dragging the clock slider ("Make the phone's clock wrong")

### 1. The browser event

The slider is `<input id="clock" type="range">` in [index.html](../../index.html), labelled "Make the phone's clock wrong". The browser fires an `input` event on every small move while you drag. `setupControls()` registered the handler:

```js
el.slider.addEventListener("input", () => {
  const wasSolved = state.mode === "solved";
  state.clockErrorS = Number(el.slider.value) * config.clockSlider.step_s + config.clockSlider.min_s;
  state.mode = "trusted"; // moving the slider again goes back to trusting the clock
  showMode();
  showClockValue();
  update(wasSolved ? "slider-back" : "slider");
});
```

The slider counts whole steps (0 to 60), and the code multiplies by `step_s` (0.05 microseconds) to get seconds. At the right-hand end `state.clockErrorS` is 3e-6 (3 microseconds). `showMode()` puts the solve button back to "Let the phone solve for its clock" (once solved it reads "The phone is solving for its clock"). `showClockValue()` writes the label, for example "1.00 µs", using `formatMicroseconds`. If you had solved the clock, the cause is `"slider-back"` and the page says "Back to trusting the clock. Press the button below to solve for it again."

### 2. `update("slider")` queues the work

`update(cause)` makes sure Python calls run one at a time. If a run is already going it sets `rerun = true` and returns, and the loop `do { ... } while (rerun)` runs once more when the current one finishes. So fast dragging never piles up calls and the latest slider value wins (decisions.md, 2026-11-23).

### 3. `runOnce("slider")` asks Python four times, in this order

Mode is "trusted", so `solveClock` is `false`. `sats` is the satellites whose switch is on (all four at the start). (If fewer than 3 are on, the page refuses before any Python call; see Part 2.)

| Step | JavaScript call | What Python runs | What comes back |
|---|---|---|---|
| 1 | `callPython("scenario.make_pseudoranges", [receiverPoint, sats, state.clockErrorS])` | `make_pseudoranges` in [scenario.py](../../mechanism/scenario.py): for each satellite, straight-line distance (Pythagoras) plus `clock_error_s * SPEED_OF_LIGHT_M_PER_S`; noise is 0 here because the page passes no `noise_m` | a list of four numbers, metres |
| 2 | `callPython("solver.solve_position", [sats, ranges, solveClock])` | `solve_position` in [solver.py](../../mechanism/solver.py): starts at the Earth's centre, repeats a least-squares correction (`np.linalg.lstsq`), at most 19 corrections (`MAX_STEPS` = 20 counts the saved guesses, including the start), and stops when the length of the whole correction (position and clock term, in metres) is under 1 mm; with `solve_clock=False` it trusts the clock (clock stays 0) | `{"x_m","y_m","z_m","clock_error_s","converged","steps"}` |
| 3 | `callPython("mapview.to_local", [lat_deg, lon_deg, point])` | `to_local` in [mapview.py](../../mechanism/mapview.py): the solved point minus the true receiver, measured along the local east, north and up directions (`coords._local_directions`) | `{"east_m","north_m","up_m"}` |
| 4 | `callPython("mapview.distance_lines", [lat_deg, lon_deg, sats, ranges, assumedClockS, config.mapHalfWidthM, config.lineSamples])` | `distance_lines` in mapview.py: for each satellite, takes the distance (pseudorange minus the assumed clock effect), finds the circle where that distance sphere cuts the ground (the flat plane up = 0 at the true receiver), and samples points that fall inside the 2 km square (`_circle_points`) | a list of four `{"id","points","inside"}` |

`assumedClockS` is `0` in trusted mode, so the lines use the raw (wrong) distances. If any call returns `{"error": ...}`, `failed()` writes Python's sentence into the message slot and `showNoFix()` clears the dot.

### 4. Crossing the bridge (the same for every call)

`callPython` in bridge.js does four things: `JSON.stringify(args)`, call the Python helper `_bridge_call("module.function", args_json)`, which runs `importlib.import_module("mechanism." + module_name)`, `json.loads` the arguments, calls the function, and returns `json.dumps(result)`; then `JSON.parse` turns the text back into a JavaScript value.

### 5. From numbers to pixels

Back in `runOnce`:

```js
const errorM = Math.hypot(local.east_m, local.north_m, local.up_m);
requestAnimationFrame(() => draw(lines, local, errorM, animate));
showWords(solution, errorM, solveClock);
```

- The error shown is `Math.hypot` of the three local numbers: straight-line distance between the solved dot and the true spot. It is the one piece of arithmetic on the page besides drawing scale.
- `draw()` calls `drawLines(lines)`: each line is an SVG `<polyline>` (created once per satellite id, then updated) whose `points` attribute is `toPixelX(e),toPixelY(n)` for each `[e, n]`. The map is a 400 by 400 box covering -1000 to +1000 metres, so one pixel is 5 metres and north is up (`toPixelY` flips the axis).
- `draw()` then places the dot at `toPixelX(local.east_m), toPixelY(local.north_m)` (hidden if it falls off the map), sets the colour class from `errorLevel(errorM)` (under 10 m "ok", under 100 m "warn", otherwise "bad", from `config.errorLimits`), and writes "Position off by" as metres (through `formatMetres` in [format.js](../../web/format.js): one decimal under 100 m, whole metres from 100 m up) plus the badge word ("Good fix", "Fix is off" or "Fix is far off").
- `showWords()` writes "The phone trusts its clock, so the distance lines miss each other." when the error is not "ok".

With the defaults, at 1 microsecond with the clock trusted the readout is 520 m ("Fix is far off"; the exact value is 520.3 m, which `formatMetres` rounds). That 520.3 m is the 3D distance from the dot to the true spot, and about 506 m of it is "up"; the dot on the map uses only east and north (`toPixelX`/`toPixelY` in `draw`), so it sits about 120 m from the centre. That is not 300 m: one microsecond adds about 300 m to each distance, but the position error depends on where the satellites are (design.md section 2b).

## Part 2: pressing "Let the phone solve for its clock"

The button is `<button id="solve">` with the label "Let the phone solve for its clock" in index.html.

1. The `click` handler in `setupControls()` sets `state.mode = "solved"` and calls `update("solve")`. The slider value is left alone, so `state.clockErrorS` is still the wrong clock you chose.
2. `runOnce("solve")` has `solveClock = true`. Before calling Python it checks `sats.length < 4` (with the clock trusted the limit is 3): if you switched satellites off, `refuse()` writes the sentence under the switches, for example "Can't solve: four things are unknown (east, north, up and the clock), but only 3 satellites are on, and each satellite gives one measurement. Turn a satellite back on." (the count is in words: "only 3 satellites are on" is written with the number from `countWords`; with none on it says "no satellites are on"). It writes "No position: see the message under the satellite switches." under the readout, clears the dot, metres value and badge with `showNoFix()`, and still draws the distance lines of the satellites that are on (two Python calls, `make_pseudoranges` and `distance_lines`). The solver is not called. The map caption then says how many lines have left the map.
3. Otherwise it runs the same four calls as above, with these differences:
   - `make_pseudoranges` is called with the same `state.clockErrorS`, so the measured distances are the same as before.
   - `solve_position` gets `true` for `solve_clock`. In `solver.py` each row of the table gets an extra `1.0` for the clock, so it solves four unknowns (x, y, z, clock). With fewer than 4 satellites it would return `{"error": "At least 4 satellites are needed."}`.
   - `assumedClockS = solveClock ? solution.clock_error_s : 0`, so `distance_lines` subtracts the solved clock error from every distance before drawing. That is why the lines meet again.
4. The button now reads "The phone is solving for its clock" (a state, not the next action), and on a mouse or touch press (not the keyboard, not reduced motion) `glide()` moves the lines and the dot from their old places to the new ones over 450 ms so you see the lines meet. `showWords()` calls `describeClock(solution.clock_error_s)`. With the defaults and the slider at 1 microsecond the solved result is a position error of 0 m and a clock error of 1.00 µs, so the page says "The phone found its clock is 1.00 µs fast. The lines meet again." (If the formatted value starts with `0.00` it says "The phone found its clock is right.")

Two other controls use the same path: a satellite switch calls `update("switch")`, and "Reset" calls `resetAll()` then `update("reset")`, which ends with "Back to the start: clock right, all four satellites on." So pressing Reset always gives a visible answer. `say()` ([say.js](../../web/say.js)) writes each message and flashes it briefly, so the same words twice still look like a reaction.

## The three-step guide

`guideStep` is 1, 2, 3 or 4. Only the hint for the current step shows, with a border on that step's control: step 1 "Step 1. Drag this slider to the right." (moves on when the fix is no longer "Good fix"), step 2 "Step 2. The lines no longer meet. Press this button." (moves on when you solve; goes back to step 1 if the lines meet again), step 3 "Step 3. Now switch one satellite off." (moves on when the page refuses to solve), then the closing line "That is the main idea: the phone needs four satellites because its own clock is a fourth unknown. Keep playing, or scroll on." Reset does not bring back a finished guide.

Not checked by eye: the 520.3 m (shown as 520 m) and 1.00 µs figures were confirmed by replaying the Python calls with the default config (and match .memory/decisions.md, 2026-11-24), not by seeing them on screen.
