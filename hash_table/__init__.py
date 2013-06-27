
from . import file_mixin
from . import memory_mixin
from . import http_mixin
from . import base
from .errors import HashNotFound
from .hashing import is_hash, algorithm


class InMemory(memory_mixin.InMemoryMixin, base.HashTableBase):
    pass

class InFileSystem(file_mixin.InFileSystemMixin, base.HashTableBase):
    pass


class HTTP(http_mixin.HTTPMixin, base.HashTableBase):
    pass

HTTPS = HTTP

__all__ = ['InMemory', 'InFileSystem', 'HashNotFound', 'is_hash', 'algorithm',
           'HTTP', 'HTTPS']
