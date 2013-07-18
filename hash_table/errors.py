
from http.client import HTTPException as _HTTPException

class HashNotFound(KeyError):
    pass

class NoHash(ValueError):
    pass

class UnexpectedStatusCode(_HTTPException):
    pass

__all__ = ['HashNotFound', 'NoHash', 'UnexpectedStatusCode']
