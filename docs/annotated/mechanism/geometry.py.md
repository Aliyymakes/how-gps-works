# geometry.py, line by line

Source: `mechanism/geometry.py`

If you have never read code, start with [how to read code](../how-to-read-code.md).

## What this file is for
Some satellite layouts give a good position and some give a bad one, even when every measurement is equally good. This file measures how bad a layout is. The number it makes is called DOP (dilution of precision): the factor by which the layout multiplies the measurement errors. Lower is better.

It looks only at the directions from the phone to the satellites. It does not use any distances or any clock.

## Which files it talks to
- `numpy` (outside library): does the arrays, the "transpose" and the "inverse" in this file.
- `mechanism/solver.py`: no direct link. The solver finds the position; this file only says how well a layout can do that.
- `web/step-geometry.js`: calls `geometry.dop` through the Python bridge, once for the spread-out satellites and once for the bunched ones.
- `tests/test_geometry.py`: checks `dop`.
- `docs/interface.md`: the contract that fixes the name `dop`, its inputs and the shape of its answer.

## In three lines
1. `make_table` turns each satellite into one row: three numbers for its direction from the phone, then a 1 for the clock.
2. `dop` multiplies that table by its own flipped copy and inverts the result. Its diagonal says how much each unknown (x, y, z, clock) is magnified.
3. Square roots of sums of the diagonal give GDOP, PDOP and TDOP, or an error sentence if the layout cannot be worked out.

## The code, line by line

```python
# Dilution of precision (DOP): how much the satellites' layout multiplies errors.
import numpy as np
```
The first line is a comment (a note for people; the computer ignores it). It names the idea of the file. `import numpy as np` loads a maths library and gives it the short name `np`. Without it, none of the table and inverse maths below would exist.

```python
KEYS = ("x_m", "y_m", "z_m")
```
`KEYS` is a fixed list of the three names a point must have: x, y and z, each in metres (`_m`). The page sends points as labelled boxes, for example `{"x_m": 3, "y_m": 4, "z_m": 0}`. Keeping the names in one place means a typo can only happen once. Without it, the names would be repeated in the code below.

```python
def read_point(point):
    # Turn {"x_m", "y_m", "z_m"} into [x, y, z]. Returns None if it is not a valid point.
    if not isinstance(point, dict):
        return None
```
`def read_point(point):` starts a recipe called `read_point`. It is given one thing, `point`. The comment says what the recipe does: turn the labelled box into a plain list of three numbers, or give back `None` ("nothing") if the input is not a proper point.

The `if` line asks: is `point` not a labelled box (a `dict`)? If it is something else, such as a number or a piece of text, the recipe stops at once with `return None`. Without this check, the lines below would crash on bad input instead of answering politely.

```python
    try:
        return np.array([float(point[key]) for key in KEYS])
    except (KeyError, TypeError, ValueError):
        return None
```
`try:` means "attempt this, and be ready for it to go wrong". Inside it, the recipe takes each name in `KEYS`, looks it up in the box (`point[key]`), turns it into a decimal number with `float(...)`, and packs the three numbers into one array. For `{"x_m": 3, "y_m": 4, "z_m": 0}` the answer is `[3.0, 4.0, 0.0]`.

`except (...)` lists the three ways this can go wrong: a name is missing (`KeyError`), a value is the wrong kind of thing (`TypeError`), or text that is not a number such as `"abc"` (`ValueError`). In each case the recipe returns `None`. Without the `try` and `except`, one bad point would stop the whole program with an ugly failure message.

```python
def make_table(receiver, satellites):
    # One row per satellite: unit direction from receiver to satellite, then a 1 for the clock.
    # Returns (table, None) or (None, error sentence).
    start = read_point(receiver)
```
This starts the main recipe, `make_table`. It gets the receiver (the phone) and the list of satellites. The comments say what comes out: a table with one row per satellite, where each row is the direction from the phone to that satellite (an arrow of length 1) followed by a 1 for the clock. It always returns a pair: either (table, nothing) or (nothing, error sentence). The caller checks which half is filled in.

`start = read_point(receiver)` turns the phone's labelled box into three numbers and calls them `start`.

```python
    if start is None:
        return None, "The receiver must have numbers x_m, y_m and z_m."
```
If `read_point` gave back `None`, the phone's point was bad. The recipe stops and returns the pair (nothing, sentence). The sentence is shown to the user as it is, so it is written in plain words. Without this check, the maths further down would meet `None` and crash.

```python
    if not isinstance(satellites, (list, tuple)) or len(satellites) < 4:
        return None, "At least 4 satellites are needed to work out DOP."
```
Two checks joined by `or`: the satellites must be a list (or a tuple, which is a list that cannot be changed), and there must be at least 4 of them. The reason is in the maths below: the table has 4 columns (x, y, z, clock), so with fewer than 4 rows the table cannot pin down 4 unknowns. If either check fails, the recipe returns an error sentence. Without it, the inverse below would fail on a table that can never be inverted.

```python
    rows = []
    for satellite in satellites:
        end = read_point(satellite)
        if end is None:
            return None, "Every satellite must have numbers x_m, y_m and z_m."
```
`rows = []` makes an empty list where finished rows will be put. `for satellite in satellites:` repeats the indented lines once for each satellite, one after another. Inside, `end = read_point(satellite)` reads that satellite's point. If it is bad, the whole recipe stops with a sentence. One bad satellite spoils the table, so it is better to stop than to skip it quietly and give a wrong answer.

```python
        arrow = end - start
        distance = np.linalg.norm(arrow)
```
`end - start` subtracts the phone's numbers from the satellite's, one by one. The result, `arrow`, points from the phone to the satellite. `np.linalg.norm(arrow)` is the length of that arrow, worked out by Pythagoras in three dimensions: the square root of x squared plus y squared plus z squared. Without the length, the arrow could not be shrunk to "length 1" below.

Worked example: phone at (0, 0, 0), satellite at (3 000 000, 4 000 000, 0) metres. The arrow is (3 000 000, 4 000 000, 0). Its length is the square root of 9 000 000 000 000 + 16 000 000 000 000 = 25 000 000 000 000, which is 5 000 000 metres.

```python
        if not np.isfinite(distance) or distance == 0:
            return None, "A satellite is at the same spot as the receiver."
```
Two ways the length can be useless. `np.isfinite` is false for infinity or "not a number" (which can come from absurdly large input). A length of exactly 0 means the satellite is on top of the phone, and in the next line we would divide by zero, which has no answer. In both cases the recipe stops with a sentence. Without this check, the next line would fill the table with nonsense or crash.

```python
        rows.append(list(arrow / distance) + [1.0])
```
This is the key line of the table. `arrow / distance` divides each of the three numbers by the length, so the arrow now has length 1: it says only which way to look, not how far. `list(...)` turns it into a plain list. `+ [1.0]` sticks a fourth number, 1.0, on the end: that is the clock column. `rows.append(...)` puts this finished row at the bottom of the list.

Worked example: (3 000 000, 4 000 000, 0) divided by 5 000 000 is (0.6, 0.8, 0). With the clock 1, the row is [0.6, 0.8, 0, 1]. Check: 0.6 squared plus 0.8 squared is 0.36 + 0.64 = 1, so the arrow really has length 1. The 1 is there because a clock error pushes every measured distance the same amount, whatever the direction.

```python
    return np.array(rows), None
```
Back outside the loop, all the rows are packed into one table (`np.array(rows)`: N rows and 4 columns for N satellites) and returned together with `None` in the second place, meaning "no problem".

Worked example (the page's "spread" satellites, from `web/step-geometry.js`: azimuth 30, 90, 210, 330 degrees and elevation 80, 20, 20, 20 degrees). Seen from the phone, with x east, y north and z up, the table is, rounded to three places:

```text
 0.087   0.150   0.985   1
 0.940   0.000   0.342   1
-0.470  -0.814   0.342   1
-0.470   0.814   0.342   1
```
The first row is the satellite almost overhead (z, the "up" number, is 0.985). The other three are low in the sky, spread around. (DOP only uses directions, so measuring them in a local east-north-up frame instead of the Earth-centred frame gives the same DOP.)

```python
def dop(receiver, satellites):
    table, problem = make_table(receiver, satellites)
    if problem:
        return {"error": problem}
```
`dop` is the recipe the page calls. It asks `make_table` for the table. Because `make_table` returns a pair, `table, problem = ...` catches both halves at once. `if problem:` is true when there is an error sentence; then `dop` hands back a labelled box `{"error": ...}` and stops. The page checks for the label `error`. This follows the contract in `docs/interface.md`. Without this, bad input would carry on into the maths.

```python
    # Transpose times table, then invert. If the layout is flat or bunched, this cannot be inverted.
    try:
        inverse = np.linalg.inv(table.T @ table)
    except np.linalg.LinAlgError:
        return {"error": "These satellites are laid out so that DOP cannot be worked out."}
```
This is the maths line. Take the table, call it H. `table.T` is H flipped so rows become columns (the "transpose", written Hᵀ). `@` means matrix multiplication. So `table.T @ table` is HᵀH. The table has 4 columns, so HᵀH is a small square table of 4 rows by 4 columns, one row and one column for each unknown: x, y, z, clock. Each entry says how much two columns of directions "overlap".

`np.linalg.inv(...)` then finds the inverse, written (HᵀH)⁻¹. The inverse of a table is like "one divided by" a number: multiplying a table by its inverse gives the "do nothing" table. The idea behind DOP: if every measurement is off by an error of about 1 metre, the position unknowns are off by an amount set by the diagonal of this inverse. A layout where the satellites look alike makes HᵀH nearly impossible to invert, so the inverse has huge numbers: errors are magnified.

Worked example, spread satellites from above. HᵀH comes out (rounded) as:

```text
 1.332  0.013  0.086  0.087
 0.013  1.347  0.148  0.150
 0.086  0.148  1.321  2.011
 0.087  0.150  2.011  4.000
```
Check the top-left number: it is the sum of each row's first number squared, 0.087 squared + 0.940 squared + 0.470 squared + 0.470 squared = 0.0076 + 0.8836 + 0.2209 + 0.2209, about 1.333. The bottom-right 4.000 is 1 + 1 + 1 + 1, one for each clock entry. Its inverse is (rounded):

```text
 0.755   0.000  -0.102   0.035
 0.000   0.755  -0.177   0.060
-0.102  -0.177   3.282  -1.641
 0.035   0.060  -1.641   1.072
```
The diagonal (top-left to bottom-right) is 0.755, 0.755, 3.282, 1.072. Up (z) is the worst because the satellites are never below the phone, so only a bit of the geometry pins the height down.

The `try` / `except` is the safety net. If the table is "flat" (for example all four satellites at the same height in the sky, as in my test with satellites at (10 000 000, 0, 10 000 000), (-10 000 000, 0, 10 000 000), (0, 10 000 000, 10 000 000) and (0, -10 000 000, 10 000 000): every z number is 0.7071 and the clock column is all 1, so one column is always 0.7071 times another) the inverse does not exist and numpy raises a `LinAlgError`. The `except` catches it and returns the sentence. Without the safety net, a bad layout would crash the page.

```python
    diagonal = np.diag(inverse)
```
`np.diag` picks out the diagonal of the table: the four numbers from top-left to bottom-right. Only these matter for DOP, because each one is the "magnification" for one unknown (x, y, z, clock). The numbers off the diagonal say how errors in one unknown drag another along, and DOP ignores them.

```python
    if not np.all(np.isfinite(diagonal)) or np.any(diagonal < 0):
        return {"error": "These satellites are laid out so that DOP cannot be worked out."}
```
A second safety net, for cases that technically invert but give nonsense. `np.all(np.isfinite(diagonal))` is true when all four numbers are ordinary numbers. `not` flips it, so the first half is true if any is infinity or "not a number". `np.any(diagonal < 0)` is true if any of the four is below zero. A true inverse of this kind of table can never have a negative diagonal, so a negative one means rounding has broken the maths for a very bad layout. In either case the recipe returns the same sentence as before. Without this, the next lines would take the square root of a negative number.

```python
    # GDOP: all four diagonal entries. PDOP: the first three (position). TDOP: the last (clock).
    return {
        "gdop": float(np.sqrt(diagonal.sum())),
        "pdop": float(np.sqrt(diagonal[:3].sum())),
        "tdop": float(np.sqrt(diagonal[3])),
    }
```
The comment names the three answers. `diagonal.sum()` adds all four numbers; `diagonal[:3]` means "the first three"; `diagonal[3]` is the fourth, counting from 0. `np.sqrt` is the square root and `float` turns the result into an ordinary number. The three answers are put in a labelled box with the names the contract promises:
- GDOP uses all four entries: the overall quality (position and clock together).
- PDOP uses only x, y and z: the position part. The page's readout shows this one.
- TDOP uses only the clock entry.

Worked example, spread satellites, diagonal 0.755, 0.755, 3.282, 1.072 (these are rounded; the code uses the full numbers):
- GDOP: square root of (0.755 + 0.755 + 3.282 + 1.072) = square root of 5.864 = 2.42.
- PDOP: square root of (0.755 + 0.755 + 3.282) = square root of 4.792 = 2.19.
- TDOP: square root of 1.072 = 1.04.

The code gives 2.42, 2.19 and 1.04. So a measurement error of 3 metres (the page's noise) turns into a position error of roughly 3 times 2.19, about 6.6 metres.

Now the bunched set from `web/step-geometry.js` (azimuth 40, 44, 48, 50 and elevation 44, 48, 52, 46 degrees). All four arrows point nearly the same way, the rows of the table are nearly the same, and the inverse blows up. The diagonal is about 26 606, 27 358, 64 874 and 117 982, giving GDOP 486.6, PDOP 344.7 and TDOP 343.5. The same 3 metres of noise now becomes about 3 times 344.7, roughly 1 034 metres. That is the lesson of the page.
