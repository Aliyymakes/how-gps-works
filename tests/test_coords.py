"""Tests for mechanism/coords.py."""

import json
import math

import pytest

from mechanism.constants import EARTH_RADIUS_M, GPS_ORBIT_RADIUS_M
from mechanism.coords import latlon_to_xyz, satellite_from_sky, xyz_to_latlon

PLACES = [(0, 0), (0, 90), (51.5, -0.12), (-33.9, 151.2), (89, 45), (-6.2, 106.8), (35, -170)]


def _xyz(point):
    return (point["x_m"], point["y_m"], point["z_m"])


def _distance(a, b):
    return math.dist(_xyz(a), _xyz(b))


@pytest.mark.parametrize("lat, lon", PLACES)
def test_round_trip(lat, lon):
    p = latlon_to_xyz(lat, lon)
    back = xyz_to_latlon(*_xyz(p))
    assert back["lat_deg"] == pytest.approx(lat, abs=1e-9)
    assert back["lon_deg"] == pytest.approx(lon, abs=1e-9)
    assert back["height_m"] == pytest.approx(0, abs=1e-3)


def test_height_round_trip():
    back = xyz_to_latlon(*_xyz(latlon_to_xyz(10, 20, 1000)))
    assert back["height_m"] == pytest.approx(1000, abs=1e-3)


def test_axes():
    p = latlon_to_xyz(0, 0)
    assert _xyz(p) == pytest.approx((EARTH_RADIUS_M, 0, 0), abs=0.001)
    assert _xyz(latlon_to_xyz(0, 90)) == pytest.approx((0, EARTH_RADIUS_M, 0), abs=0.001)
    assert _xyz(latlon_to_xyz(90, 0)) == pytest.approx((0, 0, EARTH_RADIUS_M), abs=0.001)


def test_straight_up_satellite():
    for lat, lon in PLACES:
        receiver = latlon_to_xyz(lat, lon)
        sat = satellite_from_sky(lat, lon, 0, 90)
        assert _distance(receiver, sat) == pytest.approx(GPS_ORBIT_RADIUS_M - EARTH_RADIUS_M, abs=1)
        # Directly above: same latitude and longitude, just higher.
        above = xyz_to_latlon(*_xyz(sat))
        assert above["lat_deg"] == pytest.approx(lat, abs=1e-6)
        assert above["lon_deg"] == pytest.approx(lon, abs=1e-6)


@pytest.mark.parametrize("az", [0, 90, 180, 270])
@pytest.mark.parametrize("el", [0, 30, 60])
def test_satellite_on_orbit_sphere(az, el):
    for lat, lon in PLACES:
        sat = satellite_from_sky(lat, lon, az, el)
        assert math.hypot(*_xyz(sat)) == pytest.approx(GPS_ORBIT_RADIUS_M, abs=1)


def test_north_and_east():
    receiver = latlon_to_xyz(0, 0)
    north = satellite_from_sky(0, 0, 0, 30)
    east = satellite_from_sky(0, 0, 90, 30)
    assert north["z_m"] > receiver["z_m"]
    assert east["y_m"] > receiver["y_m"]


def test_bad_input_returns_error():
    assert "error" in latlon_to_xyz(91, 0)
    assert "error" in satellite_from_sky(-91, 0, 0, 30)
    assert "error" in satellite_from_sky(0, 0, 0, -1)
    assert "error" in satellite_from_sky(0, 0, 0, 91)
    assert "error" in xyz_to_latlon(0, 0, 0)


def test_plain_types():
    json.dumps(latlon_to_xyz(10, 20, 5))
    json.dumps(xyz_to_latlon(1.0, 2.0, 3.0))
    json.dumps(satellite_from_sky(10, 20, 30, 40))
    for value in satellite_from_sky(10, 20, 30, 40).values():
        assert type(value) is float
