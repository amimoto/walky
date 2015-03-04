import unittest

from walky.constants import *
from walky.context import *
from walky.objects.router import *
from walky.serializer import *

from _common import *

class Test(unittest.TestCase):

    def test_serializer(self):


        # Initial Prep
        sys_reg = Registry()
        self.assertIsInstance(sys_reg,Registry)
        sess_reg = Registry()
        self.assertIsInstance(sess_reg,Registry)
        conn_reg = Registry()
        self.assertIsInstance(conn_reg,Registry)
        router = Router()
        self.assertIsInstance(router,Router)
        router.mapper(TestClass, ObjectWrapper)

        context = Context()
        self.assertIsInstance(context,Context)

        context.sys(sys_reg)
        context.sess(sess_reg)
        context.conn(conn_reg)
        context.router(router)

        # Can now test the basic serialization routines
        s = HandlerSerializer(context)

        self.assertEqual(s.dumps(['1234']),'[1, ["1234"]]')
        self.assertEqual(s.dumps({'hello': 'world'}),'[1, {"hello": "world"}]')
        rec = {
                    'hello': 'world',
                    'key': { 'key2': 123 }
                  }
        complex_dump = s.dumps(rec)
        self.assertEqual(complex_dump,'[1, {"hello": "world", "key": {"key2": 123}}]')
        complex_rec = s.loads(complex_dump)
        self.assertEqual(complex_rec,rec)

        # Now let's see it handle objects
        tc = TestClass()
        json_obj_dump = s.dumps(tc)
        dump_result = s.loads(json_obj_dump)
        self.assertIsInstance(dump_result,ObjectWrapper)
        self.assertEqual(dump_result._getobj_(),tc)



if __name__ == '__main__':
    unittest.main()



