from pytest import *
from pydht.hash_table import *
from pydht.errors import HashNotFound, ContentAltered
import hashlib
import io
import os
import base64
import sys
import random
import pydht.server
import threading
import urllib

@fixture()
def tmpfile(content = ''):
    import tempfile
    file = open(tempfile.mktemp('.test'), 'w+b')
    file.write(content)
    file.flush()
##    file.seek(0)
    return file

@fixture()
def fht(request = None):
    import tempfile
    tempdir = tempfile.mkdtemp()
    return InFileSystem(tempdir)

@fixture()
def mht(request = None):
    return InMemory()

@fixture(scope = 'module')
def dhtserver():
    print('dhtserver up')
    server = pydht.server.DHTHTTPServer(('localhost', 0),
                                        pydht.server.DHTRequestHandler)
    thread = threading.Thread(target = server.serve_forever, daemon = True)
    thread.start()
    def fin():
        print('dhtserver down')
        server.shutdown()
    return server

@fixture()
def hht(request):
    dhtserver = request.getfuncargvalue('dhtserver')
    dhtserver.hash_table = request.getfuncargvalue('mht')
    hht = HTTP('http://localhost:{0}/'.format(dhtserver.server_port))
    return hht

def pytest_generate_tests(metafunc):
    if 'ht' in metafunc.funcargnames:
        metafunc.addcall(param=mht)
##        metafunc.addcall(param=fht)
##        metafunc.addcall(param=hht)
    if 'fmht' in metafunc.funcargnames:
        metafunc.addcall(param=mht)
##        metafunc.addcall(param=fht)

def pytest_funcarg__ht(request):
    return request.param(request)
def pytest_funcarg__fmht(request):
    return request.param(request)
    
@fixture()
def string():
    return base64.b64encode(os.urandom(random.randint(3, 7)))

def hashed(*bytes):
    if len(bytes) == 1:
        return hashlib.sha256(bytes[0]).hexdigest()
    return tuple(map(hashed, bytes))

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
        ht.get(hashed(string))

def test_open_with_writes_string(ht, string):
    with ht.open() as f:
        f.write(string)
    assert ht.get_bytes(hashed(string)) == string

def test_string_not_avalable_in_with(ht, string):
    with ht.open() as f:
        f.write(string)
        with raises(HashNotFound):
            ht.get(hashed(string))

def test_add_twice_works(ht, string):
    ht.add(string)
    ht.add(string)
    assert ht.get_bytes(hashed(string)) == string

def test_open_two_files_with_different_content(ht, string):
    pass

def test_open_two_files_with_same_content(ht, string):
    pass

def test_empty_hashes(ht):
    assert len(ht.hashes()) == 0

def test_add_increases_hashes(ht, string):
    ht.add(string)
    ht.add(string)
    assert len(ht.hashes()) == 1

def test_hashes_include_hash_of_string(ht, string):
    ht.add(string)
    print(hashed(string) , list(ht.hashes()))
    assert hashed(string) in ht.hashes()

def test_size_of_dht_changes_when_iterating_hashes(ht, string):
    hashes = ht.hashes()
    len(hashes)
    ht.add(string)
    for x in hashes:
        assert False, x
    assert len(hashes) == 0

def test_ht_does_not_know(ht, string):
    assert not ht.knows(hashed(string))

def test_ht_knows(ht, string):
    ht.add(string)
    assert ht.knows(hashed(string))

## used bytes

def test_used_file_bytes_is_0(ht):
    assert ht.used_file_bytes() == 0

def test_used_file_bytes(fht, string):
    fht.add(string)
    assert fht.used_file_bytes() == len(string)
    fht.add(b'0' * 1000)
    assert fht.used_file_bytes() == len(string) + 1000

def test_memory_is_not_on_file_system(mht, string):
    mht.add(string)
    assert mht.used_file_bytes() == 0

def test_bytes_in_memory_is_0(ht):
    assert ht.used_memory_bytes() == 0

def test_used_memory_bytes(mht, string):
    mht.add(string)
    assert mht.used_memory_bytes() == len(string)
    mht.add(b'0' * 1000)
    assert mht.used_memory_bytes() == len(string) + 1000

def test_file_system_is_not_in_memory(fht, string):
    fht.add(string)
    assert fht.used_memory_bytes() == 0

def test_used_bytes(fmht, string):
    fmht.add(string)
    assert fmht.used_bytes() == len(string)

def test_emppty_hash_table_uses_no_space(fmht):
    assert fmht.used_bytes() == 0

def test_remove_hash(fmht, string):
    fmht.add(string)
    fmht.remove(hashed(string))
    assert not fmht.knows(hashed(string))
    assert hashed(string) not in fmht.hashes()
    with raises(HashNotFound):
        fmht.get(hashed(string))

def test_remove_unknown_hash(fmht, string):
    fmht.remove(hashed(string))
    assert not fmht.knows(hashed(string))

def test_serve_address(ht):
    "make a hash table serve its content via http"
    server = ht.serve_http(('localhost', 3002))
    assert server.host == 'localhost'
    assert server.port == 3002
    assert server.url == 'http://localhost:3002/'
    def fin():
        server.shutdown()

def test_serve_content(ht, string):
    server = ht.serve_http()
    ht.add(string)
    file = urllib.request.urlopen(server.url + hashed(string))
    assert file.read() == string
    def fin():
        server.shutdown()
    
def test_add_local_reference(ht, string):
    file = tmpfile(string)
    ht.add_reference('file:///' + file.name, hashed(string))
    assert ht.knows(hashed(string))
    assert ht.used_bytes() == 0
    assert ht.get_bytes(hashed(string)) == string

def test_add_local_file_reference(ht, string):
    file = tmpfile(string)
    ht.add_reference('file:///' + file.name)
    assert ht.knows(hashed(string))
    assert ht.get_bytes(hashed(string)) == string

def test_add_local_file_reference_file(ht, string):
    file = tmpfile(string)
    ht.add_reference('file:///' + file.name)
    file = ht.get_file(hashed(string))
    assert file.read() == string
    assert file.is_valid()

def test_change_reference_gives_error_string(fmht, string):
    file = tmpfile(string)
    fmht.add_reference('file:///' + file.name)
    file.write(b'lala')
    file.flush()
    with raises(ContentAltered):
        fmht.get_bytes(hashed(string))
    
def test_change_reference_gives_error_file(fmht, string):
    file = tmpfile(string)
    fmht.add_reference('file:///' + file.name)
    file.write(b'lala')
    file.flush()
    file = fmht.get_file(hashed(string))
    s = file.read(len(string) + 3)
    assert s == string + b'lal'
    assert not file.is_valid()
    with raises(ContentAltered):
        file.read()
    assert not file.is_valid()

def test_file_is_not_valid_when_not_read(fmht, string):
    file = tmpfile(string)
    fmht.add_reference('file:///' + file.name)
    file = fmht.get_file(hashed(string))
    assert not file.is_valid()



