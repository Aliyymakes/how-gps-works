"""Tests for the GPS solver, using satellite positions written by hand."""

import json
import math

from mechanism.constants import SPEED_OF_LIGHT_M_PER_S
from mechanism.solver import solve_position


RECEIVER = [6_371_000, 0, 0]
EARTH_RADIUS = 6_371_000
SATELLITE_DISTANCE_FROM_CENTRE = 26_571_000


def make_satellite(name, azimuth_deg, elevation_deg):
    """Place a test satellite in the sky above the receiver.

    The receiver is on the x axis, so "up" is +x, "east" is +y and "north" is +z.
    The satellite is placed in the chosen direction, on a sphere that is
    SATELLITE_DISTANCE_FROM_CENTRE from the Earth's centre.
    """
    azimuth = math.radians(azimuth_deg)
    elevation = math.radians(elevation_deg)
    up = math.sin(elevation)
    east = math.cos(elevation) * math.sin(azimuth)
    north = math.cos(elevation) * math.cos(azimuth)

    # Walk "distance" metres from the receiver along that direction and stop
    # where we reach the satellite sphere (a quadratic equation in distance).
    b = EARTH_RADIUS * up
    c = EARTH_RADIUS**2 - SATELLITE_DISTANCE_FROM_CENTRE**2
    distance = -b + math.sqrt(b * b - c)

    return {
        "id": name,
        "x_m": EARTH_RADIUS + distance * up,
        "y_m": distance * east,
        "z_m": distance * north,
    }


# One satellite straight overhead and four low in the sky, 90 degrees apart.
# These are test positions, not real satellite data.
SATELLITES = [
    make_satellite("overhead", 0, 90),
    make_satellite("north", 0, 20),
    make_satellite("east", 90, 20),
    make_satellite("south", 180, 20),
    make_satellite("west", 270, 20),
]


def point_of(satellite):
    return [satellite["x_m"], satellite["y_m"], satellite["z_m"]]


def make_distances(satellites, clock_error_s=0):
    """Make exact measurements for the receiver in this test."""
    distances = []
    for satellite in satellites:
        real_distance = math.dist(point_of(satellite), RECEIVER)
        # A clock error makes the measured distance too large.
        measured_distance = real_distance + SPEED_OF_LIGHT_M_PER_S * clock_error_s
        distances.append(measured_distance)
    return distances


def position_error(answer):
    """How far away is the answer from the correct position?"""
    return math.dist([answer["x_m"], answer["y_m"], answer["z_m"]], RECEIVER)


def test_satellites_are_far_apart_in_the_sky():
    # Each satellite is the required distance from Earth's centre.
    for satellite in SATELLITES:
        assert math.isclose(
            math.dist(point_of(satellite), [0, 0, 0]),
            SATELLITE_DISTANCE_FROM_CENTRE,
        )

    # Check the angles as seen from the receiver, not Earth's centre.
    for i in range(len(SATELLITES)):
        for j in range(i + 1, len(SATELLITES)):
            a = [point_of(SATELLITES[i])[k] - RECEIVER[k] for k in range(3)]
            b = [point_of(SATELLITES[j])[k] - RECEIVER[k] for k in range(3)]

            # The dot product helps us find the angle between directions.
            dot_product = a[0] * b[0] + a[1] * b[1] + a[2] * b[2]
            cosine = dot_product / (math.dist(a, [0, 0, 0]) * math.dist(b, [0, 0, 0]))
            # Keep cosine in its normal range to avoid rounding problems.
            cosine = max(-1.0, min(1.0, cosine))
            angle = math.degrees(math.acos(cosine))
            assert angle >= 60


def test_satellites_are_above_the_horizon():
    # The receiver's "up" is +x, so a satellite above the horizon has x beyond
    # the receiver's x.
    for satellite in SATELLITES:
        assert satellite["x_m"] > RECEIVER[0]


def test_five_satellites_with_clock_error():
    answer = solve_position(SATELLITES, make_distances(SATELLITES, 0.001))
    assert answer["converged"] is True
    assert position_error(answer) < 1
    assert abs(answer["clock_error_s"] - 0.001) < 3e-9
    assert len(answer["steps"]) <= 20


def test_four_satellites_with_clock_error():
    four_satellites = SATELLITES[:4]
    answer = solve_position(four_satellites, make_distances(four_satellites, 0.001))
    assert answer["converged"] is True
    assert position_error(answer) < 1
    assert abs(answer["clock_error_s"] - 0.001) < 3e-9
    assert len(answer["steps"]) <= 20


def test_three_satellites_when_clock_is_correct():
    three_satellites = SATELLITES[:3]
    answer = solve_position(
        three_satellites, make_distances(three_satellites), solve_clock=False
    )
    assert answer["converged"] is True
    assert position_error(answer) < 1
    assert answer["clock_error_s"] == 0.0


def test_ignoring_clock_error_gives_a_wrong_position():
    three_satellites = SATELLITES[:3]
    answer = solve_position(
        three_satellites,
        make_distances(three_satellites, 0.000001),
        solve_clock=False,
    )
    assert position_error(answer) > 100
    assert answer["clock_error_s"] == 0.0


def test_three_satellites_cannot_solve_the_clock():
    three_satellites = SATELLITES[:3]
    answer = solve_position(three_satellites, make_distances(three_satellites))
    assert isinstance(answer, dict)
    assert "error" in answer


def test_two_satellites_cannot_solve_without_the_clock():
    two_satellites = SATELLITES[:2]
    answer = solve_position(
        two_satellites, make_distances(two_satellites), solve_clock=False
    )
    assert "error" in answer


def test_different_list_lengths_give_an_error():
    answer = solve_position(SATELLITES, [1, 2, 3])
    assert "error" in answer


def test_steps_start_in_the_centre_and_end_at_the_answer():
    answer = solve_position(SATELLITES, make_distances(SATELLITES, 0.001))
    assert answer["steps"][0] == {
        "x_m": 0.0,
        "y_m": 0.0,
        "z_m": 0.0,
        "clock_error_s": 0.0,
    }
    last_step = answer["steps"][-1]
    for key in ["x_m", "y_m", "z_m", "clock_error_s"]:
        assert last_step[key] == answer[key]


def test_results_can_be_saved_as_json():
    answer = solve_position(SATELLITES, make_distances(SATELLITES, 0.001))
    json.dumps(answer, allow_nan=False)
    json.dumps(solve_position(SATELLITES[:2], [1, 2]), allow_nan=False)
