from pytest import *
from pydht.association_table import InMemory
from pydht.store import Store
from pydht.hashing import hash_for_bytes as hashed

@fixture()
def store():
    association_table = InMemory()
    return Store(association_table)

def test_save_int(store):
    hash = store.save(10000000000)
    assert store.association_table.hash_table.knows(hash)

def test_not_stored_int_is_unknown(store):
    assert not store.association_table.hash_table.knows(hashed(b'1234'))

def test_int(store):
    h1 = store.save(1234)
    h2 = store.save(12345)
    assert store.load(h1) == 1234
    assert store.load(h2) == 12345

def test_string(store):
    hash = store.save('hallo')
    assert store.load(hash) == 'hallo'

def test_tuple(store):
    hash = store.save((1, 2, 3))
    assert store.load(hash) == (1, 2, 3)
