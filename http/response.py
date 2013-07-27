from ..errors import *

import http.client

class Response(http.client.HTTPResponse):

    def get_file(self):
        code = self.getcode()
        attribute = '_get_file_{}'.format(code)
        if hasattr(self, attribute):
            return getattr(self, attribute)()
        raise UnexpectedStatusCode('Unexpected status code {} in get_file'.format(code))

    def _get_file_404(self):
        return None

    def _get_file_200(self):
        return self

    def get_size(self):
        code = self.getcode()
        attribute = '_get_size_{}'.format(code)
        if hasattr(self, attribute):
            return getattr(self, attribute)()
        raise UnexpectedStatusCode('Unexpected status code {} in size'.format(code))
    
    def _get_size_404(self):
        return None

    def _get_size_200(self):
        size = self.getheader('Content-Length')
        if size is None:
            raise ContentLengthMissing('Response from {0} has no Content-Length'.format(request.geturl()))
        return int(size)

