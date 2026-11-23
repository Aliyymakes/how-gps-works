#!/usr/bin/env bash
# Run once by Icarus from the repo root, after committing and pushing: bash scripts/create-issues-wave2.sh
# Creates the map goal and the first-screen goal, and tells the bridge goal to load mapview.py. Unverified until first run.
set -euo pipefail

BRIDGE=$(gh issue list --state open --search "Python-in-the-browser bridge in:title" --json number -q '.[0].number')
if [ -n "$BRIDGE" ]; then
  gh issue comment "$BRIDGE" --body "Change from the spec (design.md 2b, docs/interface.md): also load \`mapview.py\` in the mechanism package file list. If this goal is already merged, the first-screen goal adds it instead."
fi

gh issue create --title "Goal: distance lines for the ground map (mechanism/mapview.py)" --label goal --label "area:mechanism" --body-file - <<'BODY'
For: @scoobertfan (after your coordinates goal merges)

Write the functions that turn satellites and measured distances into lines on a flat local map, with tests, then stop.

**Area:** mechanism

**Read:** .memory/design.md section 2b; docs/interface.md (rules, and the mechanism/mapview.py table); mechanism/coords.py; mechanism/constants.py.

**Files this will touch:** mechanism/mapview.py (new), tests/test_mapview.py (new).

**Depends on:** the coordinates goal being merged (uses mechanism/coords.py). Do not import mechanism/solver.py.

**Steps**
1. `to_local` as docs/interface.md describes: the difference between a point and the true receiver, turned into east, north and up metres.
2. `distance_lines` as described. Method in words: work out each satellite's position in the local east/north/up frame. Its distance sphere cuts the ground plane (up = 0) in a circle centred directly under the satellite, radius = square root of (distance squared minus the satellite's height above the plane squared). Return points along that circle that fall inside the square of `half_width_m`. The circle is huge, so sample by angle only across the part near the square; do not sample the whole circle.
3. Bad input returns `{"error": "..."}` in plain words.
4. Short functions, plain names, a comment on each maths step in words. Every teammate must be able to explain this file on camera.

**Done when**
- [ ] `to_local` of the receiver itself is (0, 0, 0) within 0.001 m; a point 100 m north (made with coords.py) gives north 100 within 0.5 m.
- [ ] With exact distances and `assumed_clock_error_s` equal to the true clock error, every satellite's line passes within 1 m of (0, 0), for 4 satellites between 15 and 65 degrees elevation.
- [ ] With the true clock error 1e-6 s but `assumed_clock_error_s` 0, the lines miss (0, 0) by more than 100 m.
- [ ] Every returned point is inside the square (within 1 m) and there are at least 10 points per line when `inside` is true.
- [ ] Only plain numbers, lists, dicts and booleans are returned. Test with `json.dumps`.
- [ ] `python -m pytest -q` passes.
- [ ] `.memory/` updated (decisions, gotchas, an overview line, commands)
- [ ] Pull request opened with the template filled in

**Out of scope:** the solver, drawing, satellites above 65 degrees, the real Earth shape.
BODY

gh issue create --title "Goal: first screen (index.html, web/first-screen.js)" --label goal --label "area:web" --body-file - <<'BODY'
For: @jstnstyad10 and @aliyymakes (split the steps between you in an issue comment before starting)

Build the first screen exactly as design.md 2b describes, using the real mechanism through the bridge, then stop.

**Area:** web

**Read:** .memory/design.md sections 2b and 3a; docs/ui-guide.md (all of it); docs/interface.md; web/theme.css and web/theme-preview.html.

**Files this will touch:** index.html (new), web/first-screen.js (new), web/config.js (new: every placeholder number), web/bridge.js (only to add `mapview.py` to the file list, if not already there).

**Depends on:** the bridge, solver, coordinates and map goals being merged. Layout and styling can start before; the screen is not done until it runs on the real functions. No hard-coded or prepared results, ever. If you need data while waiting, call the real functions as they land.

**Steps**
1. index.html uses web/theme.css. The question, one sentence and a loading line show within 1 second; controls switch on when Python is ready.
2. Four default satellites from `coords.satellite_from_sky` (15 to 65 degrees elevation, spread around the sky), receiver at a fixed default place (placeholder in config.js).
3. Left: the ground map (SVG) with each satellite's line from `mapview.distance_lines` and the solved position dot from `mapview.to_local`. Colour the dot and a word label by error: ok / warn / bad thresholds are placeholders in config.js.
4. Right, in this order: the highlighted "Make the phone's clock wrong" slider (0 to 3 microseconds, placeholder), the computed "Position off by N m" readout, the "Let the phone solve for its clock" button, one switch per satellite, Reset.
5. Slider moves: `scenario.make_pseudoranges` then `solver.solve_position(..., solve_clock=False)`, lines drawn with assumed clock 0. Button: solve with `solve_clock=True`, lines drawn with the solved clock, and a sentence saying how fast or slow the phone found its clock to be.
6. Three satellites with the clock solved: no solve, one plain sentence: four unknowns, three measurements.
7. Words: one or two sentences per state, next to the thing they describe (ui-guide section 1).

**Done when**
- [ ] On first load: green fix, lines meet at the dot.
- [ ] Slider at 1 microsecond: lines visibly apart, readout shows the solver's error in metres (not a fixed number).
- [ ] Button pressed: lines meet again within 1 m and the clock sentence shows about 1.00 microseconds.
- [ ] A satellite switched off with the clock solved: the refusal sentence, no crash.
- [ ] Works at 390 px wide and 1200 px wide, by mouse, touch and keyboard. Screenshots of both widths in the pull request.
- [ ] Checked against docs/ui-guide.md sections 1 to 5, and listed in the pull request.
- [ ] `.memory/` updated (decisions, gotchas, an overview line, commands)
- [ ] Pull request opened with the template filled in

**Out of scope:** rungs 2 to 5, the sky view, GitHub Pages, any new colours or fonts.
BODY
echo "Done."
