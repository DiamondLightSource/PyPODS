"""
The top-level PyPODS websocket server.
"""
from ws4py.websocket import WebSocket
import json

from pvmanager import PVManager

from wsgiref.simple_server import make_server
from ws4py.websocket import EchoWebSocket
from ws4py.server.wsgirefserver import WSGIServer, WebSocketWSGIRequestHandler
from ws4py.server.wsgiutils import WebSocketWSGIApplication



pvm = PVManager()

class PodsWebSocket(WebSocket):

    def received_message(self, message):
        print("received: %s" % message)
        print("type: %s" % type(message))
        j = json.loads(str(message))
        try:
            if j["message"] == "subscribe":
                pvm.read_and_write(j["channel-name"])
        except Exception as e:
            print("Something went wrong!")
            print(e)

    def opened(self):
        print("Websocket opened.")



if __name__ == "__main__":
    # Start the server.
    server = make_server('', 9000, server_class=WSGIServer,
                         handler_class=WebSocketWSGIRequestHandler,
                         app=WebSocketWSGIApplication(handler_cls=PodsWebSocket))
    server.initialize_websockets_manager()
    server.serve_forever()
