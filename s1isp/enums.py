"""Enum types for Sentinel-1 RAW data decoding.

Enumerations defined in the "Sentinel-1 SAR Space Packet Protocol Data Unit"
document (S1-IF-ASD-PL-0007) issue 13.
"""

import enum


class EEccNumber(enum.IntEnum):
    """ECC Code Interpretation (S1-IF-ASD-PL-0007, table 3.2-4)."""

    # TODO: check "not_set"
    not_set = 0  # contingency: reserved for ground testing or mode upgrading
    s1 = 1
    s2 = 2
    s3 = 3
    s4 = 4
    s5_n = 5
    s6 = 6
    iw = 8
    wm = 9
    s5_s = 10
    s1_no_ical = 11
    s2_no_ical = 12
    s3_no_ical = 13
    s4_no_ical = 14
    rfc = 15
    test = 16
    en_s3 = 17
    an_s1 = 18
    an_s2 = 19
    an_s3 = 20
    an_s4 = 21
    an_s5_n = 22
    an_s5_s = 23
    an_s6 = 24
    s5_n_no_ical = 25
    s5_s_no_ical = 26
    s6_no_ical = 27
    en_s3_no_ical = 31
    en = 32
    an_s1_no_ical = 33
    an_s3_no_ical = 34
    an_s6_no_ical = 35
    nc_s1 = 37
    nc_s2 = 38
    nc_s3 = 39
    nc_s4 = 40
    nc_s5_n = 41
    nc_s5_s = 42
    nc_s6 = 43
    nc_ew = 44
    nc_iw = 45
    nc_wm = 46


class ETestMode(enum.IntEnum):
    """Test mode interpretation (S1-IF-ASD-PL-0007, section 3.2.2.4)."""

    default = 0
    contingency_rxm_fully_operational = 4  # 100
    contingency_rxm_fully_bypassed = 5  # 101
    oper = 6  # 110
    bypass = 7  # 111


class ERxChannelId(enum.IntEnum):
    """RX Channel ID (S1-IF-ASD-PL-0007, section 3.2.2.5)."""

    rxv = 0
    rxh = 1


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

    x3_on_4 = 0
    x2_on_3 = 1
    x5_on_9 = 3
    x4_on_9 = 4
    x3_on_8 = 5
    x1_on_3 = 6
    x1_on_6 = 7
    x3_on_7 = 8
    x5_on_16 = 9
    x3_on_26 = 10
    x4_on_11 = 11


class EAocsOpMode(enum.IntEnum):
    """AOCS Operational Mode (S1-IF-ASD-PL-0007, section 3.2.3)."""

    no_mode = 0
    npm = 5  # normal pointing mode
    ocm = 6  # orbit control mode


class EPolarization(enum.IntEnum):
    """SAS configurations for polarization.

    See S1-IF-ASD-PL-0007, section 3.2.5.13.1.1.
    """

    h_tx_only = 0
    h_h = 1
    h_v = 2
    h_vh = 3
    v_tx_only = 4
    v_h = 5
    v_v = 6
    v_vh = 7


class ETemperatureCompensation(enum.IntEnum):
    """SAS Temperature Compensation.

    See S1-IF-ASD-PL-0007, section 3.2.5.13.1.2.
    """

    fe_off_ta_off = 0
    fe_on_ta_off = 1
    fe_off_ta_on = 2
    fe_on_ta_on = 3


class ESasTestMode(enum.IntEnum):
    """SAS Test Mode (S1-IF-ASD-PL-0007, section 3.2.5.13.2.3)."""

    sat_test_mode_active = 0
    nominal_cal_mode = 1


class ECalType(enum.IntEnum):
    """SAS Calibration Type (S1-IF-ASD-PL-0007, section 3.2.5.13.2.4)."""

    tx_cal = 0
    rx_cal = 1
    epdn_cal = 2
    ta_cal = 3
    apdn_cal = 4
    tx_h_cal_iso = 7


class ECalMode(enum.IntEnum):
    """SES Calibration Mode (S1-IF-ASD-PL-0007, section 3.2.5.14.1)."""

    pcc2_ical_interleaved = 0
    pcc2_ical_preamble = 1
    pcc32_phase_coded_characterization = 2
    rf672_phase_coded_characterization = 3


class ESignalType(enum.IntEnum):
    """SES Signal Type (S1-IF-ASD-PL-0007, section 3.2.5.14.3)."""

    echo = 0
    noise = 1
    tx_cal = 8
    rx_cal = 9
    epdn_cal = 10
    ta_cal = 11
    apdn_cal = 12
    tx_h_cal_iso = 15


class EBrcCode(enum.IntEnum):
    """BRC codes."""

    BRC0 = 0
    BRC1 = 1
    BRC2 = 2
    BRC3 = 3
    BRC4 = 4
