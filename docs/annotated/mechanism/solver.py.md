# solver.py, line by line

Source: `mechanism/solver.py`

## What this file is for
This is the heart of the page: it works out where the phone is. It is given where the satellites are and how far away each one seems to be. It starts with a rough guess and improves the guess again and again until the guess stops moving. It can also work out how wrong the phone's clock is.

## Which files it talks to
- `mechanism/constants.py`: gives `SPEED_OF_LIGHT_M_PER_S`, used to turn the clock error from metres into seconds.
- `mechanism/relativity.py`: calls `solve_position` twice, once trusting the clock and once solving for it.
- `web/first-screen.js` and `web/step-geometry.js`: call `solve_position` (through the bridge) with the satellites and the measured distances from the page.
- The numbers it receives come from `mechanism/scenario.py` (`make_pseudoranges`). The exact input and output shapes are in `docs/interface.md`.
- It uses two outside tools: `math` (square root) and `numpy` (the "best fit" maths).

## In three lines
1. Guess a position (start at the Earth's centre), and for each satellite compare the distance we would expect from the guess with the distance measured.
2. Use least squares to find the one small move (and clock change) that best shrinks all those differences together.
3. Move the guess, save it, and repeat until the move is under 1 mm or 20 guesses are saved.

New to code? See [how to read code](../how-to-read-code.md).

## The code, line by line

```python
"""Find a GPS receiver's position using distances to satellites."""
```
A docstring: a sentence in triple quotes at the top of a file that says what the file is for. The computer does not act on it. Without it nothing breaks.

```python
import math
```
Brings in Python's built-in `math` toolbox. This file uses it for the square root in the straight-line distance. Without it, `math.sqrt` below would fail.

```python
import numpy as np
```
Brings in `numpy`, a library for maths on lists of numbers, and gives it the short name `np`. Used for the least-squares step and for measuring the size of a correction. Without it, the solver could not do its main calculation.

```python
from mechanism.constants import SPEED_OF_LIGHT_M_PER_S
```
Takes one named number, the speed of light (299,792,458 metres per second), from `constants.py`. It is needed to turn a clock error in metres into seconds. Without it, the name would be unknown and the file would fail to load.

```python
MAX_STEPS = 20
```
A setting: the most guesses the solver may save (the starting guess counts as one). It stops the solver looping for ever if the guess never settles. Without it the loop would have no limit.

```python
STOP_WHEN_CHANGE_IS_SMALLER_THAN = 0.001  # metres
```
A setting: the solver stops when a correction is smaller than 0.001 metres, which is 1 millimetre. The text after `#` is a comment saying the unit. A tiny correction means the guess has settled. Without it the solver would always run to the limit.

```python
def _save_step(x, y, z, clock_m):
```
Starts a small helper called `_save_step`. A helper is a named recipe: give it a guess (three position numbers and the clock error as a distance in metres) and it hands back a tidy record. The leading underscore is a habit meaning "only used inside this file". Without it the code below that calls it would fail.

```python
    """Save one guess using normal Python numbers and lists."""
```
A docstring explaining the helper: it makes a record using plain Python numbers (not numpy numbers), which the page can read. Nothing breaks without it.

```python
    return {
```
Hands back a result and begins a "dictionary": a set of labelled values written with curly brackets. Each line inside is `label: value`.

```python
        "x_m": float(x),
        "y_m": float(y),
        "z_m": float(z),
```
Three labelled values: the guess's position in metres along the three directions (x, y, z), measured from the Earth's centre. `float(...)` turns each into an ordinary decimal number. This matters because numpy numbers are a special kind that the bridge to the web page may not pass on cleanly. Without these lines the saved guess would have no position.

```python
        "clock_error_s": float(clock_m / SPEED_OF_LIGHT_M_PER_S),
```
The clock error, in seconds. Inside the solver the clock error is kept as a distance in metres (see later), so here it is divided by the speed of light to get seconds, the unit that `docs/interface.md` promises. Worked example: `clock_m` of 300 metres gives 300 / 299,792,458 = 0.0000010007 s, about 1 microsecond. Without the division the page would show metres where it expects seconds.

```python
    }
```
Closes the dictionary started by `return {`.

```python
def solve_position(satellites, pseudoranges_m, solve_clock=True):
```
Starts the main recipe, `solve_position`. It takes the list of satellites, the list of measured distances (`pseudoranges_m`, one per satellite, in metres), and a switch `solve_clock`. The `=True` means that if nobody says otherwise, the clock is solved for. "Trusted" mode on the page is `False`, "solved" mode is `True`. Without this line there is no solver for the page to call.

```python
    """Guess the receiver's location and improve it using satellite distances.

    satellites: a list of {"id", "x_m", "y_m", "z_m"} dicts (positions in metres)
    pseudoranges_m: one measured distance in metres for each satellite
    solve_clock: whether to also find the receiver's clock error
    """
```
A docstring that explains the three inputs in plain words. A "pseudorange" is a measured distance that includes the clock error and noise, so it is not exactly the true distance. The computer ignores this text, but it is the main note for the next person.

```python
    if len(satellites) != len(pseudoranges_m):
```
Checks whether the two lists have different lengths. `len(...)` counts the items in a list and `!=` means "is not equal to". If there are, say, 5 satellites but only 4 distances, some satellite has no distance.

```python
        return {"error": "There must be one distance for each satellite."}
```
If the check above is true, stop straight away and hand back a message instead of a position. The caller gets a message instead of numbers. Without the check, `zip` below would silently drop the extra items and give a wrong answer.

```python
    needed = 4 if solve_clock else 3
```
Works out how many satellites are needed. With the clock unknown there are four unknowns (x, y, z and the clock), so at least 4 distances are needed. With the clock trusted there are three unknowns, so 3. Worked example: `solve_clock=True` gives `needed = 4`; `solve_clock=False` gives `needed = 3`. Without this the solver could not tell when it has too little information.

```python
    if len(satellites) < needed:
```
Checks whether we have fewer satellites than needed.

```python
        return {"error": f"At least {needed} satellites are needed."}
```
If so, stop and report it. The `f"..."` is a sentence with `{needed}` swapped for the real number, for example "At least 4 satellites are needed." Without this, the maths would run on too little information and give a meaningless answer.

```python
    # Start at the Earth's centre with no clock error.
    x, y, z = 0.0, 0.0, 0.0
```
Sets the first guess for the position to the very centre of the Earth: x, y and z all 0.0. The solver does not need to start near the answer, so a fixed starting point keeps it simple and always the same. Without a starting guess there would be nothing to improve.

```python
    clock_m = 0.0  # Store clock error as extra distance for easier maths.
```
The first guess for the clock error is none (0). It is kept in metres, not seconds. A clock error of 1 microsecond makes every distance read about 299.79 m too long, so treating it as "extra metres" lets it be added straight onto a distance. Without it the clock could not be solved.

```python
    steps = [_save_step(x, y, z, clock_m)]
```
Makes a list called `steps` (square brackets make a list) and puts the first guess in it, using the helper from above. The page uses this list to animate how the guess moves. Without it the page could not show the journey.

```python
    converged = False
```
A yes/no flag, "has the guess settled?". It starts as `False` (no) and only becomes `True` if the loop below stops because the corrections got tiny. The page can tell the person if the solver gave up. Without it the caller could not tell a settled answer from a give-up.

```python
    # The first guess is already in steps, so we can add 19 more at most.
    for _ in range(MAX_STEPS - 1):
```
Starts a loop that repeats its indented block. `range(MAX_STEPS - 1)` means `range(19)`, so up to 19 repeats. The first guess is already saved, so 1 + 19 = 20 guesses in total, which is `MAX_STEPS`. The `_` is a name for a counter that nobody needs. Without the loop the guess would never improve.

```python
        errors = []
        changes = []
```
Two empty lists made fresh each round. `errors` will hold one "how wrong are we" number per satellite. `changes` will hold one row of numbers per satellite, saying how the distance reacts to a move. Starting empty each round stops last round's numbers leaking in.

```python
        for satellite, measured_distance in zip(satellites, pseudoranges_m):
```
An inner loop that goes through the satellites one at a time. `zip` walks the two lists side by side, so each turn gives one satellite and its own measured distance. Without `zip` the solver would not know which distance belongs to which satellite.

```python
            # Find the difference between the satellite and our guess.
            dx = x - satellite["x_m"]
            dy = y - satellite["y_m"]
            dz = z - satellite["z_m"]
```
For this satellite, finds the gap between our guessed position and the satellite along each direction. `satellite["x_m"]` reads the labelled value `x_m` from the satellite's dictionary. Note the order is guess minus satellite. Worked example: guess (0, 0, 0), satellite at (20,000,000, 10,000,000, 10,000,000) metres gives dx = 0 - 20,000,000 = -20,000,000, dy = -10,000,000, dz = -10,000,000. Without these gaps no distance can be worked out.

```python
            # Use Pythagoras to find their straight-line distance.
            distance = math.sqrt(dx * dx + dy * dy + dz * dz)
```
Pythagoras in three directions: square each gap, add them, take the square root. This is the straight-line distance from our guess to the satellite. Worked example with the gaps above: 20,000,000 squared is 4e14, and the two 10,000,000 squared are 1e14 each, which sum to 6e14. The square root of 6e14 is 24,494,897.43 m, about 24,495 km. Without this the solver cannot tell what distance our guess implies.

```python
            if distance == 0:
```
Checks for the one case that would break the next maths: the guess sits exactly on the satellite, so the distance is 0.

```python
                return {"error": "The guess is exactly on a satellite."}
```
In that case, stop and say so. Without this check, the lines below would divide by 0, which is not allowed and would crash.

```python
            # Compare what we would measure with what we actually measured.
            predicted = distance + clock_m
```
What a perfect receiver at our guess, with our guessed clock error, would measure: the true distance plus the extra distance from the clock. Worked example: distance 24,494,897.43 m and a clock guess of 0 m give 24,494,897.43 m. Without the clock term the solver could not tell a clock error from a wrong position.

```python
            errors.append(measured_distance - predicted)
```
Adds this satellite's error to the `errors` list: what was measured minus what we predicted. A positive number means the real distance is longer than our guess implies. Worked example: if the measured distance is 24,500,000 m, the error is 24,500,000 - 24,494,897.43 = 5,102.57 m. Without this the solver would not know how wrong it is.

```python
            # Find how changing x, y, and z would change the distance.
            row = [dx / distance, dy / distance, dz / distance]
```
Builds one row of the "changes" table (what maths books call the Jacobian). Each number says how much this satellite's distance changes if we move the guess by 1 m in that direction. For a straight-line distance that is simply the gap divided by the distance, a number between -1 and 1. Worked example with the gaps above: -20,000,000 / 24,494,897.43 = -0.8165, -10,000,000 / 24,494,897.43 = -0.4082, and the same -0.4082 for z. So the row is [-0.8165, -0.4082, -0.4082]. Moving 1 m in the +x direction (towards the satellite) shortens the distance by about 0.8165 m, so the number is negative. Without this the solver would not know which way to move.

```python
            if solve_clock:
```
Only when the clock is also being solved for does the row need an extra number.

```python
                # Clock error adds the same extra distance for every satellite.
                row.append(1.0)
```
Adds a fourth number, 1.0, to the end of the row. Adding 1 m to the clock error adds exactly 1 m to every predicted distance, whichever satellite it is, so its effect is always 1. Worked example: the row becomes [-0.8165, -0.4082, -0.4082, 1.0]. In trusted mode this line is skipped, so rows keep three numbers. Without it the clock could not be found.

```python
            changes.append(row)
```
Adds this satellite's row to the `changes` list. After the inner loop, `changes` has one row per satellite and `errors` has one number per satellite, in the same order.

```python
        # Find the small movement that best reduces all the errors.
        correction, _, rank, _ = np.linalg.lstsq(changes, errors, rcond=None)
```
The key step: least squares. The idea: we want a move that fixes every satellite's error at once, but the errors disagree a little, so one perfect move may not exist. Least squares finds the move whose leftover errors, squared and added up, are as small as possible. `np.linalg.lstsq` hands back four things; we keep two (the `_` names mean "ignore this"): `correction` (the move) and `rank` (how many of the unknowns the satellites can actually pin down). `rcond=None` just asks numpy to use its normal default setting.

Small worked example with made-up numbers: two unknowns and three equations, `changes` = [[1, 0], [0, 1], [1, 1]] and `errors` = [1, 2, 2.9]. The first row says the first unknown should be 1, the second says the second should be 2, the third says they should sum to 2.9, and 1 + 2 = 3 does not quite match 2.9. Least squares gives [0.9667, 1.9667]: it spreads the 0.1 disagreement across the three equations. For the real case, there is one row per satellite and the unknowns are x, y, z (and the clock). Without this line there would be no way to turn the errors into a move.

```python
        if rank < needed:
```
Checks the rank. If `rank` is lower than the number of unknowns, the satellites cannot pin them all down. Worked example: two rows [1, 0] and [2, 0] give rank 1 for 2 unknowns, since both only say something about the first unknown. Real examples are satellites all in one line or on one flat sheet.

```python
            return {"error": "These satellites cannot give one clear position."}
```
In that case, stop and report it, because the answer would not be unique. Without the check, the solver would return a position that looks fine but is only one of many equally good ones.

```python
        # Improve our guessed position.
        x += float(correction[0])
        y += float(correction[1])
        z += float(correction[2])
```
Moves the guess by the correction. `+=` means "add to what is already there". `correction[0]`, `[1]` and `[2]` are the first three numbers of the correction (counting in Python starts at 0): the moves in x, y and z. `float(...)` turns each back into an ordinary number. Worked example: x is 0.0 and the x correction is 1,500,000.0, so x becomes 1,500,000.0. Without these lines the guess would never move.

```python
        if solve_clock:
            clock_m += float(correction[3])
```
When the clock is being solved for, the fourth number of the correction is the change to the clock error, in metres, and it is added to `clock_m` the same way. In trusted mode the correction has only three numbers, so this line is skipped, which also avoids a crash from reading a fourth number that is not there. Without it the clock error would stay at 0.

```python
        # Save every new guess, including the final one.
        steps.append(_save_step(x, y, z, clock_m))
```
Saves the improved guess at the end of the `steps` list, so the page can replay the journey. It is saved before the stop check, so the final guess is always included. Without it the page would only see the first guess.

```python
        # Stop if the position and clock corrections are tiny (under 1 mm).
        if np.linalg.norm(correction) < STOP_WHEN_CHANGE_IS_SMALLER_THAN:
```
Checks whether the guess has settled. `np.linalg.norm` gives the overall size of the correction (every number squared, added, then square-rooted, like Pythagoras for a longer list of numbers). It is compared with 0.001 m. Note the size mixes the position moves and the clock move, all in metres. Worked example: a correction of [0.0003, 0.0004, 0, 0] has size sqrt(0.0003 squared + 0.0004 squared) = 0.0005 m, which is under 0.001, so we stop. A correction of [0.5, 0.4, 0.2, 0.1] has size 0.678 m, so we go round again. A correction of exactly 0.001 does not count, because the test is "smaller than".

```python
            converged = True
            break
```
When settled, record that fact (`converged = True`) and leave the loop at once (`break`). Without `converged = True` the caller could not tell a settled answer from a give-up. Without `break` the loop would carry on pointlessly.

```python
    return {
        "x_m": float(x),
        "y_m": float(y),
        "z_m": float(z),
        "clock_error_s": float(clock_m / SPEED_OF_LIGHT_M_PER_S),
        "converged": converged,
        "steps": steps,
    }
```
Hands back the final answer as a dictionary, in the shape promised by `docs/interface.md`: the position in metres, the clock error in seconds (converted with the same division as in the helper), the `converged` flag, and the whole `steps` list. This runs when the loop ends, whether it settled or ran out of tries; in the second case `converged` is still `False`. In trusted mode `clock_m` never changes, so `clock_error_s` is 0.0. Without it the caller would get nothing back.
