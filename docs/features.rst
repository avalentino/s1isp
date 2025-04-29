Features
========

Implemented features
--------------------

* Decoding of primary and secondary headers
* Decoding of sub-commutated packets
* Decoding of user data fields (bypass, BAQ and FDBAQ)
* C extension for fast Huffman decoding (for FDBAQ)


Planned features and improvements
---------------------------------

* Alternative flat structure for secondary header (like the one reported
  in Table.11 of [S1PD.SP.00110.ASTR]_)
* Speed-up conversion of primary and secondary headers to `dict` and
  Pandas data frame
* Decoding of L0 index files
* Generation of index files starting from ISPs
* Generic function for RAW files processing (dumping, filtering, transcoding)
* Serialization to HDF5 (primary header, secondary header and data fields)
* Standard file format based on the IPF re-engineering data model
  (HDF5/NetCDF, Zarr)
* Read AUX-INS files
* Timeline check (using info included in the AUX-INS)
* Check LUTs against AUX-INS info
* Integrity checks
* Tool for merging multiple L0 products belonging to the same data-take
* Tool for generating L0C and L0N from L0S
* Support for missing/duplicate lines
* Support to burst modes (TOPS and Wave)
* Detection of counters wrapping (PRI count, space packet count, ...)
* Support for Sentinel-1 C/D


References
----------

.. [S1PD.SP.00110.ASTR] Sentinel-1 Level-0 Product Format Specifications,
                        Issue 01, 20 December 2012
