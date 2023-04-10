"""Sentinel-1 Instrument Source Packets (ISP) descriptors.

The definotion of all the ISP records is provided in the "Sentinel-1 SAR
Space Packet Protocol Data Unit" document (S1-IF-ASD-PL-0007) issue 13.
"""

import enum
import math
from typing import ClassVar

import bpack
import bpack.bs
from bpack import T

from .constants_and_luts import (
    REF_FREQ,
    SYNK_MARKER,
    lookup_d_value,
    lookup_filter_output_offset,
    lookup_range_decimation_info,
    RangeDecimationInfo,
    EBaqMode,
)

BITS = bpack.EBaseUnits.BITS
BE = bpack.EByteOrder.BE


class SyncMarkerException(RuntimeError):
    """Sync marker error."""

    pass


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
    """Test mode interpretatiion (S1-IF-ASD-PL-0007, section 3.2.2.4)."""

    default = 0
    contingency_rxm_fully_operational = 4  # 100
    contingency_rxm_fully_bypassed = 5  # 101
    oper = 6  # 110
    bypass = 7  # 111


class ERxChannelId(enum.IntEnum):
    """RX Channel ID (S1-IF-ASD-PL-0007, section 3.2.2.5)."""

    rxv = 0
    rxh = 1


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


class ESasPolarization(enum.IntEnum):
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


class ESasCalType(enum.IntEnum):
    """SAS Calibration Type (S1-IF-ASD-PL-0007, section 3.2.5.13.2.4)."""

    tx_cal = 0
    rx_cal = 1
    epdn_cal = 2
    ta_cal = 3
    apdn_cal = 4
    tx_h_cal_iso = 7


class ESesCalMode(enum.IntEnum):
    """SES Calibration Mode (S1-IF-ASD-PL-0007, section 3.2.5.14.1)."""

    pcc2_ical_interleaved = 0
    pcc2_ical_preamble = 1
    pcc32_phase_coded_characterization = 2
    rf672_phase_coded_characterization = 3


class ESesSignalType(enum.IntEnum):
    """SES Signal Type (S1-IF-ASD-PL-0007, section 3.2.5.14.3)."""

    echo = 0
    noise = 1
    tx_cal = 8
    rx_cal = 9
    epdn_cal = 10
    ta_cal = 11
    apdn_cal = 12
    tx_h_cal_iso = 15


@bpack.bs.decoder
@bpack.descriptor(baseunits=BITS, byteorder=BE)
class PacketPrimaryHeader:
    """Prinary packet header (S1-IF-ASD-PL-0007, section 3.1)."""

    version: T["u3"] = 0
    packet_type: T["u1"] = 0
    secondary_header_flag: bool = True
    pid: T["u7"] = 0
    pcat: T["u4"] = 0
    sequence_flags: T["u2"] = 0
    sequence_counter: T["u14"] = 0
    packet_data_length: T["u16"] = 0


@bpack.bs.decoder
@bpack.descriptor(baseunits=BITS, byteorder=BE)
class DatationService:
    """Datation Service (S1-IF-ASD-PL-0007, section 3.2.1)."""

    coarse_time: T["u32"] = 0
    fine_time: T["u16"] = 0

    @property
    def fine_time_sec(self) -> float:
        """Fine time [s] (S1-IF-ASD-PL-0007, section 3.2.1.2).

        The Fine Time represents the subsecond time stamp of the Space Packet.
        """
        return (self.fine_time + 0.5) * 2**-16


@bpack.bs.decoder
@bpack.descriptor(baseunits=BITS, byteorder=BE)
class FixedAncillaryDataService:
    """Fixed Ancillary Data Field (S1-IF-ASD-PL-0007, section 3.2.2)."""

    sync_marker: T["u32"] = SYNK_MARKER
    data_take_id: T["u32"] = 0
    ecc_num: EEccNumber = bpack.field(size=8, default=EEccNumber.not_set)
    # n. 1 bit n/a
    test_mode: ETestMode = bpack.field(
        size=3, offset=73, default=ETestMode.default
    )
    rx_channel_id: ERxChannelId = bpack.field(size=4, default=ERxChannelId.rxv)
    instrument_configuration_id: T["u32"] = 0  # NOTE: the data type is TBD


@bpack.bs.decoder
@bpack.descriptor(baseunits=BITS, byteorder=BE)
class SubCommutatedAncillaryDataService:
    """Sub-commutated Ancillary Data Service.

    See S1-IF-ASD-PL-0007, section 3.2.3 and table 3.2.-12
    """

    word_index: T["u8"] = 0
    word_data: T["S16"] = 0


@bpack.bs.decoder
@bpack.descriptor(baseunits=BITS, byteorder=BE)
class PVTAncillatyData:
    """Position Velocity Time (PVT) Ancillary Data.

    See S1-IF-ASD-PL-0007, table 3.2-5.
    """

    x: T["f64"] = 0
    y: T["f64"] = 0
    z: T["f64"] = 0
    vx: T["f32"] = 0
    vy: T["f32"] = 0
    vz: T["f32"] = 0
    # time_stamp provided in yocto seconds (1e-24 s)
    time_stamp: T["u56"] = bpack.field(default=0, offset=296)


@bpack.bs.decoder
@bpack.descriptor(baseunits=BITS, byteorder=BE)
class PointingStatus:
    """Pointing Status (S1-IF-ASD-PL-0007, table 3.2-8)."""

    aocs_op_mode: T["u8"] = EAocsOpMode.no_mode
    roll_error: bool = bpack.field(default=False, offset=13)
    pitch_error: bool = False
    yaw_error: bool = False


@bpack.bs.decoder
@bpack.descriptor(baseunits=BITS, byteorder=BE)
class AttitudeAncillatyData:
    """Attitude Ancillary Data (S1-IF-ASD-PL-0007, table 3.2-6)."""

    q0: T["f32"] = 0
    q1: T["f32"] = 0
    q2: T["f32"] = 0
    q3: T["f32"] = 0
    omega_x: T["f32"] = 0
    omega_y: T["f32"] = 0
    omega_z: T["f32"] = 0
    # time_stamp provided in yocto seconds (1e-24 s)
    time_stamp: T["u56"] = bpack.field(default=0, offset=232)
    pointing_status: PointingStatus = bpack.field(
        default_factory=PointingStatus
    )


@bpack.bs.decoder
@bpack.descriptor(baseunits=BITS, byteorder=BE)
class HKTemperatureAncillatyData:
    """Antenna and TGU temperature HouseKeeping Data.

    See S1-IF-ASD-PL-0007, table 3.2-9.
    """

    temperature_update_status: T["u16"] = 0

    Tile1_EFEH_temperature: T["u8"] = 0
    Tile1_EFEV_temperature: T["u8"] = 0
    Tile1_TA_temperature: T["u8"] = 0

    Tile2_EFEH_temperature: T["u8"] = 0
    Tile2_EFEV_temperature: T["u8"] = 0
    Tile2_TA_temperature: T["u8"] = 0

    Tile3_EFEH_temperature: T["u8"] = 0
    Tile3_EFEV_temperature: T["u8"] = 0
    Tile3_TA_temperature: T["u8"] = 0

    Tile4_EFEH_temperature: T["u8"] = 0
    Tile4_EFEV_temperature: T["u8"] = 0
    Tile4_TA_temperature: T["u8"] = 0

    Tile5_EFEH_temperature: T["u8"] = 0
    Tile5_EFEV_temperature: T["u8"] = 0
    Tile5_TA_temperature: T["u8"] = 0

    Tile6_EFEH_temperature: T["u8"] = 0
    Tile6_EFEV_temperature: T["u8"] = 0
    Tile6_TA_temperature: T["u8"] = 0

    Tile7_EFEH_temperature: T["u8"] = 0
    Tile7_EFEV_temperature: T["u8"] = 0
    Tile7_TA_temperature: T["u8"] = 0

    Tile8_EFEH_temperature: T["u8"] = 0
    Tile8_EFEV_temperature: T["u8"] = 0
    Tile8_TA_temperature: T["u8"] = 0

    Tile9_EFEH_temperature: T["u8"] = 0
    Tile9_EFEV_temperature: T["u8"] = 0
    Tile9_TA_temperature: T["u8"] = 0

    Tile10_EFEH_temperature: T["u8"] = 0
    Tile10_EFEV_temperature: T["u8"] = 0
    Tile10_TA_temperature: T["u8"] = 0

    Tile11_EFEH_temperature: T["u8"] = 0
    Tile11_EFEV_temperature: T["u8"] = 0
    Tile11_TA_temperature: T["u8"] = 0

    Tile12_EFEH_temperature: T["u8"] = 0
    Tile12_EFEV_temperature: T["u8"] = 0
    Tile12_TA_temperature: T["u8"] = 0

    Tile13_EFEH_temperature: T["u8"] = 0
    Tile13_EFEV_temperature: T["u8"] = 0
    Tile13_TA_temperature: T["u8"] = 0

    Tile14_EFEH_temperature: T["u8"] = 0
    Tile14_EFEV_temperature: T["u8"] = 0
    Tile14_TA_temperature: T["u8"] = 0

    TGU_temperature: T["u7"] = bpack.field(default=0, offset=361)


@bpack.bs.decoder
@bpack.descriptor(baseunits=BITS, byteorder=BE)
class CountersService:
    """Counters Service (S1-IF-ASD-PL-0007, section 3.2.4)."""

    space_packet_count: T["u32"] = 0
    pri_count: T["u32"] = 0


@bpack.bs.decoder
@bpack.descriptor(baseunits=BITS, byteorder=BE)
class SasSsbData:
    """SAS SBB Data (S1-IF-ASD-PL-0007, section 3.2.5.15).

    The SAS SSB Data field indicates the actual configuration of the
    SAR Antenna Subsystem (SAS).
    """

    ssb_flag: bool = False
    polarization: ESasPolarization = bpack.field(
        size=3, default=ESasPolarization.h_tx_only
    )
    temperature_compensation: ETemperatureCompensation = bpack.field(
        size=2, default=ETemperatureCompensation.fe_off_ta_off
    )
    _dynamic_data: T["u4"] = bpack.field(default=0, offset=8)
    _beam_address: T["u10"] = bpack.field(default=0, offset=14)

    def get_elevation_beam_address(self) -> int:
        """Return the elevation beam address code.

        Please note that if ssb_flag=True an TypeError is raised.
        """
        if self.ssb_flag:
            raise TypeError(
                "SAS SSB Data with ssb_flag=True have no "
                "elevation_beam_address field"
            )
        else:
            return self._dynamic_data

    def get_azimuth_beam_address(self) -> int:
        """Return the azimuth beam address code.

        Please note that if ssb_flag=True an TypeError is raised.
        """
        if self.ssb_flag:
            raise TypeError(
                "SAS SSB Data with ssb_flag=True have no "
                "azimuth_beam_address field"
            )
        else:
            return self._beam_address

    def get_sas_test(self) -> ESasTestMode:
        """Return the SAS Test flag.

        Please note that if ssb_flag=False an TypeError is raised.
        """
        if self.ssb_flag:
            return ESasTestMode(self._dynamic_data & 0b10000000)
        else:
            raise TypeError(
                "SAS SSB Data with ssb_flag=False have no sas_test field"
            )

    def get_cal_type(self) -> ESasCalType:
        """Return the calibration type code.

        Please note that if ssb_flag=False an TypeError is raised.
        """
        if self.ssb_flag:
            return ESasCalType(self._dynamic_data & 0b01110000)
        else:
            raise TypeError(
                "SAS SSB Data with ssb_flag=False have no cal_type field"
            )

    def get_calibration_beam_address(self) -> int:
        """Return the calibration beam address code.

        Please note that if ssb_flag=True an TypeError is raised.
        """
        if self.ssb_flag:
            return self._beam_address
        else:
            raise TypeError(
                "SAS SSB Data with ssb_flag=False have no "
                "calibration_beam_address field"
            )


@bpack.bs.decoder
@bpack.descriptor(baseunits=BITS, byteorder=BE)
class SesSbbData:
    """SES SBB Data (S1-IF-ASD-PL-0007, section 3.2.5.14)."""

    cal_mode: ESesCalMode = bpack.field(size=2, default=0)
    tx_pulse_number: T["u5"] = bpack.field(default=0, offset=3)
    signal_type: ESesSignalType = bpack.field(
        size=4, default=ESesSignalType.echo
    )
    swap: bool = bpack.field(default=False, offset=15)
    swath_number: T["u8"] = 0


@bpack.bs.decoder
@bpack.descriptor(baseunits=BITS, byteorder=BE)
class RadarConfigurationSupportService:
    """Radar Configuration Support Service.

    See S1-IF-ASD-PL-0007, section 3.2.5.
    """

    error_flag: bool = False
    baq_mode: EBaqMode = bpack.field(size=5, offset=3, default=EBaqMode.BYPASS)
    baq_block_len: T["u8"] = 0
    # n. 8 bits padding
    range_decimation: ERangeDecimation = bpack.field(
        size=8, offset=24, default=0
    )
    rx_gain: T["u8"] = 0
    tx_ramp_rate: T["i16"] = 0
    tx_pulse_start_freq: T["u16"] = 0
    tx_pulse_length: T["u24"] = 0
    # n. 3 bits pad
    rank: T["u5"] = bpack.field(offset=99, default=0)
    pri: T["u24"] = 0
    swst: T["u24"] = 0
    swl: T["u24"] = 0
    sas_sbb_message: SasSsbData = bpack.field(default_factory=SasSsbData)
    ses_sbb_message: SesSbbData = bpack.field(default_factory=SesSbbData)

    delta_t_suppr_sec: ClassVar[float] = 320 / 8 / REF_FREQ * 1e6
    """Return the duration of the decimation filter transiont [s].

    See S1-IF-ASD-PL-0007, section 3.2.5.11.
    """

    @property
    def baq_block_len_samples(self) -> int:
        """Length of the BAQ data block (S1-IF-ASD-PL-0007, section 3.2.5.3).

        The BAQ Block Length is the number of complex radar samples per
        BAQ block.
        The BAQ block represents a data block for which the quantisation
        is adapted according to the block statistics.
        """
        return 8 * (self.baq_block_len + 1)

    def get_range_decimation_info(self) -> RangeDecimationInfo:
        """Return information associated to Range Decimation."""
        return lookup_range_decimation_info(self.range_decimation)

    @property
    def rx_gain_db(self) -> float:
        """Rx Gain in dB (S1-IF-ASD-PL-0007, section 3.2.5.5)."""
        return -0.5 * self.rx_gain

    @property
    def tx_ramp_rate_hz_per_sec(self) -> float:
        """Tx Pulse Ramp Rate [Hz/s] (S1-IF-ASD-PL-0007, section 3.2.5.6)."""
        return self.tx_ramp_rate * REF_FREQ**2 / 2**21

    @property
    def tx_pulse_start_freq_hz(self) -> float:
        """Tx Pulse Start Frequency [Hz].

        See S1-IF-ASD-PL-0007, section 3.2.5.7).
        """
        return 1.0e6 * (
            self.tx_ramp_rate_hz_per_sec / (4 * REF_FREQ)
            + self.tx_pulse_start_freq * REF_FREQ / 2**14
        )

    @property
    def tx_pulse_length_sec(self) -> float:
        """Tx Pulse Length [s] (S1-IF-ASD-PL-0007, section 3.2.5.8)."""
        return self.tx_pulse_length / REF_FREQ * 1e6

    @property
    def tx_pulse_length_samples(self) -> int:
        """Tx Pulse Length in samples in the space packet (N3_Tx).

        Number of complex Tx pulse samples (I/Q pairs) after the decimation
        (i.e. in Space Packet).

        See S1-IF-ASD-PL-0007, section 3.2.5.8.
        """
        rdinfo = self.get_range_decimation_info()
        f_dec = rdinfo.sampling_frequency
        return math.ceil(self.tx_pulse_length_sec * f_dec)

    @property
    def pri_sec(self) -> float:
        """Pulse Repetition Interval [s].

        See S1-IF-ASD-PL-0007, section 3.2.5.10.
        """
        return self.pri / REF_FREQ * 1e6

    @property
    def swst_sec(self) -> float:
        """Return the Sampling Window Start Time [s].

        See S1-IF-ASD-PL-0007, section 3.2.5.11.
        """
        return self.swst / REF_FREQ * 1e6

    @property
    def swl_sec(self) -> float:
        """Return the Sampling Window Length [s].

        See (S1-IF-ASD-PL-0007, section 3.2.5.12).
        """
        return self.swl / REF_FREQ * 1e6

    @property
    def swl_n3rx_samples(self) -> int:  # TODO: check
        """Return the sampling Window Length in samples after the decimation.

        Number of complex samples (I/Q pairs) after decimation (i.e. in the
        Space Packet).
        See S1-IF-ASD-PL-0007, section 3.2.5.12.
        """
        rdcode = self.range_decimation
        rdinfo = self.get_range_decimation_info()
        num = rdinfo.decimation_ratio.numerator
        den = rdinfo.decimation_ratio.denominator
        nf = rdinfo.filter_length
        filter_output_offset = 80 + nf // 4
        assert filter_output_offset == lookup_filter_output_offset(rdcode)
        b = 2 * self.swl - filter_output_offset - 17
        # WARNING: not sure if it is a truncation or a rounding
        c = b - den * int(b / den)
        d = lookup_d_value(rdcode, c)
        # WARNING: not sure if it is a truncation or a rounding
        return 2 * (num * int(b / den) + d + 1)


@bpack.bs.decoder
@bpack.descriptor(baseunits=BITS, byteorder=BE, size=24)
class RadarSampleCountService:
    """Radar Sample Count Service (S1-IF-ASD-PL-0007, section 3.2.6)."""

    number_of_quads: T["u16"] = 0
    # n. 8 bits pad


@bpack.bs.decoder
@bpack.descriptor(baseunits=BITS, byteorder=BE)
class PacketSecondaryHeader:
    """Packet Secondary Header (S1-IF-ASD-PL-0007, section 3.2)."""

    datation_service: DatationService
    fixed_ancillary_data_service: FixedAncillaryDataService
    subcom_ancillary_data_service: SubCommutatedAncillaryDataService
    counters_service: CountersService
    radar_configuration_support_service: RadarConfigurationSupportService
    radar_sample_count_service: RadarSampleCountService
