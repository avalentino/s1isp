"""Sentinel-1 RAW data decoder."""

import io
import enum
import logging
from typing import List, NamedTuple, Optional, Sequence, Tuple, Type, Union

import tqdm
import bpack

from .udf import decode_ud
from .constants import SYNC_MARKER
from .constants import PRIMARY_HEADER_SIZE as PHSIZE
from .constants import SECONDARY_HEADER_SIZE as SHSIZE
from .descriptors import (
    PVTAncillaryData,
    PrimaryHeader,
    SyncMarkerException,
    AttitudeAncillaryData,
    SecondaryHeader,
    HKTemperatureAncillaryData,
    SubCommutatedAncillaryDataService,
)

__all__ = [
    "isp_to_dict",
    "decode_stream",
    "decoded_stream_to_dict",
    "SubCommutatedDataDecoder",
]


SUB_COMM_LEN = 64


class DecodedDataItem(NamedTuple):
    primary_header: PrimaryHeader
    secondary_header: SecondaryHeader
    udf: Optional[Union[bytes, Sequence[float]]] = None


class SubCommItem(NamedTuple):
    packet_count: int  # TODO: probably it is better to use PRI count
    subcom_data: SubCommutatedAncillaryDataService


class DecodedSubCommData(NamedTuple):
    pvt: PVTAncillaryData
    att: AttitudeAncillaryData
    hk: HKTemperatureAncillaryData


class SubcomRecordInfo:
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
        "pvt": SubcomRecordInfo(PVTAncillaryData, 1),
        "att": SubcomRecordInfo(AttitudeAncillaryData, 23),
        "hk": SubcomRecordInfo(HKTemperatureAncillaryData, 42),
    }

    def __init__(self):
        self.data: List[SubCommutatedAncillaryDataService] = []

    def is_complete(self) -> bool:
        return len(self.data) == SUB_COMM_LEN

    def decode(self):
        word_indexes = [item.data_word_index for item in self.data]
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
                    item.data_word
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
        data_word_index = data.data_word_index
        if data_word_index == 0:
            return

        data_word = data.data_word

        if len(data_word) != 2:
            raise RuntimeError(
                f"Incorrect data size: {len(data_word)} (2 bytes expected)."
            )

        if data_word_index > self.MAX_WORD_INDEX:
            raise RuntimeError(f"Invalid word index {data_word_index}.")

        if not self._current_cycle_handler:
            self._new_cycle()
            if data_word_index != 1:
                self._log.warning(
                    f"Starting an incomplete sub-commutated data cycle. "
                    f"(first index: {data_word_index}."
                )
            self._append_data(item)

        else:
            assert self._current_cycle_handler.data
            prev_sc_data = self._current_cycle_handler.data[-1]
            prev_word_index = prev_sc_data.data_word_index
            step = data_word_index - prev_word_index
            if step < 0:
                self._new_cycle()
            elif (
                self._packet_count is not None
                and packet_count - self._packet_count > 1
            ):
                self._new_cycle()

            self._append_data(item)

        if data_word_index == self.MAX_WORD_INDEX:
            self._finalize_cycle()

    def finalize(self):
        """Finalize the input queue."""
        self._finalize_cycle()

    def decode(self, items: Optional[SubCommItem] = None):
        """Decode sub-commutated data."""
        if items is not None:
            for item in items:
                self.feed(item)
        self.finalize()

        self._log.info(
            "%d sub-commutated data cycles collected.", len(self._cycle_data)
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
            "%d incomplete sub-commutated data cycles.", incomplete_count
        )
        return out


class EUdfDecodingMode(enum.Enum):
    NONE = "none"  # skip the compressed user data
    EXTRACT = "extract"  # extract the compressed data and return them
    DECODE = "decode"  # decode the ISP use data

    def __str__(self):
        return self.value


def decode_stream(
    filename,
    skip: Optional[int] = None,
    maxcount: Optional[int] = None,
    bytes_offset: int = 0,
    udf_decoding_mode: EUdfDecodingMode = EUdfDecodingMode.NONE,
) -> Tuple[List[DecodedDataItem], List[int], List[SubCommItem]]:
    """Decode packet headers.

    :param filename:
        path to the L0 data component file.
    :param skip: int, optional
        number of ISPs to skip (starting form `byte_offset`).
        Default: 0.
    :param maxcount: int, optional
        maximum number of ISPs to decode (starting form `skip`).
        Default: all remaining ISPs in the file.
    :param byte_offset: int, optional
        offset in bytes, from the beginning of the binary file, to the
        first ISP (if the `skip` parameter is specified the count starts
        at this offset).
        Default: 0.
    :returns:
        a 2 items tuple containing:

        * the decoded ISPs in form of (nested) dataclass structures
        * a list of :class:`SubCommItem` s containing sub-commutated data
    """
    packet_counter: int = 0
    records: List[DecodedDataItem] = []
    subcom_data_records: List[SubCommItem] = []
    offsets: List[int] = []
    pbar = tqdm.tqdm(unit=" packets", desc="decoded")
    with open(filename, "rb") as fd, pbar:
        if bytes_offset:
            assert bytes_offset >= 0
            fd.seek(bytes_offset)

        while fd:
            # TODO: it would be probably faster to use a local variable
            offsets.append(fd.tell())

            # primary header
            data = fd.read(PHSIZE)
            if len(data) == 0 or (maxcount and len(records) > maxcount):
                break

            # type - PrimaryHeader
            primary_header = PrimaryHeader.frombytes(data)

            assert primary_header.packet_version_number == 0
            assert primary_header.packet_type == 0
            assert primary_header.sequence_flags == 3
            # assert (
            #    primary_header.packet_sequence_count == packet_counter % 2**14
            # )

            # secondary header
            assert primary_header.secondary_header_flag
            data_field_size = primary_header.packet_data_length + 1

            if skip and packet_counter < skip:
                packet_counter += 1
                fd.seek(data_field_size, io.SEEK_CUR)
                continue

            # data = fd.read(data_field_size)
            # assert data_field_size == len(data)
            data = fd.read(SHSIZE)

            # type - SecondaryHeader
            secondary_header = SecondaryHeader.frombytes(data[:SHSIZE])

            # -- Datation Service
            # ds = secondary_header.datation

            # -- Fixed Ancillary Data Service
            # fasd = secondary_header.fixed_ancillary_data
            sync = secondary_header.fixed_ancillary_data.sync_marker
            if sync != SYNC_MARKER:
                raise SyncMarkerException(
                    f"packet count: {packet_counter + 1}"
                )

            # -- Sub-commutation Ancillary Data Service
            # sc_ads = secondary_header.subcom_ancillary_data
            sc_data_item = SubCommItem(
                packet_counter,
                secondary_header.subcom_ancillary_data,
            )
            subcom_data_records.append(sc_data_item)

            # -- Counters Service
            # cs = secondary_header.counters
            # The following assertion is incorrect for IW.
            # We need a proper timeline checking mechanism.
            # assert packet_counter == cs.space_packet_count

            # -- Radar Configuration Support Service
            rcss = secondary_header.radar_configuration_support
            assert rcss.error_flag is False
            # blocksize -> even + odd
            blocksize = rcss.get_baq_block_len_samples() // 2
            assert blocksize == 128, f"blocksize: {blocksize} != 128"

            # -- Radar Sample Count Service
            rscs = secondary_header.radar_sample_count
            # See S1-IF-ASD-PL-0007, section 3.2.5.11
            if rcss.ses.signal_type <= 7:
                assert (
                    2 * rscs.number_of_quads == rcss.get_swl_n3rx_samples()
                ), (
                    f"number_of_quads: {rscs.number_of_quads}, "
                    f"swl_n3rx_samples: {rcss.get_swl_n3rx_samples()}"
                )

            # -- user data
            if udf_decoding_mode is EUdfDecodingMode.NONE:
                fd.seek(data_field_size - SHSIZE, io.SEEK_CUR)
                udf = None
            elif udf_decoding_mode is EUdfDecodingMode.EXTRACT:
                udf = fd.read(data_field_size - SHSIZE)
            elif udf_decoding_mode is EUdfDecodingMode.DECODE:
                try:
                    udfbytes = fd.read(data_field_size - SHSIZE)
                    with open("packet-00408.pkl", "wb") as _fd:
                        _fd.write(udfbytes)
                    nq = rscs.number_of_quads
                    baqmod = rcss.baq_mode
                    tstmod = secondary_header.fixed_ancillary_data.test_mode
                    udf = decode_ud(
                        udfbytes, nq, baqmod, tstmod, blocksize=blocksize
                    )
                except Exception:
                    logging.getLogger(__name__).debug(
                        f"packet_counter: {packet_counter}, "
                        f"pri_count: "
                        f"{secondary_header.counters.pri_count}, "
                        f"nq: {nq}, baqmod: {baqmod}, tstmod: {tstmod}, "
                        f"blocksize: {blocksize}"
                    )
                    raise

            assert offsets[-1] + PHSIZE + data_field_size == fd.tell()

            # append a new record
            records.append(
                DecodedDataItem(primary_header, secondary_header, udf)
            )

            packet_counter += 1
            pbar.update()

    return records, offsets, subcom_data_records


def _sas_to_dict(sas):
    sas_data = bpack.asdict(sas)
    keys = [key for key in sas_data if key.startswith("_")]
    for key in keys:
        sas_data.pop(key)

    sas_data["elevation_beam_address"] = sas.get_elevation_beam_address(
        check=False
    )
    sas_data["azimuth_beam_address"] = sas.get_azimuth_beam_address(
        check=False
    )
    sas_data["sas_test"] = sas.get_sas_test(check=False)
    sas_data["cal_type"] = sas.get_cal_type(check=False)
    sas_data["calibration_beam_address"] = sas.get_calibration_beam_address(
        check=False
    )

    return sas_data


def _radar_cfg_to_dict(rcss):
    rcss_data = bpack.asdict(rcss)
    rcss_data.pop("sas")
    rcss_data.pop("ses")

    # SAS SBB message
    sas_data = _sas_to_dict(rcss.sas)
    rcss_data.update(sas_data)

    # SES SBB message
    ses_data = bpack.asdict(rcss.ses)
    rcss_data.update(ses_data)

    return rcss_data


def _enum_value_to_name(data):
    """Rplace enum values with their symbolic name."""
    for key, value in data.items():
        if isinstance(value, enum.Enum):
            data[key] = value.name

    return data


def isp_to_dict(
    primary_header: PrimaryHeader,
    secondary_header: Optional[SecondaryHeader] = None,
    enum_value: bool = False,
) -> dict:
    """Convert primary and secondary headers to dictionary."""
    data = bpack.asdict(primary_header)
    if secondary_header:
        sh = secondary_header

        # datation service
        data.update(bpack.asdict(sh.datation))

        # fixed ancillary data service
        data.update(bpack.asdict(sh.fixed_ancillary_data))

        # subcom ancillary data service
        sads_data = bpack.asdict(sh.subcom_ancillary_data)
        sads_data.pop("data_word")
        data.update(sads_data)

        # counters service
        data.update(bpack.asdict(sh.counters))

        # radar configuration support service
        rcss_data = _radar_cfg_to_dict(sh.radar_configuration_support)
        data.update(rcss_data)

        # radar sample count service
        data.update(bpack.asdict(sh.radar_sample_count))

    if not enum_value:
        # replace enums with their symbolic name
        data = _enum_value_to_name(data)

    return data


def decoded_stream_to_dict(
    records: List[DecodedDataItem],
    enum_value: bool = False,
) -> List[dict]:
    """Convert a list of decoded ISPs into a list of metadata dictionaries."""
    out = []
    for record in records:
        primary_header, secondary_header, _ = record
        metadata = isp_to_dict(
            primary_header, secondary_header, enum_value=enum_value
        )
        out.append(metadata)

    return out
