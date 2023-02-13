"""Sentinel-1 RAW data decoder."""

import io
import enum
import logging
from typing import List, NamedTuple, Optional, Type

from .descriptors import (
    PVTAncillatyData,
    PacketPrimaryHeader,
    SyncMarkerException,
    AttitudeAncillatyData,
    PacketSecondaryHeader,
    HKTemperatureAncillatyData,
    SubCommutatedAncillaryDataService,
)
from .constants_and_luts import SYNK_MARKER

import tqdm
import bpack




SUB_COMM_LEN = 64


class DecodedDataItem(NamedTuple):
    primary_header: PacketPrimaryHeader
    secondary_header: PacketSecondaryHeader


class SubCommItem(NamedTuple):
    packet_count: int
    subcomm_data: SubCommutatedAncillaryDataService


class DecodedSubCommData(NamedTuple):
    pvt: PVTAncillatyData
    att: AttitudeAncillatyData
    hk: HKTemperatureAncillatyData


class RecordInfo:
    def __init__(self, record_type: Type, word_index: int):
        self.size: int = bpack.calcsize(record_type, bpack.EBaseUnits.BYTES)
        self.record_type = record_type
        self.first_word_index: int = word_index
        self.last_word_index = self.first_word_index + self.size // 2 - 1

    @property
    def n_words(self) -> int:
        return self.size // 2


class CycleHandler:
    record_info = {
        "pvt": RecordInfo(PVTAncillatyData, 1),
        "att": RecordInfo(AttitudeAncillatyData, 23),
        "hk": RecordInfo(HKTemperatureAncillatyData, 42),
    }

    def __init__(self):
        self.data: List[SubCommutatedAncillaryDataService] = []

    def is_complete(self) -> bool:
        return len(self.data) == SUB_COMM_LEN

    def decode(self):
        word_indexes = [item.word_index for item in self.data]
        out = []
        for info in self.record_info.values():
            try:
                first_idx = word_indexes.index(info.first_word_index)
                last_idx = first_idx + info.n_words - 1
                last_word_idx = word_indexes[last_idx]
                if last_word_idx != info.last_word_index:
                    raise IndexError
            except (IndexError, ValueError):
                out.append(None)
                raise
            else:
                data = b"".join(
                    item.word_data
                    for item in self.data[first_idx : last_idx + 1]
                )
                out.append(info.record_type.frombytes(data))

        return DecodedSubCommData(*out)


class SubCommutatedDataDecoder:
    """Decoder for sub-commutated data."""

    MAX_WORD_INDEX = SUB_COMM_LEN

    def __init__(self):
        """Initialize the decoder."""
        self._cycle_data: List[CycleHandler] = []
        self._current_cycle_handler: Optional[CycleHandler] = None
        self._packet_count = None
        self._log: logging.Logger = logging.getLogger(
            f"{__name__}.{self.__class__.__name__}"
        )

    def _finalize_cycle(self):
        handler = self._current_cycle_handler
        if handler:
            if not handler.is_complete():
                self._log.warning(
                    f"Incomplete sub-commutated data cycle: "
                    f"{len(self._cycle_data)}"
                )
            self._cycle_data.append(handler)
            self._current_cycle_handler = None

    def _new_cycle(self):
        self._finalize_cycle()
        self._current_cycle_handler = CycleHandler()

    def _append_data(self, item: SubCommItem):
        packet_count, sc_data = item
        self._current_cycle_handler.data.append(sc_data)
        self._packet_count = packet_count

    def feed(self, item: SubCommItem):
        """Feed one data record into the decoder."""
        packet_count, data = item
        word_index = data.word_index
        if word_index == 0:
            return

        word_data = data.word_data

        if len(word_data) != 2:
            raise RuntimeError(
                f"Incorrect data size: {len(word_data)} (2 bytes expected)."
            )

        if word_index > self.MAX_WORD_INDEX:
            raise RuntimeError(f"Invalid word index {word_index}.")

        if not self._current_cycle_handler:
            self._new_cycle()
            if word_index != 1:
                self._log.warning(
                    f"Starting an incomplete sub-commutated data cycle. "
                    f"(first index: {word_index}."
                )
            self._append_data(item)

        else:
            assert self._current_cycle_handler.data
            prev_sc_data = self._current_cycle_handler.data[-1]
            prev_word_index = prev_sc_data.word_index
            step = word_index - prev_word_index
            if step < 0:
                self._new_cycle()
            elif (
                self._packet_count is not None and
                packet_count - self._packet_count > 1
            ):
                self._new_cycle()

            self._append_data(item)

        if word_index == self.MAX_WORD_INDEX:
            self._finalize_cycle()

    def finalize(self):
        """Finalize the input queue."""
        self._finalize_cycle()

    def decode(self, items: Optional[SubCommItem] = None):
        """Deconde sub-commutated data."""
        if items is not None:
            for item in items:
                self.feed(item)
        self.finalize()

        self._log.info(
            "%d sub-commutated data cycles collected.",
            len(self._cycle_data)
        )

        incomplete_count = 0
        out = []
        for item in self._cycle_data:
            if not item.is_complete():
                incomplete_count += 1
                # TODO: partial decoding could be possible at this stage
                continue
            out.append(item.decode())
        self._log.info(
            "%d inclomplete sub-commutated data cycles.",
            incomplete_count
        )
        return out



            if step <= 0:
                self._cycle_count += 1

            if step not in {1, 1 - self.MAX_WORD_INDEX}:
                self._log.warning(
                    "Broken sequence of sub-commutated data word indexes: "
                    "curret=%d, previous=%d.",
                    word_index,
                    previous_word_index,
                )

        self._word_indexes.append(word_index)
        self._datastream.write(data)

    def decode(self):
        """Deconde sub-commutated data."""
        # TODO
        raise NotImplementedError


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
    # subcom_data_decoder = SubCommutatedDataDecoder()  # TODO: remove
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
            subcom_data_records.append(subcom_data)
            # TODO: reove
            # subcom_data_decoder.feed(
            #     subcom_data.word_index, subcom_data.word_data
            # )

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

    # TODO: remove
    import pickle
    with open("subcom_data.pkl", "wb") as fd:
        pickle.dump(subcom_data_records, fd)

    # TODO: remove
    import json
    with open("subcom_data.json", "w") as fd:
        # data = [bpack.asdict(item) for item in subcom_data_records]
        data = [item.word_index for item in subcom_data_records]
        json.dump(data, fd, indent="  ")

    return records
