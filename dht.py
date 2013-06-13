import hashlib
import base64
import io

strings = {}

HASHBITS = 256 # bit
HASHBYTES = int(HASHBITS / 8 * 2) # hex encoded

def add(string):
    hash = hashlib.sha256(string).hexdigest()
    strings[hash] = string
    return hash

def get(hash):
    assert len(hash) == HASHBYTES, 'expected sha256 hash with hex encoding but got {}'.format(hash)
    return strings.get(hash.lower(), None)

def get_file(hash):
    string = get(hash)
    if string is not None:
        return io.BytesIO(string)

def size(hash):
    return len(get(hash))

def is_hex(string):
    return all(letter in '0123456789abcdef' for letter in string.lower())

def is_hash(string):
    return len(string) == HASHBYTES and is_hex(string)
