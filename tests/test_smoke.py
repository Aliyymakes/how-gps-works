from mechanism.constants import SPEED_OF_LIGHT_M_PER_S


def test_one_microsecond_of_clock_error_is_about_300_metres():
    distance_m = SPEED_OF_LIGHT_M_PER_S * 1e-6
    assert 299 < distance_m < 300
