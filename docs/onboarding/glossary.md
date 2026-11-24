# Glossary

Alphabetical. Terms come from the page text ([index.html](../../index.html), `web/*.js`) and the code. "In code" names where to look. Where the code does not use a term, it says so.

- **Azimuth**: the compass direction of a satellite in the sky. 0 is north, 90 is east (docs/interface.md). In code: `azimuth_deg` in `coords.satellite_from_sky` and [web/config.js](../../web/config.js).
- **Bridge**: [web/bridge.js](../../web/bridge.js). It loads Pyodide and gives the page `callPython`.
- **C/A code**: the repeating pattern of 1023 chips each GPS satellite sends, 1 ms long (docs/facts.md rows 11 and 13). In code: `signal.ca_code`.
- **Chip**: one +1 or -1 value of the C/A code. One chip is about 977.5 ns, or about 293 m of travel (facts.md row 14, derived). In code: `CODE_LENGTH = 1023`, `delay_chips`.
- **Clock bias / clock error**: how far the phone's clock is ahead of true time. A positive value makes every measured distance too long by `clock_error_s * SPEED_OF_LIGHT_M_PER_S` (interface.md). One microsecond is about 300 m (facts.md row 32). The page's slider is "Make the phone's clock wrong".
- **Correlation / correlate**: slide a copy of the code along the received signal, multiply chip by chip and average; a high score means a match. In code: `signal.correlate`. Page heading: "How well the code matches at each shift".
- **Distance line**: the page's name for the place where one satellite's distance sphere cuts the ground, drawn on the map. In code: `mapview.distance_lines`.
- **DOP (dilution of precision)**: how much the satellites' layout multiplies measurement errors; lower is better. In code: `geometry.dop`.
  - **GDOP**: the overall figure (all four entries: three position, one clock).
  - **PDOP**: the position part only. The page's DOP readout shows PDOP.
  - **TDOP**: the clock part only.
- **ECEF**: "Earth-centred, Earth-fixed", the usual name for a frame whose origin is the Earth's centre. The code does not use this word; its x, y, z in metres from the Earth's centre (see `coords.py` docstring) is that kind of frame.
- **Elevation**: how high a satellite is above the horizon. 0 is the horizon, 90 is straight up. In code: `elevation_deg`.
- **ENU (east, north, up)**: directions at a spot on the ground. The code does not use the letters "ENU"; it uses `east_m`, `north_m`, `up_m` and `coords._local_directions`.
- **Fix**: the position the phone works out. The page words are "Good fix", "Fix is off", "Fix is far off".
- **Least squares**: finding the move that best reduces all the errors together. In code: `np.linalg.lstsq` in `solver.solve_position`.
- **Local map**: the flat square about 2 km wide centred on the true position (`mapHalfWidthM` is 1000 in config.js).
- **numpy**: a Python library for array maths. Loaded in the browser by `bridge.js` and used in `scenario.py`, `solver.py`, `geometry.py`, `signal.py`.
- **Peak to next (`peak_to_next`)**: the best correlation score divided by the second best. A big number is a clear winner. Shown on the page as "×".
- **PRN**: pseudo-random noise number, 1 to 32, which picks a satellite's C/A code. In code: the `prn` argument in `signal.py`; the page uses `prn: 7` (step-signal.js).
- **Pseudorange**: the distance a phone measures from signal travel time, including the clock error and noise, so it is not the true distance. In code: `pseudoranges_m`, `make_pseudoranges`.
- **Pyodide**: Python compiled to run in a web browser. Loaded from a CDN by `bridge.js`.
- **Pythagoras**: the straight-line distance rule used in `make_pseudoranges` and `solve_position`; no special function, just squares and a square root.
- **Receiver**: the phone. The true receiver position is Jakarta in config.js.
- **Relativity (clock drift)**: satellite clocks gain about 38 microseconds a day (facts.md row 27), which adds about 11 km of range a day. In code: `RELATIVITY_DRIFT_S_PER_DAY`, `relativity.drift_over_time`.
- **Seed**: a whole number that makes random noise repeat exactly. In code: `seed` in `make_pseudoranges` and `make_received`.
- **Shift (delay)**: how many chips the code is moved. In code: `delay_chips`, `best_delay_chips`.
- **Solver**: `solver.solve_position`. Guesses a position, measures how wrong it is, corrects, repeats.
- **SVG**: the drawing format the page uses for the map and graphs (`document.createElementNS` in first-screen.js).
- **Trusted / solved**: the two modes on the first screen. "Trusted" is `solve_clock=False` (assume the clock is right). "Solved" is `solve_clock=True` (find the clock too). In code: `state.mode`.
- **µs (microsecond)**: one millionth of a second. The page shows the slider value in µs.
