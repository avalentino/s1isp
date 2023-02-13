Reference dataset
=================

S1B_S3_RAW__0SDV_20200615T162409_20200615T162435_022046_029D76_F3E6.


Download
========

Download the entire product form the DHUS cia sentinelsat_:

.. code-block:: shell

    $ sentinelsat \
    --name S1B_S3_RAW__0SDV_20200615T162409_20200615T162435_022046_029D76_F3E6 \
    --download


Download only the relevant data files (e.g. for the VVpolarization) from
the ASF archive using asfsmd_:

.. code-block:: shell

    $ asfsmd --pol vv --data \
      S1B_S3_RAW__0SDV_20200615T162409_20200615T162435_022046_029D76_F3E6


Direct URLs:

* https://scihub.copernicus.eu/dhus/odata/v1/Products('81aa3593-3234-4a45-b1ed-e9ac30fae01d')/$value
* https://datapool.asf.alaska.edu/RAW/SB/S1B_S3_RAW__0SDV_20200615T162409_20200615T162435_022046_029D76_F3E6.zip


.. _sentinelsat: https://sentinelsat.readthedocs.io
.. _asfsmd: https://github.com/avalentino/asfsmd
