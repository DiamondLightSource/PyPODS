from pypods.channel import Channel  # @UnusedImport


class ChannelFactory(object):

    def __init__(self):
        self._channels = {}

    def get_channel(self, name):
        """Get channel of given name, creating if necessary

        :param str name: Channel name without prefix
        """
        # Get a param dict from the requested name
        params = self.parse_name(name)
        name = params["name"]
        # If channel already exists ask it to validate the new params
        if name in self._channels:
            channel = self._channels[name]
            channel.validate(**params)
        # otherwise create a new channel with those params
        else:
            channel = self.create_channel(**params)
            self._channels[name] = channel
        # and return the channel
        return channel

    def create_channel(self, **params):
        return NotImplementedError

    def parse_name(self, name):
        """Parse a channel name, returning dict of parameters"""
        return dict(name=name)
