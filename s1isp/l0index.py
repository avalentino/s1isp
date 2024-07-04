"""Function and classes for the management of L0 index files.

See Section 3.3.1.1.4 in S1PD.SP.00110.ASTR]_ Issue 1.8.
"""

import bpack
import bpack.st
from bpack import EBaseUnits, EByteOrder, T


@bpack.st.codec
@bpack.descriptor(size=36, byteorder=EByteOrder.BE, baseunits=EBaseUnits.BYTES)
class BlockDescriptor:
    """Block descriptor for L0 index files."""

    data_and_time: T["f8"]
    delta_time: T["f8"]
    delta_size: T["u4"]
    data_units_offset: T["u4"]
    byte_offset: T["i8"]
    variable_size_flag: bool


@bpack.st.codec
@bpack.descriptor(size=26, byteorder=EByteOrder.BE, baseunits=EBaseUnits.BYTES)
class AnnotationDataDescriptor:
    """Descriptor for L0 annotation data component files."""

    sensing_time_days: T["u2"]
    sensing_time_milliseconds: T["u4"]
    sensing_time_microseconds: T["u2"]
    downlink_time_days: T["u2"]
    downlink_time_milliseconds: T["u4"]
    downlink_time_microseconds: T["u2"]
    packe_length: T["u2"]
    frames: T["u2"]
    missing_frames: T["u2"]
    crc_flag: bool
