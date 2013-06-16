import hashlib

algorithm = hashlib.sha256

HASHBITS = 256 # bit
HASHBYTES = int(HASHBITS / 8 * 2) # hex encoded

def is_hex(string):
    return all([letter in '0123456789abcdef' for letter in string.lower()])

def is_hash(string):
    assert isinstance(string, str)
    return len(string) == HASHBYTES and is_hex(string)

__all__ = ['algorithm', 'is_hash', 'is_hex', 'HASHBYTES', 'HASHBITS']
