# Code tour

Files in reading order: Python first (`mechanism/`), then the bridge, then the page. For each file: its job, 3 to 6 key lines (quoted exactly), what they mean, and the question a judge is most likely to ask, with a short answer. Answers use only what the code and [../facts.md](../facts.md) say. For a slower, line-by-line read of any file, see [../annotated/how-to-read-code.md](../annotated/how-to-read-code.md) (Python files: `../annotated/mechanism/<name>.py.md`; page files: `../annotated/web/<name>.js.md`, [index.html.md](../annotated/index.html.md), [theme.css.md](../annotated/web/theme.css.md)).

## 1. [mechanism/constants.py](../../mechanism/constants.py)

Four numbers, each with its unit in the name.

```python
SPEED_OF_LIGHT_M_PER_S = 299_792_458
EARTH_RADIUS_M = 6_371_008.7714
GPS_ORBIT_RADIUS_M = 26_559_700.0
RELATIVITY_DRIFT_S_PER_DAY = 38e-6
```

The speed of light turns time into distance. The Earth is one sphere with this mean radius. The orbit radius is measured from the Earth's centre, so the satellites are about 20,200 km up (20,189 km above our sphere model; facts.md row 35). The drift is "about 38" microseconds a day. They would gain about 38 µs a day if uncorrected; real satellites are set slow before launch to cancel it (docs/facts.md rows 28-29). Our slider shows the uncorrected case.

**Judge asks:** where do these numbers come from? **Answer:** each has a source row in facts.md (rows 1, 33, 3, 27). The relativity figure is "about 38", not exact: 45 minus 7 rounded (facts.md notes).

## 2. [mechanism/coords.py](../../mechanism/coords.py)

Turns latitude and longitude into x,y,z points, and a sky direction into a satellite position.

```python
radius = EARTH_RADIUS_M + height_m
x_m = radius * math.cos(lat) * math.cos(lon)
y_m = radius * math.cos(lat) * math.sin(lon)
z_m = radius * math.sin(lat)
```

This is `latlon_to_xyz`: the radius times the direction of the spot. In `satellite_from_sky` the lines that matter are:

```python
b = sum(s * d for s, d in zip(start, direction))
c = sum(s * s for s in start) - GPS_ORBIT_RADIUS_M**2
t = -b + math.sqrt(b * b - c)
```

Start at the receiver, walk `t` metres along the sky direction, and stop where you reach the orbit sphere. That is a quadratic in `t`; the code takes the positive root.

**Judge asks:** why a sphere and not the real Earth shape? **Answer:** the conversions stay a few lines, and the simulated truth and the solver use the same model, so the solver recovers the simulated position to far below a millimetre. This is agreement with our own sphere model, not real-world accuracy; .memory/decisions.md (2026-11-23) says the page must call this a simplification; README.md ("What is simplified") says so; the page itself does not yet.

## 3. [mechanism/scenario.py](../../mechanism/scenario.py)

`make_pseudoranges` makes what the phone would measure.

```python
clock_effect_m = clock_error_s * SPEED_OF_LIGHT_M_PER_S
rng = np.random.default_rng(seed)
noise = rng.normal(0.0, noise_m, len(satellites))
...
pseudoranges.append(float(true_distance + clock_effect_m + noise_value))
```

Measured distance is the true straight-line distance plus the clock effect plus random noise. The same `seed` always gives the same noise, so a run can be repeated.

**Judge asks:** is the noise real? **Answer:** no, it is random numbers from our code (`numpy.random.default_rng`), not a recording of a receiver.

## 4. [mechanism/solver.py](../../mechanism/solver.py)

`solve_position` is the heart of the project.

```python
needed = 4 if solve_clock else 3
...
x, y, z = 0.0, 0.0, 0.0
clock_m = 0.0  # Store clock error as extra distance for easier maths.
...
correction, _, rank, _ = np.linalg.lstsq(changes, errors, rcond=None)
```

Each loop: for every satellite, compare what we would measure from the current guess (`distance + clock_m`) with what was measured (`errors` is measured distance minus predicted); build a row of how the distance changes with x, y, z (`dx / distance` and so on), plus a `1.0` for the clock when `solve_clock` is true; ask `lstsq` for the small move that best reduces all errors; apply it. Stop when the length of the whole correction (position plus the clock term, in metres) is under 1 mm (`STOP_WHEN_CHANGE_IS_SMALLER_THAN`), or when 20 guesses are saved (`MAX_STEPS`, counting the start, so at most 19 corrections: the loop is `range(MAX_STEPS - 1)`). Every guess is saved in `steps`.

**Judge asks:** why do you need four satellites? **Answer:** there are four unknowns: x, y, z (Earth-centred) and the clock. "East, north, up" is the page's wording for the same idea. With `solve_clock=True` the code returns `{"error": "At least 4 satellites are needed."}` for fewer. With three satellites and the clock trusted it solves three unknowns.

## 5. [mechanism/mapview.py](../../mechanism/mapview.py)

Turns 3D results into the 2D ground map. Two public functions: `to_local` and `distance_lines`.

```python
radius_squared = distance**2 - up_m**2
points = []
if radius_squared > 0:
    points = _circle_points(east_m, north_m, math.sqrt(radius_squared), half_width_m, samples)
```

A distance sphere cuts the flat ground in a circle centred right under the satellite. Pythagoras gives its radius from the distance and the satellite's height. `distance` itself is:

```python
distance = pseudorange - assumed_clock_error_s * SPEED_OF_LIGHT_M_PER_S
```

so the "assumed clock" changes how the lines are drawn. `_circle_points` samples only the part of the huge circle near the 2 km square.

**Judge asks:** why do the lines look straight? **Answer:** the circles have radii of about 10,000 to 22,000 km for the default satellites (computed: 10,425 / 18,339 / 22,268 / 22,268 km) and the map is 2 km wide, so only a tiny arc shows (design.md section 2b: "The lines look almost straight at this zoom").

## 6. [mechanism/geometry.py](../../mechanism/geometry.py)

`dop` measures how the satellite layout multiplies errors.

```python
rows.append(list(arrow / distance) + [1.0])
...
inverse = np.linalg.inv(table.T @ table)
diagonal = np.diag(inverse)
```

`make_table` builds one row per satellite: the unit direction from receiver to satellite plus a 1 for the clock. Then the code inverts the table's transpose times itself. The result:

```python
"pdop": float(np.sqrt(diagonal[:3].sum())),
"tdop": float(np.sqrt(diagonal[3])),
```

PDOP uses the three position entries, TDOP the clock entry, GDOP all four.

**Judge asks:** why does bunching make it worse? **Answer:** when satellites are in nearly the same direction the rows of the table are nearly the same, so the table is nearly unsolvable and the inverse is huge. gotchas.md says four satellites within 10 degrees give a DOP of about 350.

## 7. [mechanism/signal.py](../../mechanism/signal.py)

Makes the GPS C/A code, a noisy delayed copy, and finds the delay.

```python
g1_out = g1[9]
g2_out = g2[tap_a - 1] ^ g2[tap_b - 1]
bits.append(g1_out ^ g2_out)
```

`_logic_bits` runs two 10-stage shift registers for 1023 steps. The chip is the G1 output XOR the G2 output (two stages chosen by `G2_TAPS` for each PRN). `ca_code` maps logic 0 to +1 and logic 1 to -1. In `make_received`:

```python
shifted = np.roll(np.array(code, dtype=float), delay_chips)
noise = np.random.default_rng(seed).normal(0.0, noise_std, CODE_LENGTH)
```

and in `correlate`:

```python
scores.append(float(np.dot(values, np.roll(code_array, shift)) / CODE_LENGTH))
```

Try all 1023 shifts, multiply chip by chip, average. A perfect clean match scores 1.0. `best_delay_chips` is the shift with the top score.

**Judge asks:** how can it find a signal buried in noise? **Answer:** `correlate` scores every one of the 1023 shifts and takes the best, and a clean match scores 1.0. Each score averages 1023 products, so the noise in a score is about noise divided by the square root of 1023 (about noise/32), while the true peak stays near 1. With the page's settings (PRN 7, delay 14, seed 1, noise slider in steps of 0.5) it is "Found" up to 7.0 times the signal, "Barely found" from 7.5 to 11.5 times, and "Lost" at 12.0 times, the slider's last notch (best shift 713, not 14), for this one seed (a replay of `make_received` and `correlate`).

## 8. [mechanism/relativity.py](../../mechanism/relativity.py)

`drift_over_time` adds the shared drift and solves twice.

```python
drift_s = RELATIVITY_DRIFT_S_PER_DAY * hours / 24
ranges = make_pseudoranges(receiver, satellites, phone_clock_error_s + drift_s)
solved = solve_position(satellites, ranges, solve_clock=True)
trusted = solve_position(satellites, ranges, solve_clock=False)
```

The drift looks exactly like a phone clock error, because every satellite has the same one: every distance changes by the same amount (a satellite clock running ahead makes each distance read shorter; our model adds it as longer, which flips the sign of the solved clock but not the position result). `range_added_m` is `drift_s * SPEED_OF_LIGHT_M_PER_S`.

**Judge asks:** so is GPS 11 km off per day without the correction? **Answer:** the shared drift adds about 11 km of range a day, but the position stays put when the clock is solved, because the clock solve absorbs it (decisions.md 2026-11-23; gotchas.md says never claim 11 km position error). With the clock trusted, the error does grow.

## 9. [web/bridge.js](../../web/bridge.js)

```js
const PYODIDE_BASE = 'https://cdn.jsdelivr.net/pyodide/v314.0.8/full/';
...
pyodide = await loadPyodide({ indexURL: PYODIDE_BASE, packages: ['numpy'] });
...
pyodide.FS.writeFile(MECHANISM_DIR + '/' + name, texts[i])
...
return json.dumps(function(*json.loads(args_json)))
...
return JSON.parse(bridgeCall(target, JSON.stringify(args)));
```

It loads a pinned Pyodide together with numpy, fetches each file in `MECHANISM_FILES` (in parallel with the Pyodide download) and writes it into Pyodide's file system, then `callPython` sends arguments as JSON and reads JSON back. While it loads it reports "Step 1 of 2: downloading Python and numpy. This is the slow step on a first visit…" and "Step 2 of 2: loading our GPS code…". A failed load is not remembered, so a retry works. Annotated: [bridge.js.md](../annotated/web/bridge.js.md).

**Judge asks:** how does JavaScript call your Python? **Answer:** JSON text both ways, through one helper `_bridge_call` that imports `mechanism.<module>` and calls the function by name. That is why only plain numbers, lists and dicts can cross.

### 9b. [web/startup.js](../../web/startup.js), [web/say.js](../../web/say.js), [web/format.js](../../web/format.js)

Three small helpers.

```js
export function whenPythonReady(statusNode, onReady, { hasControls = true } = {}) {
export function say(node, text) {
export function formatMetres(m) {
export function formatRoughDistance(m) {
export function formatClockDigits(hours, gapMicroseconds) {
```

`whenPythonReady` is the one start-up path: the first caller starts the load, every section shows the same progress words and, if the download fails, the same sentence ("Python could not be downloaded, so nothing here can calculate yet. Check your internet connection, then press Try again.") and one "Try again" button. `say` writes a message and flashes it for 160 ms, so pressing something always gives a visible answer even when the words repeat. `formatMetres` is the one metres format: one decimal under 100 m, whole metres from 100 m up, so 520.3 m shows as "520 m". `formatRoughDistance` writes the "about" distances of rung 4 ("11 km"), and `formatClockDigits` writes its clock digits.

**Judge asks:** what if the download fails? **Answer:** the page says so in words and offers "Try again"; nothing pretends to calculate. Annotated: [startup.js.md](../annotated/web/startup.js.md), [say.js.md](../annotated/web/say.js.md), [format.js.md](../annotated/web/format.js.md).

## 10. [web/config.js](../../web/config.js)

All first-screen (and rung 4) placeholder numbers live here (a design.md rule: placeholder numbers live in one config file, never inline). The step files keep their own `geometryConfig` and `signalConfig`.

```js
export const receiver = { lat_deg: -6.2, lon_deg: 106.8 };
{ id: "1", azimuth_deg: 10, elevation_deg: 60 },
export const mapHalfWidthM = 1000;
export const clockSlider = { min_s: 0, max_s: 3e-6, step_s: 5e-8 };
export const errorLimits = { ok_m: 10, warn_m: 100 };
export const relativitySlider = { min_h: 0, max_h: 24, step_h: 1, start_h: 24 };
export const relativityMapHalfWidthM = 20000;
export const relativityPhoneClockErrorS = 0;
```

**Judge asks:** why these satellites? **Answer:** azimuths 10/100/235/325 and elevations 60/35/20/20 were picked so no two distance lines are parallel and PDOP stays under 4 (PDOP 3.37; decisions.md, 2026-11-24, issue #43).

## 11. [web/first-screen.js](../../web/first-screen.js)

Walked through in [follow-one-click.md](follow-one-click.md). It also runs the three-step guide (hints "Step 1. This only works if the phone's clock is right. Drag the slider to make it wrong.", "Step 2. The lines no longer meet. Press this button.", "Step 3. Now switch one satellite off.", then a closing line), refuses in words when too few satellites are on, and glides the lines together when you press the solve button. It also hides the "The first visit can take up to a minute on a phone." line once Python is ready, and on phones it saves the sticky map card's height (`keepStickyHeight`) so a focused control is never scrolled in under the card. Annotated: [first-screen.js.md](../annotated/web/first-screen.js.md). Key lines:

```js
if (running) { rerun = true; return; }
const ranges = await callPython("scenario.make_pseudoranges", [receiverPoint, sats, state.clockErrorS]);
const solution = await callPython("solver.solve_position", [sats, ranges, solveClock]);
const errorM = Math.hypot(local.east_m, local.north_m, local.up_m);
```

**Judge asks:** does the JavaScript do any GPS maths? **Answer:** no. Python does it all. The page does `Math.hypot` for the error and the metres-to-pixels scaling (comment at the top of the file).

## 12. [web/step-geometry.js](../../web/step-geometry.js)

Rung 2. The "Bunch the satellites" slider blends between two sets of satellite angles in `geometryConfig` (`spread` and `bunched`), then asks Python for `geometry.dop` and the solved position error.

```js
const dop = await callPython("geometry.dop", [receiverPoint, sats]);
const ranges = await callPython("scenario.make_pseudoranges", [receiverPoint, sats, geometryConfig.clock_error_s, geometryConfig.noise_m, geometryConfig.seed]);
const solution = await callPython("solver.solve_position", [sats, ranges, true]);
```

The clock is solved, with fixed noise (`noise_m: 3`) and a fixed seed, so only the layout changes. What remains is the noise multiplied by the layout, which is what DOP describes.

**Judge asks:** what does the DOP number mean? **Answer:** how much the satellites' layout multiplies measurement errors; lower is better (the page's own text).

## 13. [web/step-signal.js](../../web/step-signal.js)

Rung 3 (Part 3 of 4). The reader does the phone's job by hand first. Three rows of 40 steps are drawn as square waves: what the satellite sends, what the phone hears (a little later, with noise) and the phone's own copy. You slide the copy with the range input "Slide the phone's copy" or by dragging the row (the real delay is 14 chips). The "Match score" is looked up from Python's scores, not calculated again: `result.scores[shift]`. Then "Let the phone try every shift" draws two score charts (the first 40 shifts, and all 1023), which stay 60 px tall until you press it. The "Add noise" slider calls `signal.make_received` then `signal.correlate`.

```js
const heard = await callPython("signal.make_received", [prn, trueDelayChips, usedNoise, seed]);
const scored = await callPython("signal.correlate", [heard, prn]);
const score = result.scores[shift];
const lit = (value > 0) === (received[index] > 0);
if (scored.best_delay_chips !== signalConfig.trueDelayChips) return "bad";
```

The first two lines are in `runOnce`, which then keeps `heard` as `received` and `scored` as `result`. The `lit` line is in `drawCopyRow`: a step of the copy is lit when it is on the same side of zero as the heard value above it, and dim when it is not. This is a sign check on two numbers Python returned, and it only picks a shade; no number on the screen comes from it. The last line is in `levelOf`. The label words are "Found", "Barely found" and "Lost". The true delay is `trueDelayChips: 14` for `prn: 7`.

**Judge asks:** is the "Lost" verdict computed? **Answer:** yes: it is "Lost" only when Python's best shift differs from the true delay. `peak_to_next` under `barelyHoldingBelow` (1.5) only gives "Barely found". **Judge asks:** is the match score the page's own maths? **Answer:** no, it is the score Python's `correlate` gave for that shift. Only the lit and dim shading is chosen in JavaScript.

## 14. [web/step-relativity.js](../../web/step-relativity.js)

Rung 4 (Part 4 of 4). One slider, "Time since the satellite clocks were last corrected" (0 to 24 h, starting at 24, `config.relativitySlider`), drives two cards. On every change it calls `relativity.drift_over_time` with a one-element hours list and `config.relativityPhoneClockErrorS`, which is 0, so at 0 h both ways of solving agree.

```js
const result = await callPython("relativity.drift_over_time",
  [receiver, satellites, config.relativityPhoneClockErrorS, [hours]]);
const trusted = await fix(ranges, false);
const solved = trusted.error ? trusted : await fix(ranges, true);
```

The first card, "Satellite clocks run fast.", shows two clocks as digits ("Clock on the ground", "Clock on the satellite"; digits that differ are bright), "Satellite clock ahead by" (`solved_clock_error_s` in whole microseconds) and "So every measured distance is wrong by" (`range_added_m`). The second card, "So why doesn't your position drift?", draws the first screen's map twice, each 40 km wide (`relativityMapHalfWidthM`): "The phone trusts its clock" and "The phone solves for its clock". Each map comes from the same chain of calls the first screen uses (`make_pseudoranges`, `solve_position`, `to_local`, `distance_lines`). `drift_over_time` is called by the page but is not yet in interface.md. At 24 h with the default satellites the readouts are "about 38 µs", "about 11 km" (11,392 m), "about 20 km off" (19,767 m, with a grey line that most of it is height) and "0 m off" (computed by running `relativity.drift_over_time`). The range figure follows our model, which adds the drift as longer distances; a real satellite clock running ahead would make them shorter by the same amount (see section 8). The clock-solved result (0 m) is the same either way; the trusted figure differs slightly (19,779 m with the sign flipped, computed). The fixed lines "45 µs a day", "7 µs a day" and "about 38 µs a day" are text from facts.md rows 25 to 27; the slider does not scale them. Annotated: [step-relativity.js.md](../annotated/web/step-relativity.js.md).

**Judge asks:** why does the position not move? **Answer:** the page says it ("Every satellite is off by the same amount. To the phone that looks exactly like its own clock being wrong, and the fourth satellite already fixes that."): the drift is the same for every satellite, so it looks like the phone's own clock error and solving for the clock absorbs it.

## 15. [web/theme.js](../../web/theme.js) and [web/theme.css](../../web/theme.css)

`theme.js` exports `trackPointerLight`, `setTheme` and `loadSavedTheme`; `loadSavedTheme` falls back to `"dark"`. `theme.css` holds colours, fonts and spacing. Rules for them are in [../ui-guide.md](../ui-guide.md). Judge question: not likely to be asked; the maths is what judges probe.

## 16. [index.html](../../index.html)

Opens with "Part 1 of 4", the heading, a small drawing (`firstScreenFigure()` from `web/illustrations.js`) and a "What you're looking at" line above the map, then holds the first-screen elements by `id` (`clock`, `solve`, `error-value`, `map-lines`, `map-dot`, `switches`, the map key, and the `load-note` line "The first visit can take up to a minute on a phone.") and three empty `div`s (`step-geometry`, `step-signal`, `step-relativity`) that the step modules fill with `mount...Step`. Between the sections are the "but / therefore" link lines. On phones the map card is `position: sticky`, so the map and the number stay on screen while you use the controls below. Annotated: [index.html.md](../annotated/index.html.md).

**Judge asks:** where does the page get its numbers? **Answer:** from Python through the bridge; the HTML only has places to put them.
