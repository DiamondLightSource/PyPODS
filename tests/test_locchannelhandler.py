import unittest
from pypods.loc.locchannelhandler import LocChannelHandler


class LocChannelHandlerTest(unittest.TestCase):
    def test_constructor(self):
        ch = LocChannelHandler("test")
        self.assertEquals(ch.name, "test")
        self.assertEqual(ch.value, None)


if __name__ == '__main__':
    unittest.main()
