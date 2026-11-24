"""What a clock drift shared by every satellite does to the position (rung 4)."""

import math

from mechanism.constants import RELATIVITY_DRIFT_S_PER_DAY, SPEED_OF_LIGHT_M_PER_S
from mechanism.scenario import make_pseudoranges
from mechanism.solver import solve_position


def _is_number(value):
    """True for a normal number. True/False are not accepted as numbers."""
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def _check_input(receiver, satellites, phone_clock_error_s, hours_list):
    """Return an error message for bad input, or None if the input is fine."""
    if not isinstance(satellites, list) or len(satellites) < 4:
        return "At least 4 satellites are needed."
    if not isinstance(hours_list, list) or len(hours_list) == 0:
        return "hours_list must be a list with at least one number."
    if not _is_number(phone_clock_error_s):
        return "The phone clock error must be a number."
    for hours in hours_list:
        if not _is_number(hours):
            return "Every hour value must be a number."
        if hours < 0:
            return "Hours must not be negative."
    # A point and every satellite need numbers for x, y and z.
    points = [receiver] + satellites
    for point in points:
        if not isinstance(point, dict):
            return "The receiver and every satellite must be a point."
        for key in ("x_m", "y_m", "z_m"):
            if not _is_number(point.get(key)):
                return "Every point needs number values for x_m, y_m and z_m."
    return None


def _error_m(answer, receiver):
    """How far the solved position is from the true receiver, in metres."""
    return math.dist(
        [answer["x_m"], answer["y_m"], answer["z_m"]],
        [receiver["x_m"], receiver["y_m"], receiver["z_m"]],
    )


def drift_over_time(receiver, satellites, phone_clock_error_s, hours_list):
    """For each number of hours, add the shared drift and solve two ways.

    Returns one dict per hour: hours, range_added_m, error_clock_solved_m,
    error_clock_trusted_m, solved_clock_error_s. Bad input returns {"error": ...}.
    """
    message = _check_input(receiver, satellites, phone_clock_error_s, hours_list)
    if message:
        return {"error": message}

    results = []
    for hours in hours_list:
        # The drift grows with time and is the same for every satellite.
        drift_s = RELATIVITY_DRIFT_S_PER_DAY * hours / 24
        # It makes every measured distance longer, just like a phone clock error.
        ranges = make_pseudoranges(receiver, satellites, phone_clock_error_s + drift_s)
        if isinstance(ranges, dict):
            return ranges
        # Solve once with the clock solved, once trusting the phone's clock.
        solved = solve_position(satellites, ranges, solve_clock=True)
        if "error" in solved:
            return solved
        trusted = solve_position(satellites, ranges, solve_clock=False)
        if "error" in trusted:
            return trusted
        results.append(
            {
                "hours": float(hours),
                "range_added_m": float(drift_s * SPEED_OF_LIGHT_M_PER_S),
                "error_clock_solved_m": float(_error_m(solved, receiver)),
                "error_clock_trusted_m": float(_error_m(trusted, receiver)),
                "solved_clock_error_s": float(solved["clock_error_s"]),
            }
        )
    return results
