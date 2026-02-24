"""Tests for enum definitions."""

from s1isp.enums import ECalTypeS1CD


def test_cal_type_s1cd_values():
    """Ensure S1CD calibration type code up to 7 are accepted."""
    for idx in range(8):
        assert ECalTypeS1CD(idx) == idx

    # not applicable
    for idx in range(4, 8):
        assert ECalTypeS1CD(idx).name.startswith("_NOT_APPLICABLE")
