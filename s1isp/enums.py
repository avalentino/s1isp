"""Enum types for Sentinel-1 RAW data decoding.

Enumerations defined in the "Sentinel-1 SAR Space Packet Protocol Data Unit"
document (S1-IF-ASD-PL-0007) issue 13.
"""

import enum


class EEccNumber(enum.IntEnum):
    """ECC Code Interpretation (S1-IF-ASD-PL-0007, table 3.2-4)."""

    NOT_SET = 0  # contingency: reserved for ground testing or mode upgrading
    S1 = 1
    S2 = 2
    S3 = 3
    S4 = 4
    S5_N = 5
    S6 = 6
    IW = 8
    WV = 9
    S5_S = 10
    S1_NO_ICAL = 11
    S2_NO_ICAL = 12
    S3_NO_ICAL = 13
    S4_NO_ICAL = 14
    RFC = 15
    TEST = 16
    EN_S3 = 17
    AN_S1 = 18
    AN_S2 = 19
    AN_S3 = 20
    AN_S4 = 21
    AN_S5_N = 22
    AN_S5_S = 23
    AN_S6 = 24
    S5_N_NO_ICAL = 25
    S5_S_NO_ICAL = 26
    S6_NO_ICAL = 27
    EN_S3_NO_ICAL = 31
    EW = 32
    AN_S1_NO_ICAL = 33
    AN_S3_NO_ICAL = 34
    AN_S6_NO_ICAL = 35
    NC_S1 = 37
    NC_S2 = 38
    NC_S3 = 39
    NC_S4 = 40
    NC_S5_N = 41
    NC_S5_S = 42
    NC_S6 = 43
    NC_EW = 44
    NC_IW = 45
    NC_WM = 46


class ETestMode(enum.IntEnum):
    """Test mode interpretation (S1-IF-ASD-PL-0007, section 3.2.2.4)."""

    DEFAULT = 0
    CONTINGENCY_RXM_FULLY_OPERATIONAL = 4  # 100
    CONTINGENCY_RXM_FULLY_BYPASSED = 5  # 101
    OPER = 6  # 110
    BYPASS = 7  # 111


class ERxChannelId(enum.IntEnum):
    """RX Channel ID (S1-IF-ASD-PL-0007, section 3.2.2.5)."""

    RXV = 0
    RXH = 1


class EBaqMode(enum.IntEnum):
    """BAQ modes (S1-IF-ASD-PL-0007, section 3.2.5.2)."""

    BYPASS = 0
    BAQ3 = 3
    BAQ4 = 4
    BAQ5 = 5
    FDBAQ_MODE_0 = 12
    FDBAQ_MODE_1 = 13
    FDBAQ_MODE_2 = 14


class ERangeDecimation(enum.IntEnum):
    """Range decimation codes (S1-IF-ASD-PL-0007, section 3.2.5.4)."""

    X3_ON_4 = 0
    X2_ON_3 = 1
    X5_ON_9 = 3
    X4_ON_9 = 4
    X3_ON_8 = 5
    X1_ON_3 = 6
    X1_ON_6 = 7
    X3_ON_7 = 8
    X5_ON_16 = 9
    X3_ON_26 = 10
    X4_ON_11 = 11


class EAocsOpMode(enum.IntEnum):
    """AOCS Operational Mode (S1-IF-ASD-PL-0007, section 3.2.3)."""

    NO_MODE = 0
    NPM = 5  # NORMAL POINTING MODE
    OCM = 6  # ORBIT CONTROL MODE


class EPolarization(enum.IntEnum):
    """SAS configurations for polarization.

    See S1-IF-ASD-PL-0007, section 3.2.5.13.1.1.
    """

    H_TX_ONLY = 0
    H_H = 1
    H_V = 2
    H_VH = 3
    V_TX_ONLY = 4
    V_H = 5
    V_V = 6
    V_VH = 7


class ETemperatureCompensation(enum.IntEnum):
    """SAS Temperature Compensation.

    See S1-IF-ASD-PL-0007, section 3.2.5.13.1.2.
    """

    FE_OFF_TA_OFF = 0
    FE_ON_TA_OFF = 1
    FE_OFF_TA_ON = 2
    FE_ON_TA_ON = 3


class ESasTestMode(enum.IntEnum):
    """SAS Test Mode (S1-IF-ASD-PL-0007, section 3.2.5.13.2.3)."""

    SAT_TEST_MODE_ACTIVE = 0
    NOMINAL_CAL_MODE = 1


class ECalType(enum.IntEnum):
    """SAS Calibration Type (S1-IF-ASD-PL-0007, section 3.2.5.13.2.4)."""

    TX_CAL = 0
    RX_CAL = 1
    EPDN_CAL = 2
    TA_CAL = 3
    APDN_CAL = 4
    _NOT_APPLICABLE_5 = 5
    _NOT_APPLICABLE_6 = 6
    TXH_CAL_ISO = 7


class ECalMode(enum.IntEnum):
    """SES Calibration Mode (S1-IF-ASD-PL-0007, section 3.2.5.14.1)."""

    PCC2_ICAL_INTERLEAVED = 0
    PCC2_ICAL_PREAMBLE = 1
    PCC32_PHASE_CODED_CHARACTERIZATION = 2
    RF672_PHASE_CODED_CHARACTERIZATION = 3


class ESignalType(enum.IntEnum):
    """SES Signal Type (S1-IF-ASD-PL-0007, section 3.2.5.14.3)."""

    SILENT = -1  # NOTE: not in the specification but needed for the timeline
    ECHO = 0
    NOISE = 1
    TX_CAL = 8
    RX_CAL = 9
    EPDN_CAL = 10
    TA_CAL = 11  # NOTE: TXH_CAL_ISO for S1C and S1D
    APDN_CAL = 12
    TXH_CAL_ISO = 15


class EBrcCode(enum.IntEnum):
    """BRC codes."""

    BRC0 = 0
    BRC1 = 1
    BRC2 = 2
    BRC3 = 3
    BRC4 = 4
