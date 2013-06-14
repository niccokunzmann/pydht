#!/usr/bin/python3
import socket
import http.server
import io
import argparse

import peers
import dht
import contextlib
import threading

# TODO: redirect posts, redirect find



class DHTRequestHandler(http.server.SimpleHTTPRequestHandler):

    def is_hash(self):
        if self.path[0] != '/': return False
        hash = self.hash
        return dht.is_hash(hash)

    @property
    def hash(self):
        return self.path[1:]

    def get_hash(self):
        hash = self.hash
        file = dht.get_file(hash)
        if file is None:
            redirect = peers.get_redirect(hash)
            if redirect is None:
                return self.send_error(404, "file not found")
            self.send_response(301)
            self.send_header("Location", redirect)
            self.end_headers()
            return None
            return 
        self.send_response(200)
        self.send_header("Content-Length", str(dht.size(hash)))
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
        hash = dht.add(self.posted_content)
        return self.answer_content(hash)
        
    def is_hashes(self):
        return self.path == '/'

    def get_hashes(self):
        hashes = '\r\n'.join(dht.all())
        return self.answer_content(hashes)


if __name__ == '__main__':
    import threading
    parser = argparse.ArgumentParser()
    parser.add_argument('port', action='store',
                        default=8000, type=int,
                        nargs='?',
                        help='Specify alternate port [default: 8000]')
    args = parser.parse_args()
    peers.add('http://' + socket.gethostname() + ':' + str(args.port))
    http.server.test(DHTRequestHandler, port = args.port)
