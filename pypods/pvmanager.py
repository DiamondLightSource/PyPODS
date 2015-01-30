from pv import PV
import re
from importlib import import_module
from collections import OrderedDict


class PVManager(object):

    def __init__(self, datasources = "sim,loc"):
        """Initialise the PVManager object, searching for datasources

        :param datasources: 
        """
        self._data_sources = OrderedDict()
        for name in datasources.split(","):
            Source = import_module("pypods.{0}.{0}datasource".format(name))
            self._data_sources[name] = Source

    def _get_handler(self, channel):
        """Get the handler for a given channel name by using its
        prefix
        
        :param channel: like sim://sine(1,2,3)
        :returns: DataHandler for this channel
        """
        match = re.match(r"(.*)://(.*)", channel)
        if match:
            # sourcename://channel
            sourcename, channel = match.groups()
            source = self._data_sources[sourcename]
        else:
            # assume first datasource is default
            source = self._data_sources[self._data_sources.keys()[0]]
        return source.create_channel(channel)

    def read(self, channel, pv_changed_func, max_rate = 0):
        """Creates a readable PV object for the given channel
        
        :param channel: channel like loc://variable(8)
        :param pv_changed_func: func(name, value) that will be called
            when the value changes
        :param max_rate: max number of updates per second"""
        handler = self._get_handler(channel)
        pv = PV(channel, readable = True, writable = False,
            max_rate=max_rate)
        pv.set_read_listener(pv_changed_func)
        handler.add_read_callback(pv.read_callback)
        return pv
        
    def write(self, channel, pv_written_func, max_rate=None):
        """Creates a writeable PV object for the given channel
        
        :param channel: channel like loc://variable(8)
        :param pv_written_func: func(name, value) that will be called
            when a write completes
        :param max_rate: max number of updates per second"""
        handler = self._get_handler(channel)
        pv = PV(channel, readable=False, writable=True, max_rate=max_rate)
        pv.set_write_listener(pv_written_func)
        handler.add_write_callback(pv.write_callback)        
        return pv

    def read_and_write(self, channel, pv_changed_func, pv_written_func, max_rate=None):
        """Creates a readable and writable PV object for the given channel
        
        :param channel: channel like loc://variable(8)
        :param pv_written_func: func(name, value) that will be called
            when a write completes
        :param max_rate: max number of updates per second"""
        handler = self._get_handler(channel)
        pv = PV(channel, readable=False, writable=True, max_rate=max_rate)
        pv.set_read_listener(pv_changed_func)            
        pv.set_write_listener(pv_written_func)
        handler.add_read_callback(pv.read_callback)        
        handler.add_write_callback(pv.write_callback) 
        return pv        
