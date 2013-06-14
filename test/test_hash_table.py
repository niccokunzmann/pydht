from pytest import *
from pydht.hash_table import *
import hashlib
import io
import os
import base64
import sys
import random
import tempfile

@fixture()
def fht():
    tempdir = tempfile.mkdtemp()
    print(tempdir)
    return InFileSystem(tempdir)

@fixture()
def mht():
    return InMemory()

def pytest_generate_tests(metafunc):
    if 'ht' in metafunc.funcargnames:
        metafunc.addcall(param=mht)
        metafunc.addcall(param=fht)

def pytest_funcarg__ht(request):
    return request.param()
    
@fixture()
def string():
    return base64.b64encode(os.urandom(random.randint(3, 7)))

def hashed(bytes):
    return hashlib.sha256(bytes).hexdigest()

def test_add_returns_hash(ht, string):
    assert ht.add(string) == hashed(string)

def test_get_by_hash_memory(mht, string):
    mht.add(string)
    assert mht.get(hashed(string)) == string

def test_get_by_hash_file(fht, string):
    fht.add(string)
    assert fht.get(hashed(string)).read() == string

def test_invalid_argument(ht):
    with raises(TypeError):
        ht.add(object())

def test_add_file_memory(mht, string):
    mht.add(io.BytesIO(string))
    assert mht.get(hashed(string)) == string

def test_add_file_file(fht, string):
    fht.add(io.BytesIO(string))
    assert fht.get(hashed(string)).read() == string

def test_get_file(ht, string):
    ht.add(string)
    assert ht.get_file(hashed(string)).read() == string
    
def test_get_file_fails(ht):
    with raises(HashNotFound):
        ht.get_file(hashed(b''))

def test_get_fails(ht, string):
    with raises(HashNotFound):
        ht.get(hashed(string))

def test_get_bytes_fails(ht):
    with raises(HashNotFound):
        ht.get_bytes(hashed(b''))

def test_get_size_of_bytes(ht, string):
    ht.add(string)
    assert ht.size(hashed(string)) == len(string)

def test_get_size_not_found(ht, string):
    with raises(HashNotFound):
        ht.size(hashed(string))

def test_open_to_store(ht, string):
    f = ht.open()
    f.write(string)
    f.close()
    assert ht.get_bytes(hashed(string)) == string

def test_open_to_store_not_ended(ht, string):
    f = ht.open()
    f.write(string)
    with raises(HashNotFound):
        ht.get(hashed(string)) == string

def test_open_with_writes_string(ht, string):
    with ht.open() as f:
        f.write(string)
    assert ht.get_bytes(hashed(string)) == string

def test_string_not_avalable_in_with(ht, string):
    with ht.open() as f:
        f.write(string)
        with raises(HashNotFound):
            ht.get(hashed(string)) == string
