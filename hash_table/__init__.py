
from . import file_mixin
from . import memory_mixin
from . import http_mixin
from . import empty_mixin
from . import base
from ..hashing import is_hash, algorithm


class InMemory(memory_mixin.InMemoryMixin, base.HashTableBase):
    pass

class InFileSystem(file_mixin.InFileSystemMixin, base.HashTableBase):
    pass

class HTTP(http_mixin.HTTPMixin, base.HashTableBase):
    pass

HTTPS = HTTP

class Empty(empty_mixin.EmptyMixin, base.HashTableBase):
    pass


_default = None

def default():
    """=> the default hash table"""
    global _default
    if not _default:
        _default = InMemory()
    return _default
    

__all__ = ['InMemory', 'InFileSystem', 'is_hash', 'algorithm',
           'HTTP', 'HTTPS', 'Empty', 'default']
