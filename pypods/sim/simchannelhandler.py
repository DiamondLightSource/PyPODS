from pypods.channelhandler import ChannelHandler
from threading import Thread
import time


class FlipFlop(Thread):
    def __init__(self, callback, time_step = 0.5):
        """Takes callback function when new data available"""
        super(FlipFlop, self).__init__()
        self.callback = callback
        self.time_step = time_step
        self._value = False
    
    def run(self):
        while True:
            self._value = not self._value
            self.callback(self._value)
            time.sleep(self.time_step)
            

class SimChannelHandler(ChannelHandler):

    def __init__(self, name):
        super(SimChannelHandler, self).__init__()
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

