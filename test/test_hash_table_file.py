from pytest import *
from pydht.hash_table_file import *
import hashlib
import io
import os
import base64
import sys
import random

class MockHT:

    file = None

    def _add_hash_table_file(self, file):
        self.file = file


@fixture()
def ht():
    return MockHT()

@fixture()
def string():
    return base64.b64encode(os.urandom(random.randint(3, 7)))

@fixture()
def file(ht):
    return BytesIO(ht)

