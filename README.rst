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

The package requires Cython and the `bitstruct` module. Install them with the following commands::

    pip install cython
    pip install bitstruct

Build the package with::

    make ext

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
