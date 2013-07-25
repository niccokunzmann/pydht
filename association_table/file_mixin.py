import os

from .. import hashing

class InFileSystemMixin:

    def __init__(self, hash_table, directory = None, *args, **kw):
        super().__init__(hash_table, *args, **kw)
        self._associations = {}
        if directory is None:
            directory = self.hash_table.get_base_directory()
            if directory is None:
                raise ValueError('I need a directory.')
        self._directory = directory
        self._hash_directory = hashing.HashDirectory(self._directory)

    def _path_for_hash_and_index(self, hash, index):
        directory = self._hash_directory.make_directory(hash, 'associations')
        file_path = os.path.join(directory, str(index))
        return file_path

    def _add_association_at_index(self, index, hash, hashes_hash, hashes):
        with open(self._path_for_hash_and_index(hash, index), 'a') as file:
            file.write(hashes_hash)
            file.write('\n')

    def _get_association_hashes_at_index(self, index, hash):
        path = self._path_for_hash_and_index(hash, index)
        if not os.path.exists(path):
            return set()
        s = set()
        with open(path, 'r') as file:
            for line in file:
                s.add(line.strip())
        return s
    
__all__ = ['InFileSystemMixin']
