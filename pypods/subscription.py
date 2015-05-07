import time


class Subscription(object):
    # Max no. of calls per second, or None for no limit.
    def __init__(self, channel, listener, min_delta=0, read_only=False):
        """
        Subscription object provides rate limiting on a single channel

        :param str name: The channel name

        :param PodsSocket listener: The listening client that will have its
        cb_value, cb_connection and cb_exception messages called.

        :param float min_delta: The minimum time difference between value
        callbacks to produce.

        :param bool read_only: Whether we should force the channel to be read
        only
        """
        self.channel = channel
        self._listener = listener
        assert min_delta >= 0, \
            "min_delta {} should be >= 0".format(min_delta)
        self._min_delta = min_delta
        self._read_only = read_only
        self._paused = False
        self._closed = False

        # Sufficiently long enough ago to not trigger max rate.
        self._last_read_time = 0
        channel.add_listener(self)

    def write(self, value):
        assert self._read_only is False, \
            "Subscription {} requested read-only, ignoring write"\
            .format(self.name)
        assert self.channel.writeable, \
            "Channel {} is not writable, ignoring write".format(self.name)
        self.channel.write(value)

    def pause(self):
        """
        Pauses the PV.

        While paused, callbacks from the channel handler cause the current
        value to be updated, but the listener will not be called.
        """
        self._paused = True

    def resume(self):
        """
        Unpauses the PV.

        This will also call the read listener with the current value.
        """
        self._paused = False
        self._last_read_time = 0
        self.cb_value(self.channel.value)
        self.cb_connection(self.channel.connected, self.channel.writeable)

    def cb_value(self):
        """
        Handles a read callback from the channel handler.

        This records the current value from the channel handler, provided it
        has not been called too soon since the last time the callback was
        called.  The read listener is also notified of the current value,
        provided the PV has not been paused.

        :param name: The channel name.
        :param value: The value returned from the channel handler.
        :param kwargs: Any additional keyword arguments.
        """
        now = time.time()
        if now - self._last_read_time > self._min_delta:
            self._last_read_time = now
            if not self._paused:
                self._listener.cb_value(self, self.channel.value)

    def cb_connection(self):
        if not self._paused:
            self._listener.cb_connection(self, self.channel.connected, self.is_writeable())

    def cb_exception(self, exception):
        if not self._paused:
            self._listener.cb_exception(self, exception)

    def is_writeable(self):
        return self.channel.writeable and not self._read_only

    def is_closed(self):
        return self._closed

    def close(self):
        if not self.is_closed():
            self.channel.remove_listener(self)
            self._closed = True
