"""Tests for ISP iser data field decoding."""

import bpack
import numpy as np
import bitstruct as bs

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

    out = align_quads(ie, io, qe, qo, nq//2)
    np.testing.assert_array_equal(out, cdata[:cdata.size//2])


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
    fdata[:2**(nbits-1)] = np.arange(2**(nbits-1))
    fdata[2**(nbits-1):] = -fdata[:2**(nbits-1)]
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


def test_decode_txcal(txcal_data, txcal_ref_data):
    shdata = txcal_data[PHSIZE : PHSIZE + SHSIZE]
    secondary_header = PacketSecondaryHeader.frombytes(shdata)

    rcss = secondary_header.radar_configuration_support_service
    assert rcss.ses_sbb_message.signal_type == ESesSignalType.tx_cal

    nq = secondary_header.radar_sample_count_service.number_of_quads
    baqmod = rcss.baq_mode
    tstmod = secondary_header.fixed_ancillary_data_service.test_mode
    data = decode_ud(txcal_data[PHSIZE + SHSIZE:], nq, baqmod, tstmod)
    np.testing.assert_array_equal(data, txcal_ref_data["udf"])


def test_decode_noise(noise_data, noise_ref_data):
    shdata = noise_data[PHSIZE : PHSIZE + SHSIZE]
    secondary_header = PacketSecondaryHeader.frombytes(shdata)

    rcss = secondary_header.radar_configuration_support_service
    assert rcss.ses_sbb_message.signal_type == ESesSignalType.noise

    nq = secondary_header.radar_sample_count_service.number_of_quads
    baqmod = rcss.baq_mode
    tstmod = secondary_header.fixed_ancillary_data_service.test_mode
    data = decode_ud(noise_data[PHSIZE + SHSIZE:], nq, baqmod, tstmod)
    np.testing.assert_array_equal(data, noise_ref_data["udf"])
