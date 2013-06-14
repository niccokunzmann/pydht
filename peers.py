import multiprocessing
import DHT_interface

def add(url):
    peer = DHT_interface.DHTInterface(url, 2)
    if peer not in peers:
        peers[peer] = peer
    return peers[peer]



peers = dict()

hash_to_peer = {} # maps hash to peers

def ask_for(hash):
    for peer in all():
        print('asking peer {} for {}'.format(peer, hash))
        content = peer.get(hash)
        if content:
            return content
    return None

def get_redirect(hash):
    for peer in all():
        if peer.knows(hash):
            return peer.fullurl(hash)

def all():
    return list(peers)
