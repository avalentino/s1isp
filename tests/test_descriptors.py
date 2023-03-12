"""Tests for ISP headers decoding."""

import bpack

from s1isp.descriptors import (
    ESesSignalType,
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
