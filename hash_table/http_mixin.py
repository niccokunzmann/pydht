from . import hashing

import urllib.parse
import urllib.request

class HTTPMixin:
    
    def __init__(self, base_url):
        super().__init__()
        self._base_url = base_url

    def _url_for_hash(self, hash):
        return urllib.parse.urljoin(self._base_url, hash)

    _urlopen = staticmethod(urllib.request.urlopen)

    def _open_hash_file(self, hash, mode):
        url = self._path_for_hash(hash)
        return self._urlopen(url)
        
    def _get_file(self, hash):
        return self._open_hash_file(hash, 'rb')

    def _add_readable(self, file):

    def _hashes(self):

    def _size(self, hash):

    def _remove(self, hash):

    def _open(self):
        return files.SpooledTemporaryFile(self)

    def get(self, hash):
        return self.get_file(hash)
