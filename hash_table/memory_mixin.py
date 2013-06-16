
from . import files
from . import hashing

class InMemoryMixin:
    
    def __init__(self):
        super().__init__()
        self._content = {}

    def _add_bytes(self, bytes):
        hash = hashing.algorithm(bytes).hexdigest()
        self._content[hash] = bytes
        return hash

    def _get_bytes(self, hash):
        return self._content.get(hash)

    def _hashes(self):
        return self._content.keys()

    def _remove(self, hash):
        self._content.pop(hash)

    def _open(self):
        return files.BytesIO(self)

    def get(self, hash):
        return self.get_bytes(hash)

    def _used_memory_bytes(self):
        size = 0
        for data in self._content.values():
            size += len(data)
        return size

__all__ = ['InMemoryMixin']
