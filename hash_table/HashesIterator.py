from .. import hashing

class HashesIterator:
    """a hashes iterator with a length

once length is determined a number of length hashes is returned"""
    def __init__(self, iterator):
        self._iterator = iterator
        self._length = None

    def __len__(self):
        """<=> len(table.hashes())"""
        if self._length is None:
            length = 0
            for x in self:
                length += 1
            self._length = length
        return self._length

    def __iter__(self):
        """<=> iter(table.hashes())
used for for hash in table.hashes(): ..."""
        length = 0
        hash = None
        for hash in self._iterator():
            if self._length is not None and length >= self._length:
                return 
            yield hash
            length += 1
        if self._length is not None:
            if hash is None:
                hash = hashing.NULL_HASH
            for x in range(length, self._length):
                yield hash
        return

    def __contains__(self, hash):
        """<=> hash in table.hashes()"""
        for contained_element in self:
            if hash == contained_element:
                return True
        return False

__all__ = ['HashesIterator']


