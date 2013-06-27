from .errors import NoHash

import hashlib

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

__all__ = ['algorithm', 'is_hash', 'is_hex', 'HASHBYTES', 'HASHBITS',
           'NULL_HASH', 'NoHash']
