# -*- coding: utf-8 -*-
# Copyright (c) 2010 Örjan Persson

import gps
import time

import gpsupd.connector as connector


class GpsdConnector(connector.GpsConnector):
    def __init__(self, address, verbose=None):
        if verbose is None:
            verbose = False
        self.__verbose = verbose
        self.__address = address

    def connect(self):
        conn = gps.gps(self.__address, verbose=self.__verbose)
        conn.stream(gps.WATCH_ENABLE|gps.WATCH_NEWSTYLE)
        return conn

    def get_positions(self):
        conn = self.connect()
        try:
            while True:
                if conn.waiting():
                    conn.poll()
                else:
                    time.sleep(0.1)
                    continue

                longitude = conn.fix.longitude
                latitude = conn.fix.latitude
                altitude = None
                speed = None

                if not gps.isnan(conn.fix.altitude):
                    altitude = conn.fix.altitude
                if not gps.isnan(conn.fix.speed):
                    speed = conn.fix.speed

                yield (longitude, latitude, altitude, speed)
        finally:
            conn.close()
