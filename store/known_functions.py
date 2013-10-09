from pydht.hashing import hash_for_bytes

KNOWN_AS = b'knownas'
KNOWN_AS_HASH = hash_for_bytes(KNOWN_AS)


def loading_function(function):
    """wrapper for functions that load the data frm the loader"""
    def call_with_loaded_data(hash, loader):
        data = loader.load(hash)
        return function(data)
    call_with_loaded_data.__name__ = function.__name__
    call_with_loaded_data.__qualname__ = function.__qualname__
    return call_with_loaded_data

class FunctionStore(dict):
    def __init__(self):
        self.pop(KNOWN_AS, None)
        self.known_function(KNOWN_AS, lambda hash, loader: self[hash], loading = False)
        self.known_as.__name__ = 'known_as'
        self.known_as.__qualname__ = self.__class__.__name__ + '.known_as'

    def known_function(self, name, function = None, loading = True):
        def add(function):
            if name in self:
                raise KeyError('There is another function {} called {}'.format(self[name], name))
            if loading:
                self[function] = name
                function = loading_function(function)
            self[name] = function
            self[hash_for_bytes(name)] = function
            self[function] = name
            return function
        if function is None:
            return add
        return add(function)

    @property
    def known_as(self):
        return self[KNOWN_AS]

    def copy(self):
        copy = self.__class__()
        copy.update(self)
        copy.__init__()
        return copy

known_functions = FunctionStore()

known_function = known_functions.known_function
        
@known_function(b'utf8 string')
def decode_utf8(bytes):
    return bytes.decode('utf8')

known_function(b'integer', int)

BYTES = b'bytes'
BYTES_FUNCTION = known_function(BYTES, lambda hash, loader: loader.get_bytes(hash), loading = False)
BYTES_FUNCTION.__name__ = BYTES_FUNCTION.__qualname__ = 'bytes'
BYTES_HASH = hash_for_bytes(BYTES)


__all__ = ['known_functions', 'FunctionStore', 'decode_utf8', 'known_function',
           'KNOWN_AS', 'KNOWN_AS_HASH', 'BYTES_FUNCTION', 'BYTES_HASH']
