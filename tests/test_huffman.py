"""Unit tests for Huffman decoding."""

import itertools

import numpy as np
import pytest

from s1isp import _huffman as huffman

NSAMPLES = 128


BRC = {
    0: (0, 0, 0),
    1: (0, 0, 1),
    2: (0, 1, 0),
    3: (0, 1, 1),
    4: (1, 0, 0),
}


HUFFMAN_CODES = {
    0: {
        (0, 0): 0,
        (0, 1, 0): 1,
        (0, 1, 1, 0): 2,
        (0, 1, 1, 1): 3,
        (1, 0): -0,
        (1, 1, 0): -1,
        (1, 1, 1, 0): -2,
        (1, 1, 1, 1): -3,
    },
    1: {
        (0, 0): 0,
        (0, 1, 0): 1,
        (0, 1, 1, 0): 2,
        (0, 1, 1, 1, 0): 3,
        (0, 1, 1, 1, 1): 4,
        (1, 0): 0,
        (1, 1, 0): -1,
        (1, 1, 1, 0): -2,
        (1, 1, 1, 1, 0): -3,
        (1, 1, 1, 1, 1): -4,
    },
    2: {
        (0, 0): 0,
        (0, 1, 0): 1,
        (0, 1, 1, 0): 2,
        (0, 1, 1, 1, 0): 3,
        (0, 1, 1, 1, 1, 0): 4,
        (0, 1, 1, 1, 1, 1, 0): 5,
        (0, 1, 1, 1, 1, 1, 1): 6,
        (1, 0): 0,
        (1, 1, 0): -1,
        (1, 1, 1, 0): -2,
        (1, 1, 1, 1, 0): -3,
        (1, 1, 1, 1, 1, 0): -4,
        (1, 1, 1, 1, 1, 1, 0): -5,
        (1, 1, 1, 1, 1, 1, 1): -6,
    },
    3: {
        (0, 0, 0): 0,
        (0, 0, 1): 1,
        (0, 1, 0): 2,
        (0, 1, 1, 0): 3,
        (0, 1, 1, 1, 0): 4,
        (0, 1, 1, 1, 1, 0): 5,
        (0, 1, 1, 1, 1, 1, 0): 6,
        (0, 1, 1, 1, 1, 1, 1, 0): 7,
        (0, 1, 1, 1, 1, 1, 1, 1, 0): 8,
        (0, 1, 1, 1, 1, 1, 1, 1, 1): 9,
        (1, 0, 0): 0,
        (1, 0, 1): -1,
        (1, 1, 0): -2,
        (1, 1, 1, 0): -3,
        (1, 1, 1, 1, 0): -4,
        (1, 1, 1, 1, 1, 0): -5,
        (1, 1, 1, 1, 1, 1, 0): -6,
        (1, 1, 1, 1, 1, 1, 1, 0): -7,
        (1, 1, 1, 1, 1, 1, 1, 1, 0): -8,
        (1, 1, 1, 1, 1, 1, 1, 1, 1): -9,
    },
    4: {
        (0, 0, 0): 0,
        (0, 0, 1, 0): 1,
        (0, 0, 1, 1): 2,
        (0, 1, 0, 0): 3,
        (0, 1, 0, 1): 4,
        (0, 1, 1, 0, 0): 5,
        (0, 1, 1, 0, 1): 6,
        (0, 1, 1, 1, 0): 7,
        (0, 1, 1, 1, 1, 0): 8,
        (0, 1, 1, 1, 1, 1, 0): 9,
        (0, 1, 1, 1, 1, 1, 1, 0, 0): 10,
        (0, 1, 1, 1, 1, 1, 1, 0, 1): 11,
        (0, 1, 1, 1, 1, 1, 1, 1, 0, 0): 12,
        (0, 1, 1, 1, 1, 1, 1, 1, 0, 1): 13,
        (0, 1, 1, 1, 1, 1, 1, 1, 1, 0): 14,
        (0, 1, 1, 1, 1, 1, 1, 1, 1, 1): 15,
        (1, 0, 0): 0,
        (1, 0, 1, 0): -1,
        (1, 0, 1, 1): -2,
        (1, 1, 0, 0): -3,
        (1, 1, 0, 1): -4,
        (1, 1, 1, 0, 0): -5,
        (1, 1, 1, 0, 1): -6,
        (1, 1, 1, 1, 0): -7,
        (1, 1, 1, 1, 1, 0): -8,
        (1, 1, 1, 1, 1, 1, 0): -9,
        (1, 1, 1, 1, 1, 1, 1, 0, 0): -10,
        (1, 1, 1, 1, 1, 1, 1, 0, 1): -11,
        (1, 1, 1, 1, 1, 1, 1, 1, 0, 0): -12,
        (1, 1, 1, 1, 1, 1, 1, 1, 0, 1): -13,
        (1, 1, 1, 1, 1, 1, 1, 1, 1, 0): -14,
        (1, 1, 1, 1, 1, 1, 1, 1, 1, 1): -15,
    },
}


HCODE_LUTS = {
    brc: np.fromiter(HUFFMAN_CODES[brc].values(), dtype=np.int8)
    for brc in HUFFMAN_CODES
}


def get_huffman_data(brc: int, nsamples: int | None = None):
    codes = list(HUFFMAN_CODES[brc].keys())
    values = list(HUFFMAN_CODES[brc].values())

    ncodes = len(codes)
    if nsamples is None:
        nsamples = ncodes
        factor = 1
    else:
        factor = int(np.ceil(nsamples / ncodes))

    bits = (codes * factor)[:nsamples]
    values = (values * factor)[:nsamples]

    bits = np.fromiter(itertools.chain.from_iterable(bits), dtype=np.uint8)

    return bits, values


@pytest.mark.parametrize("brc", [0, 1, 2, 3, 4])
def test_huffman_decode(brc):
    bits, values = get_huffman_data(brc)
    nsamples = len(values)
    out = huffman.decode(bits, nsamples, brc)
    lut = HCODE_LUTS[brc]
    outvalues = lut[out]
    np.testing.assert_array_equal(values, outvalues)


@pytest.mark.parametrize("brc", [0, 1, 2, 3, 4])
def test_huffman_decode_with_count(brc):
    bits, values = get_huffman_data(brc)
    nsamples = len(values)
    out, count = huffman.decode(bits, nsamples, brc, count=True)
    assert count == len(bits)
    lut = HCODE_LUTS[brc]
    outvalues = lut[out]
    np.testing.assert_array_equal(values, outvalues)


@pytest.mark.parametrize("brc", [0, 1, 2, 3, 4])
def test_huffman_decode_with_outbuf(brc):
    bits, values = get_huffman_data(brc)
    nsamples = len(values)
    buf = np.zeros(nsamples, dtype=np.uint8)
    out = huffman.decode(bits, nsamples, brc, out=buf)
    np.testing.assert_array_equal(out, buf)
    # assert out.data is buf.data  # TODO: check
    lut = HCODE_LUTS[brc]
    outvalues = lut[out]
    np.testing.assert_array_equal(values, outvalues)


@pytest.mark.parametrize("brc", [0, 1, 2, 3, 4])
def test_huffman_decode_with_outbuf_and_count(brc):
    bits, values = get_huffman_data(brc)
    nsamples = len(values)
    buf = np.zeros(nsamples, dtype=np.uint8)
    out, count = huffman.decode(bits, nsamples, brc, out=buf, count=True)
    assert count == len(bits)
    np.testing.assert_array_equal(out, buf)
    # assert out.data is buf.data  # TODO: check
    lut = HCODE_LUTS[brc]
    outvalues = lut[out]
    np.testing.assert_array_equal(values, outvalues)


@pytest.mark.parametrize("brc", [0, 1, 2, 3, 4])
def test_huffman_decode_cycle_to_128(brc):
    bits, values = get_huffman_data(brc, nsamples=NSAMPLES)
    nsamples = len(values)
    out = huffman.decode(bits, nsamples, brc)
    lut = HCODE_LUTS[brc]
    outvalues = lut[out]
    np.testing.assert_array_equal(values, outvalues)


@pytest.mark.parametrize("brc", [0, 1, 2, 3, 4])
def test_huffman_decode_partial(brc):
    bits, values = get_huffman_data(brc, nsamples=NSAMPLES)
    nsamples = len(values)
    bits = np.resize(bits, bits.size * 2)
    out = huffman.decode(bits, nsamples, brc)
    lut = HCODE_LUTS[brc]
    outvalues = lut[out]
    np.testing.assert_array_equal(values, outvalues)
