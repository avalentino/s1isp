"""Tests for ISP user data field decoding."""

import bpack
import numpy as np
import bitstruct as bs
from test_huffman import get_huffman_data, BRC, HCODE_LUTS, HUFFMAN_CODES
from test_huffman import NSAMPLES as BLOCKSIZE

from s1isp.udf import align_quads, bypass_decode, huffman_decode, decode_ud
from s1isp.descriptors import (
    ESesSignalType,
    PacketPrimaryHeader,
    PacketSecondaryHeader,
)

PHSIZE = bpack.calcsize(PacketPrimaryHeader, bpack.EBaseUnits.BYTES)
SHSIZE = bpack.calcsize(PacketSecondaryHeader, bpack.EBaseUnits.BYTES)


def make_quats(nq: int = 100):
    n_cpx_samples = 2 * nq
    n_flt_smaples = 2 * n_cpx_samples
    fdata = np.arange(n_flt_smaples, dtype=np.float32)
    cdata = np.frombuffer(fdata.data, dtype=np.complex64)

    ie = fdata[0::4]
    io = fdata[2::4]
    qe = fdata[1::4]
    qo = fdata[3::4]

    return cdata, ie, io, qe, qo


def test_align_quads(nq: int = 100):
    cdata, ie, io, qe, qo = make_quats(nq)
    out = align_quads(ie, io, qe, qo)
    np.testing.assert_array_equal(out, cdata)


def test_align_quads_nq(nq: int = 100):
    cdata, ie, io, qe, qo = make_quats(nq)

    out = align_quads(ie, io, qe, qo, nq)
    np.testing.assert_array_equal(out, cdata)

    out = align_quads(ie, io, qe, qo, nq // 2)
    np.testing.assert_array_equal(out, cdata[: cdata.size // 2])


def test_align_quads_out(nq: int = 100):
    cdata, ie, io, qe, qo = make_quats(nq)

    buf = np.zeros_like(cdata)
    out = align_quads(ie, io, qe, qo, out=buf)
    np.testing.assert_array_equal(out, cdata)
    np.testing.assert_array_equal(out, buf)
    assert out is buf


def make_bypass(nbits: int = 10):
    n_flt_smaples = 2**10
    nq = n_flt_smaples // 4

    fdata = np.zeros(n_flt_smaples, dtype=np.float32)
    fdata[: 2 ** (nbits - 1)] = np.arange(2 ** (nbits - 1))
    fdata[2 ** (nbits - 1) :] = -fdata[: 2 ** (nbits - 1)]
    cdata = np.frombuffer(fdata.data, dtype=np.complex64)
    idata = np.arange(n_flt_smaples, dtype=np.int16)

    ie = idata[0::4]
    io = idata[2::4]
    qe = idata[1::4]
    qo = idata[3::4]
    nwords = int(np.ceil((nq * nbits) / 16))
    pad = nwords * 16 - nq * nbits

    if pad:
        fmt = f">{'u10'*nq}p{pad}"
    else:
        fmt = f">{'u10'*nq}"

    data = b"".join([bs.pack(fmt, *seq) for seq in [ie, io, qe, qo]])

    return cdata, data, nq


def test_bypass_decode(nbits=10):
    cdata, data, nq = make_bypass(nbits)
    out = bypass_decode(data, nq)
    np.testing.assert_array_equal(out, cdata)


def test_bypass_decode_out(nbits=10):
    cdata, data, nq = make_bypass(nbits)
    buf = np.zeros_like(cdata)
    out = bypass_decode(data, nq, out=buf)
    np.testing.assert_array_equal(out, cdata)
    np.testing.assert_array_equal(buf, cdata)
    assert buf is out


def get_fdbaq_channel(
    blocksize: int = BLOCKSIZE, samples: int = None, header=False
):
    nblocks = len(HUFFMAN_CODES)
    if samples is None:
        samples = nblocks * blocksize
    if header == "thidx":
        thidx = np.arange(blocksize, blocksize + nblocks, dtype=np.uint8)
        thidx_bits = np.unpackbits(thidx[:, None], axis=1)
    else:
        thidx = None

    brcs = []
    bits = []
    values = []
    for bidx, brc in enumerate(HUFFMAN_CODES):
        brcs.append(brc)
        if header == "thidx":
            bits.extend(thidx_bits[bidx])
        elif header:
            bits.extend(BRC[brc])

        bits_seq, val_seq = get_huffman_data(brc, blocksize)
        bits.extend(bits_seq.tolist())
        values.extend(val_seq)

    nbits = len(bits)
    nwords = int(np.ceil(nbits / 16))
    pad = nwords * 16 - nbits
    bits.extend([0] * pad)
    nbits = len(bits)
    assert len(bits) % 16 == 0

    return bits, values, brcs, thidx, pad


def get_fdbaq_stream(blocksize):
    ie_bits, ie_values, brcs, _, ie_pad = get_fdbaq_channel(
        blocksize, header=True
    )
    io_bits, io_values, _, _, io_pad = get_fdbaq_channel(blocksize)
    qe_bits, qe_values, _, thidx, qe_pad = get_fdbaq_channel(
        blocksize, header="thidx"
    )
    qo_bits, qo_values, _, _, qo_pad = get_fdbaq_channel(blocksize)

    assert ie_pad + io_pad + qe_pad + qo_pad > 1

    bits = np.asarray(ie_bits + io_bits + qe_bits + qo_bits, dtype=np.uint8)

    return bits, [ie_values, io_values, qe_values, qo_values], brcs, thidx


def test_huffman_decode(blocksize=BLOCKSIZE):
    bits, values, brcs, thidx = get_fdbaq_stream(blocksize)
    ie_values, io_values, qe_values, qo_values = values
    assert len(ie_values) == len(io_values) == len(qe_values) == len(qo_values)
    nq = len(ie_values)

    ie, io, qe, qo, brc_data, thidx_data = huffman_decode(bits, nq)

    np.testing.assert_array_equal(brcs, brc_data)
    np.testing.assert_array_equal(thidx, thidx_data)

    ie_hcodes = np.zeros(nq, dtype=np.int8)
    io_hcodes = np.zeros(nq, dtype=np.int8)
    qe_hcodes = np.zeros(nq, dtype=np.int8)
    qo_hcodes = np.zeros(nq, dtype=np.int8)
    for bidx, brc_value in enumerate(brc_data):
        i0 = bidx * blocksize
        i1 = min(i0 + blocksize, nq)
        lut = HCODE_LUTS[brc_value]
        ie_hcodes[i0:i1] = lut[ie[i0:i1]]
        io_hcodes[i0:i1] = lut[io[i0:i1]]
        qe_hcodes[i0:i1] = lut[qe[i0:i1]]
        qo_hcodes[i0:i1] = lut[qo[i0:i1]]

    np.testing.assert_array_equal(ie_hcodes, ie_values)
    np.testing.assert_array_equal(io_hcodes, io_values)
    np.testing.assert_array_equal(qe_hcodes, qe_values)
    np.testing.assert_array_equal(qo_hcodes, qo_values)


def test_decode_txcal(txcal_data, txcal_ref_data):
    shdata = txcal_data[PHSIZE : PHSIZE + SHSIZE]
    secondary_header = PacketSecondaryHeader.frombytes(shdata)

    rcss = secondary_header.radar_configuration_support_service
    assert rcss.ses_sbb_message.signal_type == ESesSignalType.tx_cal

    nq = secondary_header.radar_sample_count_service.number_of_quads
    baqmod = rcss.baq_mode
    tstmod = secondary_header.fixed_ancillary_data_service.test_mode
    data = decode_ud(txcal_data[PHSIZE + SHSIZE :], nq, baqmod, tstmod)
    np.testing.assert_array_equal(data, txcal_ref_data["udf"])


def test_decode_noise(noise_data, noise_ref_data):
    shdata = noise_data[PHSIZE : PHSIZE + SHSIZE]
    secondary_header = PacketSecondaryHeader.frombytes(shdata)

    rcss = secondary_header.radar_configuration_support_service
    assert rcss.ses_sbb_message.signal_type == ESesSignalType.noise

    nq = secondary_header.radar_sample_count_service.number_of_quads
    baqmod = rcss.baq_mode
    tstmod = secondary_header.fixed_ancillary_data_service.test_mode
    data = decode_ud(noise_data[PHSIZE + SHSIZE :], nq, baqmod, tstmod)
    np.testing.assert_array_equal(data, noise_ref_data["udf"])


def test_decode_echo(echo_data, echo_ref_data):
    shdata = echo_data[PHSIZE : PHSIZE + SHSIZE]
    secondary_header = PacketSecondaryHeader.frombytes(shdata)

    rcss = secondary_header.radar_configuration_support_service
    assert rcss.ses_sbb_message.signal_type == ESesSignalType.echo

    nq = secondary_header.radar_sample_count_service.number_of_quads
    baqmod = rcss.baq_mode
    tstmod = secondary_header.fixed_ancillary_data_service.test_mode
    data = decode_ud(echo_data[PHSIZE + SHSIZE :], nq, baqmod, tstmod)
    np.testing.assert_allclose(data.real, echo_ref_data["udf"].real, atol=2e-6)
    np.testing.assert_allclose(data.imag, echo_ref_data["udf"].imag, atol=2e-6)
    np.testing.assert_allclose(
        np.abs(data), np.abs(echo_ref_data["udf"]), atol=3e-6
    )
