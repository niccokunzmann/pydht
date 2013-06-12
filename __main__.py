#!/usr/bin/python3
import socket
import http.server
import hashlib
import base64
import io

PORT = 8000

peers = [('http://' + socket.gethostname() + ':' + str(PORT)).encode('ASCII')]

strings = {}

HASHBITS = 256 # bit
HASHBYTES = int(HASHBITS / 8)

def post(string):
    hash = hashlib.sha256(string).hexdigest()
    strings[hash] = string
    return hash

def get(hash):
    assert len(hash) == HASHBYTES, 'expected sha256 hash with hex encoding but got {}'.format(hash)
    return strings.get(hash, None)

def get_file(hash):
    string = get(hash)
    if string is not None:
        return io.BytesIO(hash)

def size(hash):
    return len(get(hash))

def is_hex(bytes):
    return all(letter in b'0123456789abcdef' for letter in bytes)

class DHTRequestHandler(http.server.SimpleHTTPRequestHandler):

    def is_hash(self):
        if self.path[0] != b'/': return False
        hash = self.hash
        if len(hash) != HASHBYTES: return False
        if not is_hex(hash): return False
        return True

    @property
    def hash(self):
        return self.path[1:]

    def get_hash(self):
        hash = self.hash
        file = get_file(hash)
        if file is None:
            return self.send_error(404, "file not found")
        self.send_response(200)
        self.send_header("Content-Length", str(size(hash)))
        #self.send_header("Last-Modified", self.date_time_string(fs.st_mtime))
        self.end_headers()
        return file
    head_hash = get_hash
        
    def is_peers(self):
        return self.path == '/peers'

    def get_peers(self):
        content = b'\r\n'.join(peers)
        file = io.BytesIO(content)
        self.send_response(200)
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        return file
    head_peers = get_peers

    methods = ['peers', 'hash']

    def send_head(self):
        print("path: {}".format(repr(self.path)))
        method = self.command.lower() # get, post, head
        for name in self.methods:
            if getattr(self, 'is_' + name, lambda: False)():
                return getattr(self, method + '_' + name,
                               lambda: self.send_error(404, "unsupported method"))()
        return self.send_error(404, "unsupported path")

    def do_POST(self):
        self.posted_content = self.rfile.read(self.posted_length)
        return self.do_GET()

    @property
    def posted_length(self):
        return int(self.headers.get('content-length', 0))

    posted_content = b''

    def post_peers(self):
        print('new posted peers: {}'.format(self.posted_content.splitlines()))
        peers.extend(self.posted_content.splitlines())
        self.send_response(200)
        self.end_headers()

if __name__ == '__main__':
    http.server.test(DHTRequestHandler, port = PORT)
