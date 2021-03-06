import socket
import http.server
import io
import threading

from . import peers
from . import association_table
from . import hash_table
from .association_table.association import Association
from . import hashing

# TODO: redirect posts, redirect find



class DHTRequestHandler(http.server.SimpleHTTPRequestHandler):

    @property
    def hash_table(self):
        return self.server.hash_table

    @property
    def association_table(self):
        return self.server.association_table

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

    methods = ['peers', 'hash', 'hashes', 'association_request', 'new_associations']

    def send_head(self):
        print("path: {}".format(repr(self.path)))
        print("\thashes: {}".format(list(self.hash_table.hashes())))
        method = self.command.lower() # get, post, head
        no_method = lambda: self.send_error(404, "unsupported method {}".format(repr(method_name)))
        for name in self.methods:
            if getattr(self, 'is_' + name, lambda: False)():
                method_name = method + '_' + name
                return getattr(self, method_name, no_method)()
        return self.send_error(404, "unsupported path")

    def do_POST(self):
        self.posted_content = self.rfile.read(self.posted_length)
        print('posted content: {}'.format(repr(self.posted_content)))
        return self.do_GET()

    @property
    def posted_length(self):
        return int(self.headers.get('Content-Length'))

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

    def is_new_associations(self):
        return self.path == '/associations'

    def post_new_associations(self):
        for line in self.posted_content.splitlines():
            association = Association.from_line(line)
            self.association_table.add(association)
        self.send_response(200)
        self.end_headers()
        return None

    @property
    def association(self):
        return Association.from_string(self.path[1:])

    def is_association_request(self):
        return len(self.association) > 1

    def get_association_request(self):
        associations = self.association_table.find(self.association)
        return self.answer_content(b'\n'.join(association.to_bytes() for association in associations))
        

class DHTHTTPServer(http.server.HTTPServer):
    
    hash_table = hash_table.default()
    association_table = association_table.default()

    @classmethod
    def serve_hash_table(cls, hash_table, address,
                         RequestHandler = DHTRequestHandler):
        server = cls(address, RequestHandler)
        server.hash_table = hash_table
        thread = threading.Thread(target = server.serve_forever, daemon = True)
        thread.start()
        return server
        
    @property
    def url(self):
        return 'http://{}:{}/'.format(self.host, self.port)

    @property
    def host(self):
        host = self.socket.getsockname()[0]
        try:
            localhost = socket.gethostbyname('localhost')
        except socket.gaierror:
            pass
        else:
            if host == localhost:
                return "localhost"
        if host == '0.0.0.0':
            return self.server_name
##        return host # test

    @property
    def port(self):
        return self.server_port

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


    
