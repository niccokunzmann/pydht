import multiprocessing
import DHT_interface

def add(url):
    i = DHT_interface.DHTInterface(url, 2)
    if i not in peers:
        peers.append(i)

peers = []

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
    return peers[:]
