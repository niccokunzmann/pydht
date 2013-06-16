import io
import tempfile

class HashTableFileMixin:

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
    pass

class SpooledTemporaryFile(HashTableFileMixin, tempfile.SpooledTemporaryFile):
    pass

__all__ = ['BytesIO', 'SpooledTemporaryFile']
