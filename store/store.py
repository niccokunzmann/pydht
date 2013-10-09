
from pydht.hashing import hash_for_bytes
from .known_functions import *

class Saver:
    # function : string
    from .known_functions import known_functions
    known_as = object()
        
    
    def __init__(self, association_table):
        self.association_table = association_table
        self._add_raw(KNOWN_AS)
        self.saved = {} # id : hash

    def _add_raw(self, bytes):
        association = self.association_table.add(bytes)
        association = self.association_table.add(association.to_bytes())
        assert len(association) == 1
        return association[0]

    def _add(self, function, argument):
        argument = self.save(argument)
        association = self.save_function(function), argument
        return self._add_raw(association)

    def save(self, object):
        cls = object.__class__
        if cls in self.dispatch:
            return self.dispatch[cls](self, object)
        raise NotImplementedError()

    def save_function(self, function):
        if id(function) in self.saved:
            return self.saved[id(function)]
        if function in self.known_functions:
            name = self.known_functions[function]
            hash = self._add_raw((KNOWN_AS_HASH, name))
            self.saved[id(function)] = hash
            return hash
        raise NotImplementedError('TODO')

    dispatch = {}
    dispatcher = (lambda dispatch: lambda type: lambda function: dispatch.setdefault(type, function))(dispatch)

    @dispatcher(bytes)
    def save_bytes(self, bytes):
        association = self.save_function(BYTES_FUNCTION), bytes
        return self._add_raw(association)
    
    @dispatcher(str)
    def save_str(self, string):
        return self._add(decode_utf8, string.encode('utf8'))

    @dispatcher(int)
    def save_int(self, i):
        return self._add(int, str(i))

    @dispatcher(tuple)
    def save_tuple(self, tuple):
        hashes = map(self.save, tuple)
        

class Loader:
    from .known_functions import known_functions
    
    def __init__(self, association_table):
        self.association_table = association_table
        self.loaded = {}

    @property
    def hash_table(self):
        return self.association_table.hash_table

    def load(self, hash):
        print('load')
        if hash in self.known_functions:
            print(self.known_functions[hash])
            return self.known_functions[hash]
        if hash in self.loaded:
            return self.loaded[hash]
        function_hash, argument_hash = self._load_association(hash)
        function = self.load(function_hash)
        value = function(argument_hash, self)
        self.loaded[hash] = value
        return value
        
    def _load_association(self, hash):
        bytes = self.get_bytes(hash)
        association = self.association_table.Association.from_bytes(bytes)
        return association

    def get_bytes(self, hash):
        return self.hash_table.get_bytes(hash)
        
    
class Store:
    Saver = Saver
    Loader = Loader
    
    def __init__(self, association_table):
        self.association_table = association_table

    def save(self, object):
        return self.Saver(self.association_table).save(object)
        
    def load(self, hash):
        return self.Loader(self.association_table).load(hash)


__all__ = ['Store']

