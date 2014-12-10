import os
import logging
import mock
import requests

from robot.libraries.BuiltIn import BuiltIn
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.core.management import call_command
from django.conf import settings
from django.contrib.staticfiles.finders import find as find_static_file


def intercept_requests_to_statics(url, *a, **k):
    """
    Utility function to use with mock.path.
    Blocks all requests through `requests.get` except for those to local static files.
    In that case makes `requests.get` return file content without going through `httplib`
    """
    logging.info("intercept: %s", url)
    if url.startswith(settings.STATIC_URL):
        r = requests.Response()
        try:
            path = url[len(settings.STATIC_URL):]
            path = path.split('?')[0]  # FIXME use urlparse
            file_path = find_static_file(path)
            logging.info("path:%r", path)
            logging.info("file+path:%r", file_path)
            if file_path and os.path.isfile(file_path):
                with open(file_path) as f:
                    r._content = f.read()
                    r.status_code = 200
                    logging.info("response: %s", r._content)
                    logging.info("response: %s", r.content)
            else:
                r.status_code = 404
        except Exception, e:
            r.status_code = 500
            r.reason = e.message
            import traceback
            r._content = traceback.format_exc()
        finally:
            logging.info("response: %s", r._content)
            return r
    raise AssertionError("External request detected: %s" % url)


def patch_requests():
    """Mocks requests.get
    """
    requests_patcher = mock.patch('requests.get', autospec=True)
    requests_get = requests_patcher.start()
    requests_get.side_effect = intercept_requests_to_statics
    return requests_patcher


class Server(object):
    def __init__(self):
        self._tc = StaticLiveServerTestCase('__init__')

    def start_server(self):
        self._requests_patcher = patch_requests()
        self._tc.setUpClass()
        logging.info("Server started: %s", self._tc.live_server_url)
        BuiltIn().set_suite_variable('${HOST}', self._tc.live_server_url)

    def stop_server(self):
        self._tc.tearDownClass()
        self._requests_patcher.stop()

    def server_command(self, name, *args, **kwargs):
        call_command(name, *args, **kwargs)

server = Server
