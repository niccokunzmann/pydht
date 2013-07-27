
import pydht.hashing as hashing
from collections import Iterable

class AssociationTableBase:

    from .association import Association

    def __init__(self, hash_table, *args, **kw):
        super().__init__(*args, **kw)
        self.hash_table = hash_table

    @staticmethod
    def is_hash(hash):
        return isinstance(hash, str) and hashing.is_hash(hash)

    @staticmethod
    def is_association(association):
        """=> whether the association is a Association of hashes"""
        return isinstance(association, Iterable)

    def is_association_template(self, association):
        """=> whether the association is a tuple of hashes or None"""
        return isinstance(association, Iterable) and \
               all(map(lambda hash: self.is_hash(hash) or hash is None,
                       association))

    def _convert_to_association(self, object):
        if self.is_hash(object):
            bytes = self.hash_table.get_bytes(object)
            association = self.Association.from_bytes(bytes)
        elif isinstance(object, tuple):
            hashes = []
            for hash in object:
                if hash is None: continue
                if not self.is_hash(hash):
                    hash = self.hash_table.add(hash)
                hashes.append(hash)
            association = self.Association.from_hashes(hashes)
        if isinstance(association, self.Association):
            return association
        else:
            raise TypeError('Expected Association but got type {}: {}'.format(type(association), repr(association)))

    def add(self, data):
        if self.is_association(data):
            return self._add_association(self._convert_to_association(data))
        return self._add(data)

    WRONG_ADD_ARGUMENT = 'Object {object} of type {type} can not be '\
                         'added to a AssociationTable. '\
                         'It should be a tuple of hashes or bytes'

    def _add(self, data_or_file):
        """replace to add an other object than mentioned in add"""
        raise TypeError(self.WRONG_ADD_ARGUMENT.format(
                            object = data_or_file, type = type(data_or_file)))

    def _add_association(self, hashes):
        hashes_hash = self.hash_table.add(hashes.to_bytes())
        for index, hash in enumerate(hashes):
            self._add_association_at_index(index, hash, hashes_hash, hashes)
        return hashes

    def _add_association_at_index(self, index, hash, hashes_hash, hashes):
        raise NotImplementedError('to be impemented')

    def find(self, association):
        assert self.is_association_template(association)
        assert len(association) >= 1
        return self._find(association)

    def _find(self, association):
        association = self._convert_to_association(association)
        for index, hash in enumerate(association):
            if hash is None: continue
            associations = self._get_association_hashes_at_index(index, hash)
            break
        for index, hash in enumerate(association[index + 1:], 1):
            if hash is None: continue
            associations = self._get_association_hashes_at_index_limited_to(index, hash, associations)
        _associations = set()
        for association in associations:
            _associations.add(self._convert_to_association(association))
        return _associations

    def _get_association_hashes_at_index(self, index, hash):
        raise NotImplementedError("to be implemented")

    def _get_association_hashes_at_index_limited_to(self, index, hash, associations):
        new = self._get_association_hashes_at_index(index, hash)
        return associations & new
            
    
__all__ = ['AssociationTableBase']
