"""Unit tests for ECC program."""

import itertools
from collections.abc import Mapping

import pytest

from s1isp.enums import (
    ESwath,
    EEccNumber,
    ESensorMode,
    ESignalType,
    ESequenceType,
)
from s1isp.eccprogram import (
    PulseType,
    EccProgram,
    EccSequence,
    EccSequenceItem,
    NoExactRepetitionError,
)


@pytest.mark.parametrize(
    ("signal_type", "swath", "count"),
    [
        pytest.param(ESignalType.ECHO, ESwath.IW1, None, id="enum-no-count"),
        pytest.param(ESignalType.ECHO, ESwath.IW1, 3, id="enum-count"),
        pytest.param(
            ESignalType.ECHO.value, ESwath.IW1.value, None, id="str-no-count"
        ),
        pytest.param(
            ESignalType.ECHO.value, ESwath.IW1.value, 3, id="str-count"
        ),
    ],
)
def test_ecc_sequence_item(signal_type, swath, count):
    if count is None:
        args = [signal_type, swath]
    else:
        args = [signal_type, swath, count]

    sequence_item = EccSequenceItem(*args)

    assert sequence_item.signal_type == ESignalType(signal_type)
    assert sequence_item.swath == ESwath(swath)

    expected_len = 1 if count is None else count
    assert len(sequence_item) == expected_len


@pytest.mark.parametrize("count", [5, 1, 0, None])
def test_ecc_sequence_item__iter(count):
    if count is None:
        sequence_item = EccSequenceItem(ESignalType.ECHO, ESwath.IW1)
        expected_len = 1
    else:
        sequence_item = EccSequenceItem(ESignalType.ECHO, ESwath.IW1, count)
        expected_len = count

    item = PulseType(swath=ESwath.IW1, signal=ESignalType.ECHO)
    items = list(sequence_item)

    assert len(items) == expected_len
    assert items == [item] * expected_len


def test_ecc_sequence_item__invalid_count():
    with pytest.raises(ValueError, match="invalid count value"):
        EccSequenceItem(ESignalType.ECHO, ESwath.IW1, -1)


@pytest.mark.parametrize(
    "sequence_type",
    [
        ESequenceType.PREAMBLE,
        ESequenceType.POSTAMBLE,
        "PREAMBLE",
        "POSTAMBLE",
    ],
)
def test_ecc_sequence__pre_post(sequence_type):
    items = [
        EccSequenceItem(sigtype=ESignalType.SILENT, swath=ESwath.S1, count=10),
        EccSequenceItem(sigtype=ESignalType.NOISE, swath=ESwath.S3, count=10),
        EccSequenceItem(sigtype=ESignalType.TX_CAL.value, swath="S3"),
        EccSequenceItem(sigtype=ESignalType.RX_CAL, swath=ESwath.S3, count=3),
        EccSequenceItem(sigtype=ESignalType.NOISE, swath=ESwath.S3, count=10),
    ]
    ecc_sequence_len = 34
    seq = EccSequence(sequence_type=sequence_type, items=items, repeat=False)

    assert seq.sequence_type == ESequenceType(sequence_type)
    assert seq.repeat is False
    assert len(seq) == ecc_sequence_len
    assert seq.get_isp_count() == ecc_sequence_len - len(items[0])  # SILENT
    assert list(seq) == list(itertools.chain(*items))


@pytest.mark.parametrize("sequence_type", [ESequenceType.IMAGING, "IMAGING"])
def test_ecc_sequence__imaging(sequence_type):
    items = [
        EccSequenceItem(sigtype=ESignalType.NOISE, swath=ESwath.S3),
        EccSequenceItem(sigtype=ESignalType.ECHO.value, swath="S3", count=25),
        EccSequenceItem(sigtype=ESignalType.NOISE, swath=ESwath.S3, count=13),
        EccSequenceItem(sigtype=ESignalType.ECHO, swath=ESwath.S3, count=25),
    ]
    ecc_sequence_len = 64
    seq = EccSequence(sequence_type=sequence_type, items=items, repeat=True)

    assert seq.sequence_type == ESequenceType(sequence_type)
    assert seq.repeat is True
    assert len(seq) == ecc_sequence_len
    assert seq.get_isp_count() == ecc_sequence_len
    assert list(seq) == list(itertools.chain(*items))


def test_ecc_sequence__invalid_seq_type():
    with pytest.raises(ValueError, match="is not a valid"):
        EccSequence(sequence_type="INVALID", items=[])


@pytest.mark.parametrize(
    ("mode", "ecc_num", "repetitions"),
    [
        pytest.param(ESensorMode.S3, EEccNumber.S3, None, id="enums"),
        pytest.param(
            ESensorMode.S3.value, EEccNumber.S3.value, None, id="str"
        ),
        pytest.param(ESensorMode.IW, EEccNumber.IW, 0, id="zero-repeat"),
        pytest.param(ESensorMode.EW, EEccNumber.EW, 1, id="one-repeat"),
        pytest.param(ESensorMode.RF, EEccNumber.RFC, 2, id="two-repeat"),
    ],
)
def test_ecc_program__initializer(mode, ecc_num, repetitions):
    sequences = [
        EccSequence(ESequenceType.PREAMBLE, []),
        EccSequence(ESequenceType.IMAGING, [], repeat=True),
        EccSequence(ESequenceType.POSTAMBLE, []),
    ]
    if repetitions is None:
        program = EccProgram(mode, ecc_num, sequences, swath_map={})
    else:
        program = EccProgram(
            mode, ecc_num, sequences, swath_map={}, repetitions=repetitions
        )
    assert program.mode == ESensorMode(mode)
    assert program.ecc_number == EEccNumber(ecc_num)
    assert isinstance(program.preamble, EccSequence)
    assert program.preamble.sequence_type, ESequenceType.PREAMBLE
    assert isinstance(program.imaging, EccSequence)
    assert program.imaging.sequence_type, ESequenceType.IMAGING
    assert isinstance(program.postamble, EccSequence)
    assert program.postamble.sequence_type, ESequenceType.POSTAMBLE
    assert isinstance(program.swath_map, Mapping)

    repetitions = 1 if repetitions is None else repetitions
    assert program.repetitions == repetitions

    seq_list = list(program.iter_sequences())
    assert len(seq_list) == 2 + repetitions
    assert seq_list[0].sequence_type == ESequenceType.PREAMBLE
    assert seq_list[-1].sequence_type == ESequenceType.POSTAMBLE
    assert all(
        seq.sequence_type == ESequenceType.IMAGING for seq in seq_list[1:-1]
    )


@pytest.mark.parametrize(
    "sequences",
    [
        pytest.param(
            [
                EccSequence(ESequenceType.PREAMBLE, []),
                EccSequence(ESequenceType.PREAMBLE, []),
                EccSequence(ESequenceType.IMAGING, [], repeat=True),
                EccSequence(ESequenceType.POSTAMBLE, []),
            ],
            id="multi-preamble",
        ),
        pytest.param(
            [
                EccSequence(ESequenceType.PREAMBLE, []),
                EccSequence(ESequenceType.IMAGING, [], repeat=True),
                EccSequence(ESequenceType.IMAGING, [], repeat=True),
                EccSequence(ESequenceType.POSTAMBLE, []),
            ],
            id="multi-imaging",
        ),
        pytest.param(
            [
                EccSequence(ESequenceType.PREAMBLE, []),
                EccSequence(ESequenceType.IMAGING, [], repeat=True),
                EccSequence(ESequenceType.POSTAMBLE, []),
                EccSequence(ESequenceType.POSTAMBLE, []),
            ],
            id="multi-postamble",
        ),
    ],
)
def test_ecc_program__invalid_sequences(sequences):
    with pytest.raises(ValueError, match="multiple"):
        EccProgram(ESensorMode.S3, EEccNumber.S3, sequences)


def test_ecc_program__invalid_repetitions():
    sequences = [
        EccSequence(ESequenceType.IMAGING, [], repeat=True),
    ]

    with pytest.raises(ValueError, match="positive integer"):
        EccProgram(
            ESensorMode.S3,
            EEccNumber.S3,
            sequences=sequences,
            repetitions=-1,
        )

    with pytest.raises(TypeError, match="'repetitions' must be an integer"):
        EccProgram(
            ESensorMode.S3,
            EEccNumber.S3,
            sequences=sequences,
            swath_map={},
            repetitions=1.1,
        )


@pytest.mark.parametrize(
    "sequences",
    [
        pytest.param(
            [
                EccSequence(ESequenceType.PREAMBLE, [], repeat=True),
                EccSequence(ESequenceType.IMAGING, [], repeat=True),
                EccSequence(ESequenceType.POSTAMBLE, []),
            ],
            id="pre",
        ),
        pytest.param(
            [
                EccSequence(ESequenceType.PREAMBLE, []),
                EccSequence(ESequenceType.IMAGING, [], repeat=True),
                EccSequence(ESequenceType.POSTAMBLE, [], repeat=True),
            ],
            id="post",
        ),
    ],
)
def test_ecc_program__invalid_pre_post_repeat(sequences):
    with pytest.warns(UserWarning, match="unexpectedly"):
        EccProgram(
            ESensorMode.S3,
            EEccNumber.S3,
            sequences=sequences,
            repetitions=1,
        )


def test_ecc_program__invalid_imaging_repetitions():
    sequences = [
        EccSequence(ESequenceType.PREAMBLE, []),
        EccSequence(ESequenceType.IMAGING, [], repeat=False),
        EccSequence(ESequenceType.POSTAMBLE, []),
    ]

    with pytest.warns(UserWarning, match="repeat=False"):
        EccProgram(
            ESensorMode.S3,
            EEccNumber.S3,
            sequences=sequences,
            repetitions=2,
        )


@pytest.fixture
def s3sequences():
    return [
        EccSequence(
            ESequenceType.PREAMBLE,
            [
                EccSequenceItem(
                    sigtype=ESignalType.SILENT, swath=ESwath.S3, count=90
                ),
                EccSequenceItem(
                    sigtype=ESignalType.NOISE, swath=ESwath.S3, count=10
                ),
            ],
        ),
        EccSequence(
            ESequenceType.IMAGING,
            [
                EccSequenceItem(
                    sigtype=ESignalType.ECHO, swath=ESwath.S3, count=100
                ),
            ],
            repeat=True,
        ),
        EccSequence(
            ESequenceType.POSTAMBLE,
            [
                EccSequenceItem(
                    sigtype=ESignalType.NOISE, swath=ESwath.S3, count=100
                ),
            ],
        ),
    ]


@pytest.mark.parametrize(
    "repetitions",
    [
        pytest.param(None, id="no-repeat"),
        pytest.param(1, id="repeat-one"),
        pytest.param(2, id="repeat-twice"),
    ],
)
def test_ecc_program__len(repetitions, s3sequences):
    if repetitions is not None:
        program = EccProgram(
            ESensorMode.S3, EEccNumber.S3, s3sequences, repetitions=repetitions
        )
    else:
        program = EccProgram(ESensorMode.S3, EEccNumber.S3, s3sequences)
        repetitions = 1
    assert len(program) == 200 + 100 * repetitions


def test_ecc_program__compute_repetitions(s3sequences):
    program = EccProgram(ESensorMode.S3, EEccNumber.S3, s3sequences)
    repetitions = program.compute_repetitions(310)
    assert repetitions == 2


def test_ecc_program__compute_repetitions__strict(s3sequences):
    program = EccProgram(ESensorMode.S3, EEccNumber.S3, s3sequences)

    repetitions = program.compute_repetitions(311)
    assert repetitions == 2

    with pytest.raises(NoExactRepetitionError):
        program.compute_repetitions(311, strict=True)

    repetitions = program.compute_repetitions(11)
    assert repetitions == 0

    with pytest.raises(NoExactRepetitionError):
        program.compute_repetitions(11, strict=True)


def test_ecc_program__compute_repetitions__invalid_target(s3sequences):
    program = EccProgram(ESensorMode.S3, EEccNumber.S3, s3sequences)

    with pytest.raises(ValueError, match="negative"):
        program.compute_repetitions(-1)


def test_ecc_program__iter(s3sequences):
    program = EccProgram(ESensorMode.S3, EEccNumber.S3, s3sequences)

    pulses = list(program)
    assert len(pulses) == len(program)
    assert all(isinstance(pulse, PulseType) for pulse in program)
    assert all(pulse.swath == ESwath.S3 for pulse in program)
    assert all(pulse.signal == ESignalType.SILENT for pulse in pulses[:90])
    assert all(pulse.signal == ESignalType.NOISE for pulse in pulses[90:100])
    assert all(pulse.signal == ESignalType.ECHO for pulse in pulses[100:200])
    assert all(pulse.signal == ESignalType.NOISE for pulse in pulses[200:])
