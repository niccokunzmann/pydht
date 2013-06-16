import pydht.hash_table as hash_table

ht = hash_table.InMemory()

add = ht.add
get = ht.get_bytes
get_file = ht.get_file
size = ht.size
knows = ht.knows
is_hash = ht.is_hash
hashes = ht.hashes
