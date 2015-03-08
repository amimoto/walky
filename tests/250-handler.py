import unittest

from walky.constants import *
from walky.context import *
from walky.objects.router import *
from walky.serializer import *
from walky.handler import *
from walky.port import *

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


class Test(unittest.TestCase):

    def test_handler(self):

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
        port = TestPort(id=u"TESTID")
        router.mapper(port, TestPort)

        context = Context()
        self.assertIsInstance(context,Context)

        context.sys(sys_reg)
        context.sess(sess_reg)
        context.conn(conn_reg)
        context.router(router)
        context.port(port)

        handler = Handler(context=context)

        handler.on_readline()
        handler.sendline()

        """
        tc = TestClass()
        s = Connection(
                        id="TESTID",
                        objects_global={ 'tc': tc, }
                    )
        print s.object_get('?')
        print s.object_exec('?','tc.b','123')
        print repr(s.json_request('["?","tc.b","123"]'))
        print s.id
        """

if __name__ == '__main__':
    unittest.main()

