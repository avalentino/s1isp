Sentinel-1 Instrument Source Packets decoder
============================================

`s1isp` is Python tool to decode Sentinel-1 Intrument Source Packets (ISPs)
contained in the RAW data files included in the Sentinel-1 L0 products.
It uses the bpack_ library for binary data decoding and provides a complete
set of descriptors to represent all the possible binary record of the
Sentinel-1 Instrument Source Packets (ISPs), or at least the ones related
to science data.

The relevant specification used to write the `s1isp` software are:

* `Sentinel-1 Level-0 Product Format Specifications, S1PD.SP.00110.ASTR Issue 1.7
   <https://sentinels.copernicus.eu/documents/247904/349449/Sentinel-1_Level-0_Product_Format_Specification.pdf>`_
* `Sentinel-1 SAR Space Packet Protocol Data Unit, S1-IF-ASD-PL-0007 Issue 13
   <https://sentinels.copernicus.eu/documents/247904/2142675/Sentinel-1-SAR-Space-Packet-Protocol-Data-Unit.pdf>`_


.. _bpack: https://github.com/avalentino/bpack


License
-------

Copyright 2022-2023 Antonio Valentino <antonio.valentino@tiscali.it>

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
