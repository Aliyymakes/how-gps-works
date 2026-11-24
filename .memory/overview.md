# overview.md

What is built. One dated line per merged issue, added at the end: `- YYYY-MM-DD | #issue | what now exists`.

## Area map
- `mechanism/` Python mechanism (runs in the browser through Pyodide). Owners: tw-2866, scoobertfan.
- `tests/` tests for the mechanism.
- `index.html`, `web/` the page. Owners: jstnstyad10, aliyymakes. Neither exists yet.
- `docs/interface.md` the contract between the two.

## Built
- 2026-11-22 | setup | Team system only: AGENTS.md, CLAUDE.md, CONTRIBUTING.md, .memory/, issue and pull request templates, test workflow, one smoke test. No project code yet. Not yet pushed to GitHub.
- 2026-11-23 | #13 | docs/interview-prep.md: 57 judge questions in 8 groups; answers for geometry, signal and the page from open PRs; solver, bridge, coords and mapview answers left for their owners.
- 2026-11-23 | #12 | docs/demo-script.md: draft shot list for the demo video (first screen, then rungs 2 and 3); length left to Icarus.
- 2026-11-23 | #5 (draft) | index.html, web/config.js, web/first-screen.js: the first screen (ground map, clock slider, solve button, satellite switches). Paints without Python; waits on bridge, coords, scenario, solver, mapview to run.
- 2026-11-23 | #9 (draft) | web/step-geometry.js + web/dev/step-geometry.html: rung 2 section ("Bunch the satellites" slider, sky diagram, DOP, position error). Waits on the bridge and mechanism.
- 2026-11-23 | #10 (draft) | web/step-signal.js + web/dev/step-signal.html: rung 3 section (noise slider, received signal, 1023 correlation scores with best and true delay marked). Waits on the bridge and signal.py.
- 2026-11-23 | #8 | mechanism/signal.py: `ca_code`, `make_received`, `correlate` (C/A code from the IS-GPS-200 shift registers, noisy copy, sliding match); tests in tests/test_signal.py.
- 2026-11-23 | #7 | mechanism/geometry.py: `dop(receiver, satellites)` gives GDOP, PDOP, TDOP from the satellite directions; tests in tests/test_geometry.py.
- 2026-11-23 | #11 | docs/project-page.md: draft project page text (idea, rungs, simplifications, components, team); numbers only from docs/facts.md.
- 2026-11-23 | #6 | docs/facts.md: every number the page and documents use, each with a source link and exact quoted value, re-checked by a second reviewer. Use only rows not marked unconfirmed.
- 2026-11-23 | #3 | web/bridge.js (loadMechanism, callPython) and web/bridge-test.html; not yet checked in a real browser.
- 2026-11-23 | #2 | mechanism/coords.py (lat/lon ↔ xyz on a sphere, satellite from azimuth/elevation), mechanism/scenario.py (make_pseudoranges with clock error and seeded noise), EARTH_RADIUS_M and GPS_ORBIT_RADIUS_M in constants.py, with tests.
- 2026-11-23 | #1 | mechanism/solver.py matches docs/interface.md: satellites and results as x_m/y_m/z_m dicts, steps from the Earth's centre; tests use satellites above the horizon. Duplicate mechanism/test_solver.py and the zip removed.
- 2026-11-23 | #4 | mechanism/mapview.py: to_local (east/north/up from the true receiver) and distance_lines (each satellite's distance circle on the flat local map), with tests.
- 2026-11-23 | #27 | scripts/check_relativity.py: prints the position error with the clock solved and trusted when a shared relativity drift is added.
- 2026-11-23 | #31 | README.md rewritten for judges: what it is, how to try it (LIVE LINK TBA), how it works, what is simplified, components we did not write, team.
- 2026-11-23 | #30 | mechanism/relativity.py: drift_over_time gives, per number of hours, the range added by the shared relativity drift and the position error with the clock solved and trusted; scripts/check_relativity.py uses it.
- 2026-11-23 | #37 | index.html: rung 2, 3 and 4 sections below the first screen (web/step-relativity.js new); stacked on #17, #18, #19, #26; not yet checked in a browser.
- 2026-11-24 | #41 | LICENSE: MIT, copyright 2026 aliyymakes, tw-2866, scoobertfan, jstnstyad10.
- 2026-11-24 | #40 | web/first-screen.js: when the page refuses to solve or a Python call fails, showNoFix clears the metres value, badge and map dot.
- 2026-11-24 | #43 | web/config.js default satellites: azimuths 10/100/235/325, elevations 60/35/20/20 (PDOP 3.37, four distinct line directions).
- 2026-11-24 | #45 | docs/onboarding/: README, architecture, follow-one-click, code-tour, decisions, glossary written; self-check.md still to come (self-check pending).
- 2026-11-24 | #13 | docs/interview-prep.md re-checked against merged bridge, page, step files and config.js; answers use the new default satellites (520.3 m trusted, PDOP 3.37) and name the Hᵀ H step in dop.
- 2026-11-24 | #12 | docs/demo-script.md: 8-shot demo video script, about 2:05, quoting the real page text of the first screen and rungs 2 and 3; timing is read from code, not recorded.
- 2026-11-24 | #48 | accuracy pass: README, project page, interview prep and onboarding docs corrected (stale rung 4 and PR text, drift sign, exactness, noise thresholds).
- 2026-11-24 | #52 | Live at https://aliyymakes.github.io/how-gps-works/ (repo public, GitHub Pages from main, root folder).
- 2026-11-24 | #54 | docs/ux-audit.md + docs/ux-audit/: audit of the live page before plan 004's fixes (6 blocking, 14 confusing, 6 polish findings, measured load and freeze times).
- 2026-11-24 | #56 | No silent actions: shared start-up progress and one Try again (web/startup.js), web/say.js flashes repeated messages, satellite-count refusals with true words and matching map lines, solve button shows its mode, Reset answers, caption says when lines leave the map; tests/ui/ with 10 Playwright tests.
- 2026-11-24 | #59 | First two minutes: the idea in the opening words, a map key, a 'map appears when Python has loaded' line, a three-step guided path (one highlighted control, hints that go away), a closing line, and the lines gliding together when the phone solves for its clock (not for keyboard or reduced motion).
- 2026-11-24 | #60 | Geometry, signal and relativity sections: hint that hides after first use, state sentences, DOP spelled out, signal graph cut-off note, relativity slider with trusted vs solved results; tests/ui/test_layers.py.
- 2026-11-24 | #64 | Faster start: Pyodide preloaded from the page head, numpy loaded with Pyodide, mechanism files fetched in parallel; tests/ui/test_speed.py (first paint, frame gaps, no console errors).
- 2026-11-24 | #66 | Accessibility: contrast fixes for meaningful marks (true-delay mark, slider tracks, switch off ring), reduced motion for knobs and thumbs, every drawing's label says its current state, 195 px zoom without sideways scroll; tests/ui/test_accessibility.py.
- 2026-11-24 | #68 | Visual polish: quieter link lines and more space before each section, one look for all four slider blocks, label spacing, no empty gaps, one metres format (web/format.js); before/after screenshots in docs/ux-audit/polish/.
