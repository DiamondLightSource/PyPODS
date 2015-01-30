"""
The top-level PyPODS websocket server.
"""
from ws4py.websocket import WebSocket
import json

#from pvmanager import PVManager
import mock

from wsgiref.simple_server import make_server
from ws4py.websocket import EchoWebSocket
from ws4py.server.wsgirefserver import WSGIServer, WebSocketWSGIRequestHandler
from ws4py.server.wsgiutils import WebSocketWSGIApplication



class PodsServer(object):

    def __init__(self):
        self._pvm = mock.MagicMock()
        self._channels = {}

    def dispatch(self, j):
        msg_type = j["message"]
        try:
            if msg_type == "subscribe":
                self.add_sub(j)
            elif msg_type == "event":
                self.event(j)

        except Exception as e:
            print("Something went wrong!")
            print(e)

    def add_sub(self, j):
        pv = self._pvm.read_and_write(j["channel"])
        self._channels[j["id"]] = pv
        print("channels: %s", self._channels)

    def event(self, j):
        print("received event %s"  % j)


class PodsWebSocket(WebSocket):

    def __init__(self, a, b, c, d):
        WebSocket.__init__(self, a, b, c, d)
        self.ps = PodsServer()

    def received_message(self, message):
        print("received: %s" % message)
        print("type: %s" % type(message))
        j = json.loads(str(message))
        self.ps.dispatch(j)

    def opened(self):
        print("Websocket opened.")



if __name__ == "__main__":
    # Start the server.
    server = make_server('', 9000, server_class=WSGIServer,
                         handler_class=WebSocketWSGIRequestHandler,
                         app=WebSocketWSGIApplication(handler_cls=PodsWebSocket))
    server.initialize_websockets_manager()
    server.serve_forever()
