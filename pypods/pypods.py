"""
The top-level PyPODS websocket server.
"""
from ws4py.websocket import WebSocket
import json

from pvmanager import PVManager
#import mock
class PodsServer(object):

    def __init__(self):
        self._pvm = PVManager(datasources="loc")
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

    def p(self, name, value):
        print("%s %s" % (name, value))

    def add_sub(self, j):
        pv = self._pvm.read_and_write(j["channel"], self.p ,1)
        self._channels[j["id"]] = pv
        print("channels: %s", self._channels)

    def event(self, j):
        print("received event %s"  % j)
        channel = self._channels[j["id"]]
        channel.write(j["value"])


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



