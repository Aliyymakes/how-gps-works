"""Tests for mechanism/relativity.py."""

import json

from mechanism.constants import RELATIVITY_DRIFT_S_PER_DAY
from mechanism.coords import latlon_to_xyz, satellite_from_sky
from mechanism.relativity import drift_over_time

LAT, LON = -6.2, 106.8
SKY = [(30, 60), (120, 35), (210, 20), (300, 45), (0, 80)]  # (azimuth, elevation)
PHONE_CLOCK_ERROR_S = 1e-6
HOURS = [0, 1, 6, 24]


def _setup():
    receiver = latlon_to_xyz(LAT, LON)
    sats = [
        {"id": f"S{i}", **satellite_from_sky(LAT, LON, az, el)}
        for i, (az, el) in enumerate(SKY)
    ]
    return receiver, sats


def _run(hours_list=HOURS):
    receiver, sats = _setup()
    return drift_over_time(receiver, sats, PHONE_CLOCK_ERROR_S, hours_list)


def test_range_added_after_24_hours():
    assert abs(_run()[-1]["range_added_m"] - 11392) < 1


def test_clock_solved_error_stays_small():
    for row in _run():
        assert row["error_clock_solved_m"] < 1


def test_clock_trusted_error_is_large_after_24_hours():
    assert _run()[-1]["error_clock_trusted_m"] > 1000


def test_solved_clock_includes_the_drift():
    expected = PHONE_CLOCK_ERROR_S + RELATIVITY_DRIFT_S_PER_DAY
    assert abs(_run()[-1]["solved_clock_error_s"] - expected) < 1e-9


def test_only_plain_types_are_returned():
    json.dumps(_run())


def test_bad_input_returns_error():
    receiver, sats = _setup()
    bad_calls = [
        ([], PHONE_CLOCK_ERROR_S, HOURS),
        (sats[:3], PHONE_CLOCK_ERROR_S, HOURS),
        (sats, PHONE_CLOCK_ERROR_S, []),
        (sats, PHONE_CLOCK_ERROR_S, "24"),
        (sats, PHONE_CLOCK_ERROR_S, [-1]),
        (sats, PHONE_CLOCK_ERROR_S, ["a"]),
        (sats, "a", HOURS),
    ]
    for satellites, clock, hours in bad_calls:
        result = drift_over_time(receiver, satellites, clock, hours)
        assert isinstance(result, dict) and "error" in result
