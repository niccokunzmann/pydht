import pprint

class InMemoryMixin:

    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self._associations = {}

    def _add_association_at_index(self, index, hash, hashes_hash, hashes):
        associations = self._associations
        if (hash, index) not in associations:
            associations.setdefault((hash, index), set())
        associations[(hash, index)].add(tuple(hashes))

    def _get_association_hashes_at_index(self, index, hash):
        pprint.pprint(self._associations)
        return self._associations.get((hash, index), set())
    
__all__ = ['InMemoryMixin']
