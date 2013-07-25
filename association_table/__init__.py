
from . import memory_mixin
from . import base

class InMemory(memory_mixin.InMemoryMixin, base.AssociationTableBase):
    pass


__all__ = ['InMemory']
