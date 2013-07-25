from . import files
from .. import hashing

class EmptyMixin:

    def _add_bytes(self, bytes):
        hash = hashing.algorithm(bytes).hexdigest()
        return hash

    def _get_bytes(self, hash):
        return None

    def _hashes(self):
        return []

    def _remove(self, hash):
        pass

    def _open(self):
        return files.BytesIO(self)

    def get(self, hash):
        return None

__all__ = ['EmptyMixin']
