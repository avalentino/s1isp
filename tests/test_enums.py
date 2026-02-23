"""Tests for enum definitions."""

from s1isp.enums import ECalTypeS1CD


def test_cal_type_s1cd_apdn_cal_value():
    """Ensure S1CD calibration type code 4 is accepted."""
    assert ECalTypeS1CD(4) == ECalTypeS1CD.APDN_CAL
