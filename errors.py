
from http.client import HTTPException as _HTTPException

class HashNotFound(KeyError):
    """No cnotent available for the hash."""
    pass

class NoHash(ValueError):
    """The argument is not a hash."""
    pass

class UnexpectedStatusCode(_HTTPException):
    """The http status code could not be handled."""
    pass

class ContentLengthMissing(Exception):
    """The HTTP "Content-Length" header field is required but could not be found."""
    pass

class ContentAltered(ValueError):
    """The content of the ressource does not meet the expectations."""
    pass

__all__ = ['HashNotFound', 'NoHash', 'UnexpectedStatusCode',
           'ContentLengthMissing', 'ContentAltered']
