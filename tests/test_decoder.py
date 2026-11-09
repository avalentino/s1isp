# SPDX-FileCopyrightText: 2022-2026 Antonio Valentino
#
# SPDX-License-Identifier: Apache-2.0

"""Tests for ISP decoder module."""

import types
import shutil
import typing
import fnmatch
import pathlib

import numpy as np
import pytest

try:
    import fsspec

    HAVE_FSSPEC = True
    del fsspec
except ImportError:
    HAVE_FSSPEC = False


from s1isp.decoder import EUdfDecodingMode, decode_stream
from s1isp.descriptors import (
    PrimaryHeader,
    SecondaryHeaderS1AB,
    SecondaryHeaderS1CD,
)

DATAROOT = pathlib.Path(__file__).parent / "data"
TEST_DATA: typing.Mapping[str, str] = types.MappingProxyType({
    "n": "000000-noise",
    "t": "000008-txcal",
    "e": "000408-echo",
})
TEST_PULSE_SEQ_PRE_T = 2
TEST_PULSE_SEQ_POST_T = 2
TEST_PULSE_SEQ_PRE_N = 3
TEST_PULSE_SEQ_POST_N = 3
TEST_PULSE_SEQ_E = 10
TEST_PULSE_SEQ_STR = (
    f"{'t' * TEST_PULSE_SEQ_PRE_T}{'n' * TEST_PULSE_SEQ_PRE_N}"
    f"{'e' * TEST_PULSE_SEQ_E}"
    f"{'n' * TEST_PULSE_SEQ_POST_N}{'t' * TEST_PULSE_SEQ_POST_T}"
)


class RefDataType(typing.TypedDict):
    primary_header: PrimaryHeader
    secondary_header: SecondaryHeaderS1AB | SecondaryHeaderS1CD
    udf: np.ndarray[tuple[int], np.dtype[np.complex64]]
    decoded_udf: np.ndarray[tuple[int], np.dtype[np.complex64]]


class GenDataType(typing.NamedTuple):
    pulse_sequence: str
    isp_stream: bytes
    ref_data: list[RefDataType]


def mktest_data(pulse_sequence: str) -> GenDataType:
    isp_db = {}
    ref_db = {}
    for key, path in TEST_DATA.items():
        isppath = DATAROOT.joinpath(path).with_suffix(".dat")
        refpath = DATAROOT.joinpath(path).with_suffix(".npz")
        isp_db[key] = isppath.read_bytes()
        ref_data = np.load(refpath, allow_pickle=True)
        ref_data = {
            k: v.item() if "header" in k else v for k, v in ref_data.items()
        }
        ref_db[key] = ref_data

    isp_data = b"".join([isp_db[key] for key in pulse_sequence])
    ref_data = [ref_db[key] for key in pulse_sequence]

    return GenDataType(pulse_sequence, isp_data, ref_data)


@pytest.fixture(scope="module")
def test_data(tmp_path_factory):
    _, isp_data, ref_data = mktest_data(TEST_PULSE_SEQ_STR)
    path = tmp_path_factory.getbasetemp().joinpath("s1a-isp-stream.dat")
    path.write_bytes(isp_data)
    return path, isp_data, ref_data


@pytest.fixture
def isp_stream_path(test_data):
    path, _, _ = test_data
    return path


@pytest.fixture
def isp_stream_data(test_data):
    _, isp_data, _ = test_data
    return isp_data


@pytest.fixture
def isp_stream_ref_data(test_data):
    _, _, ref_data = test_data
    return ref_data


@pytest.mark.parametrize("itype", [str, pathlib.Path])
def test_decode_stream_file(itype, isp_stream_path, isp_stream_ref_data):
    path = itype(isp_stream_path)
    records, _, _ = decode_stream(path)

    # primary headers
    primary_headers = [record.primary_header for record in records]
    ref_primary_headers = [
        item["primary_header"] for item in isp_stream_ref_data
    ]
    assert primary_headers == ref_primary_headers

    # secondary headers
    secondary_headers = [record.secondary_header for record in records]
    ref_secondary_headers = [
        item["secondary_header"] for item in isp_stream_ref_data
    ]
    assert secondary_headers == ref_secondary_headers


def _open_fsspec(path, mode="r"):
    import fsspec

    return fsspec.open(path, mode=mode)


@pytest.mark.parametrize(
    "factory",
    [
        pytest.param(open, id="open"),
        pytest.param(
            _open_fsspec,
            id="fsspec",
            marks=pytest.mark.skipif(
                not HAVE_FSSPEC, reason="fsspec is not available"
            ),
        ),
    ],
)
def test_decode_stream_fd(factory, isp_stream_path, isp_stream_ref_data):
    with factory(isp_stream_path, mode="rb") as fd:
        records, _, _ = decode_stream(fd)
        assert fd.closed is False

    # primary headers
    primary_headers = [record.primary_header for record in records]
    ref_primary_headers = [
        item["primary_header"] for item in isp_stream_ref_data
    ]
    assert primary_headers == ref_primary_headers

    # secondary headers
    secondary_headers = [record.secondary_header for record in records]
    ref_secondary_headers = [
        item["secondary_header"] for item in isp_stream_ref_data
    ]
    assert secondary_headers == ref_secondary_headers


def test_decode_stream_platform_id_error(isp_stream_path, tmp_path):
    name = isp_stream_path.name
    if fnmatch.fnmatch(name, "s1[abcd]-*"):
        name = name[4:]
    assert not fnmatch.fnmatch(name, "s1[abcd]-")
    path = tmp_path / name
    shutil.copy(isp_stream_path, path)

    with pytest.raises(ValueError, match="platform_id"):
        decode_stream(path)


@pytest.mark.parametrize("prefix", ["", "s1a-"])
def test_decode_stream_platform_id(prefix, isp_stream_path, tmp_path):
    name = isp_stream_path.name
    if fnmatch.fnmatch(name, "S1[ABCD]-"):
        name = name[4:]
    assert not fnmatch.fnmatch(name, "S1[ABCD]-")
    path = tmp_path / f"{prefix}{name}"
    shutil.copy(isp_stream_path, path)

    records, _, _ = decode_stream(path, platform_id="S1C")
    record = records[0]
    assert isinstance(record.secondary_header, SecondaryHeaderS1CD)


def test_decode_stream_byte_offset(isp_stream_path):
    all_records, _, _ = decode_stream(isp_stream_path)
    ph = all_records[0].primary_header
    byte_offsets = len(ph.tobytes()) + ph.packet_data_length + 1
    records, _, _ = decode_stream(isp_stream_path, bytes_offset=byte_offsets)
    assert len(records) == len(all_records) - 1

    all_primary_headers = [record.primary_header for record in all_records]
    primary_headers = [record.primary_header for record in records]
    assert primary_headers == all_primary_headers[1:]


@pytest.mark.parametrize("skip", [3])
def test_decode_stream_skip(skip, isp_stream_path):
    all_records, _, _ = decode_stream(isp_stream_path)
    records, _, _ = decode_stream(isp_stream_path, skip=skip)
    assert len(records) == len(all_records) - skip


@pytest.mark.parametrize(
    "mode",
    [
        EUdfDecodingMode.NONE,
        EUdfDecodingMode.EXTRACT,
        EUdfDecodingMode.DECODE,
    ],
)
def test_decode_stream_udf(mode, isp_stream_path, isp_stream_ref_data):
    records, _, _ = decode_stream(isp_stream_path, udf_decoding_mode=mode)

    # primary headers
    primary_headers = [record.primary_header for record in records]
    ref_primary_headers = [
        item["primary_header"] for item in isp_stream_ref_data
    ]
    assert primary_headers == ref_primary_headers

    # secondary headers
    secondary_headers = [record.secondary_header for record in records]
    ref_secondary_headers = [
        item["secondary_header"] for item in isp_stream_ref_data
    ]
    assert secondary_headers == ref_secondary_headers

    record = records[0]

    if mode is EUdfDecodingMode.EXTRACT:
        assert isinstance(record.udf, bytes)
    elif mode is EUdfDecodingMode.DECODE:
        assert isinstance(records[0].udf, np.ndarray)
        assert all(isinstance(item, np.complex64) for item in record.udf)
