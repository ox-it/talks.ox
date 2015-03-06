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
            # TODO should probably test multiple formats, especially YYYY
            from_date = datetime.strptime(date_param, "%d/%m/%y")
        except Exception as e:
            # catch the exception and raise an API exception instead, which the user will see
            raise ParseError(e.message)
            # TODO should raised a more specialised error than rest framework.
    return from_date


def read_yaml_param(fname, key):
    try:
        stream = open(fname + ".yaml", "r")
        doc = yaml.load(stream)
        stream.close()
        value = doc[key]
    except IOError:
        print "Failed to load file:", fname, ".yaml"
        return ""
    except KeyError:
        print "Failed to find key", key, "in file", fname, ".yaml"
        value = ""

    return value