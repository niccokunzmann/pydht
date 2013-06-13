import multiprocessing
import DHT_interface

def add(url):
    peers.append(DHT_interface.DHTInterface(url, 2))

peers = []

pool = multiprocessing.Pool(10)

def _ask_peer_for(peer, hash):
    return peer.get(hash)

def ask_for(hash):
    results = [pool.apply_async(_ask_peer_for, (peer, hash)) for peer in peers]
    for result in results:
        if result.get():
            return result
    return 

def all():
    return peers[:]
