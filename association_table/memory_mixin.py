

class InMemoryMixin:

    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self._associations = {}

    def _add_association_at_index(self, index, hash, hashes_hash, hashes):
        associations = self._associations
        if (hash, index) not in associations:
            associations.setdefault((hash, index), set())
        associations[(hash, index)].add(hashes_hash)

    def _get_association_hashes_at_index(self, index, hash):
        return associations[(hash, index)].get(set())
    
__all__ = ['InMemoryMixin']
