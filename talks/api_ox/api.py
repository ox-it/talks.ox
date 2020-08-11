"""This is only used for oxford dates, this should probably
be moved to typeahead.Datasource, but the API should support the
query of multiple dates at once to keep the use consistent
"""

from __future__ import absolute_import
import logging

import requests
from requests.exceptions import RequestException
from django.conf import settings

logger = logging.getLogger(__name__)


class JSONAttribute(object):
    def __init__(self, attribute):
        self.attribute = attribute

    def __get__(self, instance, owner):
        return instance._json.get(self.attribute, None)

    def __set__(self, *args):
        # Data descriptor
        raise AttributeError("This is a data descriptor!")


class ApiOxResource(object):

    _json = {}

    def __init__(self, base_url, timeout=10):
        self.base_url = base_url
        self.timeout = timeout

    def _get_request(self, path, params=None):
        try:
            r = requests.get('{base_url}{path}'.format(
                base_url=self.base_url, path=path), timeout=self.timeout)
            if r.status_code == requests.codes.ok:
                self._json = r.json()
                return r
            elif r.status_code == requests.codes.not_found:
                raise ApiNotFound()
            else:
                logger.error("Bad response code {code} from the API".format(
                    code=r.status_code))
                raise ApiException()
        except RequestException:
            logger.error("Unable to reach the API", exc_info=True)
            raise ApiException()


class OxfordDateResource(ApiOxResource):

    formatted = JSONAttribute('formatted')
    formatted_nocal = JSONAttribute('formatted_nocal')
    components = JSONAttribute('components')

    def __init__(self, base_url=settings.API_OX_DATES_URL, timeout=1):
        super(OxfordDateResource, self).__init__(base_url, timeout=timeout)

    @classmethod
    def from_date(cls, py_date, **kwargs):
        date_resource = cls(**kwargs)
        date_resource._get_request('{year}-{month}-{day}'.format(
            year=py_date.year, month=py_date.month, day=py_date.day))
        return date_resource


class ApiException(Exception):

    message = "API is not available"


class ApiNotFound(ApiException):

    message = "Resource not found"
