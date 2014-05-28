import requests
from requests.exceptions import RequestException


class ApiOxResource(object):

    def __init__(self, base_url, timeout=1):
        self.base_url = base_url
        self.timeout = timeout

    def _get_request(self, path, params=None):
        return requests.get('{base_url}{path}'.format(base_url=self.base_url, path=path), timeout=self.timeout)


class PlacesResource(ApiOxResource):

    PATH = '/places/'

    def get_by_id(self, ident):
        try:
            r = self._get_request('{path}{ident}'.format(path=self.PATH, ident=ident))
            if r.status_code == requests.codes.ok:
                return r.json()
            elif r.status_code == requests.codes.not_found:
                raise ApiNotFound()
            else:
                raise ApiException()
        except RequestException:
            raise ApiException()




class ApiException(Exception):

    message = "API is not available"


class ApiNotFound(ApiException):

    message = "Resource not found"
