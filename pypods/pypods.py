"""
The top-level PyPODS websocket server.
"""
from ws4py.websocket import WebSocket
import json
import traceback

from pvmanager import PVManager

class PodsServer(object):

    def __init__(self, socket):
        self._pvm = PVManager(datasources="loc")
        self._channels = {}
        self._socket = socket

    def dispatch(self, j):
        msg_type = j["message"]
        try:
            getattr(self, msg_type)(j)
        except Exception as e:
            print("Something went wrong!")
            print(e)
            traceback.print_exc()

    def read(self, name, value):
        print("Read: %s %s" % (name, value))
        self._socket.send('{"message": "event", "id": %s, "type": "value", "value": { "type": { "name": "VDouble", "version": 1}, "value": %s} }' % (0, value))

    def subscribe(self, j):
        print("Adding sub.")
        pv = self._pvm.read_and_write(j["channel"], self.read, None, 1)
        self._socket.send('{"message": "event", "id": %s, "type": "connection", "connected": true, "writeConnected": true}' % j["id"])
        self._channels[j["id"]] = pv
        print("channels: %s" % self._channels)
        pv.set_value(1)

    def unsubscribe(self, j):
        print("Removing sub.")
        try:
            pv = self._channels.pop(j["id"])
            pv.close()
        except KeyError:
            print("Error: pv for channel %s not found" % j["id"])
        self._socket.send('{"message": "event", "id": %s, "type": "connection", "connected": false, "writeConnected": false}' % j["id"])

    def event(self, j):
        print("received event %s"  % j)
        channel = self._channels[j["id"]]

    def write(self, j):
        channel = self._channels[j["id"]]
        channel.set_value(j["value"])


class PodsWebSocket(WebSocket):

    def __init__(self, a, b, c, d):
        print("Starting PodsWebSocket ...")
        WebSocket.__init__(self, a, b, c, d)
        self.ps = PodsServer(self)

    def received_message(self, message):
        print("received: %s" % message)
        print("type: %s" % type(message))
        j = json.loads(str(message))
        self.ps.dispatch(j)

    def opened(self):
        print("Websocket opened.")
        WebSocket.opened(self)

