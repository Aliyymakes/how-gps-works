# mapview.py, line by line

Source: `mechanism/mapview.py`

## What this file is for
The page shows a small flat map of the ground around the phone, 2 kilometres wide by default. Each satellite gives the phone one measured distance, and that distance draws one circle on the ground (the page calls the part of a circle that crosses the map a "distance line"). This file works out those circles, in metres east and north of the true phone position, ready for the page to draw. It also converts a single point into the same east, north, up metres.

## Which files it talks to
- `mechanism/constants.py`: gives the speed of light, used to turn a clock error in seconds into metres.
- `mechanism/coords.py`: gives the phone's x, y, z position (`latlon_to_xyz`) and the east, north and up directions (`_local_directions`).
- The page code in `web/` receives the output (see `docs/interface.md`: lists with `id`, `points` and `inside`).
- Basics of reading code are in [how to read code](../how-to-read-code.md).

## In three lines
1. Every satellite position is turned into east, north, up metres around the true phone (`to_local`, `_local`).
2. A measured distance is a sphere around the satellite; where it cuts the flat ground is a circle (`distance_lines`).
3. The circle is sampled as a list of points, and only the points inside the map square are kept (`_circle_points`).

## The code, line by line

```python
"""Turn satellites and measured distances into lines on a flat local ground map.
```
The first line of a description for people. Python does not run it as a step.

```python
The map is centred on the true receiver. East and north are in metres, up is the height.
"""
```
The rest of the description. Point (0, 0) on the map is the true phone position. East is to the right, north is up the page, and "up" is the height above the ground. The closing `"""` ends the description.

```python
import math
```
Python's built-in maths toolbox (square roots, sine, cosine, and so on). Without it, every `math.` below would fail.

```python
from mechanism.constants import SPEED_OF_LIGHT_M_PER_S
```
Brings in one fixed number: 299,792,458 metres per second. Without it the clock error could not be turned into a distance.

```python
from mechanism.coords import _local_directions, latlon_to_xyz
```
Brings in two helpers from `coords.py`: one finds the phone's x, y, z, the other finds the east, north and up arrows at the phone. This file reuses them so the maths for positions lives in one place only.

```python
# Sampling more densely than this is pointless; the line is then treated as missing the square.
_MAX_SAMPLES = 20_000
```
A limit. A circle is drawn as a list of points ("samples"). If we have to ask for more than 20,000 points, something is wrong (for example the line barely touches the square), so we stop and treat the line as not on the map. The `_` in the underscore number is only a visual comma: 20_000 is 20000. Without a limit, the later loop could keep doubling forever.

```python
_MIN_POINTS = 10
```
A line must keep at least 10 points inside the square to count as visible. Fewer than that is too short to draw.

```python
def _dot(a, b):
    return sum(x * y for x, y in zip(a, b))
```
The "dot product" of two arrows: multiply their matching parts and add the results. If one arrow has length 1, the answer says how far the other arrow reaches along it. Example: (3, 4, 0) and (1, 0, 0) give 3 x 1 + 4 x 0 + 0 x 0 = 3, so (3, 4, 0) reaches 3 units along the first axis. `zip(a, b)` pairs the first with the first, second with second, and so on.

```python
def _local(receiver, directions, point):
    """East, north, up (metres) of a point, given the receiver's xyz and its local directions."""
```
Starts a helper that moves a point into the phone's own frame: how many metres east, north and up of the phone it is.

```python
    # The difference from the receiver, as an arrow in x, y, z.
    arrow = (point["x_m"] - receiver["x_m"], point["y_m"] - receiver["y_m"], point["z_m"] - receiver["z_m"])
```
Subtract the phone's position from the point's position, part by part, to get the arrow from the phone to the point. Example: a point at (10, 20, 30) seen from a phone at (4, 5, 6) gives the arrow (6, 15, 24). Without this step we would measure from the centre of the Earth rather than from the phone.

```python
    # Each local axis is a unit arrow; the dot product is how far the arrow reaches along it.
    east, north, up = directions
```
`directions` holds the three arrows from `_local_directions`. This line gives each one its own name.

```python
    return _dot(arrow, east), _dot(arrow, north), _dot(arrow, up)
```
Measure how far the arrow reaches along east, then north, then up. This turns "arrow in the Earth's x, y, z" into "arrow in the phone's east, north, up". Example: if the arrow is (0, 3, 4) and north is (0, 1, 0) and up is (0, 0, 1), then north = 3 and up = 4. The order east, north, up is relied on by the callers.

```python
def _is_point(point):
    """True when the point is a dict with numbers for x_m, y_m and z_m."""
```
A checker: is this thing a proper point? The page could send something odd, and this keeps odd input from crashing the code.

```python
    return isinstance(point, dict) and all(
        isinstance(point.get(key), (int, float)) for key in ("x_m", "y_m", "z_m")
    )
```
The answer is yes only if both hold: the thing is a dictionary (`isinstance(point, dict)`), and for each of the three keys `x_m`, `y_m`, `z_m` the value is a number (`int` or `float`). `.get(key)` gives nothing if the key is missing, and nothing is not a number, so a missing key makes the answer no. Because of `and`, if it is not a dictionary the second check is never run, so `.get` is never called on something that cannot do it. Without this, a bad point would crash with a confusing error.

```python
def to_local(receiver_lat_deg, receiver_lon_deg, point):
    """Return where a point is relative to the true receiver, in east, north, up metres."""
```
The public function for one point. Give it the phone's latitude and longitude and a point in x, y, z; it returns east, north, up metres from the phone.

```python
    if not _is_point(point):
        return {"error": "A point needs numbers for x_m, y_m and z_m."}
```
If the point is not valid, stop and return an error message in the same style as everywhere else in the project.

```python
    receiver = latlon_to_xyz(receiver_lat_deg, receiver_lon_deg)
```
The phone's position in x, y, z. For the page's receiver (latitude -6.2, longitude 106.8) that is (-1,830,653.6, 6,063,417.1, -688,064.8) m.

```python
    if "error" in receiver:
        return receiver
```
`latlon_to_xyz` returns an error bundle if the latitude is out of range. If it did, pass that error straight on. Without this line the code below would try to read x, y, z from an error message.

```python
    directions = _local_directions(receiver_lat_deg, receiver_lon_deg)
```
The east, north and up arrows at the phone.

```python
    east_m, north_m, up_m = _local(receiver, directions, point)
```
Run the point through the helper above and keep the three results under names.

```python
    return {"east_m": float(east_m), "north_m": float(north_m), "up_m": float(up_m)}
```
Hands back a labelled bundle. Worked example: a satellite due north at 45 degrees elevation, from the page's receiver, is at (-6,711,865.9, 22,230,772.3, 12,890,356.3). The result is east about 0, north 15,322,909.75 m, up 15,322,909.75 m. North and up are equal, which matches a 45 degree elevation (equal climb and run). `float(...)` makes them plain decimal numbers.

```python
def _circle_reaches_square(centre_e, centre_n, radius, half_width_m):
    """True when the circle crosses the square: it passes between the square's nearest and farthest points."""
```
A quick test: does this circle touch the map square at all? The square is centred on the phone, with sides of `2 x half_width_m`. The circle edge crosses the square exactly when its radius lies between the distance to the square's nearest point and the distance to its farthest corner.

```python
    # Nearest point of the square to the circle's centre (clamp the centre into the square).
    near_e = min(max(centre_e, -half_width_m), half_width_m)
    near_n = min(max(centre_n, -half_width_m), half_width_m)
```
"Clamp" means: if a number is outside the allowed range, pull it back to the nearest edge of that range. `max(centre_e, -half_width_m)` stops it falling below the left edge, then `min(..., half_width_m)` stops it passing the right edge. Doing this for east and for north gives the point of the square closest to the circle's centre. Example: centre (3000, 0), half width 1000: east clamps to 1000, north stays 0, so the nearest point is (1000, 0).

```python
    nearest = math.hypot(centre_e - near_e, centre_n - near_n)
```
`math.hypot(a, b)` is the length of the slanted side of a right triangle with sides a and b (Pythagoras: the square root of a squared plus b squared). Here it gives the straight-line distance from the circle's centre to that nearest point. Example: hypot(3000 - 1000, 0 - 0) = 2000.

```python
    # Farthest point of the square is one of its corners.
    farthest = math.hypot(abs(centre_e) + half_width_m, abs(centre_n) + half_width_m)
```
The farthest part of a square from any point is a corner. `abs` drops the sign, so we always measure to the corner on the opposite side. Example: hypot(3000 + 1000, 0 + 1000) = hypot(4000, 1000) = 4,123.1.

```python
    return nearest <= radius <= farthest
```
True when the radius sits between nearest and farthest. Example: radius 2500 gives 2000 <= 2500 <= 4123.1, so True. Radius 1000 is below 2000 (circle too small to reach the square), and a circle at the centre with radius 2000 is above the farthest corner (1414.2), so both give False. Without this check we would waste time sampling circles that cannot touch the map.

```python
def _circle_points(centre_e, centre_n, radius, half_width_m, samples):
    """Points of the circle that fall inside the square, sampled only near the square."""
```
Starts the function that makes the points of one circle that are on the map.

```python
    if not _circle_reaches_square(centre_e, centre_n, radius, half_width_m):
        return []
```
If the circle cannot touch the square, return an empty list `[]` straight away. No points means nothing to draw.

```python
    # The angle (seen from the circle's centre) that points at the middle of the square.
    middle_angle = math.atan2(-centre_n, -centre_e)
```
Stand at the circle's centre and look toward the phone's spot (0, 0), the middle of the square. The direction to there is `(-centre_e, -centre_n)`. `atan2` turns that into an angle. Example: centre (3000, 0) means looking at (-3000, 0), which is angle 3.14159 radians (180 degrees, due west). We only need to sample the part of the circle near this angle, not the whole circle.

```python
    # The square fits inside a circle of radius half_width * sqrt(2) around its middle.
    # Seen from the circle's centre, that covers this half-angle (all the way round if the circle is small).
    reach = half_width_m * math.sqrt(2)
```
A square with half-width 1000 has its corners 1000 x 1.41421 = 1,414.2 m from its middle, so the whole square fits inside a circle of that radius. `reach` is that number.

```python
    half_angle = math.pi if reach >= radius else min(math.pi, math.asin(reach / radius) * 1.05)
```
How wide a slice of the circle, either side of `middle_angle`, we need to sample. If the circle is smaller than `reach`, any part of it might be inside, so take the full half-turn (`math.pi`, 180 degrees each side, which is the whole circle). Otherwise, the slice is `asin(reach / radius)`: the largest angle away from `middle_angle` at which a point of the circle can still be within `reach` of the map's middle (whatever the distance between the two centres), so no part of the circle that could land on the map is left out. It is made 5 percent bigger (`* 1.05`) as a safety margin, and never more than `math.pi`. Example: radius 2500 gives asin(1414.2 / 2500) = asin(0.5657) = 0.6013, times 1.05 = 0.6313 radians (36.2 degrees). Sampling only this slice puts all the points near the map instead of wasting them all around a huge circle.

```python
    points = []
```
An empty list that will collect the kept points.

```python
    while samples <= _MAX_SAMPLES:
        points = []
```
Repeat while we have not asked for more than 20,000 samples. Each round starts with an empty list so old results are not mixed with new ones.

```python
        for i in range(samples):
```
Go through `samples` numbers: 0, 1, 2, and so on up to one less than `samples`. Each number `i` is one sample point.

```python
            # Spread the angles evenly across the part of the circle near the square.
            angle = middle_angle - half_angle + 2 * half_angle * i / (samples - 1)
```
Spread the angles evenly from `middle_angle - half_angle` (i = 0) to `middle_angle + half_angle` (the last i). Dividing by `samples - 1` makes the last sample land exactly on the far end. Example: middle angle 3.14159, half angle 0.6313, 40 samples: the first angle is 3.14159 - 0.6313 = 2.5103. This is why `samples` is at least 2: with 1 sample we would divide by zero (the function that calls this checks that).

```python
            east_m = centre_e + radius * math.cos(angle)
            north_m = centre_n + radius * math.sin(angle)
```
A point on a circle is the centre plus radius times cos (for east) and sin (for north) of the angle. Example with the first angle 2.5103: east = 3000 + 2500 x cos(2.5103) = 3000 + 2500 x -0.8072 = 981.9, north = 2500 x sin(2.5103) = 1,475.5.

```python
            # Keep only points inside the square (tiny tolerance for rounding).
            if abs(east_m) <= half_width_m + 1e-6 and abs(north_m) <= half_width_m + 1e-6:
```
Keep the point only if it is within the square: east and north each no more than half-width away from 0. `1e-6` is a millionth of a metre, a cushion so that points exactly on the edge are not lost to tiny rounding errors. In the example above north is 1,475.5, more than 1000, so that first point is dropped. It is on the circle, but off the map.

```python
                points.append([float(east_m), float(north_m)])
```
Keep the point by adding the pair `[east, north]` to the list. `append` adds one item at the end.

```python
        if len(points) >= _MIN_POINTS:
            break
```
After a round, check how many points were kept. If there are at least 10, stop (`break` leaves the loop). That is enough for a line.

```python
        # Too few points landed inside (the line may only clip a corner): sample more densely.
        samples *= 2
```
If too few points were kept, the line only just clips the square. Double the number of samples (`*=` means "multiply and store back") and try again. Example: 40 becomes 80. Without this, thin edge cases would give a line with only a point or two and the page would draw nothing useful. The `while` limit stops the doubling at 20,000.

```python
    return points
```
Returns whatever the last round produced. It can be fewer than 10 points; the caller checks that.

```python
def distance_lines(receiver_lat_deg, receiver_lon_deg, satellites, pseudoranges_m,
                   assumed_clock_error_s, half_width_m=1000, samples=40):
```
The main function of the file. It takes the phone's latitude and longitude, a list of satellite positions, a list of measured distances (one per satellite; "pseudorange" is the name for a distance measured from signal travel time, including the clock error), the clock error to subtract, the map half width (default 1000 m) and how many points per circle to start with (default 40).

```python
    """Return one line per satellite: where its distance sphere cuts the ground plane."""
```
The description: for each satellite, a measured distance means the phone is somewhere on a ball around that satellite; where that ball meets the flat ground is a circle.

```python
    if not satellites:
        return {"error": "At least one satellite is needed."}
```
An empty list counts as "false" in Python, so `not satellites` means "no satellites". With none, there is nothing to draw, so return an error.

```python
    if len(satellites) != len(pseudoranges_m):
        return {"error": "There must be one measured distance for each satellite."}
```
Each satellite needs exactly one measured distance. If the two lists differ in length, the pairing would go wrong, so return an error instead.

```python
    if half_width_m <= 0:
        return {"error": "The map half width must be more than 0 metres."}
```
A map with no width, or a negative width, cannot exist. Refuse it.

```python
    if samples < 2:
        return {"error": "At least 2 samples are needed."}
```
One sample would cause a divide by zero (see `samples - 1` above), and a line needs at least two points anyway.

```python
    if not all(_is_point(satellite) for satellite in satellites):
        return {"error": "Each satellite needs numbers for x_m, y_m and z_m."}
```
`all(...)` is true only if every satellite passes the `_is_point` check. If any one is badly formed, return an error. Without this, one broken satellite would crash the later steps.

```python
    if not all(isinstance(value, (int, float)) for value in pseudoranges_m):
        return {"error": "Each measured distance must be a number."}
```
The same kind of check for the measured distances: every one must be a number.

```python
    receiver = latlon_to_xyz(receiver_lat_deg, receiver_lon_deg)
    if "error" in receiver:
        return receiver
```
Find the phone's x, y, z. If the latitude was out of range, pass the error on, same as in `to_local`.

```python
    directions = _local_directions(receiver_lat_deg, receiver_lon_deg)
```
The east, north and up arrows at the phone. They are worked out once here, since they are the same for every satellite.

```python
    lines = []
```
An empty list that will hold one result per satellite.

```python
    for satellite, pseudorange in zip(satellites, pseudoranges_m):
```
Walk through the satellites and their measured distances together, one pair at a time. Everything indented below runs once per satellite.

```python
        # The satellite in the local frame. The ground plane is up = 0.
        east_m, north_m, up_m = _local(receiver, directions, satellite)
```
Move the satellite into the phone's own east, north, up frame. In this frame the ground is the flat sheet where up is 0. The satellite's `up_m` is how high it is above that sheet.

```python
        # Take off the distance the clock error added, to get the distance the phone believes.
        distance = pseudorange - assumed_clock_error_s * SPEED_OF_LIGHT_M_PER_S
```
The measured distance includes an error because the phone's clock is off. Light travels about 299,792,458 m each second, so a clock error of `t` seconds adds `t x 299,792,458` metres. Example: a clock error of 1 microsecond (0.000001 s) adds 299.792 m. If the measured distance is 22,000,000 m and the assumed error is 1 microsecond, the distance the phone believes is 22,000,000 - 299.792 = 21,999,700.208 m. With an assumed error of 0 the subtraction does nothing. Without this, the circles would be too large by the clock's share.

```python
        # The sphere cuts the plane in a circle centred right under the satellite (east, north).
        # Pythagoras: distance^2 = radius^2 + up^2, so radius^2 = distance^2 - up^2.
        radius_squared = distance**2 - up_m**2
```
Picture a ball of radius `distance` around the satellite, and the flat ground below it. The circle where they meet is centred on the spot directly under the satellite, which has the same east and north as the satellite. Take a right triangle whose long side is `distance` (satellite to a point on the circle), whose upright side is `up_m` (the satellite's height) and whose flat side is the circle's radius. Pythagoras says distance squared equals radius squared plus up squared, so radius squared = distance squared - up squared. Small example: distance 5, height 4 gives radius squared = 25 - 16 = 9, so radius 3. With real sizes, a satellite straight overhead at 20,188,691.2 m with a measured distance of 20,188,691.2 m gives radius squared 0 (or a hair either side of 0, from rounding), so the circle shrinks to a single point under the satellite, and no line is drawn.

```python
        points = []
```
Start with no points for this satellite.

```python
        if radius_squared > 0:
            points = _circle_points(east_m, north_m, math.sqrt(radius_squared), half_width_m, samples)
```
If the radius squared is negative, the ball does not reach the ground at all (the measured distance is shorter than the satellite's height); if it is exactly zero, the ball only touches the ground at one spot. Either way there is no circle to draw, so we skip it. Otherwise take the square root to get the radius and ask `_circle_points` for the points of the circle that lie on the map. Without the `if`, `math.sqrt` of a negative number would crash.

```python
        # A line that only clips a corner of the square by a metre or two is too short to draw.
        inside = len(points) >= _MIN_POINTS
```
`inside` is True when at least 10 points landed on the map. A shorter line, such as one that only clips a corner, is treated as not being on the map.

```python
        lines.append({"id": satellite.get("id"), "points": points if inside else [], "inside": inside})
```
Adds this satellite's result to the list: its `id` (`.get` gives nothing instead of crashing if the satellite has no id), its points (replaced by an empty list when too few), and the `inside` flag. The page (`web/first-screen.js`) uses `inside` to decide whether to show the line or hide it.

```python
    return lines
```
Hands back one entry per satellite, in the same order as the input. The page draws each one as a line on the map: the part of that satellite's circle that crosses the map square around the true phone position.
