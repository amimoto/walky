import unittest

from _common import *

class Test(unittest.TestCase):

    def test_port(self):

        p = TestPort(u"TESTID")

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




