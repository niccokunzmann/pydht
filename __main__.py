#!/usr/bin/python3
import socket
import http.server
import hashlib
import base64
import io
import DHT_interface

PORT = 8000

def add_peer(url):
    peers.append(DHT_interface.DHTInterface(url))

peers = []

add_peer('http://' + socket.gethostname() + ':' + str(PORT))

strings = {}

HASHBITS = 256 # bit
HASHBYTES = int(HASHBITS / 8 * 2) # hex encoded

def add(string):
    hash = hashlib.sha256(string).hexdigest()
    strings[hash] = string
    return hash

def get(hash):
    assert len(hash) == HASHBYTES, 'expected sha256 hash with hex encoding but got {}'.format(hash)
    return strings.get(hash.lower(), None)

def get_file(hash):
    string = get(hash)
    if string is not None:
        return io.BytesIO(string)

def size(hash):
    return len(get(hash))

def is_hex(bytes):
    return all(letter in '0123456789abcdef' for letter in bytes.lower())

class DHTRequestHandler(http.server.SimpleHTTPRequestHandler):

    def is_hash(self):
        if self.path[0] != '/': return False
        hash = self.hash
        print('hash: {}'.format(repr(hash)))
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
            for peer in peers:
                pass
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
        content = b'\r\n'.join(map(lambda peer: peer.url_bytes, peers))
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
        peers = self.posted_content.splitlines()
        print('new posted peers: {}'.format(self.posted_content.splitlines()))
        for peer in peers:
            add_peer(peer)
        self.send_response(200)
        self.end_headers()

    def post_hash(self):
        hash = add(self.posted_content)
        self.send_response(200)
        self.send_header("Content-Length", str(len(hash)))
        self.end_headers()
        return io.BytesIO(hash.encode('ASCII'))
        

if __name__ == '__main__':
    http.server.test(DHTRequestHandler, port = PORT)
