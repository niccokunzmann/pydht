import urllib.request
import socket
import time

from pydht.hash_table import default as dht

class DHTInterface(object):

    update_hashes_seconds = 1

    def __init__(self, url, timeout = None):
        if not isinstance(url, str):
            url = url.decode('ASCII')
        if not url.endswith('/'):
            url += '/'
        self.url = url
        self.timeout = timeout
        self._hashes = set()
        self._hashes_last_update = 0

    def fullurl(self, path):
        return urllib.parse.urljoin(self.url, path)

    def urlopen(self, url, data):
        try:
            return urllib.request.urlopen(url, data, self.timeout)
        except socket.timeout:
            return None
        except urllib.error.URLError:
            return None
        
    def open(self, path, data = None):
        response = self.urlopen(self.fullurl(path), data)
        if response is None: return
        result = response.read()
        charsets = response.headers.get_charsets()
        if charsets and charsets[0]:
            result = result.decode(charsets[0])
        return result

    @property
    def peers(self):
        return self.open('peers').splitlines()

    def add_peers(self, peers):
        _peers = []
        for peer in peers:
            if hasattr(peer, 'url_bytes'):
                peer = peer.url_bytes
            if hasattr(peer, 'encode'):
                peer = peer.encode('ASCII')
            _peers.append(peer)
        return self.open('peers', b'\r\n'.join(_peers))

    def add(self, bytes):
        if isinstance(bytes, str):
            bytes = bytes.encode('utf8')
        return self.open('0' * 64, bytes)

    def get(self, hash):
        if isinstance(hash, bytes):
            hash = hash.decode('ASCII')
        try:
            return self.open(hash)
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            raise
##        except Exception:
##            import traceback
##            traceback.print_exc()

    def hashes(self):
        if self._hashes_last_update + self.update_hashes_seconds < time.time():
            self._hashes_last_update = time.time()
            response = self.open('')
            if response is None: return self._hashes
            _hashes = set()
            for hash in response.split('\r\n'):
                if dht.is_hash(hash):
                    _hashes.add(hash)
            self._hashes = _hashes
        return self._hashes

    def knows(self, hash):
        return hash in self.hashes()

    @property
    def url_bytes(self):
        return self.url.encode('ASCII')

    def __hash__(self):
        return hash(self.url)

    def __eq__(self, other):
        return hasattr(other, 'url') and other.url == self.url

    def __str__(self):
        return '<DHT {}>'.format(self.url)
        

if __name__ == '__main__':
    d = DHTInterface('http://{}:{}'.format(socket.gethostname(), 8000))
    d1 = DHTInterface('http://{}:{}'.format(socket.gethostname(), 8001))

    def test_peers():
        print('peers:{}'.format(d.peers))
        d.add_peers([b'http://atlantis:1234'])
        print('peers:{}'.format(d.peers))
    def test_store():
        hash = d.add('test!!!')
        print('hash:{}'.format(hash))
        print('test!!! == {}'.format(d.get(hash)))

    def test_hashes():
        print('hashes: {}'.format(d.hashes()))
        hash = d.add(':)')
        print('hashes: {}'.format(d.hashes()))

    def test_redirect():
        hash = d1.add('hallihallo')
        d.add_peers([d1])
        print("hallihallo == {}".format(d.get(hash)))

    test_peers()
    test_store()
    test_hashes()
    test_redirect()
