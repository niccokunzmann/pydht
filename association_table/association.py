
class Association(tuple):
    ASSOCIATION_SEPERATOR = '/'

    def to_bytes(self):
        string = self.ASSOCIATION_SEPERATOR.join(self)
        return string.encode('UTF-8')

    @classmethod
    def from_bytes(cls, bytes):
        string = bytes.decode('UTF-8')
        return cls(string.split(cls.ASSOCIATION_SEPERATOR))

    @classmethod
    def from_hashes(cls, tuple):
        return cls(tuple)

__all__ = ['Association']
