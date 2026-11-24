# scenario.py, line by line

Source: `mechanism/scenario.py`

If you have never read code, start with [how to read code](../how-to-read-code.md).

## What this file is for
A real phone measures how long each satellite signal took to arrive, and turns that into a distance. This file makes up those measured distances, so the rest of the page has something to work on. It starts from the true straight-line distance to each satellite, adds the effect of the phone's clock being wrong, and adds a little random noise.

The measured distance is called a pseudorange ("pseudo" because it is not the true distance). Nothing here is prepared in advance: every number is worked out from the positions and settings that are passed in.

## Which files it talks to
- `mechanism/constants.py`: gives `SPEED_OF_LIGHT_M_PER_S`, needed to turn a clock error in seconds into metres.
- `numpy` and `math` (outside libraries): the random number maker and the square root.
- `mechanism/relativity.py`: calls `make_pseudoranges` once for each hour value in its `hours_list`.
- `web/first-screen.js` and `web/step-geometry.js`: call `scenario.make_pseudoranges` through the Python bridge.
- `mechanism/solver.py`: receives the list this file makes and works backwards from it to a position.
- `tests/test_scenario.py` and `tests/test_mapview.py`: check and use it.
- `docs/interface.md`: the contract that fixes its name, inputs and the shape of its answer.

## In three lines
1. Reject input that makes no sense (no satellites, negative noise) with an error sentence.
2. Turn the clock error from seconds into metres, and make one random noise number per satellite, repeatable by a seed.
3. For each satellite, add straight-line distance, clock effect and noise, and return the list in the same order.

## The code, line by line

```python
"""Make the distances a phone would measure to satellites."""
```
A line in triple quotes at the top of a file is a description of the file (a "docstring"). The computer does not act on it; it is for people. Nothing breaks without it, but the file would be harder to understand.

```python
import math

import numpy as np
```
`import` brings in tools written by other people. `math` has the square root. `numpy` (nicknamed `np`) makes lists of random numbers. Without these lines, `math.sqrt` and `np.random` below would not exist.

```python
from mechanism.constants import SPEED_OF_LIGHT_M_PER_S
```
Fetches one named number from our own file `mechanism/constants.py`: the speed of light, 299 792 458 metres per second. The name ends in `_M_PER_S` so the unit is always visible. Keeping it in one file means every part of the code uses the same value.

```python
def make_pseudoranges(receiver, satellites, clock_error_s, noise_m=0, seed=0):
```
Starts the recipe `make_pseudoranges`. It takes five things:
- `receiver`: where the phone really is (a labelled box with `x_m`, `y_m`, `z_m` in metres);
- `satellites`: a list of such boxes, one per satellite;
- `clock_error_s`: how far ahead the phone's clock is, in seconds;
- `noise_m`: how big the random noise is, in metres. The `=0` means "if nobody says, use 0", so noise is off unless asked for;
- `seed`: a whole number that fixes the random noise, so the same seed always gives the same noise. Default 0.

```python
    """Return one measured distance (metres) per satellite, in the same order.

    measured = true straight-line distance + clock error effect + random noise
    """
```
Another description, this time of the recipe. The second line is the formula in words, and it is the heart of the file. Measured distance equals true distance plus the clock effect plus the noise. The order matters: answer number 1 belongs to satellite 1, and so on, so other code can match them up.

Worked example: true distance 5 000 000 m, clock effect 299.79 m, noise 0.38 m. Measured = 5 000 000 + 299.79 + 0.38 = 5 000 300.17 m. See the lines below for where each number comes from.

```python
    if not satellites:
        return {"error": "At least one satellite is needed."}
```
`not satellites` is true when the list is empty. Then the recipe returns a labelled box with an error sentence, which is the way this project reports a problem (`docs/interface.md`). Without it, an empty list would silently give an empty answer.

```python
    if noise_m < 0:
        return {"error": "Noise must not be negative."}
```
A noise size below zero is meaningless (a spread cannot be negative), and numpy would crash on it. So the recipe stops with a sentence instead.

```python
    # A clock that runs ahead makes every distance too long by the same amount.
    clock_effect_m = clock_error_s * SPEED_OF_LIGHT_M_PER_S
```
The idea: the phone works out distance as "time the signal took" times "speed of light". If the phone's clock is ahead by a little, every time looks a little too long, so every distance comes out too long by the same amount, whichever satellite it is. So the clock error in seconds, multiplied by the speed of light, gives the extra distance in metres.

Worked example: a clock 1 microsecond ahead (0.000001 s, the value the DOP step of the page uses). 0.000001 times 299 792 458 = 299.792458 metres. One millionth of a second is about 300 metres of distance, which is why clocks matter so much.

```python
    # The same seed always gives the same noise.
    rng = np.random.default_rng(seed)
    noise = rng.normal(0.0, noise_m, len(satellites))
```
The first line is a reminder of why there is a seed. `np.random.default_rng(seed)` makes a random number generator that starts from `seed`. Two generators with the same seed produce the same numbers in the same order, so a demo can be repeated exactly. Without a seed, the page would show different noise on every click.

`rng.normal(0.0, noise_m, len(satellites))` asks for a list of random numbers that cluster around 0.0 and spread out by about `noise_m` (a "normal" or bell-curve spread); the last part says how many, one per satellite. They can be positive or negative. If `noise_m` is 0 they are all exactly 0.

Worked example: with seed 0 and noise_m 3, the first satellite gets noise 0.377 m (worked out by running the code).

```python
    pseudoranges = []
    for satellite, noise_value in zip(satellites, noise):
```
`pseudoranges = []` is an empty list that will collect the answers. `zip(satellites, noise)` pairs the first satellite with the first noise number, the second with the second, and so on. `for ... in ...:` then repeats the indented lines below once per pair, calling the satellite `satellite` and its noise `noise_value`. Without the pairing, each satellite would not get its own noise number.

```python
        # Straight-line distance from Pythagoras in three dimensions.
        true_distance = math.sqrt(
            (satellite["x_m"] - receiver["x_m"]) ** 2
            + (satellite["y_m"] - receiver["y_m"]) ** 2
            + (satellite["z_m"] - receiver["z_m"]) ** 2
        )
```
This is the straight-line distance. Pythagoras tells us a right-angled triangle's long side is the square root of the two short sides squared and added. In three dimensions there are three short sides: how far apart the two points are in x, in y and in z. `satellite["x_m"] - receiver["x_m"]` is the gap in x; `** 2` means "times itself". The three squares are added, and `math.sqrt` takes the square root. The brackets at the end of the first and last line let the sum be split across lines for easier reading. Without this line there would be no true distance to start from.

Worked example: phone at (0, 0, 0), satellite at (3 000 000, 4 000 000, 0). Gaps: 3 000 000, 4 000 000, 0. Squares: 9 000 000 000 000, 16 000 000 000 000, 0. Sum: 25 000 000 000 000. Square root: 5 000 000 metres. (The numbers are made up to make the square root easy. Real satellites are about 20 000 km away.)

```python
        pseudoranges.append(float(true_distance + clock_effect_m + noise_value))
```
This is the formula from the description, now as code: true distance, plus clock effect, plus this satellite's noise. `float(...)` turns the result into an ordinary decimal number, so the page can read it. `.append` puts it at the end of the list, so the answers stay in the same order as the satellites.

Worked example, same satellite as above, clock error 1 microsecond, noise 3 m, seed 0: 5 000 000 + 299.792458 + 0.377 = 5 000 300.170 m (running the code prints 5 000 300.1696...). Without noise, the answer is 5 000 299.792458 m.

```python
    return pseudoranges
```
After the loop has dealt with every satellite, the finished list is handed back to whoever asked. Without it, the recipe would calculate everything and then give nothing back.
