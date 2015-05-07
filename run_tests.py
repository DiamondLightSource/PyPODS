import unittest
import xmlrunner

from tests.test_locchannel import LocChannelHandlerTest

loc_channel_handler_tests = unittest.TestLoader().loadTestsFromTestCase(LocChannelHandlerTest)

unittest.TextTestRunner().run(loc_channel_handler_tests)