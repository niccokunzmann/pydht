import pydht.server
import threading


@fixture(scope = 'module')
def dhtserver():
    print('dhtserver up')
    server = pydht.server.DHTHTTPServer(('localhost', 0),
                                        pydht.server.DHTRequestHandler)
    threading.Thread(target = server.serve_forever).start()
    def fin():
        print('dhtserver down')
        server.close()
    return server


@fixture()
def hht(request):
    dhtserver = request.getfuncargvalue('dhtserver')
    dhtserver.hash_table = request.getfuncargvalue('mht')
    hht = HTTP('http://localhost:{0}/'.format(dhtserver.server_port))
    hht.server = hht
    return hht
