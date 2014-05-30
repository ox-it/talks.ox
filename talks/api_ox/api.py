import logging

import requests
from requests.exceptions import RequestException

logger = logging.getLogger(__name__)


class ApiOxResource(object):

    def __init__(self, base_url, timeout=1):
        self.base_url = base_url
        self.timeout = timeout

    def _get_request(self, path, params=None):
        try:
            r = self._get_request(path)
            if r.status_code == requests.codes.ok:
                return r.json()
            elif r.status_code == requests.codes.not_found:
                raise ApiNotFound()
            else:
                logger.error("Bad response code {code} from the API".format(code=r.status_code))
                raise ApiException()
        except RequestException as re:
            logger.error("Unable to reach the API", exc_info=True)
            raise ApiException()


class PlacesResource(ApiOxResource):

    PATH = '/places/'

    def get_by_id(self, ident):
        return self._get_request('{path}{ident}'.format(path=self.PATH, ident=ident))

    def get_organisation_descendants(self, ident):
        return self._get_request('{path}{ident}/organisation-descendants'.format(path=self.PATH, ident=ident))


class ApiException(Exception):

    message = "API is not available"


class ApiNotFound(ApiException):

    message = "Resource not found"
