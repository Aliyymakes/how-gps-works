"""Tests for mechanism/scenario.py."""

import json
import math
import statistics

import pytest

from mechanism.constants import SPEED_OF_LIGHT_M_PER_S
from mechanism.coords import latlon_to_xyz, satellite_from_sky
from mechanism.scenario import make_pseudoranges

RECEIVER = latlon_to_xyz(10, 20)


def _satellites(count=4):
    sats = []
    for i in range(count):
        point = satellite_from_sky(10, 20, 90 * i, 45)
        sats.append({"id": f"S{i}", **point})
    return sats


def _true_distance(receiver, sat):
    return math.dist(
        (receiver["x_m"], receiver["y_m"], receiver["z_m"]),
        (sat["x_m"], sat["y_m"], sat["z_m"]),
    )


def test_clock_error_adds_299_point_79_metres():
    sats = _satellites()
    result = make_pseudoranges(RECEIVER, sats, 0.000001, noise_m=0)
    assert SPEED_OF_LIGHT_M_PER_S * 0.000001 == pytest.approx(299.792458)
    for sat, measured in zip(sats, result):
        assert measured == pytest.approx(_true_distance(RECEIVER, sat) + 299.792458, abs=0.001)


def test_zero_clock_zero_noise_is_true_distance():
    sats = _satellites()
    for sat, measured in zip(sats, make_pseudoranges(RECEIVER, sats, 0)):
        assert measured == pytest.approx(_true_distance(RECEIVER, sat), abs=0.001)


def test_same_seed_same_output_different_seed_differs():
    sats = _satellites()
    a = make_pseudoranges(RECEIVER, sats, 0, noise_m=5, seed=3)
    b = make_pseudoranges(RECEIVER, sats, 0, noise_m=5, seed=3)
    c = make_pseudoranges(RECEIVER, sats, 0, noise_m=5, seed=4)
    assert a == b
    assert a != c


def test_noise_spread():
    sats = _satellites() * 2500  # 10,000 values
    clean = make_pseudoranges(RECEIVER, sats, 0, noise_m=0)
    noisy = make_pseudoranges(RECEIVER, sats, 0, noise_m=5, seed=1)
    errors = [n - c for n, c in zip(noisy, clean)]
    assert len(errors) == 10_000
    assert 4.5 < statistics.pstdev(errors) < 5.5


def test_plain_types():
    result = make_pseudoranges(RECEIVER, _satellites(), 1e-6, noise_m=2, seed=1)
    json.dumps(result)
    assert all(type(v) is float for v in result)


def test_bad_input_returns_error():
    assert "error" in make_pseudoranges(RECEIVER, [], 0)
    assert "error" in make_pseudoranges(RECEIVER, _satellites(), 0, noise_m=-1)
