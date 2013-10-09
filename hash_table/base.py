import os
import urllib.request

from .. import hashing
from ..errors import HashNotFound
from .HashesIterator import HashesIterator


class HashTableBase:

    from .files import HashCheckingFile, NonCheckingBytesIO

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

    @staticmethod
    def is_reference(url):
        return isinstance(url, str)

    def get_base_directory(self):
        return None

    def add(self, data):
        """=> the hash ob the object
Add an object to the hash table.
Currently suported are bytes, readables, paths"""
        if isinstance(data, bytes):
            return self._add_bytes(data)
        if self.is_readable_file(data):
            return self._add_readable(data)
        if self.is_reference(data):
            return self.add_reference(data)
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
        return self._add_readable(self.NonCheckingBytesIO(data))

    is_hash = staticmethod(hashing.is_hash)

    def get_bytes(self, hash):
        """=> the bytes with for hash
May raise HashNotFound."""
        assert self.is_hash(hash)
        data = self._get_bytes(hash)
        if data is None:
            data = self._get_bytes_from_reference(hash)
            if data is None:
                self.error_hash_not_found(hash)
        assert isinstance(data, bytes)
        return data

    def _get_bytes_from_reference(self, hash):
        result = self._get_file_from_reference(hash)
        if result:
            return result.read()
        return result

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
            file = self._get_file_from_reference(hash)
            if file is None:
                self.error_hash_not_found(hash)
        assert self.is_readable_file(file)
        return file

    def _get_file_from_reference(self, hash):
        url = self._get_reference_url(hash)
        if url is not None:
            return self._get_file_for_url_and_hash(url, hash)

    def _get_file_for_url_and_hash(self, url, hash):
        return self.HashCheckingFile(hash, self.urlopen(url))

    urlopen = staticmethod(urllib.request.urlopen)

    def _get_reference_url(self, hash):
        raise NotImplementedError()

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
        return self.NonCheckingBytesIO(self.get_bytes(hash))

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
        """=> the number of bytes used by the content in files"""
        value = self._used_file_bytes()
        assert isinstance(value, int)
        assert value >= 0
        return value

    def used_bytes(self):
        """=> the number of bytes used by the content"""
        value = self._used_bytes()
        assert isinstance(value, int)
        assert value >= 0
        return value

    def _used_bytes(self):
        """replace if used bytes are more than in memor and in files"""
        return self.used_memory_bytes() + self.used_file_bytes()

    def serve_http(self, address = ('', 0)):
        """=> a started http server that serves the content of the hash table"""
        from .. import server
        return server.DHTHTTPServer.serve_hash_table(self, address)

    def add_reference(self, url, hash = None):
        """=> the hash for the ressource available under the given url
        the ressource is not copied.
        If not given the hash is determined.
        The ressource is available under the hash."""
        if hash is not None:
            assert self.is_hash(hash)
            return self._add_url_reference_for_hash(url, hash)
        else:
            return self._add_url_reference(url)

    def _add_url_reference_for_hash(self, url, hash):
        """replace!"""
        raise NotImplementedError()

    def _add_url_reference(self, url):
        """replace to determine the hash without using hashing.hash_for_url"""
        hash = hashing.hash_for_url(url)
        return self._add_url_reference_for_hash(url, hash)
        

__all__ = ['HashTableBase']
