
from . import base
from . import memory_mixin
from . import file_mixin

class InMemory(memory_mixin.InMemoryMixin, base.AssociationTableBase):
    pass

class InFileSystem(file_mixin.InFileSystemMixin, base.AssociationTableBase):
    pass


__all__ = ['InMemory', 'InFileSystem']
