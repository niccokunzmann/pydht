import urllib.request
import socket

class DHTInterface(object):

    def __init__(self, url):
        if isinstance(url, bytes):
            url = url.decode('ASCII')
        if not url.endswith('/'):
            url += '/'
        self.url = url

    def open(self, path, data = None):
        response = urllib.request.urlopen(urllib.parse.urljoin(self.url, path), data)
        return response.read()

    @property
    def peers(self):
        return self.open('peers').splitlines()

    def add_peers(self, peers):
        return self.open('peers', b'\r\n'.join(peers))

    def add(self, bytes):
        if isinstance(bytes, str):
            bytes = bytes.encode('utf8')
        return self.open('0' * 64, bytes)

    def get(self, hash):
        if isinstance(hash, bytes):
            hash = hash.decode('ASCII')
        return self.open(hash)

    @property
    def url_bytes(self):
        return self.url.encode('ASCII')
        

if __name__ == '__main__':
    d = DHTInterface('http://{}:{}'.format(socket.gethostname(), 8000))
    def test_peers():
        print('peers:{}'.format(d.peers))
        d.add_peers([b'http://atlantis:1234'])
        print('peers:{}'.format(d.peers))
    def test_store():
        hash = d.add('test!!!')
        print('hash:{}'.format(hash))
        print('test!!1 == {}'.format(d.get(hash)))

    test_peers()
    test_store()
