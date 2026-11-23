# Dilution of precision (DOP): how much the satellites' layout multiplies errors.
import numpy as np

KEYS = ("x_m", "y_m", "z_m")


def read_point(point):
    # Turn {"x_m", "y_m", "z_m"} into [x, y, z]. Returns None if it is not a valid point.
    if not isinstance(point, dict):
        return None
    try:
        return np.array([float(point[key]) for key in KEYS])
    except (KeyError, TypeError, ValueError):
        return None


def make_table(receiver, satellites):
    # One row per satellite: unit direction from receiver to satellite, then a 1 for the clock.
    # Returns (table, None) or (None, error sentence).
    start = read_point(receiver)
    if start is None:
        return None, "The receiver must have numbers x_m, y_m and z_m."
    if not isinstance(satellites, (list, tuple)) or len(satellites) < 4:
        return None, "At least 4 satellites are needed to work out DOP."
    rows = []
    for satellite in satellites:
        end = read_point(satellite)
        if end is None:
            return None, "Every satellite must have numbers x_m, y_m and z_m."
        arrow = end - start
        distance = np.linalg.norm(arrow)
        if not np.isfinite(distance) or distance == 0:
            return None, "A satellite is at the same spot as the receiver."
        rows.append(list(arrow / distance) + [1.0])
    return np.array(rows), None


def dop(receiver, satellites):
    table, problem = make_table(receiver, satellites)
    if problem:
        return {"error": problem}
    # Transpose times table, then invert. If the layout is flat or bunched, this cannot be inverted.
    try:
        inverse = np.linalg.inv(table.T @ table)
    except np.linalg.LinAlgError:
        return {"error": "These satellites are laid out so that DOP cannot be worked out."}
    diagonal = np.diag(inverse)
    if not np.all(np.isfinite(diagonal)) or np.any(diagonal < 0):
        return {"error": "These satellites are laid out so that DOP cannot be worked out."}
    # GDOP: all four diagonal entries. PDOP: the first three (position). TDOP: the last (clock).
    return {
        "gdop": float(np.sqrt(diagonal.sum())),
        "pdop": float(np.sqrt(diagonal[:3].sum())),
        "tdop": float(np.sqrt(diagonal[3])),
    }
