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

        self.assertEqual(s.dumps(['1234'],95),'[1, ["1234"], 95]')
        self.assertEqual(s.dumps({'hello': 'world'},100),'[1, {"hello": "world"}, 100]')
        rec = {
                    'hello': 'world',
                    'key': { 'key2': 123 }
                  }
        complex_dump = s.dumps(rec,62)
        self.assertEqual(complex_dump,'[1, {"hello": "world", "key": {"key2": 123}}, 62]')
        ( complex_rec, message_id )  = s.loads(complex_dump)
        self.assertEqual(complex_rec,rec)
        self.assertEqual(message_id,62)

        # Now let's see it handle objects
        tc = TestClass()
        json_obj_dump = s.dumps(tc,45)
        ( dump_result, message_id ) = s.loads(json_obj_dump)
        self.assertIsInstance(dump_result,ObjectWrapper)
        self.assertEqual(dump_result._getobj_(),tc)
        self.assertEqual(message_id,45)

        # Can it serialize object method invocation requests?
        omi_req = Request(
                      'object',
                      'method',
                      'a',
                      b='c'
                  )
        json_req_dump = s.dumps(omi_req,54)
        self.assertEqual(json_req_dump,'[0, "object", "method", [1, ["a"]], [1, {"b": "c"}], 54]')
        ( dump_result, message_id ) = s.loads(json_req_dump)

        self.assertIsInstance(dump_result,Request)
        self.assertEqual(message_id,54)
        self.assertEqual(dump_result.reg_obj_id,omi_req.reg_obj_id)
        self.assertEqual(dump_result.method,omi_req.method)
        self.assertEqual(dump_result.args,omi_req.args)
        self.assertEqual(dump_result.kwargs,omi_req.kwargs)

        # Can we serialize system messages?
        ## System Events
        se = SystemEvent("BOOM!")
        json_ev_dump = s.dumps(se,55)
        self.assertEqual(json_ev_dump,'[11, [1, "BOOM!"], 55]')
        ( dump_result, message_id ) = s.loads(json_ev_dump)
        self.assertIsInstance(dump_result,SystemEvent)
        self.assertEqual(message_id,55)
        self.assertEqual(dump_result.data,"BOOM!")

        ## Random System Messages
        se = SystemMessage("BAM!")
        json_ev_dump = s.dumps(se,56)
        self.assertEqual(json_ev_dump,'[12, [1, "BAM!"], 56]')
        ( dump_result, message_id ) = s.loads(json_ev_dump)
        self.assertIsInstance(dump_result,SystemMessage)
        self.assertEqual(message_id,56)
        self.assertEqual(dump_result.data,"BAM!")



if __name__ == '__main__':
    unittest.main()



