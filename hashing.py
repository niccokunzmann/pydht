from .errors import NoHash

import hashlib
import os

algorithm = hashlib.sha256

HASHBITS = 256 # bit
HASHBYTES = int(HASHBITS / 8 * 2) # hex encoded

NULL_HASH = '0' * HASHBYTES

def is_hex(string):
    return all([letter in '0123456789abcdef' for letter in string.lower()])

def is_hash(string):
    """=> whether the object represents a valid hexadecimal hash"""
    assert isinstance(string, str)
    return len(string) == HASHBYTES and is_hex(string)

def assure_is_hash(hash):
    if not is_hash(hash):
        raise NoHash('Expected a hexadecimal hash but found {}'.format(repr(hash)))

class HashDirectory:
    def __init__(self, directory):
        self.directory = directory

    def path(self, hash):
        """=> the path for a hash it may consist of different sub directories"""
        return os.path.join(self.directory, hash[:2], hash[2:])

    def make_directory(self, hash, *subdirectories):
        """=> the directory for a hash as an existing subdirectory of the base_directory"""
        directory = self.path(hash)
        if subdirectories:
            directory = os.path.join(directory, *subdirectories)
        if not os.path.isdir(directory):
            os.makedirs(directory)
        return directory

    def list(self, select = None):
        """=> hashes in directory
           select can be a function(path) that returns True or False
           whether the hash should be yielded"""
        base_directory = self.directory
        for dir in os.listdir(base_directory):
            full_dir = os.path.join(base_directory, dir)
            for dir2 in os.listdir(full_dir):
                if select and select(os.path.join(full_dir, dir2)):
                    yield dir + dir2
    

__all__ = ['algorithm', 'is_hash', 'is_hex', 'HASHBYTES', 'HASHBITS',
           'NULL_HASH', 'NoHash', 'HashDirectory']
