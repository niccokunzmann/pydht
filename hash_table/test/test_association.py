from test_hash_table import *

def pytest_generate_tests(metafunc):
    if 'ht' in metafunc.funcargnames:
        metafunc.addcall(param=mht)
##        metafunc.addcall(param=fht)

s1 = s2 = s3 = s4 = s5 = s6 = string

def test_hashes_returned_by_association(ht, s1, s2):
    assert ht.add((s1, s2)) == hashed(s1, s2)

def test_3_hashes_returned_by_association(ht, s1, s2, s3):
    assert ht.add((s1, s2, s3)) == hashed(s1, s2, s3)

def test_find_association(ht, s1, s2):
    ht.add((s1, s2))
    assert ht.find(hashed(s1, s2)) == [hashed(s1, s2)]

def test_find_all_associations_first_argument(ht, s1, s2, s3):
    ht.add((s1, s2))
    ht.add((s1, s3))
    assert ht.find((hashed(s1), None)) == [hashed(s1, s2), hashed(s1, s3)]

def test_find_all_associations_second_argument(ht, s1, s2, s3):
    ht.add((s1, s2))
    ht.add((s3, s2))
    assert ht.find((None, hashed(s2))) == [hashed(s1, s2), hashed(s3, s2)]

def test_do_not_find_not_listed_associations(ht, s1, s2, s3):
    ht.add((s3, s2)) # not listed
    ht.add((s1, s2))
    assert ht.find(hashed(s1, s2)) == [hashed(s1, s2)]

def test_do_not_find_anything(ht, s1, s2):
    ht.add(s1)
    ht.add(s2)
    assert ht.find((s1, None)) == []
    assert ht.find((s2, None)) == []

def test_do_not_find_longer_associations(ht, s1, s2, s3):
    ht.add((s1, s2, s3))
    assert ht.find((hashed(s1), None)) == [hashed(s1, s2, s3)]

def test_find_long_association(ht, s1, s2, s3, s4, s5):
    ht.add((s1, s2, s3, s4, s5))
    assert ht.find(hashed(s1, s2, s3, s4, s5)) == [hashed(s1, s2, s3, s4, s5)]
    assert ht.find(hashed(s1, s2, None, s4, s5)) == [hashed(s1, s2, s3, s4, s5)]

