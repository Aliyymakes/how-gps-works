import json
import math

from mechanism.geometry import dop

EARTH_RADIUS_M = 6_371_000
RANGE_M = 20_200_000
RECEIVER = {"x_m": EARTH_RADIUS_M, "y_m": 0, "z_m": 0}


def sat(name, azimuth_deg, elevation_deg):
    # Receiver frame: up is +x, east is +y, north is +z.
    az = math.radians(azimuth_deg)
    el = math.radians(elevation_deg)
    return {
        "id": name,
        "x_m": EARTH_RADIUS_M + RANGE_M * math.sin(el),
        "y_m": RANGE_M * math.cos(el) * math.sin(az),
        "z_m": RANGE_M * math.cos(el) * math.cos(az),
    }


SPREAD = [sat("A", 0, 85), sat("B", 0, 18), sat("C", 120, 18), sat("D", 240, 18)]
BUNCHED = [sat("A", 0, 60), sat("B", 5, 65), sat("C", 10, 60), sat("D", 5, 55)]


def test_spread_satellites_give_low_pdop():
    assert dop(RECEIVER, SPREAD)["pdop"] < 3


def test_bunched_satellites_give_high_pdop():
    assert dop(RECEIVER, BUNCHED)["pdop"] > 10


def test_fewer_than_four_satellites_is_an_error():
    assert "error" in dop(RECEIVER, SPREAD[:3])


def test_missing_key_is_an_error():
    bad = [dict(s) for s in SPREAD]
    del bad[0]["z_m"]
    assert "error" in dop(RECEIVER, bad)


def test_not_dicts_is_an_error():
    assert "error" in dop("here", SPREAD)
    assert "error" in dop(RECEIVER, ["a", "b", "c", "d"])


def test_satellite_on_the_receiver_is_an_error():
    on_top = SPREAD[:3] + [dict(RECEIVER, id="D")]
    assert "error" in dop(RECEIVER, on_top)


def test_result_is_plain_floats_and_json_works():
    result = dop(RECEIVER, SPREAD)
    json.dumps(result)
    assert set(result) == {"gdop", "pdop", "tdop"}
    assert all(type(value) is float for value in result.values())


def test_gdop_squared_is_pdop_squared_plus_tdop_squared():
    r = dop(RECEIVER, SPREAD)
    assert math.isclose(r["gdop"] ** 2, r["pdop"] ** 2 + r["tdop"] ** 2)
