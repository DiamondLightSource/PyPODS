from datasource import DataSource
from localchannelhandler import LocalChannelHandler
import re


class LocalDataSource(DataSource):
    def __init__(self):
        super(LocalDataSource, self).__init__()
        self.channels = dict()

    def create_channel(self, channel_name):
        """Creates a channel handler for the given name"""
        n, v = self.parse_name(channel_name)
        # TODO: create and return channelhandler
        if n in self.channels.keys():
            self.channels[n].set_initial_value(v)
        else:
            newchan = LocalChannelHandler(n)
            newchan.set_initial_value(v)
            self.channels[n] = newchan
        return self.channels[n]

    def parse_name(self, name):
        # Name should be of format like test31(3)
        m = re.match("(.+)\((.+)\)", name)
        if m is not None:
            return m.groups()
        else:
            raise Exception("Name format is invalid")

if __name__ == "__main__":
    l = LocalDataSource()
    l.create_channel("test(5)")