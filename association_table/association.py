
class Association(tuple):
    ASSOCIATION_SEPERATOR = '/'
    ANY_HASH = '*'

    def to_string(self):
        return self.ASSOCIATION_SEPERATOR.join(
            (self.ANY_HASH if x is None else x) for x in self)

    to_url = to_string

    def to_bytes(self):
        return self.to_string().encode('UTF-8')

    @classmethod
    def from_string(cls, string):
        return cls.from_hashes(string.split(cls.ASSOCIATION_SEPERATOR))

    @classmethod
    def from_bytes(cls, bytes):
        return cls.from_string(bytes.decode('UTF-8'))

    @classmethod
    def from_line(cls, bytes):
        return cls.from_bytes(bytes.strip())

    @classmethod
    def from_hashes(cls, tuple):
        return cls((None if e == cls.ANY_HASH else e) for e in tuple)

__all__ = ['Association']
