
from ..errors import *

import urllib.parse

import http.client
import socket

from .response import Response

class Requester:

    HTTPConnection = http.client.HTTPConnection
    HTTPSConnection = http.client.HTTPSConnection

    @classmethod
    def set_response_class(cls, _response_class):
        class HTTPConnection(cls.HTTPConnection):
            response_class = _response_class
        cls.HTTPConnection = HTTPConnection
        class HTTPSConnection(cls.HTTPSConnection):
            response_class = _response_class
        cls.HTTPSConnection = HTTPSConnection

    @classmethod
    def make(cls, url_or_requester):
        if hasattr(url_or_requester, 'is_requester') and \
           url_or_requester.is_requester():
            return url_or_requester
        return cls(url_or_requester)

    @staticmethod
    def is_requester(self):
        return True
    
    def __init__(self, base_url = None,
                 timeout = socket._GLOBAL_DEFAULT_TIMEOUT,
                 key_file = None, cert_file = None, ssl_context = None,
                 check_hostname = None):
        super().__init__()
        if base_url is not None:
            self.set_base_url(base_url)
        self._key_file = key_file
        self._cert_file = cert_file
        self._ssl_context = ssl_context
        self._check_hostname = check_hostname
        self._timeout = timeout

    def set_base_url(self, url):
        split = urllib.parse.urlparse(url)
        self._scheme = split.scheme
        self._host = split.hostname
        self._port = split.port
        self._path = split.path
        if not self._path[-1:] == '/':
            self._path += '/'

    def get_HTTPSConnection(self):
        return self.HTTPSConnection(self._host, self._port,
                                    self._key_file, self._cert_file,
                                    timeout = self._timeout,
                                    context = self._ssl_context,
                                    check_hostname = self._check_hostname)

    def get_HTTPConnection(self):
        return self.HTTPConnection(self._host, self._port,
                                   timeout = self._timeout)

    def _connection(self):
        if self._scheme == 'http':
            return self.get_HTTPConnection()
        if self._scheme == 'https':
            return self.get_HTTPSConnection()
        else:
            msg = 'expected scheme to be http and not {}'.format(self._scheme)
            raise ValueError(msg)

    @staticmethod
    def path_join(path1, path2):
        if path2[:1] == '/':
            return path1 + path2[1:]
        else:
            return  path1 + path2

    def open_url(self, method, url, data = None):
        connection = self._connection()
        connection.connect()
        # TODO: send content length or chunk content
        connection.request(method, self.path_join(self._path, url), data)
        return connection.getresponse()
            
Requester.set_response_class(Response)
