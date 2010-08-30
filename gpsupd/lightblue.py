# -*- coding: utf-8 -*-
# Copyright (c) 2010 Örjan Persson

from __future__ import absolute_import

import lightblue
import logging
import socket
import time

import gpsupd.connector as connector
import gpsupd.nmea as nmea

log = logging.getLogger(__name__)


class LightblueLineReceiver(object):
    def __init__(self, address, channel):
        self.address = address
        self.channel = channel
        self.sock = None
        self.buffer = ''

    def __del__(self):
        self.close()

    def connect(self):
        assert self.sock is None
        sock = lightblue.socket()
        log.info('Connecting to %s ...', self.address)
        sock.connect((self.address, self.channel))
        self.sock = sock
        self.buffer = ''

    def close(self):
        if self.sock is not None:
            self.sock.close()
            self.sock = None
            log.info('Disconnected from %s.', self.address)

    def readlines(self):
        assert self.sock is not None
        chunk = self.buffer + self.sock.recv(1024)

        lines = chunk.splitlines(True)
        if lines[-1].endswith('\n'):
            self.buffer = ''
        else:
            self.buffer = lines.pop()

        for line in lines:
            yield line


class LightblueConnector(connector.GpsConnector):
    def __init__(self, address, channel, checksum, verbose):
        self.address = address
        self.channel = channel
        self.checksum = checksum
        self.verbose = verbose

    def get_positions(self):
        nmeap = nmea.NmeaParser(checksum=self.checksum)
        for line in self.readlines():
            try:
                m = nmeap.parse(line)
            except:
                log.debug('Failed to parse NMEA message', exc_info=True)
                continue

            if m and m.message == 'RMC':
                yield (m.longitude, m.latitude, m.altitude, m.speed)

    def readlines(self):
        while True:
            receiver = LightblueLineReceiver(self.address, self.channel)
            try:
                receiver.connect()
                while True:
                    for line in receiver.readlines():
                        yield line
                    time.sleep(0.1)
            except socket.error, exc:
                log.error('Bluetooth connection error: %s', exc, exc_info=self.verbose)
                time.sleep(1.0)
            finally:
                receiver.close()


def select_devices():
    print 'Scanning ...'
    devices = []
    for i, (address, name, device_cls) in enumerate(lightblue.finddevices()):
        devices.append(address)
        print '%2d %30s %s' % (i+1, address, name)

    if not devices:
        print 'No devices available.'
        return None

    console = raw_input('Select devices [1]: ').split(',')
    choices = filter(lambda x: len(x) > 0, (c.strip() for c in console))
    if not choices:
        choices = [1]

    return [devices[int(c)-1] for c in choices]
