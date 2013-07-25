
from . import memory_mixin
from . import base

class InMemory(base.AssociationTableBase, mamory_mixin.InMemory):
    pass


__all__ = ['InMemory']
