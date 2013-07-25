from pydht.hash_table import InMemory as InMemoryHashTable
from pydht.association_table import *

import hashlib
import os
import base64
import sys
import random
from pytest import *

@fixture()
def mat(request = None):
    return InMemory(InMemoryHashTable())
    
def pytest_generate_tests(metafunc):
    if 'at' in metafunc.funcargnames:
        metafunc.addcall(param=mat)
##        metafunc.addcall(param=fat)


def pytest_funcarg__at(request):
    return request.param(request)

@fixture()
def string():
    return base64.b64encode(os.urandom(random.randint(3, 7)))

def hashed(*bytes):
    if len(bytes) == 1:
        return hashlib.sha256(bytes[0]).hexdigest()
    return tuple(map(hashed, bytes))

s1 = s2 = s3 = s4 = s5 = s6 = string


def test_hashes_returned_by_association(at, s1, s2):
    assert at.add((s1, s2)) == hashed(s1, s2)

def test_3_hashes_returned_by_association(at, s1, s2, s3):
    assert at.add((s1, s2, s3)) == hashed(s1, s2, s3)

def test_find_association(at, s1, s2):
    at.add((s1, s2))
    assert at.find(hashed(s1, s2)) == set([hashed(s1, s2)])

def test_find_all_associations_first_argument(at, s1, s2, s3):
    at.add((s1, s2))
    at.add((s1, s3))
    assert at.find((hashed(s1), None)) == set([hashed(s1, s2), hashed(s1, s3)])

def test_find_all_associations_second_argument(at, s1, s2, s3):
    at.add((s1, s2))
    at.add((s3, s2))
    assert at.find((None, hashed(s2))) == set([hashed(s1, s2), hashed(s3, s2)])

##def test_do_not_find_not_listed_associations(at, s1, s2, s3):
##    at.add((s3, s2)) # not listed
##    at.add((s1, s2))
##    assert at.find(hashed(s1, s2)) == [hashed(s1, s2)]
##
##def test_do_not_find_anything(at, s1, s2):
##    at.add(s1)
##    at.add(s2)
##    assert at.find((s1, None)) == []
##    assert at.find((s2, None)) == []
##
##def test_do_not_find_longer_associations(at, s1, s2, s3):
##    at.add((s1, s2, s3))
##    assert at.find((hashed(s1), None)) == [hashed(s1, s2, s3)]
##
##def test_find_long_association(at, s1, s2, s3, s4, s5):
##    at.add((s1, s2, s3, s4, s5))
##    assert at.find(hashed(s1, s2, s3, s4, s5)) == [hashed(s1, s2, s3, s4, s5)]
##    assert at.find(hashed(s1, s2, None, s4, s5)) == [hashed(s1, s2, s3, s4, s5)]
##
