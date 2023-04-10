"""Tests for LUTs."""

from s1isp.constants_and_luts import BRC_SIZE, get_fdbaq_lut


def test_fdbaq_econstruction_lut(fdbaq_reconstruction_lut):
    TOLL = 1e-16
    for brc, brc_lut in fdbaq_reconstruction_lut.items():
        brc = int(brc)
        for thidx, thidx_lut in brc_lut.items():
            thidx = int(thidx)
            lut = get_fdbaq_lut(brc, thidx, dtype="float64")
            for ucode in range(2 * BRC_SIZE[brc]):
                sign = 1 if ucode >= BRC_SIZE[brc] else 0
                mcode = ucode - BRC_SIZE[brc] if sign else ucode
                ref = thidx_lut[str(sign)][str(mcode)]

                val = lut[ucode]

                assert abs(ref - val) < TOLL
