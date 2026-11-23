"""Tests for the GPS solver, using satellite positions written by hand."""

import json
import math

from mechanism.solver import solve_position


SPEED_OF_LIGHT = 299_792_458
RECEIVER = [6_371_000, 0, 0]
SATELLITE_DISTANCE_FROM_CENTRE = 26_571_000

# Five satellites in different directions around the Earth.
# These are test positions, not real satellite data.
SATELLITES = [
    [26_571_000, 0, 0],
    [0, 26_571_000, 0],
    [0, -26_571_000, 0],
    [0, 0, 26_571_000],
    [0, 0, -26_571_000],
]


def make_distances(satellites, clock_error_s=0):
    """Make exact measurements for the receiver in this test."""
    distances = []
    for satellite in satellites:
        real_distance = math.dist(satellite, RECEIVER)
        # A clock error makes the measured distance too large.
        measured_distance = real_distance + SPEED_OF_LIGHT * clock_error_s
        distances.append(measured_distance)
    return distances


def position_error(answer):
    """How far away is the answer from the correct position?"""
    return math.dist(answer["position_m"], RECEIVER)


def test_satellites_are_far_apart_in_the_sky():
    # Each satellite is the required distance from Earth's centre.
    for satellite in SATELLITES:
        assert math.isclose(
            math.dist(satellite, [0, 0, 0]),
            SATELLITE_DISTANCE_FROM_CENTRE,
        )

    # Check the angles as seen from the receiver, not Earth's centre.
    for i in range(len(SATELLITES)):
        for j in range(i + 1, len(SATELLITES)):
            a = [SATELLITES[i][k] - RECEIVER[k] for k in range(3)]
            b = [SATELLITES[j][k] - RECEIVER[k] for k in range(3)]

            # The dot product helps us find the angle between directions.
            dot_product = a[0] * b[0] + a[1] * b[1] + a[2] * b[2]
            cosine = dot_product / (math.dist(a, [0, 0, 0]) * math.dist(b, [0, 0, 0]))
            # Keep cosine in its normal range to avoid rounding problems.
            cosine = max(-1.0, min(1.0, cosine))
            angle = math.degrees(math.acos(cosine))
            assert angle >= 60


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
    three_satellites = [SATELLITES[0], SATELLITES[1], SATELLITES[3]]
    answer = solve_position(
        three_satellites, make_distances(three_satellites), solve_clock=False
    )
    assert answer["converged"] is True
    assert position_error(answer) < 1
    assert answer["clock_error_s"] == 0.0


def test_ignoring_clock_error_gives_a_wrong_position():
    three_satellites = [SATELLITES[0], SATELLITES[1], SATELLITES[3]]
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
        "position_m": [0.0, 0.0, 0.0],
        "clock_error_s": 0.0,
    }
    assert answer["steps"][-1]["position_m"] == answer["position_m"]
    assert answer["steps"][-1]["clock_error_s"] == answer["clock_error_s"]


def test_results_can_be_saved_as_json():
    answer = solve_position(SATELLITES, make_distances(SATELLITES, 0.001))
    json.dumps(answer, allow_nan=False)
    json.dumps(solve_position(SATELLITES[:2], [1, 2]), allow_nan=False)
