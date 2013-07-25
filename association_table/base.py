
import pydht.hashing as hashing
from collections import Iterable

class AssociationTableBase:

    def __init__(self, hash_table, *args, **kw):
        super().__init__(*args, **kw)
        self.hash_table = hash_table

    @staticmethod
    def is_hash(hash):
        return isinstance(hash, str) and hashing.is_hash(hash)

    @staticmethod
    def is_association(association):
        """=> whether the association is a tuple of hashes"""
        return isinstance(association, Iterable)

    def is_association_template(self, association):
        """=> whether the association is a tuple of hashes or None"""
        return isinstance(association, Iterable) and \
               all(map(lambda hash: self.is_hash(hash) or hash is None,
                       association))

    def add(self, data):
        if self.is_association(data):
            return self._add_association(data)
        return self._add(data)

    WRONG_ADD_ARGUMENT = 'Object {object} of type {type} can not be '\
                         'added to a AssociationTable. '\
                         'It should be a tuple of hashes or bytes'

    def _add(self, data_or_file):
        """replace to add an other object than mentioned in add"""
        raise TypeError(self.WRONG_ADD_ARGUMENT.format(
                            object = data_or_file, type = type(data_or_file)))

    def _turn_into_hashes(self, association):
        hashes = []
        for hash in association:
            if not self.is_hash(hash):
                hash = self.hash_table.add(hash)
            hashes.append(hash)
        hashes_hash = self.hash_table.add(','.join(hashes).encode('UTF-8'))
        return tuple(hashes), hashes_hash

    def _add_association(self, association):
        hashes, hashes_hash = self._turn_into_hashes(association)
        for index, hash in enumerate(hashes):
            self._add_association_at_index(index, hash, hashes_hash, hashes)
        return hashes

    def _add_association_at_index(self, index, hash, hashes_hash, hashes):
        raise NotImplementedError('to be impemented')

    def find(self, association):
        assert self.is_association_template(association)
        return self._find(association)

    def _find(self, association):
        assert len(association) >= 1
        for index, hash in enumerate(association):
            if hash is None: continue
            associations = self._get_association_hashes_at_index(index, hash)
            break
        print('assoc:', index, associations)
        for index, hash in enumerate(association[index + 1:], 1):
            if hash is None: continue
            associations = self._get_association_hashes_at_index_limited_to(index, hash, associations)
            print('assoc:', index, associations)
        tuple_associations = set()
        for association in associations:
            if not isinstance(association, tuple):
                association = tuple(self.hash_table.get_bytes(association).decode('utf8').split(','))
            tuple_associations.add(association)    
        return tuple_associations

    def _get_association_hashes_at_index(self, index, hash):
        raise NotImplementedError("to be implemented")

    def _get_association_hashes_at_index_limited_to(self, index, hash, associations):
        new = self._get_association_hashes_at_index(index, hash)
        return associations & new
            
    
__all__ = ['AssociationTableBase']
