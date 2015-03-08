import unittest
import time

from walky.user import *
from walky.constants import *
from walky.context import *
from walky.objects.router import *
from walky.serializer import *
from walky.dispatcher import *
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

        context = Context()
        self.assertIsInstance(context,Context)

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
        router = Router(context)
        self.assertIsInstance(router,Router)
        router.mapper('testgroup',TestClass,TestWrapper)
        port = TestPort(u'TESTID',context)
        router.mapper('testgroup',port,TestPort)
        crew = WorkerCrew()
        crew.start()
        self.assertIsInstance(crew,WorkerCrew)
        serializer = HandlerSerializer(context)
        self.assertIsInstance(serializer,HandlerSerializer)
        messenger = Messenger()
        self.assertIsInstance(messenger,Messenger)

        context.user(user)
        context.sys(sys_reg)
        context.sess(sess_reg)
        context.conn(conn_reg)
        context.router(router)
        context.serializer(serializer)
        context.port(port)
        context.crew(crew)
        context.messenger(messenger)

        # Need to load at least one object into the context
        tc = TestClass()
        reg_obj_id = context.conn().put(tc)

        # Okay, finall can start testing the dispatcher
        dispatch = Dispatcher(context=context)
        self.assertIsInstance(dispatch,Dispatcher)

        dispatch.on_readline(u'[0,"{}","somefunc",123]'.format(reg_obj_id))
        time.sleep(0.1)

        self.assertTrue(port.buffer_send)
        self.assertEqual(port.buffer_send,['[1, "RESULT!", 123]\r\n'])

        crew.shutdown()

if __name__ == '__main__':
    unittest.main()

