import unittest
import types

from walky.constants import *
from walky.user import *
from walky.context import *
from walky.objects import *

from _common import *


class TestObjects(unittest.TestCase):

    def test_access(self):

        # Prep work
        groups = ['testgroup','group2']
        attrs = {
            'name': 'Potato',
            'url': 'http://www.potatos.com',
        }
        user = User(
                    groups,
                    attrs
                )
        self.assertIsInstance(user,User)

        c = Context( user=user )
        self.assertIsInstance(c,Context)

        # Now wrap!
        class TestWrapper(ObjectWrapper):
            _acls_ = [ [
                'testgroup',
                ALLOW_ALL,
                DENY_UNDERSCORED,
                MODE_READ|MODE_WRITE|MODE_EXECUTE, # mode
            ] ]

        tc = TestClass()
        ow = TestWrapper( tc, c )

        self.assertEqual(ow.b,'foo')
        self.assertIsInstance(ow.a,types.LambdaType)
        self.assertEqual(ow.a(),'yar')
        with self.assertRaises(Exception) as cm:
            ow._c

if __name__ == '__main__':
    unittest.main()

