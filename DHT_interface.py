import urllib.request
import socket

class DHTInterface(object):

    def __init__(self, url):
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

if __name__ == '__main__':
    d = DHTInterface('http://{}:{}'.format(socket.gethostname(), 8000))
    print('peers:{}'.format(d.peers))
    d.add_peers([b'http://atlantis:1234'])
    print('peers:{}'.format(d.peers))
    
