"""Tests for mechanism/mapview.py."""

import json
import math

from mechanism.coords import latlon_to_xyz, satellite_from_sky
from mechanism.mapview import distance_lines, to_local
from mechanism.scenario import make_pseudoranges

LAT, LON = -6.2, 106.8
SKY = [(0, 20), (90, 40), (180, 65), (270, 15)]  # (azimuth, elevation) in degrees


def _setup(clock_error_s):
    receiver = latlon_to_xyz(LAT, LON)
    sats = []
    for i, (az, el) in enumerate(SKY):
        sats.append({"id": f"S{i}", **satellite_from_sky(LAT, LON, az, el)})
    return sats, make_pseudoranges(receiver, sats, clock_error_s)


def _miss_distance(points, target=(0.0, 0.0)):
    """Smallest distance from the target to the line made by joining the points."""
    best = math.inf
    for (x1, y1), (x2, y2) in zip(points, points[1:]):
        dx, dy = x2 - x1, y2 - y1
        t = ((target[0] - x1) * dx + (target[1] - y1) * dy) / (dx * dx + dy * dy)
        t = max(0.0, min(1.0, t))
        best = min(best, math.hypot(x1 + t * dx - target[0], y1 + t * dy - target[1]))
    return best


def test_to_local_receiver_is_origin():
    here = to_local(LAT, LON, latlon_to_xyz(LAT, LON))
    assert abs(here["east_m"]) < 0.001 and abs(here["north_m"]) < 0.001 and abs(here["up_m"]) < 0.001


def test_to_local_point_100_m_north():
    # 100 m of arc north is 100 / radius radians of latitude.
    north = latlon_to_xyz(LAT + math.degrees(100 / 6_371_008.7714), LON)
    assert abs(to_local(LAT, LON, north)["north_m"] - 100) < 0.5


def test_lines_pass_through_receiver_with_right_clock():
    sats, ranges = _setup(1e-6)
    lines = distance_lines(LAT, LON, sats, ranges, 1e-6)
    assert len(lines) == 4
    for line in lines:
        assert line["inside"]
        assert _miss_distance(line["points"]) < 1


def test_lines_miss_with_wrong_clock():
    sats, ranges = _setup(1e-6)
    for line in distance_lines(LAT, LON, sats, ranges, 0):
        assert line["inside"]
        assert _miss_distance(line["points"]) > 100


def test_points_inside_square_and_enough_of_them():
    sats, ranges = _setup(0)
    for line in distance_lines(LAT, LON, sats, ranges, 0):
        assert line["inside"]
        assert len(line["points"]) >= 10
        for east_m, north_m in line["points"]:
            assert abs(east_m) <= 1001 and abs(north_m) <= 1001


def test_output_is_plain_json():
    sats, ranges = _setup(0)
    json.dumps(distance_lines(LAT, LON, sats, ranges, 0))
    json.dumps(to_local(LAT, LON, sats[0]))


def test_bad_input_returns_error():
    sats, ranges = _setup(0)
    assert "error" in distance_lines(LAT, LON, [], [], 0)
    assert "error" in distance_lines(LAT, LON, sats, ranges[:2], 0)
    assert "error" in distance_lines(LAT, LON, sats, ranges, 0, half_width_m=0)
    assert "error" in distance_lines(LAT, LON, sats, ranges, 0, samples=1)


def test_malformed_points_return_error():
    assert "error" in to_local(LAT, LON, {})
    sats, ranges = _setup(0)
    broken = [dict(sats[0])] + sats[1:]
    del broken[0]["x_m"]
    assert "error" in distance_lines(LAT, LON, broken, ranges, 0)
    assert "error" in distance_lines(LAT, LON, sats, [None] + ranges[1:], 0)


def test_line_through_a_corner_is_found():
    # A circle that only just crosses the corner (-999, -999) of the map square.
    receiver = latlon_to_xyz(0, 0)
    satellite = {"id": "S1", **satellite_from_sky(0, 0, 45, 40)}
    east_m, north_m, up_m = (to_local(0, 0, satellite)[key] for key in ("east_m", "north_m", "up_m"))
    radius = math.hypot(east_m, north_m) + 999 * math.sqrt(2)
    distance = math.sqrt(radius**2 + up_m**2)
    line = distance_lines(0, 0, [satellite], [distance], 0)[0]
    assert line["inside"]
    assert len(line["points"]) >= 10
