# gotchas.md

Traps that cut across areas. One line per entry, added at the end:
`- YYYY-MM-DD | source | X fails; do Y`. Date = last verified.

- 2026-11-22 | external | A web page cannot read satellite count or signal strength from the phone; the browser location API has no such fields. Compute satellites overhead from orbit data instead and label it as computed.
- 2026-11-22 | external | Antigravity has a size limit on rule files (reported as 12,000 characters, unverified). Keep AGENTS.md short and put detail in .memory/.
- 2026-11-22 | .gitattributes | `merge=union` keeps both sides' lines but can leave a duplicate or an odd order. Only add lines at the end of union files; never edit or reorder existing lines on a branch.
- 2026-11-22 | external | Pyodide downloads when the page first opens and that takes a few seconds (unverified how many). Show a loading message so the two-minute clock does not start on a blank page.
- 2026-11-22 | .github/workflows/tests.yml | The test workflow uses Python 3.12. Pyodide ships its own Python version; when the Pyodide version is chosen, match the workflow to it (unverified).
- 2026-11-22 | external | `gh` is not installed by default on a Mac; scripts and agents fail with "gh: command not found". Install it (`brew install gh`) and run `gh auth login` before anything else.
- 2026-11-23 | pytest.ini | Plain `pytest` puts tests/ on the import path, not the repo root, so `import mechanism` fails; pytest.ini sets `pythonpath = .`. Keep it, and run `python -m pytest -q` from the repo root.
- 2026-11-23 | web/theme.css | `.badge` sets `display: inline-flex`, which beats the `hidden` attribute; index.html adds `.badge[hidden] { display: none; }`. Do the same for any themed element you hide with `hidden`.
- 2026-11-23 | external | macOS (BSD) `sed -i` needs a suffix argument (`sed -i '' ...`); GNU-style `sed -i` fails.
- 2026-11-23 | external | gps.gov/technical/icwg/ and older IS-GPS-200 PDF links return 404. IS-GPS-200N is at https://www.gps.gov/sites/default/files/2025-07/IS-GPS-200N.pdf. Its Table 3-Ia text extracts scrambled; the "first 10 chips octal" for PRN 20-32 could not be read, so tests check PRN 1-19 only.
- 2026-11-23 | mechanism/signal.py | The "first 10 chips" octal in IS-GPS-200 is logic bits, and its first digit is ONE bit (1440 = 1 100 100 000). Compare against bits, not ±1 values.
- 2026-11-23 | tests/test_signal.py | At noise_std 50 the peak_to_next ratio sits between about 1.0 and 1.26 depending on the seed; the high-noise test relies on its fixed seed.
- 2026-11-23 | mechanism/geometry.py | Bunched satellites are rarely exactly singular in floating point, so `dop` gives a huge number (about 350 for four satellites within 10 degrees) rather than an error. Show large DOP values as they are; do not wait for an error to say "too bunched".
- 2026-11-23 | docs/facts.md | The "38 µs a day" relativity figure is 45 − 7 rounded; IS-GPS-200N's exact factory offset (−4.4647e-10) gives 38.58 µs a day (about 11.6 km). Say "about 38 µs" and "about 11 km", never exact.
- 2026-11-23 | docs/facts.md | Many sources quote −160 dBW for the received L1 C/A power; IS-GPS-200N gives −158.5 dBW minimum. The satellite count also depends on date (31 on gps.gov's 2023 page, 32 in an April 2026 Space Force slide): always say which date.
- 2026-11-23 | mechanism/solver.py | solve_position starts at the Earth's centre, so 3 satellites in one plane with the centre and the receiver (for example overhead, north and south) give "cannot give one clear position" with solve_clock=False. Pick 3-satellite test sets with one satellite off that plane.
- 2026-11-23 | mechanism/mapview.py | mapview imports the private coords._local_directions; renaming it breaks mapview. A satellite without an "id" gives "id": None in distance_lines.
- 2026-11-23 | scripts/check_relativity.py | The "about 11 km a day" relativity figure is a range error. In this model it never becomes a position error when the clock is solved, because every satellite drifts the same. Do not say "your position would be 11 km off per day" on the page without a model that shows it.
