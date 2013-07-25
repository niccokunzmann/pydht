
import pydht.hashing as hashing

class AssociationTableBase:

    def __init__(self, hash_table):
        self.hash_table = hash_table

    is_hash = staticmethod(hashing.is_hash)

    @staticmethod
    def is_association(assocation):
        """=> whether the association is a tuple of hashes"""
        return isinstance(association, tuple)

    @staticmethod
    def is_association_template(assocation):
        """=> whether the association is a tuple of hashes or None"""
        return isinstance(association, tuple) and \
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
        hashes_hash = self.hash_table.add(''.join(hashes).encode('UTF-8'))
        return hashes, hashes_hash

    def _add_association(self, association):
        hashes, hashes_hash = self._turn_into_hashes(association)
        for index, hash in enumerate(hashes):
            self._add_association_at_index(index, hash, hashes_hash, hashes)
        return hashes

    def _add_association_at_index(self, index, hash, hashes_hash, hashes):
        raise NotImplementedError('to be impemented')

    def find(self, association):
        assert is_association_template(association)
        return self._find(association)

    def _find(self, association):
        assert len(association) >= 1
        associations = self._get_association_hashes_at_index(0, association[0])
        for index, hash in enumerate(association):
            if hash is None: continue
            associations = self._get_association_hashes_at_index_limited_to(index, hash, associations)
        return associations

    def _get_association_hashes_at_index(self, index, hash):
        raise NotImplementedError("to be implemented")

    def _get_association_hashes_at_index_limited_to(self, index, associations):
        new = _get_association_hashes_at_index(self, index, hash)
        return associations & new
            
    
__all__ = ['AssociationTableBase']
