# overview.md

What is built. One dated line per merged issue, added at the end: `- YYYY-MM-DD | #issue | what now exists`.

## Area map
- `mechanism/` Python mechanism (runs in the browser through Pyodide). Owners: tw-2866, scoobertfan.
- `tests/` tests for the mechanism.
- `index.html`, `web/` the page. Owners: jstnstyad10, aliyymakes. Neither exists yet.
- `docs/interface.md` the contract between the two.

## Built
- 2026-11-22 | setup | Team system only: AGENTS.md, CLAUDE.md, CONTRIBUTING.md, .memory/, issue and pull request templates, test workflow, one smoke test. No project code yet. Not yet pushed to GitHub.
- 2026-11-23 | #9 (draft) | web/step-geometry.js + web/dev/step-geometry.html: rung 2 section ("Bunch the satellites" slider, sky diagram, DOP, position error). Waits on the bridge and mechanism.
- 2026-11-23 | #8 | mechanism/signal.py: `ca_code`, `make_received`, `correlate` (C/A code from the IS-GPS-200 shift registers, noisy copy, sliding match); tests in tests/test_signal.py.
- 2026-11-23 | #7 | mechanism/geometry.py: `dop(receiver, satellites)` gives GDOP, PDOP, TDOP from the satellite directions; tests in tests/test_geometry.py.
- 2026-11-23 | #11 | docs/project-page.md: draft project page text (idea, rungs, simplifications, components, team); numbers only from docs/facts.md.
- 2026-11-23 | #6 | docs/facts.md: every number the page and documents use, each with a source link and exact quoted value, re-checked by a second reviewer. Use only rows not marked unconfirmed.
- 2026-11-23 | #2 | mechanism/coords.py (lat/lon ↔ xyz on a sphere, satellite from azimuth/elevation), mechanism/scenario.py (make_pseudoranges with clock error and seeded noise), EARTH_RADIUS_M and GPS_ORBIT_RADIUS_M in constants.py, with tests.
- 2026-11-23 | #1 | mechanism/solver.py matches docs/interface.md: satellites and results as x_m/y_m/z_m dicts, steps from the Earth's centre; tests use satellites above the horizon. Duplicate mechanism/test_solver.py and the zip removed.
- 2026-11-23 | #27 | scripts/check_relativity.py: prints the position error with the clock solved and trusted when a shared relativity drift is added.
