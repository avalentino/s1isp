"""Tests for ISP headers decoding."""

from fractions import Fraction

import bpack
import pytest
from numpy import testing as npt

from s1isp.enums import ESignalType
from s1isp.descriptors import (
    SasCalData,
    SasImgData,
    PacketPrimaryHeader,
    PacketSecondaryHeader,
    RangeDecimationInfo,
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
    assert rcss.ses_sbb_message.signal_type == ESignalType.tx_cal


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
    assert rcss.ses_sbb_message.signal_type == ESignalType.noise


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
    assert rcss.ses_sbb_message.signal_type == ESignalType.echo


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


def test_echo_datation_service(echo_data, echo_ref_data):
    shdata = echo_data[PHSIZE : PHSIZE + SHSIZE]
    secondary_header = PacketSecondaryHeader.frombytes(shdata)

    ds = secondary_header.datation_service
    ref = echo_ref_data["secondary_header"].datation_service

    assert ds.get_fine_time_sec() == ref.get_fine_time_sec()
    npt.assert_allclose(ds.get_fine_time_sec(), 0.9439621)


def test_echo_radar_configuration_support_service(echo_data, echo_ref_data):
    shdata = echo_data[PHSIZE : PHSIZE + SHSIZE]
    secondary_header = PacketSecondaryHeader.frombytes(shdata)

    rcss = secondary_header.radar_configuration_support_service
    ref = echo_ref_data["secondary_header"].radar_configuration_support_service

    assert rcss.get_baq_block_len_samples() == ref.get_baq_block_len_samples()
    assert rcss.get_range_decimation_info() == ref.get_range_decimation_info()
    assert rcss.get_rx_gain_db() == ref.get_rx_gain_db()
    assert (
        rcss.get_tx_ramp_rate_hz_per_sec() == ref.get_tx_ramp_rate_hz_per_sec()
    )
    assert (
        rcss.get_tx_pulse_start_freq_hz() == ref.get_tx_pulse_start_freq_hz()
    )
    assert rcss.get_tx_pulse_length_sec() == ref.get_tx_pulse_length_sec()
    assert (
        rcss.get_tx_pulse_length_samples() == ref.get_tx_pulse_length_samples()
    )
    assert rcss.get_pri_sec() == ref.get_pri_sec()
    assert rcss.get_swst_sec() == ref.get_swst_sec()
    assert rcss.get_delta_t_suppr_sec() == ref.get_delta_t_suppr_sec()
    assert (
        rcss.get_swst_after_decimation_sec()
        == ref.get_swst_after_decimation_sec()
    )
    assert rcss.get_swl_sec() == ref.get_swl_sec()
    assert rcss.get_swl_n3rx_samples() == ref.get_swl_n3rx_samples()
    assert rcss.get_swl_n3rx_sec() == ref.get_swl_n3rx_sec()

    npt.assert_allclose(rcss.get_rx_gain_db(), -6.0)
    npt.assert_allclose(rcss.get_tx_ramp_rate_hz_per_sec(), 1344932774550.9954)
    npt.assert_allclose(rcss.get_tx_pulse_start_freq_hz(), -29704503.224123612)
    npt.assert_allclose(rcss.get_tx_pulse_length_sec(), 4.4172432911548294e-05)
    npt.assert_allclose(rcss.get_pri_sec(), 0.0005194923216780943)
    npt.assert_allclose(rcss.get_swst_sec(), 0.00014042997218140596)
    npt.assert_allclose(rcss.get_delta_t_suppr_sec(), 1.0656799254897057e-06)
    npt.assert_allclose(
        rcss.get_swst_after_decimation_sec(), 0.00014149565210689566
    )
    npt.assert_allclose(rcss.get_swl_sec(), 0.0003244462533153409)
    npt.assert_allclose(rcss.get_swl_n3rx_sec(), 0.0003230708601615057)

    assert rcss.get_baq_block_len_samples() == 256
    assert rcss.get_range_decimation_info() == RangeDecimationInfo(
        decimation_filer_band=59440000.0,
        decimation_ratio=Fraction(4, 9),
        filter_length=40,
        swaths=["S3"],
    )
    assert rcss.get_tx_pulse_length_samples() == 2948
    assert rcss.get_swl_n3rx_samples() == 21558
