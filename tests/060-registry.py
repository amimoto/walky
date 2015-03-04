import unittest

from walky.utils import *
from walky.objects import *
from walky.context import *
from walky.registry import *

from _common import *

class Test(unittest.TestCase):

    def test_registry(self):
        """ Can finally test the the registry handling abilities of
            the context object
        """

        # Initial Prep
        sys_reg = Registry()
        self.assertIsInstance(sys_reg,Registry)
        sess_reg = Registry()
        self.assertIsInstance(sess_reg,Registry)
        conn_reg = Registry()
        self.assertIsInstance(conn_reg,Registry)

        context = Context()
        self.assertIsInstance(context,Context)

        context.sys(sys_reg)
        context.sess(sess_reg)
        context.conn(conn_reg)

        # Put one object into the conection level registry
        tc = TestClass()
        wrapped = ObjectWrapper(tc,context)
        obj_id = context.conn().put(wrapped)

        # Put another into the system level registry
        tc2 = TestClass()
        tc2.b = "test"
        wrapped2 = ObjectWrapper(tc2,context)
        obj_id2 = context.sys().put(wrapped2)

        # Can we pull the information out?
        wrapped_obj = context.object_get(obj_id)
        self.assertEqual(wrapped,wrapped_obj)
        wrapped_obj = context.object_get(obj_id2)
        self.assertEqual(wrapped2,wrapped_obj)

        # Let's remove an object and check to see that it's gone
        context.object_delete(obj_id2)
        self.assertNone(context.object_get(obj_id2))

if __name__ == '__main__':
    unittest.main()

