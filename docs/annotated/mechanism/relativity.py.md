# relativity.py, line by line

Source: `mechanism/relativity.py`

If you have never read code, start with [how to read code](../how-to-read-code.md).

## What this file is for
Because of Einstein's relativity, satellite clocks would run about 38 microseconds a day fast compared with clocks on the ground, if nobody corrected them. This file answers the question: what does that do to the position the phone works out?

It adds a drift that grows with time, the same for every satellite, to the measured distances. Then it solves the position twice: once letting the solver find the clock error too, and once trusting the phone's clock. The answer is a short table, one line for each hour value it is asked about (the page asks for 0, 1, 6 and 24 hours).

## Which files it talks to
- `mechanism/constants.py`: gives `RELATIVITY_DRIFT_S_PER_DAY` (38e-6, from `docs/facts.md` row 27) and `SPEED_OF_LIGHT_M_PER_S`.
- `mechanism/scenario.py`: `make_pseudoranges` makes the measured distances for each hour.
- `mechanism/solver.py`: `solve_position` works out the position from those distances.
- `web/step-relativity.js`: calls `relativity.drift_over_time` through the Python bridge and shows the table.
- `scripts/check_relativity.py` and `tests/test_relativity.py`: run and check it.
- `docs/interface.md`: has no row for `drift_over_time` yet (noted in `docs/onboarding/architecture.md`).

## In three lines
1. Check the input; any problem becomes an error sentence.
2. For each hour, work out the drift in seconds and add it to the phone's clock error, so every distance gets longer by the same amount.
3. Solve twice (clock solved, clock trusted), measure how far each answer is from the true position, and return one result per hour.

A point to hold on to: this model adds the drift as an extra phone clock error. A shared drift is soaked up by the clock the solver finds, so when the clock is solved the position stays right. Only when the clock is trusted does the drift ruin the position. Do not read the table as "your position is 11 km off per day"; that would be wrong in this model. Also do not say the satellite clock "gains, so distances get longer": a satellite clock running ahead would shorten the measured distances. The code adds the drift as longer. Doing it the other way would make the solved clock come out as the phone's error minus the drift instead of plus, and would change the trusted-clock error somewhat, but with the clock solved the position would still stay right.

## The code, line by line

```python
"""What a clock drift shared by every satellite does to the position (rung 4)."""
```
A description of the file in triple quotes (a "docstring"), for people only. "Rung 4" is the fourth step of the page. The key word is "shared": the same drift on every satellite.

```python
import math
```
Loads the standard maths tools. This file uses `math.isfinite`, `math.dist`. Without it those would not exist.

```python
from mechanism.constants import RELATIVITY_DRIFT_S_PER_DAY, SPEED_OF_LIGHT_M_PER_S
from mechanism.scenario import make_pseudoranges
from mechanism.solver import solve_position
```
Three `from ... import ...` lines fetch named things from our own files. The first brings two constants: the drift per day in seconds, and the speed of light in metres per second. The second brings the recipe that makes measured distances. The third brings the recipe that solves for the position. Keeping them in their own files means this file only has to join them together.

```python
def _is_number(value):
    """True for a normal number. True/False are not accepted as numbers."""
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)
```
A small helper, with `_` at the front of the name to say "only for use inside this file". It is given a value and answers true or false. Three conditions are joined by `and`, so all must hold: it is a whole number or decimal number (`int` or `float`); it is not a `bool` (in Python `True` counts as the number 1, which would sneak through, so it is refused on purpose); and `math.isfinite` says it is not infinity and not "not a number". Without this helper, text, `True`, or infinity in the input would crash the maths or give nonsense.

```python
def _check_input(receiver, satellites, phone_clock_error_s, hours_list):
    """Return an error message for bad input, or None if the input is fine."""
    if not isinstance(satellites, list) or len(satellites) < 4:
        return "At least 4 satellites are needed."
```
Another helper. It looks at all the input and gives back either a sentence describing the first problem, or `None` ("nothing", meaning the input is fine). This first check says the satellites must be a list of at least 4. Four are needed because there are four unknowns (x, y, z and the clock).

```python
    if not isinstance(hours_list, list) or len(hours_list) == 0:
        return "hours_list must be a list with at least one number."
```
The hours must come as a list with something in it (`len(...) == 0` means empty). Without a list there is nothing to loop over below.

```python
    if not _is_number(phone_clock_error_s):
        return "The phone clock error must be a number."
```
The phone's own clock error must be a real number, checked by the helper above. Without this, a word or `True` would reach the maths.

```python
    for hours in hours_list:
        if not _is_number(hours):
            return "Every hour value must be a number."
        if hours < 0:
            return "Hours must not be negative."
```
`for hours in hours_list:` checks each hour value in turn. Each must be a real number, and must not be below 0, since there is no drift before time starts. The first bad value ends the check with its sentence.

```python
    # A point and every satellite need numbers for x, y and z.
    points = [receiver] + satellites
    for point in points:
```
The comment says what comes next. `[receiver] + satellites` joins the receiver, as a one-item list, to the front of the satellites list, so that one loop checks all of them. `for point in points:` repeats the indented lines below for each one.

```python
        if not isinstance(point, dict):
            return "The receiver and every satellite must be a point."
```
Each must be a labelled box (a `dict`) such as `{"x_m": 1, "y_m": 2, "z_m": 3}`. If it is anything else, there are no x, y, z to read.

```python
        for key in ("x_m", "y_m", "z_m"):
            if not _is_number(point.get(key)):
                return "Every point needs number values for x_m, y_m and z_m."
    return None
```
For each of the three names, `point.get(key)` reads the value, and gives `None` if the name is missing instead of crashing. `None` is not a number, so a missing name is also caught by the helper. If everything passed, the last line, `return None`, says "no problem found". It sits after the loop (less indented), so it runs only if no earlier `return` happened.

```python
def _error_m(answer, receiver):
    """How far the solved position is from the true receiver, in metres."""
    return math.dist(
        [answer["x_m"], answer["y_m"], answer["z_m"]],
        [receiver["x_m"], receiver["y_m"], receiver["z_m"]],
    )
```
A helper that measures how wrong an answer is. `math.dist` takes two points, each as a list of three numbers, and gives the straight-line distance between them (Pythagoras in three dimensions: square the gaps, add, square-root). The first list is the solver's position, the second is the true one. The result is the error in metres. Without this, there would be no figure to show.

Worked example: the solver says (3, 4, 12) and the truth is (0, 0, 0). 3 squared + 4 squared + 12 squared = 9 + 16 + 144 = 169. The square root is 13 metres.

```python
def drift_over_time(receiver, satellites, phone_clock_error_s, hours_list):
    """For each number of hours, add the shared drift and solve two ways.

    Returns one dict per hour: hours, range_added_m, error_clock_solved_m,
    error_clock_trusted_m, solved_clock_error_s. Bad input returns {"error": ...}.
    """
```
This is the recipe the page calls. The description lists what comes back: one labelled box ("dict") per hour, with five labels: `hours`, `range_added_m` (how many metres the drift adds to every distance), `error_clock_solved_m` and `error_clock_trusted_m` (the position error with the clock solved or trusted), and `solved_clock_error_s` (the clock error the solver found). For bad input it returns `{"error": ...}` instead, as the contract says.

```python
    message = _check_input(receiver, satellites, phone_clock_error_s, hours_list)
    if message:
        return {"error": message}
```
Runs the checker. If it gave back a sentence, `if message:` is true, and the recipe hands the sentence back in the error box and stops. If it gave `None`, the `if` is false and the recipe carries on. Without it, bad input would crash deeper inside.

```python
    results = []
    for hours in hours_list:
```
`results = []` is an empty list for the answers. The loop does the indented work once for each number of hours, calling it `hours`.

```python
        # The drift grows with time and is the same for every satellite.
        drift_s = RELATIVITY_DRIFT_S_PER_DAY * hours / 24
```
The maths line. The drift per day is 38 microseconds. A day has 24 hours, so the drift in `hours` hours is 38 microseconds times hours, divided by 24. The result `drift_s` is in seconds, and it is the same for every satellite (this is the "shared" part).

Worked example:
- 1 hour: 38e-6 times 1 divided by 24 = 0.0000015833 s, about 1.58 microseconds.
- 6 hours: 38e-6 times 6 / 24 = 0.0000095 s, 9.5 microseconds.
- 24 hours: 38e-6 s = 38 microseconds.

```python
        # It makes every measured distance longer, just like a phone clock error.
        ranges = make_pseudoranges(receiver, satellites, phone_clock_error_s + drift_s)
        if isinstance(ranges, dict):
            return ranges
```
The comment gives the modelling choice: the drift is treated like extra phone clock error, so it is simply added to the phone's own clock error and passed on. `make_pseudoranges` then gives each satellite a measured distance that is the true distance plus the clock error (now bigger) times the speed of light. No noise is passed, so noise is 0. This is a model choice: the real satellite clock would, if running ahead, shorten distances (see the note at the top). With the clock solved, the position comes out right either way.

If `make_pseudoranges` hits a problem it returns a `dict` (a labelled box with `error`) instead of a list. `isinstance(ranges, dict)` spots that and passes the error straight on. Without the check, the solver below would be given an error box instead of distances.

```python
        # Solve once with the clock solved, once trusting the phone's clock.
        solved = solve_position(satellites, ranges, solve_clock=True)
        if "error" in solved:
            return solved
```
`solve_position` works back from the satellites and the measured distances to a position. With `solve_clock=True` it also solves for the unknown clock error, which is the real way a phone works (four unknowns, at least four satellites). If the answer holds the label `error`, the failure is passed back as it is. Without that check, the lines below would try to read a position from an error box.

```python
        trusted = solve_position(satellites, ranges, solve_clock=False)
        if "error" in trusted:
            return trusted
```
The same distances again, but with `solve_clock=False`: the solver is told to believe the phone's clock is perfect (clock error 0). Any real clock error then has nowhere to go, and it bends the position instead. This is the comparison the page wants: a phone that solves for its clock versus a phone that trusts it.

```python
        results.append(
            {
                "hours": float(hours),
                "range_added_m": float(drift_s * SPEED_OF_LIGHT_M_PER_S),
                "error_clock_solved_m": float(_error_m(solved, receiver)),
                "error_clock_trusted_m": float(_error_m(trusted, receiver)),
                "solved_clock_error_s": float(solved["clock_error_s"]),
            }
        )
```
This builds this hour's result box and adds it to the list. Each `float(...)` turns a value into an ordinary decimal number.
- `hours`: the hour value.
- `range_added_m`: the drift turned into metres, drift in seconds times the speed of light. Worked example, 1 hour: 0.0000015833 times 299 792 458 = 474.67 metres. For 6 hours it is 2 848.03 metres. For 24 hours: 38e-6 times 299 792 458 = 11 392.11 metres, the figure in `docs/facts.md` row 31 (11.39 km, worked out from 38 microseconds; NASA's source says only "about 11 km", and the 38 microseconds is itself rounded).
- `error_clock_solved_m` and `error_clock_trusted_m`: how far each solved position is from the truth, using `_error_m` above.
- `solved_clock_error_s`: the clock error that the solver found, in seconds.

Running it with the page's settings (`web/config.js`: receiver in Jakarta; four satellites at azimuth 10, 100, 235, 325 degrees and elevation 60, 35, 20, 20 degrees, placed on the GPS orbit, about 20 900 to 23 700 km from the receiver; a phone clock error of 1 microsecond) gives:

```text
hours  range_added_m  error_clock_solved_m  error_clock_trusted_m  solved_clock_error_s
0           0.0       about 0 (under 1e-8)     520.3                1.0000e-06
1         474.7       about 0 (under 1e-8)    1344.2                2.5833e-06
6        2848.0       about 0 (under 1e-8)    5463.1                1.0500e-05
24     11392.1        about 0 (under 1e-8)   20287.0                3.9000e-05
```
Read it like this. With the clock solved, the position error stays at about zero, because the drift is the same for every satellite and the solved clock soaks it up: the solved clock error is 1 microsecond (the phone's own) plus the drift, 1 + 1.5833 = 2.5833 microseconds at 1 hour and 1 + 38 = 39 microseconds at 24 hours. With the clock trusted, there is nowhere for the shared drift to go, so the position is pushed away: over 20 km off after a day. The page must say this carefully: the large error belongs to trusting the clock, not to relativity itself.

```python
    return results
```
After the loop, the full list of results, one per hour, in the same order as `hours_list`, is returned. It sits after the loop (less indented) so it runs only when every hour has been done. Without it, the page would receive nothing.
