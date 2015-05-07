import re
from collections import OrderedDict
from subscription import Subscription

class SubscriptionManager(object):
    '''
    Single
    '''

    def __init__(self):
        self._factory = OrderedDict()

    def register_factory(self, regex, factory):
        """Register a ChannelFactory to create channels matching regex

        :param str regex: Should match the desired channel name format and the
        first group should extract the channel name

        :param ChannelFactory factory: ChannelFactory instance that will have
        its create_channel() method called with the channel name
        """
        self._factory[re.compile(regex)] = factory

    def register_default_factories(self, sep="://"):
        """Register all the default factory names"""
        from loc import LocChannelFactory
        self.register_factory("loc{}(.*)".format(sep), LocChannelFactory())

    def subscription(self, name, listener, min_delta=0, read_only=False):
        # Get a channel from the factory
        channel = None
        for regex, factory in self._factory.items():
            m = regex.match(name)
            if m:
                channel = factory.get_channel(m.group(1))
                break
        assert channel is not None, \
            "Failed to find a channel match for {}".format(name)
        sub = Subscription(channel, listener, min_delta, read_only)
        return sub
