"""
The top-level PyPODS websocket server.
"""


from ws4py.websocket import WebSocket


class PodsWebSocket(WebSocket):

    def received_message(self, message):
        print("received: %s" % message)

    def opened(self):
        print("opened")



# Start the server.

from wsgiref.simple_server import make_server
from ws4py.websocket import EchoWebSocket
from ws4py.server.wsgirefserver import WSGIServer, WebSocketWSGIRequestHandler
from ws4py.server.wsgiutils import WebSocketWSGIApplication

server = make_server('', 9000, server_class=WSGIServer,
                     handler_class=WebSocketWSGIRequestHandler,
                     app=WebSocketWSGIApplication(handler_cls=PodsWebSocket))
server.initialize_websockets_manager()
server.serve_forever()
