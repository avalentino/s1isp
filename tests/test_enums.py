"""Unit tests for enums."""

from types import NoneType

import pytest

from s1isp.enums import EEccNumber, ESensorMode, ecc_number_to_sensor_mode


@pytest.mark.parametrize("ecc_number", list(EEccNumber))
def test_ecc_number_to_sensor_mode__enum(ecc_number):
    sensor_mode = ecc_number_to_sensor_mode(ecc_number)
    assert isinstance(sensor_mode, (ESensorMode, NoneType))


@pytest.mark.parametrize("ecc_number", list(EEccNumber.__members__.values()))
def test_ecc_number_to_sensor_mode__str(ecc_number):
    sensor_mode = ecc_number_to_sensor_mode(ecc_number)
    assert isinstance(sensor_mode, (ESensorMode, NoneType))


def test_ecc_number_to_sensor_mode__s1():
    ecc_number = EEccNumber.S1
    expected_sensor_mode = ESensorMode.S1

    sensor_mode = ecc_number_to_sensor_mode(ecc_number)
    assert sensor_mode == expected_sensor_mode

    sensor_mode = ecc_number_to_sensor_mode(ecc_number.value)
    assert sensor_mode == expected_sensor_mode


def test_ecc_number_to_sensor_mode__not_set():
    ecc_number = EEccNumber.NOT_SET
    expected_sensor_mode = None

    sensor_mode = ecc_number_to_sensor_mode(ecc_number)
    assert sensor_mode == expected_sensor_mode

    sensor_mode = ecc_number_to_sensor_mode(ecc_number.value)
    assert sensor_mode == expected_sensor_mode


def test_ecc_number_to_sensor_mode__invalid():
    ecc_number = "invalid"

    with pytest.raises(ValueError, match="invalid ecc_number"):
        ecc_number_to_sensor_mode(ecc_number)
