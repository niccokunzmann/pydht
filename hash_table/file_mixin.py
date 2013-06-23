from . import files
from . import hashing

import tempfile
import os


class InFileSystemMixin:

    def __init__(self, directory):
        super().__init__()
        self._directory = directory

    def _path_for_hash(self, hash):
        directory = os.path.join(self._directory, hash[:2])
        if not os.path.isdir(directory):
            os.makedirs(directory)
        return os.path.join(directory, hash[2:])

    def _open_hash_file(self, hash, mode):
        path = self._path_for_hash(hash)
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
        path = self._path_for_hash(hash)
        try: os.rename(tempname, path)
        except FileExistsError: os.remove(tempname)
        return hash
            
    def _add_files(self, file):
        if file.name is None:
            return self._add_readable(file)
        hash = get_hash_from_file(file)
        try: os.rename(to_file.name, self._path_for_hash(hash))
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
        dirs = os.listdir(self._directory)
        for dir in dirs:
            files = os.listdir(os.path.join(self._directory, dir))
            for file in files:
                yield dir + file
        return

    def _size(self, hash):
        try:
            return os.path.getsize(self._path_for_hash(hash))
        except FileNotFoundError:
            return None

    def _remove(self, hash):
        path = self._path_for_hash(hash)
        if os.path.isfile(path):
            os.remove(path)

    def _open(self):
        return files.SpooledTemporaryFile(self)

    def get(self, hash):
        return self.get_file(hash)

    def _used_file_bytes(self):
        size = 0
        for hash in self.hashes():
            try: size += os.path.getsize(self._path_for_hash(hash))
            except (): pass # File not found
        return size
    
__all__ = ['InFileSystemMixin']
