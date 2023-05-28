# cython: language_level=3, boundscheck=False

"""Extension module for Huffman decoding of Sentinel-1 RAW data."""

from libc.stdint cimport uint8_t


cdef extern from "huffman.h" nogil:
    int huffman_brc0(int, const uint8_t*, int, uint8_t*)
    int huffman_brc1(int, const uint8_t*, int, uint8_t*)
    int huffman_brc2(int, const uint8_t*, int, uint8_t*)
    int huffman_brc3(int, const uint8_t*, int, uint8_t*)
    int huffman_brc4(int, const uint8_t*, int, uint8_t*)


import numpy as np
cimport numpy as cnp


class HuffmanDecodingError(ValueError):
    pass


def decode(
    const uint8_t[::1] data not None,
    int nsamples,
    int brc,
    uint8_t[::1] out=None,
    bint count=False,
):
    """Decode Huffman encoded data according to the specified BRC code.

    This function decodes both M-Codes and the sign of each sample,
    but the returned values are unit8 that can be used as indices for a
    look-up table.
    Negative values are encoded into uint8 samples as follows::

      [0, 1,, 2, 3, -0, -1, -2, -3] --> [0, 1,, 2, 3, 4, 5, 6, 7]
    
    Please note that the double "zero" value (positive and negative) is
    preserved to allow to univocally map the returned values to the original
    data.
    
    :param data: np.ndarray or typed memory view of uint8 values
        bits of the Huffman encoded data store one per (uint8) element.
        The sequence can be obtained using the np.unpackbits function.
    :param nsamples: int
        number of samples expected in output
    :param brc: int
        BRC code. Each BRC code has an associated binary tree for decoding.
        Possible valuea are in the range [0 ... 4].
    :param out: (optional) output array of uint8
        if provided the the decoded data are stored in the 'out' array.
    :param count: bool
        when the flag is set to true the function returns the count of
        consumed bits as additional outpuT (default: False) 
    :returns:
        the Huffman decoded data.

        If the `count` flag is set to True thean also the number of
        consuumed bits is returned:

          decode(...) -> data, count
    """
    cdef int nbits = data.shape[0]
    cdef int idx = 0

    if nbits < 1:
        raise ValueError("The input 'data' array is empty.")

    if not 0 <= brc <= 4:
        raise ValueError(f"Invalid BRC: {brc}")

    if out is None:
        out = np.empty(nsamples, dtype=np.uint8)
    elif out.shape[0] < nsamples:
        raise ValueError(
            f"Output array size ({out.shape[0]}) is too small to contain "
            f"{nsamples} values.")

    with nogil:
        if brc == 0:
            idx = huffman_brc0(nbits, &data[0], nsamples, &out[0])
        elif brc == 1:
            idx = huffman_brc1(nbits, &data[0], nsamples, &out[0])
        elif brc == 2:
            idx = huffman_brc2(nbits, &data[0], nsamples, &out[0])
        elif brc == 3:
            idx = huffman_brc3(nbits, &data[0], nsamples, &out[0])
        elif brc == 4:
            idx = huffman_brc4(nbits, &data[0], nsamples, &out[0])
    if idx < 0:
        raise HuffmanDecodingError(
            f"Not enaough data to decode the requested samples ({nsamples})."
        )
    
    if count:
        return np.asarray(out), idx
    else:
        return np.asarray(out)

