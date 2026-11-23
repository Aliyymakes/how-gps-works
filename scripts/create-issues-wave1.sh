#!/usr/bin/env bash
# Run once by Icarus from the repo root: bash scripts/create-issues-wave1.sh
# Invites the three teammates and creates the first three goals. Unverified until first run.
set -euo pipefail
REPO=$(gh repo view --json nameWithOwner -q .nameWithOwner)

for U in tw-2866 scoobertfan jstnstyad10; do
  gh api -X PUT "repos/$REPO/collaborators/$U" -f permission=push >/dev/null && echo "invited $U"
done

gh issue create --title "Goal: position solver (mechanism/solver.py)" --label goal --label "area:mechanism" --body-file - <<'BODY'
For: @tw-2866

Write the solver that turns satellite positions and measured distances into a position and a clock error, with tests, then stop.

**Area:** mechanism

**Read:** .memory/design.md sections 2a and 3; docs/interface.md (rules, and the mechanism/solver.py table); mechanism/constants.py.

**Files this will touch:** mechanism/solver.py (new), tests/test_solver.py (new). Nothing else in mechanism/.

**Depends on:** nothing. Do not import mechanism/coords.py or mechanism/scenario.py; they are being written in another issue. Build your test data by hand.

**Steps**
1. Write `solve_position(satellites, pseudoranges_m, solve_clock=True)` exactly as docs/interface.md describes. Method: start at the centre of the Earth with clock error 0, then repeat "work out how wrong each measured distance is for the current guess, and nudge the guess to shrink those errors" (least squares with numpy) until the nudge is under 0.001 m or 20 rounds have passed. Record every guess in `steps`.
2. With `solve_clock=False`, solve for x, y, z only and leave `clock_error_s` at 0.
3. Return `{"error": "..."}` in plain words when there are too few satellites (under 4, or under 3 with `solve_clock=False`) or the two lists differ in length.
4. Keep it readable: short functions, plain names, and a comment on each maths step saying what it does in words. Every teammate must be able to explain this file on camera.
5. Tests use a receiver at (6371000, 0, 0) and at least 5 satellites about 26,571,000 m from the Earth's centre, spread at least 60 degrees apart as seen from the receiver.

**Done when**
- [ ] 5 satellites, exact distances, clock error 0.001 s: solved position within 1 m of the true one, clock error within 3e-9 s, `converged` true, at most 20 steps.
- [ ] Exactly 4 satellites, same check, passes.
- [ ] 3 satellites, `solve_clock=False`, clock error 0: position within 1 m.
- [ ] 3 satellites, `solve_clock=False`, clock error 0.000001 s: position more than 100 m off. This is the effect the page shows first.
- [ ] 3 satellites with `solve_clock=True` returns an error dict, not an exception.
- [ ] `steps[0]` is the centre of the Earth and the last step equals the returned answer.
- [ ] Only plain numbers, lists, dicts and booleans are returned (no numpy types). Test it with `json.dumps`.
- [ ] `python -m pytest -q` passes.
- [ ] `.memory/` updated (decisions, gotchas, an overview line, commands)
- [ ] Pull request opened with the template filled in

**Out of scope:** coordinates, making the measurements, noise, anything on the page, satellite geometry scores.
BODY

gh issue create --title "Goal: coordinates and measurements (mechanism/coords.py, scenario.py)" --label goal --label "area:mechanism" --body-file - <<'BODY'
For: @scoobertfan

Write the code that places satellites in the sky and produces the distances a phone would measure, with tests, then stop.

**Area:** mechanism

**Read:** .memory/design.md sections 2a and 3; docs/interface.md (rules, and the coords.py and scenario.py tables); mechanism/constants.py; .memory/decisions.md (the sphere line).

**Files this will touch:** mechanism/coords.py (new), mechanism/scenario.py (new), mechanism/constants.py (add two constants), tests/test_coords.py (new), tests/test_scenario.py (new).

**Depends on:** nothing. Do not import mechanism/solver.py; it is being written in another issue.

**Steps**
1. Add to mechanism/constants.py: `EARTH_RADIUS_M` and `GPS_ORBIT_RADIUS_M` (distance from the Earth's centre). Look both up in a reliable source, do not use numbers from memory, and write the source and the values in decisions.md. Expect roughly 6,371,000 m and 26,560,000 m; if your source is far from these, stop and ask.
2. mechanism/coords.py: `latlon_to_xyz`, `xyz_to_latlon` and `satellite_from_sky`, exactly as docs/interface.md describes, on a sphere. `satellite_from_sky` follows the line from the receiver in the given sky direction until it reaches orbit height.
3. mechanism/scenario.py: `make_pseudoranges` as described. Each value is the straight-line distance + `clock_error_s * SPEED_OF_LIGHT_M_PER_S` + random noise. The same `seed` must give the same noise every time.
4. Bad input (latitude outside -90..90, elevation outside 0..90, empty satellite list) returns `{"error": "..."}` in plain words.
5. Keep it readable: short functions, plain names, a comment on each maths step in words.

**Done when**
- [ ] `latlon_to_xyz` then `xyz_to_latlon` returns the starting latitude and longitude within 1e-9 degrees, for at least 5 places including the equator and lat 89.
- [ ] `latlon_to_xyz(0, 0)` is (`EARTH_RADIUS_M`, 0, 0) within 0.001 m; `latlon_to_xyz(0, 90)` is on the +y axis; `latlon_to_xyz(90, 0)` is on the +z axis.
- [ ] `satellite_from_sky` at elevation 90 is `GPS_ORBIT_RADIUS_M - EARTH_RADIUS_M` from the receiver within 1 m, directly above it.
- [ ] For azimuth 0, 90, 180, 270 and elevation 0, 30, 60: the satellite is `GPS_ORBIT_RADIUS_M` from the Earth's centre within 1 m.
- [ ] From a receiver at lat 0, lon 0: azimuth 0 gives a satellite with larger z than the receiver, azimuth 90 gives larger y.
- [ ] `make_pseudoranges` with clock error 0.000001 s and noise 0 equals the true distance + 299.792458 m within 0.001 m.
- [ ] Same seed gives identical output; over 10,000 values with `noise_m=5` the spread (standard deviation) is between 4.5 and 5.5.
- [ ] Only plain numbers, lists and dicts are returned (no numpy types). Test it with `json.dumps`.
- [ ] `python -m pytest -q` passes.
- [ ] `.memory/` updated (decisions, gotchas, an overview line, commands)
- [ ] Pull request opened with the template filled in

**Out of scope:** the solver, real satellite orbits, signal codes, relativity, anything on the page.
BODY

gh issue create --title "Goal: Python-in-the-browser bridge (web/bridge.js)" --label goal --label "area:web" --body-file - <<'BODY'
For: @jstnstyad10

Make the page able to run the team's Python in the browser and call it from JavaScript, proven on a bare test page, then stop.

**Area:** web

**Read:** .memory/design.md section 3; docs/interface.md (rules, and "The page side"); .memory/gotchas.md; .memory/directives.md (Approved).

**Files this will touch:** web/bridge.js (new), web/bridge-test.html (new), .github/workflows/tests.yml (only the Python version line, only if step 1 says so). Do not create index.html or any CSS file.

**Depends on:** nothing. Only mechanism/constants.py exists today; the other mechanism files arrive from other issues while you work.

**Steps**
1. Use Pyodide from its official CDN. Look up the current stable version in the Pyodide docs, pin that exact version in the URL, and write the version and the Python version it ships in decisions.md. If that Python version differs from the one in .github/workflows/tests.yml, change the workflow to match.
2. web/bridge.js exports `loadMechanism(onStatus)` and `callPython(name, args)` as docs/interface.md describes. `loadMechanism` loads Pyodide and numpy, then fetches these files into a `mechanism` package: `__init__.py`, `constants.py`, `coords.py`, `scenario.py`, `solver.py`, `signal.py`, `relativity.py`. A file that does not exist yet is skipped with one console warning, not an error.
3. `callPython("solver.solve_position", [a, b])` sends the arguments as JSON text, calls the function in `mechanism.solver`, and returns the result parsed from JSON text. A Python exception becomes a rejected promise with the Python message.
4. All URLs are relative, so the page works both at `http://localhost:8000/web/bridge-test.html` and under a sub-path such as `/how-gps-works/web/bridge-test.html`.
5. web/bridge-test.html is plain and unstyled: it shows each status message while loading, then the speed of light read from `mechanism.constants`, the numpy version, and the seconds from page open to ready.
6. No frameworks, no build step, no other dependencies.

**Done when**
- [ ] Served with `python -m http.server 8000` from the repo root, web/bridge-test.html shows 299792458, a numpy version and a load time in seconds. Paste a screenshot in the pull request. If your agent cannot open a browser, the human does this and it is listed under "Verified by a person".
- [ ] A status message is on screen within 1 second of opening, before Pyodide has finished loading.
- [ ] The browser console shows one warning for each missing mechanism file and no errors.
- [ ] Calling a function that does not exist rejects with a readable message.
- [ ] The measured load time (first visit and a reload) is written in the pull request and in gotchas.md.
- [ ] `.memory/` updated (decisions, gotchas, an overview line, commands)
- [ ] Pull request opened with the template filled in

**Out of scope:** the real page, any styling or layout, drawing satellites, GitHub Pages.
BODY

echo "Done. Teammates accept the invite by email or at https://github.com/$REPO/invitations"
