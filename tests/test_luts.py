"""Tests for LUTs."""

import pytest

import s1isp.luts
from s1isp.luts import BRC_SIZE, get_fdbaq_lut


def test_range_decimation_info_sampling_frequency():
    decimation_info = s1isp.luts.RANGE_DECIMATION_LUT[0]
    assert decimation_info.swaths == ["Full bandwidth"]
    fs = decimation_info.sampling_frequency
    assert fs > decimation_info.decimation_filer_band
    assert fs > 100.0e6


def test_lookup_range_decimation_info():
    decimation_info = s1isp.luts.lookup_range_decimation_info(0)
    assert isinstance(decimation_info, s1isp.luts.RangeDecimationInfo)
    assert decimation_info == s1isp.luts.RANGE_DECIMATION_LUT[0]

    assert s1isp.luts.lookup_range_decimation_info(2) is None


def test_lookup_d_value():
    d = s1isp.luts.lookup_d_value(0, 0)
    assert isinstance(d, int)

    with pytest.raises(IndexError):
        s1isp.luts.lookup_d_value(2, 2)


def test_lookup_filter_output_offset():
    assert isinstance(s1isp.luts.lookup_filter_output_offset(0), int)

    with pytest.raises(IndexError, match="Invalid filter output"):
        s1isp.luts.lookup_filter_output_offset(2)


def test_lookup_tgu_temperature():
    assert isinstance(s1isp.luts.lookup_tgu_temperature(0), float)


def test_lookup_efe_temperature():
    assert isinstance(s1isp.luts.lookup_efe_temperature(10), float)

    with pytest.raises(IndexError, match="Invalid EFE temperature"):
        s1isp.luts.lookup_efe_temperature(2)


def test_lookup_ta_temperature():
    assert isinstance(s1isp.luts.lookup_ta_temperature(10), float)

    with pytest.raises(IndexError, match="Invalid TA temperature"):
        s1isp.luts.lookup_ta_temperature(2)


def test_fdbaq_reconstruction_lut(fdbaq_reconstruction_lut):
    toll = 1e-16
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

                assert abs(ref - val) < toll
