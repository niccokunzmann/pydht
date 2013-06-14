import hashlib
import io
import os
import pydht.hash_table_file as hash_table_file
import shutil
import tempfile

HASHBITS = 256 # bit
HASHBYTES = int(HASHBITS / 8 * 2) # hex encoded

def is_hex(string):
    return all([letter in '0123456789abcdef' for letter in string.lower()])

def is_hash(string):
    assert isinstance(string, str)
    return len(string) == HASHBYTES and is_hex(string)

class HashNotFound(KeyError):
    pass

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

    is_hash = staticmethod(is_hash)

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
        return self._hashes()
    
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
        
class InMemoryMixin:
    def __init__(self):
        super().__init__()
        self._content = {}

    def _add_bytes(self, bytes):
        hash = hashlib.sha256(bytes).hexdigest()
        self._content[hash] = bytes
        return hash

    def _get_bytes(self, hash):
        return self._content.get(hash)

    def _hashes(self):
        return self._content.keys()

    def _remove(self, hash):
        self._content.pop(hash)

    def _open(self):
        return hash_table_file.BytesIO(self)

    def get(self, hash):
        return self.get_bytes(hash)


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
        os.rename(tempname, path)
        return hash
            
    def _add_hash_table_file(self, file):
        if file.name is None:
            return self._add_readable(file)
        hash = get_hash_from_file(file)
        os.rename(to_file.name, self._path_for_hash(hash))

    def get_hash_from_file(self, file, write = None):
        hash = hashlib.sha256()
        while 1:
            data = file.read(1024)
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
        os.remove(self._path_for_hash(hash))

    def _open(self):
        return hash_table_file.SpooledTemporaryFile(self)

    def get(self, hash):
        return self.get_file(hash)

class InFileSystem(InFileSystemMixin, HashTableBase):
    pass

class InMemory(InMemoryMixin, HashTableBase):
    pass
