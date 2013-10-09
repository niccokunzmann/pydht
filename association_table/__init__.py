
from . import base
from . import memory_mixin
from . import file_mixin
from . import http_mixin

class InMemory(memory_mixin.InMemoryMixin, base.AssociationTableBase):
    @staticmethod
    def default_hash_table(*args, **kw):
        from pydht.hash_table import InMemory
        return InMemory(*args, **kw)

class InFileSystem(file_mixin.InFileSystemMixin, base.AssociationTableBase):
    @staticmethod
    def default_hash_table(*args, **kw):
        from pydht.hash_table import InFileSystem
        return InFileSystem(*args, **kw)

class HTTP(http_mixin.HTTPMixin, base.AssociationTableBase):
    @staticmethod
    def default_hash_table(*args, **kw):
        from pydht.hash_table import HTTP
        return HTTP(*args, **kw)

_default = None

def default():
    """=> the default association table"""
    global _default
    if not _default:
        from .. import hash_table
        _default = InMemory(hash_table.default())
    return _default
    

__all__ = ['InMemory', 'InFileSystem', 'HTTP', 'default']
