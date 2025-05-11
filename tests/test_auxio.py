"""Unite test for the s1aux.auxio module."""

import pathlib
from collections.abc import Mapping

import pytest

from s1isp.enums import ESwath, EEccNumber, ESignalType, ESequenceType
from s1isp.eccprogram import EccProgram

s1aux = pytest.importorskip("s1aux")
auxio = pytest.importorskip("s1isp.auxio")


TESTDIR = pathlib.Path(__file__).parent
DATAROOT = TESTDIR / "data"
AUX_INS_DATAFILE = DATAROOT / "auxio" / "s1b-aux-ins.xml"


@pytest.fixture
def auxinsdata():
    return s1aux.load(AUX_INS_DATAFILE)


@pytest.mark.parametrize(
    "sequence_type",
    list(ESequenceType) + list(ESequenceType.__members__.values()),
)
def test__get_sequence_type__std(sequence_type):
    out_sequence_type = auxio._get_sequence_type(sequence_type)
    assert out_sequence_type is ESequenceType(sequence_type)


def test__get_sequence_type__auxins(auxinsdata):
    for timeline_ in auxinsdata.timeline_list.timeline:
        for seq in timeline_.sequence_list.sequence:
            sequence_type = auxio._get_sequence_type(seq.name)
            if "preamble" in seq.name.lower():
                assert sequence_type is ESequenceType.PREAMBLE
            elif "postamble" in seq.name.lower():
                assert sequence_type is ESequenceType.POSTAMBLE
            else:
                assert sequence_type is ESequenceType.IMAGING


def test__get_sequence_type__invalid():
    with pytest.raises(ValueError, match="invalid sequence type"):
        auxio._get_sequence_type("INVALID")

    with pytest.raises(ValueError, match="invalid sequence type"):
        auxio._get_sequence_type(180.2)

    with pytest.raises(ValueError, match="invalid sequence type"):
        auxio._get_sequence_type({})


@pytest.mark.parametrize(
    "signal_type", list(ESignalType) + list(ESignalType.__members__.values())
)
def test__get_signal_type_type__std(signal_type):
    out_signal_type = auxio._get_signal_type(signal_type)
    assert out_signal_type is ESignalType(signal_type)


def test_get_signal_type__auxins(auxinsdata):
    for timeline_ in auxinsdata.timeline_list.timeline:
        for seq in timeline_.sequence_list.sequence:
            for item in seq.isp_list.isp:
                name = item.signal.name
                signal_type = auxio._get_signal_type(name)
                assert isinstance(signal_type, ESignalType)


def test__get_signal_type__invalid():
    with pytest.raises(ValueError, match="invalid signal type"):
        auxio._get_signal_type("INVALID")

    with pytest.raises(ValueError, match="invalid signal type"):
        auxio._get_signal_type(180.2)

    with pytest.raises(ValueError, match="invalid signal type"):
        auxio._get_signal_type({})


def test__get_swath_map(auxinsdata):
    for timeline_ in auxinsdata.timeline_list.timeline:
        swath_map_info = timeline_.swath_map_list.swath_map
        swath_map = auxio._get_swath_map(swath_map_info)
        assert isinstance(swath_map, Mapping)
        assert all(isinstance(key, int) for key in swath_map)
        assert all(isinstance(value, ESwath) for value in swath_map.values())


def test__get_swath_map__invalid(auxinsdata):
    for timeline_ in auxinsdata.timeline_list.timeline:
        # replicate one value
        swath_map_info = list(timeline_.swath_map_list.swath_map)
        swath_map_info.append(swath_map_info[0])

        with pytest.raises(RuntimeError, match="multiple"):
            auxio._get_swath_map(swath_map_info)


def test_load():
    prog_map = auxio.load_ecc_programs(AUX_INS_DATAFILE)
    assert all(isinstance(item, EEccNumber) for item in prog_map)
    assert all(isinstance(item, EccProgram) for item in prog_map.values())
