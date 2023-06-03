"""Look-up tables for Sentinel-1 RAW data decoding.

LUTs are defined in the "Sentinel-1 SAR Space Packet Protocol Data Unit"
document (S1-IF-ASD-PL-0007) issue 13.
"""

import enum
import dataclasses
from typing import List
from fractions import Fraction
from functools import lru_cache

from .constants import REF_FREQ


@dataclasses.dataclass(frozen=True)
class RangeDecimationInfo:
    """Range decipation parameters (S1-IF-ASD-PL-0007, section3.2.5.4)."""

    decimation_filer_band: float  # [Hz]
    decimation_ratio: Fraction
    filter_length: int  # samples
    swaths: List[str]

    @property
    def sampling_frequency(self) -> float:
        """Return the sampling frequency in Hz."""
        return self.decimation_ratio * 4 * REF_FREQ * 1e6


# LUT for Range Decimation (S1-IF-ASD-PL-0007, section 3.2.5.4)
RANGE_DECIMATION_LUT = [
    RangeDecimationInfo(100.0e6, Fraction(3, 4), 28, ["Full bandwidth"]),
    RangeDecimationInfo(87.71e6, Fraction(2, 3), 28, ["S1", "WV1"]),
    None,
    RangeDecimationInfo(74.25e6, Fraction(5, 9), 32, ["S2"]),
    RangeDecimationInfo(59.44e6, Fraction(4, 9), 40, ["S3"]),
    RangeDecimationInfo(50.62e6, Fraction(3, 8), 48, ["S4"]),
    RangeDecimationInfo(44.89e6, Fraction(1, 3), 52, ["S5"]),
    RangeDecimationInfo(22.20e6, Fraction(1, 6), 92, ["EW1"]),
    RangeDecimationInfo(56.59e6, Fraction(3, 7), 36, ["IW1"]),
    RangeDecimationInfo(42.86e6, Fraction(5, 16), 68, ["S6", "IW3"]),
    RangeDecimationInfo(
        15.10e6, Fraction(3, 26), 120, ["EW2", "EW3", "EW4", "EW5"]
    ),
    RangeDecimationInfo(48.35e6, Fraction(4, 11), 44, ["IW2", "WV2"]),
]


def lookup_range_decimation_info(code: int) -> RangeDecimationInfo:
    """Return the range decimation information corresponding to the input code.

    The LUT is defined in S1-IF-ASD-PL-0007, section 3.2.5.4.

    :param code: int
        range decimation code
    :returns: RangeDecimationInfo
        range decimation info
    """
    return RANGE_DECIMATION_LUT[code]


# 2D LUT for the computation of the D parameter
# (S1-IF-ASD-PL-0007, table 5.1-1)
# fmt: off
D_LUT2D = [
    [1, 1, 2, 3],
    [1, 1, 2],
    [],
    [1, 1, 2, 2, 3, 3, 4, 4, 5],
    [0, 1, 1, 2, 2, 3, 3, 4, 4],
    [0, 1, 1, 1, 2, 2, 3, 3],
    [0, 0, 1],
    [0, 0, 0, 0, 0, 1],
    [0, 1, 1, 2, 2, 3, 3],
    [0, 0, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 4, 4, 4, 5],
    [0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 3, 3],  # noqa: E501
    [0, 1, 1, 1, 2, 2, 3, 3, 3, 4, 4],
]
# fmt: on


def lookup_d_value(rdcode: int, cvalue: int) -> int:
    """Return the value of D as a function of C and the range decimation code.

    Look up table supporting the computation of the number of samples after
    decimation as defined in S1-IF-ASD-PL-0007, table 5.1-1.

    :param rdcode: int
        range decimation code from 0 to 11
    :param cvalue: int
        value of the C parameter
    :returns: int
        the value of the D parameter
    """
    return D_LUT2D[rdcode][cvalue]


# LUT for Range Decimation filter output offset values
# (S1-IF-ASD-PL-0007, table 5.1-2)
FILTER_OUTPUT_OFFSET_LUT = [
    87,
    87,
    None,
    88,
    90,
    92,
    93,
    103,
    89,
    97,
    110,
    91,
    None,
    None,
    None,
    None,
]


def lookup_filter_output_offset(code: int) -> int:
    """Return the value of the decimatiion filter output offset.

    Values are defined in S1-IF-ASD-PL-0007, table 5.1-2.

    :param code: int
        filter output offset code
    :returns: int
        filter output offset value in samples
    """
    offset = FILTER_OUTPUT_OFFSET_LUT[code]
    if offset is None:
        raise IndexError(f"Invalid filter output ofset code: {code}.")
    return offset


# TGU temerature calibration values in Celsius degrees
# (S1-IF-ASD-PL-0007, section 5.4.1)
TGU_TEMPERATURE_LUT = [
    +116.14,
    +115.02,
    +113.90,
    +112.78,
    +111.66,
    +110.54,
    +109.42,
    +108.30,
    +107.18,
    +106.06,
    +104.94,
    +103.82,
    +102.70,
    +101.58,
    +100.46,
    +99.34,
    +98.22,
    +97.10,
    +95.98,
    +94.86,
    +93.74,
    +92.62,
    +91.50,
    +90.38,
    +89.26,
    +88.14,
    +87.02,
    +85.90,
    +84.78,
    +83.66,
    +82.54,
    +81.42,
    +80.30,
    +79.18,
    +78.06,
    +76.94,
    +75.82,
    +74.70,
    +73.58,
    +72.46,
    +71.34,
    +70.22,
    +69.10,
    +67.98,
    +66.86,
    +65.74,
    +64.62,
    +63.50,
    +62.38,
    +61.26,
    +60.14,
    +59.02,
    +57.90,
    +56.78,
    +55.66,
    +54.54,
    +53.42,
    +52.30,
    +51.18,
    +50.06,
    +48.94,
    +47.82,
    +46.70,
    +45.58,
    +44.46,
    +43.34,
    +42.22,
    +41.10,
    +39.98,
    +38.86,
    +37.74,
    +36.62,
    +35.50,
    +34.38,
    +33.26,
    +32.14,
    +31.02,
    +29.90,
    +28.78,
    +27.66,
    +26.54,
    +25.42,
    +24.30,
    +23.18,
    +22.06,
    +20.94,
    +19.82,
    +18.70,
    +17.58,
    +16.46,
    +15.34,
    +14.22,
    +13.10,
    +11.98,
    +10.86,
    +9.74,
    +8.62,
    +7.50,
    +6.38,
    +5.26,
    +4.14,
    +3.02,
    +1.90,
    +0.78,
    -0.34,
    -1.46,
    -2.58,
    -3.70,
    -4.82,
    -5.94,
    -7.06,
    -8.18,
    -9.30,
    -10.42,
    -11.54,
    -12.66,
    -13.78,
    -14.90,
    -16.02,
    -17.14,
    -18.26,
    -19.38,
    -20.50,
    -21.62,
    -22.74,
    -23.86,
    -24.98,
    -26.10,
]


def lookup_tgu_temperature(code: int) -> float:
    """Return the TGU temperature value corresponding to the input code.

    The temperature is returned in Celsius degrees.
    The function uses the calibration LUT defined in S1-IF-ASD-PL-0007,
    section 5.4.1.
    """
    return TGU_TEMPERATURE_LUT[code]


# EFE temperature calibration valies in Celsius degrees
# (S1-IF-ASD-PL-0007, section 5.4.2)
EFE_TEMPERATURE_LUT = [
    None,
    None,
    None,
    None,
    -51.38,
    -47.38,
    -44.38,
    -41.50,
    -38.75,
    -36.75,
    -34.88,
    -32.88,
    -31.00,
    -29.63,
    -28.00,
    -27.00,
    -25.50,
    -24.13,
    -23.13,
    -22.00,
    -21.00,
    -20.00,
    -19.00,
    -18.13,
    -17.00,
    -16.00,
    -15.00,
    -14.38,
    -13.88,
    -13.00,
    -12.00,
    -11.38,
    -10.88,
    -10.00,
    -9.00,
    -8.50,
    -8.00,
    -7.00,
    -6.50,
    -6.00,
    -5.38,
    -4.88,
    -4.00,
    -3.50,
    -3.00,
    -2.50,
    -2.00,
    -1.38,
    -1.00,
    -0.13,
    +0.25,
    +1.00,
    +1.50,
    +2.00,
    +2.50,
    +3.00,
    +3.50,
    +3.88,
    +4.25,
    +4.88,
    +5.13,
    +5.88,
    +6.13,
    +6.63,
    +7.00,
    +7.50,
    +8.00,
    +8.50,
    +9.00,
    +9.50,
    +9.88,
    +10.13,
    +10.50,
    +11.00,
    +11.50,
    +11.88,
    +12.13,
    +12.63,
    +13.00,
    +13.50,
    +14.00,
    +14.50,
    +14.88,
    +15.13,
    +15.50,
    +16.00,
    +16.50,
    +16.88,
    +17.13,
    +17.50,
    +17.88,
    +18.13,
    +18.50,
    +19.00,
    +19.50,
    +19.88,
    +20.13,
    +20.50,
    +21.00,
    +21.50,
    +21.88,
    +22.13,
    +22.50,
    +22.88,
    +23.13,
    +23.50,
    +24.00,
    +24.50,
    +24.50,
    +25.00,
    +25.50,
    +25.88,
    +26.13,
    +26.50,
    +26.88,
    +27.13,
    +27.50,
    +28.00,
    +28.50,
    +28.75,
    +29.13,
    +29.50,
    +29.88,
    +30.13,
    +30.50,
    +30.88,
    +31.13,
    +31.50,
    +32.00,
    +32.50,
    +32.75,
    +33.13,
    +33.50,
    +33.88,
    +34.13,
    +34.50,
    +34.88,
    +35.13,
    +35.50,
    +36.00,
    +36.50,
    +36.88,
    +37.13,
    +37.50,
    +37.88,
    +38.13,
    +38.50,
    +39.00,
    +39.50,
    +39.75,
    +40.13,
    +40.50,
    +40.88,
    +41.13,
    +41.75,
    +42.13,
    +42.50,
    +42.88,
    +43.13,
    +43.50,
    +43.88,
    +44.25,
    +44.75,
    +45.13,
    +45.50,
    +45.88,
    +46.25,
    +46.75,
    +47.13,
    +47.50,
    +47.88,
    +48.25,
    +48.75,
    +49.13,
    +49.50,
    +49.88,
    +50.25,
    +50.88,
    +51.13,
    +51.75,
    +52.13,
    +52.50,
    +52.88,
    +53.25,
    +53.88,
    +54.25,
    +54.88,
    +55.13,
    +55.75,
    +56.13,
    +56.75,
    +57.13,
    +57.50,
    +57.88,
    +58.25,
    +58.88,
    +59.25,
    +59.88,
    +60.25,
    +60.88,
    +61.25,
    +61.88,
    +62.25,
    +62.88,
    +63.25,
    +63.88,
    +64.25,
    +64.88,
    +65.25,
    +65.88,
    +66.50,
    +67.13,
    +67.75,
    +68.13,
    +68.88,
    +69.25,
    +69.88,
    +70.50,
    +71.13,
    +71.88,
    +72.25,
    +73.00,
    +73.75,
    +74.25,
    +74.88,
    +75.50,
    +76.25,
    +76.88,
    +77.50,
    +78.50,
    +79.13,
    +79.88,
    +80.50,
    +81.25,
    +82.00,
    +82.88,
    +83.63,
    +84.50,
    +85.50,
    +86.88,
    +87.00,
    +87.88,
    +88.63,
    +89.63,
    +90.63,
    +91.63,
    +92.63,
    +93.63,
    +95.00,
    +96.00,
    +97.00,
    +98.50,
    +99.88,
    +100.88,
    +102.00,
    +103.50,
]


def lookup_efe_temperature(code: int) -> float:
    """Return the EFE temperature value corresponding to the input code.

    The Electronic Front End (EFE) temperature is returned in Celsius degrees.
    The function uses the calibration LUT defined in S1-IF-ASD-PL-0007,
    section 5.4.2.
    """
    temperature = EFE_TEMPERATURE_LUT[code]
    if temperature is None:
        raise IndexError(f"Invalid EFE temperature code: {code}.")
    return temperature


class EBaqMode(enum.IntEnum):
    """BAQ modes (S1-IF-ASD-PL-0007, section 3.2.5.2)."""

    BYPASS = 0
    BAQ3 = 3
    BAQ4 = 4
    BAQ5 = 5
    FDBAQ_MODE_0 = 12
    FDBAQ_MODE_1 = 13
    FDBAQ_MODE_2 = 14


class EBrcCode(enum.IntEnum):
    """BRC codes."""

    BRC0 = 0
    BRC1 = 1
    BRC2 = 2
    BRC3 = 3
    BRC4 = 4


# S1-IF-ASD-PL-0007 section 5.2.1 Table 5.2-1
# Simple Reconstruction Parameter Values A, B
SRM_LUT_A = {
    EBaqMode.BAQ3: [3.0000, 3.0000, 3.1200, 3.5500],
    EBaqMode.BAQ4: [7.0000, 7.0000, 7.0000, 7.1700, 7.4000, 7.7600],
    EBaqMode.BAQ5: [
        15.0000,
        15.0000,
        15.0000,
        15.0000,
        15.0000,
        15.0000,
        15.4400,
        15.5600,
        16.1100,
        16.3800,
        16.6500,
    ],
}


# S1-IF-ASD-PL-0007 section 5.2.1 Table 5.2-1
# Simple Reconstruction Parameter Values A, B
SRM_LUT_B = {
    EBrcCode.BRC0: [3.0000, 3.0000, 3.1600, 3.5300],
    EBrcCode.BRC1: [4.0000, 4.0000, 4.0800, 4.3700],
    EBrcCode.BRC2: [6.0000, 6.0000, 6.0000, 6.1500, 6.5000, 6.8800],
    EBrcCode.BRC3: [9.0000, 9.0000, 9.0000, 9.0000, 9.3600, 9.5000, 10.1000],
    EBrcCode.BRC4: [
        15.0000,
        15.0000,
        15.0000,
        15.0000,
        15.0000,
        15.0000,
        15.2200,
        15.5000,
        16.0500,
    ],
}


# S1-IF-ASD-PL-0007 section 5.2.2.1 Table 5.2-2
# Normalised Reconstruction Levels
BAQ_NRL_LUT = {
    EBaqMode.BAQ3: [0.2490, 0.7681, 1.3655, 2.1864],
    EBaqMode.BAQ4: [
        0.1290,
        0.3900,
        0.6601,
        0.9471,
        1.2623,
        1.6261,
        2.0793,
        2.7467,
    ],
    EBaqMode.BAQ5: [
        0.0660,
        0.1985,
        0.3320,
        0.4677,
        0.6061,
        0.7487,
        0.8964,
        1.0510,
        1.2143,
        1.3896,
        1.5800,
        1.7914,
        2.0329,
        2.3234,
        2.6971,
        3.2692,
    ],
}


# S1-IF-ASD-PL-0007 section 5.2.2.1 Table 5.2-2
# Normalised Reconstruction Levels
FDBAQ_NRL_LUT = {
    EBrcCode.BRC0: [0.3637, 1.0915, 1.8208, 2.6406],
    EBrcCode.BRC1: [0.3042, 0.9127, 1.5216, 2.1313, 2.8426],
    EBrcCode.BRC2: [0.2305, 0.6916, 1.1528, 1.6140, 2.0754, 2.5369, 3.1191],
    EBrcCode.BRC3: [
        0.1702,
        0.5107,
        0.8511,
        1.1916,
        1.5321,
        1.8726,
        2.2131,
        2.5536,
        2.8942,
        3.3744,
    ],
    EBrcCode.BRC4: [
        0.1130,
        0.3389,
        0.5649,
        0.7908,
        1.0167,
        1.2428,
        1.4687,
        1.6947,
        1.9206,
        2.1466,
        2.3725,
        2.5985,
        2.8244,
        3.0504,
        3.2764,
        3.6623,
    ],
}


# S1-IF-ASD-PL-0007 section 5.2.2.2 Table 5.2-3
# Sigma Factors
SIGMA_FACTORS_LUT = [
    0.00,
    0.63,
    1.25,
    1.88,
    2.51,
    3.13,
    3.76,
    4.39,
    5.01,
    5.64,
    6.27,
    6.89,
    7.52,
    8.15,
    8.77,
    9.40,
    10.03,
    10.65,
    11.28,
    11.91,
    12.53,
    13.16,
    13.79,
    14.41,
    15.04,
    15.67,
    16.29,
    16.92,
    17.55,
    18.17,
    18.80,
    19.43,
    20.05,
    20.68,
    21.31,
    21.93,
    22.56,
    23.19,
    23.81,
    24.44,
    25.07,
    25.69,
    26.32,
    26.95,
    27.57,
    28.20,
    28.83,
    29.45,
    30.08,
    30.71,
    31.33,
    31.96,
    32.59,
    33.21,
    33.84,
    34.47,
    35.09,
    35.72,
    36.35,
    36.97,
    37.60,
    38.23,
    38.85,
    39.48,
    40.11,
    40.73,
    41.36,
    41.99,
    42.61,
    43.24,
    43.87,
    44.49,
    45.12,
    45.75,
    46.37,
    47.00,
    47.63,
    48.25,
    48.88,
    49.51,
    50.13,
    50.76,
    51.39,
    52.01,
    52.64,
    53.27,
    53.89,
    54.52,
    55.15,
    55.77,
    56.40,
    57.03,
    57.65,
    58.28,
    58.91,
    59.53,
    60.16,
    60.79,
    61.41,
    62.04,
    62.98,
    64.24,
    65.49,
    66.74,
    68.00,
    69.25,
    70.50,
    71.76,
    73.01,
    74.26,
    75.52,
    76.77,
    78.02,
    79.28,
    80.53,
    81.78,
    83.04,
    84.29,
    85.54,
    86.80,
    88.05,
    89.30,
    90.56,
    91.81,
    93.06,
    94.32,
    95.57,
    96.82,
    98.08,
    99.33,
    100.58,
    101.84,
    103.09,
    104.34,
    105.60,
    106.85,
    108.10,
    109.35,
    110.61,
    111.86,
    113.11,
    114.37,
    115.62,
    116.87,
    118.13,
    119.38,
    120.63,
    121.89,
    123.14,
    124.39,
    125.65,
    126.90,
    128.15,
    129.41,
    130.66,
    131.91,
    133.17,
    134.42,
    135.67,
    136.93,
    138.18,
    139.43,
    140.69,
    141.94,
    143.19,
    144.45,
    145.70,
    146.95,
    148.21,
    149.46,
    150.71,
    151.97,
    153.22,
    154.47,
    155.73,
    156.98,
    158.23,
    159.49,
    160.74,
    161.99,
    163.25,
    164.50,
    165.75,
    167.01,
    168.26,
    169.51,
    170.77,
    172.02,
    173.27,
    174.53,
    175.78,
    177.03,
    178.29,
    179.54,
    180.79,
    182.05,
    183.30,
    184.55,
    185.81,
    187.06,
    188.31,
    189.57,
    190.82,
    192.07,
    193.33,
    194.58,
    195.83,
    197.09,
    198.34,
    199.59,
    200.85,
    202.10,
    203.35,
    204.61,
    205.86,
    207.11,
    208.37,
    209.62,
    210.87,
    212.13,
    213.38,
    214.63,
    215.89,
    217.14,
    218.39,
    219.65,
    220.90,
    222.15,
    223.41,
    224.66,
    225.91,
    227.17,
    228.42,
    229.67,
    230.93,
    232.18,
    233.43,
    234.69,
    235.94,
    237.19,
    238.45,
    239.70,
    240.95,
    242.21,
    243.46,
    244.71,
    245.97,
    247.22,
    248.47,
    249.73,
    250.98,
    252.23,
    253.49,
    254.74,
    255.99,
    255.99,
]


@lru_cache()  # COMPATIBILITY: parentheses are not needed in Python >= 3.8
def get_baq_lut(baqmode: EBaqMode, thidx: int, dtype="float32"):
    """Return the BAQ reconstruction look-up table (LUT)."""
    import numpy as np

    baqmode = EBaqMode(baqmode)
    if baqmode not in {EBaqMode.BAQ3, EBaqMode.BAQ4, EBaqMode.BAQ5}:
        raise ValueError(f"Unexpected BAQ mode: {baqmode}")
    if not (0 <= thidx < 256):
        raise ValueError(f"Unexpected thidx value: {thidx}")

    nbits = baqmode.value
    lut = np.empty(2**nbits, dtype=np.float64)
    n = 2 ** (nbits - 1)

    if thidx < n:
        lut[: n - 1] = np.arange(n - 1, dtype=np.float64)
        lut[n - 1] = SRM_LUT_A[baqmode][thidx]
    else:
        lut[:n] = np.asarray(BAQ_NRL_LUT[baqmode]) * SIGMA_FACTORS_LUT[thidx]
    lut[n:] = -lut[:n]

    return lut.astype(dtype)


BRC_SIZE = {
    EBrcCode.BRC0: 4,
    EBrcCode.BRC1: 5,
    EBrcCode.BRC2: 7,
    EBrcCode.BRC3: 10,
    EBrcCode.BRC4: 16,
}


@lru_cache()  # COMPATIBILITY: parentheses are not needed in Python >= 3.8
def get_fdbaq_lut(brc: EBrcCode, thidx: int, dtype="float32"):
    """Return the FDBAQ reconstruction look-up table (LUT)."""
    import numpy as np

    brc = EBrcCode(brc)
    if not (0 <= thidx < 256):
        raise ValueError(f"Unexpected thidx value: {thidx}")

    n = BRC_SIZE[brc]
    lutsize = 2 * n
    lut = np.empty(lutsize, dtype=np.float64)

    m = len(SRM_LUT_B[brc]) - 1
    if thidx <= m:
        lut[: n - 1] = np.arange(n - 1, dtype=np.float64)
        lut[n - 1] = SRM_LUT_B[brc][thidx]
    else:
        lut[:n] = np.asarray(FDBAQ_NRL_LUT[brc]) * SIGMA_FACTORS_LUT[thidx]
    lut[n:] = -lut[:n]

    return lut.astype(dtype)
