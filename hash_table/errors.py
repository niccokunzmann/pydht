
class HashNotFound(KeyError):
    pass

class NoHash(ValueError):
    pass

__all__ = ['HashNotFound', 'NoHash']
