# constants.py, line by line

Source: `mechanism/constants.py`

## What this file is for
This file holds four fixed numbers that the rest of the mechanism needs: how fast light travels, how big the Earth is, how high the GPS satellites orbit, and how fast satellite clocks drift because of relativity. Each number is written once here so every other file uses the same value. It does no work itself: it only names numbers.

## Which files it talks to
- `mechanism/solver.py`: uses `SPEED_OF_LIGHT_M_PER_S` to turn the clock error from metres into seconds.
- `mechanism/scenario.py`, `mechanism/mapview.py`, `mechanism/relativity.py`: use the speed of light to switch between seconds and metres.
- `mechanism/coords.py`: uses `EARTH_RADIUS_M` and `GPS_ORBIT_RADIUS_M` to place the ground and the satellites.
- `mechanism/relativity.py`: uses `RELATIVITY_DRIFT_S_PER_DAY`.
- It imports nothing. The numbers come from `docs/facts.md`, the project's list of checked facts.

## In three lines
1. A "constant" is a name for a number that never changes while the program runs.
2. The name says the unit (`_M_` is metres, `_S_` is seconds), so nobody mixes them up.
3. Change a number here and every file that uses it changes with it.

New to code? See [how to read code](../how-to-read-code.md).

## The code, line by line

```python
# Physical constants used by the mechanism. Units are in the names.
```
A comment: a note for people that the computer ignores (it starts with `#`). It says these are real-world fixed numbers, and that the unit is spelled out in each name. Without it nothing breaks; readers just lose a hint.

```python
SPEED_OF_LIGHT_M_PER_S = 299_792_458
```
Creates a name, `SPEED_OF_LIGHT_M_PER_S`, and sets it to 299,792,458. Read the name as "metres per second". The underscores inside the number are only for reading ease (like commas) and the computer ignores them. Radio signals from satellites travel at this speed, so distance = speed x travel time. The solver also uses it to convert a clock error: a clock that is 1 microsecond (0.000001 s) off adds 0.000001 x 299,792,458 = 299.79 m of apparent distance. Without this line, every file that imports it would fail to start.

```python
# Sphere model of the Earth: mean radius R1 of GRS 80 (docs/facts.md row 33).
EARTH_RADIUS_M = 6_371_008.7714
```
The comment says where the number comes from: the Earth is treated as a perfect ball, with the average radius of a standard Earth model (GRS 80). The line names that radius `EARTH_RADIUS_M`: 6,371,008.7714 metres, about 6,371 km. `coords.py` uses it to turn a latitude and longitude into a point in space. Without it, the receiver could not be placed on the ground.

```python
# GPS orbit radius from the Earth's centre: nominal semi-major axis 26,559.7 km (docs/facts.md row 3).
GPS_ORBIT_RADIUS_M = 26_559_700.0
```
The comment explains that GPS satellites circle at 26,559.7 km from the Earth's centre (not from the ground). The line stores that as metres: 26,559,700.0. Worked example: straight above the receiver a satellite is 26,559,700.0 - 6,371,008.7714 = 20,188,691.2286 m away, about 20,189 km. `coords.py` uses this to put satellites on their orbit. Without it the satellites would have no place to be.

```python
# Satellite clocks gain about 38 microseconds a day from relativity (docs/facts.md row 27).
RELATIVITY_DRIFT_S_PER_DAY = 38e-6
```
The comment says that, if uncorrected, a satellite clock gains about 38 microseconds a day because of relativity. The line stores it as seconds per day. `38e-6` means 38 x 10^-6, which is 0.000038 s. Worked example: one day of drift, times the speed of light, is 0.000038 x 299,792,458 = 11,392.1 m, so after one day every distance would be wrong by about 11.4 km. `relativity.py` uses it to show that drift. Without it, the relativity part of the page could not compute anything.
