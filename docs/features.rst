Features
========

Implemented features
--------------------

* Decoding of primary and secondary headers
* Decoding of sub-commutated packets
* Decoding of user data fields (bypass, BAQ and FDBAQ)
* C extension for fast Huffman decoding (for FDBAQ)


Planned Features
----------------

* Alternative flat structure for secondary header
* Speed-up conversion of primary and secondary headers to Pandas data frame
* Decoding of L0 index files
* Generation of index files starting from ISPs
* Generic function for RAW files processing (dumping, filtering, transcoding)
* Conversion to HDF5 (primary header, secondary header and data fields)
* Timeline check
* Tool for merging multiple L0 products belonging to the same data-take
* Tool for generating L0C and L0N from L0S
