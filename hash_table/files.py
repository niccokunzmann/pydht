import io
import tempfile
import os
from .. import hashing
from ..errors import ContentAltered

class HashTableFileMixin:
    """A mixin for a hashtable that adds itself to the hashtable when closed"""

    def __init__(self, hash_table, *args, **kw):
        super().__init__(*args, **kw)
        self._hash_table = hash_table

    def add_to_hashtable(self):
        self.seek(0)
        self._hash_table._add_hash_table_file(self)

    def close(self, *args, **kw):
        self.add_to_hashtable()
        super().close(*args, **kw)

    def __enter__(self, *args, **kw):
        if hasattr(super(), '__enter__'):
            super().__enter__(*args, **kw)
        return self

    def __exit__(self, *args, **kw):
        self.add_to_hashtable()
        if hasattr(super(), '__exit__'):
            return super().__exit__(*args, **kw)

class BytesIO(HashTableFileMixin, io.BytesIO):
    """A io.BytesIO for a hashtable that adds itself to the hashtable when closed"""
    pass

class SpooledTemporaryFile(HashTableFileMixin, tempfile.SpooledTemporaryFile):
    """A tempfile.SpooledTemporaryFile for a hashtable that adds itself to the hashtable when closed"""
    pass

class HashingFile:
    """One can read from this file and the hash is updated"""

    default_chunk_size = 4096

    is_hash = staticmethod(hashing.is_hash)

    def __init__(self, file, length = None):
        self._file = file
        self._read = self._file.read
        if hasattr(file, 'fileno'):
            self.fileno = file.fileno
        self._algorithm = hashing.algorithm()
        self._length = self.get_length_of_file(file, length)

    @property
    def length(self):
        """=> length of the file or None"""
        return self._length

    def get_length_of_file(self, file, length = None):
        if length is not None: return length
        if hasattr(file, '__len__'):
            return len(file)
        if hasattr(file, 'fileno'):
            try: return os.fstat(file.fileno()).st_size
            except OSError: pass
        if hasattr(file, 'seek') and hasattr(file, 'tell'):
            start = file.tell()
            file.seek(0, 2) # end of stream
            try: return file.tell() - start
            finally: file.seek(start)
        if hasattr(file, 'getvalue'):
            return len(file.getvalue())

    def read(self, *args):
        bytes = self._read(*args)
        self._algorithm.update(bytes)
        return bytes

    @property
    def hash(self):
        return self._algorithm.hexdigest()

    def __len__(self):
        if self._length is None:
            raise TypeError('length not supported for {}'.format(self._file))
        return self._length

    def __iter__(self):
        # should be readline but is not required yet
        data = self.read(self.default_chunk_size)
        while data:
            yield data
            data = self.read(self.default_chunk_size)

class HashCheckingFile(HashingFile):

    def __init__(self, expected_hash, file, length = None):
        assert self.is_hash(expected_hash)
        super().__init__(file, length = length)
        self.expected_hash = expected_hash
        self._bytes_read = 0

    @property
    def bytes_read(self):
        """=> the number of bytes read from this file"""
        return self._bytes_read

    def is_valid(self):
        """=> whether the hash of the content matches"""
        return self.hash == self.expected_hash and self.is_read_completed()

    def is_read_completed(self):
        """=> whether something can be expected to be read from the file
        if the file has a length"""
        return self.bytes_read == self.length

    def read(self, *args):
        """read from the file and at check for consistency when its end is reached"""
        bytes = super().read(*args)
        self._bytes_read += len(bytes)
        if self.is_read_completed() and not self.is_valid():
            return self.error_hash_does_not_match()
        return bytes

    def error_hash_does_not_match(self):
        """Throw an error that the content differs from the expected"""
        raise ContentAltered("Expected the hash {} for the ressource {}"
                             " but got the hash {}".format(self.expected_hash,
                                                           self._file,
                                                           self.hash))

class NonCheckingBytesIO(io.BytesIO):
    @staticmethod
    def is_valid():
        return True

__all__ = ['BytesIO', 'SpooledTemporaryFile', 'HashingFile', 'HashCheckingFile']
