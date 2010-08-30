gpsupds
=======

GPS updater is used to retrieve gps data and to update other sources. Right now
that other source is fixed and is Google Earth.

Data can be read through GPSd_ or directly through bluetooth (using
lightblue_). The latter should only be used where GPSd_ is not available.

.. _GPSd: http://gpsd.berlios.de/
.. _lightblue: http://lightblue.sf.net/

Google Earth
------------

To get Google Earth to automatically read the file, create a network link. Just
right-click your places and add a network link. Browse to the file created by
gpsupds and set it to be updated periodically.
