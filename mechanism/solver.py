"""Find a GPS receiver's position using distances to satellites."""

import math

import numpy as np


SPEED_OF_LIGHT = 299_792_458  # metres per second
MAX_STEPS = 20
STOP_WHEN_CHANGE_IS_SMALLER_THAN = 0.001  # metres


def _save_step(x, y, z, clock_m):
    """Save one guess using normal Python numbers and lists."""
    return {
        "position_m": [float(x), float(y), float(z)],
        "clock_error_s": float(clock_m / SPEED_OF_LIGHT),
    }


def solve_position(satellites, pseudoranges_m, solve_clock=True):
    """Guess the receiver's location and improve it using satellite distances.

    satellites: a list of [x, y, z] positions in metres
    pseudoranges_m: one measured distance in metres for each satellite
    solve_clock: whether to also find the receiver's clock error
    """
    if len(satellites) != len(pseudoranges_m):
        return {"error": "There must be one distance for each satellite."}

    needed = 4 if solve_clock else 3
    if len(satellites) < needed:
        return {"error": f"At least {needed} satellites are needed."}

    # Start at the Earth's centre with no clock error.
    x, y, z = 0.0, 0.0, 0.0
    clock_m = 0.0  # Store clock error as extra distance for easier maths.
    steps = [_save_step(x, y, z, clock_m)]
    converged = False

    # The first guess is already in steps, so we can add 19 more at most.
    for _ in range(MAX_STEPS - 1):
        errors = []
        changes = []

        for satellite, measured_distance in zip(satellites, pseudoranges_m):
            # Find the difference between the satellite and our guess.
            dx = x - satellite[0]
            dy = y - satellite[1]
            dz = z - satellite[2]

            # Use Pythagoras to find their straight-line distance.
            distance = math.sqrt(dx * dx + dy * dy + dz * dz)
            if distance == 0:
                return {"error": "The guess is exactly on a satellite."}

            # Compare what we would measure with what we actually measured.
            predicted = distance + clock_m
            errors.append(measured_distance - predicted)

            # Find how changing x, y, and z would change the distance.
            row = [dx / distance, dy / distance, dz / distance]
            if solve_clock:
                # Clock error adds the same extra distance for every satellite.
                row.append(1.0)
            changes.append(row)

        # Find the small movement that best reduces all the errors.
        correction, _, rank, _ = np.linalg.lstsq(changes, errors, rcond=None)
        if rank < needed:
            return {"error": "These satellites cannot give one clear position."}

        # Improve our guessed position.
        x += float(correction[0])
        y += float(correction[1])
        z += float(correction[2])
        if solve_clock:
            clock_m += float(correction[3])

        # Save every new guess, including the final one.
        steps.append(_save_step(x, y, z, clock_m))

        # Stop if the position and clock corrections are tiny (under 1 mm).
        if np.linalg.norm(correction) < STOP_WHEN_CHANGE_IS_SMALLER_THAN:
            converged = True
            break

    return {
        "position_m": [float(x), float(y), float(z)],
        "clock_error_s": float(clock_m / SPEED_OF_LIGHT),
        "converged": converged,
        "steps": steps,
    }
