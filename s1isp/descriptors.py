"""Sentinel-1 Instrument Source Packets (ISP) descriptors.

The definotion of all the ISP records is provided in the "Sentinel-1 SAR
Space Packet Protocol Data Unit" document (S1-IF-ASD-PL-0007) issue 13.
"""

import math
from typing import Union

import bpack
import bpack.bs
from bpack import T

from .luts import (
    lookup_d_value,
    lookup_filter_output_offset,
    lookup_range_decimation_info,
    RangeDecimationInfo,
)
from .enums import (
    EBaqMode,
    ECalMode,
    ECalType,
    ETestMode,
    EEccNumber,
    EAocsOpMode,
    ESignalType,
    ERxChannelId,
    ESasTestMode,
    EPolarization,
    ERangeDecimation,
    ETemperatureCompensation,
)
from .constants import REF_FREQ, SYNK_MARKER

BITS = bpack.EBaseUnits.BITS
BE = bpack.EByteOrder.BE


class SyncMarkerException(RuntimeError):
    """Sync marker error."""

    pass


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

    def get_fine_time_sec(self) -> float:
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
class SasImgData:
    """SAS SBB Data (S1-IF-ASD-PL-0007, section 3.2.5.13.1).

    The SAS SSB Data field indicates the actual configuration of the
    SAR Antenna Subsystem (SAS).
    """

    ssb_flag: bool = False
    polarization: EPolarization = bpack.field(
        size=3, default=EPolarization.h_tx_only
    )
    temperature_compensation: ETemperatureCompensation = bpack.field(
        size=2, default=ETemperatureCompensation.fe_off_ta_off
    )
    elevation_beam_address: T["u4"] = bpack.field(default=0, offset=8)
    azimuth_beam_address: T["u10"] = bpack.field(default=0, offset=14)


@bpack.bs.decoder
@bpack.descriptor(baseunits=BITS, byteorder=BE)
class SasCalData:
    """SAS SBB Data (S1-IF-ASD-PL-0007, section 3.2.5.13.2).

    The SAS SSB Data field indicates the actual configuration of the
    SAR Antenna Subsystem (SAS).
    """

    ssb_flag: bool = False
    polarization: EPolarization = bpack.field(
        size=3, default=EPolarization.h_tx_only
    )
    temperature_compensation: ETemperatureCompensation = bpack.field(
        size=2, default=ETemperatureCompensation.fe_off_ta_off
    )
    sas_test: bool = bpack.field(default=0, offset=8)
    cal_type: T["u3"] = bpack.field(default=0)
    calibration_beam_address: T["u10"] = bpack.field(default=0, offset=14)


@bpack.bs.decoder
@bpack.descriptor(baseunits=BITS, byteorder=BE)
class SasSsbData:
    """SAS SBB Data (S1-IF-ASD-PL-0007, section 3.2.5.13).

    The SAS SSB Data field indicates the actual configuration of the
    SAR Antenna Subsystem (SAS).
    """

    ssb_flag: bool = False
    polarization: EPolarization = bpack.field(
        size=3, default=EPolarization.h_tx_only
    )
    temperature_compensation: ETemperatureCompensation = bpack.field(
        size=2, default=ETemperatureCompensation.fe_off_ta_off
    )
    _dynamic_data: T["u4"] = bpack.field(default=0, offset=8)
    _beam_address: T["u10"] = bpack.field(default=0, offset=14)

    def get_sas_data(self) -> Union[SasImgData, SasCalData]:
        """Return the specific SAS data record accordingthe sas_flag.

        If the `ssb_flag` is True than and `SasSsbDataImaging` instance is
        returned, otherwise a `SasSsbDataCal` instance is returned.
        """
        if not self.ssb_flag:
            return SasImgData(
                self.ssb_flag,
                self.polarization,
                self.temperature_compensation,
                self.get_elevation_beam_address(),
                self.get_azimuth_beam_address(),
            )
        else:
            return SasCalData(
                self.ssb_flag,
                self.polarization,
                self.temperature_compensation,
                self.get_sas_test(),
                self.get_cal_type(),
                self.get_calibration_beam_address(),
            )

    def get_elevation_beam_address(self, check: bool = True) -> int:
        """Return the elevation beam address code.

        Please note that if `ssb_flag` is `True` and `check` is `True` then
        a TypeError is raised.
        """
        if check and self.ssb_flag:
            raise TypeError(
                "SAS SSB Data with ssb_flag=True have no "
                "elevation_beam_address field"
            )
        else:
            return self._dynamic_data

    def get_azimuth_beam_address(self, check: bool = True) -> int:
        """Return the azimuth beam address code.

        Please note that if `ssb_flag` is `True` and `check` is `True` then
        a TypeError is raised.
        """
        if check and self.ssb_flag:
            raise TypeError(
                "SAS SSB Data with ssb_flag=True have no "
                "azimuth_beam_address field"
            )
        else:
            return self._beam_address

    def get_sas_test(self, check: bool = True) -> ESasTestMode:
        """Return the SAS Test flag.

        Please note that if `ssb_flag` is `False` and `check` is `True` then
        an TypeError is raised.
        """
        if check and not self.ssb_flag:
            raise TypeError(
                "SAS SSB Data with ssb_flag=False have no sas_test field"
            )
        else:
            return ESasTestMode((self._dynamic_data >> 3) & 0b0000001)

    def get_cal_type(self, check: bool = True) -> ECalType:
        """Return the calibration type code.

        Please note that if `ssb_flag` is `False` and `check` is `True` then
        an TypeError is raised.
        """
        if check and not self.ssb_flag:
            raise TypeError(
                "SAS SSB Data with ssb_flag=False have no cal_type field"
            )
        else:
            return ECalType(self._dynamic_data & 0b00000111)

    def get_calibration_beam_address(self, check: bool = True) -> int:
        """Return the calibration beam address code.

        Please note that if `ssb_flag` is `False` and `check` is `True` then
        an TypeError is raised.
        """
        if check and not self.ssb_flag:
            raise TypeError(
                "SAS SSB Data with ssb_flag=False have no "
                "calibration_beam_address field"
            )
        else:
            return self._beam_address


@bpack.bs.decoder
@bpack.descriptor(baseunits=BITS, byteorder=BE)
class SesSbbData:
    """SES SBB Data (S1-IF-ASD-PL-0007, section 3.2.5.14)."""

    cal_mode: ECalMode = bpack.field(size=2, default=0)
    tx_pulse_number: T["u5"] = bpack.field(default=0, offset=3)
    signal_type: ESignalType = bpack.field(size=4, default=ESignalType.echo)
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
    tx_ramp_rate: T["u16"] = 0
    tx_pulse_start_freq: T["u16"] = 0
    tx_pulse_length: T["u24"] = 0
    # n. 3 bits pad
    rank: T["u5"] = bpack.field(offset=99, default=0)
    pri: T["u24"] = 0
    swst: T["u24"] = 0
    swl: T["u24"] = 0
    sas_sbb_message: SasSsbData = bpack.field(default_factory=SasSsbData)
    ses_sbb_message: SesSbbData = bpack.field(default_factory=SesSbbData)

    def get_baq_block_len_samples(self) -> int:
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

    def get_rx_gain_db(self) -> float:
        """Rx Gain in dB (S1-IF-ASD-PL-0007, section 3.2.5.5)."""
        return -0.5 * self.rx_gain

    def _get_tx_ramp_rate_mhz_per_usec(self) -> float:
        """Tx Pulse Ramp Rate [Hz/s] (S1-IF-ASD-PL-0007, section 3.2.5.6)."""
        sign = 1 if self.tx_ramp_rate >> 15 else -1
        value = self.tx_ramp_rate & 0b0111111111111111

        return sign * (value * REF_FREQ**2 / 2**21)

    def get_tx_ramp_rate_hz_per_sec(self) -> float:
        """Tx Pulse Ramp Rate [Hz/s] (S1-IF-ASD-PL-0007, section 3.2.5.6)."""
        return self._get_tx_ramp_rate_mhz_per_usec() * 1e12

    def get_tx_pulse_start_freq_hz(self) -> float:
        """Tx Pulse Start Frequency [Hz].

        See S1-IF-ASD-PL-0007, section 3.2.5.7).
        """
        sign = 1 if self.tx_pulse_start_freq >> 15 else -1
        value = self.tx_pulse_start_freq & 0b0111111111111111
        return 1e6 * (
            self._get_tx_ramp_rate_mhz_per_usec() / (4 * REF_FREQ)
            + sign * value * REF_FREQ / 2**14
        )

    def get_tx_pulse_length_sec(self) -> float:
        """Tx Pulse Length [s] (S1-IF-ASD-PL-0007, section 3.2.5.8)."""
        return self.tx_pulse_length / REF_FREQ * 1e-6

    def get_tx_pulse_length_samples(self) -> int:
        """Tx Pulse Length in samples in the space packet (N3_Tx).

        Number of complex Tx pulse samples (I/Q pairs) after the decimation
        (i.e. in Space Packet).

        See S1-IF-ASD-PL-0007, section 3.2.5.8.
        """
        rdinfo = self.get_range_decimation_info()
        f_dec = rdinfo.sampling_frequency
        return math.ceil(self.get_tx_pulse_length_sec() * f_dec)

    def get_pri_sec(self) -> float:
        """Pulse Repetition Interval [s].

        See S1-IF-ASD-PL-0007, section 3.2.5.10.
        """
        return self.pri / REF_FREQ * 1e-6

    def get_swst_sec(self) -> float:
        """Return the Sampling Window Start Time [s].

        See S1-IF-ASD-PL-0007, section 3.2.5.11.
        """
        return self.swst / REF_FREQ * 1e-6

    def get_delta_t_suppr_sec(self) -> float:
        """Duration of teh transient of teh decimation filter [s].

        See (S1-IF-ASD-PL-0007, section 3.2.5.11).
        """
        return 320 / 8 / REF_FREQ * 1e-6

    def get_swst_after_decimation_sec(self) -> float:
        """Return the Sampling Window Start Time [s].

        See S1-IF-ASD-PL-0007, section 3.2.5.11.
        """
        return (self.swst + 320 / 8) / REF_FREQ * 1e-6

    def get_swl_sec(self) -> float:
        """Return the Sampling Window Length [s].

        See (S1-IF-ASD-PL-0007, section 3.2.5.12).
        """
        return self.swl / REF_FREQ * 1e-6

    def get_swl_n3rx_samples(self) -> int:
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

    def get_swl_n3rx_sec(self) -> int:
        """Return the sampling Window Length in seconds after the decimation.

        See S1-IF-ASD-PL-0007, section 3.2.5.12.
        """
        fs = self.get_range_decimation_info().sampling_frequency
        return self.get_swl_n3rx_samples() / fs


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
