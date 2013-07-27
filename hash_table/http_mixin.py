from .. import hashing
from . import files
from ..errors import *

from ..http.requester import Requester

class HTTPMixin:

    Requester = Requester
    
    def __init__(self, requester):
        self._requester = self.Requester.make(requester)
        self._open_url = self._requester.open_url

    _hashing_file = files.HashingFile
    
    def _add_readable(self, file):
        hashing_file = self._hashing_file(file)
        self._open_url('POST', hashing.NULL_HASH, data = hashing_file)
        return hashing_file.hash

    def _hashes(self):
        response = self._open_url('GET', '')
        for line in response:
            line = line.strip()
            if line:
                hash = line.decode()
                hashing.assure_is_hash(hash)
                yield hash

    def _get_file(self, hash):
        response = self._open_url('GET', hash)
        return response.get_file()

    def _size(self, hash):
        response = self._open_url('HEAD', hash)
        return response.get_size()

    def _remove(self, hash):
        raise NotImplementedError('to be implemented in future')

    def _open(self):
        return files.SpooledTemporaryFile(self)

    def get(self, hash):
        return self.get_file(hash)

__all__ = ['HTTPMixin']
