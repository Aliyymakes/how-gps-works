"""Turn satellites and measured distances into lines on a flat local ground map.

The map is centred on the true receiver. East and north are in metres, up is the height.
"""

import math

from mechanism.constants import SPEED_OF_LIGHT_M_PER_S
from mechanism.coords import _local_directions, latlon_to_xyz

# Sampling more densely than this is pointless; the line is then treated as missing the square.
_MAX_SAMPLES = 20_000
_MIN_POINTS = 10


def _dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def _local(receiver, directions, point):
    """East, north, up (metres) of a point, given the receiver's xyz and its local directions."""
    # The difference from the receiver, as an arrow in x, y, z.
    arrow = (point["x_m"] - receiver["x_m"], point["y_m"] - receiver["y_m"], point["z_m"] - receiver["z_m"])
    # Each local axis is a unit arrow; the dot product is how far the arrow reaches along it.
    east, north, up = directions
    return _dot(arrow, east), _dot(arrow, north), _dot(arrow, up)


def _is_point(point):
    """True when the point is a dict with numbers for x_m, y_m and z_m."""
    return isinstance(point, dict) and all(
        isinstance(point.get(key), (int, float)) for key in ("x_m", "y_m", "z_m")
    )


def to_local(receiver_lat_deg, receiver_lon_deg, point):
    """Return where a point is relative to the true receiver, in east, north, up metres."""
    if not _is_point(point):
        return {"error": "A point needs numbers for x_m, y_m and z_m."}
    receiver = latlon_to_xyz(receiver_lat_deg, receiver_lon_deg)
    if "error" in receiver:
        return receiver
    directions = _local_directions(receiver_lat_deg, receiver_lon_deg)
    east_m, north_m, up_m = _local(receiver, directions, point)
    return {"east_m": float(east_m), "north_m": float(north_m), "up_m": float(up_m)}


def _circle_points(centre_e, centre_n, radius, half_width_m, samples):
    """Points of the circle that fall inside the square, sampled only near the square."""
    # The angle (seen from the circle's centre) that points at the middle of the square.
    middle_angle = math.atan2(-centre_n, -centre_e)
    # The square fits inside a circle of radius half_width * sqrt(2) around its middle.
    # Seen from the circle's centre, that covers this half-angle (all the way round if the circle is small).
    reach = half_width_m * math.sqrt(2)
    half_angle = math.pi if reach >= radius else min(math.pi, math.asin(reach / radius) * 1.05)
    points = []
    while samples <= _MAX_SAMPLES:
        points = []
        for i in range(samples):
            # Spread the angles evenly across the part of the circle near the square.
            angle = middle_angle - half_angle + 2 * half_angle * i / (samples - 1)
            east_m = centre_e + radius * math.cos(angle)
            north_m = centre_n + radius * math.sin(angle)
            # Keep only points inside the square (tiny tolerance for rounding).
            if abs(east_m) <= half_width_m + 1e-6 and abs(north_m) <= half_width_m + 1e-6:
                points.append([float(east_m), float(north_m)])
        if len(points) >= _MIN_POINTS or not points:
            break
        # Too few points landed inside: sample more densely.
        samples *= 2
    return points


def distance_lines(receiver_lat_deg, receiver_lon_deg, satellites, pseudoranges_m,
                   assumed_clock_error_s, half_width_m=1000, samples=40):
    """Return one line per satellite: where its distance sphere cuts the ground plane."""
    if not satellites:
        return {"error": "At least one satellite is needed."}
    if len(satellites) != len(pseudoranges_m):
        return {"error": "There must be one measured distance for each satellite."}
    if half_width_m <= 0:
        return {"error": "The map half width must be more than 0 metres."}
    if samples < 2:
        return {"error": "At least 2 samples are needed."}
    if not all(_is_point(satellite) for satellite in satellites):
        return {"error": "Each satellite needs numbers for x_m, y_m and z_m."}
    if not all(isinstance(value, (int, float)) for value in pseudoranges_m):
        return {"error": "Each measured distance must be a number."}
    receiver = latlon_to_xyz(receiver_lat_deg, receiver_lon_deg)
    if "error" in receiver:
        return receiver
    directions = _local_directions(receiver_lat_deg, receiver_lon_deg)
    lines = []
    for satellite, pseudorange in zip(satellites, pseudoranges_m):
        # The satellite in the local frame. The ground plane is up = 0.
        east_m, north_m, up_m = _local(receiver, directions, satellite)
        # Take off the distance the clock error added, to get the distance the phone believes.
        distance = pseudorange - assumed_clock_error_s * SPEED_OF_LIGHT_M_PER_S
        # The sphere cuts the plane in a circle centred right under the satellite (east, north).
        # Pythagoras: distance^2 = radius^2 + up^2, so radius^2 = distance^2 - up^2.
        radius_squared = distance**2 - up_m**2
        points = []
        if radius_squared > 0:
            points = _circle_points(east_m, north_m, math.sqrt(radius_squared), half_width_m, samples)
        # A line that only clips a corner of the square by a metre or two is too short to draw.
        inside = len(points) >= _MIN_POINTS
        lines.append({"id": satellite.get("id"), "points": points if inside else [], "inside": inside})
    return lines
