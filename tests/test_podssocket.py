'''
Created on 7 May 2015

@author: tmc43
'''
from pkg_resources import require
require("cothread")
require("mock")
import unittest
import sys
import os
import cothread
from mock import MagicMock
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from pypods.podssocket import PodsSocket


class Test(unittest.TestCase):

    def setUp(self):
        self.sock = MagicMock()
        self.ps = PodsSocket(self.sock)
        self.ps.environ = dict(QUERY_STRING="maxRate=100")
        self.ps.opened()
        
    def test_opened_query_string_parse(self):
        self.assertEquals(self.ps.min_delta, 100)

    def test_received_message_subscribe(self):
        self.ps.received_message('{"message":"subscribe","id":0,"channel":"loc/test(43)"}')
        cothread.Yield()
        self.sock.sendall.assert_called_once_with('\x81u{"message": "event", "type": "value", "id": 0, "value": {"type": {"version": "1", "name": "VDouble"}, "value": 43.0}}')

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()