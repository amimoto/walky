import unittest
import types

from walky.constants import *
from walky.user import *
from walky.connection import *
from walky.objects import *

from _common import *


class TestObjects(unittest.TestCase):

    def test_access(self):

        user = TestUser()
        self.assertIsInstance(user,User)

        c = Connection( 1, user=user )
        self.assertIsInstance(c,Connection)

        tc = TestClass()
        ow = TestWrapper( tc, c )

        self.assertEqual(ow.b,'foo')
        self.assertIsInstance(ow.a,types.LambdaType)
        self.assertEqual(ow.a(),'yar')
        with self.assertRaises(Exception) as cm:
            ow._c

if __name__ == '__main__':
    unittest.main()

