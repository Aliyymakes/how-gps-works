# Interview prep: questions a judge may ask

**Draft for Icarus.** Not reviewed. Round 2 is a recorded team interview (design.md 5a): all four on camera, one take, up to 10 minutes of answers. Judges' questions are written from our submission and source code, so every teammate must be able to answer every section in their own words.

How to use this file:
- Answers marked "to be filled in" wait for that code to merge. The owner explains it in their own words. Nobody should invent how it works.
- Answers from code are taken from open pull requests (branches `7-geometry-dop`, `8-signal-code`, `5-first-screen`, `9-step-geometry`, `10-step-signal`). Check them again after merge.
- Numbers here are only ones that appear in the code or in design.md. Any number we show on the page must be checked against a source (design.md 2a).

---

## 1. The solver loop (solver.py)

Owner explains each answer. The code is not merged yet.

**1.1 What does `solve_position` do, in one minute?**
Answer: to be filled in after solver.py merges (owner explains in their own words).
(Contract: it takes the satellites and the measured distances and returns x, y, z, the clock error, the list of guesses (`steps`) and whether it `converged`. Source: docs/interface.md.)

**1.2 Why does the solver start from the centre of the Earth, and why does it need several steps?**
Answer: to be filled in after solver.py merges (owner explains in their own words).
(Contract: the first guess in `steps` is the centre of the Earth. Source: docs/interface.md.)

**1.3 What does `converged` mean, and what does the page do if it is false?**
Answer: to be filled in after solver.py merges (owner explains in their own words).

**1.4 What does the solver do differently with `solve_clock=False`?**
Answer: to be filled in after solver.py merges (owner explains in their own words).
(Contract: it trusts the phone's clock, keeps the clock error at 0 and needs at least 3 satellites. With `True` it needs at least 4. Source: docs/interface.md.)

**1.5 Trap: Why do you need 4 satellites, not 3?**
Conceptual part from the spec: there are four unknowns (east, north, up and the clock error), so at least four measurements are needed. The first screen refuses in one sentence when there are 3 satellites and the clock is solved (design.md 2b).
Answer for how the solver code handles this case: to be filled in after solver.py merges (owner explains in their own words).

**1.6 Trap: With 4 satellites and the clock trusted, why do the distance lines visibly miss each other?**
Conceptual part from the spec: there are more measurements than unknowns, so with a wrong clock they cannot all agree. With only 3 satellites the three spheres would still meet at one point, just the wrong one, so the picture could not show the problem (design.md 2b).
Answer for what the solver then returns: to be filled in after solver.py merges (owner explains in their own words).

**1.7 Where does the measured distance come from in the demo, and is it real data?**
Conceptual part from the spec: `make_pseudoranges` builds each distance as true distance, plus the clock error effect, plus random noise (docs/interface.md). It is computed from the user's inputs, not prepared (design.md 1, point 5). The page says the satellites are simulated.
Answer for the code details: to be filled in after scenario.py merges (owner explains in their own words).

---

## 2. The bridge (bridge.js, Pyodide)

**2.1 What is Pyodide, and what does the bridge do?**
Answer: to be filled in after bridge.js merges (owner explains in their own words).
(Contract: `loadMechanism(onStatus)` loads Pyodide, numpy and the mechanism files and reports progress. `callPython("module.function", [args])` calls `mechanism.<module>.<function>` and returns a plain JavaScript value. Source: docs/interface.md.)

**2.2 What is allowed to cross between Python and JavaScript, and why?**
Only plain numbers, strings, booleans, lists and dicts. No numpy arrays and no custom classes. The reason recorded is that this is simple to convert in Pyodide and simple to explain (docs/interface.md, decisions.md 2026-11-22).

**2.3 Does the page do any GPS maths?**
No. The page calls Python and draws what comes back (docs/interface.md). The only arithmetic in the page files is turning metres into pixels, the slider to angle blend (geometry step), and `Math.hypot` to turn east, north and up differences into one error length in metres (`web/first-screen.js`, `web/step-geometry.js`, `web/step-signal.js` in the open PRs).

**2.4 What happens if Python fails or the engine cannot load?**
From the open PRs: each step file loads `bridge.js` inside a try block. On failure it shows a plain message and leaves the controls off, instead of breaking the page (`web/first-screen.js`). For bad input, a Python function returns `{"error": "<plain message>"}` and the page shows that sentence (docs/interface.md).
Answer for how the bridge itself reports errors: to be filled in after bridge.js merges (owner explains in their own words).

**2.5 Trap: A Python call takes time. What stops the page showing a stale result while the user drags a slider?**
From the open PRs: each step keeps a "running" flag. If a call is in progress, it remembers that a newer run is wanted and runs once more afterwards (`web/first-screen.js`, `web/step-geometry.js`, `web/step-signal.js`). The geometry and signal steps also copy the slider value at the start of a run, so a run draws the value it was started with.
Answer for the bridge side: to be filled in after bridge.js merges (owner explains in their own words).

**2.6 Trap: How do you know the numbers on screen were computed in the browser and not prepared?**
Answer: to be filled in after bridge.js merges (owner explains in their own words).
(What the repo already says: every number and line comes from the mechanism functions (design.md 2b); the mechanism must compute its outputs from the user's inputs, with no prepared results and no hosted AI (AGENTS.md rule 7).)

---

## 3. Coordinates and the map lines (coords.py, mapview.py)

**3.1 What coordinate system does the mechanism use?**
Positions are x, y, z in metres from the centre of the Earth (docs/interface.md). Latitude and longitude are converted by `latlon_to_xyz` and back by `xyz_to_latlon`.
Answer for the formulas: to be filled in after coords.py merges (owner explains in their own words).

**3.2 How is a satellite placed from "azimuth and elevation"?**
Contract: `satellite_from_sky` returns a point at GPS orbit height, seen from the receiver in that direction. Azimuth 0 is north and 90 is east. Elevation 0 is the horizon and 90 is straight up (docs/interface.md).
Answer for how it is worked out: to be filled in after coords.py merges (owner explains in their own words).

**3.3 What is a "distance line" on the ground map?**
Conceptual part from the spec: the satellite's measured distance defines a sphere around the satellite. The line is where that sphere cuts the ground. At about 2 km wide (the placeholder in design.md 2b) it looks almost straight, which is why the page calls it a "distance line" (design.md 2b, docs/interface.md).
Answer for how `distance_lines` finds the points: to be filled in after mapview.py merges (owner explains in their own words).

**3.4 Which distance does each line use, and why does it matter?**
Contract: `pseudorange - assumed_clock_error_s * SPEED_OF_LIGHT_M_PER_S` (docs/interface.md). So when the page assumes the clock error is 0, the lines use the raw measurements and pull apart. When it uses the solved clock error, the lines meet (design.md 2b).
Answer for the code: to be filled in after mapview.py merges (owner explains in their own words).

**3.5 What does `inside: false` mean?**
Contract: the line does not cross the square map, so `points` is empty (docs/interface.md).
Answer for how it is decided: to be filled in after mapview.py merges (owner explains in their own words).

**3.6 Trap: A clock that is 1 microsecond ahead adds about 300 m to every distance. Is the position error 300 m?**
No. Spec: the distance error is about 300 m per microsecond, but the position error depends on where the satellites are, so the page always shows the error the solver computes, never a fixed 300 m (design.md 2b). The page measures it as the distance between the solved point and the true receiver (`Math.hypot` of east, north and up in `web/first-screen.js`).

**3.7 Trap: Why is the map flat when the Earth is round?**
See section 6, question 6.2.

---

## 4. DOP (geometry.py) (answers from open PR, check after merge)

**4.1 What is DOP in plain words?**
It tells you how much the layout of the satellites multiplies the measurement errors. Lower is better (docs/interface.md). The page shows PDOP (`web/step-geometry.js` reads `dop.pdop`).

**4.2 How does `dop` work?**
For each satellite it takes the direction from the receiver to the satellite as an arrow of length 1, and adds a 1 for the clock. That gives one row per satellite. It then multiplies the table by its own transpose, inverts the result, and takes square roots of sums of the diagonal (`mechanism/geometry.py`).

**4.3 What is the difference between GDOP, PDOP and TDOP?**
From the code: GDOP uses all four diagonal entries (position and clock together), PDOP uses the first three (position only), TDOP uses the last one (the clock) (`mechanism/geometry.py`).

**4.4 Why does `dop` need at least 4 satellites?**
The table has four columns (x, y, z and clock), so with fewer than four rows it cannot be inverted. The code returns an error sentence if there are fewer than 4 (`mechanism/geometry.py`, docs/interface.md).

**4.5 Does `dop` use the measured distances or the noise?**
No. It uses only the directions to the satellites (docs/interface.md, `mechanism/geometry.py`). That is why it needs no local map frame.

**4.6 Trap: What happens to DOP when the satellites are bunched into one patch of sky, and why?**
Spec (design.md 2a rung 2): the same satellites and the same error give a far worse fix when they are bunched. Code reason: the rows of the table become almost the same, so the multiplied table is almost impossible to invert and the result gets very large. If it truly cannot be inverted, the code returns an error sentence ("These satellites are laid out so that DOP cannot be worked out.") (`mechanism/geometry.py`).

**4.7 Trap: If DOP is only about layout, how does the geometry demo show the real position error?**
From the open PR: the page runs the solver with the clock solved, on measurements with the same noise and seed every run, so only the layout changes between runs. The page shows PDOP and the error in metres between the solved and true positions (`web/step-geometry.js`).

---

## 5. The C/A code and correlation (signal.py) (answers from open PR, check after merge)

**5.1 What is the C/A code?**
Each satellite sends its own repeating pattern of 1023 values, each +1 or -1 (`ca_code(prn)`, docs/interface.md). The receiver knows every satellite's pattern, so it can tell them apart.

**5.2 How is the code generated?**
Two 10-stage shift registers (G1 and G2), both starting as all ones, are clocked once per chip. For each chip, the G1 output is added (XOR) to the G2 output. The G2 output adds two chosen stages, and that choice is what makes each satellite's code different (`mechanism/signal.py`, taken from IS-GPS-200 Table 3-Ia, section 3.3.2.3).

**5.3 How is a delay turned into something the receiver can measure?**
`make_received` shifts the code by a whole number of chips and wraps the end round to the start, then adds random noise with a set standard deviation and seed. The code itself has size 1 (docs/interface.md, `mechanism/signal.py`).

**5.4 How does `correlate` find the delay?**
It tries every shift of the satellite's code, multiplies it chip by chip with what was received, and averages. A perfect match with no noise scores 1.0. The shift with the highest score is `best_delay_chips` (`mechanism/signal.py`).

**5.5 What is `peak_to_next`?**
The best score divided by the second best score. A big number means a clear winner. If no score is above 0 it returns 1.0. If only the best is above 0 it returns 1e9, because infinity is not valid JSON (`mechanism/signal.py`). The page treats a value under 1.5 as "found but barely" and caps the display at "over 1000x" (`web/step-signal.js`, placeholders).

**5.6 Trap: Why does correlation work when the signal is below the noise?**
Conceptual: one chip on its own is buried in noise. But the score adds up 1023 chip-by-chip products. At the right shift every product leans the same way, so they add up. Noise is random, so its products point both ways and mostly cancel. At the wrong shifts the code does not line up with itself, so those also stay small. (Reasoning from how `correlate` averages; check the explanation wording with Icarus.)

**5.7 Trap: What happens when the noise gets too big, and how does the page show it?**
The page has a noise slider and shows whether the best shift equals the true delay. When it does not, the page calls it lost; when the peak is only barely above the next score, it says "found but barely" (`web/step-signal.js`). Where exactly it fails depends on the noise and seed, so run the page and report what you see rather than quoting a number.

**5.8 Trap: Your delays are whole chips. Real signals are not. Does that matter?**
See section 6, question 6.4.

**5.9 Is the noise real?**
It is simulated: random numbers from a generator with a fixed seed, so a run can be repeated (`mechanism/signal.py`, `web/step-signal.js`).

---

## 6. The simplifications

**6.1 Why is the Earth a sphere of one radius?**
The real Earth is slightly flattened. We use a sphere because the conversions are a few lines anyone on the team can explain. The simulated truth and the solver use the same model, so results stay exact. The page must say this is a simplification (decisions.md 2026-11-23, marked provisional).

**6.2 Why a flat 2D ground map of about 2 km?**
At that zoom the distance lines look almost straight, and the map ignores "up" when drawing (design.md 2b, docs/interface.md). The line is still where the satellite's distance sphere cuts the ground plane.
Answer for how mapview.py does the cut: to be filled in after mapview.py merges (owner explains in their own words).

**6.3 Are the satellites real?**
No. Satellites are placed from an azimuth and an elevation we choose, at GPS orbit height. The browser cannot read how many satellites the phone really uses; it only gives latitude, longitude, accuracy, altitude, heading and speed. A "real satellites above you" view was cut or left for last because predicting orbits is hard to explain and a library for it would be code we did not write (design.md 2, 2a).

**6.4 Why are signal delays whole chips?**
In the code, `delay_chips` must be a whole number from 0 to 1022 (`mechanism/signal.py`, docs/interface.md). This keeps the demo simple to explain. A real receiver is not limited to whole chips. Reason the team chose this: team to fill in.

**6.5 Is the first screen's "microsecond clock error" realistic?**
The slider range, noise and error limits are placeholders to be tuned in testing, and the page's own numbers are to be checked against a source before shipping (`web/config.js`, design.md 2a). Icarus decides which stay.

**6.6 What other simplifications should we admit?**
- The satellites do not move; each scenario is a fixed snapshot (code in open PRs sets fixed azimuth and elevation).
- Noise on distances is a plain random value with a chosen size (docs/interface.md).
- The relativity step and the reflections step are not built yet. Relativity (rung 4) is tested before it is promised: a drift shared by all satellites may be absorbed by the clock solve and show no position drift. Reflections are the first rung to cut (design.md 2b).
- Team to confirm the list after merge.

**6.7 Trap: What would happen if all the satellite clocks drifted the same way?**
Spec (design.md 2b): a drift shared by all satellites may be absorbed by the clock solve, so the position would not drift, only the clock value would change. If so, the page shows the range error and says why the solver hides it. This is "tested before it is promised", so check with the solver before answering with confidence. Team to confirm after solver.py merges.

**6.8 Trap: What is the real accuracy of your demo compared with a phone?**
Team to fill in. Do not quote a number we have not verified (design.md 2a).

---

## 7. Why Python in the browser (design.md 3)

**7.1 Why is the mechanism written in Python and not JavaScript?**
Two of the four teammates code only in Python, and they own the mechanism (design.md 3, Icarus, 2026-11-22).

**7.2 How does Python run in a web browser?**
Through Pyodide, which runs Python in the user's browser (design.md 3). The page loads it with numpy and the mechanism files (docs/interface.md). Answer for how that loading works in detail: to be filled in after bridge.js merges (owner explains in their own words).

**7.3 Why not call a server?**
The brief requires a public link with no sign-in, download or API key (design.md 1, point 3), and requires that outputs are computed by our code from the user's inputs (point 5). Running in the browser keeps it all in the page. Whether a server was ever considered: team to fill in.

**7.4 Why plain numbers, strings, lists and dicts between the two sides?**
See question 2.2.

**7.5 Trap: How do you know the page is not just playing recorded results?**
Every number and line comes from the mechanism functions (design.md 2b). The mechanism must be our own code that computes outputs from the inputs, with no prepared results (AGENTS.md rule 7, design.md 1 point 5). A judge can change a slider and see new values.

**7.6 Trap: What did you use that you did not write?**
Pyodide and numpy are open-source components. The brief allows them if the team can explain why it chose them (design.md 1, point 7). Why these two: Pyodide because the mechanism owners write Python (design.md 3). Numpy: team to fill in. The C/A code taps come from the public IS-GPS-200 spec, cited in `mechanism/signal.py`.

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

## Still to fill in after merge

- Group 1: all answers (solver.py).
- Group 2: 2.1, 2.4 (bridge side), 2.5 (bridge side), 2.6 (bridge.js).
- Group 3: formulas and how lines and `inside` are worked out (coords.py, mapview.py).
- Groups 6, 7, 8: lines marked "team to fill in".
- Re-check groups 4 and 5 against `main` once geometry.py and signal.py merge.
