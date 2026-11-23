"""What does a relativity clock drift shared by every satellite do to the position?

Run from the repo root: python scripts/check_relativity.py

Every satellite clock gains about 38 microseconds a day (docs/facts.md row 27).
Here we add that same drift to every measured distance and solve twice:
once with the phone's clock solved, once with the phone's clock trusted.
"""

import math
import sys
from pathlib import Path

# Let the script import the mechanism package from the repo root.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from mechanism.constants import SPEED_OF_LIGHT_M_PER_S
from mechanism.coords import latlon_to_xyz, satellite_from_sky
from mechanism.scenario import make_pseudoranges
from mechanism.solver import solve_position

DRIFT_S_PER_DAY = 38e-6  # docs/facts.md row 27, "about 38 microseconds a day"
PHONE_CLOCK_ERROR_S = 1e-6
RECEIVER_LAT_DEG, RECEIVER_LON_DEG = -6.2, 106.8
SKY = [(30, 60), (120, 35), (210, 20), (300, 45), (0, 80)]  # (azimuth, elevation)
DRIFT_TIMES_H = [0, 1, 6, 24]


def make_satellites():
    satellites = []
    for number, (azimuth, elevation) in enumerate(SKY, start=1):
        point = satellite_from_sky(RECEIVER_LAT_DEG, RECEIVER_LON_DEG, azimuth, elevation)
        satellites.append({"id": f"S{number}", **point})
    return satellites


def position_error_m(answer, receiver):
    return math.dist(
        [answer["x_m"], answer["y_m"], answer["z_m"]],
        [receiver["x_m"], receiver["y_m"], receiver["z_m"]],
    )


def main():
    receiver = latlon_to_xyz(RECEIVER_LAT_DEG, RECEIVER_LON_DEG)
    satellites = make_satellites()
    print("hours | range added (m) | error, clock solved (m) | solved clock (us) | error, clock trusted (m)")
    for hours in DRIFT_TIMES_H:
        drift_s = DRIFT_S_PER_DAY * hours / 24
        # The drift makes every satellite's distance longer by the same amount,
        # exactly like a phone clock error would.
        ranges = make_pseudoranges(receiver, satellites, PHONE_CLOCK_ERROR_S + drift_s)
        solved = solve_position(satellites, ranges, solve_clock=True)
        trusted = solve_position(satellites, ranges, solve_clock=False)
        print(
            f"{hours:5} | {drift_s * SPEED_OF_LIGHT_M_PER_S:15.1f} | "
            f"{position_error_m(solved, receiver):23.4f} | "
            f"{solved['clock_error_s'] * 1e6:17.4f} | "
            f"{position_error_m(trusted, receiver):24.1f}"
        )


if __name__ == "__main__":
    main()
