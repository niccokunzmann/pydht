import socket
import http.server
import io

from . import peers
from .hash_table import default as default_hash_table

# TODO: redirect posts, redirect find



class DHTRequestHandler(http.server.SimpleHTTPRequestHandler):

    @property
    def hash_table(self):
        return self.server.hash_table

    def is_hash(self):
        if self.path[0] != '/': return False
        hash = self.hash
        return self.hash_table.is_hash(hash)

    @property
    def hash(self):
        return self.path[1:]

    def get_hash(self):
        hash = self.hash
        if not self.hash_table.knows(hash):
            redirect = peers.get_redirect(hash)
            if redirect is None:
                return self.send_error(404, "file not found")
            self.send_response(301)
            self.send_header("Location", redirect)
            self.end_headers()
            return 
        file = self.hash_table.get_file(hash)
        self.send_response(200)
        self.send_header("Content-Length", str(self.hash_table.size(hash)))
        self.end_headers()
        return file
    head_hash = get_hash
        
    def is_peers(self):
        return self.path == '/peers'

    def get_peers(self):
        content = b'\r\n'.join(map(lambda peer: peer.url_bytes, peers.all()))
        return self.answer_content(content)
    head_peers = get_peers

    methods = ['peers', 'hash', 'hashes']

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

    def answer_content(self, content, encoding = 'ASCII', content_type = None):
        if isinstance(content, str):
            content = content.encode(encoding)
        if content_type is None:
            content_type = self.guess_type('')
        self.send_response(200)
        self.send_header("Content-Length", str(len(content)))
        self.send_header("Content-Type", '{}; charset={}'.format(content_type, encoding))
        self.end_headers()
        return io.BytesIO(content)
        
    def post_peers(self):
        posted_peers = self.posted_content.splitlines()
        print('new posted peers: {}'.format(self.posted_content.splitlines()))
        for peer in posted_peers:
            peers.add(peer)
        self.send_response(200)
        self.end_headers()

    def post_hash(self):
        hash = self.hash_table.add(self.posted_content)
        return self.answer_content(hash)
        
    def is_hashes(self):
        return self.path == '/'

    def get_hashes(self):
        # TODO: do not load everything into memory
        hashes = '\r\n'.join(self.hash_table.hashes())
        return self.answer_content(hashes)

class DHTHTTPServer(http.server.HTTPServer):
    
    _hash_table = None
    @property
    def hash_table(self):
        if self._hash_table is None:
            return default_hash_table
        return self._hash_table

    @hash_table.setter
    def hash_table(self, hash_table):
        self._hash_table = hash_table

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('port', action='store',
                        default=8000, type=int,
                        nargs='?',
                        help='Specify alternate port [default: 8000]')
    args = parser.parse_args()
    peers.add('http://' + socket.gethostname() + ':' + str(args.port))
    http.server.test(DHTRequestHandler, DHTHTTPServer, port = args.port)


    
