Reference dataset
=================

The reference dataset is the same ued in the `Sentinel-1 Level-0 Data
Decoding Package`_ document, inwhich it is also available a link to the
decoded version of the data::

  S1B_S3_RAW__0SDV_20200615T162409_20200615T162435_022046_029D76_F3E6


Download
========

Download the entire product form the DHUS via sentinelsat_:

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


.. _`Sentinel-1 Level-0 Data Decoding Package`:
    https://sentinel.esa.int/web/sentinel/user-guides/sentinel-1-sar/document-library/-/asset_publisher/1dO7RF5fJMbd/content/id/3316522?_com_liferay_asset_publisher_web_portlet_AssetPublisherPortlet_INSTANCE_1dO7RF5fJMbd
.. _sentinelsat: https://sentinelsat.readthedocs.io
.. _asfsmd: https://github.com/avalentino/asfsmd
