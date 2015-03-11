import unittest

from walky.constants import *
from walky.acl import *
from walky.connection import *

from _common import *

class Test(unittest.TestCase):

    def test_connection(self):
        c = Connection(
                1,
                sys="SYS",
                conn="CONN",
                sess="SESS",
                user="USER",
            )
        self.assertIsInstance(c,Connection)
        self.assertEqual(c.sys(),"SYS")
        self.assertEqual(c.conn(),"CONN")
        self.assertEqual(c.sess(),"SESS")
        self.assertEqual(c.user(),"USER")
        c.user("CHANGED")
        self.assertEqual(c.user(),"CHANGED")



if __name__ == '__main__':
    unittest.main()

