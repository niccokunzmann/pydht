from . import files
from .. import hashing

class InMemoryMixin:
    
    def __init__(self):
        super().__init__()
        self._content = {}
        self._references = {}

    def _add_bytes(self, bytes):
        hash = hashing.algorithm(bytes).hexdigest()
        self._content[hash] = bytes
        return hash

    def _get_bytes(self, hash):
        return self._content.get(hash)

    def _get_file(self, hash):
        content = self._get_bytes(hash)
        if content is not None:
            return self.NonCheckingBytesIO(content)

    def _hashes(self):
        yield from self._content.keys()
        yield from self._references.keys()

    def _remove(self, hash):
        self._content.pop(hash, None)

    def _open(self):
        return files.BytesIO(self)

    def get(self, hash):
        return self.get_bytes(hash)

    def _used_memory_bytes(self):
        size = 0
        for data in self._content.values():
            size += len(data)
        return size

    def _add_url_reference_for_hash(self, url, hash):
        self._references.setdefault(hash, set())
        self._references[hash].add(url)
        return hash

    def _get_reference_url(self, hash):
        urls = self._references.get(hash)
        if urls is not None: return next(iter(urls))

__all__ = ['InMemoryMixin']
