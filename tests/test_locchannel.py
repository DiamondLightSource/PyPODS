from pkg_resources import require
require("mock")
require("cothread")
import unittest
import sys
import os
from mock import MagicMock
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from pypods.loc.locchannelfactory import LocChannelFactory


class LocChannelTest(unittest.TestCase):

    def setUp(self):
        self.factory = LocChannelFactory()

    def test_constructor_no_typ(self):
        ch = self.factory.get_channel("test")
        self.assertEquals(ch.name, "test")
        self.assertEqual(ch.value, None)
        self.assertEqual(ch.typ, str)
        self.assertEqual(ch.initial, None)

    def test_constructor_typ(self):
        ch = self.factory.get_channel("test<VDouble>")
        self.assertEquals(ch.name, "test")
        self.assertEqual(ch.value, None)
        self.assertEqual(ch.typ, float)
        self.assertEqual(ch.initial, None)

    def test_constructor_initial(self):
        ch = self.factory.get_channel("test(32)")
        self.assertEquals(ch.name, "test")
        self.assertEqual(ch.value, 32.0)
        self.assertEqual(ch.typ, float)
        self.assertEqual(ch.initial, 32.0)

    def test_constructor_initial_type(self):
        ch = self.factory.get_channel("test<VString>(32)")
        self.assertEquals(ch.name, "test")
        self.assertEqual(ch.value, "32")
        self.assertEqual(ch.typ, str)
        self.assertEqual(ch.initial, "32")

    def test_constructor_initial_type_mismatch(self):
        self.assertRaises(
            ValueError, self.factory.get_channel, 'test<VDouble>("foo")')

    def test_value_callbacks(self):
        listener = MagicMock()
        ch = self.factory.get_channel("test(32)")
        ch.add_listener(listener)
        ch.write(54)
        listener.cb_value.assertCalledWith(32)

    def test_two_differing_initial_values_raises(self):
        ch = self.factory.get_channel("test(32)")
        self.assertRaises(AssertionError, self.factory.get_channel, "test(34)")

if __name__ == '__main__':
    unittest.main()
