import io
import tempfile
from . import hashing

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

    default_chunk_size = 1024

    def __init__(self, file, length = None):
        self._file = file
        self._read = self._file.read
        if hasattr(file, 'fileno'):
            self.fileno = file.fileno
        self._algorithm = hashing.algorithm()
        self._length = length

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
        data = self.read(self.default_chunk_size)
        while data:
            yield data
            data = self.read(self.default_chunk_size)
        

__all__ = ['BytesIO', 'SpooledTemporaryFile']
