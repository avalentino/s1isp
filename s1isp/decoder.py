"""Sentinel-1 RAW data decoder."""

import io
import enum
import logging
import datetime
from typing import Optional

from .descriptors import (
    PacketPrimaryHeader,
    SyncMarkerException,
    PacketSecondaryHeader,
)
from .constants_and_luts import SYNK_MARKER

import tqdm
import bpack


def _sas_to_dict(sas):
    sas_data = bpack.asdict(sas)
    keys = [key for key in sas_data if key.startswith("_")]
    for key in keys:
        sas_data.pop(key)
    if sas.ssb_flag:
        sas_data["elevation_beam_address"] = None
        sas_data["azimuth_beam_address"] = None
        sas_data["sas_test"] = sas.get_sas_test()
        sas_data["cal_type"] = sas.get_cal_type()
        sas_data[
            "calibration_beam_address"
        ] = sas.get_calibration_beam_address()
    else:
        sas_data[
            "elevation_beam_address"
        ] = sas.get_elevation_beam_address()
        sas_data["azimuth_beam_address"] = sas.get_azimuth_beam_address()
        sas_data["sas_test"] = None
        sas_data["cal_type"] = None
        sas_data["calibration_beam_address"] = None

    return sas_data


def _radar_cfg_to_dict(rcss):
    rcss_data = bpack.asdict(rcss)
    rcss_data.pop("sas_sbb_message")
    rcss_data.pop("ses_sbb_message")

    # SAS SBB message
    sas_data = _sas_to_dict(rcss.sas_sbb_message)
    rcss_data.update(sas_data)

    # SES SBB message
    ses_data = bpack.asdict(rcss.ses_sbb_message)
    rcss_data.update(ses_data)

    return rcss_data


def _enum_value_to_name(data):
    """Rplace enum values with their symbolic name."""
    for key, value in data.items():
        if isinstance(value, enum.Enum):
            data[key] = value.name

    return data


def isp_to_dict(
    primary_header: PacketPrimaryHeader,
    secondary_header: Optional[PacketSecondaryHeader] = None,
    enum_value: bool = False,
) -> dict:
    """Converst promary and secondaty headers to dictionary."""
    data = bpack.asdict(primary_header)
    if secondary_header:
        sh = secondary_header

        # datation service
        data.update(bpack.asdict(sh.datation_service))

        # fixed ancillary data service
        data.update(bpack.asdict(sh.fixed_ancillary_data_service))

        # subcom ancillary data service
        sads_data = bpack.asdict(sh.subcom_ancillary_data_service)
        sads_data.pop("word_data")
        data.update(sads_data)

        # counters service
        data.update(bpack.asdict(sh.counters_service))

        # radar configuration support service
        rcss_data = _radar_cfg_to_dict(sh.radar_configuration_support_service)
        data.update(rcss_data)

        # radar sample count service
        data.update(bpack.asdict(sh.radar_sample_count_service))

    if not enum_value:
        # replace enums with their symbolic name
        data = _enum_value_to_name(data)

    return data


def decode_stream(
    filename,
    skip: Optional[int] = None,
    maxcount: Optional[int] = None,
    bytes_offset: int = 0,
    enum_value: bool = False,
):
    """Decode packet headers and store them into a pandas data-frame."""
    log = logging.getLogger(__name__)
    log.info(f'start decoding: "{filename}"')
    t0 = datetime.datetime.now()

    primary_header_size = bpack.calcsize(
        PacketPrimaryHeader, bpack.EBaseUnits.BYTES
    )
    secondary_header_size = bpack.calcsize(
        PacketSecondaryHeader, bpack.EBaseUnits.BYTES
    )
    records = []
    subcom_data_records = []
    packet_counter = 0
    pbar = tqdm.tqdm(unit=" packets", desc="decoded")
    with open(filename, "rb") as fd, pbar:
        if bytes_offset:
            assert bytes_offset >= 0
            fd.seek(bytes_offset)

        while fd:
            # primary header
            data = fd.read(primary_header_size)
            if len(data) == 0 or (maxcount and len(records) > maxcount):
                break

            # type - PacketPrimaryHeader
            primary_header = PacketPrimaryHeader.frombytes(data)

            assert primary_header.version == 0
            assert primary_header.packet_type == 0
            assert primary_header.sequence_flags == 3
            # assert primary_header.sequence_counter == packet_counter % 2**14

            # secondary header
            assert primary_header.secondary_header_flag
            data_field_size = primary_header.packet_data_length + 1

            if skip and packet_counter < skip:
                packet_counter += 1
                fd.seek(data_field_size, io.SEEK_CUR)
                continue

            # data = fd.read(data_field_size)
            data = fd.read(secondary_header_size)

            # type - PacketSecondaryHeader
            secondary_header = PacketSecondaryHeader.frombytes(
                data[:secondary_header_size]
            )

            sync = secondary_header.fixed_ancillary_data_service.sync_marker
            if sync != SYNK_MARKER:
                raise SyncMarkerException(
                    f"packat count: {packet_counter + 1}"
                )

            subcom_data = secondary_header.subcom_ancillary_data_service
            subcom_data_records.append([subcom_data])

            radar_cfg = secondary_header.radar_configuration_support_service
            assert radar_cfg.error_flag is False
            # baq_block_len = 8 * (radar_cfg.baq_block_len + 1)
            # assert baq_block_len == 256, (
            #     f'baq_block_len: {radar_cfg.baq_block_len}, '
            #     f'baq_mode: {radar_cfg.baq_mode}'
            # )

            counters_service = secondary_header.counters_service
            assert packet_counter == counters_service.space_packet_count
            packet_counter += 1

            # update the dataframe
            metadata = isp_to_dict(
                primary_header, secondary_header, enum_value=enum_value
            )
            records.append(metadata)

            # user data
            # fd.read(data_field_size - secondary_header_size)
            fd.seek(data_field_size - secondary_header_size, io.SEEK_CUR)

            # TBW

            pbar.update()

    elapsed = datetime.datetime.now() - t0
    log.info(f"decoding complete (elapsed time: {elapsed})")

    return records
