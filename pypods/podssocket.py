"""
The top-level PyPODS websocket server.
"""
from ws4py.websocket import WebSocket
import json
import urlparse
import cothread
from subscriptionmanager import SubscriptionManager


class SubUidMap(object):

    def __init__(self):
        self._sub = {}
        self._uid = {}

    def add(self, uid, sub):
        self._uid[sub] = uid
        self._sub[uid] = sub

    def uid(self, sub, default=None):
        return self._uid.get(sub, default)

    def sub(self, uid, default=None):
        return self._sub.get(uid, default)

    def uids(self):
        return self._uid.keys()

    def remove(self, uid, sub):
        self._uid.pop(uid)
        self._sub.pop(sub)


class PodsDispatcher(object):
    """Utility object to run things in the cothread main loop"""

    def __init__(self):
        self.q = cothread.EventQueue()
        cothread.Spawn(self.run)

    def run(self):
        """Main loop runs in cothread thread"""
        for f, args, kwargs in self.q:
            f(*args, **kwargs)

    def spawn(self, f, *args, **kwargs):
        """Can be called from any thread"""
        cothread.Callback(self.q.Signal, (f, args, kwargs))


class PodsSocket(WebSocket):
    dispatcher = PodsDispatcher()
    # TODO: deal with different VTypes
    _vtypes = {str: "VString", float: "VDouble"}

    def opened(self):
        """Can be called from any thread"""
        self.dispatcher.spawn(self.create_manager)

    def closed(self, code, reason=None):
        """Can be called from any thread"""
        self.dispatcher.spawn(self.unsubscribe_all)

    def received_message(self, message):
        """Can be called from any thread"""
        # Think we need to do something with message here otherwise it becomes invalid
        self.dispatcher.spawn(self.process_message, json.loads(str(message)))

    def create_manager(self):
        query_string = self.environ.get("QUERY_STRING")
        args = urlparse.parse_qs(query_string)
        min_delta = float(args.get("maxRate", ['1000'])[0])
        assert min_delta > 20, "maxRate {} should be >20ms".format(min_delta)
        self.min_delta = min_delta
        self._sm = SubscriptionManager()
        self._sm.register_default_factories(sep="/")
        # map uid -> subscription
        self._map = SubUidMap()

    def unsubscribe_all(self):
        # unsubscribe subscriptions
        for uid in self._map.uids():
            self.unsubscibe(uid)

    def process_message(self, params):
        # process message, subscribe, unsubscribe, pause, resume
        message = str(params["message"])
        uid = int(params["id"])
        if message == "subscribe":
            channel_name = str(params["channel"])
            min_delta = float(params.get("maxRate", self.min_delta))
            read_only = bool(params.get("readOnly", False))
            self.subscribe(uid, channel_name, min_delta, read_only)
        elif message == "unsubscribe":
            self.unsubscribe(uid)
        elif message == "write":
            value = params["value"]
            self._map.sub(uid).write(value)
        elif message == "pause":
            self._map.sub(uid).pause()
        elif message == "resume":
            self._map.sub(uid).resume()

    def subscribe(self, uid, channel_name, min_delta, read_only):
        sub = self._sm.subscription(channel_name, self, min_delta, read_only)
        self._map.add(uid, sub)

    def unsubscribe(self, uid):
        sub = self._map.sub(uid)
        sub.close()
        self._map.remove(uid, sub)

    def serialise_value(self, value):
        # TODO: serialise alarm, display, time
        vtype = self._vtypes[type(value)]
        typ = dict(name=vtype, version="1")
        return dict(type=typ, value=value)

    def cb_value(self, sub, value):
        uid = self._map.uid(sub)
        assert uid is not None, "No uid for sub {}".format(sub)
        message = dict(message="event", id=uid, type="value",
                       value=self.serialise_value(value))
        self.send(json.dumps(message))

    def cb_connection(self, sub, connected, writeable):
        uid = self._map.uid(sub)
        assert uid, "No uid for sub {}".format(sub)
        message = dict(message="event", id=uid, type="connection",
                       connected=connected, writeConnected=writeable)
        self.send(json.dumps(message))

    def cb_exception(self, sub, exception):
        # callback functions for subscription, send ws message
        uid = self._map.uid(sub, -1)
        message = dict(message="event", id=uid, type="error",
                       error=exception)
        self.send(json.dumps(message))
