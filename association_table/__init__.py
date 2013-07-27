
from . import base
from . import memory_mixin
from . import file_mixin
from . import http_mixin

class InMemory(memory_mixin.InMemoryMixin, base.AssociationTableBase):
    pass

class InFileSystem(file_mixin.InFileSystemMixin, base.AssociationTableBase):
    pass

class HTTP(http_mixin.HTTPMixin, base.AssociationTableBase):
    pass

_default = None

def default():
    """=> the default association table"""
    global _default
    if not _default:
        from .. import hash_table
        _default = InMemory(hash_table.default())
    return _default
    

__all__ = ['InMemory', 'InFileSystem', 'HTTP', 'default']
