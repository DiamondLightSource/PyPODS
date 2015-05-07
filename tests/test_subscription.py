from pkg_resources import require
require("mock")
require("cothread")
import unittest
import sys
import os
import cothread
from mock import MagicMock
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from pypods.subscription import Subscription
from pypods.subscriptionmanager import SubscriptionManager

class SubscriptionTest(unittest.TestCase):

    def test_no_factories(self):
        self.sm = SubscriptionManager()
        listener = MagicMock()
        self.assertRaises(AssertionError, self.sm.subscription, "loc://test", listener)

    def test_loc_factory(self):
        self.sm = SubscriptionManager()        
        listener = MagicMock()
        from pypods.loc import LocChannelFactory
        from pypods.loc.locchannel import LocChannel
        self.sm.register_factory("loc://(.*)", LocChannelFactory())
        sub = self.sm.subscription("loc://test(1)", listener)
        self.assertEqual(type(sub.channel), LocChannel)
        listener.cb_value.assert_called_once_with(sub, 1.0)

    def test_write_calls_dummy(self):
        channel = MagicMock()
        listener = MagicMock()
        sub = Subscription(channel, listener)
        sub.write(32)
        channel.write.assert_called_once_with(32)
        channel.value = 32
        sub.cb_value(channel.value)
        listener.cb_value.assert_called_once_with(sub, channel.value)

    def test_rate_conversion(self):
        channel = MagicMock()
        listener = MagicMock()
        sub = Subscription(channel, listener, 0.01)
        channel.value = 32
        sub.cb_value(channel.value)
        channel.value = 33
        sub.cb_value(channel.value)
        listener.cb_value.assert_called_once_with(sub, 32)
        listener.cb_value.reset_mock()
        channel.value = 34
        cothread.Sleep(0.01)
        sub.cb_value(channel.value)
        listener.cb_value.assert_called_once_with(sub, 34)
        listener.cb_value.reset_mock()
        channel.value = 35
        cothread.Sleep(0.01)
        sub.cb_value(channel.value)
        listener.cb_value.assert_called_once_with(sub, 35)
        
if __name__ == '__main__':
    unittest.main()
