import unittest

from walky.connection import *
from walky.port import *

class TestPort(Port):

    def init(self):
        self.buffer_recv = []
        self.buffer_send = []

    def _receiveline(self):
        return self.buffer_recv.pop()

    def on_receiveline(self,line): pass

    def _sendline(self,line):
        self.buffer_send.append(line)

class Test(unittest.TestCase):

    def test_port(self):

        connection = Connection(1)
        p = TestPort(u"TESTID",connection)

        self.assertTrue(p)
        self.assertEqual(p.id,u"TESTID")

        l_recv = u"TEST123"
        p.buffer_recv.append(l_recv)
        l = p.receiveline()
        self.assertEqual(l,l_recv)

        l_send = u"TEST456"
        p.sendline(l_send)
        l = p.buffer_send.pop()
        self.assertEqual(
            l,
            l_send+"\r\n" # appends crlf
        )


if __name__ == '__main__':
    unittest.main()




