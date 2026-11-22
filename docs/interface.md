# interface.md: the contract between mechanism/ (Python) and the page

Status: Proposed 2026-11-22. Nothing here is built. The first mechanism goal confirms or changes it. After that, a change needs its own issue and a yes from both sides.

Rules:
- The page calls Python functions and draws what they return. The page does no GPS maths.
- Only plain numbers, strings, lists and dicts cross the line. No numpy arrays, no custom classes.
- Units are in the name: `_m` metres, `_s` seconds, `_deg` degrees.
- A function never fails silently. On bad input it returns `{"error": "<plain message>"}`.

Proposed functions:

| Function | Takes | Returns |
|---|---|---|
| `satellites_overhead(lat_deg, lon_deg, unix_time_s)` | where the user is and when | list of `{"id", "azimuth_deg", "elevation_deg", "x_m", "y_m", "z_m"}` for satellites above the horizon |
| `solve_position(satellites, pseudoranges_m)` | satellite positions and the measured distance to each | `{"x_m", "y_m", "z_m", "lat_deg", "lon_deg", "clock_error_s", "steps"}` where `steps` is the list of guesses the solver made, in order |

More functions get added here as the spec names more inputs (design.md section 6).
