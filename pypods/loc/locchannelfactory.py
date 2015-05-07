import re
from pypods.channelfactory import ChannelFactory
from locchannel import LocChannel


class LocChannelFactory(ChannelFactory):
    # matches something in the format:
    #  name
    #  name<typ>
    #  name(initial)
    #  name<type>(initial)
    name_re = re.compile("(?P<name>[^\(<]+)"              # mandatory name
                         "(?:<(?P<typ>[^>]+)>)?"         # optional type
                         "(?:\((?P<initial>[^\)]+)\))?"  # optional initial val
                         )

    def create_channel(self, name, typ, initial):
        """Creates a channel for the given channel_name

        :rtype LocChannel
        """
        ret = LocChannel(name, typ, initial)
        return ret

    def parse_name(self, name):
        m = self.name_re.match(name)
        assert m, "Name format {} is invalid".format(name)
        return m.groupdict()
