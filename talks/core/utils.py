from datetime import datetime, timedelta

from rest_framework.exceptions import ParseError
import yaml

def parse_date(date_param):
    """
    Parse the date string parameter
    :param date_param:
        Either a keyword:
            'today', 'tomorrow'
        or a string in the format 'dd/mm/yy'
    :return:
        datetime object
    """
    if not date_param:
        return None
    elif date_param == "today":
        from_date = datetime.today().date()
    elif date_param == "tomorrow":
        from_date = datetime.today().date() + timedelta(1)
    else:
        try:
            from_date = datetime.strptime(date_param, "%d/%m/%y")
        except Exception as e:
            try:
                from_date = datetime.strptime(date_param, "%d/%m/%Y")
            except Exception as e:
                try:
                    from_date = datetime.strptime(date_param, "%Y-%m-%d")
                except Exception as e:
                    # catch the exception and raise an API exception instead, which the user will see
                    raise ParseError(e.message)
                    # TODO should raised a more specialised error than rest framework.
    return from_date


def read_yaml_param(fname, key):
    fullname = fname + ".yaml"
    try:
        stream = open(fullname, "r")
        doc = yaml.load(stream)
        stream.close()
        value = doc[key]
    except IOError:
        print "Failed to load file:", fullname
        return ""
    except KeyError:
        print "Failed to find key", key, "in file", fullname
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
