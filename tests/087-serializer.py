import unittest

from walky.constants import *
from walky.user import *
from walky.connection import *
from walky.router import *
from walky.serializer import *

from _common import *

class Test(unittest.TestCase):

    def test_serializer(self):

        # Initial Prep
        user = TestUser()
        self.assertIsInstance(user,User)

        sys_reg = Registry()
        self.assertIsInstance(sys_reg,Registry)
        sess_reg = Registry()
        self.assertIsInstance(sess_reg,Registry)
        conn_reg = Registry()
        self.assertIsInstance(conn_reg,Registry)
        router = Router()
        self.assertIsInstance(router,Router)
        router.mapper('testgroup', TestClass, ObjectWrapper)

        class DummyEngine(object):
            pass
        engine = DummyEngine()
        engine.router = router

        connection = Connection(1,engine=engine)
        self.assertIsInstance(connection,Connection)

        connection.user(user)
        connection.sys(sys_reg)
        connection.sess(sess_reg)
        connection.conn(conn_reg)

        # Can now test the basic serialization routines
        s = Serializer()

        self.assertEqual(s.dumps(['1234'],connection,95),'[1, ["1234"], 95]')
        self.assertEqual(s.dumps({'hello': 'world'},connection,100),'[1, {"hello": "world"}, 100]')
        rec = {
                    'hello': 'world',
                    'key': { 'key2': 123 }
                  }
        complex_dump = s.dumps(rec,connection,62)
        self.assertEqual(complex_dump,'[1, {"hello": "world", "key": {"key2": 123}}, 62]')
        ( complex_rec, message_id )  = s.loads(complex_dump,connection)
        self.assertEqual(complex_rec,rec)
        self.assertEqual(message_id,62)

        # Now let's see it handle objects
        tc = TestClass()
        json_obj_dump = s.dumps(tc,connection,45)
        ( dump_result, message_id ) = s.loads(json_obj_dump,connection)
        self.assertIsInstance(dump_result,ObjectStub)
        self.assertEqual(message_id,45)

        # Can it serialize object method invocation requests?
        omi_req = Request(
                      'object',
                      'method',
                      'a',
                      b='c'
                  )
        json_req_dump = s.dumps(omi_req,connection,54)
        self.assertEqual(json_req_dump,'[0, "object", "method", ["a"], {"b": "c"}, 54]')
        ( dump_result, message_id ) = s.loads(json_req_dump,connection)

        self.assertIsInstance(dump_result,Request)
        self.assertEqual(message_id,54)
        self.assertEqual(dump_result.reg_obj_id,omi_req.reg_obj_id)
        self.assertEqual(dump_result.method,omi_req.method)
        self.assertEqual(dump_result.args,omi_req.args)
        self.assertEqual(dump_result.kwargs,omi_req.kwargs)

        # Can we serialize system messages?
        ## System Events
        se = SystemEvent("BOOM!")
        json_ev_dump = s.dumps(se,connection,55)
        self.assertEqual(json_ev_dump,'[11, "BOOM!", 55]')
        ( dump_result, message_id ) = s.loads(json_ev_dump,connection)
        self.assertIsInstance(dump_result,SystemEvent)
        self.assertEqual(message_id,55)
        self.assertEqual(dump_result.data,"BOOM!")

        ## Random System Messages
        se = SystemMessage("BAM!")
        json_ev_dump = s.dumps(se,connection,56)
        self.assertEqual(json_ev_dump,'[12, "BAM!", 56]')
        ( dump_result, message_id ) = s.loads(json_ev_dump,connection)
        self.assertIsInstance(dump_result,SystemMessage)
        self.assertEqual(message_id,56)
        self.assertEqual(dump_result.data,"BAM!")



if __name__ == '__main__':
    unittest.main()



