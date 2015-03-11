import unittest
import time

from walky.user import *
from walky.constants import *
from walky.connection import *
from walky.router import *
from walky.serializer import *
from walky.port import *
from walky.messenger import *

from _common import *


class TestPort(Port):

    def init(self):
        self.buffer_recv = []
        self.buffer_send = []

    def _receiveline(self):
        return self.buffer_recv.pop()

    def on_receiveline(self,line): pass

    def _sendline(self,line):
        self.buffer_send.append(line)

class TestWrapper(ObjectWrapper):
    _acls_ = [ [
        'testgroup',
        ALLOW_ALL,
        DENY_UNDERSCORED,
        MODE_READ|MODE_WRITE|MODE_EXECUTE, # mode
    ] ]

class Test(unittest.TestCase):

    def test_handler(self):

        # Initial Prep
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
        sys_reg = Registry()
        self.assertIsInstance(sys_reg,Registry)
        sess_reg = Registry()
        self.assertIsInstance(sess_reg,Registry)
        conn_reg = Registry()
        self.assertIsInstance(conn_reg,Registry)
        router = Router()
        self.assertIsInstance(router,Router)
        router.mapper('testgroup',TestClass,TestWrapper)
        crew = WorkerCrew()
        crew.start()
        self.assertIsInstance(crew,WorkerCrew)
        serializer = Serializer()
        self.assertIsInstance(serializer,Serializer)
        messenger = Messenger()
        self.assertIsInstance(messenger,Messenger)


        class DummyServer(object):
            pass
        engine = DummyServer()
        engine.router = router
        engine.crew = crew
        engine.serializer = serializer

        connection = Connection(1,engine=engine)
        self.assertIsInstance(connection,Connection)

        port = TestPort(u'TESTID',connection)
        router.mapper('testgroup',port,TestPort)

        connection.user(user)
        connection.sys(sys_reg)
        connection.sess(sess_reg)
        connection.conn(conn_reg)
        connection.port(port)
        connection.messenger(messenger)

        # Need to load at least one object into the connection
        tc = TestClass()
        reg_obj_id = connection.conn().put(tc)

        # Okay, finall can start testing the dispatcher
        connection.on_readline(u'[0,"{}","somefunc",123]'.format(reg_obj_id))
        time.sleep(0.1)

        self.assertTrue(port.buffer_send)
        self.assertEqual(port.buffer_send,['[1, "RESULT!", 123]\r\n'])

        crew.shutdown()

if __name__ == '__main__':
    unittest.main()

