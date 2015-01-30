import time


class PV(object):

    # Max no. of calls per second, or None for no limit.
    def __init__(self, channel_handler, writable, readable, max_rate):
        """
        Initialises a new PV.

        :param channel_handler: The channel handler.
        :param writable: Whether the PV is readable.
        :param readable: Whether the PV is writable.
        :param max_rate: The maximum number of calls per second, or None for no rate limiting.
        """
        if max_rate is not None and max_rate <= 0:
            raise ValueError("max_rate must be positive if specified")

        self._writable = writable
        self._readable = readable
        self._max_rate = max_rate
        self._channel_handler = channel_handler
        self._value = None
        self._read_listener = None
        self._write_listener = None
        self._paused = False
        self._closed = False

        # Sufficiently long enough ago to not trigger max rate.
        self._last_read_time = 0

        if readable:
            channel_handler.add_read_listener(self._channel_handler_read_listener)
        if writable:
            channel_handler.add_write_listener(self._channel_handler_write_listener)

    def get_name(self):
        return self._channel_handler.get_name()

    def set_value(self, value):
        self._channel_handler.write(value)
        self._value = value

    def set_read_listener(self, listener):
        self._read_listener = listener

    def set_write_listener(self, listener):
        self._write_listener = listener
        return self._channel_handler.add_write_callback(listener)

    def _channel_handler_read_listener(self, name, value, **kwargs):
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
        if self._max_rate is None or now - self._last_read_time > 1.0 / self._max_rate:
            self._value = value
            self._last_read_time = now
            if not self._paused and self._read_listener is not None:
                self._read_listener(name, value, **kwargs)

    def _channel_handler_write_listener(self, name, value, **kwargs):
        if self._write_listener is not None:
            self._write_listener(name, value, **kwargs)

    def is_readable(self):
        return self._readable and self._channel_handler.is_readable()

    def is_writable(self):
        return self._writable and self._channel_handler.is_writable()

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
        self._read_listener(self._value)

    def close(self):
        self._closed = True
        self._read_listener = None
        self._write_listener = None
        if self._readable:
            self._channel_handler.remove_read_callback(self._channel_handler_read_listener)
        if self._writable:
            self._channel_handler.remove_write_callback(self._channel_handler_write_listener)

    def is_closed(self):
        return self._closed

    def is_connected(self):
        return self._channel_handler.is_connected()