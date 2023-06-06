"""Constants for Sentinel-1 RAW data decoding.

Constants defined in the "Sentinel-1 SAR Space Packet Protocol Data Unit"
document (S1-IF-ASD-PL-0007) issue 13.
"""

REF_FREQ = 37.53472224  # [MHz]
SYNC_MARKER = 0x352EF853  # (S1-IF-ASD-PL-0007, section 3.2.2.1)

PRIMARY_HEADER_SIZE = 6  # (S1-IF-ASD-PL-0007, section 3.1)
SECONDARY_HEADER_SIZE = 62  # (S1-IF-ASD-PL-0007, section 3.2)
