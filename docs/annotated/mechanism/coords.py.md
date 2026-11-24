# coords.py, line by line

Source: `mechanism/coords.py`

## What this file is for
The Earth is a ball, and the page needs to put things on it: the phone on the ground and the satellites in the sky. This file turns "latitude and longitude" into three plain numbers (x, y, z) that say where a point is in space, and back again. It also turns a sky direction (which way to look, and how high) into the position of a satellite out in orbit.

## Which files it talks to
- `mechanism/constants.py`: gives this file the Earth's radius and the GPS orbit radius.
- `mechanism/mapview.py`: uses `latlon_to_xyz` and `_local_directions` to draw the flat local map.
- No other mechanism file uses it. The page calls `latlon_to_xyz` and `satellite_from_sky` directly (from `web/first-screen.js`, `web/step-geometry.js` and `web/step-relativity.js`); see `docs/interface.md` for what the page receives. `xyz_to_latlon` is used only by the tests.
- Basics of reading code (functions, `if`, lists) are in `docs/annotated/how-to-read-code.md`.

## In three lines
1. `latlon_to_xyz` and `xyz_to_latlon` convert between "latitude, longitude, height" and "x, y, z metres from the centre of the Earth".
2. `_local_directions` finds the three directions east, north and up at a spot on the ground.
3. `satellite_from_sky` uses those directions to find the point at orbit height that lies in a given compass direction and elevation from the phone.

## The code, line by line

```python
"""Turn latitude, longitude and sky directions into x, y, z points on a sphere.
```
A triple-quoted text at the top of a file is a description for people. Python does not run it as a step. Without it the code still works, but the next reader has no summary.

```python
The origin is the centre of the Earth. The x axis points to latitude 0, longitude 0.
The y axis points to latitude 0, longitude 90 east. The z axis points to the north pole.
"""
```
These lines are the rest of that description, and the closing `"""` ends it. They fix the three axes. Point (0, 0, 0) is the middle of the Earth. The x axis goes out through the spot where the equator meets the zero meridian. The y axis goes out through the equator at 90 degrees east. The z axis goes up through the north pole. Everything below depends on this choice. If one part of the code used a different choice, points would land in the wrong places.

```python
import math
```
Python's built-in toolbox of maths functions (sine, cosine, square root). Without this line every `math.` below would fail with an error.

```python
from mechanism.constants import EARTH_RADIUS_M, GPS_ORBIT_RADIUS_M
```
Brings in two fixed numbers from our own `constants.py`: the Earth's radius (6,371,008.7714 metres) and the distance from the Earth's centre to a GPS satellite (26,559,700 metres). Keeping them in one place means every file uses the same value.

```python
def _point(x_m, y_m, z_m):
    return {"x_m": float(x_m), "y_m": float(y_m), "z_m": float(z_m)}
```
A small helper that packs three numbers into a labelled bundle (a dictionary) like `{"x_m": ..., "y_m": ..., "z_m": ...}`. The `_` at the start of the name means "for use inside this file". `float(...)` turns each value into a plain decimal number, so the page gets ordinary numbers it can read. The `_m` in each name says the unit is metres. Without this helper every function would repeat the same bundle code, and a typo in one place could break the page's data.

```python
def latlon_to_xyz(lat_deg, lon_deg, height_m=0):
    """Return the point at this latitude, longitude and height above the sphere."""
```
Starts a function that turns a place on the Earth into x, y, z. Inputs are latitude and longitude in degrees, and an optional height in metres (`=0` means "on the ground if you do not say"). The text in triple quotes is its description.

```python
    if not -90 <= lat_deg <= 90:
        return {"error": "Latitude must be between -90 and 90 degrees."}
```
A safety check. Latitude only exists between -90 (south pole) and 90 (north pole). If the number is outside that, the function stops and hands back an error message instead of a position. The rest of the program checks for the word `"error"` and shows the message. Without this check, a latitude of 200 would silently give a position that is not on any real place.

```python
    lat = math.radians(lat_deg)
    lon = math.radians(lon_deg)
```
The maths functions work in radians (a full turn is about 6.283), not degrees (a full turn is 360). These two lines convert. Example: 106.8 degrees is 106.8 x 3.14159 / 180 = 1.864 radians. Without this, `math.cos(106.8)` would treat the number as radians and give a wrong answer.

```python
    # Distance from the centre of the Earth.
    radius = EARTH_RADIUS_M + height_m
```
The comment line is a note for people. The code line works out how far the point is from the Earth's centre: the Earth's radius plus any height. On the ground this is 6,371,008.7714 m. At 1,000 m up it is 6,372,008.7714 m.

```python
    # cos(lat) is the share of the radius that lies in the flat equator plane.
    x_m = radius * math.cos(lat) * math.cos(lon)
    y_m = radius * math.cos(lat) * math.sin(lon)
```
The idea: first, how much of the radius lies flat in the equator plane. A point at the equator has all of it, a point at a pole has none. That share is `cos(lat)`. Then, within that flat plane, `cos(lon)` says how much goes toward x and `sin(lon)` how much goes toward y.

Worked example with the page's receiver, latitude -6.2 and longitude 106.8:
- cos(-6.2 degrees) = 0.99415, cos(106.8 degrees) = -0.28903, sin(106.8 degrees) = 0.95732.
- x = 6,371,008.7714 x 0.99415 x -0.28903 = -1,830,653.6 m.
- y = 6,371,008.7714 x 0.99415 x 0.95732 = 6,063,417.1 m.

x is negative because longitude 106.8 is past 90 degrees east, so the point is on the far side from x's direction. Without these lines there would be no x and y.

```python
    # Height up the pole axis only depends on latitude.
    z_m = radius * math.sin(lat)
```
Going up toward the north pole depends only on latitude, not longitude. The z value is `radius x sin(lat)`. Example: sin(-6.2 degrees) = -0.10800, so z = 6,371,008.7714 x -0.10800 = -688,064.8 m. It is negative because -6.2 is south of the equator. Without it the point would have no up-and-down position.

```python
    return _point(x_m, y_m, z_m)
```
Hands back the three numbers, packed by the helper. Without a `return` the caller would get nothing.

```python
def xyz_to_latlon(x_m, y_m, z_m):
    """Return latitude, longitude and height above the sphere for a point."""
```
The opposite function: from x, y, z back to latitude, longitude and height. Handy for checking that a point went to the right place.

```python
    # Distance from the centre of the Earth.
    radius = math.sqrt(x_m**2 + y_m**2 + z_m**2)
```
The straight-line distance from the centre is the 3D version of Pythagoras: square each part, add, take the square root. (`x_m**2` means x times x.) Example: (1, 1, 1) gives the square root of 3, about 1.732. For our receiver the three squares add up to 6,371,008.77 squared, so the radius comes back as 6,371,008.7714.

```python
    if radius == 0:
        return {"error": "The centre of the Earth has no latitude or longitude."}
```
If the point is exactly the centre, every direction is "outwards", so there is no latitude or longitude to report. The function returns an error rather than a made-up answer. Without it, the code below would give an arbitrary result for (0, 0, 0).

```python
    # Latitude is the angle above the equator plane.
    flat = math.sqrt(x_m**2 + y_m**2)
    lat_deg = math.degrees(math.atan2(z_m, flat))
```
`flat` is how far the point is from the pole axis (its distance within the equator plane). Latitude is the angle you look up (or down) from that flat plane: `atan2(z, flat)` finds that angle from the two lengths, and `math.degrees` converts radians back to degrees. Example for our receiver: flat = 6,333,744.5 and z = -688,064.8, so the angle is atan2(-688,064.8, 6,333,744.5) = -0.10821 radians = -6.2 degrees. Using `atan2` (rather than dividing and using `atan`) keeps it correct even right at a pole where `flat` is 0.

```python
    # Longitude is the angle around the pole axis, measured from the x axis.
    lon_deg = math.degrees(math.atan2(y_m, x_m))
```
Longitude is the angle you turn around the pole axis, starting from the x axis. `atan2(y, x)` finds it from the two flat parts. Example: x = -1,830,653.6 and y = 6,063,417.1 give 106.8 degrees. Without this line there would be no longitude.

```python
    return {
        "lat_deg": float(lat_deg),
        "lon_deg": float(lon_deg),
        "height_m": float(radius - EARTH_RADIUS_M),
    }
```
Hands back latitude, longitude and height as a labelled bundle. Height is the distance from the centre minus the Earth's radius: a point at 20,188,691.2286 m above the ground is at 26,559,700 m from the centre. Going out and back for our receiver gives -6.2, 106.8 and a height of 0.0, which is the round-trip check. Note the height can be negative for a point inside the ball, for example (1, 1, 1) gives about -6,371,007 m.

```python
def _local_directions(lat_deg, lon_deg):
    """Unit vectors (east, north, up) at a spot on the ground, each as (x, y, z)."""
```
Standing on the ground, you have three natural directions: east, north and up. This function says which way each one points, in the shared x, y, z axes. "Unit vector" means an arrow of length exactly 1, so it only carries a direction. The result is three (x, y, z) triples.

```python
    lat = math.radians(lat_deg)
    lon = math.radians(lon_deg)
```
Degrees to radians again, same reason as before.

```python
    # Up points straight away from the centre of the Earth.
    up = (math.cos(lat) * math.cos(lon), math.cos(lat) * math.sin(lon), math.sin(lat))
```
Up is the same direction as "from the centre to the point", but with length 1. So it is the same formula as `latlon_to_xyz`, without the radius. For the receiver: (-0.28734, 0.95172, -0.10800).

```python
    # East points the way longitude grows; it has no z part.
    east = (-math.sin(lon), math.cos(lon), 0.0)
```
East is the way you move if longitude increases. That is a sideways turn around the pole axis, so it never goes up or down: its z part is 0. For the receiver: (-0.95732, -0.28903, 0.0).

```python
    # North is at right angles to both: it points toward the pole along the ground.
    north = (-math.sin(lat) * math.cos(lon), -math.sin(lat) * math.sin(lon), math.cos(lat))
```
North is the way along the ground toward the north pole. It is at right angles to both up and east. For the receiver: (-0.03122, 0.10339, 0.99415). Check: north has a big positive z (0.99415), meaning going north also climbs toward the pole, which is right.

```python
    return east, north, up
```
Gives back the three arrows in a fixed order. Callers use that order, so swapping it would swap east and north on the map.

```python
def satellite_from_sky(receiver_lat_deg, receiver_lon_deg, azimuth_deg, elevation_deg):
    """Return the point at GPS orbit height seen in this direction from the receiver."""
```
Given where the phone is, the compass direction to look (azimuth: 0 is north, 90 is east) and how high above the horizon (elevation: 0 is the horizon, 90 is straight up), find the satellite's x, y, z. It assumes the satellite is exactly on the GPS orbit sphere.

```python
    if not -90 <= receiver_lat_deg <= 90:
        return {"error": "Latitude must be between -90 and 90 degrees."}
```
Same latitude safety check as before, applied to the phone's latitude.

```python
    if not 0 <= elevation_deg <= 90:
        return {"error": "Elevation must be between 0 and 90 degrees."}
```
A satellite below the horizon (negative elevation) is hidden by the Earth, and above 90 makes no sense. So the function refuses and says why. Without this, a satellite under your feet could be produced.

```python
    receiver = latlon_to_xyz(receiver_lat_deg, receiver_lon_deg)
```
Where the phone is in x, y, z (on the ground, height 0). For our receiver that is (-1,830,653.6, 6,063,417.1, -688,064.8).

```python
    east, north, up = _local_directions(receiver_lat_deg, receiver_lon_deg)
```
The east, north and up arrows at the phone. The three names catch the three results in order.

```python
    az = math.radians(azimuth_deg)
    el = math.radians(elevation_deg)
```
Convert the two sky angles to radians.

```python
    # Sky direction: along the ground (east/north mix) scaled by cos(el), plus up scaled by sin(el).
    ground = [math.sin(az) * e + math.cos(az) * n for e, n in zip(east, north)]
```
The idea: a direction in the sky is "some way along the ground, plus some way up". First work out the ground part. Facing azimuth `az`, you go `sin(az)` of the way east and `cos(az)` of the way north (azimuth 0 is all north, 90 is all east). The `for e, n in zip(east, north)` part does the same sum for each of x, y and z in turn, pairing east's x with north's x, and so on. The result is a three-number list. Without it the satellite would not depend on compass direction.

```python
    direction = [math.cos(el) * g + math.sin(el) * u for g, u in zip(ground, up)]
```
Now tilt up. A high elevation puts more into `up` and less into the ground part: `cos(el)` of the ground arrow plus `sin(el)` of the up arrow. Example: elevation 45 degrees, azimuth 0 (due north) gives about 0.7071 of north plus 0.7071 of up. Elevation 90 gives pure up. The result is one arrow of length 1 pointing at the satellite. Without it there would be no direction to follow.

```python
    # Walk t metres along the line so that |receiver + t*direction| = orbit radius.
    # With a = |direction|^2 = 1 this is t^2 + 2*b*t + c = 0.
```
The idea: start at the phone and walk `t` metres along `direction`. We want to stop where our distance from the Earth's centre equals the orbit radius. Writing that out gives a quadratic equation, `t^2 + 2*b*t + c = 0`. The lead number (called `a`) is 1 because the direction arrow has length 1, which keeps the equation simple.

```python
    start = (receiver["x_m"], receiver["y_m"], receiver["z_m"])
```
Unpacks the phone's bundle into three plain numbers in a row, easier to loop over in the sums below.

```python
    b = sum(s * d for s, d in zip(start, direction))
```
`b` is the "dot product" of the phone's position and the direction: multiply the x parts, the y parts and the z parts, then add them. It says how much the walk heads away from the centre: it works out to the Earth's radius times sin(elevation), so it is 0 for a satellite on the horizon and largest straight up. For a satellite directly overhead (from anywhere on Earth) the phone's position and direction line up, so `b` = 6,371,008.7714.

```python
    c = sum(s * s for s in start) - GPS_ORBIT_RADIUS_M**2
```
`c` is "the phone's squared distance from the centre, minus the orbit radius squared". For a phone on the ground this is 6,371,008.7714 squared minus 26,559,700 squared = 40,589,752,765,256 - 705,417,664,090,000 = -664,827,911,324,744 (about -6.65 x 10^14).

```python
    # c is negative (the receiver is inside the orbit), so the positive root is the one ahead of us.
    t = -b + math.sqrt(b * b - c)
```
The quadratic formula gives two answers; the plus sign gives the one in front of the phone (the other is behind it, on the far side of the Earth). Because `c` is negative, the square root is always bigger than `b`, so `t` is positive. Example, satellite straight up (elevation 90): t = -6,371,008.7714 + sqrt(6,371,008.7714^2 + 664,827,911,324,744) = 20,188,691.2286 m. That equals 26,559,700 - 6,371,008.7714, exactly the orbit height, which is what we expect straight up.

```python
    return _point(*(s + t * d for s, d in zip(start, direction)))
```
Walk `t` metres from the phone along the direction: new x = start x + t times direction x, and likewise for y and z. The `*` unpacks the three results into the helper's three inputs. The result is the satellite's position. Example: az 0, el 45 from our receiver gives (-6,711,865.9, 22,230,772.3, 12,890,356.3) m. Check its length: it is 26,559,700 m from the centre, as it must be.
