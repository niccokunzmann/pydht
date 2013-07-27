
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


__all__ = ['InMemory', 'InFileSystem', 'HTTP']
