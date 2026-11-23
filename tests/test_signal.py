import json

from mechanism.signal import ca_code, correlate, make_received

# Table 3-Ia of IS-GPS-200 Revision N (01-AUG-2022), column "First 10 Chips Octal".
# The first octal digit is one bit (chip 1); the other three digits are 3 bits each (chips 2 to 10).
# Chips are logic bits here: 0 -> +1, 1 -> -1.
FIRST_10_OCTAL = {
    1: "1440", 2: "1620", 3: "1710", 4: "1744", 5: "1133", 6: "1455", 7: "1131", 8: "1454",
    9: "1626", 10: "1504", 11: "1642", 12: "1750", 13: "1764", 14: "1772", 15: "1775",
    16: "1776", 17: "1156", 18: "1467", 19: "1633",
}


def octal_to_chips(octal):
    bits = octal[0] + format(int(octal[1:], 8), "09b")
    return [1 - 2 * int(b) for b in bits]


def test_first_ten_chips_match_the_spec_table():
    for prn, octal in FIRST_10_OCTAL.items():
        assert ca_code(prn)[:10] == octal_to_chips(octal), prn


def test_prn_1_first_chips_written_out():
    # The spec footnote says PRN 1 starts 1100100000.
    assert ca_code(1)[:10] == [-1, -1, 1, 1, -1, 1, 1, 1, 1, 1]


def test_every_prn_has_1023_plus_or_minus_one_values():
    for prn in range(1, 33):
        code = ca_code(prn)
        assert len(code) == 1023
        assert all(type(v) is int and v in (1, -1) for v in code)


def test_bad_prn_gives_error():
    for bad in (0, 33, -1, 1.5, "1", None):
        assert "error" in ca_code(bad)


def test_noise_free_delay_is_found():
    for delay in (0, 1, 100, 777, 1022):
        result = correlate(make_received(5, delay, 0), 5)
        assert result["best_delay_chips"] == delay
        assert abs(result["scores"][delay] - 1.0) < 1e-9


def test_moderate_noise_still_finds_delay():
    result = correlate(make_received(7, 300, 3, seed=1), 7)
    assert result["best_delay_chips"] == 300
    assert result["peak_to_next"] > 1.3


def test_very_high_noise_loses_the_delay():
    result = correlate(make_received(7, 300, 50, seed=1), 7)
    assert result["best_delay_chips"] != 300
    assert result["peak_to_next"] < 1.3


def test_wrong_satellite_gives_no_clear_peak():
    result = correlate(make_received(1, 400, 0), 2)
    assert max(result["scores"]) < 0.2
    assert result["peak_to_next"] < 1.5


def test_bad_inputs_return_error_not_raise():
    assert "error" in make_received(0, 5, 1)
    assert "error" in make_received(1, 1023, 1)
    assert "error" in make_received(1, 5, -1)
    assert "error" in correlate([1.0] * 10, 1)
    assert "error" in correlate([1.0] * 1023, 40)


def test_outputs_are_json_safe():
    received = make_received(3, 10, 1, seed=2)
    json.dumps(ca_code(3))
    json.dumps(received)
    json.dumps(correlate(received, 3))
    json.dumps(correlate([0.0] * 1023, 3))
    json.dumps(ca_code(0))
