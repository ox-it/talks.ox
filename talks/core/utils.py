from __future__ import absolute_import
from __future__ import print_function
from datetime import datetime, timedelta
from re import sub, compile
from sys import maxunicode

from rest_framework.exceptions import ParseError
import yaml

def clean_xml(dirty):
    if dirty is None:
        return ""

    _illegal_unichrs = [(0x00, 0x08), (0x0B, 0x0C), (0x0E, 0x1F),
                            (0x7F, 0x84), (0x86, 0x9F),
                            (0xFDD0, 0xFDDF), (0xFFFE, 0xFFFF)]
    if maxunicode >= 0x10000:  # not narrow build
            _illegal_unichrs.extend([(0x1FFFE, 0x1FFFF), (0x2FFFE, 0x2FFFF),
                                     (0x3FFFE, 0x3FFFF), (0x4FFFE, 0x4FFFF),
                                     (0x5FFFE, 0x5FFFF), (0x6FFFE, 0x6FFFF),
                                     (0x7FFFE, 0x7FFFF), (0x8FFFE, 0x8FFFF),
                                     (0x9FFFE, 0x9FFFF), (0xAFFFE, 0xAFFFF),
                                     (0xBFFFE, 0xBFFFF), (0xCFFFE, 0xCFFFF),
                                     (0xDFFFE, 0xDFFFF), (0xEFFFE, 0xEFFFF),
                                     (0xFFFFE, 0xFFFFF), (0x10FFFE, 0x10FFFF)])

    _illegal_ranges = ["%s-%s" % (chr(low), chr(high))
                       for (low, high) in _illegal_unichrs]
    _illegal_xml_chars_RE = compile(u'[%s]' % u''.join(_illegal_ranges))
    clean = _illegal_xml_chars_RE.sub('', dirty)
    return clean

def parse_date(date_param, from_date=None):
    """
    Parse the date string parameter
    :param date_param:
        Either a keyword:
            'today', 'tomorrow'
        or a string in the format 'dd/mm/yy'
        or a time delta, i.e. +7
    :from_date:
        In
    :return:
        datetime object
    """

    if not date_param:
        return None
    elif date_param == "today":
        date = datetime.today().date()
    elif date_param == "tomorrow":
        date = datetime.today().date() + timedelta(1)
    elif date_param[0:4] == "plus":
        if not from_date:
            raise ParseError("Cannot use time delta without a from date")
        try:
            delta = int(date_param[4:])
            date = from_date+timedelta(delta)
        except Exception as e:
            raise ParseError(e.message)
            date = from_d
    else:
        try:
            date = datetime.strptime(date_param, "%d/%m/%y")
        except Exception as e:
            try:
                date = datetime.strptime(date_param, "%d/%m/%Y")
            except Exception as e:
                try:
                    date = datetime.strptime(date_param, "%Y-%m-%d")
                except Exception as e:
                    # catch the exception and raise an API exception instead, which the user will see
                    raise ParseError(e.message)
                    # TODO should raised a more specialised error than rest framework.
    return date


def read_yaml_param(fname, key):
    fullname = fname + ".yaml"
    try:
        stream = open(fullname, "r")
        doc = yaml.load(stream)
        stream.close()
        value = doc[key]
    except IOError:
        print("Failed to load file:", fullname)
        return ""
    except KeyError:
        print("Failed to find key", key, "in file", fullname)
        value = ""

    return value


def iso8601_duration(value):
    """
    Get an ISO8601 duration string
    :param value: A datetime object (usually the result of enddate - startdate)
    :return: A string in ISO8601 duration format representing the length of time for value
    """

    # split seconds to larger units
    seconds = value.total_seconds()
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    days, hours, minutes = map(int, (days, hours, minutes))
    seconds = round(seconds, 6)

    ## build date
    date = ''
    if days:
        date = '%sD' % days

    ## build time
    time = u'T'
    # hours
    bigger_exists = date or hours
    if bigger_exists:
        time += '{:02}H'.format(hours)
    # minutes
    bigger_exists = bigger_exists or minutes
    if bigger_exists:
      time += '{:02}M'.format(minutes)
    # seconds
    if seconds.is_integer():
        seconds = '{:02}'.format(int(seconds))
    else:
        # 9 chars long w/leading 0, 6 digits after decimal
        seconds = '%09.6f' % seconds
    # remove trailing zeros
    seconds = seconds.rstrip('0')
    time += '{}S'.format(seconds)
    return u'P' + date + time
