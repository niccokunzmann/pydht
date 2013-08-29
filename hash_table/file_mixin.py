from . import files
from .. import hashing

import tempfile
import os


class InFileSystemMixin:

    CONTENT = 'content'

    HashDirectory = hashing.HashDirectory

    def __init__(self, directory):
        super().__init__()
        self._directory = directory
        self._hash_directory = self.HashDirectory(self._directory)

    def get_base_directory(self):
        return self._directory

    def _content_path_for_hash(self, hash):
        directory = self._hash_directory.make_directory(hash)
        return os.path.join(directory, self.CONTENT)

    def _open_hash_file(self, hash, mode):
        path = self._content_path_for_hash(hash)
        return open(path, mode)
        
    def _get_file(self, hash):
        try:
            return self._open_hash_file(hash, 'rb')
        except FileNotFoundError:
            return None

    def _add_readable(self, file):
        tempname = tempfile.mktemp()
        with open(tempname, 'wb') as to_file:
            hash = self.get_hash_from_file(file, to_file.write)
        path = self._content_path_for_hash(hash)
        try: os.rename(tempname, path)
        except FileExistsError: os.remove(tempname)
        return hash
            
    def _add_files(self, file):
        if file.name is None:
            return self._add_readable(file)
        hash = get_hash_from_file(file)
        try: os.rename(to_file.name, self._content_path_for_hash(hash))
        except FileExistsError: os.remove(to_file.name)

    def get_hash_from_file(self, file, write = None):
        """=> the hash of a files content

the file must support read()"""
        hash = hashing.algorithm()
        while 1:
            try: data = file.read(1024)
            except EOFError: break
            hash.update(data)
            if write: write(data)
            if len(data) < 1024:
                break
        return hash.hexdigest()

    def _hashes(self):
        exists = lambda path: os.path.exists(os.path.join(path, self.CONTENT))
        return self._hash_directory.list(exists)

    def _knows(self, hash):
        return os.path.exists(self._content_path_for_hash(hash))

    def _size(self, hash):
        try:
            return os.path.getsize(self._content_path_for_hash(hash))
        except FileNotFoundError:
            return None

    def _remove(self, hash):
        path = self._content_path_for_hash(hash)
        if os.path.isfile(path):
            os.remove(path)

    def _open(self):
        return files.SpooledTemporaryFile(self)

    def get(self, hash):
        return self.get_file(hash)

    def _used_file_bytes(self):
        size = 0
        for hash in self.hashes():
            try: size += os.path.getsize(self._content_path_for_hash(hash))
            except FileNotFoundError: pass # race condition with remove
        return size
    
__all__ = ['InFileSystemMixin']
