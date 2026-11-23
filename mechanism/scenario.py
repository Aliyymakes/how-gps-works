"""Make the distances a phone would measure to satellites."""

import math

import numpy as np

from mechanism.constants import SPEED_OF_LIGHT_M_PER_S


def make_pseudoranges(receiver, satellites, clock_error_s, noise_m=0, seed=0):
    """Return one measured distance (metres) per satellite, in the same order.

    measured = true straight-line distance + clock error effect + random noise
    """
    if not satellites:
        return {"error": "At least one satellite is needed."}
    if noise_m < 0:
        return {"error": "Noise must not be negative."}
    # A clock that runs ahead makes every distance too long by the same amount.
    clock_effect_m = clock_error_s * SPEED_OF_LIGHT_M_PER_S
    # The same seed always gives the same noise.
    rng = np.random.default_rng(seed)
    noise = rng.normal(0.0, noise_m, len(satellites))
    pseudoranges = []
    for satellite, noise_value in zip(satellites, noise):
        # Straight-line distance from Pythagoras in three dimensions.
        true_distance = math.sqrt(
            (satellite["x_m"] - receiver["x_m"]) ** 2
            + (satellite["y_m"] - receiver["y_m"]) ** 2
            + (satellite["z_m"] - receiver["z_m"]) ** 2
        )
        pseudoranges.append(float(true_distance + clock_effect_m + noise_value))
    return pseudoranges
