import io
import os

from . import hashing
from .errors import HashNotFound

class HashTableBase:

    @staticmethod
    def is_readable(file):
        return hasattr(file, 'read') and callable(file.read)

    @staticmethod
    def is_writable(file):
        return hasattr(file, 'read') and callable(file.read)

    @staticmethod
    def is_closable(file):
        return hasattr(file, 'close') and callable(file.close)

    @staticmethod
    def is_path(path):
        return os.path.isfile(path)

    def add(self, data):
        if isinstance(data, bytes):
            return self._add_bytes(data)
        if self.is_readable(data):
            return self._add_readable(data)
        if self.is_path(data):
            self._add_path(data)
        return self._add(data_or_file)

    WRONG_ADD_ARGUMENT = 'Object {object} of type {type} can not be '\
                         'added to a HashTable. '\
                         'It should be bytes or have a read method.'

    def _add(self, data_or_file):
        raise ValueError(self.WRONG_ADD_ARGUMENT.format(
                            object = data_or_file, type = type(data_or_file)))

    def _add_readable(self, file):
        return self.add(file.read())
    
    def _add_bytes(self, data):
        return self._add_readable(io.BytesIO(data))

    is_hash = staticmethod(hashing.is_hash)

    def get_bytes(self, hash):
        assert self.is_hash(hash)
        data = self._get_bytes(hash)
        if data is None:
            self.error_hash_not_found(hash)
        assert isinstance(data, bytes)
        return data

    def _get_bytes(self, hash):
        result = self.get_file(hash)
        if result:
            return result.read()
        return result

    def get_file(self, hash):
        assert self.is_hash(hash)
        file = self._get_file(hash)
        if file is None:
            self.error_hash_not_found(hash)
        assert self.is_readable(file)
        return file

    def error_hash_not_found(self, hash, traceback = None):
        error = HashNotFound('hash {hash} is not in {self}'.format(**locals()))
        raise error.with_traceback(traceback)

    def _get_file(self, hash):
        return io.BytesIO(self.get_bytes(hash))

    def size(self, hash):
        assert self.is_hash(hash)
        size = self._size(hash)
        if size is None:
            self.error_hash_not_found(hash)
        assert isinstance(size, int)
        return size

    def _size(self, hash):
        return len(self.get_bytes(hash))

    def hashes(self):
        return HashesIterator(self._hashes)
    
    def _hashes(self):
        raise NotImplementedError()

    def knows(self, hash):
        assert self.is_hash(hash)
        return self._knows(hash)

    def _knows(self, hash):
        assert self.is_hash(hash)
        return hash in self.hashes()

    def remove(self, hash):
        assert self.is_hash(hash)
        return self._remove(hash)

    def _remove(self, hash):
        raise NotImplementedError()

    def _add_path(self, path):
        hash = hashlib.sha256()
        with open(path, 'rb') as file:
            self.add(file)

    def open(self):
        """Open a file that is written to the hash table when closed."""
        file = self._open()
        assert self.is_closable(file)
        assert self.is_writable(file)
        return file

    def _open(self):
        raise NotImplementedError()

    def _add_hash_table_file(self, file):
        self.add(file)


class HashesIterator:
    """a hashes iterator with a length

once length is determined a number of length hashes is returned"""
    def __init__(self, iterator):
        self._iterator = iterator
        self._length = None

    def __len__(self):
        """len(table.hashes())"""
        if self._length is None:
            length = 0
            for x in self:
                length += 1
            self._length = length
        return self._length

    def __iter__(self):
        """for hash in table.hashes()"""
        length = 0
        hash = None
        for hash in self._iterator():
            if self._length is not None and length >= self._length:
                return 
            yield hash
            length += 1
        if self._length is not None:
            if hash is None:
                hash = hashing.algorithm('').hexdigest()
            for x in range(length, self._length):
                yield hash
        return

    def __contains__(self, element):
        for contained_element in self:
            if element == contained_element:
                return True
        return False


__all__ = ['HashTableBase']
