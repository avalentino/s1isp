"""Tools to parse AUX-INS files and instantiate EccPrograms."""

from __future__ import annotations

import os
import contextlib

import s1aux

from .enums import ESwath, EEccNumber, ESignalType, ESequenceType
from .eccprogram import EccProgram, EccSequence, SwathMapType, EccSequenceItem


def _get_sequence_type(name: ESequenceType | str) -> ESequenceType:
    """Return an :class:`ESequenceType` enumerator for the input string."""
    if isinstance(name, ESequenceType):
        return name
    if isinstance(name, str):
        if name == "Preamble":
            return ESequenceType.PREAMBLE
        if name == "Image Acquisition":
            return ESequenceType.IMAGING
        if name == "Postamble":
            return ESequenceType.POSTAMBLE

    with contextlib.suppress(ValueError):
        return ESequenceType(name)

    raise ValueError(f"invalid sequence type: {name!r}")


def _get_signal_type(name: ESignalType | str) -> ESignalType:
    """Return an :class:`ESignalType` enumerator for the input string."""
    if isinstance(name, ESignalType):
        return ESignalType(name)
    if isinstance(name, str):
        str_to_sigtype_map: dict[str, ESignalType] = {
            "SILENT": ESignalType.SILENT,
            "ECHO": ESignalType.ECHO,
            "NOISE": ESignalType.NOISE,
            "TX_CAL": ESignalType.TX_CAL,
            "RX_CAL": ESignalType.RX_CAL,
            "EPDN_CAL": ESignalType.EPDN_CAL,
            "TA_CAL": ESignalType.TA_CAL,
            "APDN_CAL": ESignalType.APDN_CAL,
            "TX_HCAL_ISO": ESignalType.TXH_CAL_ISO,
        }
        with contextlib.suppress(KeyError):
            return str_to_sigtype_map[name]

    raise ValueError(f"invalid signal type: {name!r}")


def _auxins_to_ecc_sequence_item(item) -> EccSequenceItem:
    return EccSequenceItem(
        _get_signal_type(item.signal.name),
        ESwath(item.swath.name),
        count=item.num_pri.value,
    )


def _auxins_to_ecc_sequence(sequence) -> EccSequence:
    items = [
        _auxins_to_ecc_sequence_item(item) for item in sequence.isp_list.isp
    ]
    assert sequence.repeat in {"true", "false"}  # nosec
    repeat: bool = sequence.repeat == "true"
    return EccSequence(_get_sequence_type(sequence.name), items, repeat=repeat)


def _get_swath_map(auxins_swath_map) -> SwathMapType:
    swath_map: dict[int, ESwath] = {}
    for item in auxins_swath_map:
        swath_number = int(item.swath_number)
        swath = ESwath(item.swath.name)
        if swath_number in swath_map:
            raise RuntimeError(
                f"multiple swath number {swath_number} not allowed"
            )
        swath_map[swath_number] = swath
    return swath_map


def _auxins_to_ecc_program(timeline_) -> EccProgram:
    sequences = [
        _auxins_to_ecc_sequence(seq)
        for seq in timeline_.sequence_list.sequence
    ]
    swath_map = _get_swath_map(timeline_.swath_map_list.swath_map)
    return EccProgram(
        timeline_.mode.name, timeline_.ecc_number, sequences, swath_map
    )


def load_ecc_programs(
    filename: str | os.PathLike[str],
) -> dict[EEccNumber, EccProgram]:
    """Load the Sentinel-1 ECC programs from an AUX-INS product.

    The input `filename` parameter is the filename of the XML data component
    of an AUX-INS product ("data/s1a-aux-ins.xml").

    The function returns a mapping having the :class:`EEccNumber` enumeration
    (keys), and :class:`EccPrograms` (values).
    """
    auxins = s1aux.load(filename)
    return {
        EEccNumber(item.ecc_number): _auxins_to_ecc_program(item)
        for item in auxins.timeline_list.timeline
    }
