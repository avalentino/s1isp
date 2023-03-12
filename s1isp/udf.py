"""Tools and functions for user data field decoding.

The specification of algorithms for the user data field decoding is
in the "Sentinel-1 SAR Space Packet Protocol Data Unit" document
(S1-IF-ASD-PL-0007) issue 13 section 3.3.
"""

import enum
from typing import Optional

import numpy as np
import bpack.np

from .descriptors import EBaqMode, ETestMode, RadarConfigurationSupportService
from .constants_and_luts import get_baq_lut

BLOCKSIZE = 128


class EDataFormatType(enum.Enum):
    """Data Format Type.

    See S1-IF-ASD-PL-0007 section 3.3.2 Table 3.3-2.
    """

    A = "A"
    B = "B"
    C = "C"
    D = "D"


def get_data_format_type(
    baqmod: EBaqMode, tstmod: ETestMode
) -> EDataFormatType:
    """Return the data format type.

    See S1-IF-ASD-PL-0007 section 3.3.2 Table 3.3-2.
    """
    tstmod = ETestMode(tstmod)
    baqmod = EBaqMode(baqmod)

    bypass_modes = {
        ETestMode.contingency_rxm_fully_bypassed,
        ETestMode.bypass,
    }
    oper_modes = {
        ETestMode.default,
        ETestMode.contingency_rxm_fully_operational,
        ETestMode.oper,
    }

    if tstmod in bypass_modes:
        if baqmod == EBaqMode.BYPASS:
            return EDataFormatType.A
    elif tstmod in oper_modes:
        if baqmod == EBaqMode.BYPASS:
            return EDataFormatType.B
        elif baqmod in {EBaqMode.BAQ3, EBaqMode.BAQ4, EBaqMode.BAQ5}:
            return EDataFormatType.C
        elif baqmod in {
            EBaqMode.FDBAQ_MODE_0,
            EBaqMode.FDBAQ_MODE_1,
            EBaqMode.FDBAQ_MODE_2,
        }:
            return EDataFormatType.D

    raise ValueError(
        f"Invalid combination: baqmod={baqmod.name}, testmod={tstmod.name}."
    )


def align_quads(
    ie: np.ndarray,
    io: np.ndarray,
    qe: np.ndarray,
    qo: np.ndarray,
    nq: Optional[int] = None,
    *,
    out: np.ndarray = None,
) -> np.ndarray:
    """Align decoded data channels.

    Align in phase (i) and in quadrature (q) components of even (e)
    and odd (o) samples into a contiguois array of complex samples.
    """
    nq_max = min([len(ie), len(io), len(qe), len(qo)])
    if nq is None:
        nq = nq_max
    assert nq <= nq_max

    if out is None:
        out = np.empty(nq * 2, dtype=np.complex64)
    assert out.size == 2 * nq

    out.real[::2] = ie[:nq]
    out.real[1::2] = io[:nq]
    out.imag[::2] = qe[:nq]
    out.imag[1::2] = qo[:nq]

    return out


def bypass_decode(
    data: bytes,
    nq: int,
    *,
    out: Optional[np.ndarray] = None,
) -> np.ndarray:
    """Decode user data for data format A and B (bypass algorithm).

    See section 4 and 4.2 of S1-IF-ASD-PL-0007.
    """
    bits_per_sample = 10
    nw = int(np.ceil(bits_per_sample / 16 * nq))
    assert len(data) >= (2 * nw) * 4
    nbytes = nw * 2

    ie = bpack.np.unpackbits(
        data[:nbytes],
        bits_per_sample=bits_per_sample,
        sign_mode=bpack.np.ESignMode.SIGN_AND_MOD,
    )
    io = bpack.np.unpackbits(
        data[nbytes : 2 * nbytes],
        bits_per_sample=bits_per_sample,
        sign_mode=bpack.np.ESignMode.SIGN_AND_MOD,
    )
    qe = bpack.np.unpackbits(
        data[2 * nbytes : 3 * nbytes],
        bits_per_sample=bits_per_sample,
        sign_mode=bpack.np.ESignMode.SIGN_AND_MOD,
    )
    qo = bpack.np.unpackbits(
        data[3 * nbytes :],
        bits_per_sample=bits_per_sample,
        sign_mode=bpack.np.ESignMode.SIGN_AND_MOD,
    )

    return align_quads(ie, io, qe, qo, nq, out=out)


def baq_decode(
    data: bytes,
    nq: int,
    baqmod: EBaqMode,
    *,
    out: Optional[np.ndarray] = None,
    blocksize: int = BLOCKSIZE,
) -> np.ndarray:
    """Decode user data for data format C (Decimation + BAQ algorithm).

    Sentinel-1 supports Block Adaptive Quantisation (BAQ) to 3, 4, and 5 bits.

    See section 4 and 4.3 of S1-IF-ASD-PL-0007.
    """
    bits_per_sample = baqmod.value
    nb = int(np.ceil(nq / blocksize))  # == ceil(2 * nq / 256)

    nw_ie = int(np.ceil(bits_per_sample * nq / 16))
    nw_io = nw_ie
    nw_qe = int(np.ceil((bits_per_sample * nq + 8 * nb) / 16))
    nw_qo = nw_ie
    assert len(data) >= 2 * (nw_ie + nw_io + nw_qe + nw_qo)

    offset = 0
    nbytes = 2 * nw_ie
    ie = bpack.np.unpackbits(
        data[offset : offset + nbytes], bits_per_sample=bits_per_sample
    )

    offset += nbytes
    nbytes = 2 * nw_io
    io = bpack.np.unpackbits(
        data[offset : offset + nbytes], bits_per_sample=bits_per_sample
    )

    offset += nbytes
    nbytes = 2 * nw_qe
    blockstride = bits_per_sample * blocksize + 8
    qe = bpack.np.unpackbits(
        data[offset + 1 : offset + nbytes],  # NOTE: extra offset for THIDX
        bits_per_sample=bits_per_sample,
        samples_per_block=blocksize,
        blockstride=blockstride,
    )
    assert blockstride % 8 == 0
    step = blockstride // 8
    thidx_data = np.frombuffer(data[offset : offset + nbytes], dtype=np.uint8)
    thidx_data = thidx_data[::step]

    offset += nbytes
    nbytes = 2 * nw_qo
    qo = bpack.np.unpackbits(
        data[offset : offset + nbytes], bits_per_sample=bits_per_sample
    )

    # TODO: use out directly
    decoded_ie = np.empty(len(ie), dtype=np.float32)
    decoded_io = np.empty(len(io), dtype=np.float32)
    decoded_qe = np.empty(len(qe), dtype=np.float32)
    decoded_qo = np.empty(len(qo), dtype=np.float32)
    for bidx, thidx in enumerate(thidx_data):
        lut = get_baq_lut(baqmod, thidx)
        idx = slice(bidx * blocksize, (bidx + 1) * blocksize)
        decoded_ie[idx] = lut[ie[idx]]
        decoded_io[idx] = lut[io[idx]]
        decoded_qe[idx] = lut[qe[idx]]
        decoded_qo[idx] = lut[qo[idx]]

    return align_quads(
        decoded_ie, decoded_io, decoded_qe, decoded_qo, nq, out=out
    )


def fdbaq_decode(*args, **kwargs):
    """Decode user data for data format D (Decimatiion + FDBAQ algorithm).

    FDBAQ is the Flexible Dynamic Block Adaptive Quantisation.
    It is the baseline compression mode for echoes in sicence data.

    See section 4 and 4.4 of S1-IF-ASD-PL-0007.
    """
    raise NotImplementedError("fdbaq_decode")


def decode_ud(
    data: bytes,
    nq: int,
    rcss: RadarConfigurationSupportService,
    tstmod: ETestMode,
) -> np.ndarray:
    """Decode user data for data."""
    baqmod = rcss.baq_mode
    data_format_type = get_data_format_type(baqmod, tstmod)

    if data_format_type == EDataFormatType.A:
        return bypass_decode(data, nq)
    elif data_format_type == EDataFormatType.B:
        return bypass_decode(data, nq)
    elif data_format_type == EDataFormatType.C:
        return baq_decode(data, nq, baqmod=baqmod)
    elif data_format_type == EDataFormatType.D:
        return fdbaq_decode(data, rcss)
    else:
        raise ValueError(f"Invalid data format type: '{data_format_type}'.")
