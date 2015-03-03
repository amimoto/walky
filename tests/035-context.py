import unittest

from walky.constants import *
from walky.acl import *
from walky.context import *

from _common import *

class Test(unittest.TestCase):

    def test_context(self):
        c = Context(
                system="SYS",
                conn="CONN",
                sess="SESS",
                user="USER",
            )
        self.assertIsInstance(c,Context)
        self.assertEqual(c.sys(),"SYS")
        self.assertEqual(c.conn(),"CONN")
        self.assertEqual(c.sess(),"SESSION")
        self.assertEqual(c.user(),"USER")
        c.user("CHANGED")
        self.assertEqual(c.user(),"CHANGED")



if __name__ == '__main__':
    unittest.main()

