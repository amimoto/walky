import unittest

from walky.utils import *
from walky.objects import *
from walky.connection import *
from walky.registry import *

from _common import *

class Test(unittest.TestCase):

    def test_registry(self):
        """ Can finally test the the registry handling abilities of
            the connection object
        """

        # Initial Prep
        sys_reg = Registry()
        self.assertIsInstance(sys_reg,Registry)
        sess_reg = Registry()
        self.assertIsInstance(sess_reg,Registry)
        conn_reg = Registry()
        self.assertIsInstance(conn_reg,Registry)

        connection = Connection(1)
        self.assertIsInstance(connection,Connection)

        connection.sys(sys_reg)
        connection.sess(sess_reg)
        connection.conn(conn_reg)

        # Put one object into the conection level registry
        tc = TestClass()
        wrapped = ObjectWrapper(tc,connection)
        obj_id = connection.conn().put(wrapped)

        # Put another into the system level registry
        tc2 = TestClass()
        tc2.b = "test"
        wrapped2 = ObjectWrapper(tc2,connection)
        obj_id2 = connection.sys().put(wrapped2)

        # Can we pull the information out?
        wrapped_obj = connection.object_get(obj_id)
        self.assertEqual(wrapped,wrapped_obj)
        wrapped_obj = connection.object_get(obj_id2)
        self.assertEqual(wrapped2,wrapped_obj)

        # Let's remove an object and check to see that it's gone
        connection.object_delete(obj_id2)
        self.assertTrue(connection.object_get(obj_id2))
        connection.object_delete(obj_id)
        self.assertIsNone(connection.object_get(obj_id))

if __name__ == '__main__':
    unittest.main()

