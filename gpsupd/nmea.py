# -*- coding: utf-8 -*-
# Copyright (c) 2010 Örjan Persson

import logging
import re

log = logging.getLogger(__name__)


class NmeaMessages(type):
    """NMEA Messages

    Keeps a registry over all known NMEA messages. By default the name of the
    message is derived from the name of the class. If the name of the message
    is other than the name of the class, set the `message` attribute of the
    class.
    """
    registry = {}

    def __new__(cls, name, bases, attrs):
        new = super(NmeaMessages, cls).__new__(cls, name, bases, attrs)
        message = getattr(new, 'message', name)
        if message is not None:
            NmeaMessages.registry[message] = new
        return new

    @classmethod
    def construct(cls, name, talker, *args, **kwargs):
        r = cls.registry.get(name)
        if r is not None:
            r = r(*args, **kwargs)
            r.message = name
            r.talker = talker
        return r


class Message(object):
    """NMEA Message"""
    __metaclass__ = NmeaMessages

    def __init__(self, message=None, talker=None, *args, **kwargs):
        super(Message, self).__init__(*args, **kwargs)
        self.message = message
        self.talker = talker


class AAM(Message):
    """Arrival Alarm"""
    def __init__(self, ce, pp, radius, nm, wn, *args, **kwargs):
        super(AAM, self).__init__(*args, **kwargs)
        self.ce = ce
        self.pp = pp
        self.radius = radius
        self.nm = nm
        self.wn = wn


class GSV(Message):
    """Satellites in view"""
    def __init__(self, count, origin, total, *args, **kwargs):
        self.count = int(count)
        self.origin = origin
        self.total = total

        class Satellite(object):
            def __init__(self, pnr, elevation, azimuth, snr):
                self.pnr = pnr
                self.elevation = elevation
                self.azimuth = azimuth
                self.snr = snr

        self.sattelites = []
        args = list(args)
        while len(args) >= 4:
            pnr = args.pop(0)
            elevation = args.pop(0)
            azimuth = args.pop(0)
            snr = args.pop(0)
            self.sattelites.append(Satellite(pnr, elevation, azimuth, snr))

        super(GSV, self).__init__(*args, **kwargs)


class RMC(Message):
    """Recommended Minimum sentence C"""
    def __init__(self, clock, status, latitude, n_or_s,
                 longitude, e_or_w, speed, direction, date, variation,
                 variation_e_or_w, faa_mode, *args, **kwargs):
        super(RMC, self).__init__(*args, **kwargs)

        self.longitude = float(longitude)
        self.latitude = float(latitude)

        if n_or_s == 'S':
            self.longitude *= -1
        if e_or_w == 'W':
            self.latitude *= -1

        try:
            self.speed = float(speed)
        except ValueError:
            self.speed = None

        self.altitude = None


class NmeaError(Exception):
    pass


class ParseError(NmeaError):
    pass


class ChecksumMismatch(ParseError):
    pass


class NmeaParser(object):
    NMEA_RE = re.compile(r'^\$(\w{2})(\w{3}),([^*\r\n]+)(?:\*([A-Fa-f\d+]+))?[\r\n]+$')

    def __init__(self, checksum=None, *args, **kwargs):
        super(NmeaParser, self).__init__(*args, **kwargs)
        if checksum is None:
            checksum = True
        self.checksum = checksum

    def parse(self, line):
        m = self.NMEA_RE.match(line)
        if not m:
            raise ParseError('Failed to parse line')

        talker, msg, args, chksum = m.groups()

        if self.checksum and chksum is not None:
            l = (talker, msg, ',', args)
            chksum = int(chksum, 16)
            if self.__calculate_checksum(*l) != chksum:
                raise ChecksumMismatch('Calculated checksum mismatch')

        args = args.split(',')
        log.debug('talker: %s, msg: %s, args: %r', talker, msg, args)

        return NmeaMessages.construct(msg, talker, *args)

    def __calculate_checksum(self, *parts):
        """Calculate message checksum

        The checksum in the NMEA specification is an XOR of all characters
        between the $ and *.
        """
        checksum = 0
        for p in parts:
            for s in p:
                checksum ^= ord(s)
        return checksum
