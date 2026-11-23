# interface.md: the contract between mechanism/ (Python) and the page

Status: set by the orchestrator 2026-11-23 for the first goals. A change needs its own issue and a yes from both sides.

Rules:
- The page calls Python functions and draws what they return. The page does no GPS maths.
- Only plain numbers, strings, booleans, lists and dicts cross the line. No numpy arrays, no custom classes.
- Units are in the name: `_m` metres, `_s` seconds, `_deg` degrees.
- Positions are x, y, z in metres from the centre of the Earth. The Earth is treated as a sphere (see decisions.md).
- A point is `{"x_m": number, "y_m": number, "z_m": number}`. A satellite is a point with an extra `"id"` string.
- A function never fails silently. On bad input it returns `{"error": "<plain message>"}`.
- `clock_error_s` is how far the phone's clock is ahead of true time. A positive value makes every measured distance too long by `clock_error_s * SPEED_OF_LIGHT_M_PER_S`.

## mechanism/coords.py

| Function | Returns |
|---|---|
| `latlon_to_xyz(lat_deg, lon_deg, height_m=0)` | a point |
| `xyz_to_latlon(x_m, y_m, z_m)` | `{"lat_deg", "lon_deg", "height_m"}` |
| `satellite_from_sky(receiver_lat_deg, receiver_lon_deg, azimuth_deg, elevation_deg)` | a point at GPS orbit height, seen from the receiver in that direction. Azimuth 0 is north, 90 is east. Elevation 0 is the horizon, 90 is straight up |

## mechanism/scenario.py

| Function | Returns |
|---|---|
| `make_pseudoranges(receiver, satellites, clock_error_s, noise_m=0, seed=0)` | list of measured distances in metres, one per satellite, in the same order: true distance + clock error effect + random noise with standard deviation `noise_m` |

## mechanism/solver.py

| Function | Returns |
|---|---|
| `solve_position(satellites, pseudoranges_m, solve_clock=True)` | `{"x_m", "y_m", "z_m", "clock_error_s", "steps", "converged"}`. `steps` is the list of guesses in order, each `{"x_m", "y_m", "z_m", "clock_error_s"}`, starting from the centre of the Earth. With `solve_clock=False` the solver trusts the phone's clock (`clock_error_s` stays 0) and needs at least 3 satellites; with `True` it needs at least 4 |

## mechanism/mapview.py (added 2026-11-23, design.md 2b)

The local ground map is a flat square centred on the true receiver position: east and north in metres, up ignored for drawing.

| Function | Returns |
|---|---|
| `to_local(receiver_lat_deg, receiver_lon_deg, point)` | `{"east_m", "north_m", "up_m"}`: where a point (for example the solved position) is relative to the true receiver |
| `distance_lines(receiver_lat_deg, receiver_lon_deg, satellites, pseudoranges_m, assumed_clock_error_s, half_width_m=1000, samples=40)` | one entry per satellite, same order: `{"id", "points": [[east_m, north_m], ...], "inside": true/false}`. `points` traces where the satellite's distance sphere cuts the ground plane, inside the square of `half_width_m`. The distance used is `pseudorange - assumed_clock_error_s * SPEED_OF_LIGHT_M_PER_S`. `inside` is false and `points` empty when the line does not cross the square |

## The page side (web/bridge.js)

| Function | Does |
|---|---|
| `await loadMechanism(onStatus)` | loads Pyodide, numpy and the mechanism files; calls `onStatus(text)` with progress messages |
| `callPython("module.function", [arg1, arg2, ...])` | calls `mechanism.<module>.<function>` and returns its result as a plain JavaScript value |

Later rungs add `mechanism/signal.py` and `mechanism/relativity.py`. The bridge's file list must include `mapview.py`. Their functions are added here by the goal that builds them.
