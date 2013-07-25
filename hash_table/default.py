"""The default hash table.
"""

from .. import hash_table

ht = hash_table.InMemory()

add = ht.add
get_bytes = ht.get_bytes
get_file = ht.get_file
get = ht.get_bytes
size = ht.size
knows = ht.knows
is_hash = ht.is_hash
hashes = ht.hashes
