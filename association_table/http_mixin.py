import os

from .. import hashing
from ..http.requester import Requester

class HTTPMixin:

    Requester = Requester

    def __init__(self, hash_table, base_url_or_requester = None):
        super().__init__(hash_table)
        if base_url_or_requester is None:
            self._requester = self.Requester.make(hash_table)
        else:
            self._requester = self.Requester.make(base_url_or_requester)    
        self._open_url = self._requester.open_url

    def to_requester(self):
        """=> this object's requester"""
        return self._requester

    def _find(self, association):
        association = self._convert_to_association(association)
        response = self._open_url('GET', association.to_url())
        return response.get_associations(self.Associations)
        
    def _add_association(self, association):
        association = self._convert_to_association(association)
        response = self._open_url('POST', 'associations', association.to_bytes())
        

    
__all__ = ['HTTPMixin']
