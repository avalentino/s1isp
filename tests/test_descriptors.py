"""Tests for ISP headers decoding."""

import bpack
import pytest

from s1isp.descriptors import (
    ESesSignalType,
    SasCalData,
    SasImgData,
    PacketPrimaryHeader,
    PacketSecondaryHeader,
)

PHSIZE = bpack.calcsize(PacketPrimaryHeader, bpack.EBaseUnits.BYTES)
SHSIZE = bpack.calcsize(PacketSecondaryHeader, bpack.EBaseUnits.BYTES)


def test_txcal(txcal_data, txcal_ref_data):
    phdata = txcal_data[:PHSIZE]
    shdata = txcal_data[PHSIZE : PHSIZE + SHSIZE]

    primary_header = PacketPrimaryHeader.frombytes(phdata)
    assert primary_header == txcal_ref_data["primary_header"]

    secondary_header = PacketSecondaryHeader.frombytes(shdata)
    assert secondary_header == txcal_ref_data["secondary_header"]

    assert primary_header.packet_data_length + 1 == len(txcal_data) - PHSIZE

    rcss = secondary_header.radar_configuration_support_service
    assert rcss.ses_sbb_message.signal_type == ESesSignalType.tx_cal


def test_cal_sas(txcal_data, txcal_ref_data):
    shdata = txcal_data[PHSIZE : PHSIZE + SHSIZE]
    secondary_header = PacketSecondaryHeader.frombytes(shdata)

    rcss = secondary_header.radar_configuration_support_service
    sas = rcss.sas_sbb_message
    cal_sas = sas.get_sas_data()
    assert isinstance(cal_sas, SasCalData)

    ref_sh = txcal_ref_data["secondary_header"]
    ref_rcss = ref_sh.radar_configuration_support_service
    ref_sas = ref_rcss.sas_sbb_message

    assert sas.get_sas_test() == ref_sas.get_sas_test()
    assert cal_sas.sas_test == ref_sas.get_sas_test()
    assert sas.get_cal_type() == ref_sas.get_cal_type()
    assert cal_sas.cal_type == ref_sas.get_cal_type()

    ref_cal_beam_address = ref_sas.get_calibration_beam_address()
    assert sas.get_calibration_beam_address() == ref_cal_beam_address
    assert cal_sas.calibration_beam_address == ref_cal_beam_address

    with pytest.raises(TypeError):
        sas.get_elevation_beam_address()
    el_beam_address = (cal_sas.sas_test << 3) | cal_sas.cal_type
    assert sas.get_elevation_beam_address(check=False) == el_beam_address

    with pytest.raises(TypeError):
        sas.get_azimuth_beam_address()
    assert sas.get_azimuth_beam_address(check=False) == ref_cal_beam_address


def test_noise(noise_data, noise_ref_data):
    phdata = noise_data[:PHSIZE]
    shdata = noise_data[PHSIZE : PHSIZE + SHSIZE]

    primary_header = PacketPrimaryHeader.frombytes(phdata)
    assert primary_header == noise_ref_data["primary_header"]

    secondary_header = PacketSecondaryHeader.frombytes(shdata)
    assert secondary_header == noise_ref_data["secondary_header"]

    assert primary_header.packet_data_length + 1 == len(noise_data) - PHSIZE

    rcss = secondary_header.radar_configuration_support_service
    assert rcss.ses_sbb_message.signal_type == ESesSignalType.noise


def test_noise_sas(noise_data, noise_ref_data):
    shdata = noise_data[PHSIZE : PHSIZE + SHSIZE]
    secondary_header = PacketSecondaryHeader.frombytes(shdata)

    rcss = secondary_header.radar_configuration_support_service
    sas = rcss.sas_sbb_message
    cal_sas = sas.get_sas_data()
    assert isinstance(cal_sas, SasImgData)

    ref_sh = noise_ref_data["secondary_header"]
    ref_rcss = ref_sh.radar_configuration_support_service
    ref_sas = ref_rcss.sas_sbb_message

    ref_el_beam_address = ref_sas.get_elevation_beam_address()
    assert sas.get_elevation_beam_address() == ref_el_beam_address
    assert cal_sas.elevation_beam_address == ref_el_beam_address

    ref_az_beam_address = ref_sas.get_azimuth_beam_address()
    assert sas.get_azimuth_beam_address() == ref_az_beam_address
    assert cal_sas.azimuth_beam_address == ref_az_beam_address

    with pytest.raises(TypeError):
        sas.get_sas_test()
    sas_test = (cal_sas.elevation_beam_address >> 3) & 0b00000001
    assert sas.get_sas_test(check=False) == sas_test

    with pytest.raises(TypeError):
        sas.get_cal_type()
    cal_type = cal_sas.elevation_beam_address & 0b00000111
    assert sas.get_cal_type(check=False) == cal_type

    with pytest.raises(TypeError):
        sas.get_calibration_beam_address()
    assert sas.get_calibration_beam_address(check=False) == ref_az_beam_address


def test_echo(echo_data, echo_ref_data):
    phdata = echo_data[:PHSIZE]
    shdata = echo_data[PHSIZE : PHSIZE + SHSIZE]

    primary_header = PacketPrimaryHeader.frombytes(phdata)
    assert primary_header == echo_ref_data["primary_header"]

    secondary_header = PacketSecondaryHeader.frombytes(shdata)
    assert secondary_header == echo_ref_data["secondary_header"]

    assert primary_header.packet_data_length + 1 == len(echo_data) - PHSIZE

    rcss = secondary_header.radar_configuration_support_service
    assert rcss.ses_sbb_message.signal_type == ESesSignalType.echo


def test_echo_sas(echo_data, echo_ref_data):
    shdata = echo_data[PHSIZE : PHSIZE + SHSIZE]
    secondary_header = PacketSecondaryHeader.frombytes(shdata)

    rcss = secondary_header.radar_configuration_support_service
    sas = rcss.sas_sbb_message
    cal_sas = sas.get_sas_data()
    assert isinstance(cal_sas, SasImgData)

    ref_sh = echo_ref_data["secondary_header"]
    ref_rcss = ref_sh.radar_configuration_support_service
    ref_sas = ref_rcss.sas_sbb_message

    ref_el_beam_address = ref_sas.get_elevation_beam_address()
    assert sas.get_elevation_beam_address() == ref_el_beam_address
    assert cal_sas.elevation_beam_address == ref_el_beam_address

    ref_az_beam_address = ref_sas.get_azimuth_beam_address()
    assert sas.get_azimuth_beam_address() == ref_az_beam_address
    assert cal_sas.azimuth_beam_address == ref_az_beam_address

    with pytest.raises(TypeError):
        sas.get_sas_test()
    sas_test = (cal_sas.elevation_beam_address >> 3) & 0b00000001
    assert sas.get_sas_test(check=False) == sas_test

    with pytest.raises(TypeError):
        sas.get_cal_type()
    cal_type = cal_sas.elevation_beam_address & 0b00000111
    assert sas.get_cal_type(check=False) == cal_type

    with pytest.raises(TypeError):
        sas.get_calibration_beam_address()
    assert sas.get_calibration_beam_address(check=False) == ref_az_beam_address
