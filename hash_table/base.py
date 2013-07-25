import io
import os

from .. import hashing
from ..errors import HashNotFound

class HashTableBase:

    @staticmethod
    def is_readable_file(file):
        """=> whether it can be read from the object"""
        return hasattr(file, 'read') and callable(file.read)

    @staticmethod
    def is_writable_file(file):
        """=> whether it can be written to the object"""
        return hasattr(file, 'read') and callable(file.read)

    @staticmethod
    def is_closable_file(file):
        """=> whether the object can be closed"""
        return hasattr(file, 'close') and callable(file.close)

    def add(self, data):
        """=> the hash ob the object
Add an object to the hash table.
Currently suported are bytes, readables, paths"""
        if isinstance(data, bytes):
            return self._add_bytes(data)
        if self.is_readable_file(data):
            return self._add_readable(data)
        return self._add(data)

    WRONG_ADD_ARGUMENT = 'Object {object} of type {type} can not be '\
                         'added to a HashTable. '\
                         'It should be bytes or have a read method.'

    def _add(self, data_or_file):
        """replace to add an other object than mentioned in add"""
        raise TypeError(self.WRONG_ADD_ARGUMENT.format(
                            object = data_or_file, type = type(data_or_file)))

    def _add_readable(self, file):
        """replace to add a file better than reading everything into memory"""
        return self.add(file.read())

    def _add_bytes(self, data):
        """replace to add a bytes better than putting them into a BytesIO"""
        return self._add_readable(io.BytesIO(data))

    is_hash = staticmethod(hashing.is_hash)

    def get_bytes(self, hash):
        """=> the bytes with for hash
May raise HashNotFound."""
        assert self.is_hash(hash)
        data = self._get_bytes(hash)
        if data is None:
            self.error_hash_not_found(hash)
        assert isinstance(data, bytes)
        return data

    def _get_bytes(self, hash):
        """replace to get bytes better than reading them from a file"""
        result = self.get_file(hash)
        if result:
            return result.read()
        return result

    def get_file(self, hash):
        """=> a file with the content for hash
May raise HasNotFound."""
        assert self.is_hash(hash)
        file = self._get_file(hash)
        if file is None:
            self.error_hash_not_found(hash)
        assert self.is_readable_file(file)
        return file

    def get(self, hash):
        """replace!"""
        raise NotImplementedError('This should be implemented like get_file'\
                                  ' or get_bytes depending on what is less '\
                                  'effort.')

    def error_hash_not_found(self, hash, traceback = None):
        """raises HashNotFound."""
        error = HashNotFound('hash {hash} is not in {self}'.format(**locals()))
        raise error.with_traceback(traceback)

    def _get_file(self, hash):
        """replace to get a file better than putting all bytes into a BytesIO"""
        return io.BytesIO(self.get_bytes(hash))

    def size(self, hash):
        """=> the number of bytes behind the hash"""
        assert self.is_hash(hash)
        size = self._size(hash)
        if size is None:
            self.error_hash_not_found(hash)
        assert isinstance(size, int)
        return size

    def _size(self, hash):
        """replace to get the size better than the length of the bytes"""
        return len(self.get_bytes(hash))

    def hashes(self):
        """=> an iterator over all hashes known to the hashtable
len(iterator) => the number of hashes
for hash in iterator: iterate over the hashes.
Once the len(iterator) is called it is of exactly this size."""
        return HashesIterator(self._hashes)
    
    def _hashes(self):
        """replace! => all hashes in an iterable"""
        raise NotImplementedError()

    def knows(self, hash):
        """=> whether there is content available for hash.
This means that HashNotFound is unlikely to be raised when using size or get*"""
        assert self.is_hash(hash)
        return self._knows(hash)

    def _knows(self, hash):
        """replace to test better than inclusion in hashes()"""
        assert self.is_hash(hash)
        return hash in self.hashes()

    def remove(self, hash):
        """remove a hash from the hashtable. No HashNotFound is raised."""
        assert self.is_hash(hash)
        return self._remove(hash)

    def _remove(self, hash):
        """replace! should remove the content of hash"""
        raise NotImplementedError()

    def open(self):
        """=> an open file that is written to the hash table when closed."""
        file = self._open()
        assert self.is_closable_file(file)
        assert self.is_writable_file(file)
        return file

    def _open(self):
        """replace!"""
        raise NotImplementedError()

    def _add_hash_table_file(self, file):
        """add a file that is returned by self.open()"""
        self.add(file)

    def _used_memory_bytes(self):
        """replace to return the approximate bytes of memory used"""
        return 0
    
    def used_memory_bytes(self):
        """=> the number of bytes used by the content"""
        value = self._used_memory_bytes()
        assert isinstance(value, int)
        assert value >= 0
        return value

    def _used_file_bytes(self):
        """replace to return the approximate bytes of file system storage used"""
        return 0
    
    def used_file_bytes(self):
        """=> the number of bytes used by the content"""
        value = self._used_file_bytes()
        assert isinstance(value, int)
        assert value >= 0
        return value

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


__all__ = ['HashTableBase']
