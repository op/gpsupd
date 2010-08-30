# -*- coding: utf-8 -*-
# Copyright (c) 2010 Örjan Persson

import logging

log = logging.getLogger(__name__)


class GoogleEarthUpdater(object):
    KML_TEMPLATE = """<?xml version="1.0" encoding="utf-8"?>
<kml xmlns="http://earth.google.com/kml/2.0">
    <Placemark>
        <name>%(name)s</name>
        <description>%(description)s</description>
        <LookAt>
            <longitude>%(longitude)f</longitude>
            <latitude>%(latitude)f</latitude>
            <range>%(range)f</range>
            <tilt>%(tilt)f</tilt>
            <heading>%(heading)f</heading>
        </LookAt>
        <Point>
            <coordinates>%(longitude)f,%(latitude)f,%(altitude)f</coordinates>
        </Point>
    </Placemark>
</kml>"""

    def __init__(self, filename):
        self.filename = filename
        self.file = None
        self.data = {'name': 'GPS Position', 'description': '',
                     'latitude': 0., 'longitude': 0.,
                     'altitude': 0., 'range': 0, 'tilt': 0,
                     'heading': 0}

    def __del__(self):
        self.close()

    def close(self):
        if self.file is not None:
            f = self.file
            self.file = None
            f.close()

    def callback(self, longitude, latitude, altitude, speed):
        data = self.data.copy()

        data.update(dict(longitude=longitude, latitude=latitude))

        if altitude is not None:
            data['altitude'] = altitude

        if speed is not None:
            data['speed'] = speed

        opened = self.file is not None
        if data != self.data and self.write(data):
            self.data = data
            if not opened:
                log.info('File %s updated with gps data.', self.filename)
            log.debug('File updated: %r', data)
        else:
            log.debug('No update')

    def write(self, data):
        if self.file is None:
            try:
                self.file = file(self.filename, 'w')
            except:
                return False

        try:
            self.file.seek(0)
            self.file.truncate()
            self.file.write(self.KML_TEMPLATE % data)
            self.file.flush()
        except:
            log.exception('Failed to write to file')
            self.file.close()
            self.file = None
            return False

        return True
