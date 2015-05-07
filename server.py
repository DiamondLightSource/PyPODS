from pkg_resources import require
import cothread
cothread.coselect.select_hook()

from pypods.podssocket import PodsSocket
from wsgiref.simple_server import make_server
from ws4py.server.wsgirefserver import WSGIServer, WebSocketWSGIRequestHandler
from ws4py.server.wsgiutils import WebSocketWSGIApplication

if __name__ == "__main__":
    @cothread.Spawn
    def ticker():
        while True:
            print 'I am alive'
            cothread.Sleep(5)
    
    # Start the server.
    server = make_server('', 9000, server_class=WSGIServer,
                         handler_class=WebSocketWSGIRequestHandler,
                         app=WebSocketWSGIApplication(handler_cls=PodsSocket))
    server.initialize_websockets_manager()
    server.serve_forever()
