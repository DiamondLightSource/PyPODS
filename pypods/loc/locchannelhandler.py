from channelhandler import ChannelHandler


class LocChannelHandler(ChannelHandler):

    def __init__(self, name):
        super(LocChannelHandler, self).__init__()
        self.name = name
        self.value = None
        self.read_callbacks = list()
        self.write_callbacks = list()

    def connect(self):
        pass

    def disconnect(self):
        pass

    def write(self, value, callback=None):
        if self.value != value:
            self.value = value
            # Raise a callback
            for cbr in self.read_callbacks:
                cbr(self.name, self.value)
            for cbw in self.write_callbacks:
                cbw(self.name, self.value)
        if callback is not None:
            callback(self.name, self.value)

    def add_write_callback(self, callback):
        self.write_callbacks.append(callback)

    def add_read_callback(self, callback):
        self.read_callbacks.append(callback)

    def remove_write_callback(self, callback):
        self.write_callbacks.remove(callback)

    def remove_read_callback(self, callback):
        self.read_callbacks.remove(callback)

    def delete(self):
        pass

    def set_initial_value(self, value):
        self.value = value

