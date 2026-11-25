# Reader test

## What the test is

A reader who had never seen the code answered 100 questions about specific lines of code. The reader could use only the docs in `docs/annotated/` and `docs/onboarding/`, not the code. Another agent then graded each answer against an answer key and a list of points the answer must mention. The keys were checked against the code, and where a key was wrong the code won. (No key needed changing.)

Grades: PASS (correct and covers every must-mention point), VAGUE (not wrong, but misses a point or is too general), WRONG, MISSING (the reader said "NOT IN DOCS").

## Results

| Round | PASS | VAGUE | WRONG | MISSING |
|---|---|---|---|---|
| 1 (100 questions) | 90 | 9 | 0 | 1 |
| 2 (10 re-asked, after doc fixes) | 7 | 3 | 0 | 0 |
| 3 (3 re-asked, docs unchanged, new reader) | 2 | 1 | 0 | 0 |

After round 3: 99 of 100 questions pass; only Q65 is still VAGUE.

Round 4 (Q65 only): the explanation of that line in say.js.md now says, in the line's own block, that the message still appears when the flash is skipped because the text was set on the line before. A fresh reader then answered with both required points (the browser-support check and that the text is already set): PASS. **Final: 100 of 100 questions pass.** Round 4 was graded by the main session against the same must-mention list.

## Doc gaps found and how they were fixed

Seven gaps were fixed in the docs between the rounds.

| Doc | Question | Gap | Fix |
|---|---|---|---|
| web/config.js.md | 46 | Did not say where `receiver` is used | Says first-screen.js buildScene passes it to coords.latlon_to_xyz |
| index.html.md | 97 | Said "the code scales positions" without naming the constant | Names MAP_SIZE (400) in first-screen.js |
| index.html.md | 98 | Did not say what enables the disabled slider | Says first-screen.js start() calls setControlsDisabled(false) after buildScene |
| mechanism/signal.py.md | 38 | Did not say ca_code is in the same file or that its error dict is passed back | Both added |
| web/say.js.md | 65 | Did not say the text is set before the animate check | Clause added |
| mechanism/solver.py.md | 32 | Line-39 block did not point to where the first guess is saved | Forward pointer added |
| mechanism/signal.py.md | 37 | Did not say the result is the list of 1023 chips | Added |

Three round-1 non-passes were reader misses, where the docs already said the point: 12, 63, 89. All three passed in round 2.

## What is still not perfect

- Q65 needed a fourth round: the point was in the doc, but one line earlier than readers looked, so it was repeated where the question points (fixed in round 4).
- Q37 and Q46 were VAGUE in round 2 but passed in round 3 with a new reader and unchanged docs (the points are in signal.py.md and config.js.md). So those two were reader omissions, not doc gaps.
- Grading is strict against the must-mention lists.
- The test covers 100 questions, not every line. The grader and the reader are both AI agents, and the keys come from the same people who wrote the docs.

## All 100 questions

| id | file | line | question | round 1 | round 2 | round 3 |
|---|---|---|---|---|---|---|
| 1 | mechanism/constants.py | 2 | "SPEED_OF_LIGHT_M_PER_S = 299_792_458". What is this line and what do the underscores and the l... | PASS |  |  |
| 2 | mechanism/constants.py | 5 | "EARTH_RADIUS_M = 6_371_008.7714". What does this number stand for, and which file needs it? | PASS |  |  |
| 3 | mechanism/constants.py | 7 | "GPS_ORBIT_RADIUS_M = 26_559_700.0". What is this distance measured from, and which function us... | PASS |  |  |
| 4 | mechanism/constants.py | 9 | "RELATIVITY_DRIFT_S_PER_DAY = 38e-6". What does 38e-6 mean, and how many metres of distance err... | PASS |  |  |
| 5 | mechanism/constants.py | 1 | "# Physical constants used by the mechanism. Units are in the names.". What practical habit doe... | PASS |  |  |
| 6 | mechanism/coords.py | 18 | "if not -90 <= lat_deg <= 90:". What does this check do and what happens when it fails? | PASS |  |  |
| 7 | mechanism/coords.py | 57 | "east = (-math.sin(lon), math.cos(lon), 0.0)". What does this line compute, and why is the last... | PASS |  |  |
| 8 | mechanism/coords.py | 67 | "if not 0 <= elevation_deg <= 90:". What does this check do and what is elevation here? | PASS |  |  |
| 9 | mechanism/coords.py | 82 | "t = -b + math.sqrt(b * b - c)". Maths: what equation is being solved here and why this root (p... | PASS |  |  |
| 10 | mechanism/coords.py | 69 | "receiver = latlon_to_xyz(receiver_lat_deg, receiver_lon_deg)". Which other function is called ... | PASS |  |  |
| 11 | mechanism/geometry.py | 20 | "start = read_point(receiver)". Which function is called here, what does it return for a bad re... | PASS |  |  |
| 12 | mechanism/geometry.py | 23 | "if not isinstance(satellites, (list, tuple)) or len(satellites) < 4:". Why must there be at le... | VAGUE | PASS |  |
| 13 | mechanism/geometry.py | 34 | "rows.append(list(arrow / distance) + [1.0])". What goes into this row, and what is the 1.0 for... | PASS |  |  |
| 14 | mechanism/geometry.py | 44 | "inverse = np.linalg.inv(table.T @ table)". What is computed here and what goes wrong for a fla... | PASS |  |  |
| 15 | mechanism/geometry.py | 53 | ""pdop": float(np.sqrt(diagonal[:3].sum())),". Maths: which diagonal entries make PDOP, and how... | PASS |  |  |
| 16 | mechanism/mapview.py | 43 | "directions = _local_directions(receiver_lat_deg, receiver_lon_deg)". Which function is called ... | PASS |  |  |
| 17 | mechanism/mapview.py | 56 | "return nearest <= radius <= farthest". What does this line decide and how are nearest and fart... | PASS |  |  |
| 18 | mechanism/mapview.py | 83 | "samples *= 2". When does this run and what is the point? | PASS |  |  |
| 19 | mechanism/mapview.py | 111 | "distance = pseudorange - assumed_clock_error_s * SPEED_OF_LIGHT_M_PER_S". What does this line ... | PASS |  |  |
| 20 | mechanism/mapview.py | 114 | "radius_squared = distance**2 - up_m**2". Maths: what is this and why does it give a circle on ... | PASS |  |  |
| 21 | mechanism/relativity.py | 12 | "return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value... | PASS |  |  |
| 22 | mechanism/relativity.py | 60 | "drift_s = RELATIVITY_DRIFT_S_PER_DAY * hours / 24". Maths: what is drift_s for 12 hours, and w... | PASS |  |  |
| 23 | mechanism/relativity.py | 62 | "ranges = make_pseudoranges(receiver, satellites, phone_clock_error_s + drift_s)". Which functi... | PASS |  |  |
| 24 | mechanism/relativity.py | 63 | "if isinstance(ranges, dict):". Why is this check here and what happens next? | PASS |  |  |
| 25 | mechanism/relativity.py | 69 | "trusted = solve_position(satellites, ranges, solve_clock=False)". How does this differ from th... | PASS |  |  |
| 26 | mechanism/scenario.py | 15 | "if not satellites:". What does this do and what does the caller get? | PASS |  |  |
| 27 | mechanism/scenario.py | 20 | "clock_effect_m = clock_error_s * SPEED_OF_LIGHT_M_PER_S". Maths: what is clock_effect_m for a ... | PASS |  |  |
| 28 | mechanism/scenario.py | 22 | "rng = np.random.default_rng(seed)". What is a seed here and what would change without one? | PASS |  |  |
| 29 | mechanism/scenario.py | 23 | "noise = rng.normal(0.0, noise_m, len(satellites))". What numbers does this produce and what is... | PASS |  |  |
| 30 | mechanism/scenario.py | 32 | "pseudoranges.append(float(true_distance + clock_effect_m + noise_value))". What is added toget... | PASS |  |  |
| 31 | mechanism/solver.py | 34 | "needed = 4 if solve_clock else 3". Why 4 or 3? | PASS |  |  |
| 32 | mechanism/solver.py | 39 | "x, y, z = 0.0, 0.0, 0.0". What is this and what is saved right after it? | VAGUE | PASS |  |
| 33 | mechanism/solver.py | 65 | "row = [dx / distance, dy / distance, dz / distance]". Maths: what do these three numbers mean ... | PASS |  |  |
| 34 | mechanism/solver.py | 72 | "correction, _, rank, _ = np.linalg.lstsq(changes, errors, rcond=None)". What does it do, what ... | PASS |  |  |
| 35 | mechanism/solver.py | 87 | "if np.linalg.norm(correction) < STOP_WHEN_CHANGE_IS_SMALLER_THAN:". What does this test and wh... | PASS |  |  |
| 36 | mechanism/signal.py | 45 | "g2_out = g2[tap_a - 1] ^ g2[tap_b - 1]". What does this line do and why the - 1? | PASS |  |  |
| 37 | mechanism/signal.py | 63 | "return [1 - 2 * b for b in _logic_bits(prn)]". Maths: what does 1 - 2 * b do to a logic bit? | VAGUE | VAGUE | PASS |
| 38 | mechanism/signal.py | 68 | "code = ca_code(prn)". Which function is called and what does the next line do with the result? | VAGUE | PASS |  |
| 39 | mechanism/signal.py | 104 | "scores.append(float(np.dot(values, np.roll(code_array, shift)) / CODE_LENGTH))". Maths: what i... | PASS |  |  |
| 40 | mechanism/signal.py | 113 | "peak_to_next = 1e9". When is this used and why a number instead of infinity? | PASS |  |  |
| 41 | web/bridge.js | 54 | "const sources = Promise.all(MECHANISM_FILES.map(fetchText));". What does this do and why is it... | PASS |  |  |
| 42 | web/bridge.js | 55 | "sources.catch(() => {}); // the failure is reported where the result is awaited below". What d... | PASS |  |  |
| 43 | web/bridge.js | 79 | "return json.dumps(function(*json.loads(args_json)))". What happens in this Python line inside ... | PASS |  |  |
| 44 | web/bridge.js | 94 | "bridgeCall.destroy();". Why is this in a finally block? | PASS |  |  |
| 45 | web/bridge.js | 28 | "loading = null; // a failed load is not remembered: the next call tries again". What does this... | PASS |  |  |
| 46 | web/config.js | 5 | "export const receiver = { lat_deg: -6.2, lon_deg: 106.8 }; // placeholder, provisional". What ... | VAGUE | VAGUE | PASS |
| 47 | web/config.js | 18 | "export const lineSamples = 40; // points per distance line, placeholder". Where is this number... | PASS |  |  |
| 48 | web/config.js | 21 | "export const clockSlider = { min_s: 0, max_s: 3e-6, step_s: 5e-8 }; // placeholder, provisiona... | PASS |  |  |
| 49 | web/config.js | 24 | "export const errorLimits = { ok_m: 10, warn_m: 100 }; // placeholder, provisional". What do th... | PASS |  |  |
| 50 | web/config.js | 30 | "export const relativityPhoneClockErrorS = 0; // placeholder, provisional: the phone's own cloc... | PASS |  |  |
| 51 | web/first-screen.js | 151 | "if (running) { rerun = true; return; }". What does this do and why is it there? | PASS |  |  |
| 52 | web/first-screen.js | 185 | "const solution = await callPython("solver.solve_position", [sats, ranges, solveClock]);". Whic... | PASS |  |  |
| 53 | web/first-screen.js | 195 | "const errorM = Math.hypot(local.east_m, local.north_m, local.up_m);". What is calculated and w... | PASS |  |  |
| 54 | web/first-screen.js | 277 | "function toPixelX(east_m) { return (east_m + config.mapHalfWidthM) * MAP_SIZE / (2 * config.ma... | PASS |  |  |
| 55 | web/first-screen.js | 417 | "void node.offsetWidth;". Why read a value and throw it away? | PASS |  |  |
| 56 | web/format.js | 4 | "const digits = new Intl.NumberFormat("en", { maximumFractionDigits: m < 100 ? 1 : 0 }).format(... | PASS |  |  |
| 57 | web/format.js | 4 | "const digits = new Intl.NumberFormat("en", { maximumFractionDigits: m < 100 ? 1 : 0 }).format(... | PASS |  |  |
| 58 | web/format.js | 3 | "export function formatMetres(m) {". What does export allow, and which files use this function? | PASS |  |  |
| 59 | web/format.js | 5 | "return `${digits} m`;". What is special about the space before the m? | PASS |  |  |
| 60 | web/format.js | 2 | "// always with a thousands separator. The space before "m" cannot break across lines.". Which ... | PASS |  |  |
| 61 | web/say.js | 3 | "export function say(node, text) {". What is the function for and who calls it? | PASS |  |  |
| 62 | web/say.js | 4 | "node.textContent = text;". What does it do and how is it different from innerHTML? | PASS |  |  |
| 63 | web/say.js | 5 | "if (text && node.animate) node.animate([{ opacity: 0.3 }, { opacity: 1 }], { duration: 160, ea... | VAGUE | PASS |  |
| 64 | web/say.js | 5 | "if (text && node.animate) node.animate([{ opacity: 0.3 }, { opacity: 1 }], { duration: 160, ea... | PASS |  |  |
| 65 | web/say.js | 5 | "if (text && node.animate) node.animate([{ opacity: 0.3 }, { opacity: 1 }], { duration: 160, ea... | VAGUE | VAGUE | VAGUE, round 4 PASS |
| 66 | web/startup.js | 46 | "const bridge = await import("./bridge.js");". Why is bridge.js imported here and not at the to... | PASS |  |  |
| 67 | web/startup.js | 18 | "started = true;". What is this part of and what does it achieve? | PASS |  |  |
| 68 | web/startup.js | 53 | "if (state !== "loading") return;". What does this do and what would go wrong without it? | PASS |  |  |
| 69 | web/startup.js | 77 | "button.addEventListener("click", () => attempt()); // restarts the load for every section". Wh... | PASS |  |  |
| 70 | web/startup.js | 67 | "section.onReady(callPython);". What is callPython here and where does it come from? | PASS |  |  |
| 71 | web/theme.js | 6 | "const card = event.target.closest?.(".card");". What does this line find and what happens on t... | PASS |  |  |
| 72 | web/theme.js | 9 | "card.style.setProperty("--px", `${event.clientX - box.left}px`);". What is stored and which fi... | PASS |  |  |
| 73 | web/theme.js | 15 | "document.documentElement.dataset.theme = name;". What does it set and which CSS rule responds? | PASS |  |  |
| 74 | web/theme.js | 16 | "try { localStorage.setItem("theme", name); } catch (_) { /* storage can be blocked; the switch... | PASS |  |  |
| 75 | web/theme.js | 22 | "setTheme(saved === "light" ? "light" : "dark");". What are the possible outcomes? | PASS |  |  |
| 76 | web/step-geometry.js | 209 | "const away = (90 - sat.elevation_deg) / 90 * SKY_RADIUS;". Maths: what is `away` for elevation... | PASS |  |  |
| 77 | web/step-geometry.js | 212 | "group.setAttribute("transform", `translate(${mid + away * Math.sin(angle)} ${mid - away * Math... | PASS |  |  |
| 78 | web/step-geometry.js | 236 | "const sky = currentSky(); // the layout this run is about, even if the slider moves meanwhile"... | PASS |  |  |
| 79 | web/step-geometry.js | 244 | "const dop = await callPython("geometry.dop", [receiverPoint, sats]);". Which Python function i... | PASS |  |  |
| 80 | web/step-geometry.js | 250 | "const solution = await callPython("solver.solve_position", [sats, ranges, true]);". Why is the... | PASS |  |  |
| 81 | web/step-relativity.js | 80 | "if (!document.getElementById("rel-style")) {". What is this guard for? | PASS |  |  |
| 82 | web/step-relativity.js | 169 | "const hours = Number(el.slider.value); // the slider may move while Python works". Why is the ... | PASS |  |  |
| 83 | web/step-relativity.js | 171 | "const result = await callPython("relativity.drift_over_time",". Which file/function is called ... | PASS |  |  |
| 84 | web/step-relativity.js | 182 | "el.range.textContent = formatMetres(row.range_added_m);". Maths: what text is shown at 24 hour... | PASS |  |  |
| 85 | web/step-relativity.js | 188 | "if (el.sentence.textContent !== sentence) say(el.sentence, sentence); // only when the words c... | PASS |  |  |
| 86 | web/step-signal.js | 95 | "el.slider.max = Math.round((max - min) / step);". Maths: what is the slider's max, and what no... | PASS |  |  |
| 87 | web/step-signal.js | 153 | "const received = await callPython("signal.make_received", [prn, trueDelayChips, usedNoise, see... | PASS |  |  |
| 88 | web/step-signal.js | 170 | "if (result.best_delay_chips !== signalConfig.trueDelayChips) return "bad";". What does it deci... | PASS |  |  |
| 89 | web/step-signal.js | 204 | "el.clipNote.textContent = usedNoise * 2 > receivedLimit". Maths: with receivedLimit 4, at what... | VAGUE | PASS |  |
| 90 | web/step-signal.js | 216 | "const y = PLOT_HEIGHT - ((clamped - low) / (high - low)) * PLOT_HEIGHT;". What does this line ... | PASS |  |  |
| 91 | web/theme.css | 43 | "--r-inner: max(4px, calc(var(--r-card) - var(--pad-card) / 2));". Maths: what value does this ... | PASS |  |  |
| 92 | web/theme.css | 109 | "background: radial-gradient(360px circle at var(--px) var(--py), rgba(255, 255, 255, 0.06), tr... | PASS |  |  |
| 93 | web/theme.css | 161 | ".toggle input { position: absolute; opacity: 0; width: 1px; height: 1px; }". Why is the checkb... | PASS |  |  |
| 94 | web/theme.css | 196 | "* { transition-property: opacity, color, background-color, border-color !important; }". When d... | PASS |  |  |
| 95 | web/theme.css | 58 | "[data-theme="light"] {". What triggers this block and what does it do? | PASS |  |  |
| 96 | index.html | 10 | "<link rel="modulepreload" href="https://cdn.jsdelivr.net/pyodide/v314.0.8/full/pyodide.mjs" cr... | PASS |  |  |
| 97 | index.html | 87 | "<svg class="map" id="map" viewBox="0 0 400 400" role="img" aria-label="Ground map. Each satell... | VAGUE | PASS |  |
| 98 | index.html | 110 | "<input id="clock" type="range" value="0" disabled>". Why disabled and what enables it? | MISSING | PASS |  |
| 99 | index.html | 152 | "<script type="module" src="web/first-screen.js"></script>". What does it start and what does t... | PASS |  |  |
| 100 | index.html | 157 | "mountGeometryStep(document.getElementById("step-geometry"));". What does it do and where is th... | PASS |  |  |

## Round for the redesigned page (25 Nov 2026, plan 005)

After the UI redesign, the docs for index.html, theme.css, config.js, format.js, first-screen.js, illustrations.js (new), step-signal.js, step-relativity.js and step-geometry.js were rewritten. One agent wrote 20 new questions (R1 to R20) about changed lines, with an answer key and must-mention points built from the source code. A fresh reader answered them using only `docs/annotated/` and `docs/onboarding/`, without seeing the code or the key. The main session graded the answers.

| PASS | VAGUE | WRONG | MISSING |
|---|---|---|---|
| 20 | 0 | 0 | 0 |

Spread: step-signal.js 5, step-relativity.js 4, index.html 3, first-screen.js 2, illustrations.js 2, and one each for step-geometry.js, theme.css, config.js and format.js. The trap question (R3: the signal clip note first shows at noise 1.5, not 1.0, because the slider moves in 0.5 steps) was answered correctly from the documented rule. No doc needed changing.
