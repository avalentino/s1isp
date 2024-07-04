Sentinel-1 Instrument Source Packets decoder
============================================

.. badges

|GHA Status|

.. |GHA Status| image:: https://github.com/avalentino/s1isp/actions/workflows/ci.yml/badge.svg
    :target: https://github.com/avalentino/s1isp/actions
    :alt: GitHub Actions Status

.. description

`s1isp` is Python tool to decode Sentinel-1 Instrument Source Packets (ISPs)
contained in the RAW data files included in the Sentinel-1 L0 products.
It uses the bpack_ library for binary data decoding and provides a complete
set of descriptors to represent all the possible binary record of the
Sentinel-1 Instrument Source Packets (ISPs), or at least the ones related
to science data.

The relevant specification documents used to write the `s1isp` software are:

* S1-IF-ASD-PL-0007_, "Sentinel-1 SAR Space Packet Protocol Data Unit", Issue 13
* S1PD.SP.00110.ASTR_, "Sentinel-1 Level-0 Product Format Specifications", Issue 1.7


.. _bpack: https://github.com/avalentino/bpack
..  _S1PD.SP.00110.ASTR:
   https://sentinels.copernicus.eu/documents/247904/349449/Sentinel-1_Level-0_Product_Format_Specification.pdf
.. _S1-IF-ASD-PL-0007:
   https://sentinels.copernicus.eu/documents/247904/2142675/Sentinel-1-SAR-Space-Packet-Protocol-Data-Unit.pdf


Requirements and Installation
-----------------------------

The package requires Cython and the `bitstruct` module. These dependencies are
managed automatically by `setuptools` and the `pyproject.toml` file.

To install the package, use the following command::

    $ python3 -m pip install .

For editable mode, use::

    $ python3 -m pip install --editable .

For optional dependencies, use::

    $ python3 -m pip install s1isp[cli,hdf5]

The extension for Huffman decoding can be built locally using::

    $ make ext


Command line interface (CLI)
----------------------------

The package has a simple CLI::

    $ python3 -m s1isp -h
    usage: s1isp [-h] [--version]
                [--loglevel {DEBUG,INFO,WARNING,ERROR,CRITICAL}]
                [-q] [-v] [-d] [-o OUTFILE] [--skip SKIP] [--maxcount MAXCOUNT]
                [--bytes_offset BYTES_OFFSET] [--enum-value]
                [--output-format {pkl,h5,csv,xlsx}] [--force]
                [--data {none,extract,decode}]
                filename

    Sentinel-1 Instrument Source Packets decoder Command Line Interface.

    positional arguments:
    filename              RAW data file name

    options:
    -h, --help            show this help message and exit
    --version             show program's version number and exit
    --loglevel {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                            logging level (default: INFO)
    -q, --quiet           suppress standard output messages, only errors are
                            printed to screen
    -v, --verbose         print verbose output messages
    -d, --debug           print debug messages
    -o OUTFILE, --outfile OUTFILE
                            output file name for metadata (default file with
                            the same basename of the input stored in the
                            current working directory)
    --skip SKIP           number of ISPs to skip at the beginning of the file
    --maxcount MAXCOUNT   number of ISPs to dump
    --bytes_offset BYTES_OFFSET
                            number bytes to skip at the beginning of the file
    --enum-value          dump the enum numeric value instead of the symbolic name
    --output-format {pkl,h5,csv,xlsx}, --of {pkl,h5,csv,xlsx}
                            specify the output format
                            (default: <EOutputFormat.PICKLE: 'pkl'>)
    --force               overwtire the output file if it already exists
    --data {none,extract,decode}
                            control the management of the user data field data
                            (default: 'none')


License
-------

Copyright (c) 2022-2023 Antonio Valentino <antonio.valentino@tiscali.it>

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
