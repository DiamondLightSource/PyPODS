from pypods.subscription import Subscription  # @UnusedImport
import cothread

class Channel(object):

    # base class, subclassed by all
    connected = None

    def __init__(self, name):
        # Externally accessible params
        self.name = name
        self.value = None
        self.connected = False
        self.writeable = False
        # Internal params
        self._listeners = []

    def add_listener(self, listener):
        """Add callback function that will be called on value, connection
        and error update

        :param Subscription listener: Subscription object
        """
        assert listener not in self._listeners, \
            "Channel {} already has a listener {}".format(self.name, listener)
        self._listeners.append(listener)
        if len(self._listeners) == 1:
            # This will do the connected callback
            self.connect()
        else:
            # Do a connected and value callback ourself
            cothread.Spawn(self.do_cb_connection)
            cothread.Spawn(self.do_cb_value)

    def remove_listener(self, listener):
        """Remove callback functions
        """
        self._listeners.remove(listener)
        if len(self._listeners) == 0:
            self.disconnect()

    def do_cb_value(self):
        for listener in self._listeners:
            listener.cb_value()

    def do_cb_exception(self, exception):
        for listener in self._listeners:
            listener.cb_exception(exception)

    def do_cb_connection(self):
        for listener in self._listeners:
            listener.cb_connection()

    def connect(self):
        raise NotImplementedError

    def validate(self, **params):
        raise NotImplementedError

    def write(self):
        raise NotImplementedError

    def disconnect(self):
        raise NotImplementedError
