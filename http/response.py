from ..errors import *

import http.client
from ..association_table.association import Association

class Response(http.client.HTTPResponse):

    @staticmethod
    def _method_for_status_code(name, doc):
        def get_(self, *args, **kw):
            code = self.getcode()
            attribute = '_get_{}_{}'.format(name, code)
            if hasattr(self, attribute):
                return getattr(self, attribute)(*args, **kw)
            raise UnexpectedStatusCode('Unexpected status code {} in get_{}'.format(code, name))
        get_.__name__ += name
        get_.__doc__ = doc
        return get_

    get_file = _method_for_status_code('file', '=> the file object with the content')

    def _get_file_404(self):
        return None

    def _get_file_200(self):
        return self

    get_file = _method_for_status_code('size', '=> size of the request body')

    def _get_size_404(self):
        return None

    def _get_size_200(self):
        size = self.getheader('Content-Length')
        if size is None:
            raise ContentLengthMissing('Response from {0} has no Content-Length'.format(request.geturl()))
        return int(size)

    def get_associations(self):
        file = self.get_file()
        associations = set()
        for line in file:
            associations.add(Association.from_line(line))
        return associations
