from . import hashing
from . import files

import urllib.parse
from http.client import HTTPError
import http.client
import socket

class HTTPMixin:
    
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
        split = urllib.parse.urlsplit(url)
        self._scheme = split.scheme
        self._host = split.host
        self._port = split.port
        self._path = split.path

    _hashing_file = files.HashingFile
    
    HTTPConnection = http.client.HTTPConnection
    HTTPSConnection = http.client.HTTPSConnection

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

    def _open_url(self, method, url, data = None):
        connection = self._connection()
        connection.connect()
        response = connection.request(method, url, data)
        return response
    
    def _get_file(self, hash):
        try:
            return self._open_url('GET', hash, 'rb')
        except HTTPError as error:
            if error.code == 404:
                return None

    def _add_readable(self, file):
        hashing_file = self._hashing_file(file)
        self._open_url('POST', hashing.NULL_HASH, data = hashing_file)
        return hashing_file.hash

    def _hashes(self):
        response = self._open_url('')
        for line in response:
            line = line.strip()
            if line:
                hash = line.decode()
                hashing.assure_is_hash(hash)
                yield hash

    def _size(self, hash):
        response = self._open_url('HEAD', hash)
        size = response.getheader('Content-Length')
        return int(size)

    def _remove(self, hash):
        raise NotImplementedError('to be implemented in future')

    def _open(self):
        return files.SpooledTemporaryFile(self)

    def get(self, hash):
        return self.get_file(hash)

__all__ = ['HTTPMixin']
